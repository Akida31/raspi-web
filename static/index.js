const socket = io();

const IN = 1;
const OUT = 0;
const BCM = 11;
const BOARD = 10;


socket.on('fehler', function (data) {
    console.log(data);
    alert(data);
})

socket.on('getmode', function (data) {
    let mode = data["mode"];
    if (mode === null) {
        document.getElementById("modus").innerHTML = `<p>Welcher Modus soll genutzt werden?</p>
        <button onclick="wechselModus('${BCM}');">BCM</button>
        <button onclick="wechselModus('${BOARD}');">BOARD</button>`;
    }
    else {
        renderPins();
    }
})

socket.on('setmode', function (data) {
    let modus;
    if (data['mode'] === '11') {
        modus = 'BCM';
    }
    else {
        modus = 'BOARD';
    }
    document.getElementById("modus").innerHTML = `Modus: ${modus}`
    renderPins();
})

socket.on('setup', function (data) {
    renderPin(data["pin"], data["direction"], data["status"]);
})

socket.on('output', function (data) {
    renderPin(data["pin"], OUT, data["status"]);
})

socket.on('input', function (data) {
    console.log("input", data);
    renderPin(data["pin"], IN, data["status"]);
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
    socket.emit('setup', {pin: pin, direction: richtung});
}

function wechselStatus(pin, status) {
    socket.emit('output', {pin: pin, status: status});
}

function wechselModus(modus) {
    socket.emit('setmode', {mode: modus});
}

function renderPins() {
    let container = document.getElementById('pins');
    for (let pin=1; pin < 20; pin++) {
        container.innerHTML += `<div id="pin${pin}">
            <p>Pin ${pin}</p>
            <button onclick="wechselRichtung(${pin}, ${IN})">input</button>
            <button onclick="wechselRichtung(${pin}, ${OUT})">output</button>
        </div>`;
    }
}

socket.emit('getmode', {});