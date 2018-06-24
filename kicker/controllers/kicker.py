import ast
import base64
import jinja2
import logging
import random
from functools import reduce
import werkzeug

from odoo import SUPERUSER_ID
from odoo import api, http
from odoo.exceptions import UserError
from odoo.http import request
from odoo.modules import get_module_resource
from odoo.addons.base.ir.ir_qweb import AssetsBundle
from odoo.addons.web.controllers.main import binary_content

_logger = logging.getLogger(__name__)


class KickerController(http.Controller):

    NUM_BG = 10

    def _get_or_create_team(self, player1, player2=None):
        if not player2:
            domain = [('player_ids', 'in', player1.ids)]
            player_ids = [(4, player1.id, False)]
        else:
            domain = ['&', ('player_ids', 'in', player1.ids), ('player_ids', 'in', player2.ids)]
            player_ids = [(4, player1.id, False), (4, player2.id, False)]
        team = request.env['kicker.team'].sudo().search(domain, limit=1)
        if not team:
            team = request.env['kicker.team'].sudo().create({
                'player_ids': player_ids
            })
        return team

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

    @http.route(['/kicker/', "/kicker/<path:route>"], auth="user")
    def app(self, **kw):
        return request.render('kicker.app', {'body_classname': 'o_kicker_app', 'user': request.env.user})

    # JSON routes
    @http.route('/kicker/json/dashboard', type='json', auth='user', csrf=False)
    def dashboard(self, **kw):
        partner = request.env.user.partner_id
        teammates = partner.kicker_team_ids.mapped('player_ids') - partner
        nightmares = partner.browse()
        data = {
            'name': partner.name,
            'wins': partner.wins,
            'losses': partner.losses,
            'teammates': teammates.read(['id', 'name', 'tagline']),
            'nightmares': nightmares.read(['id', 'name', 'tagline']),
            'graph': [32.0/52*100, 35.0/53*100, 36.0/54*100, 36.0/56*100, 36.0/57*100]
        }
        return data

    @http.route('/kicker/json/community', type='json', auth='user', csrf=False)
    def community(self, **kw):
        partner = request.env.user.partner_id
        usual = partner.kicker_team_ids.mapped('player_ids') - partner
        rare = partner.search([('kicker_player', '=', True), ('id', 'not in', usual.ids)]) - partner
        demo_data = {
            'usual': usual.read(['id', 'name', 'tagline']),
            'rare': rare.read(['id', 'name', 'tagline']),
        }
        return demo_data

    @http.route(['/kicker/json/player', '/kicker/json/player/<int:player_id>'], type='json', auth='user')
    def player_info(self, player_id=None, **kw):
        if not player_id:
            player_id = request.env.user.partner_id.id
        partner = request.env['res.partner'].browse(player_id)
        if not partner:
            raise werkzeug.exceptions.NotFound()
        return partner.read(['id', 'name', 'email', 'main_kicker_id', 'tagline'])[0]
    
    @http.route('/kicker/json/update_profile', type='json', auth='user', methods=['POST'], csrf=False)
    def update_profile(self, name, tagline, main_kicker, avatar=None, **kw):
        partner = request.env.user.partner_id
        vals = {
            'name': name,
            'tagline': tagline,
            'main_kicker_id': False if main_kicker == -1 else int(main_kicker),
        }
        if avatar:
            vals['image'] = avatar
        partner.write(vals)
        return {'success': True, 'player':partner.read(['id', 'name', 'email', 'main_kicker_id', 'tagline'])[0]}

    @http.route(['/kicker/json/players'], type='json', auth='user')
    def list_players(self, **kw):
        return request.env['res.partner'].search_read([('kicker_player', '=', True)], fields=['id', 'name'])

    @http.route(['/kicker/json/kickers'], type='json', auth='user')
    def list_kickers(self, **kw):
        kickers = request.env['kicker.kicker'].sudo().search_read([], fields=['id', 'nickname'])
        default = request.env.user.partner_id.main_kicker_id.id
        return {'kickers': kickers, 'default': default}

    @http.route(['/kicker/score/submit'], type='json', auth='user', methods=['POST'], csrf=False)
    def submit_score(self, **post):
        Partner = request.env['res.partner']
        player11 = post.get('player11') and Partner.browse(int(post.get('player11')))
        player21 = post.get('player21') and Partner.browse(int(post.get('player21')))
        if not player11 and player21:
            raise UserError(_('There must be at least one player per team.'))
        player12 = post.get('player12') and Partner.browse(int(post.get('player12')))
        player22 = post.get('player22') and Partner.browse(int(post.get('player22')))
        green_team = self._get_or_create_team(player11, player12)
        red_team = self._get_or_create_team(player21, player22)
        kicker = request.env['kicker.kicker'].browse(int(post.get('kicker_id')))
        game = request.env['kicker.game'].sudo().create({
            'kicker_id': kicker.id,
            'score_ids': [(0, False, {'team_id': green_team.id, 'score': int(post.get('score1'))}),
                          (0, False, {'team_id': red_team.id, 'score': int(post.get('score2'))})],
        })
        return {'success': True, 'game_id': game.id}

    # Non-json routes
    @http.route(['/kicker/avatar', '/kicker/avatar/<int:player_id>'], type='http', auth="public")
    def avatar(self, player_id=None, **kw):
        if not player_id:
            player_id = request.env.user.partner_id.id
        status, headers, content = binary_content(model='res.partner', id=player_id, field='image_medium', default_mimetype='image/png', env=request.env(user=SUPERUSER_ID))

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

    @http.route('/kicker/sw.js', type='http', auth='public')
    def serviceworker(self, **kw):
        bundles = ['web.assets_common', 'web.assets_frontend']
        attachments = request.env['ir.attachment']
        for bundle in bundles:
            attachments += attachments.search([
                ('url', '=like', '/web/content/%-%/{0}%'.format(bundle))
            ])
        urls = attachments.mapped('url')
        js = request.env['ir.ui.view'].render_template('kicker.service_worker', values={'urls': urls})
        headers = {
            'Content-Type': 'text/javascript',
        }
        response = http.request.make_response(js, headers=headers)
        return response