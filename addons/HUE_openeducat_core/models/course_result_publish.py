from odoo import fields, models

class CourseResultPublish(models.Model):
    _name = 'op.course.resultspublish'
    _description = 'op.course.resultspublish'
    
    acadyears = fields.Many2one('op.academic.year', string='Academic Year',required=True)
    course_id = fields.Many2one('op.course', string='Course',required=True)
    semesters = fields.Many2one('op.semesters', string='Semester',required=True)
    publishflag = fields.Selection([('open','open'),('close','close'),('publish','publish')], string='Publish')