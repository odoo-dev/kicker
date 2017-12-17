import ast
import base64
import logging
import random
from functools import reduce
import werkzeug

from odoo import SUPERUSER_ID
from odoo import api, http
from odoo.http import request
from odoo.modules import get_module_resource
from odoo.addons.web.controllers.main import binary_content

_logger = logging.getLogger(__name__)


class KickerController(http.Controller):

    NUM_BG = 10

    @http.route(['/free', '/free/<model("kicker.kicker"):kicker>'], type='http', auth="public")
    def is_the_kicker_free(self, kicker=None, **kw):
        if not kicker:
            kicker = request.env['kicker.kicker'].sudo().search([], limit=1)
        if not kicker:
            return request.not_found()
        rand_bg = random.randrange(0, self.NUM_BG - 1, step=1)
        return request.render('kicker.page_is_free', {
            'is_free': kicker.is_available,
            'bg': ('yes_%s' if kicker.is_available else 'no_%s') % rand_bg,
        })

    @http.route(['/kicker/app', "/kicker/app/<path:route>"], auth="user")
    def app(self, **kw):
        return request.render('kicker.app', {'body_classname': 'o_kicker_app', 'user': request.env.user})

    @http.route(['/kicker/ping'], auth='none', csrf=False)
    def ping(self, token=False, status="", **kw):
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

    # JSON routes for the JS app
    @http.route('/app/init', type='json', auth="user", csrf=True)
    def init(self, **kw):
        user_info = request.env.user.read(['name', 'image_small'])
        return user_info

    @http.route('/app/dashboard', type='json', auth='user', csrf=False)
    def dashboard(self, **kw):
        User = request.env['res.users'].sudo()
        teammates = list(map(lambda u: User.env.ref('kicker.%s' % u), ['dbo', 'jem', 'mat']))
        teammates = reduce(lambda u, v: u + v, teammates)
        nightmares = list(map(lambda u: User.env.ref('kicker.%s' % u), ['bst', 'elo', 'mat']))
        nightmares = reduce(lambda u, v: u + v, nightmares)
        demo_data = {
            'wins': 36,
            'losses': 57,
            'teammates': teammates.read(['id', 'name']),
            'nightmares': nightmares.read(['id', 'name']),
            'graph': [32.0/52*100, 35.0/53*100, 36.0/54*100, 36.0/56*100, 36.0/57*100]
        }
        return demo_data


    @http.route('/app/community', type='json', auth='user', csrf=False)
    def community(self, **kw):
        User = request.env['res.users'].sudo()
        usual = list(map(lambda u: User.env.ref('kicker.%s' % u), ['dbo', 'jem', 'mat']))
        usual = reduce(lambda u, v: u + v, usual)
        rare = list(map(lambda u: User.env.ref('kicker.%s' % u), ['bst', 'elo']))
        rare = reduce(lambda u, v: u + v, rare)
        demo_data = {
            'usual': usual.read(['id', 'name']),
            'rare': rare.read(['id', 'name']),
        }
        return demo_data

    @http.route(['/kicker/avatar', '/kicker/avatar/<int:user_id>'], type='http', auth="public")
    def avatar(self, user_id=None, **kw):
        if not user_id:
            user_id = request.env.uid
        status, headers, content = binary_content(model='res.users', id=user_id, field='image_medium', default_mimetype='image/png', env=request.env(user=SUPERUSER_ID))

        if not content:
            img_path = get_module_resource('web', 'static/src/img', 'placeholder.png')
            with open(img_path, 'rb') as f:
                image = f.read()
            content = base64.b64encode(image)
        if status == 304:
            return werkzeug.wrappers.Response(status=304)
        image_base64 = base64.b64decode(content)
        headers.append(('Content-Length', len(image_base64)))
        response = request.make_response(image_base64, headers)
        response.status = str(status)
        return response