from odoo import models, fields, api
import logging


_logger = logging.getLogger(__name__)


class ControlSecurity(models.Model):
    _name = 'subjects.control.security'
    _description = 'subjects.control.security'
    _rec_name = 'user'


    user = fields.Many2one('hr.employee', string='User', required=True)
    course_id = fields.Many2one('op.course', string='Course', required=True)
    batch_id = fields.Many2one('op.batch', required=True)
    subject_id = fields.Many2many('op.subject', string='Subject', required=True)


    @api.onchange('course_id')
    def onchange_course_id(self):
        self.batch_id = False
        self.subject_id = False
        # if self.env.ref('hr_extention.group_service_manager') in self.env.user.groups_id:
        #     courses = self.env['op.course'].search([]).ids
        #     batches = self.env['op.batch'].sudo().search([('control_allowed', '=',True),('course_id', '=', self.course_id.id),('intern_batch', '=', False)])
        # else:
        emp = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)])
        if not emp:
            emp = self.env.user.employee_id
        # courses = emp.course_ids.ids
        courses = self.env['op.course'].search([]).ids #till service manager group is added
        batches = self.env['op.batch'].sudo().search([('control_allowed', '=',True),('course_id', '=', self.course_id.id),('intern_batch', '=', False)])
        domain = {'course_id': [('id', 'in', courses)], 'batch_id': [('id', 'in', batches.ids)]}
        return {'domain': domain}


    @api.onchange('batch_id')
    def onchange_batch_id(self):
        subject_ids = []
        for course_subject in self.batch_id.sudo().subject_registration_ids:
            if course_subject.sudo().id not in subject_ids:
                subject_ids.append(course_subject.sudo().id)
        if self.course_id.parent_id:
            parent_batch = self.env['op.batch'].sudo().search([('control_allowed', '=',True),('semester', '=', self.batch_id.semester.id),
                                                               ('academic_year', '=', self.batch_id.academic_year.id),
                                                               ('course_id', '=', self.course_id.parent_id.id),('intern_batch', '=', False)])
            for course_subject in parent_batch.sudo().subject_registration_ids:
                if course_subject.sudo().id not in subject_ids:
                    subject_ids.append(course_subject.sudo().id)
        subject_ids = self.env['op.subject'].sudo().search(
            ['|', ('course_id', '=', self.course_id.id), ('course_id', '=', self.course_id.parent_id.id),
             ('id', 'in', subject_ids)]).ids
        domain = {'subject_id': [('id', 'in', subject_ids)]}
        return {'domain': domain}
