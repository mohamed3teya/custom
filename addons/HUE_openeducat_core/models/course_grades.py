from odoo import fields, models

class CourseGrades(models.Model):
    _name = 'op.course.grades'
    _description = 'op.course.grades'
    _rec_name = 'grade_id'
    
    course_id = fields.Many2one('op.course', string='Course')
    grade_Eqiv = fields.Many2one('op.gradeseqiv', string='Grade Equivalent')
    grade_id = fields.Many2one('op.grades', string='Grade', required=True)
    percent_from = fields.Float(string='Percent From', required=True)
    percent_to = fields.Float(string='Percent To', required=True)
    points_from = fields.Float(string='Points From', required=True)
    points_to = fields.Float(string='Points To')
    first_pass_grade = fields.Boolean(string='First Pass Grade')
    second_pass_grade = fields.Boolean(string='Second Pass Grade')
    honours_grade = fields.Boolean(string='Honours Grade')