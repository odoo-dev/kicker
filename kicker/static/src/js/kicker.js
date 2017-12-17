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
    init: function (parents, options) {
        this._super.apply(this, arguments);
        this.unsaved_changes = false;
        this.user = undefined;
    },
    start: function() {
        var self = this;
        return rpc.query({
            route: '/kicker/user'
        })
        .then(function (user_data) {
            self.user = user_data;
            self.renderElement();
        });
    },
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
                self.usual = data.usual;
                self.rare = data.rare;
                self.renderElement();            
            });
    },
})

var CommunityProfile = Widget.extend({
    template: 'Profile',
    xmlDependencies: ['/kicker/static/src/xml/kicker_templates.xml'],
    init: function (parents, options) {
        this._super.apply(this, arguments);
        this.user_id = options.user_id;
        this.user = undefined;
    },
    willStart: function() {
        var self = this;
        return rpc.query({
            route: '/kicker/user/' + this.user_id
        })
        .then(function (user_data) {
            self.user = user_data;
        });
    },
})

var App = Widget.extend({
  xmlDependencies: ['/kicker/static/src/xml/kicker_templates.xml'],
  events: {
    'click #burger-toggle, .overlay': '_toggleMenu',
    "swipeleft .overlay, #sidebar, #top-header": function (ev) {this._toggleMenu(ev, 'close');},
    'swiperight #top-header, .o_kicker_main':  function (ev) {this._toggleMenu(ev, 'open');},
    'click a[data-router]': '_onMenuClick',
  },
  pages: {
      dashboard: Dashboard,
      profile: Profile,
      community: Community,
      communityProfile: CommunityProfile,
  },
  init: function (parent, options) {
      this._super.apply(this, arguments);
      var self = this;
      Router.config({ mode: 'history'});

      // adding routes (most specific to less specific)
      Router
      .add(/dashboard/, function () {
          self._switchPage('dashboard');
      })
      .add(/profile/, function () {
          self._switchPage('profile');
      })
      .add(/community\/user\/(.*)/, function (user_id) {
          self._switchPage('communityProfile', {user_id: user_id});
      })
      .add(/community/, function () {
          self._switchPage('community');
      })
      .add(function () {
          self._switchPage('dashboard');
      })
      .listen();
  },
  willStart: function () {
    Router.check();
    return this._super.apply(this, arguments);
  },

  _toggleMenu: function (ev, force) {
    if (force === 'open') {
        this.$('#sidebar').addClass('active');
        this.$('.overlay').fadeIn();

    } else if (force === 'close') {
        this.$('#sidebar').removeClass('active');
        this.$('.overlay').fadeOut();

    } else {
        this.$('#sidebar').toggleClass('active');
        this.$('.overlay').fadeToggle();
    }
  },  
  _onMenuClick: function (ev) {
      ev.preventDefault();
      var link = $(ev.target).closest('a');
      if (link.length > 0) {
          var path = link[0].pathname;
          Router.navigate(path);
      }
      this._toggleMenu({}, 'close');
  },
  _switchPage: function (target, options) {
      var pageConstructor = this.pages[target];
      if (!(this.content instanceof pageConstructor)) {
          this.content = new pageConstructor(this, options);
          this.content.replace(this.$('.o_kicker_main'));
      }
      this._toggleMenu({}, 'close');

  },
});

var app = new App();
var el = $('.o_kicker_app');
app.attachTo(el);
});
