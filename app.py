"""
    raspi-web

    Gib dem Benutzer über eine Webseite die Möglichkeit,
    Ein- und Ausgänge auszulesen und zu verändern.

    :author: Akida31
    :license: MIT
"""

# importiere die passenden Module
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

# importiere GPIO
# wenn GPIO Berechtigungen benötigt, brich ab
# wenn GPIO nicht verfügbar ist (weil das Programm nicht auf einem Pi ausgeführt wird)
#   nutze eigenes GPIO-Modul, welches zwar keine Funktionalität darstellt,
#   aber das Programm so auf Syntax- und auch manche andere Fehler überprüft werden kann.
try:
    from RPi import GPIO
except RuntimeError:
    print("Keine Berechtigungen RPi.GPIO zu importieren. Starte das Programm mit 'sudo'")
    exit(1)
except ModuleNotFoundError:
    print("Modul RPi.GPIO nicht gefunden. \nNutze eigenes Modul...")
    from fakegpio import GPIO

    GPIO = GPIO()

# erstelle die App und richte socketio ein
app = Flask(__name__)
socketio = SocketIO(app)

# erstelle die Konfiguration
konfiguration = {"modus": None, "pins": {}}
verbundene_benutzer = 0


def validiere_daten(daten, *argumente):
    """
    validiere die Daten der Anfrage des Benutzers.
    Überprüft, ob alle Argumente vorhanden sind und auch ein Modus gesetzt wurde
    Wenn nicht, wird ein Fehler über *emit* zurückgegeben
    :param daten: dict - die Eingabe des Benutzers
    :param argumente: list[str] - die zu überprüfenden Argumente
    :return: boolean
    """
    if konfiguration["modus"] is not None:
        for argument in argumente:
            if argument not in daten:
                emit("fehler", {"text": f"Fehlendes Argument: '{argument}'"})
                return False
        return True
    else:
        emit("fehler", {"text": "Setze zuerst den Modus"})
        return False


def input_callback(pin):
    global konfiguration
    status = GPIO.input(pin)
    socketio.emit("input", {"pin": pin, "status": status})
    konfiguration["pins"][pin]["status"] = status


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("connect")
def handle_connect():
    global verbundene_benutzer
    verbundene_benutzer += 1


@socketio.on("disconnect")
def handle_disconnect():
    global verbundene_benutzer, konfiguration
    verbundene_benutzer -= 1
    if verbundene_benutzer <= 0 and len(konfiguration["pins"]) > 0:
        GPIO.cleanup()
        konfiguration = {"modus": None, "pins": {}}


@socketio.on("get_all")
def handle_get(_daten):
    emit("get_all", konfiguration)


@socketio.on("getmode")
def handle_getmode(_daten):
    modus = GPIO.getmode()
    emit("getmode", {"modus": modus})


@socketio.on("output")
def handle_output(data):
    global konfiguration
    if validiere_daten(data, "pin", "status"):
        pin = data["pin"]
        status = data["status"]
        if (pin_konfiguration := konfiguration["pins"].get(pin)) and pin_konfiguration["richtung"] == GPIO.OUT:
            GPIO.output(pin, status)
            pin_konfiguration["status"] = status
            socketio.emit("output", data)
        else:
            emit("fehler", {"text": "Der GPIO Pin wurde nicht als Ausgang gewählt"})


@socketio.on("setmode")
def handle_setmode(daten):
    global konfiguration
    if "modus" in daten:
        if (modus := int(daten["modus"])) in [GPIO.BOARD, GPIO.BCM]:
            GPIO.setmode(modus)
            konfiguration["modus"] = modus
            socketio.emit("setmode", daten)
        else:
            emit("fehler", {"text": "Ungültiger Modus"})
    else:
        emit("fehler", {"text": f"Fehlendes Argument: 'modus'"})


@socketio.on("setup")
def handle_setup(daten):
    global konfiguration
    if validiere_daten(daten, "pin", "richtung"):
        richtung = daten["richtung"]
        pin = daten["pin"]
        if richtung not in [GPIO.IN, GPIO.OUT]:
            emit("fehler", {"text": "Ungültige Richtung"})
            return
        GPIO.setup(pin, richtung)
        if pin in konfiguration["pins"] and konfiguration["pins"][pin]["richtung"] == GPIO.IN:
            GPIO.remove_event_detect(pin)
        if richtung == GPIO.IN:
            GPIO.add_event_detect(pin, GPIO.BOTH, callback=input_callback)
        status = GPIO.input(pin)
        konfiguration["pins"][pin] = {"richtung": richtung, "status": status}
        socketio.emit("setup", {"pin": pin, "richtung": richtung, "status": status})


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0")
    GPIO.cleanup()
