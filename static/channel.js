document.addEventListener('DOMContentLoaded', () => {
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
    function sendMessage() {
        let timestamp = new Date().toLocaleTimeString();
        let msg = document.getElementById("comment").value;
        socket.emit('send message', msg, timestamp);
        document.getElementById("comment").value = '';
    }
    socket.on('connect', () => {
        socket.emit('joined');
        document.querySelector('#newChannel').addEventListener('click', () => {
            localStorage.removeItem('last_channel');
        });

        document.querySelector('#leave').addEventListener('click', () => {
            socket.emit('left');
            localStorage.removeItem('last_channel');
            window.location.replace('/');
        });

        document.querySelector('#logout').addEventListener('click', () => {
            localStorage.removeItem('last_channel');
        });

        document.querySelector('#comment').addEventListener("keydown", event => {
            if (event.key == "Enter") {
                sendMessage();
            }
        });

        document.querySelector('#send-button').addEventListener("click", sendMessage);
    });

    socket.on('status', data => {
        let row = `<${data.msg}>`;
        document.querySelector('#chat').value += row + '\n';
        localStorage.setItem('last_channel', data.channel);
    });

    socket.on('announce message', data => {
        let row = `<${data.timestamp}> - [${data.user}]: ${data.msg}`;
        document.querySelector('#chat').value += row + '\n';
    });
});
