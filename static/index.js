const socket = io();

const IN = 1;
const OUT = 0;
const BCM = 11;
const BOARD = 10;


socket.on('fehler', function (daten) {
    alert(daten["text"]);
})

// TODO multi client connection
socket.on('getmode', function (daten) {
    let modus = daten["modus"];
    if (modus === null) {
        document.getElementById("modus").innerHTML = `<p>Welcher Modus soll genutzt werden?</p>
        <button onclick="wechselModus('${BCM}');">BCM</button>
        <button onclick="wechselModus('${BOARD}');">BOARD</button>`;
    }
    else {
        renderPins();
    }
})

socket.on('setmode', function (daten) {
    let modus;
    if (daten['modus'] === '11') {
        modus = 'BCM';
    }
    else {
        modus = 'BOARD';
    }
    document.getElementById("modus").innerHTML = `Modus: ${modus}`
    renderPins();
})

socket.on('setup', function (daten) {
    renderPin(daten["pin"], daten["richtung"], daten["status"]);
})

socket.on('output', function (daten) {
    renderPin(daten["pin"], OUT, daten["status"]);
})

socket.on('input', function (daten) {
    renderPin(daten["pin"], IN, daten["status"]);
})

function renderPin(pin, richtung, status) {
    let text = `<p>Pin ${pin}</p>`;
    let text2;
    let andereRichtung;
    if (richtung === IN) {
        andereRichtung = OUT;
        text2 = `<p>${status}</p>`;
    }
    else {
        andereRichtung = IN;
        let andererStatus;
        if (status === 0) {
            andererStatus = 1;
        }
        else {
            andererStatus = 0;
        }
        text2 = `<button onclick="wechselStatus(${pin}, ${andererStatus})">${status}</button>`;
    }
    text += `<button onclick="wechselRichtung(${pin}, ${andereRichtung})">${richtung}</button>`;
    text += text2;
    document.getElementById(`pin${pin}`).innerHTML = text;
}

function wechselRichtung(pin, richtung) {
    socket.emit('setup', {pin: pin, richtung: richtung});
}

function wechselStatus(pin, status) {
    socket.emit('output', {pin: pin, status: status});
}

function wechselModus(modus) {
    socket.emit('setmode', {modus: modus});
}

function renderPins() {
    let container = document.getElementById('pins');
    for (let pin=1; pin < 20; pin++) {
        container.innerHTML += `<div id="pin${pin}">
            <p>Pin ${pin}</p>
            <button onclick="wechselRichtung(${pin}, ${IN})">Eingang</button>
            <button onclick="wechselRichtung(${pin}, ${OUT})">Ausgang</button>
        </div>`;
    }
}

socket.emit('getmode', {});