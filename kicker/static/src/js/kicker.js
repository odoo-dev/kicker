odoo.define('kicker.app', function (require) {
"use strict";

var core = require('web.core');
var time = require('web.time');
var Widget = require('web.Widget');
var local_storage = require('web.local_storage');
var rpc = require('web.rpc');
var _t = core._t;

require('web.dom_ready');
var App = Widget.extend({
  events: {
    'click #burger-toggle, .overlay': '_toggleMenu',
  },

  _toggleMenu: function (ev) {
    // open sidebar
    this.$('#sidebar').toggleClass('active');
    // fade in the overlay
    this.$('.overlay').fadeToggle();
    this.$('a[aria-expanded=true]').attr('aria-expanded', 'false');
  },
});

var app = new App();
var el = $('.o_kicker_app');
app.attachTo(el);
});
