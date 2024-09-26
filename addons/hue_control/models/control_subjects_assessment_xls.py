from odoo import models, fields, api


class ControlResultXls(models.Model):
    _name = 'control.subjects.assessment.xls'
    _description = 'control.subjects.assessment.xls'


    connect_id = fields.Many2one('subjects.control', string='Control', ondelete='cascade', required=True, index=True)
    xls = fields.Binary(required=True)
    xls_type = fields.Selection([('team', 'team'), ('form', 'form')])
    assessment_id = fields.Many2one('op.assessments', required=True)
    status= fields.Selection([('active', 'active'), ('inactive', 'inactive')], default='active', required=True)


    @api.onchange('assessment_id')
    def filter_assessment_id(self):
        for rec in self:
            assessment_ids = rec.connect_id.subject_id.subject_assessmentsdegree.mapped('assessment_id.id')
            domain = {'assessment_id': [('id', 'in', assessment_ids)]}
            return {'domain': domain}