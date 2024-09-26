from odoo import models, fields, api


class OpExamAttendees(models.Model):
    _inherit = 'op.exam.attendees'


    seat_no = fields.Char('Seat No')
    student_code = fields.Integer(related='student_id.student_code', store=True, readonly=True)
    start_time = fields.Datetime('Start Time', related='exam_id.start_time', store=True)
    end_time = fields.Datetime('End Time', related='exam_id.end_time', store=True)
    exam_type = fields.Many2one('op.exam.type', related='exam_id.exam_type', store=True)


    @api.onchange('exam_id')
    def onchange_exam(self):
        self.course_id = self.exam_id.session_id.course_id
        self.batch_id = self.exam_id.session_id.batch_id
        self.start_time = self.exam_id.start_time
        self.end_time = self.exam_id.end_time
        self.student_id = False