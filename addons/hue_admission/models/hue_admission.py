from odoo import fields, models, api
from odoo.exceptions import ValidationError

class HorusAdmission(models.Model):
    _name = 'op.hue.admission'
    _description = 'op.hue.admission'
    
    name = fields.Char(required=True)
    active_admission = fields.Boolean(string="Active admission",required=True)
    join_year_id = fields.Many2one('hue.joining.years', string="Join Year",required=True)
    semster_id = fields.Many2one('op.semesters', string="semester",required=True)
    std_status_id = fields.Many2one('hue.std.data.status', string="student status",required=True)
    admission_register_ids = fields.One2many('op.admission.register', 'hue_admission_id', string='Admission Register')
    
    @api.constrains('active_admission')
    def validate_active_admission(self):
        for rec in self:
            domain = [
                ('active_admission', '=', True),
                ('id', '!=', rec.id),
            ]
            active_admission = self.search_count(domain)
            if active_admission:
                raise ValidationError(('Only 1 Admission can be active, disable any other active admission !'))