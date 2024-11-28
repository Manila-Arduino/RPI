from subprocess import call
from typing import Callable
from gpiozero import Button as GPIOButton
from time import sleep
from datetime import datetime


def _usage():
    #! BUTTON
    button = Button(16, lambda: print("Button pressed!"))


class Button:
    def __init__(
        self,
        pin: int,
        callback: Callable,
        press_interval_s: int = 1,
    ):
        self.pin = pin
        self.button = GPIOButton(self.pin)
        self.callback = callback
        self.button.when_pressed = self.on_pressed
        self.last_pressed = datetime.now()
        self.press_interval_s = press_interval_s

    def on_pressed(self):
        print(
            f"Button {self.pin} pressed: {(datetime.now() - self.last_pressed).total_seconds()} {self.press_interval_s}"
        )
        if (datetime.now() - self.last_pressed).total_seconds() < self.press_interval_s:
            return

        self.callback()
        self.last_pressed = datetime.now()
