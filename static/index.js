// Erstellung einer Verbindung zum Backend
const socket = io();

// Definierung der Konstanten, genauso wie im Backend
// `const` steht fuer Konstanten
// Konstanten werden normalerweise komplett gross geschrieben (upper case)
const IN = 1;
const OUT = 0;
const BCM = 11;
const BOARD = 10;

// fuer das `fehler`-Event wird eine Funktion hinzugefuegt und die Daten des Events uebergeben
socket.on('fehler', function (daten) {
    // zeige dem Benutzer als Nachricht den extrahierten Text
    alert(daten["text"]);
});

socket.on('get_all', function (daten) {
    // zuerst wird der Modus gesetzt
    setzeModus(daten["modus"]);
    let pins = daten['pins'];
    // dieser Syntax ist wie eine For-Schleife in Python
    for (let pin in pins) {
        // nun wird jeder Pin hinzugefuegt
        renderPin(pin, pins[pin]['richtung'], pins[pin]['status']);
    }
});

socket.on('getmode', function (daten) {
    // extrahiere den Modus aus den daten
    // daten ist vom Typ `Object`, das ist aequivalent zu dictionaries in Python
    let modus = daten["modus"];
    // ueberpruefe, ob der Modus schon gesetzt war
    if (modus === null) {
        // erstelle eine Oberflaeche zur Auswahl des Modus
        // dafuer wird der Inhalt des Elementes mit der id `modus` geaendert
        // zur besseren Lesbarkeit werden die Konstanten `BCM` und `BOARD` fuer die Buttons eingesetzt
        document.getElementById("modus").innerHTML = `<p>Welcher Modus soll genutzt werden?</p>
        <button onclick="wechselModus('${BCM}');">BCM</button>
        <button onclick="wechselModus('${BOARD}');">BOARD</button>`;
    } else {
        // Anfrage an der Server für die komplette Konfiguration
        socket.emit('get_all', {});
    }
});

socket.on('input', function (daten) {
    renderPin(daten["pin"], IN, daten["status"]);
});


socket.on('output', function (daten) {
    renderPin(daten["pin"], OUT, daten["status"]);
});

socket.on('setmode', function (daten) {
    // setze den Modus fuer das Frontend
    setzeModus(daten['modus']);
});

socket.on('setup', function (daten) {
    // zeige den Pin, der konfiguriert wurde, an
    renderPin(daten["pin"], daten["richtung"], daten["status"]);
});


function setzeModus(modus) {
    // damit sowohl der String '11' als auch die Zahl 11 als BCM erkannt wird,
    // wird zur ueberpruefung ein == benutzt
    if (modus == '11') {
        modus = 'BCM';
    } else {
        modus = 'BOARD';
    }
    // zeige den Modus an
    document.getElementById("modus").innerHTML = `<p>RaspiWeb - Modus: ${modus}</p>`;
    // mache den Container mit der id `neuer-pin` sichtbar
    document.getElementById('neuer-pin').style.display = 'flex';
}

function wechselRichtung(pin, richtung) {
    socket.emit('setup', {pin: pin, richtung: richtung});
}

function wechselStatus(pin, status) {
    socket.emit('output', {pin: pin, status: status});
}

function wechselModus(modus) {
    // sende an das Backend das `setmode` Event und uebergebe den Modus
    socket.emit('setmode', {modus: modus});
}

function neuerPin(pin) {
    // fuege einen neuen Container fuer den pin zu der Oberflaeche dazu
    // dabei werden Bilder (im svg-Format) zur besseren Gestaltung verwendet
    // der Pin wird aber nur fuer den einen Benutzer hinzugefuegt und erst beim setup,
    // also wechselRichtung im Backend initialisiert
    let container = document.getElementById('pins');
    container.innerHTML += `<div id="pin${pin}" class="pin">
            <p>Pin ${pin}</p>
            <button class="input-button" onclick="wechselRichtung(${pin}, ${IN})"><img src="static/input.svg" alt=""/> Eingang</button>
            <button class="output-button" onclick="wechselRichtung(${pin}, ${OUT})"><img src="static/output.svg" alt=""/ class="image">Ausgang</button>
        </div>`;
}

function pinHinzufuegen() {
    // erstelle eine Variable, die auf das HTML-Element mit der id `pin-nummer` zeigt
    let pin = document.getElementById('pin-nummer');
    // auslesen des Wertes vom Eingabefeld
    let nummer = pin.value;
    // Da fuer jeden Pin eine id `pin` + nummer erstellt wird,
    // wird nun getestet, ob ein Element mit der id schon existiert
    if (document.getElementById(`pin${nummer}`) !== null) {
        alert("Pin existiert bereits")
    } else {
        neuerPin(nummer);
    }
    // Der Wert des Eingabefeldes wird nun zur besseren Bedienung um 1 erhoeht,
    // da haeufig mehrere Pins hintereinander genutzt werden
    pin.value++;
}


function renderPin(pin, richtung, status) {
    // zeige den Pin an
    // dies geschieht sowohl bei der Konfiguration eines neuen Pins
    // als auch bei jeder Aenderung des Pins

    // wenn der Pin noch nicht existiert, erstelle ihn neu
    if (document.getElementById(`pin${pin}`) === null) {
        neuerPin(pin);
    }
    let text = `<p>Pin ${pin}</p>`;
    let buttonInClass, buttonOutClass, buttonInDisable, buttonOutDisable = "";
    let statusIcon, andererStatus;
    let statusHtml;
    // setze ein bestimmtes Icon fuer die Anzeige und merke den anderen Status,
    // um ihn spaeter wechseln zu koennen
    if (status === 0) {
        statusIcon = '<img src="static/lamp-off.svg" alt="aus" class="status-image"/>';
        andererStatus = 1;
    } else {
        statusIcon = '<img src="static/lamp-on.svg" alt="an" class="status-image"/>';
        andererStatus = 0;
    }

    // Erstellung der spezifischen Anzeige fuer Input und Output
    // buttonInClass und buttonOutClass sind fuer das Hinzufuegen des Styles wichtig
    // es wird auch die derzeitige Richtung `disabled`, das heisst unbenutzbar gemacht,
    // damit nicht ausversehen viele Events ueber ein erneutes Setup an den Server gesendet werden
    if (richtung === IN) {
        buttonInClass = "button-disabled";
        buttonInDisable = "disabled";
        statusHtml = `<div class="status-input">${statusIcon}</div>`;
    } else {
        buttonOutClass = "button-disabled";
        buttonOutDisable = "disabled";
        statusHtml = `<div onclick="wechselStatus(${pin}, ${andererStatus})" class="status-button">${statusIcon}</div>`;
    }
    // Erstelle nun das Grundgeruest fuer jeden Pin
    text += `<div class="status"><p>Status:</p>${statusHtml}</div>`;
    text += `<button class="input-button ${buttonInClass}" onclick="wechselRichtung(${pin}, ${IN})" ${buttonInDisable}>
                <img src="static/input.svg" alt=""/> Eingang</button>
            <button class="output-button ${buttonOutClass}" 
                onclick="wechselRichtung(${pin}, ${OUT})" ${buttonOutDisable}>
                <img src="static/output.svg" alt=""/ class="image">Ausgang</button>`;
    // setze den Inhalt des Pins
    // nun ist klar, dass der Pin auch existiert (da er sonst oben erstellt wurde)
    // und somit kann `getElementById` keinen Fehler werfen
    document.getElementById(`pin${pin}`).innerHTML = text;
}

// frage, ob schon ein Modus gesetzt wurde
// uebergebe dabei eine leere Datenmenge, da das Event keine zusaetzlichen Daten benoetigt
socket.emit('getmode', {});