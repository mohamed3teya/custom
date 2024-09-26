from odoo import fields, models

class CustomFacility(models.Model):
    _inherit = 'op.facility'
    
    college_id = fields.Many2one('hue.faculties', string='College')
    college_only = fields.Boolean(string='College Only')
    exam_capacity = fields.Integer(string='Exam Capacity')
    study_capacity = fields.Integer(string='Study Capacity')