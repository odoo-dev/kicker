from odoo import http
from odoo.http import request

import random


class KickerController(http.Controller):

    NUM_BG = 10

    @http.route(['/free'], type='http', auth="public")
    def is_the_kicker_free(self, **kw):
        is_free = False
        rand_bg = random.randrange(0, self.NUM_BG - 1, step=1)
        bg = ('yes_%s' if is_free else 'no_%s') % rand_bg
        return request.render('kicker.page_is_free', {'is_free': is_free, 'bg': bg})
