from odoo import fields, models

class CourseLoadHoursLevels(models.Model):
    _name = 'op.course.loadhourslevels'
    _description = 'op.course.loadhourslevels'
    
    course_id = fields.Many2one('op.course', string='Course',required=True)
    gpa_from = fields.Float(string='GPA From',required=True)
    gpa_to = fields.Float(string='GPA To',required=True)
    hours_from = fields.Integer(string='Hours From',required=True)
    hours_to = fields.Integer(string='Hours To',required=True)
    LH_levels = fields.Many2one('op.levels', string='Level',required=True)
    LH_semesters = fields.Many2one('op.semesters', string='Semester',required=True)