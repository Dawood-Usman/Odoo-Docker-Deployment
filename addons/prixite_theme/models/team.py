from odoo import models, fields


class TeamCategory(models.Model):
    _name = 'team.category'
    _description = 'Category of team members based on skills or roles'

    name = fields.Char(string='Name', required=True)


class TechStackImage(models.Model):
    _name = 'tech.stack.image'
    _description = 'Tech Stack Image'

    image = fields.Binary(string='Image', required=True)
    title = fields.Char(string='Title', required=True)
    team_member_id = fields.Many2one('team.member', string='Team Member', ondelete='cascade')


class TeamMember(models.Model):
    _name = 'team.member'
    _description = 'Team Member'

    name = fields.Char(string='Name', required=True)
    title = fields.Char(string='Title', required=True)
    bio = fields.Text(string='Bio')
    description = fields.Text(string='Description')
    profile = fields.Binary(string='Image')
    category_ids = fields.Many2many('team.category', string='Categories')
    tech_stack_image_ids = fields.One2many('tech.stack.image', 'team_member_id', string='Tech Stack Images')
