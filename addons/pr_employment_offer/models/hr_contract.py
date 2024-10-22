import pdb

from odoo import fields, models, api, _


class HrContract(models.Model):
    _inherit = 'hr.contract'

    us_complete_salary = fields.Integer(string="US Complete Salary", store=True)

    def write(self, vals):
        old_state = False
        old_salary = False
        if 'us_complete_salary' in vals:
            old_salary = self.us_complete_salary
        elif 'state' in vals:
            old_state = self.state
        res = super().write(vals)
        for contract in self:
            old_state and self.env.ref('pr_employment_offer.email_template_contract_state').with_context(
                old_state=old_state).send_mail(contract.id, force_send=True) or True
            isinstance(old_salary, int) and self.env.ref(
                'pr_employment_offer.email_template_salary_update').with_context(
                old_salary=old_salary).send_mail(contract.id, force_send=True) or True

        return res
