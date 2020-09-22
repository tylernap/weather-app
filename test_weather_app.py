"""
test_weather_app

This is the testing harness used by pytest to do unit testing on our weather application.
"""

import argparse
from unittest.mock import patch

import pytest
from pytest_mock import MockerFixture

import weather_app

MOCK_REQUESTS_SUCCESS = {
    "coord": {"lon": -83, "lat": 39.96},
    "weather": [
        {"id": 800, "main": "Clear", "description": "clear sky", "icon": "01d"}
    ],
    "base": "stations",
    "main": {
        "temp": 69.76,
        "feels_like": 63.07,
        "temp_min": 68,
        "temp_max": 72,
        "pressure": 1028,
        "humidity": 30,
    },
    "visibility": 10000,
    "wind": {"speed": 6.93, "deg": 130},
    "clouds": {"all": 1},
    "dt": 1600725366,
    "sys": {
        "type": 1,
        "id": 3656,
        "country": "US",
        "sunrise": 1600687147,
        "sunset": 1600731043,
    },
    "timezone": -14400,
    "id": 4509177,
    "name": "Testcity",
    "cod": 200,
}

MOCK_REQUESTS_FAILURE = {"cod": "404", "message": "city not found"}


@patch("weather_app.requests")
@patch("weather_app.argparse.ArgumentParser.parse_args")
def test_args_success(mock_argparse, mock_requests, capsys):
    """
    Tests a standard run with all arguments filled in
    """
    mock_requests.get.return_value.status_code = 200
    mock_requests.get.return_value.json.return_value = MOCK_REQUESTS_SUCCESS
    mock_argparse.return_value = argparse.Namespace(location="Testcity", api_key="asdf")
    _ = weather_app.main()
    assert "Testcity weather" in capsys.readouterr().out


@patch("weather_app.requests")
@patch("weather_app.argparse.ArgumentParser.parse_args")
def test_env_success(mock_argparse, mock_requests, monkeypatch, capsys):
    """
    Tests a run with pulling the API key from environment variables or .env
    """
    monkeypatch.setenv("API_KEY", "abcdefg")
    mock_requests.get.return_value.status_code = 200
    mock_requests.get.return_value.json.return_value = MOCK_REQUESTS_SUCCESS
    mock_argparse.return_value = argparse.Namespace(location="Testcity", api_key=None)
    _ = weather_app.main()
    assert "Testcity weather" in capsys.readouterr().out


@patch("weather_app.requests")
@patch("weather_app.argparse.ArgumentParser.parse_args")
def test_failure(mock_argparse, mock_requests, caplog):
    """
    Tests how the application handles errors
    """
    mock_requests.get.return_value.status_code = 404
    mock_requests.get.return_value.json.return_value = MOCK_REQUESTS_FAILURE
    mock_argparse.return_value = argparse.Namespace(location="Testcity", api_key="asdf")
    _ = weather_app.main()
    assert "ERROR" in caplog.text


@patch("weather_app.argparse.ArgumentParser.parse_args")
def test_no_key(mock_argparse, monkeypatch, caplog):
    """
    Tests when no API key is provided to see if it properly errors
    """
    mock_argparse.return_value = argparse.Namespace(location="Testcity", api_key=None)
    monkeypatch.setenv("API_KEY", "")
    with pytest.raises(SystemExit):
        _ = weather_app.main()
    assert "API key missing" in caplog.text


@patch("weather_app.requests")
@patch("weather_app.argparse.ArgumentParser.parse_args")
@patch("weather_app.get_input")
def test_location_input(mock_get_input, mock_argparse, mock_requests, capsys):
    """
    Tests if it properly gets the location from a raw input
    """
    mock_requests.get.return_value.status_code = 200
    mock_requests.get.return_value.json.return_value = MOCK_REQUESTS_SUCCESS
    mock_argparse.return_value = argparse.Namespace(location=None, api_key="asdf")
    mock_get_input.return_value = "Testcity"
    _ = weather_app.main()
    assert "Testcity weather" in capsys.readouterr().out


@patch("weather_app.argparse.ArgumentParser.parse_args")
def test_invalid_input(mock_argparse, caplog):
    """
    Tests when the location provided does not meet the regex requirements
    """
    mock_argparse.return_value = argparse.Namespace(location="abc123", api_key="asdf")
    with pytest.raises(SystemExit):
        _ = weather_app.main()
    assert "is not a valid location" in caplog.text


@patch("weather_app.requests")
@patch("weather_app.argparse.ArgumentParser.parse_args")
def test_api_failure(mock_argparse, mock_requests, caplog):
    """
    Tests when the API returns a 500 when a server error is returned
    """
    mock_argparse.return_value = argparse.Namespace(location="Testcity", api_key="asdf")
    mock_requests.get.return_value.status_code = 500
    _ = weather_app.main()
    assert "An unknown error has occurred with the OpenWeather API" in caplog.text


@patch("weather_app.requests")
@patch("weather_app.argparse.ArgumentParser.parse_args")
def test_location_parse_append(mock_argparse, mock_requests, capsys):
    """
    Tests if it properly appends US to the end of a location when needed. We assume it returns back a proper response
    """
    mock_requests.get.return_value.status_code = 200
    mock_requests.get.return_value.json.return_value = MOCK_REQUESTS_SUCCESS
    mock_argparse.return_value = argparse.Namespace(
        location="Testcity NY", api_key="asdf"
    )
    _ = weather_app.main()
    assert "Testcity weather" in capsys.readouterr().out


@patch("weather_app.argparse.ArgumentParser.parse_args")
@patch("weather_app.get_input")
def test_location_empty(mock_get_input, mock_argparse, caplog):
    """
    Tests if the location is left empty
    """
    mock_argparse.return_value = argparse.Namespace(location="", api_key="asdf")
    mock_get_input.return_value = ""
    with pytest.raises(SystemExit):
        _ = weather_app.main()
    assert "A location is required" in caplog.text


@patch("weather_app.argparse.ArgumentParser.parse_args")
@patch("weather_app.get_input")
def test_location_too_many_items(mock_get_input, mock_argparse, caplog):
    """
    Tests if the input is an invalid state with too many items to split
    """
    mock_argparse.return_value = argparse.Namespace(
        location="A B C D E", api_key="asdf"
    )
    with pytest.raises(SystemExit):
        _ = weather_app.main()
    assert "The location provided has too many items" in caplog.text
