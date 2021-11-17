// Adding the format attr to strings
String.prototype.format = function () {
    var i = 0, args = arguments;
    return this.replace(/{}/g, function () {
      return typeof args[i] != 'undefined' ? args[i++] : '';
    });
  };

// Websocket messages
let chatSocket = ''
try {
    const roomName = JSON.parse(document.getElementById('room-name').textContent);

    var loc = window.location;
    var wsStart = 'ws://';
    if (loc.protocol == 'https:') {
        wsStart = 'wss://'
    }

    chatSocket = new WebSocket(
        wsStart
        + window.location.host
        + '/ws/webchat/'
        + roomName
        + '/'
    );

    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);

        if (data.type == 'stream_result'){
            let result = data.message

            // Clean empty_results
            empty_results = document.querySelectorAll('.empty_results')
            empty_results.forEach(element => {
                element.remove()
            });

            // Get the current count of the children of stream_results
            let stream_results = document.getElementById('stream_results');

            let count = stream_results.childElementCount + 1;

            let html = `<tr>
                <th scope="row">{}</th>
                <td>{}</td>
                <td>{}</td>
                <td>{}</td>
                <td>{}</td>
                <td>{}</td>
                <td>{}</td>
            </tr>`.format(count, result.key, result.layout, result.type, result.title, result.subtitle, result.url,)

            stream_results.innerHTML += html;
        }
    };

    chatSocket.onclose = function(e) {
        console.error('UI Bad Response');
        location.reload()
    };
} catch (error) {
    
}