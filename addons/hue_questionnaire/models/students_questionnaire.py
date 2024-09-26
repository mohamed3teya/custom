from odoo import models, fields


class studentquestionnaireModel(models.Model):
    _name = 'students.questionnaire'
    _description = 'students.questionnaire'
    _inherit = ['mail.thread']


    student_id = fields.Many2one('op.student',required=True)
    academic_year_id = fields.Many2one('op.academic.year', string='Academic Year', required=True )
    semester_id = fields.Many2one('op.semesters', string='Joined Semester', required=True)