from odoo import models, fields, api


class RegistrationCancelWizard(models.TransientModel):
    _name = 'registration.cancel.wizard'
    _description = 'Wizard to capture registration cancellation reason'

    reason = fields.Text(string="Reason for Cancellation", required=True)

    def confirm_reason(self):
        registration_id = self.env.context.get('active_id')
        registration = self.env['medical.inpatient.registration'].browse(registration_id)

        registration.reason_cancel_registration = self.reason
        registration.state = 'cancel'