from odoo import http
from odoo.http import request

class KickerController(http.Controller):

    @http.route(['/free'], type='http', auth="public")
    def is_the_kicker_free(self):
        is_free = True
        return request.render('kicker.page_is_free', {'is_free': is_free})
