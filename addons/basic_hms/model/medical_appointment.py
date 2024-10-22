# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
#from datetime import datetime, date
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz

class medical_appointment(models.Model):
	_name = "medical.appointment"
	_description = "Medical Appointment"
	_inherit = 'mail.thread'

	name = fields.Char(string="Appointment ID", readonly=True ,copy=True)
	is_invoiced = fields.Boolean(copy=False,default = False)
	institution_partner_id = fields.Many2one('res.partner',domain=[('is_institution','=',True)],string="Health Center")
	inpatient_registration_id = fields.Many2one('medical.inpatient.registration',string="Inpatient Registration")
	patient_status = fields.Selection([
			('ambulatory', 'Ambulatory'),
			('outpatient', 'Outpatient'),
			('inpatient', 'Inpatient'),
		], 'Patient status', sort=False,default='outpatient')
	patient_id = fields.Many2one('medical.patient','Patient',required=True)
	urgency_level = fields.Selection([
			('a', 'Normal'),
			('b', 'Urgent'),
			('c', 'Medical Emergency'),
		], 'Urgency Level', sort=False,default="b")
	# appointment_date = fields.Datetime('Appointment Date',required=True,default = fields.Datetime.now)
	appointment_date = fields.Datetime(string='Appointment Date', required=True)
	appointment_end = fields.Datetime('Appointment End')
	doctor_id = fields.Many2one('medical.physician','Physician',required=True)
	no_invoice = fields.Boolean(string='Invoice exempt',default=True)
	validity_status = fields.Selection([
			('invoice', 'Invoice'),
			('tobe', 'To be Invoiced'),
		], 'Status', sort=False,readonly=True,default='tobe')
	appointment_validity_date = fields.Datetime('Validity Date')
	consultations_id = fields.Many2one('product.product','Consultation Service',required=True)
	comments = fields.Text(string="Info")
	state = fields.Selection([('draft','Draft'),('confirmed','Confirm'),('cancel','Cancel'),('done','Done')],string="State",default='draft')
	invoice_to_insurer = fields.Boolean('Invoice to Insurance')
	medical_patient_psc_ids = fields.Many2many('medical.patient.psc',string='Pediatrics Symptoms Checklist')
	medical_prescription_order_ids = fields.One2many('medical.prescription.order','appointment_id',string='Prescription')
	insurer_id = fields.Many2one('medical.insurance','Insurer')
	duration = fields.Integer('Duration')

	## new code
	state = fields.Selection([
		('draft', 'Draft'),
		('confirm', 'Confirm'),
		('paid', 'Paid'),
		('cancelled', 'Cancelled')
	], string='Stage', default='draft')

	patient_phone = fields.Char(string='Patient phone', readonly=True)
	invoice_count = fields.Integer(compute='_compute_invoice_data', string="Number of Invoices")
	invoice_ids = fields.One2many('account.move', 'invoice_origin', string='Invoices')

	@api.depends('invoice_ids.state', 'invoice_ids.currency_id', 'invoice_ids.amount_untaxed',
				 'invoice_ids.company_id')
	def _compute_invoice_data(self):
		for invoice in self:
			invoice.invoice_count = len(invoice.invoice_ids.filtered_domain(self._get_appointment_invoice_domain()))

	def _get_appointment_invoice_domain(self):
		return [('state', 'in', ('draft', 'posted', 'cancel'))]

	def action_view_appointment_invoice(self):
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

	@api.onchange('doctor_id', 'appointment_date')
	def _check_physician_availability(self):
		for rec in self:
			if rec.doctor_id and rec.appointment_date:
				## ensure that appointment date is today date or greater than today date
				appointment_date = rec.appointment_date.date()
				today_date = datetime.today().date()

				# Check if the appointment date is in the past
				if appointment_date < today_date:
					return {
						'warning': {
							'title': 'Invalid Date',
							'message': 'The appointment date must be today or in the future.'
						}
					}

				user_tz = self.env.user.tz or 'UTC'
				local_appointment_datetime = self._convert_utc_to_local(rec.appointment_date, user_tz)
				appointment_time = local_appointment_datetime.time()

				day_of_week = local_appointment_datetime.strftime('%w')
				schedule = self.env['medical.schedule'].search([
					('physician_id', '=', rec.doctor_id.id),
					('day_of_week', '=', day_of_week)
				])
				if schedule:
					# Check if the appointment time is within the doctor's available time slots
					for slot in schedule:
						start_time = self._convert_float_to_time(slot.start_time)
						end_time = self._convert_float_to_time(slot.end_time)

						if start_time <= str(appointment_time) <= end_time:
							return  # Valid time, so no warning or error

					# If no valid time slot found, show the available slots
					available_timings = [
						f"{self._convert_float_to_time(slot.start_time)} - {self._convert_float_to_time(slot.end_time)}"
						for slot in schedule
					]
					timings_message = f"The doctor is available at the following times: {', '.join(available_timings)}."

					return {
						'warning': {
							'title': 'Doctor Unavailable',
							'message': f"The selected time ({appointment_time}) is outside the doctor's available time slots. {timings_message}"
						}
					}
				else:
					# Doctor is not available on this day
					available_timings = [
						f"{self._get_day_name(slot.day_of_week)}: {self._convert_float_to_time(slot.start_time)} - {self._convert_float_to_time(slot.end_time)}"
						for slot in rec.doctor_id.medical_schedule_ids
					]
					timings_message = f"Doctor {rec.doctor_id.partner_id.name} is available at the following times:\n" + "\n".join(
						available_timings)

					return {
						'warning': {
							'title': 'Doctor Unavailable',
							'message': timings_message
						}
					}

	def _convert_float_to_time(self, float_time):
		"""Helper function to convert float time to HH:MM format"""
		hours = int(float_time)
		minutes = int((float_time - hours) * 60)
		return f"{hours:02d}:{minutes:02d}"

	def _get_day_name(self, day_of_week):
		"""Helper function to convert day index to name"""
		days = {
			'1': 'Monday', '2': 'Tuesday', '3': 'Wednesday', '4': 'Thursday',
			'5': 'Friday', '6': 'Saturday', '7': 'Sunday'
		}
		return days.get(day_of_week, '')

	def _convert_utc_to_local(self, utc_dt, user_tz):
		"""Convert a UTC datetime to the user's local timezone."""
		utc_dt = pytz.utc.localize(utc_dt)
		return utc_dt.astimezone(pytz.timezone(user_tz))

	def action_confirm(self):
		for rec in self:
			rec.state = 'confirm'

	def action_cancel(self):
		for rec in self:
			rec.state = 'cancelled'

	def print_appointment_receipt(self):
		for rec in self:
			print('hello')
	## new code
 
	def _valid_field_parameter(self, field, name):
		return name == 'sort' or super()._valid_field_parameter(field, name)

	@api.onchange('patient_id')
	def onchange_name(self):
		self.patient_phone = self.patient_id.phone
		ins_obj = self.env['medical.insurance']
		ins_record = ins_obj.search([('medical_insurance_partner_id', '=', self.patient_id.patient_id.id)])
		if len(ins_record)>=1:
			self.insurer_id = ins_record[0].id
		else:
			self.insurer_id = False

	@api.model_create_multi
	def create(self, vals_list):
		for vals in vals_list:
			vals['name'] = self.env['ir.sequence'].next_by_code('medical.appointment') or 'APT'
			# Check if institution_partner_id is being created
			if vals.get('institution_partner_id'):
				partner_vals = vals.get('institution_partner_id')
				if partner_vals:
					partner_id = self.env['res.partner'].sudo().search([
						('id', '=', partner_vals)
					])
					if partner_id:
						partner_id.is_institution = True
			msg_body = 'Appointment created'
			for msg in self:
				msg.message_post(body=msg_body)
		return super(medical_appointment, self).create(vals_list)


	@api.onchange('inpatient_registration_id')
	def onchange_patient(self):
		if not self.inpatient_registration_id:
			self.patient_id = ""
		inpatient_obj = self.env['medical.inpatient.registration'].browse(self.inpatient_registration_id.id)
		self.patient_id = inpatient_obj.id

	def confirm(self):
		self.write({'state': 'confirmed'})

	def done(self):
		self.write({'state': 'done'})

	def cancel(self):
		self.write({'state': 'cancel'})

	def print_prescription(self):
		return self.env.ref('basic_hms.report_print_prescription').report_action(self)


	def view_patient_invoice(self):
		self.write({'state': 'cancel'})

	def create_invoice(self):
		lab_req_obj = self.env['medical.appointment']
		account_invoice_obj  = self.env['account.move']
		account_invoice_line_obj = self.env['account.move.line']
		lab_req = lab_req_obj
		if lab_req.is_invoiced == True:
			raise UserError(_(' Invoice is Already Exist'))
		if lab_req.no_invoice == False:
			res = account_invoice_obj.create({'partner_id': lab_req.patient_id.patient_id.id,
												   'date_invoice': date.today(),
											 		'company_id': self.company_id.id,
											 		'journal_id': account_journal_id.id,
											 'account_id':lab_req.patient_id.patient_id.property_account_receivable_id.id,
											 })
			res1 = account_invoice_line_obj.create({'product_id':lab_req.consultations_id.id ,
											 'product_uom': lab_req.consultations_id.uom_id.id,
											 'name': lab_req.consultations_id.name,
											 'product_uom_qty':1,
											 'price_unit':lab_req.consultations_id.lst_price,
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
								'views': [ [list_view_id,'form' ]],
								'target': action.target,
								'context': action.context,
								'res_model': action.res_model,
								'res_id':res.id,
							}
				if res:
					result['domain'] = "[('id','=',%s)]" % res.id
		else:
			 raise UserError(_(' The Appointment is invoice exempt'))
		return result

	
		
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
