
import uuid

import odoo
from odoo import api, fields, models, SUPERUSER_ID
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)


class Kicker(models.Model):

	_name = 'kicker.kicker'
	_descrption = 'Kicker'
	_order = 'nickname'

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
			kicker.available = kicker.ping_ids[0].available

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
