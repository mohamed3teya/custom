from odoo import models, fields


class HUEStudentRegistration(models.Model):
    _name = 'hue.student.registration'
    _description = 'hue.student.registration'
    _inherit = ['mail.thread']

    batch_id = fields.Many2one('op.batch', string='Batch', required=True, tracking=True)
    course_id = fields.Many2one('op.course', string='Course', related='batch_id.course_id', store=True, tracking=True)
    status = fields.Selection([('Draft', 'Draft'), ('Pending', 'Pending'), ('Approved', 'Approved')], string='Status',
                              required=True, default='Draft', tracking=True)
    student_id = fields.Many2one('op.student', 'Student', required=True, tracking=True)
    session_id = fields.Many2one('op.session', 'Session', required=True, tracking=True, ondelete="cascade")

    def unlink(self):
        for rec in self:
            student_data = self.env['op.session'].sudo().search([('id', '=', rec.session_id.id)])
            student_data.write({'student_ids': [(3, rec.student_id.id)]})
        return super(HUEStudentRegistration, self).unlink()