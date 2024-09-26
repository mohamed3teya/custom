from odoo import models, fields


class AssessmentsDegrees(models.Model):
    _name = 'op.course.assessments.dgrees'
    _description = 'Add Assessments'
    _rec_name = 'assessment_id'

    subject_id = fields.Many2one('op.subject', 'Subject')
    assessment_id = fields.Many2one('op.assessments', 'Assessment', required=True)
    degree = fields.Float('Degree', required=True)
    showinresult = fields.Boolean('Show in Result')