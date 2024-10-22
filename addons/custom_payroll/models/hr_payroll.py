#-*- coding: utf-8 -*-
import calendar
from collections import defaultdict
import pytz
from datetime import datetime, time, timedelta, date
from dateutil.relativedelta import relativedelta

from odoo import api, Command, fields, models, _

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _get_attendance_worked_day_lines_values(self, domain=None):
        self.ensure_one()
        res = []
        hours_per_day = self._get_worked_day_lines_hours_per_day()
        work_hours = self.contract_id.get_work_hours(self.date_from, self.date_to, domain=domain)
        work_hours_ordered = sorted(work_hours.items(), key=lambda x: x[1])
        biggest_work = work_hours_ordered[-1][0] if work_hours_ordered else 0
        add_days_rounding = 0
        ## new code
        ## check the current month
        working_hours_list = []
        attendance_count = 0
        attendance_hours = 0
        absent_count = 0
        absent_hours = 0

        leave_data = defaultdict(lambda: {'days': 0, 'hours': 0})
        processed_leave_dates = set()

        date_from = self.date_from
        employee_id = self.employee_id

        ## also get the working times of employee
        working_hours_id = employee_id.resource_calendar_id.attendance_ids
        for att in working_hours_id:
            if att.dayofweek not in working_hours_list:
                working_hours_list.append(att.dayofweek)

        month_from = date_from.month
        year_from = date_from.year

        days_in_month_from = calendar.monthrange(year_from, month_from)[1]

        monthly_wage = self.contract_id.wage
        per_day_salary = monthly_wage / days_in_month_from

        for day in range(1, days_in_month_from + 1):
            current_date = date_from.replace(day=day)

            if current_date in processed_leave_dates:
                continue

            day_of_week = str(current_date.weekday())

            if day_of_week in working_hours_list:
                attendance_record = self.env['hr.attendance'].search([
                    ('employee_id', '=', employee_id.id),
                    ('check_in', '>=', current_date),
                    ('check_in', '<', current_date + timedelta(days=1)),
                    ('worked_hours', '!=', 0)
                ], limit=1)
                ## if attendance found, then mark present
                if attendance_record:
                    attendance_count += 1
                    attendance_hours += hours_per_day
                ## if not found then check the leave
                else:
                    leave_records = self.env['hr.leave'].search([
                        ('employee_id', '=', employee_id.id),
                        ('state', '=', 'validate'),
                        ('request_date_from', '<=', current_date),
                        ('request_date_to', '>=', current_date)
                    ])

                    if leave_records:
                        for leave in leave_records:

                            work_entry_type = leave.holiday_status_id.work_entry_type_id

                            # Calculate the leave duration
                            leave_start = leave.request_date_from
                            leave_end = leave.request_date_to

                            # Calculate total leave days for this leave period
                            # total_leave_days = (leave_end - leave_start).days + 1
                            total_leave_days = leave.number_of_days_display

                            full_days = int(total_leave_days)
                            fractional_day = total_leave_days - full_days

                            leave_hours_per_day = hours_per_day

                            # Track all days within this leave period in the processed_leave_dates set
                            for leave_day in range(full_days):
                                leave_date = leave_start + timedelta(days=leave_day)
                                processed_leave_dates.add(leave_date)

                            if fractional_day > 0:
                                # Add the fractional day date to processed_leave_dates
                                fractional_day_date = leave_start + timedelta(days=full_days)
                                processed_leave_dates.add(fractional_day_date)

                            # Add leave details dynamically, grouping by leave type
                            leave_data[work_entry_type]['days'] += total_leave_days
                            leave_data[work_entry_type]['hours'] += total_leave_days * leave_hours_per_day
                    ## if no leave, then mark absent or unpaid
                    else:
                        if current_date < date.today():
                            absent_count += 1
                            absent_hours += hours_per_day

        ## append the attendance
        if attendance_count > 0:
            attendance_work_entry_type = self.env['hr.work.entry.type'].search([
                ('name', '=', 'Attendance')
            ])
            attendance_line = {
                'work_entry_type_id': attendance_work_entry_type.id,
                'name': attendance_work_entry_type.name,
                'number_of_days': attendance_count,
                'number_of_hours': attendance_hours,
            }
            res.append(attendance_line)

        for work_entry_type, data in leave_data.items():
            if data['days'] > 0:
                leave_line = {
                    'work_entry_type_id': work_entry_type.id,
                    'name': work_entry_type.name,
                    'number_of_days': data['days'],
                    'number_of_hours': data['hours']
                }
                res.append(leave_line)

        if absent_count > 0:
            absent_work_entry_type = self.env['hr.work.entry.type'].search([
                ('name', '=', 'Absent')
            ])
            absent_line = {
                'work_entry_type_id': absent_work_entry_type.id,
                'name': absent_work_entry_type.name,
                'number_of_days': absent_count,
                'number_of_hours': absent_hours
            }
            res.append(absent_line)


        return res

        ## new code

    def _get_worked_day_lines(self, domain=None, check_out_of_contract=True):
        """
        :returns: a list of dict containing the worked days values that should be applied for the given payslip
        """
        res = []
        # fill only if the contract as a working schedule linked
        self.ensure_one()
        contract = self.contract_id
        if contract.resource_calendar_id:
            # res = self._get_worked_day_lines_values(domain=domain)
            res = self._get_attendance_worked_day_lines_values(domain=domain)
            if not check_out_of_contract:
                return res

            # If the contract doesn't cover the whole month, create
            # worked_days lines to adapt the wage accordingly
            out_days, out_hours = 0, 0
            reference_calendar = self._get_out_of_contract_calendar()
            if self.date_from < contract.date_start:
                start = fields.Datetime.to_datetime(self.date_from)
                stop = fields.Datetime.to_datetime(contract.date_start) + relativedelta(days=-1, hour=23, minute=59)
                out_time = reference_calendar.get_work_duration_data(start, stop, compute_leaves=False, domain=['|', ('work_entry_type_id', '=', False), ('work_entry_type_id.is_leave', '=', False)])
                out_days += out_time['days']
                out_hours += out_time['hours']
            if contract.date_end and contract.date_end < self.date_to:
                start = fields.Datetime.to_datetime(contract.date_end) + relativedelta(days=1)
                stop = fields.Datetime.to_datetime(self.date_to) + relativedelta(hour=23, minute=59)
                out_time = reference_calendar.get_work_duration_data(start, stop, compute_leaves=False, domain=['|', ('work_entry_type_id', '=', False), ('work_entry_type_id.is_leave', '=', False)])
                out_days += out_time['days']
                out_hours += out_time['hours']

            if out_days or out_hours:
                work_entry_type = self.env.ref('hr_payroll.hr_work_entry_type_out_of_contract')
                res.append({
                    'sequence': work_entry_type.sequence,
                    'work_entry_type_id': work_entry_type.id,
                    'number_of_days': out_days,
                    'number_of_hours': out_hours,
                })
        return res

    @api.depends('employee_id', 'contract_id', 'struct_id', 'date_from', 'date_to')
    def _compute_worked_days_line_ids(self):
        if not self or self.env.context.get('salary_simulation'):
            return
        valid_slips = self.filtered(
            lambda p: p.employee_id and p.date_from and p.date_to and p.contract_id and p.struct_id)
        if not valid_slips:
            return
        # Make sure to reset invalid payslip's worked days line
        self.update({'worked_days_line_ids': [(5, 0, 0)]})
        # Ensure work entries are generated for all contracts
        generate_from = min(p.date_from for p in valid_slips) + relativedelta(days=-1)
        generate_to = max(p.date_to for p in valid_slips) + relativedelta(days=1)
        # self.contract_id.generate_work_entries(generate_from, generate_to)
        #
        # work_entries = self.env['hr.work.entry'].search([
        #     ('date_stop', '<=', generate_to),
        #     ('date_start', '>=', generate_from),
        #     ('contract_id', 'in', self.contract_id.ids),
        # ])
        # work_entries_by_contract = defaultdict(lambda: self.env['hr.work.entry'])
        # for work_entry in work_entries:
        #     work_entries_by_contract[work_entry.contract_id.id] += work_entry

        for slip in valid_slips:
            if not slip.struct_id.use_worked_day_lines:
                continue

            # convert slip.date_to to a datetime with max time to compare correctly in filtered_domain.
            slip_tz = pytz.timezone(slip.contract_id.resource_calendar_id.tz)
            utc = pytz.timezone('UTC')
            date_from = slip_tz.localize(datetime.combine(slip.date_from, time.min)).astimezone(utc).replace(
                tzinfo=None)
            date_to = slip_tz.localize(datetime.combine(slip.date_to, time.max)).astimezone(utc).replace(tzinfo=None)
            # payslip_work_entries = work_entries_by_contract[slip.contract_id].filtered_domain([
            #     ('date_stop', '<=', date_to),
            #     ('date_start', '>=', date_from),
            # ])
            # payslip_work_entries._check_undefined_slots(slip.date_from, slip.date_to)
            # YTI Note: We can't use a batched create here as the payslip may not exist
            slip.update({'worked_days_line_ids': slip._get_new_worked_days_lines()})

class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    @api.depends('is_paid', 'is_credit_time', 'number_of_hours', 'payslip_id', 'contract_id.wage',
                 'payslip_id.sum_worked_hours')
    def _compute_amount(self):
        for worked_days in self:
            ## new code
            month_from = worked_days.payslip_id.date_from.month
            year_from = worked_days.payslip_id.date_from.year

            days_in_month_from = calendar.monthrange(year_from, month_from)[1]

            monthly_wage = worked_days.payslip_id.contract_id.wage
            per_day_salary = monthly_wage / days_in_month_from
            ## new code
            if worked_days.payslip_id.edited or worked_days.payslip_id.state not in ['draft', 'verify']:
                continue
            if not worked_days.contract_id or worked_days.code == 'OUT' or worked_days.is_credit_time:
                worked_days.amount = 0
                continue
            if worked_days.payslip_id.wage_type == "hourly":
                worked_days.amount = worked_days.payslip_id.contract_id.hourly_wage * worked_days.number_of_hours if worked_days.is_paid else 0
            else:
                # worked_days.amount = worked_days.payslip_id.contract_id.contract_wage * worked_days.number_of_hours / (
                #             worked_days.payslip_id.sum_worked_hours or 1) if worked_days.is_paid else 0
                worked_days.amount = per_day_salary * worked_days.number_of_days
