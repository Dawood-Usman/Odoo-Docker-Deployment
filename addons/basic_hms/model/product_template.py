from odoo import api, fields, models, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_room = fields.Boolean(string='Is Room', default=False)
    room_type = fields.Selection([
        ('intensive_care_unit', 'Intensive Care Unit'),
        ('patient_room', 'Patient Room'),
        ('behavioral_room', 'Behavioral Room'),
        ('mental_health_room', 'Mental Health Room'),
        ('general_ward', 'General Ward'),
        ('semi_private', 'Semi Private')
    ], string='Room Type')

class ProductProduct(models.Model):
    _inherit = 'product.product'

    state = fields.Selection([
        ('available', 'Available'),
        ('occupied', 'Occupied')
    ], string='State', default='available')
    is_bed = fields.Boolean(string='Is Bed', default=False)

    def action_occupied(self):
        for rec in self:
            rec.state = 'occupied'

    def action_available(self):
        for rec in self:
            rec.state = 'available'