import time
import board
import busio
import numpy as np
import adafruit_mlx90640
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from PyQt5 import QtCore
from typing import Callable, Optional


def _usage():
    #! MLX90640
    mlx90640 = MLX90640()
    mlx90640.start()


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
        self.refresh_rate = refresh_rate
        self.max_retries = max_retries
        self.vmin = vmin
        self.vmax = vmax
        self.cmap = cmap
        self.plot_size = plot_size
        self.frame = np.zeros((24 * 32,))
        self.data_array = np.zeros((24, 32))
        self.t_array = []

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
        plt.title("Thermal Image")

        # Set fullscreen mode
        manager = plt.get_current_fig_manager()
        window = manager.window
        window.setWindowFlags(window.windowFlags() | QtCore.Qt.FramelessWindowHint)
        window.showFullScreen()

        return fig, ax, therm1

    def _update_display(self):
        self.therm1.set_data(np.fliplr(self.data_array))
        self.therm1.set_clim(vmin=np.min(self.data_array), vmax=np.max(self.data_array))
        self.ax.draw_artist(self.ax.patch)
        self.ax.draw_artist(self.therm1)
        self.fig.canvas.update()
        self.fig.canvas.flush_events()

    def update(self):
        t1 = time.monotonic()
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                self.mlx.getFrame(self.frame)
                self.data_array = np.reshape(self.frame, (24, 32))
                self._update_display()
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
