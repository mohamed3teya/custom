from odoo import models, fields


class HUEStudentRegistrationLog(models.Model):
    _name = 'hue.student.registration.log'
    _description = 'hue.student.registration.log'
    _rec_name = 'student_id'

    student_id = fields.Many2one('op.student', 'Student', required=True, ondelete="cascade")
    batch_id = fields.Many2one('op.batch', string='Batch', required=True, ondelete="cascade")
    registerer = fields.Selection([('Student', 'Student'), ('Adviser', 'Adviser'), ('Admin', 'Admin')],
                                  string='Modifier', required=True, default='Student')
    update_time = fields.Datetime('Update Time')
    status = fields.Selection([('Draft', 'Draft'), ('Pending', 'Pending'), ('Approved', 'Approved')], string='Status',
                              required=True, default='Pending')
    user_id = fields.Many2one('res.users', 'User', required=True)
    session_ids = fields.Many2many('op.session', 'registration_session_rel', 'registration_id', 'session_id',
                                   string='Sessions', ondelete="cascade")