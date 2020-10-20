from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit

try:
    from RPi import GPIO
except RuntimeError:
    print("Keine Berechtigungen RPi.GPIO zu importieren. Starte das Programm mit 'sudo'")
    exit(1)
except ModuleNotFoundError:
    print("Modul RPi.GPIO nicht gefunden. \nNutze eigenes Modul...")
    from fakegpio import GPIO

    GPIO = GPIO()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
config = {'mode': None, 'pins': {}}
connected = 0


def check_json(inp, *args):
    for arg in args:
        if arg not in inp:
            send({'error', f'missing argument: {arg}'}, json=True)
            return False
    return True


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('setmode')
def handle_setmode(data):
    global config
    if check_json(data, "mode"):
        if (mode := int(data["mode"])) in [GPIO.BOARD, GPIO.BCM]:
            GPIO.setmode(mode)
            config['mode'] = mode
            socketio.emit('setmode', data)


@socketio.on('setup')
def handle_setup(data):
    global config
    if check_json(data, "pin", "direction"):
        direction = data["direction"]
        pin = data["pin"]
        if direction not in [GPIO.IN, GPIO.OUT]:
            send({'error', 'invalid direction'}, json=True)
        else:
            GPIO.setup(pin, direction)
            config['pins'][pin] = {'direction': direction, 'status': GPIO.LOW}
            socketio.emit('setup', data)
        if direction == GPIO.IN:
            GPIO.add_event_detect(pin, GPIO.RISING, callback=handle_rising)
            GPIO.add_event_detect(pin, GPIO.FALLING, callback=handle_falling)


@socketio.on('output')
def handle_output(data):
    global config
    if check_json(data, "pin", "status"):
        pin = data["pin"]
        status = data["status"] != GPIO.LOW
        if (pin_config := config['pins'].get(pin)) and pin_config['direction'] == GPIO.OUT:
            GPIO.output(pin, status)
            pin_config['status'] = status
            socketio.emit('output', data)
        else:
            send({'error': 'The GPIO channel has not been set up as an OUTPUT'}, json=True)


def handle_input(pin, status):
    global config
    socketio.emit('input', {'pin': pin, 'status': 0})
    config["pins"][pin]['status'] = status


def handle_rising(pin):
    handle_input(pin, 1)


def handle_falling(pin):
    handle_input(pin, 0)


@socketio.on('get_all')
def handle_get():
    emit('get_all', config)


@socketio.on('connect')
def handle_connect():
    global connected
    connected += 1


@socketio.on('disconnect')
def handle_disconnect():
    global connected
    connected -= 1
    if connected <= 0:
        GPIO.cleanup()


if __name__ == '__main__':
    socketio.run(app)
