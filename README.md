# weather-app

A simple python application that leverages to OpenWeather API to get the current temperature for a given location

## Usage

```
usage: weather_app.py [-h] [-l LOCATION] [-k API_KEY]

Calls openweathermap.org for weather information

optional arguments:
  -h, --help            show this help message and exit
  -l LOCATION, --location LOCATION
                        Location to search for (ie. Chicago IL)
  -k API_KEY, --api-key API_KEY
                        API Key used to interact with openweathermap. Optional if using .env
```

For location, the formatting should be "City STATE COUNTRY". State and country codes should follow ISO3166

Examples:
- Chicago
- Chicago IL
- Chicago IL US
