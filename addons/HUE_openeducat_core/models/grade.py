from odoo import models, fields

class Grades(models.Model):
    _name = 'op.grades'
    _description = 'subject and level grades'

    name = fields.Char()
    add_to_gpa = fields.Boolean(string="Add To GPA", default=False)
    absent_grade = fields.Boolean(string="Absent Grade")
    pass_grade = fields.Boolean(string="Pass Grade")
    theoretical_fail = fields.Boolean(string="Theoretical Fail")
    sequence = fields.Integer(default=False)