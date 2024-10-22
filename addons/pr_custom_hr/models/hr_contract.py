import pdb

from odoo import fields, models, api, _
from odoo.tools.safe_eval import safe_eval


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    currency_rate = fields.Float(string='Currency Rate')

    def compute_sheet(self):
        # context = {**self.env.context, 'currency_rate': self.currency_rate}
        # pdb.set_trace()
        self = self.with_context(currency_rate=self.currency_rate)
        res = super(HrPayslipEmployees, self).compute_sheet()
        return res


class HrContract(models.Model):
    _inherit = 'hr.contract'

    is_multi_currency = fields.Boolean(string='Is Multi Currency')
    secondary_currency_id = fields.Many2one('res.currency', string='Secondary Currency')
    lst_currency_rate = fields.Float(string='Last Currency Rate')
    wage_in_2nd_currency = fields.Float(string='Wage In Secondary Currency')
