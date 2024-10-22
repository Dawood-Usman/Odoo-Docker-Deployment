import pdb

from odoo import fields, api, models, _
from odoo.exceptions import ValidationError


# class CRMLeadRelevancy(models.Model):
#     _name = 'crm.lead.relevancy'
#     name = fields.Char(string='Title')
#     code = fields.Char(string='Code')


class CRMLeads(models.Model):
    _inherit = "crm.lead"

    # lead_relevancy = fields.Many2one('crm.lead.relevancy', string='Relevancy')
    lead_relevancy = fields.Selection([
        ('yes', 'YES'),
        ('no', 'NO'),
    ], string='Relevancy', tracking=True)
    developer_note = fields.Text(string='Developer Note', tracking=True)
    developer_id = fields.Many2one('res.users', string='Assigned Developer')

    def write(self, vals):
        res = super().write(vals)
        vals.pop('lead_relevancy', False)
        vals.pop('developer_note', False)
        lead_url = f"/web#action=kp_developer_leads.developer_lead_action&amp;id={self.id}"
        if vals and self.env.user.has_group('kp_developer_leads.developer_group'):
            raise ValidationError(
                f"'Show Developer Leads' group is on for user {self.env.user} you are not allowed to change fields other than 'lead_relevancy' and 'developer_note'")
        if 'developer_id' in vals and (self.env.user.has_group('sales_team.group_sale_salesman') or self.env.user.has_group(
                'sales_team.group_sale_manager')):
            template = self.env.ref('kp_developer_leads.developer_user_mail')
            if template:
                template.sudo().send_mail(self.id, force_send=True)
        return res
