# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, _


class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    has_work_entries_public = fields.Boolean(compute='_compute_has_work_entries_public')

    def _compute_has_work_entries_public(self):
        employee_ids = self.employee_id
        self.env.cr.execute("""
        SELECT id, EXISTS(SELECT 1 FROM hr_work_entry WHERE employee_id = e.id limit 1)
          FROM hr_employee e
         WHERE id in %s
        """, (tuple(employee_ids.ids),))

        result = {eid[0]: eid[1] for eid in self.env.cr.fetchall()}

        for employee in self:
            employee.has_work_entries_public = result.get(employee.employee_id.id, False)

    def action_open_work_entries(self, initial_date=False):
        employee_id = self.employee_id
        self.ensure_one()
        ctx = {'default_employee_id': employee_id.id}
        if initial_date:
            ctx['initial_date'] = initial_date
        return {
            'type': 'ir.actions.act_window',
            'name': _('%s work entries', employee_id.display_name),
            'view_mode': 'calendar,tree,form',
            'res_model': 'hr.work.entry',
            'context': ctx,
            'domain': [('employee_id', '=', employee_id.id)],
        }
