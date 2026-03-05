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
import json
import sys

OWM_API_KEY = ""


def get_coordinates(state: str, country: str) -> tuple:
    """Use Nominatim API to convert location name to (lat, lng)."""
    address = f"{state}, {country}"
    url = (
        "https://nominatim.openstreetmap.org/search"
        f"?q={urllib.request.quote(address)}"
        "&format=json&limit=1"
    )

    req = urllib.request.Request(url, headers={"User-Agent": "AQI-Agent/1.0"})
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read().decode())

    if not data:
        raise RuntimeError("Location not found")

    return float(data[0]["lat"]), float(data[0]["lon"])


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


def get_aqi(lat: float, lng: float) -> tuple:
    """Use OpenWeatherMap Air Pollution API to fetch pollutants and compute AQI."""
    url = (
        "http://api.openweathermap.org/data/2.5/air_pollution"
        f"?lat={lat}&lon={lng}&appid={OWM_API_KEY}"
    )

    req = urllib.request.Request(url)
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read().decode())

    if not data.get("list"):
        raise RuntimeError("Air Pollution API returned no data")

    components = data["list"][0]["components"]
    pm25 = components.get("pm2_5", 0)
    aqi = pm25_to_aqi(pm25)

    return aqi, pm25


def agent(aqi: int) -> str:
    """Map AQI value to health advisory."""
    if aqi <= 50:
        return "Good - Air quality is satisfactory."
    elif aqi <= 100:
        return "Moderate - Acceptable, but sensitive individuals may experience issues."
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups - Elderly & children should limit outdoor activity."
    elif aqi <= 200:
        return "Unhealthy - Everyone may begin to experience health effects."
    elif aqi <= 300:
        return "Very Unhealthy - Health alert. Avoid prolonged outdoor exertion."
    else:
        return "Hazardous - Emergency conditions. Stay indoors."


def main():
    global OWM_API_KEY

    print("\n" + "="*60)
    print("HOW TO GET YOUR FREE OpenWeatherMap API KEY:")
    print("="*60)
    print("1. Visit: https://home.openweathermap.org/api_keys")
    print("2. Sign up for a free account (no billing required)")
    print("3. Confirm your email address")
    print("4. Copy your API key from the dashboard")
    print("5. Paste it below when prompted")
    print("="*60 + "\n")

    OWM_API_KEY = input("Enter your OpenWeatherMap API Key: ").strip()
    if not OWM_API_KEY:
        print("Error: No API key provided.")
        print("Get a free key at: https://home.openweathermap.org/api_keys")
        sys.exit(1)

    lat = float(input("Enter latitude: ").strip())
    lng = float(input("Enter longitude: ").strip())

    try:
        aqi_value, pm25 = get_aqi(lat, lng)
    except Exception as e:
        print(f"Error getting AQI: {e}")
        sys.exit(1)

    decision = agent(aqi_value)

    print(f"\nLatitude: {lat:.4f} | Longitude: {lng:.4f}")
    print(f"PM2.5: {pm25} ug/m3")
    print(f"AQI: {aqi_value}")
    print(f"Decision: {decision}\n")


if __name__ == "__main__":
    main()
