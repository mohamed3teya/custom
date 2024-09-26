from odoo import fields, models, api


class Semester(models.Model):
    _name = 'op.semesters'
    _description = 'HUE semetsers'

    name = fields.Char()
    sequence = fields.Integer(string="sequence")
    timetable_current = fields.Boolean(default=False)
    sds_current = fields.Boolean(default=False)
    enroll_semester = fields.Boolean(default=False)
    term_id = fields.Many2one('op.academic.term', string="Term")
    current = fields.Boolean(default=False)
    gpa_current = fields.Boolean(default=False)
    run_semester_gpa = fields.Boolean(default=False)