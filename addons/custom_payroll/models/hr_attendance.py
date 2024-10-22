#-*- coding: utf-8 -*-
from datetime import datetime, timedelta, UTC, time

from odoo import api, fields, models, _
import pytz

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    @api.model
    def _cron_attendance_absent(self):
        one_day_ago = datetime.now() - timedelta(days=1)
        one_day_ago_date = one_day_ago.date()

        local_tz = pytz.timezone(self.env.user.tz)
        checkin_local = datetime.combine(one_day_ago_date, time.min)
        checkin_utc = local_tz.localize(checkin_local).astimezone(UTC)

        checkin_utc_str = checkin_utc.strftime('%Y-%m-%d %H:%M:%S')
        checkin_utc_final = datetime.strptime(checkin_utc_str, '%Y-%m-%d %H:%M:%S')

        checkout_local = datetime.combine(one_day_ago_date, time.max)
        checkout_utc = local_tz.localize(checkout_local).astimezone(UTC)

        checkout_utc_str = checkout_utc.strftime('%Y-%m-%d %H:%M:%S')
        checkout_utc_final = datetime.strptime(checkout_utc_str, '%Y-%m-%d %H:%M:%S')

        working_hours_list = []

        employees = self.env['hr.employee'].search([])

        for employee_id in employees:
            working_hours_id = employee_id.resource_calendar_id.attendance_ids
            for att in working_hours_id:
                if att.dayofweek not in working_hours_list:
                    working_hours_list.append(att.dayofweek)


            if str(one_day_ago_date.weekday()) in working_hours_list:

                attendance_records = self.search([
                    ('employee_id', '=', employee_id.id),
                    ('check_in', '>=', checkin_utc_final),
                    ('check_in', '<', checkout_utc_final)
                ])

                if not attendance_records:
                    leave_records = self.env['hr.leave'].search([
                        ('employee_id', '=', employee_id.id),
                        ('state', '=', 'validate'),
                        ('request_date_from', '<=', one_day_ago_date),
                        ('request_date_to', '>=', one_day_ago_date)
                    ])

                    if not leave_records:
                        self.create({
                            'employee_id': employee_id.id,
                            'check_in': checkin_utc_final,
                            'check_out': checkin_utc_final,
                            'worked_hours': 0
                        })