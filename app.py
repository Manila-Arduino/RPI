from classes.ShutdownButton import ShutdownButton
from classes.Wrapper import Wrapper
from gpiozero.pins.lgpio import LGPIOFactory
from gpiozero import Device, PWMLED

Device.pin_factory = LGPIOFactory(chip=4)

# ? -------------------------------- CONSTANTS
shutdown_pin = 16

# ? -------------------------------- CLASSES
shutdown_button = ShutdownButton(shutdown_pin)

# ? -------------------------------- VARIABLES


# ? -------------------------------- FUNCTIONS


# ? -------------------------------- SETUP
def setup():
    pass


# ? -------------------------------- LOOP
def loop():
    pass


# ? -------------------------------- ETC
setup()


def onExit():
    pass

# 

Wrapper(
    loop,
    onExit=onExit,
    stop_key=None,
    keyboardEvents=[
        # ["d", video.save_image],  # type: ignore
    ],
)
