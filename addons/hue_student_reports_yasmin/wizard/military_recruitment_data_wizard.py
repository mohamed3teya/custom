
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class MilitaryrecruitmentWizard(models.TransientModel):
    _name = "military.recruitment.data.wizard"
    _description = "military recruitment data wizard"

    faculty = fields.Many2one('hue.faculties','Faculty')
    student_city = fields.Many2one('hue.cities','Student City')
    student_certificate = fields.Many2one('hue.certificates','Student Certificate')
    level = fields.Many2one('op.levels', 'level')
    student_status = fields.Many2many('hue.std.data.status')
    join_year = fields.Many2one('hue.joining.years' , string="Join Year")
    age = fields.Integer ( )
    age_date = fields.Date()
    military_status = fields.Selection([('ادي الخدمة','ادي الخدمة'),('معاف مؤقت','معاف مؤقت'),('معاف نهائي','معاف نهائي'),('مؤجل لسن 28','مؤجل لسن 28'),('مؤجل لسن 29','مؤجل لسن 29'),('تحت الطلب','تحت الطلب')])
    std_per_page = fields.Integer( required=True ,default=10)
    all_military_status = fields.Boolean()

    def print_report(self):
        data = self.read(['faculty'])[0]
        report = self.env.ref('hue_student_reports_yasmin.action_report_military_recruitment')
        return report.report_action(self, data=data)
    