"""
Simple Reflex Agent - Air Quality Index
========================================
1. Takes latitude and longitude as input
2. Uses OpenWeatherMap Air Pollution API for pollutant data (free)
3. Computes AQI using US EPA PM2.5 breakpoints
4. Applies simple reflex rules to generate health advisory
5. Displays AQI and health recommendation
"""

import urllib.request
import urllib.parse
import json
import sys

OWM_API_KEY: str = ""


PM25_BREAKPOINTS = [
    (0.0,   12.0,   0,  50),
    (12.1,  35.4,  51, 100),
    (35.5,  55.4, 101, 150),
    (55.5, 150.4, 151, 200),
    (150.5, 250.4, 201, 300),
    (250.5, 500.4, 301, 500),
]


def pm25_to_aqi(pm25: float) -> int:
    """Convert PM2.5 concentration (ug/m3) to AQI using EPA breakpoints."""
    for c_lo, c_hi, i_lo, i_hi in PM25_BREAKPOINTS:
        if c_lo <= pm25 <= c_hi:
            return round((i_hi - i_lo) / (c_hi - c_lo) * (pm25 - c_lo) + i_lo)
    return 500


def validate_api_key():
    """Validate OpenWeatherMap API key before continuing."""
    url = (
        "http://api.openweathermap.org/data/2.5/air_pollution"
        f"?lat=0&lon=0&appid={urllib.parse.quote(OWM_API_KEY)}"
    )

    try:
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode())
    except Exception:
        raise RuntimeError("Unable to validate API key. Please check your internet connection or API key format.")

    if "list" not in data:
        if "message" in data:
            raise RuntimeError(data["message"])
        raise RuntimeError("Invalid API response")


def get_aqi(lat: float, lng: float) -> tuple:
    """Fetch pollutants and compute AQI."""
    url = (
        "http://api.openweathermap.org/data/2.5/air_pollution"
        f"?lat={lat}&lon={lng}&appid={urllib.parse.quote(OWM_API_KEY)}"
    )

    try:
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read().decode())
    except Exception:
        raise RuntimeError("Network error while contacting API")

    if "list" not in data:
        if "message" in data:
            raise RuntimeError(f"API Error: {data['message']}")
        raise RuntimeError("Unexpected API response")

    components = data["list"][0]["components"]
    pm25 = components.get("pm2_5", 0)

    aqi = pm25_to_aqi(pm25)

    return aqi, pm25


def agent(aqi: int) -> str:
    """Map AQI value to health advisory."""
    if aqi <= 50:
        return "Good (0-50) - Air quality is satisfactory."
    elif aqi <= 100:
        return "Moderate (51-100) - Acceptable but sensitive individuals may experience issues."
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups (101-150) - Elderly & children should limit outdoor activity."
    elif aqi <= 200:
        return "Unhealthy (151-200) - Everyone may begin to experience health effects."
    elif aqi <= 300:
        return "Very Unhealthy (201-300) - Health alert. Avoid prolonged outdoor exertion."
    else:
        return "Hazardous (301-500) - Emergency conditions. Stay indoors."


def main():
    global OWM_API_KEY

    print("\n" + "=" * 60)
    print("HOW TO GET YOUR FREE OpenWeatherMap API KEY")
    print("=" * 60)
    print("1. Visit: https://home.openweathermap.org/api_keys")
    print("2. Sign up for a free account")
    print("3. Confirm your email")
    print("4. Copy your API key")
    print("5. Paste it below")
    print("=" * 60 + "\n")

    OWM_API_KEY = input("Enter your OpenWeatherMap API Key: ").strip()

    if not OWM_API_KEY:
        print("Error: No API key provided.")
        sys.exit(1)

    if " " in OWM_API_KEY:
        print("Error: API key cannot contain spaces.")
        sys.exit(1)

    # Validate API key first
    try:
        validate_api_key()
        print("API key validated successfully.\n")
    except Exception as e:
        print(f"API Key Error: {e}")
        sys.exit(1)

    # Get coordinates safely
    try:
        lat = float(input("Enter latitude: ").strip())
        lng = float(input("Enter longitude: ").strip())
    except ValueError:
        print("Invalid coordinates entered.")
        sys.exit(1)

    # Get AQI
    try:
        aqi_value, pm25 = get_aqi(lat, lng)
    except Exception as e:
        print(f"Error getting AQI: {e}")
        sys.exit(1)

    decision = agent(aqi_value)

    print("\n" + "-" * 40)
    print(f"Location Coordinates : {lat:.4f}, {lng:.4f}")
    print(f"PM2.5 Concentration  : {pm25} ug/m3")
    print(f"Calculated AQI       : {aqi_value}")
    print(f"Health Advisory      : {decision}")
    print("-" * 40 + "\n")


if __name__ == "__main__":
    main()
    