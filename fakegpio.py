"""
Ein Erseatzmodul für nicht RaspberryPis.
So können Syntax und einfache Programmlogik überprüft werden.
"""


class GPIO:
    # Konstanten sind aus dem normalen Modul übernommen
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
    RPI_REVISION = 0  # TODO
    RPI_INFO = {}  # TODO
    SERIAL = 40
    SPI = 41
    UNKNOWN = - 1
    VERSION = '0.7.0'

    # Methodennamen und Erklärungen sind auch übernommen,
    # nur der Inhalt wurde geändert
    def __init__(self):
        self.mode = None

    def add_event_callback(self):
        """Add a callback for an event already defined using add_event_detect()
        channel      - either board pin number or BCM number depending on which mode is set.
        callback     - a callback function"""
        raise NotImplementedError

    def add_event_detect(self):
        """Enable edge detection events for a particular GPIO channel.
        channel      - either board pin number or BCM number depending on which mode is set.
        edge         - RISING, FALLING or BOTH
        [callback]   - A callback function for the event (optional)
        [bouncetime] - Switch bounce timeout in ms for callback"""
        raise NotImplementedError

    def cleanup(self):
        """Clean up by resetting all GPIO channels that have been used by this program to INPUT with no
            pullup/pulldown and no event detection
        [channel] - individual channel or list/tuple of channels to clean up.
        Default - clean every channel that has been used. """
        raise NotImplementedError

    def event_detect(self):
        """Returns True if an edge has occurred on a given GPIO.
        You need to enable edge detection using add_event_detect() first.
        channel - either board pin number or BCM number depending on which mode is set."""
        raise NotImplementedError

    def getmode(self):
        """Get numbering mode used for channel numbers.
        Returns BOARD, BCM or None"""
        raise NotImplementedError

    def gpio_function(self):
        """Return the current GPIO function (IN, OUT, PWM, SERIAL, I2C, SPI)
        channel - either board pin number or BCM number depending on which mode is set."""
        raise NotImplementedError

    def input(self):
        """Input from a GPIO channel.  Returns HIGH=1=True or LOW=0=False
        channel - either board pin number or BCM number depending on which mode is set."""
        raise NotImplementedError

    def output(self):
        """Output to a GPIO channel or list of channels
        channel - either board pin number or BCM number depending on which mode is set.
        value   - 0/1 or False/True or LOW/HIGH"""
        raise NotImplementedError

    def remove_event_detect(self):
        """Remove edge detection for a particular GPIO channel
        channel - either board pin number or BCM number depending on which mode is set."""
        raise NotImplementedError

    def setmode(self):
        """
        Set up numbering mode to use for channels.
        BOARD - Use Raspberry Pi board numbers
        BCM   - Use Broadcom GPIO 00..nn numbers
        """
        raise NotImplementedError

    def setup(self):
        """Set up a GPIO channel or list of channels with a direction and (optional) pull/up down control
        channel        - either board pin number or BCM number depending on which mode is set.
        direction      - IN or OUT
        [pull_up_down] - PUD_OFF (default), PUD_UP or PUD_DOWN
        [initial]      - Initial value for an output channel"""
        raise NotImplementedError

    def setwarnings(self):
        """Enable or disable warning messages"""
        raise NotImplementedError

    def wait_for_edge(self):
        """Wait for an edge.  Returns the channel number or None on timeout.
        channel      - either board pin number or BCM number depending on which mode is set.
        edge         - RISING, FALLING or BOTH
        [bouncetime] - time allowed between calls to allow for switchbounce
        [timeout]    - timeout in ms"""
        raise NotImplementedError
