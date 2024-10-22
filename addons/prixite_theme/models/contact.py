from odoo import models, fields

class ContactUs(models.Model):
    _name = 'contact'
    _description = 'Contact Us Form Entries'

    name = fields.Char(string='Name', required=True)
    email = fields.Char(string='Email', required=True)
    phone = fields.Char(string='Phone')
    company = fields.Char(string='Company')
    message = fields.Text(string='Message')