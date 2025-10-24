import matplotlib.pyplot as plt
import numpy as np
import io
from datetime import datetime, timezone, timedelta
# --- Data Scaling Function ---
def scale_ohlc_data(data, scale_factor):
    """
    Multiplies the OHLC values by the scale_factor and rounds them
    to 2 decimal places.
    """
    scaled_data = []
    for item in data:
        date_obj = item[0]
        ohlc_values = item[1:]

        # Rounding to 2 decimal places
        scaled_ohlc = [round(value * scale_factor, 2) for value in ohlc_values]

        scaled_item = (date_obj,) + tuple(scaled_ohlc)
        scaled_data.append(scaled_item)
    return scaled_data

# --- CustomCandlestick Class ---
class CustomCandlestick:
    def __init__(self, data, graphic='triangle', width=0.4):
        self.data = data
        self.graphic = graphic
        self.width = width

        # Set figure and axes background to BLACK
        self.fig, self.ax = plt.subplots(figsize=(18, 8))
        self.fig.patch.set_facecolor('#111111')
        self.ax.set_facecolor('#111111')
        plt.switch_backend('Agg') # Commented out for local testing

    def _plot_rocket(self, x, open_price, high, low, close_price, color, label=None):

        # --- 1. Draw the High-Low Wick ---
        self.ax.plot([x, x], [low, high], color='#D1D5DB', linewidth=1, alpha=0.6, zorder=1)

        # --- 2. Determine Candle Geometry ---
        is_bullish = close_price > open_price
        y_tip = close_price
        y_base = open_price

        # Doji protection
        body_height_abs = abs(open_price - close_price)
        if body_height_abs == 0:
             range_h_l = high - low
             if range_h_l == 0: range_h_l = 0.001
             min_height = 0.005 * range_h_l
             if is_bullish: y_tip += min_height
             else: y_tip -= min_height
        rocket_width = self.width * 0.8
        half_body_width = round(rocket_width / 2,2)
        # Base Cap Configuration (Two Overlapping Circles)
        point_size = 500
        offset = half_body_width * 1.2
        x1 = x - offset
        x2 = x + offset
        # Top Cap Configuration (Single Large Circle)
        top_cap_size = (half_body_width ** 2) * 10000*0.78
        if is_bullish:
            y_body_top = y_tip      # Close Price
            y_body_bottom = y_base  # Open Price

            # X_body/Y_body define a simple RECTANGLE
            X_body = [x - half_body_width, x - half_body_width, x + half_body_width, x + half_body_width]
            Y_body = [y_body_top, y_body_bottom, y_body_bottom, y_body_top]

            # 1. Base Cap (Two smaller circles at the OPEN price)
            self.ax.scatter([x1, x2], [y_body_bottom, y_body_bottom],
                            s=point_size, color=color, alpha=1, zorder=2, marker='o')

            # 2. Top Cap (Single large circle at the CLOSE price)
            self.ax.scatter([x], [y_body_top],
                            s=top_cap_size, color=color, alpha=1, zorder=2, marker='o')

        else: # Bearish (Open > Close)
            y_body_top = y_base      # Open Price (The highest point of the body)
            y_body_bottom = y_tip    # Close Price (The lowest point of the body)

            # X_body/Y_body define a simple RECTANGLE
            X_body = [x - half_body_width, x - half_body_width, x + half_body_width, x + half_body_width]
            Y_body = [y_body_top, y_body_bottom, y_body_bottom, y_body_top]

            # --- FIX: SWAP CAP PLACEMENT ---

            # 1. Base Cap (Two smaller circles) MUST be at the OPEN price (y_body_top)
            # This is the original base of the rocket
            self.ax.scatter([x1, x2], [y_body_top, y_body_top],
                            s=point_size, color=color, alpha=1, zorder=2, marker='o')

            # 2. Top Cap (Single large circle) MUST be at the CLOSE price (y_body_bottom)
            # This is the new rounded tip of the rocket
            self.ax.scatter([x], [y_body_bottom],
                            s=top_cap_size, color=color, alpha=1, zorder=2, marker='o')
            # -------------------------------

        # Draw the filled body (now a rectangle)
        self.ax.fill(X_body, Y_body, color=color, alpha=1, zorder=2)


    def plot(self, title="Candlestick Chart", xlabel="Date", ylabel="Price"):

        # REMOVED label generation logic (has_bullish_drawn, label_text)

        for i, (date, open_price, high, low, close) in enumerate(self.data):
            color = '#1ECD1E' if close >= open_price else '#FC413B'

            # Note: label_text is no longer generated or used
            if self.graphic == 'triangle':
                # Pass None for label, or ensure _plot_rocket handles its absence
                self._plot_rocket(i, open_price, high, low, close, color, label=None)

        # ADD TITLE AND LABELS (Set colors to white for dark mode)
        self.ax.set_title(title, color='white')
        self.ax.set_xlabel(xlabel, color='white')
        self.ax.set_ylabel(ylabel, color='white')

        # REMOVE GRID
        self.ax.grid(False)

        # COMMENTED OUT: Legend rendering is intentionally removed
        # self.ax.legend(...)

        # Set tick and spine colors to white
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        self.ax.spines['left'].set_color('white')
        self.ax.spines['right'].set_color('white')
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('white')


        # X-AXIS HANDLING
        if self.data and isinstance(self.data[0][0], datetime):
            dates = [item[0] for item in self.data]
            self.ax.set_xticks(range(len(dates)))

            step = max(1, len(dates) // 15)
            labels = [''] * len(dates)
            for i in range(0, len(dates), step):
                labels[i] = dates[i].strftime('%H:%M')
                if i == 0 or dates[i].date() != dates[i-step].date():
                     labels[i] = dates[i].strftime('%m-%d %H:%M')

            self.ax.set_xticklabels(labels, rotation=45, ha='right')
        else:
            self.ax.set_xticks(range(len(self.data)))

        if self.data:
            self.ax.set_xlim(-self.width * 2, len(self.data) - 1 + self.width * 2)

        # Y-AXIS SCALING
        if self.data:
            all_lows = [item[3] for item in self.data]
            all_highs = [item[2] for item in self.data]
            if all_highs and all_lows:
                min_y = min(all_lows)
                max_y = max(all_highs)
                padding = (max_y - min_y) * 0.10
                self.ax.set_ylim(min_y - padding, max_y + padding)

        plt.tight_layout()

    # --- ADDED FOR LOCAL TESTING ---
    def show_chart(self):
        """Displays the chart interactively for local testing/viewing."""
        plt.show()

    # --- KEPT FOR PRODUCTION USE ---
    def get_image_buffer(self):
        """Saves the chart to an in-memory BytesIO buffer, preserving dark theme."""
        buf = io.BytesIO()
        self.fig.savefig(
            buf,
            format='png',
            bbox_inches='tight',
            facecolor=self.fig.get_facecolor()
        )
        plt.close(self.fig)
        buf.seek(0)
        return buf