from odoo import fields, models

class Committees(models.Model):
    _name = 'op.committees'
    _description = 'Add Committees'
    
    name = fields.Char('Name')


class ExamSubjectsCommittees(models.Model):
    _name = 'op.exam.committees'
    _description = 'Add Exams Subjects'
    
    course_id = fields.Many2one('op.course')
    subject_id = fields.Many2one('op.subject')
    from_date = fields.Char('FromDate', required=True)
    to_date = fields.Char('ToDate', required=True)
    committeeid = fields.Many2one('op.committees', required=True)
    acadyear = fields.Many2one('op.academic.year', required=True)
    semester = fields.Many2one('op.semesters', required=True)
    daydate = fields.Char('Day Date', required=True)