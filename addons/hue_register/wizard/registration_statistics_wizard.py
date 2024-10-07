
from odoo import api, fields, models


class registrationStatisticsWizard(models.TransientModel):
    _name = "registration.statistics.wizard"
    _description = "registration statistics wizard"
    
    course_id = fields.Many2one('op.course', string='Course', required=True)
    subject_id = fields.Many2one('op.subject', domain="[('id', 'in', suitable_subject_ids)]")
    suitable_subject_ids = fields.Many2many('op.subject', compute='_compute_suitable_subject_ids')
   
    @api.onchange('course_id')
    def _compute_suitable_subject_ids(self):
        for rec in self:
            rec.subject_id = False
            subjects = self.env['op.subject'].sudo().search([('course_id', '=', rec.course_id.id)])
            rec.suitable_subject_ids = subjects.ids



    def check_report(self):
        data = {}
        data['form'] = self.read(['course_id'])[0]
        return self._print_report(data)


    def _print_report(self, data):
        data['form'].update(self.read(['course_id'])[0])
        return self.env.ref('hue_register.action_registration_statistics').report_action(self, data=data,
                                                                                                   config=False)
