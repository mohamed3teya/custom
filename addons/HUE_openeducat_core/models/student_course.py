from odoo import fields, models
from datetime import datetime

class CustomStudentCourse(models.Model):
    _inherit = 'op.student.course'
    
    batch_id = fields.Many2one('op.batch', required=False)