from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PatientDischargeWizard(models.TransientModel):
    _name = 'patient.discharge.wizard'
    _description = 'Wizard to capture patient discharge reason'

    reason = fields.Text(string="Reason for Patient Discharge", required=True)

    def confirm_reason(self):
        registration_id = self.env.context.get('active_id')
        registration = self.env['medical.inpatient.registration'].browse(registration_id)

        invoice_id = self.env['account.move'].sudo().search([
            ('invoice_origin', '=', registration.name)
        ])
        if invoice_id:
            amount_residual = invoice_id.amount_residual
            if amount_residual != 0:
                raise UserError(_('The patient should clear all its payment dues before discharge'))
            else:
                registration.reason_cancel_registration = self.reason
                registration.state = 'done'