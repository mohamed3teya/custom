from odoo import fields, models

class SubjectRequiredFrom(models.Model):
    _name = 'op.subjectrequiredfrom'
    _description = 'op.subjectrequiredfrom'
    
    name = fields.Char()
    
    
class SubjectRequiredFrom(models.Model):
    _inherit = 'op.subject'
    
    subject_requiredfrom = fields.Many2one('op.subjectrequiredfrom', string='Required from')
    subject_elective = fields.Many2one('op.elective.groups', string='groups')