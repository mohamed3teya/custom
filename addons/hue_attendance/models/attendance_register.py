from odoo import models, fields

class OpAttendanceRegisterExt(models.Model):
    _inherit = 'op.attendance.register'


    def create_attendance(self):
        sessions = self.env['op.session'].search([('course_id', '=', self.course_id.id), ('batch_id', '=', self.batch_id.id)], limit=1)
        records = self.env['op.student'].search([('session_ids', '=', session.id)])

        for record in records:
            vals = {
                'attendance_id': self.id,
                'student_id': record.id,
                'present': False,
            }
            already = self.env['op.attendance.line'].sudo().search([('attendance_id','=',self.id),('student_id','=',record.id)],limit=1)
            if not already:
                modified_attendance =  self.env['op.attendance.line'].sudo().create(vals)