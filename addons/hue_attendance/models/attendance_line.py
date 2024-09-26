from odoo import models, fields, api
from datetime import datetime


class OpAttendanceSheetExt(models.Model):
    _inherit = 'op.attendance.line'

    session_id = fields.Many2one('op.session', 'Session', related='attendance_id.session_id', store=True, readonly=True)
    permitted = fields.Boolean('Permitted ?', default=False, tracking=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('start', 'Attendance Start'),
         ('done', 'Attendance Taken'), ('cancel', 'Cancelled')],
        'Status',store=True,compute='_compute_state',readonly=True)
    student_code = fields.Integer('Student Code', related='student_id.student_code', readonly=True)
    leave = fields.Char(compute='_compute_leave', string='Leave')
    active = fields.Boolean('Active',default=True)
    absence_reason = fields.Char(tracking=True)
    emp_id = fields.Many2one('hr.employee', 'Faculty' , readonly=True)
    student_id = fields.Many2one('op.student', 'Student', required=True, tracking=True, domain="[('id', 'in', suitable_student_ids)]")
    suitable_student_ids = fields.Many2many('op.student', compute='_compute_suitable_student_ids',) #to add domain to student
    
    def _compute_leave(self):
        for line in self:
            leaves = self.env['op.student.leaves'].sudo().search([('student_id', '=', line.student_id.id), ('date_from', '<=', line.attendance_date), ('date_to', '>=', line.attendance_date)], limit=1)
            if leaves:
                line.leave = leaves.leave_type
            else:
                line.leave = ''
    
    
    def _compute_state(self):
        for line in self:
            line.state = line.attendance_id.state
            
            
    #Add domain to students
    @api.onchange('student_id')
    def _compute_suitable_student_ids(self):
        for line in self:
            if line.batch_id:
                session = self.env['op.session'].search([('start_datetime', '>=', str(line.batch_id.default_week_start)+' 00:00:00'), ('start_datetime', '<=', str(line.batch_id.default_week_end)+' 23:59:59'), ('course_id', '=', line.course_id.id), ('batch_id', '=', line.batch_id.id), ('type', '=', line.session_id.type), ('timing_id', '=', line.session_id.timing_id.id), ('to_timing_id', '=', line.session_id.to_timing_id.id), ('classroom_id', '=', line.session_id.classroom_id.id), ('sub_classroom', '=', line.session_id.sub_classroom), ('facility_id', '=', line.session_id.facility_id.id)], limit=1)
                records = self.env['op.student'].search([('session_ids', '=', session.id)])
                line.suitable_student_ids = records.ids
                print("line.suitable_student_ids11111111111:-----------", line.suitable_student_ids)
            else:
                students = self.env['op.student'].search([])
                line.suitable_student_ids = students.ids
                print("line.suitable_student_ids22222222222:--------", line.suitable_student_ids)