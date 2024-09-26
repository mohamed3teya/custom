# -*- coding: utf-8 -*-
import datetime
from datetime import date, timedelta,datetime
import time
from odoo import api, models



class StudentAttendanceReport(models.AbstractModel):
    _name = 'report.hue_student_reports.student_attendance_report'
    _description = "Student Attendance Report"
    

    
    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        student_code = docs
        report = False
        if 'student_id' in docs :
            student_id = docs.student_id
            course_id =docs.student_id.course_id
            report = True
        else:
            student_id = docs
            course_id =student_id.course_id
            report = False

        if 'batch_id' in docs :            
            batch_id = docs.batch_id
        else:
            curr_academic_year = self.env['op.academic.year'].sudo().search([('current', '=', True)], limit=1).id
            curr_semester = self.env['op.semesters'].sudo().search([('current', '=', True)], limit=1).id
            batch_id = self.env['op.batch'].sudo().search([('course_id', '=', course_id.id ) ,('academic_year', '=', curr_academic_year ),('semester', '=', curr_semester ),('intern_batch', '=', False )],limit=1)

        # sessions = self.env['op.session'].sudo().search([('student_id', '=', student_id.id)])

        # all_sessions = self.env['op.attendance.line'].sudo().search([('student_id', '=', student_id.id)])
        student_attendances =[]
        AcadYearID = self.env['op.academic.year'].sudo().search([('current', '=', True)], limit=1).id
        semester_id = self.env['op.semesters'].sudo().search([('current', '=', True)], limit=1).id
        parent_batch = self.env['op.batch'].sudo().search(['|',('course_id', '=', course_id.id),('course_id', '=', course_id.parent_id.id)])

        student_attendances = self.env['op.attendance.line'].sudo().search([('student_id', '=', student_id.id), ('permitted', '=', False), ('present', '=', False),
                 ('batch_id.semester', '=', batch_id.semester.id),('batch_id.academic_year', '=', batch_id.academic_year.id)]) #('batch_id', 'in', parent_batch.ids)
        subjects = []
        for student_attendance in student_attendances:
            subject = {}
            check = True
            for rec in subjects:
                if rec['subject'] == student_attendance.session_id.subject_id:
                    check = False
            if check:
                without_reg_day = self.env['op.student.accumlative.semesters'].sudo().search([('student_id', '=', student_id.id),('academicyear_id', '=', batch_id.academic_year.ids)
                        ,('semester_id', '=', batch_id.semester.ids)])
                print(student_attendance.session_id)
                subject['subject'] = student_attendance.session_id.subject_id
                sessions = self.get_registrations(student_id, student_attendance.session_id.subject_id.id,parent_batch ,batch_id)
                subject['all_count'] = sessions['sessions_count']
                leave_days = self.get_student_leaves(student_id.id)
                student_absence_count =0
                student_absence=[]
                if student_id.course_id.id != 15 :
                    if without_reg_day.create_date :
                        student_absence_count = self.env['op.attendance.line'].sudo().search_count([('attendance_date', '>', without_reg_day.create_date),('student_id', '=', student_id.id), ('permitted', '=', False), ('present', '=', False),
                            ('session_id', 'in', sessions['session_ids']), ('attendance_date', 'not in', leave_days)])              
                        student_absence = self.env['op.attendance.line'].sudo().search([('attendance_date', '>', without_reg_day.create_date),('student_id', '=', student_id.id), ('present', '=', False), ('session_id', 'in', sessions['session_ids'])])
                else :
                    student_absence_count = self.env['op.attendance.line'].sudo().search_count([('student_id', '=', student_id.id), ('permitted', '=', False), ('present', '=', False),
                    ('session_id', 'in', sessions['session_ids']), ('attendance_date', 'not in', leave_days)])              
                    student_absence = self.env['op.attendance.line'].sudo().search([('student_id', '=', student_id.id), ('present', '=', False), ('session_id', 'in', sessions['session_ids'])])

                subject['absence_count'] = student_absence_count
                subject['attendance_lines'] = student_absence

                subject['percentage'] = 0
                if sessions['sessions_count'] > 0:
                    subject['percentage'] = int(student_absence_count / sessions['sessions_count'] * 100)
                subjects.append(subject)
                    

        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'docs': docs,
            'students' : student_attendances,
            'subjects' : subjects,
            'report' :report
        }
        return docargs

    def get_registrations(self, student_id, subject_id, batch_id=None ,batch=None):
        if student_id.religion == 'مسيحى' :
            global_leaves = self.env['op.global.leaves'].sudo().search([])
        else:
            global_leaves = self.env['op.global.leaves'].sudo().search([('christianity', '=', False)])
        leaves_days = []
        AcadYearID = self.env['op.academic.year'].sudo().search([('current', '=', True)], limit=1).id
        semester_id = self.env['op.semesters'].sudo().search([('current', '=', True)], limit=1).id
        for global_leave in global_leaves:
            num_days = datetime.strptime(str(global_leave.date_to),"%Y-%m-%d") - datetime.strptime(str(global_leave.date_from),"%Y-%m-%d")
            for i in range (0, num_days.days+1):
                new_date = datetime.strptime(str(global_leave.date_from),"%Y-%m-%d") + timedelta(days=i)
                leaves_days.append(datetime.strftime(str(new_date),"%Y-%m-%d"))

        ret = {}
        sessions = self.env['op.session'].sudo().search([('subject_id', '=', subject_id), ('batch_id', 'in', batch_id.ids), ('student_ids', '=', student_id.id)
          , '|', ('course_id', '=', student_id.course_id.id), ('course_id', '=', student_id.course_id.parent_id.id) ]) # , ('day_date', 'not in', leaves_days)
         # ('start_datetime', '>=', batch_id.start_date), ('end_datetime', '<=', batch_id.end_date + ' 23:59:59')
        ret['sessions_count'] = 0
        ret['session_ids']=[]
        without_reg_day = self.env['op.student.accumlative.semesters'].sudo().search([('course_id', '=', student_id.course_id.id),('student_id', '=', student_id.id),('academicyear_id', '=', batch.academic_year.id)
                        ,('semester_id', '=',semester_id)])
        if student_id.course_id.id != 15 :
            if without_reg_day :
                reg_day=datetime.strptime(str(without_reg_day.create_date), '%Y-%m-%d %H:%M:%S').date()
                reg_day_plus_one=  reg_day + timedelta(days=1)
                my_time = datetime.min.time()
                my_datetime = datetime.combine(reg_day_plus_one, my_time)
                for session in sessions:
                    cnt = self.env['op.session'].sudo().search_count([('type', '=', session.type), ('subject_id', '=', session.subject_id.id), ('timing_id', '=', session.timing_id.id),
                        ('to_timing_id', '=', session.to_timing_id.id), ('classroom_id', '=', session.classroom_id.id), ('sub_classroom', '=', session.sub_classroom), ('facility_id', '=', session.facility_id.id)
                        ,('start_datetime', '>=',str(my_datetime))
                        , '|', ('course_id', '=', student_id.course_id.id), ('course_id', '=', student_id.course_id.parent_id.id)])  #, ('day_date', 'not in', leaves_days)
                    ret['sessions_count'] += cnt
                    sess = self.env['op.session'].sudo().search([('type', '=', session.type), ('subject_id', '=', session.subject_id.id), ('timing_id', '=', session.timing_id.id),
                        ('to_timing_id', '=', session.to_timing_id.id), ('classroom_id', '=', session.classroom_id.id), ('sub_classroom', '=', session.sub_classroom), ('facility_id', '=', session.facility_id.id), ('day_date', 'not in', leaves_days)])
                    ret['session_ids'] += sess.ids
            else :
                ret['sessions_count'] = 0
                ret['session_ids'] = []
        else:
            for session in sessions:
                # cnt = self.env['op.session'].sudo().search_count([('type', '=', session.type), ('subject_id', '=', session.subject_id.id), ('timing_id', '=', session.timing_id.id),
                #     ('to_timing_id', '=', session.to_timing_id.id), ('classroom_id', '=', session.classroom_id.id), ('sub_classroom', '=', session.sub_classroom), ('facility_id', '=', session.facility_id.id)
                #    ,('course_id', '=', student_id.course_id.id) ,
                #     ('batch_id.semester', '=', batch.semester.id),('batch_id.academic_year', '=', batch.academic_year.id)])  #, ('day_date', 'not in', leaves_days)
                # ret['sessions_count'] += cnt
                sess = self.env['op.session'].sudo().search([('type', '=', session.type), ('subject_id', '=', session.subject_id.id), ('timing_id', '=', session.timing_id.id),
                    ('to_timing_id', '=', session.to_timing_id.id), ('classroom_id', '=', session.classroom_id.id), ('sub_classroom', '=', session.sub_classroom), ('facility_id', '=', session.facility_id.id), ('day_date', 'not in', leaves_days)])
                ret['session_ids'] += sess.ids
            ret['sessions_count'] = len(sessions)

        return ret

    def get_student_leaves(self, student_id):
        global_leaves = self.env['op.student.leaves'].sudo().search([('student_id','=',student_id)])
        leaves_days = []
        for global_leave in global_leaves:
            num_days = datetime.strptime(str(global_leave.date_to),"%Y-%m-%d") - datetime.strptime(str(global_leave.date_from),"%Y-%m-%d")
            print('________________________')
            print (datetime.strptime(str(global_leave.date_to),"%Y-%m-%d"))
            print (num_days.days)
            for i in range (0, num_days.days+1):
                new_date = datetime.strptime(str(global_leave.date_from),"%Y-%m-%d") + timedelta(days=i)
                print(datetime.strftime(str(new_date),"%Y-%m-%d"))
                leaves_days.append(datetime.strftime(str(new_date),"%Y-%m-%d"))
        return leaves_days

