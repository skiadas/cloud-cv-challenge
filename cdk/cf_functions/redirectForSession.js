// Cloudfront Function that redirects to establish a session
var SESSION_COOKIE_NAME = 'RESUMEID';

function handler(event) {
  var request = event.request;
  var cookies = request.cookies;
  if (SESSION_COOKIE_NAME in cookies) return request;
  // Session not set. We must redirect.
  return {
    statusCode: 302,
    statusDescription: "Temporary Redirect. Please set session cookie.",
    headers: {
      location: {
        value: `https://${request.headers.host.value}${request.uri}`
      }
    },
    cookies: makeCookie()
  }
}

function makeCookie() {
  var o = {};
  o[SESSION_COOKIE_NAME] = {
    value: Math.random().toString(36).substring(7),
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

