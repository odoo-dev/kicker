import ast
import logging
import random

from odoo import api, http
from odoo.http import request

_logger = logging.getLogger(__name__)


class KickerController(http.Controller):

    NUM_BG = 10

    @http.route(['/free', '/free/<model("kicker.kicker"):kicker>'], type='http', auth="public")
    def is_the_kicker_free(self, kicker=None, *kw):
        if not kicker:
            kicker = request.env['kicker.kicker'].sudo().search([], limit=1)
        if not kicker:
            return request.not_found()
        rand_bg = random.randrange(0, self.NUM_BG - 1, step=1)
        return request.render('kicker.page_is_free', {
            'is_free': kicker.is_available,
            'bg': ('yes_%s' if kicker.is_available else 'no_%s') % rand_bg,
        })

    @http.route(['/kicker/ping'], auth='none', csrf=False)
    def ping(self, token=False, status="", *kw):
        """
            TEST URL:
                /kicker/ping?token=123-456789-321&status={"available": True,"temperature":"15.4"}
        """
        with api.Environment.manage():
            if token:
                try:
                    ip_address = request.httprequest.environ['REMOTE_ADDR']
                    payload = ast.literal_eval(status)
                    available = status.get('available', False)
                    return request.env['kicker.ping'].sudo().ping(token, available, ip_address)
                except Exception as err:
                    _logger.error("Kicker Ping failed when evaluting status")
            return False
