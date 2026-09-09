"""
Weather Panel UI — Interactive, dark-themed popup with animations.
Features: city search bar, 3-day forecast, hover effects, toggle °C/°F, fade-in.
"""

import tkinter as tk
from tkinter import font as tkfont


# Color scheme — dark theme
COLORS = {
    "bg": "#1a1a2e",
    "bg_card": "#16213e",
    "bg_card_hover": "#1a2744",
    "bg_stat": "#0f3460",
    "bg_stat_hover": "#134178",
    "bg_search": "#16213e",
    "text_primary": "#ffffff",
    "text_secondary": "#a8b2d1",
    "text_accent": "#e94560",
    "text_temp": "#ffffff",
    "text_city": "#e94560",
    "border": "#0f3460",
    "button_bg": "#e94560",
    "button_bg_hover": "#c73e54",
    "button_fg": "#ffffff",
    "toggle_on": "#e94560",
    "toggle_off": "#0f3460",
    "forecast_bg": "#16213e",
    "forecast_hover": "#1a2744",
    "search_border": "#e94560",
}


class WeatherPanel(tk.Toplevel):
    """Interactive popup panel with weather info, search, forecast, and animations."""

    def __init__(self, master, weather_data: dict, on_refresh=None, on_close=None,
                 on_city_change=None, on_toggle_unit=None):
        super().__init__(master)

        self.on_refresh = on_refresh
        self.on_close_callback = on_close
        self.on_city_change = on_city_change
        self.on_toggle_unit = on_toggle_unit
        self.weather_data = weather_data
        self._current_alpha = 0.0

        # Window configuration
        self.title("Weather")
        self.overrideredirect(True)  # Remove title bar
        self.configure(bg=COLORS["bg"])
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.0)  # Start invisible for fade-in

        # Panel dimensions
        self.panel_width = 420
        self.panel_height = 680

        # Position near system tray (bottom-right)
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = screen_w - self.panel_width - 20
        y = screen_h - self.panel_height - 60
        self.geometry(f"{self.panel_width}x{self.panel_height}+{x}+{y}")

        # Dragging support
        self._drag_data = {"x": 0, "y": 0}

        # Close on Escape
        self.bind("<Escape>", lambda e: self._close())

        # Build UI
        self._build_ui()

        # Fade-in animation
        self.after(10, self._fade_in)

        # Grab focus
        self.after(100, self.focus_force)

    # ── Fade-in animation ──

    def _fade_in(self):
        """Smoothly fade in the panel."""
        self._current_alpha += 0.08
        if self._current_alpha >= 0.96:
            self._current_alpha = 0.96
            self.attributes("-alpha", self._current_alpha)
            return
        self.attributes("-alpha", self._current_alpha)
        self.after(15, self._fade_in)

    def _fade_out_and_close(self):
        """Smoothly fade out then close."""
        self._current_alpha -= 0.1
        if self._current_alpha <= 0:
            self._do_close()
            return
        self.attributes("-alpha", self._current_alpha)
        self.after(15, self._fade_out_and_close)

    # ── Drag support ──

    def _start_drag(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _on_drag(self, event):
        x = self.winfo_x() + event.x - self._drag_data["x"]
        y = self.winfo_y() + event.y - self._drag_data["y"]
        self.geometry(f"+{x}+{y}")

    # ── Build UI ──

    def _build_ui(self):
        data = self.weather_data

        # Scrollable area via canvas
        canvas = tk.Canvas(self, bg=COLORS["bg"], highlightthickness=0, bd=0)
        canvas.pack(fill="both", expand=True)

        main = tk.Frame(canvas, bg=COLORS["bg"], padx=24, pady=18)
        canvas.create_window((0, 0), window=main, anchor="nw", width=self.panel_width)

        # Enable dragging on the main frame
        main.bind("<Button-1>", self._start_drag)
        main.bind("<B1-Motion>", self._on_drag)

        # ── Header: Close + Title ──
        header = tk.Frame(main, bg=COLORS["bg"])
        header.pack(fill="x", pady=(0, 10))

        title_label = tk.Label(
            header, text="Weather", font=("Segoe UI", 11),
            fg=COLORS["text_secondary"], bg=COLORS["bg"],
        )
        title_label.pack(side="left")

        close_btn = tk.Label(
            header, text="✕", font=("Segoe UI", 14, "bold"),
            fg=COLORS["text_secondary"], bg=COLORS["bg"], cursor="hand2",
        )
        close_btn.pack(side="right")
        close_btn.bind("<Button-1>", lambda e: self._close())
        self._add_hover(close_btn, fg_hover=COLORS["text_accent"], fg_normal=COLORS["text_secondary"])

        # ── Search Bar ──
        search_frame = tk.Frame(main, bg=COLORS["bg_search"], padx=2, pady=2,
                                highlightbackground=COLORS["border"], highlightthickness=1)
        search_frame.pack(fill="x", pady=(0, 14))

        search_inner = tk.Frame(search_frame, bg=COLORS["bg_search"])
        search_inner.pack(fill="x", padx=8, pady=6)

        search_icon = tk.Label(
            search_inner, text="🔍", font=("Segoe UI", 12),
            fg=COLORS["text_secondary"], bg=COLORS["bg_search"],
        )
        search_icon.pack(side="left", padx=(0, 6))

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_inner, textvariable=self.search_var,
            font=("Segoe UI", 13), fg=COLORS["text_primary"],
            bg=COLORS["bg_search"], insertbackground=COLORS["text_accent"],
            bd=0, highlightthickness=0,
        )
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.insert(0, "Search city...")
        self.search_entry.config(fg=COLORS["text_secondary"])

        # Search bar focus/blur behavior
        self.search_entry.bind("<FocusIn>", self._on_search_focus)
        self.search_entry.bind("<FocusOut>", self._on_search_blur)
        self.search_entry.bind("<Return>", self._on_search_submit)

        # Highlight border on focus
        def _highlight_search(e):
            search_frame.config(highlightbackground=COLORS["search_border"])
        def _unhighlight_search(e):
            search_frame.config(highlightbackground=COLORS["border"])
        self.search_entry.bind("<FocusIn>", lambda e: (_highlight_search(e), self._on_search_focus(e)), add=False)
        self.search_entry.bind("<FocusOut>", lambda e: (_unhighlight_search(e), self._on_search_blur(e)), add=False)

        search_btn = tk.Label(
            search_inner, text="→", font=("Segoe UI", 16, "bold"),
            fg=COLORS["text_accent"], bg=COLORS["bg_search"], cursor="hand2",
        )
        search_btn.pack(side="right", padx=(6, 0))
        search_btn.bind("<Button-1>", self._on_search_submit)

        # ── City name ──
        city_text = data.get("name", "Unknown")
        country = data.get("country", "")
        if country:
            city_text += f", {country}"

        city_label = tk.Label(
            main, text=f"📍 {city_text}",
            font=("Segoe UI", 16, "bold"),
            fg=COLORS["text_city"], bg=COLORS["bg"],
            anchor="w", cursor="hand2",
        )
        city_label.pack(fill="x", pady=(0, 6))
        # Tooltip on hover
        self._add_tooltip(city_label, "Click search bar to change city")

        # ── Weather Card (hoverable) ──
        card = tk.Frame(main, bg=COLORS["bg_card"], padx=24, pady=20)
        card.pack(fill="x", pady=(0, 14))
        self._add_card_hover(card, COLORS["bg_card"], COLORS["bg_card_hover"])

        # Condition
        emoji = data.get("emoji", "❓")
        desc = data.get("description", "Unknown")
        condition_label = tk.Label(
            card, text=f"{emoji}  {desc}",
            font=("Segoe UI", 17),
            fg=COLORS["text_primary"], bg=COLORS["bg_card"],
        )
        condition_label.pack(pady=(0, 10))

        # Temperature
        temp = data.get("temperature", "--")
        unit = data.get("unit_symbol", "°C")
        temp_label = tk.Label(
            card, text=f"{temp}{unit}",
            font=("Segoe UI", 54, "bold"),
            fg=COLORS["text_temp"], bg=COLORS["bg_card"],
        )
        temp_label.pack(pady=(0, 4))

        # Feels like
        feels = data.get("feels_like", "--")
        feels_label = tk.Label(
            card, text=f"Feels like {feels}{unit}",
            font=("Segoe UI", 12),
            fg=COLORS["text_secondary"], bg=COLORS["bg_card"],
        )
        feels_label.pack(pady=(0, 4))

        # Store card children for hover color sync
        self._card_children = [condition_label, temp_label, feels_label]

        # ── Stats row (hoverable cards) ──
        stats_frame = tk.Frame(main, bg=COLORS["bg"])
        stats_frame.pack(fill="x", pady=(0, 14))

        stats = [
            ("💧", f"{data.get('humidity', '--')}%", "Humidity"),
            ("💨", f"{data.get('wind_speed', '--')} km/h", "Wind"),
            ("🌡️", f"{data.get('temp_min', '--')}–{data.get('temp_max', '--')}", "Lo – Hi"),
        ]

        for i, (icon, value, label) in enumerate(stats):
            stat_card = tk.Frame(stats_frame, bg=COLORS["bg_stat"], padx=10, pady=12)
            stat_card.grid(row=0, column=i, padx=5, sticky="nsew")
            stats_frame.columnconfigure(i, weight=1)

            icon_lbl = tk.Label(
                stat_card, text=icon, font=("Segoe UI", 18),
                fg=COLORS["text_primary"], bg=COLORS["bg_stat"],
            )
            icon_lbl.pack()
            val_lbl = tk.Label(
                stat_card, text=value, font=("Segoe UI", 12, "bold"),
                fg=COLORS["text_primary"], bg=COLORS["bg_stat"],
            )
            val_lbl.pack(pady=(4, 2))
            lbl_lbl = tk.Label(
                stat_card, text=label, font=("Segoe UI", 9),
                fg=COLORS["text_secondary"], bg=COLORS["bg_stat"],
            )
            lbl_lbl.pack()

            # Hover effect on stat cards
            self._add_card_hover(stat_card, COLORS["bg_stat"], COLORS["bg_stat_hover"],
                                 children=[icon_lbl, val_lbl, lbl_lbl])

        # ── 3-Day Forecast ──
        forecast = data.get("forecast", [])
        if forecast:
            forecast_title = tk.Label(
                main, text="3-Day Forecast",
                font=("Segoe UI", 13, "bold"),
                fg=COLORS["text_primary"], bg=COLORS["bg"],
                anchor="w",
            )
            forecast_title.pack(fill="x", pady=(4, 8))

            for day in forecast:
                day_frame = tk.Frame(main, bg=COLORS["forecast_bg"], padx=14, pady=10)
                day_frame.pack(fill="x", pady=(0, 5))

                # Day name
                day_name = tk.Label(
                    day_frame, text=f"{day['day_name']}",
                    font=("Segoe UI", 12, "bold"),
                    fg=COLORS["text_primary"], bg=COLORS["forecast_bg"],
                    width=5, anchor="w",
                )
                day_name.pack(side="left")

                # Date
                day_date = tk.Label(
                    day_frame, text=f"{day['date']}",
                    font=("Segoe UI", 10),
                    fg=COLORS["text_secondary"], bg=COLORS["forecast_bg"],
                    width=7, anchor="w",
                )
                day_date.pack(side="left", padx=(4, 0))

                # Emoji
                day_emoji = tk.Label(
                    day_frame, text=day["emoji"],
                    font=("Segoe UI", 14),
                    fg=COLORS["text_primary"], bg=COLORS["forecast_bg"],
                )
                day_emoji.pack(side="left", padx=(8, 8))

                # Description
                day_desc = tk.Label(
                    day_frame, text=day["description"],
                    font=("Segoe UI", 10),
                    fg=COLORS["text_secondary"], bg=COLORS["forecast_bg"],
                    anchor="w",
                )
                day_desc.pack(side="left", fill="x", expand=True)

                # Temp range
                day_temp = tk.Label(
                    day_frame, text=f"{day['temp_min']}° / {day['temp_max']}°",
                    font=("Segoe UI", 11, "bold"),
                    fg=COLORS["text_accent"], bg=COLORS["forecast_bg"],
                )
                day_temp.pack(side="right")

                # Hover effect
                children = [day_name, day_date, day_emoji, day_desc, day_temp]
                self._add_card_hover(day_frame, COLORS["forecast_bg"], COLORS["forecast_hover"],
                                     children=children)

        # ── Bottom bar: Toggle + Refresh ──
        bottom = tk.Frame(main, bg=COLORS["bg"])
        bottom.pack(fill="x", pady=(12, 4))

        # Toggle °C / °F button
        is_celsius = unit == "°C"
        toggle_text = "°C" if is_celsius else "°F"
        toggle_btn = tk.Label(
            bottom, text=f"  {toggle_text}  ",
            font=("Segoe UI", 12, "bold"),
            fg=COLORS["button_fg"],
            bg=COLORS["toggle_on"] if is_celsius else COLORS["toggle_off"],
            cursor="hand2", padx=10, pady=6,
        )
        toggle_btn.pack(side="left")
        toggle_btn.bind("<Button-1>", lambda e: self._toggle_unit())
        self._add_hover(toggle_btn, bg_hover=COLORS["button_bg_hover"],
                        bg_normal=COLORS["toggle_on"] if is_celsius else COLORS["toggle_off"])

        # Last updated
        fetched = data.get("fetched_at", "--")
        updated = tk.Label(
            bottom, text=f"Updated: {fetched}",
            font=("Segoe UI", 9),
            fg=COLORS["text_secondary"], bg=COLORS["bg"],
        )
        updated.pack(side="left", padx=(12, 0))

        # Refresh button
        refresh_btn = tk.Label(
            bottom, text="  🔄 Refresh  ",
            font=("Segoe UI", 12, "bold"),
            fg=COLORS["button_fg"], bg=COLORS["button_bg"],
            cursor="hand2", padx=10, pady=6,
        )
        refresh_btn.pack(side="right")
        refresh_btn.bind("<Button-1>", lambda e: self._refresh())
        self._add_hover(refresh_btn, bg_hover=COLORS["button_bg_hover"], bg_normal=COLORS["button_bg"])

    # ── Search bar handlers ──

    def _on_search_focus(self, event):
        if self.search_entry.get() == "Search city...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg=COLORS["text_primary"])

    def _on_search_blur(self, event):
        if not self.search_entry.get().strip():
            self.search_entry.insert(0, "Search city...")
            self.search_entry.config(fg=COLORS["text_secondary"])

    def _on_search_submit(self, event=None):
        city = self.search_var.get().strip()
        if city and city != "Search city..." and self.on_city_change:
            self.on_city_change(city)
            self._close()

    # ── Hover helpers ──

    def _add_hover(self, widget, fg_hover=None, fg_normal=None, bg_hover=None, bg_normal=None):
        """Add hover color change to a widget."""
        def on_enter(e):
            if fg_hover:
                widget.config(fg=fg_hover)
            if bg_hover:
                widget.config(bg=bg_hover)
        def on_leave(e):
            if fg_normal:
                widget.config(fg=fg_normal)
            if bg_normal:
                widget.config(bg=bg_normal)
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def _add_card_hover(self, frame, bg_normal, bg_hover, children=None):
        """Add hover effect to a card frame and optionally its children."""
        all_widgets = [frame] + (children or [])

        def on_enter(e):
            for w in all_widgets:
                try:
                    w.config(bg=bg_hover)
                except tk.TclError:
                    pass

        def on_leave(e):
            for w in all_widgets:
                try:
                    w.config(bg=bg_normal)
                except tk.TclError:
                    pass

        for w in all_widgets:
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)

    def _add_tooltip(self, widget, text):
        """Add a simple tooltip to a widget."""
        tip = None

        def show(e):
            nonlocal tip
            tip = tk.Toplevel(widget)
            tip.overrideredirect(True)
            tip.attributes("-topmost", True)
            x = e.x_root + 15
            y = e.y_root + 10
            tip.geometry(f"+{x}+{y}")
            lbl = tk.Label(tip, text=text, font=("Segoe UI", 9),
                           fg="#ffffff", bg="#333333", padx=8, pady=4)
            lbl.pack()

        def hide(e):
            nonlocal tip
            if tip:
                tip.destroy()
                tip = None

        widget.bind("<Enter>", show)
        widget.bind("<Leave>", hide)

    # ── Actions ──

    def _refresh(self):
        self._close()
        if self.on_refresh:
            self.on_refresh()

    def _toggle_unit(self):
        self._close()
        if self.on_toggle_unit:
            self.on_toggle_unit()

    def _close(self):
        self._fade_out_and_close()

    def _do_close(self):
        try:
            self.destroy()
        except tk.TclError:
            pass
        if self.on_close_callback:
            self.on_close_callback()
