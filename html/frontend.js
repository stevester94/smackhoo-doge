let pc;
let signalingSocket;

function negotiate() {
    return pc.createOffer().then(function(offer) {
        return pc.setLocalDescription(offer);
    }).then(function() {
        // wait for ICE gathering to complete
        return new Promise(function(resolve) {
            if (pc.iceGatheringState === 'complete') {
                resolve();
            } else {
                function checkState() {
                    if (pc.iceGatheringState === 'complete') {
                        pc.removeEventListener('icegatheringstatechange', checkState);
                        resolve();
                    }
                }
                pc.addEventListener('icegatheringstatechange', checkState);
            }
        });
    }).then(function() {
        signalingSocket.send(JSON.stringify(pc.localDescription));
    }).catch(function(e) {
        alert(e);
    });
}


async function startStreaming() {
    var config = {
        sdpSemantics: 'unified-plan',
        iceServers: [{urls: ['stun:stun.l.google.com:19302']}]
    };
    pc = new RTCPeerConnection(config);

    // Create an audio track
    const audioTrack = pc.addTransceiver("audio").receiver.track;
    const audioPlayer = document.getElementById("audioPlayer");
    audioPlayer.srcObject = new MediaStream([audioTrack]);

    // Connect to the signaling server
    const signalingUrl = "wss://"+location.host+"/ws";
    signalingSocket = new WebSocket(signalingUrl);

    console.log( "signalingUrl: " + signalingUrl )

    signalingSocket.onopen = async () => {
        negotiate();
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
