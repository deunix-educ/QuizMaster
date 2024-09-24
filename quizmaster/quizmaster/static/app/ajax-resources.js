/**
 * Ajax resources
 *
 * options: xhr_type : '',	//basic, csrftoken, token
 *			username : '',
 *			password : '',
 *			token    : '',
 *			datatype : 'json'
 */

function AjaxModule(options) {

	var defaults = {
			xhr_type: '',	//basic, csrftoken, token
			username: '',
			password: '',
			token : '',
			datatype: 'json',
			host: window.location.protocol + "//" + window.location.host,
	};

	var opt  = $.extend(defaults, options);
	var host = opt.host;
	function _beforeSend(request) {
        switch (opt.xhr_type ) {
	        case "basic":
	        	var f = { beforeSend: function(xhr) {
        				xhr.setRequestHeader("Authorization", "Basic " + btoa(opt.username + ":" + opt.password));
        			}
	        	};
	        	return $.extend(request, f);
	        case "token":
	        	var f = { beforeSend: function(xhr) {
	        			xhr.setRequestHeader("Token", opt.token);
	        		}
	        	};
	        	return $.extend(request, f);
	        case "csrftoken":
	        	var f = { beforeSend: function(xhr) {
	        			xhr.setRequestHeader("X-CSRFToken", opt.token);
	        		}
	        	};
	        	return $.extend(request, f);
	        default:
	            return request;
        }
	}
	function ajaxRequest(uri, method, datas, dtype) {
		var datatype = opt.datatype;
		if ( (typeof dtype!='undefined') && (dtype!='') ) {
			datatype = dtype;
		}
		var data = (typeof datas=='undefined') ? ((datatype=="json") ? {} : "") : datas;
		var request = {
	    	url: host + uri,
	    	type: method,
	    	dataType: datatype,
	    	data:  (method=='POST') || (method=='PUT') ? JSON.stringify(data): data,
	    	contentType: (datatype=="json") ? "application/json; charset=utf-8": "text/plain; charset=utf-8",
	    	cache: false,
	    	error: function(r) {
	            console.log("Ajax error: "+ JSON.stringify(r) );
	        },
	    };
		request = _beforeSend(request);
		return request;
	}
	this.Get 	= function(uri, data, datatype) { return $.ajax(ajaxRequest(uri, 'GET', data, datatype ));  };
	this.Post	= function(uri, data, datatype) { return $.ajax(ajaxRequest(uri, 'POST', data, datatype )); };
	this.Put 	= function(uri, data, datatype) { return $.ajax(ajaxRequest(uri, 'PUT', data, datatype ));   };
	this.Delete = function(uri) 				{ return $.ajax(ajaxRequest(uri, 'DETELE')); }
}
// django csrfmiddlewaretoken
var ajax = new AjaxModule({xhr_type : 'csrftoken', token: csrftoken, });

