from flask import Flask
from flask_socketio import SocketIO

try:
    import RPi.GPIO as GPIO
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


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    socketio.run(app)
