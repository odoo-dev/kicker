from odoo import http

class KickerAPI(http.Controller):

    @http.route(['/free'], type='http', auth="none")
    def is_the_kicker_free(self):
        return '1'
