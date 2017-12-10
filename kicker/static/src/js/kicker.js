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
        this.chartData = {
          // A labels array that can contain any sort of values
          labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
          // Our series array that contains series objects or in this case series data arrays
          series: [
          ]
        };
        this.chartOptions = {
            axisX: {
                showGrid: false,
            },
            axisY: {
                showGrid: true,
                showLabel: true,
                low: 0,
                high: 100,
                ticks: [0, 25, 50, 75, 100],
                type: Chartist.FixedScaleAxis,
            },
        };
    },
    start: function () {
        var self = this;
        return $.when(
            rpc.query({
                route: '/app/dashboard',
            }),
            this._super.apply(this, arguments)
        )
            .then(function(data) {
                console.log(data);
                self.wins = data.wins;
                self.losses = data.losses;
                self.teammates = data.teammates;
                self.nightmares = data.nightmares;
                self.chartData.series = [data.graph];
                self.renderElement();            
            });
    },
    renderElement: function () {
        var result = this._super.apply(this, arguments);
        new Chartist.Line(this.$('.ct-chart')[0], this.chartData, this.chartOptions);
        return result;
    }    
})

var Profile = Widget.extend({
    template: 'Profile',
    xmlDependencies: ['/kicker/static/src/xml/kicker_templates.xml'],
})

var Community = Widget.extend({
    template: 'Community',
    xmlDependencies: ['/kicker/static/src/xml/kicker_templates.xml'],
    start: function () {
        var self = this;
        return $.when(
            rpc.query({
                route: '/app/community',
            }),
            this._super.apply(this, arguments)
        )
            .then(function(data) {
                console.log(data);
                self.usual = data.usual;
                self.rare = data.rare;
                self.renderElement();            
            });
    },
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
      community: Community,
  },
  init: function (parent, options) {
      this._super.apply(this, arguments);
      var self = this;
      Router.config({ mode: 'history'});

      // adding routes
      Router
      .add(/dashboard/, function () {
          self._switchPage('dashboard');
      })
      .add(/profile/, function () {
          self._switchPage('profile');
      })
      .add(/community/, function () {
          self._switchPage('community');
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
