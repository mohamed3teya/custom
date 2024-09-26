from odoo import models, fields


class opStudentsStudyTimetable(models.Model):
    _inherit = 'op.student'

    session_ids = fields.Many2many('op.session', 'student_session_rel', 'student_id', 'session_id', 'Registrations')


    def student_transcript(self):
        print('____________________________________________________________________________________')
        data = {'form': {'student_id': self.env.context.get('active_id', False), 'report_type': 'transcript'}}
        print("Data:----------------1111111111111------------", data['form']['student_id'])
        return self.env.ref('hue_student_reports.action_report_transcript_internal').report_action(self, data=data,
                                                                                                    config=False)

    def student_progress(self):
        print('____________________________________________________________________________________')
        data = {'form': {'student_id': self.env.context.get('active_id', False), 'report_type': 'transcript'}}
        return self.env.ref('hue_student_reports.action_report_student_progress_internal').report_action(self, data=data,config=False)


    def student_registration_form(self):
        data = {'form': {'student_id': self.env.context.get('active_id', False), 'report_type': 'registration'}}
        return self.env.ref('hue_student_reports.action_student_registration_report').report_action(self, data=data, config=False)


    def student_gpa_debug(self):
        data = {'form': {'student_id': self.env.context.get('active_id', False), 'report_type': 'registration'}}
        return self.env.ref('hue_student_reports.action_student_gpa_debug_report').report_action(self, data=data,config=False)


    def student_timetable(self):
        data = {'form': {'student_id': self.env.context.get('active_id', False)}}
        return self.env.ref('hue_timetable.action_report_timetable').report_action(self, data=data, config=False)
    
    
    def student_exam(self):
        data = {'form': {'student_id': self.env.context.get('active_id', False)}}
        return self.env.ref('hue_student_reports.action_student_exam_report').report_action(self, data=data, config=False)


    def student_subject_result(self):
        data = {'form': {'student_id': self.env.context.get('active_id', False)}}
        return self.env.ref('hue_student_reports.action_subject_result_report').report_action(self, data=data, config=False)


    def student_attendance(self):
        data = {'form': {'student_id': self.env.context.get('active_id', False)}}
        return self.env.ref('hue_student_reports.action_student_form_attendance_report').report_action(self, data=data, config=False)


    def name_search(self, name, args=None, operator='ilike', limit=100):
        if name:
            recs = self.search(['|', ('name', operator, name), ('student_code', operator, name)] + (args or []), limit=limit)
            return recs.name_get()
        return super(opStudentsStudyTimetable, self).name_search(name, args=args, operator=operator, limit=limit)