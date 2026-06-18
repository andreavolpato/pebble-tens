// Phone-side entry point. Clay renders the config page (src/pkjs/config.js)
// and sends the chosen settings to the watch via AppMessage. The number
// inputs arrive as strings, so coerce them to ints before they're sent.
var Clay = require('pebble-clay');
var clayConfig = require('./config');
var clay = new Clay(clayConfig, null, { autoHandleEvents: false });

var NUMERIC_KEYS = ['BIRTH_YEAR', 'BIRTH_MONTH', 'BIRTH_DAY', 'LIFE_SPAN_YEARS'];

Pebble.addEventListener('showConfiguration', function (e) {
  Pebble.openURL(clay.generateUrl());
});

Pebble.addEventListener('webviewclosed', function (e) {
  if (!e || !e.response) {
    return;
  }
  var dict = clay.getSettings(e.response);

  // Coerce numeric inputs (Clay yields them as strings).
  NUMERIC_KEYS.forEach(function (key) {
    var mk = 'MESSAGE_KEY_' + key;
    if (dict[mk] !== undefined) {
      dict[mk] = parseInt(dict[mk], 10) || 0;
    }
  });

  Pebble.sendAppMessage(
    dict,
    function () {
      console.log('Tens settings sent');
    },
    function (err) {
      console.log('Tens settings failed: ' + JSON.stringify(err));
    }
  );
});
