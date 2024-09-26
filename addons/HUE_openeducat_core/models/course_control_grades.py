from odoo import fields, models

class CourseControlGrades(models.Model):
    _name = 'op.course.controlgrades'
    _description = 'op.course.controlgrades'
    
    course_id = fields.Many2one('op.course', string='Course')
    deduction_grade_first = fields.Many2one('op.grades', string='deduction Grade 1')
    deduction_grade_second = fields.Many2one('op.grades', string='deduction Grade 2')
    fr_percent = fields.Float(string='Fr Percent')
    pass_degree = fields.Float(string='Pass Degree')