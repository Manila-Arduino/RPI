from classes.Button import Button
from classes.MLX90640 import MLX90640
from classes.Relay import Relay
from classes.ShutdownButton import ShutdownButton
from classes.Video import Video


#! VIDEO CAM
video = Video("/dev/video0", 480, 320, "d")


#! SHUTDOWN BUTTON
shutdown_button = ShutdownButton(16, 2)


#! BUTTON
button = Button(16, lambda: print("Button pressed!"))


#! RELAY
relay = Relay(26, active_high=True)
relay.on()
relay.off()
relay.toggle()
relay.is_on()

#! MLX90640
mlx90640 = MLX90640()
mlx90640.capture()


while True:
    if True:
        break


def main():
    pass


if __name__ == "__main__":
    main()
