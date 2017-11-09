from odoo import http


class KickerController(http.Controller):

    @http.route(['/free'], type='http', auth="public")
    def is_the_kicker_free(self):
        return request.render('kicker.page_is_free', {})
