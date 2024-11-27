from datetime import datetime
import threading
import gpiozero


def _usage():
    #! RELAY
    relay = Relay(26, active_high=True)
    relay.on()
    relay.off()
    relay.toggle()
    relay.is_on()


class Relay:
    def __init__(self, pin: int, active_high: bool = False):
        self.relay = gpiozero.OutputDevice(
            pin, active_high=active_high, initial_value=False
        )
        self.relay.off()
        self.last_on = datetime.now()

    def on(self, seconds: int = 0, interval_s: int = 0):
        if interval_s > 0:
            now = datetime.now()
            if (now - self.last_on).seconds < interval_s:
                return

        self.relay.on()
        self.last_on = datetime.now()

        if seconds > 0:
            timer = threading.Timer(seconds, self.off)
            timer.start()

    def off(self):
        self.relay.off()

    def toggle(self):
        self.relay.toggle()

    def is_on(self):
        return self.relay.value
