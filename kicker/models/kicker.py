
import logging
from operator import attrgetter
import uuid

import odoo
from odoo import api, fields, models, SUPERUSER_ID
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)


class Kicker(models.Model):

    _name = 'kicker.kicker'
    _descrption = 'Kicker'
    _order = 'nickname'
    _rec_name = 'nickname'

    def _default_token(self):
        return str(uuid.uuid4())

    nickname = fields.Char('Nickname', required=True, help="Nickname of the kicker. Used in the ping.")
    location = fields.Char('Location')
    token = fields.Char('Token', required=True, default=_default_token)
    ping_ids = fields.One2many("kicker.ping", "kicker_id", "Pings")
    is_available = fields.Boolean('Is Available', compute='_compute_is_available')
    last_status_change = fields.Datetime("Available since", _compute='_compute_last_status_change')

    @api.depends('ping_ids.available')
    def _compute_is_available(self):
        for kicker in self:
            if kicker.ping_ids:
                kicker.is_available = kicker.ping_ids[0].available
            else:
                kicker.is_available = False

    @api.depends('ping_ids.available')
    def _compute_last_status_change(self):
        for kicker in self:
            last_ping_change = self.env['kicker.ping'].search([('kicker_id', '=', kicker.id), ('available', '!=', kicker.is_available)])
            kicker.last_status_change = last_ping_change.create_date


class Ping(models.Model):

    _name = 'kicker.ping'
    _description = 'Kicker Ping'
    _order = 'create_date DESC'

    kicker_id = fields.Many2one('kicker.kicker', string="Kicker")
    kicker_token = fields.Char('Kicker Token')
    create_date = fields.Datetime('Create date', default=fields.Datetime.now)
    available = fields.Boolean('Is free')
    ip_address = fields.Char("IP address of the ping")

    @api.model
    def ping(self, kicker_token, available, ip_address=False):
        kicker = self.env['kicker.kicker'].search([('token', '=', kicker_token)])
        if not kicker:
            _logger.warning("Unknow kicker has ping, but we don't know who ...")
            return False

        ping = self.create({
            'kicker_id': kicker.id,
            'kicker_token': kicker_token,
            'available': available,
            'ip_address': ip_address,
        })

        self.env['bus.bus'].sendone((self._cr.dbname, 'kicker.ping', kicker.id), {
            'kicker_name': kicker.nickname,
            'create_date': ping.create_date,
            'available': ping.available,
        })
        return True


class KickerTeam(models.Model):
    _name = 'kicker.team'
    _description = 'Kicker Team'

    player_ids = fields.Many2many('res.partner', string='Players')


class KickerTeamScore(models.Model):
    _name = 'kicker.team.score'
    _description = 'Kicker Team Score'

    team_id = fields.Many2one('kicker.team', 'Playing Team')
    game_id = fields.Many2one('kicker.game', string='Kicker Game')
    score = fields.Integer(string='Final Score')


class KickerGame(models.Model):
    _name = 'kicker.game'
    _description = 'Kicker Game'
    _rec_name = 'create_date'

    create_date = fields.Datetime()
    score_ids = fields.One2many('kicker.team.score', 'game_id', string='Team Scores')
    kicker_id = fields.Many2one('kicker.kicker', string='Kicker')
    winning_team_id = fields.Many2one('kicker.team', compute='_compute_result', store=True)
    losing_team_id = fields.Many2one('kicker.team', compute='_compute_result', store=True)

    @api.depends('score_ids', 'score_ids.score')
    def _compute_result(self):
        ordered_scores = sorted(self.mapped('score_ids'), key=attgetter('score'))
        for game in self:
            scores_for_team = filter(lambda s: s.game_id == game.id,ordered_score)
            game.winning_team = scores_for_team[0]
            game.winning_team = scores_for_team[1]