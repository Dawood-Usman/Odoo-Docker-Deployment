from odoo import fields, models, api, _


class HrApplication(models.Model):
    _inherit = 'hr.applicant'

    resource_calendar_id = fields.Many2one('resource.calendar', string='Working Schedule')
    due_date = fields.Date(String="Acceptance Due Date")

    def send_offer_letter(self):
        self.env.ref('pr_employment_offer.email_template_job_offer').send_mail(self.id, force_send=True)
        # return self.env.ref('pr_employment_offer.action_report_offer_letter').report_action(self.id)
