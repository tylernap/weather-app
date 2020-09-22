#!/usr/bin/env python3
"""
weather_app.py

This is a small sample application that pulls data from openweathermap.org
"""
import logging
import argparse
import os
import re
import sys

import dotenv
import requests

# ===Global variables===
# This can probably be called from environment variables, but for the sake of simplicity,
# I am sticking with a global variable
LOGGING_LEVEL = logging.ERROR

BASE_API_URL = "https://api.openweathermap.org/data/2.5/weather"

logging.basicConfig(
    stream=sys.stdout, level=logging.WARN, format="%(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)
logger.setLevel(LOGGING_LEVEL)
logger.info("Starting weather application")


def parse_options() -> argparse.ArgumentParser:
    """
    Method used to parse options passed to the application
    """

    epilog = (
        '\nFor location, the formatting should be "City STATE COUNTRY". State and country codes should follow ISO3166'
        "\n\nExamples:"
        "\n  Chicago"
        "\n  Chicago IL"
        "\n  Chicago IL US\n"
    )
    parser = argparse.ArgumentParser(
        description="Calls openweathermap.org for weather information",
        epilog=epilog,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "-l",
        "--location",
        dest="location",
        help="Location to search for (ie. Chicago IL)",
    )
    parser.add_argument(
        "-k",
        "--api-key",
        dest="api_key",
        help="API Key used to interact with openweathermap. Optional if using .env",
    )

    return parser


def get_input(text) -> str:
    """
    Small function that takes input and returns it. This is mainly so that we can do testing
    """

    return input(text)


def main() -> None:
    """
    The main application. The steps it will take:
        - Parse options for API key and location
        - Pull environment variables for API key if nothing is provided
        - Asks for a location if location is not provided
        - Some field validation
            - Value exists
            - Is of the proper size
            - Is only letters
        - Reorganizes fields to be used with API and calls the API
        - Parses out temperature and returns to end user
    """
    # Parse the options passed
    parser = parse_options()
    options = parser.parse_args()

    if options.api_key:
        api_key = options.api_key
    else:
        dotenv.load_dotenv()
        api_key = os.getenv("API_KEY")

    if not api_key:
        logger.error(
            "API key missing! Either fill out a .env file or use -k with your key"
        )
        sys.exit(1)

    print(api_key)
    if options.location:
        location = options.location
    else:
        location = get_input("Where are you? ")

    # Some field validation for location
    try:
        # Validate that there is anything
        if not len(location.split()):
            raise Exception("A location is required.")
        # Make sure that there aren't too many values
        if len(location.split()) > 3:
            raise Exception("The location provided has too many items")
        # All fields should be only letters
        for item in location.split():
            if not re.match(r"^[a-zA-Z]*$", item):
                raise Exception(f"{location} is not a valid location.")
    except Exception as e:
        logger.error(f"A validation error has occurred: {str(e)}")
        parser.print_help()
        sys.exit(1)

    # If location is city and state, tack on US as the default country
    if len(location.split()) == 2:
        location += " US"

    # Make the call and parse out the temperature
    response = requests.get(
        f"{BASE_API_URL}?q={','.join(location.split())}&appid={api_key}&units=imperial"
    )
    logger.debug(f"Response: {response.json()}")
    if response.status_code == 200:
        logger.info("Successfully retrieved data")
        temps = int(response.json()["main"]["temp"])
        print(f"{location.split()[0]} weather:")
        print(f"{str(temps)} degrees Fahrenheit")
    elif response.status_code == 404:
        logger.error(f"Could not find any location for {location}")
    else:
        logger.error(
            f"An unknown error has occurred with the OpenWeather API: {str(response.json())}"
        )


if "__main__" in __name__:
    main()
