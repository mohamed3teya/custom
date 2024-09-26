from odoo import models, fields


class OpSessionRegistrationEnrollment(models.Model):
    _name = 'op.session.registration.enrollment'
    _description = 'op.session.registration.enrollment'


    name = fields.Char()
    status = fields.Selection([('active', 'Active'), ('inactive', 'Inactive')])
    active = fields.Boolean(default=True)
    student_id = fields.Many2one('op.student', 'Student')
    teacher_id = fields.Many2one('op.faculty', 'Teacher')
    role = fields.Selection([('student', 'Student'), ('teacher', 'Teacher'), ('administrator', 'Administrator')], readonly=True)
    primary = fields.Boolean(readonly=True)
    beginDate = fields.Date(readonly=True)
    endDate = fields.Date(readonly=True)
    registration_enrollment_id = fields.Many2one('op.session.registration', ondelete='cascade', readonly=False)
    course_id = fields.Many2one('op.course', related='registration_enrollment_id.course_id', store=True, readonly=False)