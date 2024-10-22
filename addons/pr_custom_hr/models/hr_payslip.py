import pdb

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    currency_rate = fields.Float(string='Currency Rate')

    def _contract_multicurrency_setup(self):
        # pdb.set_trace()
        multi_currency_contract = self.contract_id.is_multi_currency
        # currency_rate = payslip.contract_id.lst_currency_rate
        currency_rate = self.env.context.get('currency_rate', False) or self.currency_rate
        if multi_currency_contract and currency_rate:
            self.contract_id.lst_currency_rate = currency_rate
            self.contract_id.wage = currency_rate * self.contract_id.wage_in_2nd_currency
        elif multi_currency_contract and not currency_rate:
            raise UserError(
                _(f'Contract for user {self.employee_id.name} is a multicurrency contract but currency rate is not given'))
        return True

    def compute_sheet(self):
        payslips = self.filtered(lambda slip: slip.state in ['draft', 'verify'])
        # delete old payslip lines
        payslips.line_ids.unlink()
        # this guarantees consistent results
        self.env.flush_all()
        today = fields.Date.today()
        for payslip in payslips:
            payslip._contract_multicurrency_setup()
            number = payslip.number or self.env['ir.sequence'].next_by_code('salary.slip')
            payslip.write({
                'number': number,
                'state': 'verify',
                'compute_date': today
            })
        self.env['hr.payslip.line'].create(payslips._get_payslip_lines())
        return True
