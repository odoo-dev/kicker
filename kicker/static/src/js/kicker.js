odoo.define('kicker.app', function (require) {
"use strict";

var core = require('web.core');
var time = require('web.time');
var Widget = require('web.Widget');
var local_storage = require('web.local_storage');
var Router = require('demo.router');
var rpc = require('web.rpc');
var _t = core._t;

require('web.dom_ready');

var Dashboard = Widget.extend({
    template: 'Dashboard',
    xmlDependencies: ['/kicker/static/src/xml/kicker_templates.xml'],
    init: function () {
        this.data = {
          // A labels array that can contain any sort of values
          labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
          // Our series array that contains series objects or in this case series data arrays
          series: [
            [5, 2, 4, 2, 0]
          ]
        };
        this.chartOptions = {
            axisX: {
                showGrid: false,
            },
            axisY: {
                showGrid: false,
                showLabel: false,
            },
        };
    },
    start: function () {
        var self = this;
        setTimeout(function() {
            self.name = 'Damien Yvuob';
            self.wins = 36;
            self.losses = 154;
            self.data.series = [[1,0,2,4,6]];
            self.renderElement();
        }, 2000);
    },
    renderElement: function () {
        var result = this._super.apply(this, arguments);
        new Chartist.Line(this.$('.ct-chart')[0], this.data, this.chartOptions);
        return result;
    }    
})

var Profile = Widget.extend({
    template: 'Profile',
    xmlDependencies: ['/kicker/static/src/xml/kicker_templates.xml'],
})

var App = Widget.extend({
  events: {
    'click #burger-toggle, .overlay': '_toggleMenu',
    "swipeLeft .overlay, #sidebar": '_toggleMenu',
    'click a[data-router]': '_onMenuClick',
  },
  pages: {
      dashboard: Dashboard,
      profile: Profile,
  },
  init: function (parent, options) {
      this._super.apply(this, arguments);
      var self = this;
      Router.config({ mode: 'history', root:'/kicker/app'});

      // adding routes
      Router
      .add(/dashboard/, function () {
          self._switchPage('dashboard');
      }).add(/profile/, function () {
          self._switchPage('profile');
      })
      .listen();
  },
  start: function () {
    this.content = new Dashboard(this, {});
    this.content.replace(this.$('.o_kicker_content'));
    Router.check();
    return this._super.apply(this, arguments);
  },

  _toggleMenu: function (ev) {
    // open sidebar
    this.$('#sidebar').toggleClass('active');
    // fade in the overlay
    this.$('.overlay').fadeToggle();
  },
  _closeMenu: function (ev) {
    // open sidebar
    this.$('#sidebar').removeClass('active');
    // fade in the overlay
    this.$('.overlay').fadeOut();
  },
  
  _onMenuClick: function (ev) {
      ev.preventDefault();
      Router.navigate(ev.target.pathname);
      this._closeMenu();
  },
  _switchPage: function (target) {
      var pageConstructor = this.pages[target];
      if (!(this.content instanceof pageConstructor)) {
          this.content = new pageConstructor(this, {});
          this.content.replace(this.$('.o_kicker_main'));
      }
      this._closeMenu();

  },
});

var app = new App();
var el = $('.o_kicker_app');
app.attachTo(el);
});
