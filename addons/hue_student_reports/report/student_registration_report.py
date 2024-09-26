# -*- coding: utf-8 -*-
import datetime
from datetime import datetime
import time
import pytz
from odoo import api, models


class StudentRegistrationReports(models.AbstractModel):
    _name = 'report.hue_student_reports.student_registration_reports'
    _description = "Student Registration Form"

    def convert_time(self, time):
        active_tz = pytz.timezone(self._context.get("tz", "Africa/Cairo") if self._context else "Africa/Cairo")
        new_timestamp =   datetime.strptime(str(time), '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.utc).astimezone(
            active_tz)

        return datetime.strftime(new_timestamp, '%m/%d/%Y %H:%M:%S')

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        student_id = self.env[model].browse(self.env.context.get('active_id'))
        curr_academic_year = self.env['op.academic.year'].sudo().search([('timetable_current', '=', True)], limit=1)
        curr_semester = self.env['op.semesters'].sudo().search([('timetable_current', '=', True)], limit=1)
        docs = {'student_id': student_id, 'report_type': 'transcript', 'language': 'ar', 'student_code_show': True,
                'title': False, 'logo': False, 'student_pic': False, 'course': True, 'level': True,
                'national_id': False, 'nationality': False, 'birthday': False, 'birth_place': False, 'address': False,
                'prev_cert': False, 'military': False, 'results': False, 'to': '', 'notes': '', 'results': True}
        # student_id = student
        # student_code = docs.student_code
        # docs = list(docs)
        # print('________________________________________________________________')
        # print(docs['title'])
        student = self.env['op.student.accumulative'].sudo().search(
            [('academicyear_id', '=', curr_academic_year.id),('course_id', '=', student_id.course_id.id),('student_id', '=', student_id.id)], limit=1)

        load_hours = self.env['op.course.loadhours'].sudo().search(
            [('gpa_to', '>', student_id.new_gpa),('gpa_from', '<=', student_id.new_gpa),('level_id.name', '=', student_id.sudo().level.d_id),('semester_id', '=', curr_semester.id), ('course_id', '=', student_id.course_id.id)], limit=1).hours_to

        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'docs': docs,
            'time': time,
            'student': student,
            'curr_academic_year': curr_academic_year,
            'curr_semester': curr_semester,
            'load_hours': load_hours,
            'convert_time': self.convert_time,
        }
        return docargs
