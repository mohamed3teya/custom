from odoo import models, fields, api


class HUEAcademicCalendar(models.Model):
    _name = 'hue.event.calendar'
    _description = 'hue.event.calendar'
    _inherit = ['mail.thread']

    course_id = fields.Many2one('op.course', string='Course', required=True, tracking=True)
    type = fields.Selection(
        [('student_registration', 'Student Registration'), ('adviser_registration', 'Adviser Registration'),
         ('admin_registration', 'Admin Registration'),('exam_timetable', 'Exam Timetable'),
         ('study_timetable', 'Study Timetable'),('admission_apply', 'Admission Apply')],required=True, tracking=True)
    academic_year = fields.Many2one('op.academic.year', string='Academic Year', required=True, tracking=True)
    semester = fields.Many2one('op.semesters', string='Semester', required=True, tracking=True)
    start_date = fields.Datetime('Start Date', required=True, tracking=True)
    end_date = fields.Datetime('End Date', required=True, tracking=True)
    level = fields.Many2one('op.levels', string='Level', tracking=True)
    gpa_from = fields.Float('GPA From', required=True, tracking=True, default=0)
    gpa_to = fields.Float('GPA To', required=True, tracking=True, default=4.01)
    student_id = fields.Many2many('op.student', string='Student', compute='_compute_students', tracking=True,required=True)
    max_level =  fields.Boolean(default=False)
    
    
    # @api.onchange('course_id')
    # def onchange_course_id(self):
    #     for rec in self:
    #         rec.student_id = False
    #         students = self.env['op.student'].sudo().search([('course_id', '=', rec.course_id.id)])
    #         domain = {'student_id': [('id', 'in', students.ids)]}
    #         return {'domain': domain}
    
    @api.depends('course_id')
    def _compute_students(self):
        for rec in self:
            students = self.env['op.student'].sudo().search([('course_id', '=', rec.course_id.id)])
            rec.student_id = students.ids