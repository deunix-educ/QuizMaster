// Common
function tsNow() {
    return Math.floor(new Date().getTime()/1000);
}

function publish(topic, payload) {
    try {
        mqttc.publishMessage(topic, payload);
    } catch(e) {
        //console.log(e);
    }
}

// origine/dev/uuid/ts/evt
function topicToJson(topics) {
    var topic = topics.split('/');
    return {dev: topic[1], mode: topic[1], uuid: topic[2], ts: topic[3], evt: topic[4] };
}

function onDisconnectionCb(response) {
    $('i.ws-status').removeClass('w3-text-green').addClass('w3-text-red');
}

function onConnectionCb()            {
    $('i.ws-status').removeClass('w3-text-red').addClass('w3-text-green');
}

function server_alive(p)  {
   p.alive ?
    $('i.alive-status').removeClass('w3-text-red').addClass('w3-text-green'):
    $('i.alive-status').removeClass('w3-text-green').addClass('w3-text-red');
}


let countDown = function(target, timeout) {
    console.log(target);
    target.html(timeout);
    const ts = new Date().getTime() + (timeout*1000);
    let timer = setInterval(function() {
        var count = Math.round( (ts - new Date().getTime()) / 1000);
        count < 0 ? clearInterval(timer): target.html(count);
    }, 500);
};

