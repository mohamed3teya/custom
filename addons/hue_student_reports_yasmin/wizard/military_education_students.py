
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class MilitaryStudentWizard(models.TransientModel):
    _name = "military.education.students.wizard"
    _description = "military education students wizard"

    faculty_id = fields.Many2one('hue.faculties')
    academic_year_id = fields.Many2one('op.academic.year', string='Academic Year')
    semester_id = fields.Many2one('op.semesters')
    military_num= fields.Many2one('military.student', string='Military number')
    level = fields.Many2one('op.levels')
    student_status = fields.Many2many('hue.std.data.status')
    no_military = fields.Boolean('student with no military!')

    def print_report(self):
        data = self.read(['faculty_id'])[0]
        report = self.env.ref('hue_student_reports_yasmin.action_report_military_education')
        return report.report_action(self, data=data)
    