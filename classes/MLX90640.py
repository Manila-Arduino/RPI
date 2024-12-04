import time
import board
import busio
import numpy as np
import adafruit_mlx90640
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from PyQt5 import QtCore
from typing import Callable, Optional
import matplotlib.backend_bases as mpl_cursor
from PyQt5.QtGui import QPixmap, QCursor, QPainter, QColor, QPen
from PyQt5.QtCore import Qt

n_detects = 30
temp_diff_min = 5


def _usage():
    #! MLX90640
    mlx90640 = MLX90640()
    mlx90640.update(35, 99)


class MLX90640:
    def __init__(
        self,
        refresh_rate: adafruit_mlx90640.RefreshRate = adafruit_mlx90640.RefreshRate.REFRESH_4_HZ,
        max_retries: int = 5,
        vmin: float = 0.0,
        vmax: float = 60.0,
        cmap: str = "inferno",
        plot_size: tuple = (4, 2),
    ):
        plt.rcParams["toolbar"] = "none"
        self.refresh_rate = refresh_rate
        self.max_retries = max_retries
        self.vmin = vmin
        self.vmax = vmax
        self.cmap = cmap
        self.plot_size = plot_size
        self.frame = np.zeros((24 * 32,))
        self.data_array = np.zeros((24, 32))
        self.t_array = []

        self.last_n_temps = []

        # Initialize sensor
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.mlx = adafruit_mlx90640.MLX90640(self.i2c)
        self.mlx.refresh_rate = self.refresh_rate

        # Initialize plot
        self.fig, self.ax, self.therm1 = self._setup_plot()

    def _setup_plot(self):
        plt.ion()
        fig, ax = plt.subplots(figsize=self.plot_size)
        therm1 = ax.imshow(
            np.zeros((24, 32)),
            vmin=self.vmin,
            vmax=self.vmax,
            cmap=self.cmap,
            interpolation="bilinear",
        )
        cbar = fig.colorbar(therm1)
        cbar.set_label("Temperature [°C]", fontsize=14)
        # plt.title("Thermal Image")

        # Add a warning or label at the bottom of the figure
        self.description_text = plt.figtext(
            0.5,
            0.05,  # Position (x, y) in figure coordinates (0.5 is centered, 0.01 is near bottom)
            "Normal",
            ha="center",  # Horizontal alignment
            fontsize=10,  # Font size
            color="red",  # Text color
            weight="bold",  # Make it bold
        )

        # Add dynamic temperature display
        self.selected_y = 12
        self.selected_x = 16
        selected_temp = np.fliplr(self.data_array)[self.selected_y, self.selected_x]
        self.temperature_text = plt.figtext(
            0.5,
            0.92,  # Position (x, y) near the top
            f"Selected Temp: {selected_temp:.2f} °C",
            ha="center",
            fontsize=15,
            color="blue",
            weight="bold",
        )

        self.amb_temp_text = plt.figtext(
            0.05,
            0.95,  # Position (x, y) near the top
            f"AT: 0.0 °C",
            fontsize=10,
            color="black",
            weight="bold",
        )

        self.amb_hum_text = plt.figtext(
            0.05,
            0.90,  # Position (x, y) near the top
            f"AH: 0.0 %",
            fontsize=10,
            color="black",
            weight="bold",
        )

        # Remove x and y labels
        ax.axis("off")

        # Set fullscreen mode
        manager = plt.get_current_fig_manager()
        window = manager.window
        window.setWindowFlags(window.windowFlags() | QtCore.Qt.FramelessWindowHint)
        window.showFullScreen()

        # Center the cursor on the image
        def center_cursor():
            QCursor.setPos(210, 160)

        # Call this function after the window is displayed
        fig.canvas.draw_idle()
        center_cursor()

        # Customize the coordinate display to show temperature
        def custom_coord(x, y):
            row = int(y)
            col = int(x)
            if 0 <= row < 24 and 0 <= col < 32:
                temp = self.data_array[row, col]
                return f"Temp: {temp:.2f} °C"
            return "Temp: -- °C"

        ax.format_coord = custom_coord

        # Define the click event
        def on_click(event):
            if event.inaxes == ax:
                self.selected_x, self.selected_y = int(event.xdata), int(event.ydata)

        # Connect the click event to the figure
        fig.canvas.mpl_connect("button_press_event", on_click)

        # Create and set a custom crosshair cursor
        crosshair_size = 50  # Increase this value to make the crosshair larger
        pixmap = QPixmap(crosshair_size, crosshair_size)
        pixmap.fill(Qt.transparent)  # Transparent background

        painter = QPainter(pixmap)
        # pen_color = QColor("black")
        pen_color = QColor(0, 255, 0)
        pen_thickness = 4  # Increase this value for thicker lines
        pen = QPen(pen_color)
        pen.setWidth(pen_thickness)
        painter.setPen(pen)

        # Draw horizontal and vertical lines for the crosshair
        painter.drawLine(crosshair_size // 2, 0, crosshair_size // 2, crosshair_size)
        painter.drawLine(0, crosshair_size // 2, crosshair_size, crosshair_size // 2)
        painter.end()

        custom_cursor = QCursor(pixmap)

        window.setCursor(custom_cursor)

        return fig, ax, therm1

    def _update_display(self, ambient_temp: float, ambient_humidity: float):
        temp = 0
        if 0 <= self.selected_y < 24 and 0 <= self.selected_x < 32:
            temp = np.fliplr(self.data_array)[self.selected_y, self.selected_x]

            self.temperature_text.set_text(f"{temp:.2f} °C")
            # self.fig.canvas.draw_idle()

        if temp != 0 and len(self.last_n_temps) < n_detects:
            self.last_n_temps = [temp] * n_detects

        elif temp != 0:
            self.last_n_temps.pop(0)
            self.last_n_temps.append(temp)

        is_fluctuating = (
            len(self.last_n_temps) > 0
            and max(self.last_n_temps) - min(self.last_n_temps) > temp_diff_min
        )

        print(f"temp: {temp}, type: {type(temp)} temp > 4: {temp > 4}")

        print(len(set(self.last_n_temps)) == n_detects)
        print(max(self.last_n_temps))
        print(min(self.last_n_temps))
        print(max(self.last_n_temps) - min(self.last_n_temps))
        print(max(self.last_n_temps) - min(self.last_n_temps) > temp_diff_min)

        if temp > 70:
            self.description_text.set_text(
                "Device Overheating or Malfunction. Check the equipment"
            )
        elif temp > 50:
            self.description_text.set_text(
                "Extreme Temperatures (High). Check the equipment"
            )

        elif temp > 40:
            self.description_text.set_text(
                "Abnormal Temperature Detected. Check the equipment"
            )

        elif temp < -10:
            self.description_text.set_text(
                "Extreme Temperatures (Low). Check the equipment"
            )

        elif is_fluctuating:
            self.description_text.set_text(
                "Rapid Temperature Changes. Check the equipment"
            )

        else:
            self.description_text.set_text("Normal Temperature")

        # Ambient temperature and humidity
        self.amb_temp_text.set_text(f"AT: {ambient_temp:.2f} °C")
        self.amb_hum_text.set_text(f"AH: {ambient_humidity:.2f} %")
        self.fig.canvas.draw_idle()

        self.therm1.set_data(np.fliplr(self.data_array))
        self.therm1.set_clim(vmin=np.min(self.data_array), vmax=np.max(self.data_array))
        self.ax.draw_artist(self.ax.patch)
        self.ax.draw_artist(self.therm1)
        self.fig.canvas.update()
        self.fig.canvas.flush_events()

    def update(self, ambient_temp: float, ambient_humidity: float):
        t1 = time.monotonic()
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                self.mlx.getFrame(self.frame)
                self.data_array = np.reshape(self.frame, (24, 32))

                self._update_display(ambient_temp, ambient_humidity)
                plt.pause(0.001)
                self.t_array.append(time.monotonic() - t1)
                print(
                    "Sample Rate: {0:2.1f}fps".format(
                        len(self.t_array) / np.sum(self.t_array)
                    )
                )
                break
            except ValueError:
                retry_count += 1
            except RuntimeError as e:
                retry_count += 1
                if retry_count >= self.max_retries:
                    print(f"Failed after {self.max_retries} retries with error: {e}")
                    return
