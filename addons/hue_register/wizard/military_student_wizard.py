# from odoo import models, fields

# class MilitaryStudentWizard(models.TransientModel):
#     _name = "military.student.wizard"
#     _description = "Military Student "
#     
#     faculity_id = fields.Many2one('hue.faculties', string='Faculty')
#     academic_year_id = fields.Many2one('op.academic.year', string='Academic Year')
#     semester_id = fields.Many2one('op.semesters', string='Semester')
#     military_num= fields.Many2one('military.student', string='Military number')
#     level = fields.Many2one('op.levels', string='Level')
#     student_status = fields.Many2many('hue.std.data.status')
#     no_military = fields.Boolean('student with no military!')
#     graduation_std = fields.Boolean('with graduate students!')
# 
# 
#     def check_report(self):
#         data = {}
#         data['form'] = self.read(['faculity_id'])[0]
#         print("data['form']:-----------------------------1", data['form'])
#         return self._print_report(data)
# 
# 
#     def _print_report(self, data):
#         data['form'].update(self.read(['faculity_id'])[0])
#         x = data['form'].update(self.read(['faculity_id'])[0])
#         print(" data['form']:-----------------------------2", x)
#         return self.env.ref('hue_register.action_military_student_report').report_action(self, data=data,config=False)

from odoo import api, fields, models

class MilitaryStudentWizard(models.TransientModel):
    _name = "military.student.wizard"
    _description = "Military Student"

    faculity_id = fields.Many2one('hue.faculties', string='Faculty')
    academic_year_id = fields.Many2one('op.academic.year', string='Academic Year')
    semester_id = fields.Many2one('op.semesters', string='Semester')
    military_num = fields.Many2one('military.student', string='Military number')
    level = fields.Many2one('op.levels', string='Level')
    student_status = fields.Many2many('hue.std.data.status')
    no_military = fields.Boolean('student with no military!')
    graduation_std = fields.Boolean('with graduate students!')

    def check_report(self):
        data = {'form': self.get_wizard_data()}
        print("data:----------------------------1", data)
        return self._print_report(data)

    def get_wizard_data(self):
        return {
            'faculity_id': self.faculity_id.id,
            'academic_year_id': self.academic_year_id.id,
            'semester_id': self.semester_id.id,
            'military_num': self.military_num.id,
            'level': self.level.id,
            'student_status': [(6, 0, self.student_status.ids)],
            'no_military': self.no_military,
            'graduation_std': self.graduation_std,
        }

    def _print_report(self, data):
        report = self.env.ref('hue_register.action_military_student_report')
        print("data----------------------------2", data)
        return report.report_action(self, data=data, config=False)
