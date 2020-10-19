from flask import Flask, render_template
from flask_socketio import SocketIO, send
import json

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
inputPins = []
connected = 0


def check_json(inp, *args):
    for arg in args:
        if arg not in inp:
            send({'error', f'missing argument: {arg}'})
            return False
    return True


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('setmode')
def handle_setmode(data):
    if check_json(data, "mode"):
        if (mode := int(data["mode"])) in [GPIO.BOARD, GPIO.BCM]:
            GPIO.setmode(mode)


@socketio.on('setup')
def handle_setup(data):
    if check_json(data, "pin", "direction"):
        direction = data["direction"]
        if direction not in [GPIO.IN, GPIO.OUT]:
            send({'error', 'invalid direction'})
        else:
            GPIO.setup(data["pin"], direction)


@socketio.on('output')
def handle_output(data):
    if check_json(data, "pin", "status"):
        GPIO.output(data["pin"], data["status"] != 0)


@socketio.on('read')
def handle_read(json):
    if check_json(json["pin"]):
        send({'success', bool(GPIO.input(pin))})


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
