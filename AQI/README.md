# Air Quality Index (AQI) Agent

A simple reflex agent that retrieves real-time air quality data and provides health advisories based on AQI values.

## Features

- **Real-time AQI Calculation**: Fetches air pollution data using the OpenWeatherMap Air Pollution API
- **EPA Breakpoints**: Converts PM2.5 concentration to AQI using official US EPA standards
- **Health Advisories**: Provides actionable health recommendations based on current air quality
- **Simple Reflex Logic**: Direct condition-action mapping with no memory or prediction

## How It Works

1. User provides latitude and longitude coordinates
2. Agent queries OpenWeatherMap API for current PM2.5 levels
3. PM2.5 concentration is converted to AQI using EPA breakpoints
4. Health advisory is generated based on AQI value

## Setup

### Requirements

- Python 3.6+
- Free OpenWeatherMap API key (no billing required)

### Installation

1. Clone or download this project
2. Get a free API key:
   - Visit: https://home.openweathermap.org/api_keys
   - Sign up for a free account
   - Confirm your email
   - Copy your API key

### Usage

```bash
python aqi_agent.py
```

When prompted:
1. Enter your OpenWeatherMap API key
2. Enter latitude (e.g., 40.7128 for New York City)
3. Enter longitude (e.g., -74.0060 for New York City)

The agent will display:
- Current coordinates
- PM2.5 concentration (µg/m³)
- AQI value (0-500+)
- Health advisory

## AQI Categories

| AQI Range | Level | Health Implication |
|-----------|-------|-------------------|
| 0-50 | Good | Air quality is satisfactory |
| 51-100 | Moderate | Acceptable; some may experience issues |
| 101-150 | Unhealthy for Sensitive Groups | Elderly & children should limit outdoor activity |
| 151-200 | Unhealthy | Everyone may experience health effects |
| 201-300 | Very Unhealthy | Health alert; avoid prolonged outdoor exertion |
| 301+ | Hazardous | Emergency conditions; stay indoors |

## API Reference

### OpenWeatherMap Air Pollution API

- Endpoint: `http://api.openweathermap.org/data/2.5/air_pollution`
- Parameters: `lat`, `lon`, `appid` (API key)
- Returns: Real-time pollutant data including PM2.5, PM10, NO2, O3, etc.

## Example

```
Enter your OpenWeatherMap API Key: abc123def456...
Enter latitude: 34.0522
Enter longitude: -118.2437

Latitude: 34.0522 | Longitude: -118.2437
PM2.5: 35.2 ug/m3
AQI: 103
Decision: Moderate - Acceptable, but sensitive individuals may experience issues.
```

## Data Sources

- **Air Quality Data**: [OpenWeatherMap Air Pollution API](https://openweathermap.org/api/air-pollution)
- **AQI Standards**: US Environmental Protection Agency (EPA)

## License

This project is provided as-is for educational purposes.
