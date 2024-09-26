from odoo import models, fields
from datetime import datetime

class FinancialYear(models.Model):
    _name = 'hue.years'
    _description = 'Horus financial years'


    name = fields.Char()
    join_year = fields.Many2one('hue.joining.years', string="Join Year",required=True)
    total = fields.Integer(string="Total EGP",required=True)
    total_dollar = fields.Integer(string="Total USD",required=True)
    total_special = fields.Integer(string="Total Special Cases",required=True)
    year = fields.Selection([(str(num), str(num)) for num in range((datetime.now().year)-15, (datetime.now().year)+1)], required=True)
    faculty = fields.Many2one('hue.faculties',required=True)
    notes = fields.Char(string="Total Notes")
    active = fields.Boolean(default=True)
    in_ids = fields.One2many('hue.installments', 'years_id', string='Year Installments')
    course_id = fields.Many2one('op.course', string='Course')
    increase_ids = fields.One2many('hue.years.increase', 'year_id', string='Year Installments Increase')
    scholarship = fields.Boolean()