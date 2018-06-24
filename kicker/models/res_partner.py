from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    kicker_team_ids = fields.Many2many('kicker.team', relation='kicker_team_res_partner_rel')
    wins = fields.Integer(compute='_compute_stats')
    losses = fields.Integer(compute='_compute_stats')
    kicker_player = fields.Boolean()
    main_kicker = fields.Many2one('kicker.kicker', 'Default Kicker')

    @api.depends('kicker_team_ids')
    def _compute_stats(self):
        teams = self.mapped('kicker_team_ids')
        data = self.env['kicker.team.score'].read_group([('team_id', 'in', teams.ids)], fields=['team_id', 'won'], groupby=['team_id', 'won'], lazy=False)
        for partner in self:
            wins = list(filter(lambda d: d['team_id'][0] in partner.kicker_team_ids.ids and d['won'], data))
            partner.wins = wins and sum(list(map(lambda w: w['__count'], wins)))
            losses = list(filter(lambda d: d['team_id'][0] in partner.kicker_team_ids.ids and not d['won'], data))
            partner.losses = losses and sum(list(map(lambda l: l['__count'], losses)))
