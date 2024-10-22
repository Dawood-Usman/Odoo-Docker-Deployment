# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import date,datetime

from odoo.exceptions import ValidationError, UserError
from odoo.osv import expression


class medical_inpatient_registration(models.Model):
    _name = 'medical.inpatient.registration'
    _description = 'Medical Inpatient Registration'

    name = fields.Char(string="Registration Code", copy=False, readonly=True, index=True)
    patient_id = fields.Many2one('medical.patient',string="Patient",required=True)
    hospitalization_date = fields.Datetime(string="Hospitalization date",required=True)
    discharge_date = fields.Datetime(string="Expected Discharge date",required=True)
    attending_physician_id = fields.Many2one('medical.physician',string="Attending Physician")
    operating_physician_id = fields.Many2one('medical.physician',string="Operating Physician")
    admission_type = fields.Selection([('routine','Routine'),('maternity','Maternity'),('elective','Elective'),('urgent','Urgent'),('emergency','Emergency  ')],required=True,string="Admission Type")
    medical_pathology_id = fields.Many2one('medical.pathology',string="Reason for Admission")
    info = fields.Text(string="Extra Info")
    bed_transfers_ids = fields.One2many('bed.transfer','inpatient_id',string='Transfer Bed')
    medical_diet_belief_id = fields.Many2one('medical.diet.belief',string='Belief')
    therapeutic_diets_ids = fields.One2many('medical.inpatient.diet','medical_inpatient_registration_id',string='Therapeutic_diets')
    diet_vegetarian = fields.Selection([('none','None'),('vegetarian','Vegetarian'),('lacto','Lacto Vegetarian'),('lactoovo','Lacto-Ovo-Vegetarian'),('pescetarian','Pescetarian'),('vegan','Vegan')],string="Vegetarian")
    nutrition_notes = fields.Text(string="Nutrition notes / Directions")
    state = fields.Selection([('free','Free'),('confirmed','Confirmed'),('invoiced','Invoiced'),('hospitalized','Hospitalized'),('cancel','Cancel'),('done','Done')],string="State",default="free")
    nursing_plan = fields.Text(string="Nursing Plan")
    discharge_plan = fields.Text(string="Discharge Plan")
    icu = fields.Boolean(string="ICU")
    medication_ids = fields.One2many('medical.inpatient.medication','medical_inpatient_registration_id',string='Medication')

    product_id = fields.Many2one('product.product', string='Assign Bed', required=True,
                                 domain=[('is_bed','=',True)])
    is_invoiced = fields.Boolean(copy=False, default=False)
    validity_status = fields.Selection([
        ('invoice', 'Invoice'),
        ('tobe', 'To be Invoiced'),
    ], 'Status', sort=False, readonly=True, default='tobe')

    invoice_count = fields.Integer(compute='_compute_invoice_data', string="Number of Invoices")
    invoice_ids = fields.One2many('account.move', 'invoice_origin', string='Invoices')
    reason_cancel_registration = fields.Text(string='Reason Cancel Registration')
    reason_discharge = fields.Text(string='Reason Discharge')

    @api.depends('invoice_ids.state', 'invoice_ids.currency_id', 'invoice_ids.amount_untaxed',
                 'invoice_ids.company_id')
    def _compute_invoice_data(self):
        for invoice in self:
            invoice.invoice_count = len(invoice.invoice_ids.filtered_domain(self._get_appointment_invoice_domain()))

    def _get_appointment_invoice_domain(self):
        return [('state', 'in', ('draft', 'posted', 'cancel'))]

    def action_view_inpatient_invoice(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        action['context'] = self._prepare_appointment_invoice_context()
        action['domain'] = expression.AND(
            [[('invoice_origin', '=', self.name)], self._get_appointment_invoice_domain()])
        invoices = self.invoice_ids.filtered_domain(self._get_appointment_invoice_domain())
        if len(invoices) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices.id
        return action

    def _prepare_appointment_invoice_context(self):
        """ Prepares the context for a new quotation (sale.order) by sharing the values of common fields """
        self.ensure_one()
        invoice_context = {
            'default_invoice_origin': self.name,
            'default_partner_id': self.patient_id.patient_id.id,
            'default_company_id': self.env.company.id,
        }
        return invoice_context

    @api.constrains('hospitalization_date', 'discharge_date')
    def _check_discharge_date(self):
        for record in self:
            if record.discharge_date <= record.hospitalization_date:
                raise ValidationError("The Expected Discharge date must be after the Hospitalization date.")

    @api.model
    def default_get(self, fields):
        result = super(medical_inpatient_registration, self).default_get(fields)
        patient_id  = self.env['ir.sequence'].next_by_code('medical.inpatient.registration')
        if patient_id:
            if 'name' in fields:
                result.update({
                            'name':patient_id,
                           })
        return result

    def registration_confirm(self):
        registration_id = self.env['medical.inpatient.registration'].search([
            ('product_id', '=', self.product_id.id),
            ('state', 'not in', ['cancel', 'done']),
            ('id', '!=', self.id)
        ])
        if registration_id:
            raise UserError(_("Bed is already assigned to another patient"))
        else:
            self.write({'state': 'confirmed'})

    def registration_admission(self):
        invoice_id = self.env['account.move'].sudo().search([
            ('invoice_origin', '=', self.name)
        ])
        if invoice_id:
            if invoice_id.state == 'draft':
                raise UserError(
                    _('The invoice is still in draft state. Please validate it before admitting the patient.'))
            elif invoice_id.state == 'posted':
                amount_residual = invoice_id.amount_residual
                if amount_residual == invoice_id.amount_total:
                    raise UserError(
                        _('The patient has not made any payments yet. Please ensure at least a partial payment has been made.'))
                elif amount_residual > 0:
                    # Partial payment made, proceed
                    self.write({'state': 'hospitalized'})
                else:
                    # Full payment made, proceed
                    self.write({'state': 'hospitalized'})

    def registration_cancel(self):
        return {
            'name': 'Cancel Registration',
            'type': 'ir.actions.act_window',
            'res_model': 'registration.cancel.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('basic_hms.view_registration_cancel_wizard').id,
            'target': 'new',
            'context': {'default_model_id': self.id}
        }
        # self.write({'state': 'cancel'})

    def patient_discharge(self):
        return {
            'name': 'Patient Discharge',
            'type': 'ir.actions.act_window',
            'res_model': 'patient.discharge.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('basic_hms.view_patient_discharge_wizard').id,
            'target': 'new',
            'context': {'default_model_id': self.id}
        }
        # invoice_id = self.env['account.move'].sudo().search([
        #     ('invoice_origin', '=', self.name)
        # ])
        # if invoice_id:
        #     amount_residual = invoice_id.amount_residual
        #     if amount_residual != 0:
        #         raise UserError(_('The patient should clear all its payment dues before discharge'))
        #     else:
        #         self.write({'state': 'done'})

    def create_invoice(self):
        for lab_req_obj in self:
            # lab_req_obj = self.env['medical.inpatient.registration']
            account_invoice_obj = self.env['account.move']
            account_invoice_line_obj = self.env['account.move.line']
            lab_req = lab_req_obj
            if lab_req.is_invoiced == True:
                raise UserError(_(' Invoice is Already Exist'))
            else:
                res = account_invoice_obj.create({'partner_id': lab_req.patient_id.patient_id.id,
                                                  'date_invoice': date.today(),
                                                  'company_id': self.company_id.id,
                                                  'journal_id': account_journal_id.id,
                                                  'account_id': lab_req.patient_id.patient_id.property_account_receivable_id.id,
                                                  })
                res1 = account_invoice_line_obj.create({'product_id': lab_req.product_id.id,
                                                        'product_uom': lab_req.product_id.uom_id.id,
                                                        'name': lab_req.product_id.name,
                                                        'product_uom_qty': 1,
                                                        'price_unit': lab_req.product_id.standard_price,
                                                        'account_id': lab_req.patient_id.patient_id.property_account_receivable_id.id,
                                                        'invoice_id': res.id})

                if res:
                    lab_req.write({'is_invoiced': True})
                    imd = self.env['ir.model.data']
                    action = self.env.ref('account.action_invoice_tree1')
                    list_view_id = imd.sudo()._xmlid_to_res_id('account.view_order_form')
                    result = {
                        'name': action.name,
                        'help': action.help,
                        'type': action.type,
                        'views': [[list_view_id, 'form']],
                        'target': action.target,
                        'context': action.context,
                        'res_model': action.res_model,
                        'res_id': res.id,
                    }
                    if res:
                        result['domain'] = "[('id','=',%s)]" % res.id
            return result


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:s
