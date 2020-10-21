from flask import Flask, render_template
from flask_socketio import SocketIO, emit

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
            emit('fehler', {'text': f'Fehlendes Argumend: {arg}'})
            return False
    return True


def check_input(inp, *args):
    print(config)
    print(inp)
    if config["mode"]:
        return check_json(inp, *args)
    else:
        emit('fehler', {'text': 'Setze zuerst den Modus'})
        return False


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
        else:
            emit('fehler', {'text': 'Ungültiger modus'})


@socketio.on('getmode')
def handle_getmode(_data):
    mode = GPIO.getmode()
    emit('getmode', {"mode": mode})


@socketio.on('setup')
def handle_setup(data):
    global config
    if check_input(data, "pin", "direction"):
        direction = data["direction"]
        pin = data["pin"]
        if direction not in [GPIO.IN, GPIO.OUT]:
            emit('fehler', {'text': 'Ungültige Richtung'})
            return
        GPIO.setup(pin, direction)
        if pin in config['pins'] and config['pins'][pin]['direction'] == GPIO.IN:
            GPIO.remove_event_detect(pin)
        if direction == GPIO.IN:
            GPIO.add_event_detect(pin, GPIO.BOTH, callback=handle_input)
            print("added callback for", pin)
        status = GPIO.input(pin)
        config['pins'][pin] = {'direction': direction, 'status': status}
        socketio.emit('setup', {'pin': pin, 'direction': direction, 'status': status})


@socketio.on('output')
def handle_output(data):
    global config
    if check_input(data, "pin", "status"):
        pin = data["pin"]
        status = data["status"]
        if (pin_config := config['pins'].get(pin)) and pin_config['direction'] == GPIO.OUT:
            GPIO.output(pin, status)
            pin_config['status'] = status
            print(f"output, {data}")
            socketio.emit('output', data)
        else:
            emit('fehler', {'text': 'Der GPIO Pin wurde nicht als Ausgang gewählt'})


def handle_input(pin):
    global config
    status = GPIO.input(pin)
    print(f"input on pin {pin} with status {status}")
    socketio.emit('input', {'pin': pin, 'status': status})
    config["pins"][pin]['status'] = status


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
    if connected <= 0 and len(config["pins"]) > 0:
        GPIO.cleanup()


if __name__ == '__main__':
    import logging

    logging.getLogger('werkzeug').disabled = True
    socketio.run(app, host='0.0.0.0', )
