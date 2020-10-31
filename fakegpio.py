"""
    fakegpio

    Ein Ersatzmodul fuer nicht RaspberryPis.
    So koennen Syntax und einfache Programmlogik ueberprueft werden.

    :author: Akida31
    :license: MIT
"""

from time import sleep
from threading import Thread
from random import randint


class GPIO:
    # Konstanten sind aus RPi.GPIO uebernommen
    BCM = 11
    BOARD = 10
    BOTH = 33
    FALLING = 32
    HARD_PWM = 43
    HIGH = 1
    I2C = 42
    IN = 1
    LOW = 0
    OUT = 0
    PUD_DOWN = 21
    PUD_UP = 22
    RISING = 31
    RPI_REVISION = 0
    RPI_INFO = {}
    SERIAL = 40
    SPI = 41
    UNKNOWN = - 1
    VERSION = "0.7.0"

    # Methodennamen und Erklaerungen sind auch uebernommen,
    # nur der Inhalt wurde geaendert
    def __init__(self):
        """
        erstelle ein neues Fake-GPIO-Objekt
        """
        self.mode = None
        self.channels = {}
        self.events = []

    def _callback(self, channel, callback):
        """Funktion, die fuer den event_callback genutzt wird
        Sie ruft die gewuenschte Funktion nach 5-10 Sekunden auf
        :param channel: Der channel mit Änderung
        :param callback: Die Callbackfunktion
        """
        sleep(randint(5, 10))
        if channel in self.events:
            callback(channel)

    def _check_mode(self):
        """
        checkt, ob schon ein mode gesetzt wurde
        :raises: RuntimeError
        """
        if self.mode is None:
            raise RuntimeError("Please set pin numbering mode using GPIO.setmode(GPIO.BOARD) or GPIO.setmode(GPIO.BCM)")

    def _check_channel_input(self, channel):
        """
        checkt, ob der channel als input gesetzt wurde
        :raises: RuntimeError
        """
        if self.channels.get(channel) != GPIO.IN:
            raise RuntimeError("You must setup() the GPIO channel as an input first")

    def add_event_callback(self, channel, callback):
        """Add a callback for an event already defined using add_event_detect()
        channel      - either board pin number or BCM number depending on which mode is set.
        callback     - a callback function"""
        self._check_mode()
        self._check_channel_input(channel)
        if channel not in self.events:
            raise RuntimeError("Add event detection using add_event_detect first before adding a callback")
        print(f"event callback fuer channel {channel} hinzugefuegt: {callback}")
        thread = Thread(target=self._callback, args=(channel, callback))
        thread.start()

    def add_event_detect(self, channel, edge, callback=None, bouncetime=None):
        """Enable edge detection events for a particular GPIO channel.
        channel      - either board pin number or BCM number depending on which mode is set.
        edge         - RISING, FALLING or BOTH
        [callback]   - A callback function for the event (optional)
        [bouncetime] - Switch bounce timeout in ms for callback"""
        self._check_mode()
        self._check_channel_input(channel)
        if edge == GPIO.RISING:
            edge = "rising"
        elif edge == GPIO.FALLING:
            edge = "falling"
        elif edge == GPIO.BOTH:
            edge = "both"
        else:
            raise ValueError("The edge must be set to RISING, FALLING or BOTH")
        print(f"event detect fuer channel {channel} fuer {edge} und bouncetime {bouncetime}ms")
        if callback:
            self.add_event_callback(channel, callback)

    def cleanup(self, channel=None):
        """Clean up by resetting all GPIO channels that have been used by this program to INPUT with no
            pullup/pulldown and no event detection
        [channel] - individual channel or list/tuple of channels to clean up.
        Default - clean every channel that has been used. """
        if channel:
            if type(channel) == int:
                channel = [channel]
            for c in channel:
                del self.channels[c]
                print(f"cleanup von channel {c}")
        else:
            print("cleanup")
            self.channels = {}

    def event_detected(self, channel):
        """Returns True if an edge has occurred on a given GPIO.
        You need to enable edge detection using add_event_detect() first.
        channel - either board pin number or BCM number depending on which mode is set."""
        self._check_mode()
        return bool(randint(0, 1))

    def getmode(self):
        """Get numbering mode used for channel numbers.
        Returns BOARD, BCM or None"""
        return self.mode

    def gpio_function(self, channel):
        """Return the current GPIO function (IN, OUT, PWM, SERIAL, I2C, SPI)
        channel - either board pin number or BCM number depending on which mode is set."""
        self._check_mode()
        return self.channels.get(channel)

    def input(self, channel):
        """Input from a GPIO channel.  Returns HIGH=1=True or LOW=0=False
        channel - either board pin number or BCM number depending on which mode is set."""
        self._check_mode()
        if channel not in self.channels:
            raise RuntimeError("You must setup() the GPIO channel first")
        print(f"input fuer channel {channel}")
        return randint(0, 1)

    def output(self, channel, value):
        """Output to a GPIO channel or list of channels
        channel - either board pin number or BCM number depending on which mode is set.
        value   - 0/1 or False/True or LOW/HIGH"""
        self._check_mode()
        if channel in self.channels:
            print(f"output fuer channel {channel} auf {value} gesetzt")
        else:
            raise RuntimeError("The GPIO channel has not been set up as an OUTPUT")

    def remove_event_detect(self, channel):
        """Remove edge detection for a particular GPIO channel
        channel - either board pin number or BCM number depending on which mode is set."""
        self._check_mode()
        self.events.remove(channel)
        print(f"event detect fuer channel {channel} entfernt")

    def setmode(self, mode):
        """
        Set up numbering mode to use for channels.
        BOARD - Use Raspberry Pi board numbers
        BCM   - Use Broadcom GPIO 00..nn numbers
        """
        if mode in [GPIO.BCM, GPIO.BOARD]:
            self.mode = mode
            print(f"Modus auf {mode} gesetzt")
        else:
            raise ValueError("An invalid mode was passed to setmode()")

    def setup(self, channel: int, direction: int, pull_up_down=None, initial=None):
        """Set up a GPIO channel or list of channels with a direction and (optional) pull/up down control
        channel        - either board pin number or BCM number depending on which mode is set.
        direction      - IN or OUT
        [pull_up_down] - PUD_OFF (default), PUD_UP or PUD_DOWN
        [initial]      - Initial value for an output channel"""
        self._check_mode()
        if direction == GPIO.OUT:
            direction = "OUT"
        elif direction == GPIO.IN:
            direction = "IN"
        else:
            raise ValueError("An invalid direction was passed to setup()")
        self.channels[channel] = direction
        print(f"setup channel {channel} auf {direction} mit pull_up_down {pull_up_down} und initial {initial}")

    def setwarnings(self, on):
        """Enable or disable warning messages"""
        print(f"setwarnings: {on}")

    def wait_for_edge(self, channel, edge, bouncetime=None, timeout=None):
        """Wait for an edge.  Returns the channel number or None on timeout.
        channel      - either board pin number or BCM number depending on which mode is set.
        edge         - RISING, FALLING or BOTH
        [bouncetime] - time allowed between calls to allow for switchbounce
        [timeout]    - timeout in ms"""
        self._check_mode()
        self._check_channel_input(channel)
        if edge == GPIO.RISING:
            edge = "rising"
        elif edge == GPIO.FALLING:
            edge = "falling"
        elif edge == GPIO.BOTH:
            edge = "both"
        else:
            raise ValueError("The edge must be set to RISING, FALLING or BOTH")
        print(f"wait_for_edge mit channel {channel} edge {edge}, bouncetime {bouncetime} und timeout {timeout}")
        wartezeit = min(randint(5, 10), timeout / 1000)
        sleep(wartezeit)
