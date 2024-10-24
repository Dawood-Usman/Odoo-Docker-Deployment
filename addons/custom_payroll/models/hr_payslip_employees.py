# -*- coding: utf-8 -*-

from collections import defaultdict
from datetime import datetime, date, time
from dateutil.relativedelta import relativedelta
import pytz

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import format_date


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    def compute_sheet(self):
        self.ensure_one()
        if not self.env.context.get('active_id'):
            from_date = fields.Date.to_date(self.env.context.get('default_date_start'))
            end_date = fields.Date.to_date(self.env.context.get('default_date_end'))
            today = fields.date.today()
            first_day = today + relativedelta(day=1)
            last_day = today + relativedelta(day=31)
            if from_date == first_day and end_date == last_day:
                batch_name = from_date.strftime('%B %Y')
            else:
                batch_name = _('From %s to %s', format_date(self.env, from_date), format_date(self.env, end_date))
            payslip_run = self.env['hr.payslip.run'].create({
                'name': batch_name,
                'date_start': from_date,
                'date_end': end_date,
            })
        else:
            payslip_run = self.env['hr.payslip.run'].browse(self.env.context.get('active_id'))

        employees = self.with_context(active_test=False).employee_ids
        if not employees:
            raise UserError(_("You must select employee(s) to generate payslip(s)."))

        #Prevent a payslip_run from having multiple payslips for the same employee
        employees -= payslip_run.slip_ids.employee_id
        success_result = {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.payslip.run',
            'views': [[False, 'form']],
            'res_id': payslip_run.id,
        }
        if not employees:
            return success_result

        payslips = self.env['hr.payslip']
        Payslip = self.env['hr.payslip']

        contracts = employees._get_contracts(
            payslip_run.date_start, payslip_run.date_end, states=['open', 'close']
        ).filtered(lambda c: c.active)
        # contracts.generate_work_entries(payslip_run.date_start, payslip_run.date_end)
        # work_entries = self.env['hr.work.entry'].search([
        #     ('date_start', '<=', payslip_run.date_end + relativedelta(days=1)),
        #     ('date_stop', '>=', payslip_run.date_start + relativedelta(days=-1)),
        #     ('employee_id', 'in', employees.ids),
        # ])
        for slip in payslip_run.slip_ids:
            slip_tz = pytz.timezone(slip.contract_id.resource_calendar_id.tz)
            utc = pytz.timezone('UTC')
            date_from = slip_tz.localize(datetime.combine(slip.date_from, time.min)).astimezone(utc).replace(tzinfo=None)
            date_to = slip_tz.localize(datetime.combine(slip.date_to, time.max)).astimezone(utc).replace(tzinfo=None)
            # payslip_work_entries = work_entries.filtered_domain([
            #     ('contract_id', '=', slip.contract_id.id),
            #     ('date_stop', '<=', date_to),
            #     ('date_start', '>=', date_from),
            # ])
            # payslip_work_entries._check_undefined_slots(slip.date_from, slip.date_to)


        # if(self.structure_id.type_id.default_struct_id == self.structure_id):
            # work_entries = work_entries.filtered(lambda work_entry: work_entry.state != 'validated')
            # if work_entries._check_if_error():
            #     work_entries_by_contract = defaultdict(lambda: self.env['hr.work.entry'])
            #
            #     for work_entry in work_entries.filtered(lambda w: w.state == 'conflict'):
            #         work_entries_by_contract[work_entry.contract_id] |= work_entry
            #
            #     for contract, work_entries in work_entries_by_contract.items():
            #         conflicts = work_entries._to_intervals()
            #         time_intervals_str = "\n - ".join(['', *["%s -> %s" % (s[0], s[1]) for s in conflicts._items]])
            #     return {
            #         'type': 'ir.actions.client',
            #         'tag': 'display_notification',
            #         'params': {
            #             'title': _('Some work entries could not be validated.'),
            #             'message': _('Time intervals to look for:%s', time_intervals_str),
            #             'sticky': False,
            #         }
            #     }


        default_values = Payslip.default_get(Payslip.fields_get())
        payslips_vals = []
        for contract in self._filter_contracts(contracts):
            values = dict(default_values, **{
                'name': _('New Payslip'),
                'employee_id': contract.employee_id.id,
                'payslip_run_id': payslip_run.id,
                'date_from': payslip_run.date_start,
                'date_to': payslip_run.date_end,
                'contract_id': contract.id,
                'struct_id': self.structure_id.id or contract.structure_type_id.default_struct_id.id,
            })
            payslips_vals.append(values)
        payslips = Payslip.with_context(tracking_disable=True).create(payslips_vals)
        payslips._compute_name()
        payslips.compute_sheet()
        payslip_run.state = 'verify'

        return success_result