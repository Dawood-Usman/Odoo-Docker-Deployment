from odoo import api, fields, models, _

class MedicalSchedule(models.Model):
    _name = 'medical.schedule'
    _description = 'Doctor Schedule'

    physician_id = fields.Many2one('medical.physician', string='Physician', required=True)
    day_of_week = fields.Selection([
        ('1', 'Monday'),
        ('2', 'Tuesday'),
        ('3', 'Wednesday'),
        ('4', 'Thursday'),
        ('5', 'Friday'),
        ('6', 'Saturday'),
        ('7', 'Sunday'),
    ], string='Day of the Week', required=True)
    start_time = fields.Float(string='Start Time', required=True)
    end_time = fields.Float(string='End Time', required=True)