from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class EmployeeCourseRel(models.Model):
    _name = 'employee.course.rel'
    _description = 'Employee Course Relation'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    course_id = fields.Many2one('op.course', string='Course', required=True)
    

class HrEmployeeExt(models.Model):
	_inherit = 'hr.employee'

	course_ids = fields.Many2many('op.course', 'employee_course_rel', 'employee_id', 'course_id', 'Courses')


class OpFacultyExt(models.Model):
	_inherit = 'op.faculty'

	job_id = fields.Many2one('hr.job', 'Job Position')
	department_id = fields.Many2one('hr.department', 'Department')
	id_number = fields.Char('ID Card Number', size=64, required=True)
	
	_sql_constraints = [
		('id_number_uniq', 'UNIQUE (id_number)', 'ID number already exist!'),
	]


	def create_employee(self):
		print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
		for record in self:
			if not record.last_name:
				record.write({'last_name': ' '})

			vals = {
				'name': record.name + ' ' + (record.middle_name or '') +
						' ' + (record.last_name or ''),
				'country_id': record.nationality.id,
				'gender': record.gender,
				'job_id': record.job_id.id,
				'department_id': record.department_id.id,
				'address_id': record.partner_id.id,
				'identification_id': record.id_number,
				'work_email': record.email,
			}
			print("vals:----------", vals)
			emp_id = self.env['hr.employee'].search([('identification_id', '=', record.id_number)], limit=1)
			print("emp_id:--------", emp_id)
			if emp_id:
				record.write({'emp_id': emp_id.id})
				record.sudo().partner_id.write({'employee': True, 'email': record.email}) #'supplier': True, 
			else:
				emp_id = self.env['hr.employee'].create(vals)
				record.write({'emp_id': emp_id.id})
				record.sudo().partner_id.write({'employee': True, 'email': record.email}) #'supplier': True, 


class ResUsers(models.Model):
	_inherit = "res.users"

	def create_user(self, records, user_group=None):
		oauth_provider = self.env['auth.oauth.provider'].sudo().search([('enabled', '=', True)], limit=1)
		if oauth_provider:
			provider = oauth_provider.id
		else:
			provider = 0
		for rec in records:
			if not rec.user_id:
				user_vals = {
					'name': rec.name,
					'login': rec.email,
					'partner_id': rec.partner_id.id,
					'oauth_provider_id': provider,
					'oauth_uid': rec.email,
					'groups_id': [(6, 0, [user_group.id])],
				}
				user_id = self.create(user_vals)
				rec.user_id = user_id
				if user_group:
					user_id.sudo().groups_id = [(6, 0, [user_group.id])]


class WizardOpFacultyEmployeeExt(models.TransientModel):
	_inherit = 'wizard.op.faculty.employee'
	_description = "Create Employee and User of Faculty"

	user_boolean = fields.Boolean("Want to create user too ?", default=True)

	def create_employee(self):
		for record in self:
			active_id = self.env.context.get('active_ids', []) or []
			faculty = self.env['op.faculty'].browse(active_id)
			faculty.create_employee()
			if not faculty.emp_id.user_id:
				if record.user_boolean and not faculty.user_id:
					user_group = self.env.ref('HUE_openeducat_core.group_advisor_admin')
					if faculty.email:
						user_id = self.env['res.users'].create_user(faculty, user_group)
						# user_id.employee_id = faculty.emp_id

				faculty.emp_id.user_id = faculty.user_id
			else:
				faculty.user_id = faculty.emp_id.user_id