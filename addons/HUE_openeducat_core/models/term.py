from odoo import models, fields


class HUETerms(models.Model):
    _inherit = 'op.academic.term'


    name = fields.Char()
    term_start_date = fields.Date(string="from date")
    term_end_date = fields.Date(string="to date")
    academic_year_id = fields.Many2one('op.academic.year', string="Academic Years")
    global_term_id = fields.Many2one('hue.global.terms', string="Global Term")
    active_validate = fields.Boolean(string="Active Validate", default=False)
    active_run = fields.Boolean(string="Active Run", default=False)
    semester_id = fields.Many2one('op.semesters', string='Semester')
    