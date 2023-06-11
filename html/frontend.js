let pc;
let signalingSocket

async function startStreaming() {
    pc = new RTCPeerConnection();

    // Create an audio track
    const audioTrack = pc.addTransceiver("audio").receiver.track;
    const audioPlayer = document.getElementById("audioPlayer");
    audioPlayer.srcObject = new MediaStream([audioTrack]);

    // Connect to the signaling server
    const signalingUrl = "wss://"+location.host+":5984/ws";
    signalingSocket = new WebSocket(signalingUrl);

    console.log( "signalingUrl: " + signalingUrl )

    signalingSocket.onopen = async () => {
        // Send an offer to the server
        console.log( "Sending 'offer'" )
        signalingSocket.send("offer");
    };

    signalingSocket.onmessage = async (event) => {
        const message = JSON.parse(event.data);
        console.log( 'Got message' )
        if (message.type === "answer") {
            console.log( 'Got answer' )
            // Set the remote description
            await pc.setRemoteDescription(new RTCSessionDescription(message));
        }
    };

    pc.addEventListener('track', function(evt) {
        if (evt.track.kind == 'video')
            document.getElementById('video').srcObject = evt.streams[0];
        else
            document.getElementById('audioPlayer').srcObject = evt.streams[0];
    });

    // Listen for ICE candidates and send them to the server
    pc.onicecandidate = (event) => {
        console.log( "Got ICE candidate, sending shit to backend" )
        if (event.candidate) {
            signalingSocket.send(JSON.stringify({
                type: "candidate",
                candidate: event.candidate.toJSON()
            }));
        }
    };

    // Create an offer and set it as the local description
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);
    signalingSocket.send(JSON.stringify(pc.localDescription));
}

function stopStreaming() {
    pc.close();
}

function increaseFrequency() {
    signalingSocket.send(
        JSON.stringify({
            "cmd": "increaseFrequency",
            "amountHz": 100
        })
    );
}

function decreaseFrequency() {
    signalingSocket.send(
        JSON.stringify({
            "cmd": "increaseFrequency",
            "amountHz": -100
        })
    );
}

window.addEventListener("unload", () => {
    if (pc) {
        pc.close();
    }
});
