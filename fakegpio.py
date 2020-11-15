"""
    fakegpio

    Ein Ersatzmodul fuer RPi.GPIO, das auf Computern laeuft.
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

    # Methodennamen und Docstrings sind auch uebernommen,
    # nur der Inhalt wurde geaendert
    # deswegen sind auch die meisten Methodennamen, Docsstrings und Variablennamen auf Englisch
    def __init__(self):
        """
        erstelle ein neues Fake-GPIO-Objekt
        """
        # zu Beginn ist noch kein Modus gesetzt
        self.mode = None
        # zu Beginn sind noch keine Channels/ Pins konfiguriert
        self.channels = {}
        # es sind zu Beginn auch noch keine callbacks fuer events hinzugefuegt
        self.events = []

    def _callback(self, channel, callback):
        """Funktion, die fuer den event_callback genutzt wird
        Sie ruft die gewuenschte Funktion nach 5-10 Sekunden auf
        :param channel: Der channel mit Aenderung
        :param callback: Die Callbackfunktion
        """
        # warte eine zufaellige Zeit
        sleep(randint(5, 10))
        # falls der Channel noch nicht entfernt wurde
        # (zum Beispiel durch einen Wechsel des Channels zu einem Ausgang)
        # rufe die Callbackfunktion auf
        if channel in self.events:
            callback(channel)

    def _check_mode(self):
        """
        ueberpruefe, ob schon ein mode gesetzt wurde
        :raises: RuntimeError
        """
        if self.mode is None:
            raise RuntimeError("Please set pin numbering mode using GPIO.setmode(GPIO.BOARD) or GPIO.setmode(GPIO.BCM)")

    def _check_channel_input(self, channel):
        """
        ueberpruefe, ob der channel als input gesetzt wurde
        :raises: RuntimeError
        """
        # da `.get` `None` zurueckgibt wenn der Schluessel `channel` nicht existiert,
        # wird auch bei fehlender Konfiguration der Fehler geworfen
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
        # erstelle und starte einen neuen Thread, damit das Programm nicht pausiert
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
        # erstelle aus der unverstaendlichen Zahl in `edge` einen lesbaren Text
        # und ueberpruefe dabei, ob `edge` einen gueltigen Wert enthaelt
        if edge == GPIO.RISING:
            edge = "rising"
        elif edge == GPIO.FALLING:
            edge = "falling"
        elif edge == GPIO.BOTH:
            edge = "both"
        else:
            raise ValueError("The edge must be set to RISING, FALLING or BOTH")
        print(f"event detect fuer channel {channel} fuer {edge} und bouncetime {bouncetime} ms")
        self.events.append(channel)
        # falls ein callback als Parameter uebergeben wurde, fuege dieses hinzu
        if callback:
            self.add_event_callback(channel, callback)

    def cleanup(self, channel=None):
        """Clean up by resetting all GPIO channels that have been used by this program to INPUT with no
            pullup/pulldown and no event detection
        [channel] - individual channel or list/tuple of channels to clean up.
        Default - clean every channel that has been used. """
        # falls `channel` angegeben wurden, werden nur diese bereinigt,
        # ansonsten wird alles bereinigt
        if channel:
            # ueberpruefe, ob `channel` eine Zahl ist und erstelle eventuell eine Liste nur mit dieser Zahl
            # dies ist wichtig, weil eine For-Schleife nicht ueber eine Zahl,
            # sondern in meinem Fall nur ueber eine Liste, iterieren kann
            if type(channel) == int:
                channel = [channel]
            for c in channel:
                # loesche den channel `c` aus dem dictionary `self.channels`
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
        # mit `bool()` kann aus einer Zahl ohne grossen Aufwand ein bool (Wahrheitswert) erstellt werden
        # dabei werden alle Zahlen zu `True`, nur 0 wird zu `False`
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
        # gib einen zufaelligen Status zurueck
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
        # entferne den channel aus der Liste `self.events`
        self.events.remove(channel)
        print(f"event detect fuer channel {channel} entfernt")

    def setmode(self, mode):
        """
        Set up numbering mode to use for channels.
        BOARD - Use Raspberry Pi board numbers
        BCM   - Use Broadcom GPIO 00..nn numbers
        """
        # ueberpruefe, ob der Modus gueltig ist
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
        # ueberpruefe, ob die Richtung (direction) gueltig ist
        # wenn dies der Fall ist, erstelle aus der Zahl einen lesbaren Text
        if direction == GPIO.OUT:
            direction_text = "OUT"
        elif direction == GPIO.IN:
            direction_text = "IN"
        else:
            raise ValueError("An invalid direction was passed to setup()")
        self.channels[channel] = direction
        print(f"setup channel {channel} auf {direction_text} mit pull_up_down {pull_up_down} und initial {initial}")

    def setwarnings(self, on):
        """Enable or disable warning messages"""
        # diese Funktion macht eigentlich nichts, ist aber wegen der Kombatibilitaet vorhanden
        print(f"setwarnings: {on}")

    def wait_for_edge(self, channel, edge, bouncetime=None, timeout=None):
        """Wait for an edge.  Returns the channel number or None on timeout.
        channel      - either board pin number or BCM number depending on which mode is set.
        edge         - RISING, FALLING or BOTH
        [bouncetime] - time allowed between calls to allow for switchbounce
        [timeout]    - timeout in ms"""
        self._check_mode()
        self._check_channel_input(channel)
        # ueberpruefe, ob `edge` gueltig ist und erstelle eventuell aus der Zahl einen lesbaren Text
        if edge == GPIO.RISING:
            edge = "rising"
        elif edge == GPIO.FALLING:
            edge = "falling"
        elif edge == GPIO.BOTH:
            edge = "both"
        else:
            raise ValueError("The edge must be set to RISING, FALLING or BOTH")
        print(f"wait_for_edge mit channel {channel} edge {edge}, bouncetime {bouncetime} und timeout {timeout}")
        # generiere und warte fuer eine zufaellige Zeit
        # aber maximal fuer den `timeout`
        wartezeit = max(randint(5, 10), timeout / 1000)
        sleep(wartezeit)
