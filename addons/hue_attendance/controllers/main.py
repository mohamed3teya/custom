# -*- coding: utf-8 -*-
import datetime
from datetime import timedelta,datetime

from odoo import http
from odoo.http import request


class StudentAttendance(http.Controller):

    @http.route(['/attendance', '/my/attendance'], type='http', auth="user", website=True)
    def attendance(self, **kw):
        values = {}  # self._prepare_portal_layout_values()
        user_id = request.env.user
        student_id = request.env['op.student'].sudo().search([('user_id', '=', user_id.id)])

        academic_year = request.env['op.academic.year'].sudo().search([('current', '=', True)], limit=1)
        semester = request.env['op.semesters'].sudo().search([('current', '=', True)], limit=1)
    
        student_attendances = request.env['op.attendance.line'].sudo().search([('student_id', '=', student_id.id), ('permitted', '=', False), ('present', '=', False) ,
            ('batch_id.semester', '=',semester.id ), ('batch_id.academic_year', '=', academic_year.id)])
        subjects = []
        for student_attendance in student_attendances:
            subject = {}
            check = True
            for rec in subjects:
                if rec['subject'] == student_attendance.session_id.subject_id:
                    check = False
            if check:
                without_reg_day = request.env['op.student.accumlative.semesters'].sudo().search([('student_id', '=', student_id.id),('academicyear_id', '=', academic_year.id)
                        ,('semester_id', '=',semester.id)])
                subject['subject'] = student_attendance.session_id.subject_id
                sessions = self.get_registrations(student_id, student_attendance.session_id.subject_id.id)
                subject['all_count'] = sessions['sessions_count']
                leave_days = self.get_student_leaves(student_id.id)
                
                
                student_absence_count =0
                student_absence=[]
                if student_id.course_id.id != 15 :
                    if without_reg_day.create_date :
                        student_absence_count = request.env['op.attendance.line'].sudo().search_count([('attendance_date', '>', without_reg_day.create_date),('student_id', '=', student_id.id), ('permitted', '=', False), ('present', '=', False), ('session_id', 'in', sessions['session_ids']), ('attendance_date', 'not in', leave_days)])
                        student_absence = request.env['op.attendance.line'].sudo().search([('attendance_date', '>', without_reg_day.create_date),('student_id', '=', student_id.id), ('present', '=', False), ('session_id', 'in', sessions['session_ids']),
                            ('attendance_date', 'not in', leave_days)])
                else :
                    student_absence_count = request.env['op.attendance.line'].sudo().search_count([('student_id', '=', student_id.id), ('permitted', '=', False), ('present', '=', False), ('session_id', 'in', sessions['session_ids']), ('attendance_date', 'not in', leave_days)])
                    student_absence = request.env['op.attendance.line'].sudo().search([('student_id', '=', student_id.id), ('present', '=', False), ('session_id', 'in', sessions['session_ids']),
                    ('attendance_date', 'not in', leave_days)])
                subject['absence_count'] = student_absence_count
                subject['attendance_lines'] = student_absence

                subject['percentage'] = 0
                if sessions['sessions_count'] > 0:
                    subject['percentage'] = int(student_absence_count / sessions['sessions_count'] * 100)
                subjects.append(subject)

        values.update({
            'students': student_attendances,
            'subjects': subjects,
            # 'studentattendance': StuAttendanceData,
            'company': student_id.company_id,
            'academic_year': academic_year,
            'semester': semester,
            'active': 'studentattendance'
        })
        return request.render("hue_attendance.attendance", values)

    def get_registrations(self, student_id, subject_id):
        global_leaves = request.env['op.global.leaves'].sudo().search([])
        leaves_days = []
        for global_leave in global_leaves:
            num_days = datetime.strptime(global_leave.date_to,"%Y-%m-%d") - datetime.strptime(global_leave.date_from,"%Y-%m-%d")
            # print('________________________')
            # print (datetime.strptime(global_leave.date_to,"%Y-%m-%d"))
            # print (num_days.days)
            for i in range (0, num_days.days+1):
                new_date = datetime.strptime(global_leave.date_from,"%Y-%m-%d") + timedelta(days=i)
                # print(datetime.strftime(new_date,"%Y-%m-%d"))
                leaves_days.append(datetime.strftime(new_date,"%Y-%m-%d"))

        ret = {}
        sessions = request.env['op.session'].sudo().search([('student_ids', '=', student_id.id), ('subject_id', '=', subject_id)]) # , ('day_date', 'not in', leaves_days)
        ret['sessions_count'] = 0
        ret['session_ids']=[]
        AcadYearID = request.env['op.academic.year'].sudo().search([('current', '=', True)], limit=1).id
        semester_id = request.env['op.semesters'].sudo().search([('current', '=', True)], limit=1).id
        without_reg_day = request.env['op.student.accumlative.semesters'].sudo().search([('course_id', '=', student_id.course_id.id),('student_id', '=', student_id.id),('academicyear_id', '=', AcadYearID)
                        ,('semester_id', '=',semester_id)])
        if student_id.course_id.id != 15 :
            if without_reg_day :
                reg_day=datetime.strptime(without_reg_day.create_date, '%Y-%m-%d %H:%M:%S').date()
                reg_day_plus_one=  reg_day + timedelta(days=1)
                my_time = datetime.min.time()
                my_datetime = datetime.combine(reg_day_plus_one, my_time)
                print("44444444444444444444445666666666666666666666666666666666666666666666666666666666666")
                print(str(my_datetime))
                print(without_reg_day)
                print(my_time)
                print(my_datetime)
                print(without_reg_day.create_date)
                for session in sessions:
                    cnt = request.env['op.session'].sudo().search_count([('type', '=', session.type), ('subject_id', '=', session.subject_id.id), ('timing_id', '=', session.timing_id.id), ('to_timing_id', '=', session.to_timing_id.id),
                        ('classroom_id', '=', session.classroom_id.id), ('sub_classroom', '=', session.sub_classroom), ('facility_id', '=', session.facility_id.id)
                        ,('start_datetime', '>=',str(my_datetime))]) #, ('day_date', 'not in', leaves_days)
                    ret['sessions_count'] += cnt
                    sess = request.env['op.session'].sudo().search([('type', '=', session.type), ('subject_id', '=', session.subject_id.id), ('timing_id', '=', session.timing_id.id), ('to_timing_id', '=', session.to_timing_id.id), ('classroom_id', '=', session.classroom_id.id), ('sub_classroom', '=', session.sub_classroom), ('facility_id', '=', session.facility_id.id), ('day_date', 'not in', leaves_days)])
                    ret['session_ids'] += sess.ids
            else :
                ret['sessions_count'] = 0
                ret['session_ids'] = []
        else:
            for session in sessions:
                cnt = request.env['op.session'].sudo().search_count([('type', '=', session.type), ('subject_id', '=', session.subject_id.id), ('timing_id', '=', session.timing_id.id), ('to_timing_id', '=', session.to_timing_id.id),
                        ('classroom_id', '=', session.classroom_id.id), ('sub_classroom', '=', session.sub_classroom), ('facility_id', '=', session.facility_id.id)
                        ]) #, ('day_date', 'not in', leaves_days)
                ret['sessions_count'] += cnt
                sess = request.env['op.session'].sudo().search([('type', '=', session.type), ('subject_id', '=', session.subject_id.id), ('timing_id', '=', session.timing_id.id), ('to_timing_id', '=', session.to_timing_id.id), ('classroom_id', '=', session.classroom_id.id), ('sub_classroom', '=', session.sub_classroom), ('facility_id', '=', session.facility_id.id), ('day_date', 'not in', leaves_days)])
                ret['session_ids'] += sess.ids
            
        return ret

    def get_student_leaves(self, student_id):
        global_leaves = request.env['op.student.leaves'].sudo().search([('student_id','=',student_id)])
        leaves_days = []
        for global_leave in global_leaves:
            num_days = datetime.strptime(global_leave.date_to,"%Y-%m-%d") - datetime.strptime(global_leave.date_from,"%Y-%m-%d")
            # print('________________________')
            # print (datetime.strptime(global_leave.date_to,"%Y-%m-%d"))
            # print (num_days.days)
            for i in range (0, num_days.days+1):
                new_date = datetime.strptime(global_leave.date_from,"%Y-%m-%d") + timedelta(days=i)
                print(datetime.strftime(new_date,"%Y-%m-%d"))
                leaves_days.append(datetime.strftime(new_date,"%Y-%m-%d"))
        return leaves_days



