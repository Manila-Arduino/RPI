import time
import board
import busio
import numpy as np
import adafruit_mlx90640
import matplotlib.pyplot as plt


def _usage():
    """
    pip install matplotlib
    pip install scipy
    pip install numpy
    sudo apt install -y python-smbus
    sudo apt install -y i2c-tools
    sudo nano /boot/config.txt

        Note: under #Uncomment some or all of these to enable the ...
            dtparam=i2c_arm=on, i2c_arm_baudrate=400000

    sudo reboot
    sudo i2cdetect -y 1

    sudo pip install RPI.GPIO adafruit-blinka
    sudo pip install adafruit-circuitpython-mlx90640
    """
    #! MLX90640
    mlx90640 = MLX90640()
    mlx90640.capture()


class MLX90640:
    def __init__(self, address=0x33):
        i2c = busio.I2C(board.SCL, board.SDA)
        mlx = adafruit_mlx90640.MLX90640(i2c)
        mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_4_HZ
        plt.ion()
        fig, ax = plt.subplots(figsize=(12, 7))
        therm1 = ax.imshow(
            np.zeros((24, 32)),
            vmin=0,
            vmax=60,
            cmap="inferno",
            interpolation="bilinear",
        )
        cbar = fig.colorbar(therm1)
        cbar.set_label("Temperature [°C]", fontsize=14)
        plt.title("Thermal Image")

        frame = np.zeros((24 * 32,))
        t_array = []
        max_retries = 5

        while True:
            t1 = time.monotonic()
            retry_count = 0
            while retry_count < max_retries:
                try:
                    mlx.getFrame(frame)
                    data_array = np.reshape(frame, (24, 32))

                    #! Update
                    self.update_display(fig, ax, therm1, data_array)

                    plt.pause(0.001)
                    t_array.append(time.monotonic() - t1)
                    print(
                        "Sample Rate: {0:2.1f}fps".format(
                            len(t_array) / np.sum(t_array)
                        )
                    )
                    break
                except ValueError:
                    retry_count += 1
                except RuntimeError as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        print(f"Failed after {max_retries} retries with error: {e}")
                        break

    def capture(self):
        return self.read()

    def update_display(self, fig, ax, therm1, data_array):
        therm1.set_data(np.fliplr(data_array))
        therm1.set_clim(vmin=np.min(data_array), vmax=np.max(data_array))
        ax.draw_artist(ax.patch)
        ax.draw_artist(therm1)
        fig.canvas.update()
        fig.canvas.flush_events()
