from odoo import fields, models


class Grade_Equivalent(models.Model):
    _name= 'op.course.gradeseqiv'
    _description = 'op.course.gradeseqiv'
    
    course_id = fields.Many2one('op.course', string="Course")
    point_from = fields.Float(string="Point From")
    grade = fields.Selection([('Excellent', 'Excellent'),('V.Good', 'V.Good'),('Good','Good'),('Acceptable','Acceptable')])
    point_to = fields.Float(string="Point To")
    

class GradeEquiv(models.Model):
    _name= 'op.gradeseqiv'
    _description = 'op.gradeseqiv'
    
    name = fields.Char()