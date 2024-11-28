import Adafruit_DHT as dht


def _usage():
    #! DHT22
    """
    git clone https://github.com/adafruit/Adafruit_Python_DHT.git
    cd Adafruit_Python_DHT
    sudo apt-get update
    sudo apt-get install build-essential python3-dev
    sudo apt install python3-setuptools
    sudo python3 setup.py install
    """
    shutdown_button = DHT22(16, 2)


class DHT22:
    def __init__(self, pin: int):
        self.pin = pin

    def read(self):
        h, t = dht.read_retry(dht.DHT22, self.pin)
        return t, h
