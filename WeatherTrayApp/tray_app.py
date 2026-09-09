"""
Weather Tray App — Main system tray application.
Manages the tray icon, context menu, weather fetching, and auto-refresh timer.

Threading model:
  - Main thread: tkinter event loop (required for UI)
  - Background thread: pystray system tray icon
  - Daemon threads: weather fetching, auto-refresh timer
"""

import threading
import tkinter as tk
from tkinter import simpledialog, messagebox

import pystray
from PIL import Image, ImageDraw, ImageFont

from config import load_config, save_config
from weather_api import fetch_full_weather
from weather_panel import WeatherPanel


def safe_print(*args, **kwargs):
    """Print that won't crash on emoji/unicode in Windows console."""
    try:
        print(*args, **kwargs)
    except (UnicodeEncodeError, OSError):
        text = " ".join(str(a) for a in args)
        text = text.encode("ascii", errors="replace").decode("ascii")
        print(text, **kwargs)


class WeatherTrayApp:
    """System tray weather application."""

    def __init__(self):
        self.config = load_config()
        self.weather_data = None
        self.tray_icon = None
        self.refresh_timer = None
        self.panel_open = False
        self.current_panel = None

        # Tkinter root (hidden, used for dialogs and panel)
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.protocol("WM_DELETE_WINDOW", self._on_quit)

        # Initial fetch (blocking, before UI starts)
        self._fetch_and_update()

        # Start auto-refresh timer
        self._start_timer()

        # Create tray icon in background thread
        self._create_tray_in_thread()

        # Run tkinter mainloop on main thread (REQUIRED for panels to work)
        self.root.mainloop()

    def _create_tray_in_thread(self):
        """Create and run the system tray icon in a background thread."""
        icon_image = self._generate_icon()

        menu = pystray.Menu(
            pystray.MenuItem("Refresh Now", self._on_refresh),
            pystray.MenuItem("Change City", self._on_change_city),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Toggle C / F", self._on_toggle_unit),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self._on_quit),
        )

        city = self.config.get("city", "Weather")
        temp_text = ""
        if self.weather_data:
            temp_text = f" | {self.weather_data['temperature']}{self.weather_data['unit_symbol']}"

        self.tray_icon = pystray.Icon(
            name="WeatherTray",
            icon=icon_image,
            title=f"Weather: {city}{temp_text}",
            menu=menu,
        )

        # Left-click -> show panel
        self.tray_icon.on_activate = self._on_tray_click

        # Run tray icon in a BACKGROUND THREAD so tkinter mainloop isn't blocked
        tray_thread = threading.Thread(target=self._run_tray, daemon=True)
        tray_thread.start()

    def _run_tray(self):
        """Run the tray icon (called in background thread)."""
        self.tray_icon.run(setup=self._tray_setup)

    def _tray_setup(self, icon):
        """Called when tray icon is ready."""
        icon.visible = True
        safe_print("Tray icon is ready!")

    def _generate_icon(self, size=64) -> Image.Image:
        """Generate a tray icon image showing the current temperature."""
        img = Image.new("RGBA", (size, size), (26, 26, 46, 255))
        draw = ImageDraw.Draw(img)

        if self.weather_data:
            temp = self.weather_data.get("temperature", "--")
            temp_str = f"{int(temp)}" if isinstance(temp, (int, float)) else "--"
        else:
            temp_str = "--"

        # Rounded rectangle background
        draw.rounded_rectangle(
            [2, 2, size - 2, size - 2],
            radius=12,
            fill=(233, 69, 96, 240),
        )

        # Temperature text
        try:
            font_size = 30 if len(temp_str) <= 2 else 24
            font = ImageFont.truetype("segoeui.ttf", font_size)
        except (OSError, IOError):
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except (OSError, IOError):
                font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), temp_str, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        x = (size - text_w) // 2
        y = (size - text_h) // 2 - 2
        draw.text((x, y), temp_str, fill="white", font=font)

        return img

    def _fetch_and_update(self):
        """Fetch weather data and update the tray icon."""
        city = self.config.get("city", "Kolkata")
        unit = self.config.get("temperature_unit", "celsius")

        safe_print(f"Fetching weather for {city}...")
        data = fetch_full_weather(city, unit)

        if data:
            self.weather_data = data
            safe_print(f"  -> {data['temperature']}{data['unit_symbol']} | {data['description']}")
            self._update_tray_icon()
        else:
            safe_print(f"  -> Failed to fetch weather for {city}")

    def _update_tray_icon(self):
        """Update the tray icon image and tooltip."""
        if self.tray_icon is None:
            return

        try:
            icon_image = self._generate_icon()
            self.tray_icon.icon = icon_image

            if self.weather_data:
                city = self.weather_data.get("name", "")
                temp = self.weather_data.get("temperature", "--")
                unit = self.weather_data.get("unit_symbol", "C")
                desc = self.weather_data.get("description", "")
                self.tray_icon.title = f"{city}: {temp}{unit} | {desc}"
            else:
                self.tray_icon.title = "Weather: No data"
        except Exception as e:
            safe_print(f"Error updating tray icon: {e}")

    def _start_timer(self):
        """Start the auto-refresh timer."""
        self._cancel_timer()
        interval = self.config.get("refresh_interval_minutes", 30) * 60
        self.refresh_timer = threading.Timer(interval, self._timer_tick)
        self.refresh_timer.daemon = True
        self.refresh_timer.start()

    def _cancel_timer(self):
        """Cancel the auto-refresh timer."""
        if self.refresh_timer:
            self.refresh_timer.cancel()
            self.refresh_timer = None

    def _timer_tick(self):
        """Timer callback — refresh and restart timer."""
        self._fetch_and_update()
        self._start_timer()

    # ── Tray event handlers ──

    def _on_tray_click(self, icon=None):
        """Left-click on tray icon -> show weather panel."""
        if self.panel_open or self.weather_data is None:
            return

        self.panel_open = True
        # Schedule on tkinter's main thread
        self.root.after(0, self._show_panel)

    def _show_panel(self):
        """Show the weather popup panel (runs on main thread)."""
        if self.weather_data is None:
            self.panel_open = False
            return

        # Close existing panel if any
        if self.current_panel:
            try:
                self.current_panel.destroy()
            except tk.TclError:
                pass

        try:
            self.current_panel = WeatherPanel(
                self.root,
                self.weather_data,
                on_refresh=self._on_refresh,
                on_close=self._on_panel_close,
                on_city_change=self._on_city_change_from_panel,
                on_toggle_unit=self._on_toggle_unit_from_panel,
            )
            safe_print("Panel opened!")
        except Exception as e:
            safe_print(f"Error showing panel: {e}")
            self.panel_open = False

    def _on_panel_close(self):
        """Called when the panel is closed."""
        self.panel_open = False
        self.current_panel = None

    def _on_city_change_from_panel(self, new_city):
        """Called when user searches a city from the panel search bar."""
        if new_city and new_city.strip():
            self.config["city"] = new_city.strip()
            save_config(self.config)
            safe_print(f"City changed to: {new_city}")
            threading.Thread(target=self._fetch_and_update, daemon=True).start()

    def _on_toggle_unit_from_panel(self):
        """Called when user clicks the toggle on the panel."""
        current = self.config.get("temperature_unit", "celsius")
        new_unit = "fahrenheit" if current == "celsius" else "celsius"
        self.config["temperature_unit"] = new_unit
        save_config(self.config)
        safe_print(f"Temperature unit changed to: {new_unit}")
        threading.Thread(target=self._fetch_and_update, daemon=True).start()

    def _on_refresh(self, icon=None, item=None):
        """Menu action: Refresh weather data."""
        threading.Thread(target=self._fetch_and_update, daemon=True).start()

    def _on_change_city(self, icon=None, item=None):
        """Menu action: Change city via input dialog."""
        self.root.after(0, self._show_city_dialog)

    def _show_city_dialog(self):
        """Show a dialog to change the city."""
        current = self.config.get("city", "Kolkata")
        new_city = simpledialog.askstring(
            "Change City",
            f"Current city: {current}\n\nEnter new city name:",
            parent=self.root,
        )

        if new_city and new_city.strip():
            new_city = new_city.strip()
            self.config["city"] = new_city
            save_config(self.config)
            safe_print(f"City changed to: {new_city}")
            threading.Thread(target=self._fetch_and_update, daemon=True).start()

    def _on_toggle_unit(self, icon=None, item=None):
        """Menu action: Toggle temperature unit."""
        current = self.config.get("temperature_unit", "celsius")
        new_unit = "fahrenheit" if current == "celsius" else "celsius"
        self.config["temperature_unit"] = new_unit
        save_config(self.config)
        safe_print(f"Temperature unit changed to: {new_unit}")
        threading.Thread(target=self._fetch_and_update, daemon=True).start()

    def _on_quit(self, icon=None, item=None):
        """Menu action: Quit the application."""
        safe_print("Quitting...")
        self._cancel_timer()
        if self.tray_icon:
            self.tray_icon.stop()
        try:
            self.root.quit()
            self.root.destroy()
        except tk.TclError:
            pass


def run():
    """Entry point to run the Weather Tray App."""
    app = WeatherTrayApp()


if __name__ == "__main__":
    run()
