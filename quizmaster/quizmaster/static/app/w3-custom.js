// custom.js

let alertDelay = 3000;
window.setTimeout(function() {$('div.alert').fadeTo(500, 0).slideUp(500, function(){ $(this).remove(); });}, alertDelay);


w3_alert = function(message, bgc, timeout, classname) {
    var bg = (typeof bgc === 'undefined') ?  'w3-blue': bgc;
    var cls = (typeof classname === 'undefined') ?  '': classname;
    var html = '<div class="p-1 alert '+ bg +' '+ cls +' " style="min-width:300px;">' +
				'<span onclick="this.parentElement.style.display=\'none\'" class="w3-button w3-right">&times;</span><h5>'+message+'</h5>' +
               '</div>'
    $('#flash-message-placeholder').append(html);

    if (timeout < 0) timeout = 3600*1000;
    if (timeout == 0) timeout = 1000;

    window.setTimeout(function() {
        $('div.alert').fadeTo(500, 0).slideUp(500, function() {
        	$(this).remove();
        });
    }, timeout);
};



function blink(id, time, interval, callback) {
    var timer=window.setInterval(function(){id.css("opacity", "0.0");
    window.setTimeout(function(){id.css("opacity", "1");}, 100);}, interval);
    window.setTimeout(function(){clearInterval(timer); id.text('');}, time);
}

function clean_uri() { var uri = window.location.protocol + "//" + window.location.host + window.location.pathname;window.history.replaceState({}, document.title, uri);}
function showConfirm(msgConfirm){ if (confirm(msgConfirm)==true) return true; return false; }

toJsonWebsocketMessage = function(type, payload) {
	var msg = (typeof payload == 'undefined') ? {} : payload;
	//console.log(type);console.log(msg);
	return JSON.stringify( {'type': type, 'text': msg} );
};


toMqttMessage = function(type, topic, payload) {
    var msg = (typeof payload == 'undefined') ? {} : payload;
    return toJsonWebsocketMessage(type, {topic: topic, payload: msg});
};

// some useful functions
function toFloat(value, n) {
    try {
        value.replace(',', '.');
    } catch(e){}
    return parseFloat(value).toFixed(n);
}

function toDecimal(value, n) {
	return parseInt(value).toFixed(n);
}

intToFloat = toDecimal;

function b64_to_utf8( str ) {
	return decodeURIComponent(escape(window.atob( str )));
}

function utf8_to_b64(str) {
  return window.btoa(unescape(encodeURIComponent(str)));
}


function bytes_to_b64( buffer ) {
    var binary = '';
    var bytes = new Uint8Array( buffer );
    var len = bytes.byteLength;
    for (var i = 0; i < len; i++) {
        binary += String.fromCharCode( bytes[ i ] );
    }
    return window.btoa( binary );
}

var dateOptions = {hourCycle:"h24",year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",second:"2-digit",};

function locale_date(unixtimestamp) {
	var date = new Date(parseInt(unixtimestamp));
	var dateString =
	date.getFullYear() + "/" +
	("0" +(date.getMonth()+1)).slice(-2)+ "/" +
	("0" + date.getDate()).slice(-2) + " " +
	("0" + date.getHours()).slice(-2) + ":" +
	("0" + date.getMinutes()).slice(-2) + ":" +
	("0" + date.getSeconds()).slice(-2);
	return dateString;
}
dateToString = locale_date;

function to_locale_time(unixtimestamp, loc) {
    var date = new Date(parseInt(unixtimestamp));
    return date.toLocaleTimeString();
}

function to_localeDate(unixtimestamp, loc) {
    var locale = (typeof loc === 'undefined') ?  'fr-FR': loc;
    var date = new Date(parseInt(unixtimestamp));
    return date.toLocaleDateString(locale, dateOptions);
}

function to_localeDateMillisecond(unixtimestamp, loc) {
    var locale = (typeof loc === 'undefined') ?  'fr-FR': loc;
    var date = new Date(1000*parseInt(unixtimestamp));
    return date.toLocaleDateString(locale, dateOptions);
}


function getUrlParameter(sParam) {
    var sPageURL = window.location.search.substring(1),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;
    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');
        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : decodeURIComponent(sParameterName[1]);
        }
    }
}

function strReplace(str, c){
    try {
        return str.replace(/\s+g/, c);
    } catch(e) {}
    return str;

}
function rtrim(str, c){
    try {
        return str.replace(/\s+$/, c);
    } catch(e) {}
    return str;
}

function ltrim(str, c){
    try {
        return str.replace(/^\s+/, c);
    } catch(e) {}
    return str;

}

function lztrim(str, c){
    try {
        return str.replace(/^0+/, c);
    } catch(e) {}
    return str;
}

function lastString(str, c){
    var n = str.split(c);
    return n[n.length - 1];
}

function checked_array(name) {
    var a = [];
    $.each($("input[name="+ name +"]:checked"), function() { a.push(this.value); });
    return a;
}

function imagePreview(id) {
	$('.imagepreview').attr('src', id.attr('src'));
	$('#imagemodal').css("display", "block");
}

function unloadAllJS() {
    var jsArray = new Array();
    jsArray = document.getElementsByTagName('script');
    for (i = 0; i < jsArray.length; i++){
        if (jsArray[i].id){
          unloadJS(jsArray[i].id)
        }else{
          jsArray[i].parentNode.removeChild(jsArray[i]);
        }
    }
}

function toggleTextColor(id, from, to) { id.removeClass('w3-text-'+from).addClass('w3-text-'+ to);}
function toggleBgColor(id, from, to)   { id.removeClass('w3-'+from).addClass('w3-'+ to);}

function buttonEnable(id)   { id.prop('disabled', false);}
function buttonDisable(id)  { id.prop('disabled', true);}
function checkBox(id)       { id.prop('checked', true);}
function uncheckBox(id)     { id.prop('checked', false);}
function radioOn(id)        { id.prop('checked', true);}
function radioOff(id)       { id.prop('disabled', false);}

function switchOn(id)       { checkBox(id); id.data('btn', '1');}
function switchOff(id)      { uncheckBox(id); id.data('btn', '0');}
function buttonSetOn(id)    { id.data('btn', '1'); }
function buttonSetOff(id)   { id.data('btn', '0'); }
function buttonIsOn(id)     { return id.data('btn')=='1'; }
function buttonIsOff(id)    { return id.data('btn')=='0'; }
function buttonOn(id, msg)  { buttonSetOn(id);id.html(msg); toggleBgColor(id, 'blue', 'orange');}
function buttonOff(id, msg) { buttonSetOff(id);id.html(msg); toggleBgColor(id, 'orange', 'blue');}
function w3Hide(id)         { id.removeClass('w3-show').addClass('w3-hide'); }
function w3Show(id)         { id.removeClass('w3-hide').addClass('w3-show'); }

function open_tab(evt, tab, tabname, link) {
    var i, x, tablinks;
    x = document.getElementsByClassName("tabx");
    for (i = 0; i < x.length; i++) {x[i].style.display = "none";}
    tablinks = document.getElementsByClassName(link);
    for (i = 0; i < x.length; i++) { tablinks[i].className = tablinks[i0 ].className.replace(" w3-dark-grey", "");  }
    document.getElementById(tab).style.display = "block";
    evt.currentTarget.className += " w3-dark-grey";

    if (tab == tabname) { ws_pub(tab); }
}


//