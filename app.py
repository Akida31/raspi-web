"""
    raspi-web

    Kontrolliere Deinen Raspberry Pi ueber das Internet

    :author: Akida31
    :license: MIT
"""

# importiere die passenden Module
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

# importiere GPIO
# wenn GPIO Berechtigungen benoetigt, brich ab
# wenn GPIO nicht verfuegbar ist (weil das Programm nicht auf einem Pi ausgefuehrt wird),
#   nutze FakeGPIO, welches das Programm auf Syntax- und auch manche andere Fehler ueberpruefen kann.
try:
    from RPi import GPIO
except RuntimeError:  # dieser Fehler wird bei fehlenden Berechtigungen geworfen
    print("Keine Berechtigungen RPi.GPIO zu importieren. Starte das Programm mit 'sudo'")
    exit(1)
except ModuleNotFoundError:
    print("Modul RPi.GPIO nicht gefunden. \nNutze eigenes Modul...")
    from fakegpio import GPIO
    # erstelle die GPIO Instanz, danach kann FakeGPIO wie das normale GPIO benutzt werden
    GPIO = GPIO()

# erstelle die App und richte SocketIO ein
app = Flask(__name__)
socketio = SocketIO(app)

# erstelle die Konfiguration
konfiguration = {"modus": None, "pins": {}}
# wenn der Server startet, kann noch kein Benutzer verbunden sein
verbundene_benutzer = 0


def validiere_daten(daten, *argumente):
    """
    validiere die Daten aus der Anfrage des Benutzers.
    Ueberprueft, ob alle Argumente vorhanden sind und auch ein Modus gesetzt wurde
    Wenn nicht, wird ein Fehler ueber *emit* zurueckgegeben
    :param daten: dict - die Eingabe des Benutzers
    :param argumente: list[str] - die zu ueberpruefenden Argumente
    :return: boolean
    """
    # ueberpruefe, ob schon der Modus konfiguriert wurde
    if konfiguration.get("modus") is not None:
        # ueberpruefe fuer jedes Argument, ob dieses in den Daten enthalten ist
        for argument in argumente:
            if argument not in daten:
                # wenn dies nicht der Fall ist, gib einen Fehler an den Benutzer zurueck
                emit("fehler", {"text": f"Fehlendes Argument: '{argument}'"})
                return False
        return True
    else:
        # wenn noch kein Modus gesetzt wurde, wird ebenfalls ein Fehler an den Benutzer gesendet
        emit("fehler", {"text": "Setze zuerst den Modus"})
        return False


def input_callback(pin):
    """
    Benachrichtigt alle verbundenen Benutzer ueber eine Aenderung eines Eingangs
    und aendert die Konfiguration.
    Wird bei einer Aenderung eines Pins durch GPIO aufgerufen
    """
    global konfiguration
    status = GPIO.input(pin)
    socketio.emit("input", {"pin": pin, "status": status})
    konfiguration["pins"][pin]["status"] = status


@app.route("/")
def index():
    """zeige dem Benutzer die HTML-Datei aus dem Ordner `templates` an"""
    return render_template("index.html")


@socketio.on("connect")
def handle_connect():
    """erhoehe die Anzahl der verbundenen Benutzer um 1"""
    global verbundene_benutzer
    verbundene_benutzer += 1


@socketio.on("disconnect")
def handle_disconnect():
    """
    verringere die Anzahl der verbundenen Benutzer um 1,
    ueberpruefe, ob keine Benutzer mehr verbunden ist
        und auch schon Pins konfiguriert wurden
    und bereinige alles falls dies der Fall sein sollte
    """
    global verbundene_benutzer, konfiguration
    verbundene_benutzer -= 1
    if verbundene_benutzer <= 0 and len(konfiguration["pins"]) > 0:
        GPIO.cleanup()
        # erstelle die Konfiguration genauso wie beim Start der Servers
        konfiguration = {"modus": None, "pins": {}}


@socketio.on("get_all")
def handle_get(_daten):
    """gib die gesamte gespeicherte Konfiguration zurueck"""
    emit("get_all", konfiguration)


@socketio.on("getmode")
def handle_getmode(_daten):
    """gib den Modus zurueck"""
    modus = GPIO.getmode()
    emit("getmode", {"modus": modus})


@socketio.on("output")
def handle_output(data):
    """aendere den Ausgang eines Pins"""
    global konfiguration
    if validiere_daten(data, "pin", "status"):
        pin = data["pin"]
        status = data["status"]
        # aendere den Status des Pins, falls dieser als Ausgang konfiguriert wurde
        # und benachrichtige alle Benutzer
        if (pin_konfiguration := konfiguration["pins"].get(pin)) and pin_konfiguration["richtung"] == GPIO.OUT:
            GPIO.output(pin, status)
            pin_konfiguration["status"] = status
            socketio.emit("output", data)
        else:
            emit("fehler", {"text": "Der GPIO Pin wurde nicht als Ausgang gewaehlt"})


@socketio.on("setmode")
def handle_setmode(daten):
    """setze den Modus"""
    global konfiguration
    # ueberpruefe, ob ueberhaupt ein Modus mitgesendet wurde
    if "modus" in daten:
        # ueberpruefe, ob der Modus zulaessig ist und setze ihn eventuell
        if (modus := int(daten["modus"])) in [GPIO.BOARD, GPIO.BCM]:
            GPIO.setmode(modus)
            konfiguration["modus"] = modus
            socketio.emit("setmode", daten)
        else:
            emit("fehler", {"text": "Ungueltiger Modus"})
    else:
        emit("fehler", {"text": "Fehlendes Argument: 'modus'"})


@socketio.on("setup")
def handle_setup(daten):
    """konfiguriere einen Pin"""
    global konfiguration
    if validiere_daten(daten, "pin", "richtung"):
        richtung = daten["richtung"]
        pin = daten["pin"]
        # ueberpruefe, ob die Richtung zulaessig ist
        if richtung not in [GPIO.IN, GPIO.OUT]:
            emit("fehler", {"text": "Ungueltige Richtung"})
            return
        GPIO.setup(pin, richtung)
        # loesche die Callback-Funktion fuer den Pin, wenn er als Eingang konfiguriert wurde,
        # da eine Callback-Funktion nicht zweimal fuer einen Pin hinzugefuegt werden darf
        if pin in konfiguration["pins"] and konfiguration["pins"][pin]["richtung"] == GPIO.IN:
            GPIO.remove_event_detect(pin)
        if richtung == GPIO.IN:
            # setze die Callback-Funktion, sodass die Benutzer benachrichtigt werden,
            # falls sich der Status des Pins aendert
            GPIO.add_event_detect(pin, GPIO.BOTH, callback=input_callback)
        # sende allen Benutzern die Konfiguration des Pins
        status = GPIO.input(pin)
        konfiguration["pins"][pin] = {"richtung": richtung, "status": status}
        socketio.emit("setup", {"pin": pin, "richtung": richtung, "status": status})


if __name__ == "__main__":
    # starte den Server und erlaube auch Verbindungen von anderen Computern
    socketio.run(app, host="0.0.0.0")
    # nach dem Beenden des Servers fuere eine Bereinigung durch
    GPIO.cleanup()
