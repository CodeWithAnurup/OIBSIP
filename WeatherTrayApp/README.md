# 🌤️ WeatherTrayApp — System Tray Weather for Windows

A lightweight, always-on weather application that lives in your **Windows system tray**. Get real-time weather at a glance — no browser needed, no API key required.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows)
![License](https://img.shields.io/badge/License-MIT-green)
![API](https://img.shields.io/badge/API-Open--Meteo-orange)
![Cost](https://img.shields.io/badge/Cost-100%25%20Free-brightgreen)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🌡️ **Tray Icon** | Shows current temperature right on the system tray icon |
| 📋 **Interactive Panel** | Click to see detailed weather with dark-themed UI |
| 🔍 **City Search** | Search any city directly from the panel |
| 📅 **3-Day Forecast** | See upcoming weather at a glance |
| 🔄 **Auto Refresh** | Updates every 30 minutes automatically |
| 🌡️ **Unit Toggle** | Switch between °C and °F with one click |
| ✨ **Animations** | Smooth fade-in/out, hover effects on all elements |
| 📌 **Draggable Panel** | Move the weather panel anywhere on screen |
| 💾 **Remembers Settings** | City and preferences saved locally |
| 🚀 **Auto-Start** | Optional Windows startup integration |

## 🆓 100% Free — No API Key Needed

Uses [Open-Meteo API](https://open-meteo.com/) — a completely free, open-source weather API.
- ✅ No signup required
- ✅ No API key needed
- ✅ No rate limits for personal use
- ✅ No cost — ever

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/CodeWithAnurup/OIBSIP.git
cd OIBSIP/WeatherTrayApp
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
python main.py
```

The weather icon will appear in your **system tray** (bottom-right, near the clock).

> 💡 **Tip:** If you don't see it, click the `^` arrow near the clock — Windows hides new tray icons by default.

### 4. Run silently (no console window)
Double-click `start_weather.pyw` to run without a console window.

---

## 🖱️ How to Use

| Action | What Happens |
|--------|-------------|
| **Hover** tray icon | Shows city, temperature, and condition |
| **Left-click** tray icon | Opens the interactive weather panel |
| **Right-click** tray icon | Context menu: Refresh, Change City, Toggle °C/°F, Quit |

### Panel Features:
- 🔍 **Search bar** — Type a city name and press Enter
- 📅 **3-day forecast** — Scroll down to see upcoming days
- 🌡️ **Toggle button** — Switch °C / °F
- 🔄 **Refresh button** — Get latest data
- ✨ **Hover effects** — Interactive stat cards and forecast rows

---

## 🚀 Auto-Start on Windows Boot

To make it run 24/7 automatically:

1. Press `Win + R` → type `shell:startup` → Enter
2. Create a shortcut to `start_weather.pyw` in that folder

Or run this PowerShell command:
```powershell
powershell -ExecutionPolicy Bypass -File create_startup_shortcut.ps1
```

---

## 📁 Project Structure

```
WeatherTrayApp/
├── main.py                      # Entry point
├── tray_app.py                  # System tray icon + menu + panel integration
├── weather_api.py               # Open-Meteo API (geocoding + weather + forecast)
├── weather_panel.py             # Interactive dark-themed popup UI
├── config.py                    # Save/load user preferences to JSON
├── start_weather.pyw            # Silent launcher (no console window)
├── create_startup_shortcut.ps1  # Auto-start setup script
├── test_tray.py                 # Quick tray icon test
├── requirements.txt             # Python dependencies
└── weather_config.json          # (auto-created) saved user preferences
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|-----------|---------|
| **Python 3.10+** | Core language |
| **Open-Meteo API** | Free weather data (no key needed) |
| **pystray** | Windows system tray integration |
| **Pillow** | Dynamic tray icon generation |
| **tkinter** | Interactive popup panel UI |
| **requests** | HTTP API calls |

---

## 🌐 API Details

### Weather Data (Open-Meteo)
```
GET https://api.open-meteo.com/v1/forecast
    ?latitude=22.57&longitude=88.36
    &current=temperature_2m,humidity,weather_code,wind_speed,apparent_temperature
    &daily=temperature_2m_max,temperature_2m_min,weather_code
    &forecast_days=4
```

### City Geocoding (Open-Meteo)
```
GET https://geocoding-api.open-meteo.com/v1/search
    ?name=Kolkata&count=1
```

---

## 📝 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

*Built with ❤️ by [Anurup](https://github.com/CodeWithAnurup)*
