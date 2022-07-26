// Cloudfront Function that redirects to establish a session
var SESSION_COOKIE_NAME = 'RESUMEID';

function handler(event) {
  var request = event.request;
  var cookies = request.cookies;
  var eventType = event.context.eventType;
  if (eventType == 'viewer-request') {
    if (SESSION_COOKIE_NAME in cookies) return request;
    // Session not set. We must redirect.
    return {
      statusCode: 302,
      statusDescription: "Temporary Redirect. Please set session cookie.",
      headers: {
        location: {
          value: `https://${request.headers.host.value}${request.uri}`,
        },
      },
      cookies: makeCookie(),
    };
  } else if (eventType == 'viewer-response') {
    var response = event.response;
    var sessionCookie = request.cookies[SESSION_COOKIE_NAME];
    response.cookies[SESSION_COOKIE_NAME] = makeCookie(sessionCookie.value);
    return response;
  } else {
    console.log('Unknown event type: ' + eventType);
    return;
  }
}

function makeCookie(value) {
  var o = {};
  o[SESSION_COOKIE_NAME] = {
    value: value || Math.random().toString(36).substring(7),
    attributes: "Expires=" + expiry_date(2 * 60),
  };
  return o;
}

var MINS_TO_MILLIS = 60 * 1000;

function expiry_date(minutes) {
  var expires_at = new Date();
  expires_at.setTime(expires_at.getTime() + minutes * MINS_TO_MILLIS);
  return expires_at.toUTCString();
}

