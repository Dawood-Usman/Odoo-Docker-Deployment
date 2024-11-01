from odoo import models, fields


class Testimonial(models.Model):
    _name = 'testimonials'

    name = fields.Char(string='Name', required=True)
    image = fields.Binary(string='Image')
    description = fields.Text(string='Description')
    designation = fields.Char(string='Designation')
    company_name = fields.Char(string='Company Name')
    website_url = fields.Char(string='Website URL')

