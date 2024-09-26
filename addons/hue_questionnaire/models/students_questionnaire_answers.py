from odoo import models, fields


class studentquestionnaireanswersModel(models.Model):
    _name = 'students.questionnaire.answers'
    _description = 'students.questionnaire.answers'
    _inherit = ['mail.thread']
    
    
    subject_id = fields.Many2one('op.subject', string='Subject', required=True)
    course_id = fields.Many2one('op.course', related='subject_id.course_id', readonly=True, store=True)
    academic_year_id = fields.Many2one('op.academic.year', string='Academic Year', required=True )
    semester_id = fields.Many2one('op.semesters', string='Joined Semester', required=True)
    question_id = fields.Many2one('questions',required=True)
    score_5 = fields.Integer()
    score_4 = fields.Integer()
    score_3 = fields.Integer()
    score_2 = fields.Integer()
    score_1 = fields.Integer()