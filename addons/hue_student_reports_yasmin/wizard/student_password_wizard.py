
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class StudentPasswordtWizard(models.TransientModel):
    _name = "student.password.wizard"
    _description = "student password wizard"

    student_id = fields.Many2one('op.student')
   
    def print_report(self):
        data = self.read(['student_id'])[0]
        report = self.env.ref('hue_student_reports_yasmin.action_report_student_password')
        return report.report_action(self, data=data)
    