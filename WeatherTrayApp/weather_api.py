"""
Weather API module using Open-Meteo (100% free, no API key needed).
Handles geocoding and weather data fetching.
"""

import requests
from datetime import datetime

# Open-Meteo endpoints (completely free, no auth required)
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

# WMO Weather interpretation codes → (description, emoji)
WMO_CODES = {
    0: ("Clear Sky", "☀️"),
    1: ("Mainly Clear", "🌤️"),
    2: ("Partly Cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Foggy", "🌫️"),
    48: ("Rime Fog", "🌫️"),
    51: ("Light Drizzle", "🌦️"),
    53: ("Moderate Drizzle", "🌦️"),
    55: ("Dense Drizzle", "🌧️"),
    56: ("Freezing Drizzle", "🌧️"),
    57: ("Heavy Freezing Drizzle", "🌧️"),
    61: ("Slight Rain", "🌦️"),
    63: ("Moderate Rain", "🌧️"),
    65: ("Heavy Rain", "🌧️"),
    66: ("Freezing Rain", "🌧️"),
    67: ("Heavy Freezing Rain", "🌧️"),
    71: ("Slight Snow", "🌨️"),
    73: ("Moderate Snow", "🌨️"),
    75: ("Heavy Snow", "❄️"),
    77: ("Snow Grains", "❄️"),
    80: ("Slight Showers", "🌦️"),
    81: ("Moderate Showers", "🌧️"),
    82: ("Violent Showers", "⛈️"),
    85: ("Slight Snow Showers", "🌨️"),
    86: ("Heavy Snow Showers", "❄️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm + Hail", "⛈️"),
    99: ("Thunderstorm + Heavy Hail", "⛈️"),
}


def get_coordinates(city_name: str) -> dict | None:
    """
    Look up city coordinates using Open-Meteo Geocoding API.
    Returns dict with 'name', 'latitude', 'longitude', 'country', 'admin1' (state)
    or None if not found.
    """
    try:
        resp = requests.get(
            GEOCODING_URL,
            params={"name": city_name, "count": 1, "language": "en", "format": "json"},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

        if "results" not in data or len(data["results"]) == 0:
            return None

        result = data["results"][0]
        return {
            "name": result.get("name", city_name),
            "latitude": result["latitude"],
            "longitude": result["longitude"],
            "country": result.get("country", ""),
            "admin1": result.get("admin1", ""),  # state/region
        }
    except (requests.RequestException, KeyError, ValueError) as e:
        print(f"Geocoding error: {e}")
        return None


def get_weather(latitude: float, longitude: float, unit: str = "celsius") -> dict | None:
    """
    Fetch current weather + daily forecast from Open-Meteo.
    Returns parsed weather dict or None on error.
    """
    temp_unit = "fahrenheit" if unit == "fahrenheit" else "celsius"
    try:
        resp = requests.get(
            WEATHER_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,relative_humidity_2m,weather_code,"
                           "wind_speed_10m,apparent_temperature,is_day",
                "daily": "temperature_2m_max,temperature_2m_min,weather_code",
                "temperature_unit": temp_unit,
                "wind_speed_unit": "kmh",
                "timezone": "auto",
                "forecast_days": 4,
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

        current = data["current"]
        daily = data["daily"]
        weather_code = current.get("weather_code", 0)
        description, emoji = WMO_CODES.get(weather_code, ("Unknown", "❓"))

        unit_symbol = "°F" if unit == "fahrenheit" else "°C"

        # Build 3-day forecast (skip today = index 0)
        forecast = []
        for i in range(1, min(4, len(daily.get("time", [])))):
            day_code = daily["weather_code"][i] if i < len(daily.get("weather_code", [])) else 0
            day_desc, day_emoji = WMO_CODES.get(day_code, ("Unknown", "❓"))
            day_date = datetime.strptime(daily["time"][i], "%Y-%m-%d")
            forecast.append({
                "day_name": day_date.strftime("%a"),
                "date": day_date.strftime("%d %b"),
                "temp_max": daily["temperature_2m_max"][i],
                "temp_min": daily["temperature_2m_min"][i],
                "emoji": day_emoji,
                "description": day_desc,
            })

        return {
            "temperature": current["temperature_2m"],
            "feels_like": current["apparent_temperature"],
            "humidity": current["relative_humidity_2m"],
            "wind_speed": current["wind_speed_10m"],
            "weather_code": weather_code,
            "description": description,
            "emoji": emoji,
            "is_day": current.get("is_day", 1),
            "temp_max": daily["temperature_2m_max"][0],
            "temp_min": daily["temperature_2m_min"][0],
            "unit_symbol": unit_symbol,
            "fetched_at": datetime.now().strftime("%I:%M %p"),
            "timezone": data.get("timezone", ""),
            "forecast": forecast,
        }
    except (requests.RequestException, KeyError, ValueError, IndexError) as e:
        print(f"Weather API error: {e}")
        return None


def fetch_full_weather(city_name: str, unit: str = "celsius") -> dict | None:
    """
    Convenience function: geocode city → fetch weather → return combined result.
    Returns dict with location + weather data, or None on error.
    """
    location = get_coordinates(city_name)
    if location is None:
        return None

    weather = get_weather(location["latitude"], location["longitude"], unit)
    if weather is None:
        return None

    return {**location, **weather}
