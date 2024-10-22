# -*- coding: utf-8 -*-
import pdb
from datetime import datetime, timedelta, date
from pytz import timezone, UTC
import pytz
from odoo import models, fields, api


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    late_check_in = fields.Integer(string="Late Check-in(Minutes)", compute="get_late_minutes", store=True)
    early_check_out = fields.Integer(string="Early Check-out(Minutes)", compute="get_early_minutes", store=True)

    def _is_first_checkin(self):
        Attendance = self.env['hr.attendance'].search([('employee_id', '=', self.employee_id.id)])
        today_entries = Attendance.filtered(lambda x: x.check_in.date() == self.check_in.date())
        if len(today_entries) == 1:
            return True
        else:
            return False
        # datetime.strptime(self.check_in, '')

    def _recheck_early_checkout(self):
        Attendance = self.env['hr.attendance'].search([('employee_id', '=', self.employee_id.id)])
        today_entries = Attendance.filtered(lambda x: x.check_out.date() == self.check_in.date())
        for rec in today_entries:
            rec.early_check_out = False
        return True

    @api.depends('check_in')
    def get_late_minutes(self):
        for rec in self:
            rec.late_check_in = 0.0
            # if rec.check_in and rec.status != 'Holiday':
            if rec.check_in:
                week_day = rec.sudo().check_in.weekday()
                if rec.employee_id.contract_id:
                    work_schedule = rec.sudo().employee_id.contract_id.resource_calendar_id
                    for schedule in work_schedule.sudo().attendance_ids:
                        if schedule.dayofweek == str(week_day) and schedule.day_period in ('morning', 'afternoon'):
                            work_from = schedule.hour_from
                            result = '{0:02.0f}:{1:02.0f}'.format(*divmod(work_from * 60, 60))
                            user_tz = self.env.user.tz
                            dt = rec.check_in
                            if user_tz in pytz.all_timezones:
                                old_tz = pytz.timezone('UTC')
                                new_tz = pytz.timezone(user_tz)
                                dt = old_tz.localize(dt).astimezone(new_tz)
                            str_time = dt.strftime("%H:%M")
                            check_in_date = datetime.strptime(str_time, "%H:%M").time()
                            start_date = datetime.strptime(result, "%H:%M").time()
                            t1 = timedelta(hours=check_in_date.hour, minutes=check_in_date.minute)
                            t2 = timedelta(hours=start_date.hour, minutes=start_date.minute)
                            if check_in_date > start_date and rec._is_first_checkin():
                                final = t1 - t2
                                final = (final.total_seconds() / 60) - rec.employee_id.late_check_in_after
                                if final > 0:
                                    rec.sudo().late_check_in = final

    @api.depends('check_out')
    def get_early_minutes(self):
        for rec in self:
            rec.early_check_out = 0.0
            # if rec.check_out and rec.status!='Holiday':
            if rec.check_out:
                week_day = rec.sudo().check_out.weekday()
                if rec.employee_id.contract_id:
                    work_schedule = rec.sudo().employee_id.contract_id.resource_calendar_id
                    # for schedule in work_schedule.sudo().attendance_ids:
                    day_schedule_line = work_schedule.sudo().attendance_ids.filtered(
                        lambda x: x.dayofweek == str(week_day) and x.day_period in ('morning', 'afternoon'))
                    # get the second half evening if available
                    day_schedule_line = day_schedule_line[1] if len(day_schedule_line) > 1 else day_schedule_line
                    if day_schedule_line:
                        work_to = day_schedule_line.hour_to
                        result = '{0:02.0f}:{1:02.0f}'.format(*divmod(work_to * 60, 60))

                        user_tz = self.env.user.tz
                        dt = rec.check_out

                        if user_tz in pytz.all_timezones:
                            old_tz = pytz.timezone('UTC')
                            new_tz = pytz.timezone(user_tz)
                            dt = old_tz.localize(dt).astimezone(new_tz)
                        out_time = dt.strftime("%H:%M")
                        check_out_time = datetime.strptime(out_time, "%H:%M").time()
                        schedule_end_time = datetime.strptime(result, "%H:%M").time()
                        t1 = timedelta(hours=check_out_time.hour, minutes=check_out_time.minute)
                        t2 = timedelta(hours=schedule_end_time.hour, minutes=schedule_end_time.minute)
                        # if check_out_time < schedule_end_time:
                        final = t2 - t1
                        # pdb.set_trace()
                        rec._recheck_early_checkout()
                        final = (final.total_seconds() / 60) - rec.employee_id.early_check_out_before
                        if final > 0:
                            rec.sudo().early_check_out = final

    def late_check_in_records(self):
        self.env['late.check_in'].sudo().search([]).unlink()
        existing_records = self.env['late.check_in'].sudo().search([]).attendance_id.ids
        minutes_after = int(self.env['ir.config_parameter'].sudo().get_param('late_check_in_after')) or 0
        late_check_in_ids = self.sudo().search([])  # ('status','=','Present')
        for rec in late_check_in_ids:
            if rec.late_check_in > minutes_after:
                self.env['late.check_in'].sudo().create({
                    'employee_id': rec.employee_id.id,
                    'late_minutes': rec.late_check_in,
                    'date': rec.check_in.date(),
                    'attendance_id': rec.id,
                })

    def early_check_out_records(self):
        self.env['early.check_out'].sudo().search([]).unlink()
        existing_records = self.env['early.check_out'].sudo().search([]).attendance_id.ids
        minutes_after = int(self.env['ir.config_parameter'].sudo().get_param('early_check_out_before')) or 0
        early_check_out_ids = self.sudo().search([])  # ('status','=','Present')
        for rec in early_check_out_ids:
            early_check_out = rec.sudo().early_check_out
            if rec.early_check_out > minutes_after:
                self.env['early.check_out'].sudo().create({
                    'employee_id': rec.employee_id.id,
                    'early_minutes': rec.early_check_out,
                    'date': rec.check_in.date(),
                    'attendance_id': rec.id,
                })


class HrContract(models.Model):
    _inherit = 'hr.contract'

    def calc_late_checkin_deduction(self, contract, payslip):
        print('ok')
