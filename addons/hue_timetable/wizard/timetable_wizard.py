
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class TimetableWizard(models.TransientModel):
    _name = "timetable.wizard"
    _description = " Timetable wizard"

    course_id = fields.Many2one('op.course')
    batch_id = fields.Many2one('op.batch')
    subject_id = fields.Many2one('op.subject')
    faculty_id = fields.Many2one('op.faculty')
    facility_id = fields.Many2one('op.facility')
    student_id = fields.Many2one('op.student')
    level_id = fields.Many2one('op.levels')
    actual_lectures = fields.Boolean('Actual lectures!')
    course_batch_required = fields.Boolean(string='Course Required', compute='_compute_course_required', store=False)
    
    @api.onchange('facility_id', 'faculty_id')
    def _compute_course_required(self):
        self.course_batch_required = not (self.facility_id or self.faculty_id)
        
    @api.onchange('course_id')
    def onchange_course(self):
        if self.batch_id and self.course_id:
            if self.batch_id.course_id != self.course_id:
                self.batch_id = False

    def print_report(self):
        data = self.read(['course_id'])[0]
        report = self.env.ref('hue_timetable.action_report_timetable')
        return report.report_action(self, data=data)
    