from odoo.tests import common

class TestKicker(common.TransactionCase):
    
    def setUp(self):
        super(TestKicker, self).setUp()
        self.team1 = self.env['kicker.team'].create({
            'name': 'The Avengers',
            'player_ids': [(0, False, {'name': 'Iron Man'}), (0, False, {'name': 'Black Widow'})],
        })
        self.team2 = self.env['kicker.team'].create({
            'name': 'The Defenders',
            'player_ids': [(0, False, {'name': 'Jessica Jones'}), (0, False, {'name': 'Luke Cage'})],
        })
        self.kicker = self.env['kicker.kicker'].create({'nickname': 'Test Kicker'})


    def test_win(self):
        game = self.env['kicker.game'].create({
            'score_ids': [(0, False, {'team_id': self.team1.id, 'score': 11}), (0, False, {'team_id': self.team2.id, 'score': 9})]
            })
        self.assertEqual((self.team1.wins, self.team1.losses), (1, 0), "Wins/losses computation is off")
        self.assertEqual((self.team2.wins, self.team2.losses), (0, 1), "Wins/losses computation is off")

