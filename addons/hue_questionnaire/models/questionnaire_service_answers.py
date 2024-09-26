from odoo import models, fields


class servicequestionnaireanswersModel(models.Model):
    _name = 'questionnaire.service.answers'
    _description = 'questionnaire.service.answers'
    _inherit = ['mail.thread']
    
    
    course_id = fields.Many2one('op.course')
    academic_year_id = fields.Many2one('op.academic.year', string='Academic Year', required=True )
    semester_id = fields.Many2one('op.semesters', string='Joined Semester', required=True)
    question_id = fields.Many2one('questions',required=True)
    score_5 = fields.Integer()
    score_4 = fields.Integer()
    score_3 = fields.Integer()
    score_2 = fields.Integer()
    score_1 = fields.Integer()