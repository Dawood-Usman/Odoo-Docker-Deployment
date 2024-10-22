# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import api, fields, models


class HrLeaveType(models.Model):
    _inherit = "hr.leave.type"

    sandwich = fields.Boolean(string="Apply")
    leave_notification = fields.Boolean(string="Show Notification")


class LeaveApply(models.Model):
    _inherit = 'hr.leave'
    set_notification = fields.Boolean()

    @api.depends('request_date_from', 'request_date_to', 'employee_id')
    def _compute_number_of_days_display(self):
        res = super(LeaveApply, self)._compute_number_of_days_display()
        for record in self:
            start_date = record.date_from
            end_date = record.date_to
            if record.holiday_status_id.sandwich and record.employee_id:
                record.set_notification = record.holiday_status_id.leave_notification

                leave_dates = []
                for leave_days in record.employee_id.resource_calendar_id.global_leave_ids:
                    if leave_days.date_from.date() + timedelta(1) == leave_days.date_to.date():
                        leave_dates.append(str(leave_days.date_to.date()))
                    else:
                        duration = (leave_days.date_to - leave_days.date_from).days + 1
                        for single_date in (leave_days.date_from + timedelta(days) for days in range(duration)):
                            leave_dates.append(str(single_date.date()))

                working_days = []
                for day in record.employee_id.resource_calendar_id.attendance_ids:
                    if int(day.dayofweek) not in working_days:
                        working_days.append(int(day.dayofweek))
                total_days = (end_date - start_date).days + 1

                check = 0
                for day in range(1, 31):
                    next_date = (end_date + timedelta(day)).date()
                    next_dates = str(next_date) in leave_dates or next_date.weekday() not in working_days
                    if next_dates:
                        check += 1
                    else:
                        break
                for day in range(1, 31):
                    previous_date = (start_date - timedelta(day)).date()
                    previous_dates = str(previous_date) in leave_dates or previous_date.weekday() not in working_days
                    if previous_dates:
                        check += 1
                    else:
                        break
                if start_date.date() != end_date.date():
                    record.number_of_days = total_days + check
                    record.number_of_days_display = record.number_of_days
                else:
                    if record.number_of_days != 0:
                        record.number_of_days += check
                        record.number_of_days_display = record.number_of_days
            else:
                record.set_notification = False
                days, hours = record._get_duration()
                record.number_of_days = days
        return res
