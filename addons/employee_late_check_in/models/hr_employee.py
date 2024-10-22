# -*- coding: utf-8 -*-
from odoo import models, fields, _
import logging

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    late_check_in_count = fields.Integer(string="Late Check-In", compute="get_late_check_in_count")
    late_check_in_after = fields.Integer(string="Late Check-in Starts After (Mint)", groups="hr.group_hr_user")
    early_check_out_before = fields.Integer(string="Early Check-out Starts Before (Mint)", groups="hr.group_hr_user")

    def action_to_open_late_check_in_records(self):
        print("===========")
        domain = [('employee_id', '=', self.id)]
        return {
            'name': _('Employee Late Check-in'),
            'domain': domain,
            'res_model': 'late.check_in',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'limit': 80,
        }

    def get_late_check_in_count(self):
        self.late_check_in_count = self.env['late.check_in'].search_count([('employee_id', '=', self.id)])


class HrEmployees(models.Model):
    _inherit = 'hr.employee.public'

    late_check_in_count = fields.Integer(string="Late Check-In", compute="get_late_check_in_count")

    def action_to_open_late_check_in_records(self):
        domain = [('employee_id', '=', self.id), ]
        return {
            'name': _('Employee Late Check-in'),
            'domain': domain,
            'res_model': 'late.check_in',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'limit': 80,
        }

    def get_late_check_in_count(self):
        self.late_check_in_count = self.env['late.check_in'].search_count([('employee_id', '=', self.id)])


class HrContract(models.Model):
    _inherit = 'hr.contract'

    def calc_unpaid_leaves_deduction(self, rule, contract, payslip):
        deduction = 0.0

        try:
            total_hrs = 0.0
            leave_records = self.env['hr.leave'].search([('employee_id', '=', payslip.employee_id.id),
                                                         ('request_date_to', '<=', payslip.date_to),
                                                         ('request_date_from', '>=', payslip.date_from),
                                                         ('state', '=', 'validate'),
                                                         ('holiday_status_id.name', '=', 'Unpaid')
                                                         ])

            for rec in leave_records:
                total_hrs += rec.number_of_days
            if total_hrs:
                deduction = (self.wage / 30.5) * total_hrs
        except Exception as e:
            _logger.exception(
                "Salary Rule Information: Deduction of Unpaid Leaves Rule (calc_late_checkin_deduction), Rule Code %s Error Message: %s" % (
                    rule, str(e)))
        return deduction

    def calc_late_checkin_deduction(self, category, rule, contract, payslip):
        obj, value = category
        deduction = 0.0
        late_checkin_minutes = int(contract.employee_id.late_check_in_after)
        early_checkout_minutes = int(contract.employee_id.early_check_out_before)

        try:
            late_check_in_id = self.env['hr.attendance'].search([
                ('employee_id', '=', payslip.employee_id.id),
                ('attendance_date', '<=', payslip.date_to),
                ('attendance_date', '>=', payslip.date_from)
            ])

            total_records = 0
            for x in late_check_in_id:
                total_records += x.late_check_in + x.early_check_out

            deduction = ((category.get('BASIC') / 30.5) / 8) / 60
            deduction = deduction * total_records
            # deduct_leave=round(total_records/3)
            # if total_records%3==0:
            #     deduction=(category.BASIC/30.5)*deduct_leave
        except Exception as e:
            _logger.exception(
                "Salary Rule Information: Deduction of Late Chaeckin and Early checkout Rule (calc_late_checkin_deduction), Rule Code %s Error Message: %s" % (
                    rule, str(e)))
        return deduction

    def w_calc_late_checkin_deduction(self, category, rule, contract, payslip):
        deduction = 0.0
        late_checkin_minutes = int(contract.employee_id.late_check_in_after)
        early_checkout_minutes = int(contract.employee_id.early_check_out_before)
        import pdb;
        pdb.set_trace()

        try:
            late_check_in_id = self.env['hr.attendance'].search([
                ('employee_id', '=', payslip.employee_id.id),
                ('attendance_date', '<=', payslip.date_to),
                ('attendance_date', '>=', payslip.date_from)
            ])

            total_records = 0
            for x in late_check_in_id:
                total_records += x.late_check_in + x.early_check_out

            deduction = ((contract.wage / 24) / 8) / 60
            deduction = deduction * total_records
            # deduct_leave=round(total_records/3)
            # if total_records%3==0:
            #     deduction=(category.BASIC/30.5)*deduct_leave
        except Exception as e:
            _logger.exception(
                "Salary Rule Information: Deduction of Late Chaeckin and Early checkout Rule (calc_late_checkin_deduction), Rule Code %s Error Message: %s" % (
                    rule, str(e)))
        return deduction
