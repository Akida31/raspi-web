const socket = io();

const IN = 1;
const OUT = 0;
const BCM = 11;
const BOARD = 10;


socket.on('fehler', function (daten) {
    alert(daten["text"]);
})

socket.on('getmode', function (daten) {
    let modus = daten["modus"];
    if (modus === null) {
        document.getElementById("modus").innerHTML = `<p>Welcher Modus soll genutzt werden?</p>
        <button onclick="wechselModus('${BCM}');">BCM</button>
        <button onclick="wechselModus('${BOARD}');">BOARD</button>`;
    } else {
        socket.emit('get_all', {});
    }
})

socket.on('get_all', function (daten) {
    setzeModus(daten["modus"]);
    console.log("daten", daten);
    let pins = daten['pins'];
    for (let pin in pins) {
        renderPin(pin, pins[pin]['richtung'], pins[pin]['status']);
    }
})

function setzeModus(modus) {
    if (modus == '11') {
        modus = 'BCM';
    } else {
        modus = 'BOARD';
    }
    document.getElementById("modus").innerHTML = `<p>RaspiWeb - Modus: ${modus}</p>`;
    document.getElementById('neuer-pin').style.display = 'flex';
}

socket.on('setmode', function (daten) {
    setzeModus(daten['modus']);
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
    if (document.getElementById(`pin${pin}`) === null) {
        neuerPin(pin);
    }
    let text = `<p>Pin ${pin}</p>`;
    let buttonInClass, buttonOutClass, buttonInDisable, buttonOutDisable = "";
    let statusIcon, andererStatus;
    let statusHtml;
    if (status === 0) {
        statusIcon = '<img src="static/lamp-off.svg" alt="aus" class="status-image"/>';
        andererStatus = 1;
    } else {
        statusIcon = '<img src="static/lamp-on.svg" alt="an" class="status-image"/>';
        andererStatus = 0;
    }
    if (richtung === IN) {
        buttonInClass = "button-disabled";
        buttonInDisable = "disabled";
        statusHtml = `<div class="status-input">${statusIcon}</div>`;
    } else {
        buttonOutClass = "button-disabled";
        buttonOutDisable = "disabled";
        statusHtml = `<div onclick="wechselStatus(${pin}, ${andererStatus})" class="status-button">${statusIcon}</div>`;
    }
    text += `<div class="status"><p>Status:</p>${statusHtml}</div>`;
    text += `<button class="input-button ${buttonInClass}" onclick="wechselRichtung(${pin}, ${IN})" ${buttonInDisable}>
                <img src="static/input.svg" alt=""/> Eingang</button>
            <button class="output-button ${buttonOutClass}" onclick="wechselRichtung(${pin}, ${OUT})" ${buttonOutDisable}>
                <img src="static/output.svg" alt=""/ class="image">Ausgang</button>`
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

function neuerPin(pin) {
    let container = document.getElementById('pins');
    container.innerHTML += `<div id="pin${pin}" class="pin">
            <p>Pin ${pin}</p>
            <button class="input-button" onclick="wechselRichtung(${pin}, ${IN})"><img src="static/input.svg" alt=""/> Eingang</button>
            <button class="output-button" onclick="wechselRichtung(${pin}, ${OUT})"><img src="static/output.svg" alt=""/ class="image">Ausgang</button>
        </div>`;
}


function pinHinzufuegen() {
    let pin = document.getElementById('pin-nummer');
    let nummer = pin.value;
    if (document.getElementById(`pin${nummer}`) !== null) {
        alert("Pin existiert bereits")
    } else {
        neuerPin(nummer);
    }
    pin.value = 1;
}

socket.emit('getmode', {});