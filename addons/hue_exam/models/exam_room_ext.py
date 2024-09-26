from odoo import models, fields, api


class OpExamRoom(models.Model):
    _inherit = 'op.exam.room'
    
    classroom_id = fields.Many2one('op.classroom', 'Classroom', required=False , tracking=True)
    college_id = fields.Many2one('hue.faculties', 'College', required=True, tracking=True)
    facility_id = fields.Many2one('op.facility', 'Facility', required=False, tracking=True)
    sequence = fields.Integer('Sequence', required=True, tracking=True)
    start = fields.Integer('Start', required=True, tracking=True)
    computer_lab = fields.Boolean(tracking=True)

    @api.constrains('capacity')
    def check_capacity(self):
        if self.capacity < 0:
            raise ValidationError(_('Enter proper Capacity'))