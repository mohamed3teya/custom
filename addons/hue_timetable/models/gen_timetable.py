from odoo import models, fields ,api, _
from odoo.exceptions import ValidationError
# import datetime
import warnings
import pytz
import calendar
from datetime import date, timedelta, datetime, time


class CalendarEventExt(models.Model):
    _inherit = 'calendar.event'
    
    session_id = fields.Integer()


class GenerateSession(models.TransientModel):
    _inherit = 'generate.time.table'

    start_date = fields.Date( related="batch_id.default_week_start", readonly=True)
    end_date = fields.Date(related="batch_id.default_week_end", readonly=True)


    def act_gen_time_table(self):
        # missed_session_lines = "_"
        sessions_to_create = []
        for session in self:
            print("session:----------", session)
            print("session.time_table_lines:---------", session.time_table_lines)
            #Added validation for duplicated sessions
            for t_line in session.time_table_lines:
                temp_time = t_line.timing_id.time
                duration = t_line.timing_id.duration
                temp_start_timing = t_line.timing_id
                #to keep track of table line sessions this handels session timming according to groups and sections
                while temp_time < t_line.to_timing_id.time:
                    temp_time += duration
                    temp_end_timing = self.env['op.timing'].search([('time','=',temp_time)])
                    if not temp_end_timing:
                        raise ValidationError("please update your timing duration configurations")
                    #conditions for lecture check
                    if t_line.session_type == 'Lecture':
                        line_data = (t_line.day, t_line.classroom_id, temp_start_timing, temp_end_timing)
                        if line_data in sessions_to_create:
                            raise ValidationError("you have a duplicated session at "+ str(calendar.day_name[int(t_line.day)])+
                                " for subject: "+ t_line.subject_id.name + " At timing: "+ t_line.timing_id.name)
                        #this added to check if any of the group sections have an assigned lab or section on the lecture time
                        i = 0
                        while i < 20: #20 represents max no of sections
                            if (t_line.day, t_line.classroom_id, t_line.classroom_id, temp_start_timing, temp_end_timing, (t_line.classroom_id.name+str(i))) in sessions_to_create:
                                raise ValidationError("one of this group sections have a section on this time, Please change this session on "+ str(calendar.day_name[int(t_line.day)])+
                                " for subject: "+ t_line.subject_id.name + " At timing: "+ t_line.timing_id.name)
                            i+=1 
                        sessions_to_create.append(line_data)
                        temp_start_timing = temp_end_timing   
                    #conditions for lab or section check
                    else:
                        temp_line_data = (t_line.day, t_line.classroom_id, temp_start_timing, temp_end_timing)
                        if temp_line_data in sessions_to_create:
                            raise ValidationError("students have a lecture on this date, change "+t_line.session_type+
                                              " at day: "+str(calendar.day_name[int(t_line.day)])+" time: "+t_line.timing_id.name+
                                              " For subject: "+t_line.subject_id.name)
                        else:
                            line_data = (t_line.day, t_line.classroom_id, t_line.classroom_id, temp_start_timing, temp_end_timing, (t_line.classroom_id.name+str(t_line.sub_classroom_id.name)))
                            print("(t_line.classroom_id.name+str(t_line.sub_classroom_id.name))", (t_line.classroom_id.name+str(t_line.sub_classroom_id.name)))
                            if line_data in sessions_to_create:
                                raise ValidationError("you have a duplicated "+ t_line.session_type + " session at "+ str(calendar.day_name[int(t_line.day)])+
                                    " for subject: "+ t_line.subject_id.name + " At timing: "+ t_line.timing_id.name)
                            else:
                                sessions_to_create.append(line_data)
                                temp_start_timing = temp_end_timing   
                print("sessions_to_create_final:-------------", sessions_to_create)
                #end of validation
            start_date = datetime.strptime(
                str(session.start_date), '%Y-%m-%d')
            end_date = datetime.strptime(str(session.end_date), '%Y-%m-%d')
            for n in range((end_date - start_date).days + 1):
                curr_date = start_date + timedelta(n)
                gap = 2
                for line in session.time_table_lines:
                    #Added to compute Start & End
                    midnight = datetime.combine(date.today(), time.min)
                    time_delta_start = timedelta(hours=(line.timing_id.time-gap))
                    time_delta_end = timedelta(hours=(line.to_timing_id.time-gap))
                    time_obj_start = (midnight + time_delta_start).time()
                    time_obj_end = (midnight + time_delta_end).time()
                    #end
                    if int(line.day) == curr_date.weekday():
                        hour = line.timing_id.hour
                        to_hour = line.to_timing_id.hour
                        if line.timing_id.am_pm == 'pm' and int(hour) != 12:
                            hour = int(hour) + 12
                        if line.to_timing_id.am_pm == 'pm' and int(to_hour) != 12:
                            to_hour = int(to_hour) + 12
                        per_time = '%s:%s:00' % (hour, line.timing_id.minute)
                        per_time_to = '%s:%s:00' % (to_hour, line.to_timing_id.minute)
                        
                        final_date = datetime.strptime(
                            curr_date.strftime('%Y-%m-%d ') +
                            per_time, '%Y-%m-%d %H:%M:%S')
                        final_date_to = datetime.strptime(
                            curr_date.strftime('%Y-%m-%d ') +
                            per_time_to, '%Y-%m-%d %H:%M:%S')
                        local_tz = pytz.timezone(
                            self.env.user.partner_id.tz or 'GMT')
                            
                        local_dt = local_tz.localize(final_date, is_dst=None)
                        utc_dt = local_dt.astimezone(pytz.utc)
                        utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")

                        local_dt_to = local_tz.localize(final_date_to, is_dst=None)
                        utc_dt_to = local_dt_to.astimezone(pytz.utc)
                        utc_dt_to = utc_dt_to.strftime("%Y-%m-%d %H:%M:%S")

                        curr_start_date = datetime.strptime(
                            utc_dt, "%Y-%m-%d %H:%M:%S")
                        curr_end_date = datetime.strptime(
                            utc_dt_to, "%Y-%m-%d %H:%M:%S")

                        chk_facility = self.env['op.session'].search([
                            ('type', '=', calendar.day_name[int(line.day)]),
                            ('facility_id', '=', line.facility_id.id),
                            '|', '&',
                            ('timing_id', '<=', line.timing_id.id),
                            ('to_timing_id', '>=', line.to_timing_id.id),
                            '|', '&',
                            ('timing_id', '>=', line.timing_id.id),
                            ('to_timing_id', '<=', line.to_timing_id.id),
                            '|', '&',
                            ('timing_id', '<=', line.timing_id.id),
                            ('to_timing_id', '>', line.timing_id.id),
                            '&',
                            ('timing_id', '<', line.to_timing_id.id),
                            ('to_timing_id', '>=', line.to_timing_id.id),
                        ])
                        if chk_facility and line.similarity == False:
                            raise ValidationError(
                                "Facility " + line.facility_id.name + " is busy for " + calendar.day_name[
                                    int(line.day)] + ' ' + line.timing_id.name + ' to ' + line.to_timing_id.name)
                            # missed_session_lines += "busy facilty: " + line.facility_id.name + " for subject: "+ line.subject_id.name + ' ' + calendar.day_name[int(line.day)] + ' ' + line.timing_id.name + ' to ' + line.to_timing_id.name + '_'
                        # faculty_warn = False
                        for faculty in line.faculty_ids:
                            chk_faculty = self.env['op.session'].search([
                                ('type', '=', calendar.day_name[int(line.day)]),
                                ('faculty_ids', '=', faculty.id),
                                '|', '&',
                                ('timing_id', '<=', line.timing_id.id),
                                ('to_timing_id', '>=', line.to_timing_id.id),
                                '|', '&',
                                ('timing_id', '>=', line.timing_id.id),
                                ('to_timing_id', '<=', line.to_timing_id.id),
                                '|', '&',
                                ('timing_id', '<=', line.timing_id.id),
                                ('to_timing_id', '>', line.timing_id.id),
                                '&',
                                ('timing_id', '<', line.to_timing_id.id),
                                ('to_timing_id', '>=', line.to_timing_id.id),
                            ])
                            if chk_faculty and line.similarity == False:
                                raise ValidationError(
                                    "Instructor " + faculty.name + " is busy for " + calendar.day_name[
                                        int(line.day)] + ' ' + line.timing_id.name + ' to ' + line.to_timing_id.name)

                                # missed_session_lines += "busy faculty: " + faculty.name + " for subject: "+ line.subject_id.name + ' ' + calendar.day_name[int(line.day)] + ' ' + line.timing_id.name + ' to ' + line.to_timing_id.name + '_'
                                # faculty_warn = True
                        # if faculty_warn:
                        #     continue
                        already = self.env['op.session'].search([
                            ('subject_id', '=', line.subject_id.id),
                            ('course_id', '=', session.course_id.id),
                            ('batch_id', '=', session.batch_id.id),
                            ('timing_id', '=', line.timing_id.id),
                            ('to_timing_id', '=', line.to_timing_id.id),
                            ('classroom_id', '=', line.classroom_id.id),
                            ('facility_id', '=', line.facility_id.id),
                            ('sub_classroom', '=', line.sub_classroom_id.name),
                            ('session_type', '=', line.session_type),
                            ('session_date', '=', curr_start_date.strftime("%Y-%m-%d %H:%M:%S")),
                            ('type', '=', calendar.day_name[int(line.day)]),
                            ('student_count', '=', line.student_count),
                        ])
                        if not already:
                            classroom_exist = self.env['op.classroom'].search(
                                        [('course_id', '=', session.batch_id.course_id.id),
                                         ('batch_id', '=', session.batch_id.id)])
                            if classroom_exist:
                               
                                if not line.classroom_id:
                                    classroom = self.env['op.classroom'].search(
                                        [('course_id', '=', session.batch_id.course_id.id),
                                         ('batch_id', '=', session.batch_id.id)]).ids
                                    teams = self.env['student.study.groups'].sudo().search(
                                        [('study_group_id', 'in', classroom)])
                                    student_ids = teams.mapped('student_id').ids
                                elif line.sub_classroom_id:
                                    classroom = self.env['op.classroom'].search([('id', '=', line.classroom_id.id), (
                                        'course_id', '=', session.batch_id.course_id.id),
                                        ('batch_id', '=', session.batch_id.id)],
                                                                                limit=1).id
                                    teams = self.env['student.study.groups'].sudo().search(
                                        [('study_group_id', '=', classroom),
                                         ('sub_classroom', '=', line.sub_classroom_id.name)])
                                    student_ids = teams.mapped('student_id').ids
                                else:
                                    classroom = self.env['op.classroom'].search([('id', '=', line.classroom_id.id), (
                                        'course_id', '=', session.batch_id.course_id.id),
                                        ('batch_id', '=', session.batch_id.id)],
                                                                                limit=1).id
                                    teams = self.env['student.study.groups'].sudo().search(
                                        [('study_group_id', '=', classroom)])
                                    student_ids = teams.mapped('student_id').ids
                                sess = self.env['op.session'].create({
                                    'faculty_id': line.faculty_id.id,
                                    'faculty_ids': [(6, 0, line.faculty_ids.ids)],
                                    'q_faculty_ids': [(6, 0, line.faculty_ids.ids)],
                                    'student_ids': [(6, 0, student_ids)],
                                    'subject_id': line.subject_id.id,
                                    'course_id': session.course_id.id,
                                    'batch_id': session.batch_id.id,
                                    'timing_id': line.timing_id.id,
                                    'to_timing_id': line.to_timing_id.id,
                                    'classroom_id': line.classroom_id.id,
                                    'facility_id': line.facility_id.id,
                                    'sub_classroom': 0 if line.session_type == "Lecture" else line.sub_classroom_id.name,
                                    'session_type': line.session_type,
                                    'session_date':curr_start_date.strftime("%Y-%m-%d %H:%M:%S"),
                                    #Added to compute start and end date
                                    'start_datetime': datetime.combine(curr_start_date.date(), time_obj_start),
                                    'end_datetime': datetime.combine(curr_end_date.date(), time_obj_end),
                                    #end
                                    'type': calendar.day_name[int(line.day)],
                                    'student_count': line.student_count,
                                    'similarity': line.similarity,
                                })
                                # create calendar events for generated sessions
                                partners = []
                                if line.faculty_ids:
                                    for fac in line.faculty_ids:
                                        partners.append(fac.partner_id.id)
                                self.env["calendar.event"].create({
                                    'name': line.subject_id.name.split('|')[0]+'/'+str(line.session_type),
                                    'privacy': 'public',
                                    'show_as': 'busy',
                                    'start': datetime.combine(curr_start_date.date(), time_obj_start),
                                    'stop': datetime.combine(curr_end_date.date(), time_obj_end),
                                    'location': line.facility_id.name,
                                    'partner_id': self.env.user.partner_id,
                                    'partner_ids': [(6, 0, partners)],
                                    'session_id': sess.id
                                })
                            else:
                                print("start date:-----------------", datetime.combine(curr_start_date.date(), time_obj_start))
                                sess = self.env['op.session'].create({
                                    'faculty_id': line.faculty_id.id,
                                    'faculty_ids': [(6, 0, line.faculty_ids.ids)],
                                    'q_faculty_ids': [(6, 0, line.faculty_ids.ids)],
                                    'subject_id': line.subject_id.id,
                                    'course_id': session.course_id.id,
                                    'batch_id': session.batch_id.id,
                                    'timing_id': line.timing_id.id,
                                    'to_timing_id': line.to_timing_id.id,
                                    'classroom_id': line.classroom_id.id,
                                    'facility_id': line.facility_id.id,     
                                    'sub_classroom': 0 if line.session_type == "Lecture" else line.sub_classroom_id.name,
                                    'session_type': line.session_type,
                                    'session_date':curr_start_date.strftime("%Y-%m-%d %H:%M:%S"),
                                    #Added to compute start and end date
                                    'start_datetime': datetime.combine(curr_start_date.date(), time_obj_start),
                                    'end_datetime': datetime.combine(curr_end_date.date(), time_obj_end),
                                    #end
                                    'type': calendar.day_name[int(line.day)],
                                    'student_count': line.student_count,
                                    'similarity': line.similarity,
                                })
                                # create calendar events for generated sessions
                                partners = []
                                if line.faculty_ids:
                                    for fac in line.faculty_ids:
                                        partners.append(fac.partner_id.id)
                                self.env["calendar.event"].create({
                                    'name': line.subject_id.name.split('|')[0]+'/'+str(line.session_type),
                                    'privacy': 'public',
                                    'show_as': 'busy',
                                    'start': datetime.combine(curr_start_date.date(), time_obj_start),
                                    'stop': datetime.combine(curr_end_date.date(), time_obj_end),
                                    'location': line.facility_id.name,
                                    'partner_id': self.env.user.partner_id,
                                    'partner_ids': [(6, 0, partners)],
                                    'session_id': sess.id
                                })
            # if missed_session_lines != '_':
            #     print("missed_session_lines", missed_session_lines)
            #     action = {
            #         'type': 'ir.actions.client',
            #         'tag': 'display_notification',
            #         'params': {
            #             'message': _('Those session lines not created ' + missed_session_lines),
            #             'sticky': True,
            #             'type': 'danger',# types: success, warning, danger, info
            #             'next': {'type': 'ir.actions.act_window_close'},
            #         },
            #     }
            #     return action
            calendars = self.env["calendar.event"].search([])
            print("calendars", calendars)
            return {'type': 'ir.actions.act_window_close'}


    def validate_gen_time_table(self):
        missed_session_lines = "_"
        sessions_to_create = []
        for session in self:
            print("session.time_table_lines:---------", session.time_table_lines)
            #Added validation for duplicated sessions
            for t_line in session.time_table_lines:
                temp_time = t_line.timing_id.time
                duration = t_line.timing_id.duration
                temp_start_timing = t_line.timing_id
                #to keep track of table line sessions this handels session timming according to groups and sections
                while temp_time < t_line.to_timing_id.time:
                    temp_time += duration
                    temp_end_timing = self.env['op.timing'].search([('time','=',temp_time)])
                    if not temp_end_timing:
                        raise ValidationError("please update your timing duration configurations")
                    #conditions for lecture check
                    if t_line.session_type == 'Lecture':
                        line_data = (t_line.day, t_line.classroom_id, temp_start_timing, temp_end_timing)
                        if line_data in sessions_to_create:
                            # raise ValidationError("you have a duplicated session at "+ str(calendar.day_name[int(t_line.day)])+
                            #     " for subject: "+ t_line.subject_id.name + " At timing: "+ t_line.timing_id.name)
                            msg = (" " +"you have a duplicated session at "+ str(calendar.day_name[int(t_line.day)])+ " for subject: "+ t_line.subject_id.name + " At timing: "+ t_line.timing_id.name + "\n")
                            if not msg in missed_session_lines: 
                                missed_session_lines += msg
                                print("missed_session_lines-1:------", missed_session_lines)
                        #this added to check if any of the group sections have an assigned lab or section on the lecture time
                        i = 0
                        while i < 20: #20 represents max no of sections
                            if (t_line.day, t_line.classroom_id, t_line.classroom_id, temp_start_timing, temp_end_timing, (t_line.classroom_id.name+str(i))) in sessions_to_create:
                                # raise ValidationError("one of this group sections have a section on this time, Please change this session on "+ str(calendar.day_name[int(t_line.day)])+
                                # " for subject: "+ t_line.subject_id.name + " At timing: "+ t_line.timing_id.name)
                                msg = (" "+"one of this group sections have a section on this time, Please change this session on "+ str(calendar.day_name[int(t_line.day)])+
                                " for subject: "+ t_line.subject_id.name + " At timing: "+ t_line.timing_id.name+"\n")
                                if not msg in missed_session_lines: 
                                    missed_session_lines += msg
                            i+=1 
                        print("missed_session_lines-2:------", missed_session_lines)
                        sessions_to_create.append(line_data)
                        temp_start_timing = temp_end_timing   
                    #conditions for lab or section check
                    else:
                        temp_line_data = (t_line.day, t_line.classroom_id, temp_start_timing, temp_end_timing)
                        if temp_line_data in sessions_to_create:
                            # raise ValidationError("students have a lecture on this date, change "+t_line.session_type+
                            #                   " at day: "+str(calendar.day_name[int(t_line.day)])+" time: "+t_line.timing_id.name+
                            #                   " For subject: "+t_line.subject_id.name)
                            msg = (" "+"students have a lecture on this date, change "+t_line.session_type+
                                              " at day: "+str(calendar.day_name[int(t_line.day)])+" time: "+t_line.timing_id.name+
                                              " For subject: "+t_line.subject_id.name+"\n")
                            if not msg in missed_session_lines: 
                                    missed_session_lines += msg
                        else:
                            line_data = (t_line.day, t_line.classroom_id, t_line.classroom_id, temp_start_timing, temp_end_timing, (t_line.classroom_id.name+str(t_line.sub_classroom_id.name)))
                            print("(t_line.classroom_id.name+str(t_line.sub_classroom_id.name))", (t_line.classroom_id.name+str(t_line.sub_classroom_id.name)))
                            if line_data in sessions_to_create:
                                # raise ValidationError("you have a duplicated "+ t_line.session_type + " session at "+ str(calendar.day_name[int(t_line.day)])+
                                #     " for subject: "+ t_line.subject_id.name + " At timing: "+ t_line.timing_id.name)
                                msg = (" "+"you have a duplicated "+ t_line.session_type + " session at "+ str(calendar.day_name[int(t_line.day)])+
                                    " for subject: "+ t_line.subject_id.name + " At timing: "+ t_line.timing_id.name+"\n")
                                if not msg in missed_session_lines: 
                                    missed_session_lines += msg
                            else:
                                sessions_to_create.append(line_data)
                                temp_start_timing = temp_end_timing   
                print("sessions_to_create_final:-------------", sessions_to_create)
                #end of validation
            start_date = datetime.strptime(
                str(session.start_date), '%Y-%m-%d')
            end_date = datetime.strptime(str(session.end_date), '%Y-%m-%d')
            for n in range((end_date - start_date).days + 1):
                curr_date = start_date + timedelta(n)
                gap = 2
                for line in session.time_table_lines:
                    #Added to compute Start & End
                    midnight = datetime.combine(date.today(), time.min)
                    time_delta_start = timedelta(hours=(line.timing_id.time-gap))
                    time_delta_end = timedelta(hours=(line.to_timing_id.time-gap))
                    time_obj_start = (midnight + time_delta_start).time()
                    time_obj_end = (midnight + time_delta_end).time()
                    #end
                    if int(line.day) == curr_date.weekday():
                        hour = line.timing_id.hour
                        to_hour = line.to_timing_id.hour
                        if line.timing_id.am_pm == 'pm' and int(hour) != 12:
                            hour = int(hour) + 12
                        if line.to_timing_id.am_pm == 'pm' and int(to_hour) != 12:
                            to_hour = int(to_hour) + 12
                        per_time = '%s:%s:00' % (hour, line.timing_id.minute)
                        per_time_to = '%s:%s:00' % (to_hour, line.to_timing_id.minute)
                        
                        final_date = datetime.strptime(
                            curr_date.strftime('%Y-%m-%d ') +
                            per_time, '%Y-%m-%d %H:%M:%S')
                        final_date_to = datetime.strptime(
                            curr_date.strftime('%Y-%m-%d ') +
                            per_time_to, '%Y-%m-%d %H:%M:%S')
                        local_tz = pytz.timezone(
                            self.env.user.partner_id.tz or 'GMT')
                            
                        local_dt = local_tz.localize(final_date, is_dst=None)
                        utc_dt = local_dt.astimezone(pytz.utc)
                        utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")

                        local_dt_to = local_tz.localize(final_date_to, is_dst=None)
                        utc_dt_to = local_dt_to.astimezone(pytz.utc)
                        utc_dt_to = utc_dt_to.strftime("%Y-%m-%d %H:%M:%S")

                        curr_start_date = datetime.strptime(
                            utc_dt, "%Y-%m-%d %H:%M:%S")
                        curr_end_date = datetime.strptime(
                            utc_dt_to, "%Y-%m-%d %H:%M:%S")

                        chk_facility = self.env['op.session'].search([
                            ('type', '=', calendar.day_name[int(line.day)]),
                            ('facility_id', '=', line.facility_id.id),
                            '|', '&',
                            ('start_datetime', '<=', curr_start_date.strftime("%Y-%m-%d %H:%M:%S")),
                            ('end_datetime', '>=', curr_end_date.strftime("%Y-%m-%d %H:%M:%S")),
                            '|', '&',
                            ('start_datetime', '>=', curr_start_date.strftime("%Y-%m-%d %H:%M:%S")),
                            ('end_datetime', '<=', curr_end_date.strftime("%Y-%m-%d %H:%M:%S")),
                            '|', '&',
                            ('start_datetime', '<=', curr_start_date.strftime("%Y-%m-%d %H:%M:%S")),
                            ('end_datetime', '>', curr_start_date.strftime("%Y-%m-%d %H:%M:%S")),
                            '&',
                            ('start_datetime', '<', curr_end_date.strftime("%Y-%m-%d %H:%M:%S")),
                            ('end_datetime', '>=', curr_end_date.strftime("%Y-%m-%d %H:%M:%S")),
                        ])
                        if chk_facility and line.similarity == False:
                            # raise ValidationError(
                            #     "Facility " + line.facility_id.name + " is busy for " + calendar.day_name[
                            #         int(line.day)] + ' ' + line.timing_id.name + ' to ' + line.to_timing_id.name)
                            msg = (" "+"busy facilty: " + line.facility_id.name + " for subject: "+ line.subject_id.name + ' ' + calendar.day_name[int(line.day)] + ' ' + line.timing_id.name + ' to ' + line.to_timing_id.name + '\n')
                            missed_session_lines += msg
                        faculty_warn = False
                        for faculty in line.faculty_ids:
                            chk_faculty = self.env['op.session'].search([
                                ('type', '=', calendar.day_name[int(line.day)]),
                                ('faculty_ids', '=', faculty.id),
                                '|', '&',
                                ('start_datetime', '<=', curr_start_date.strftime("%Y-%m-%d %H:%M:%S")),
                                ('end_datetime', '>=', curr_end_date.strftime("%Y-%m-%d %H:%M:%S")),
                                '|', '&',
                                ('start_datetime', '>=', curr_start_date.strftime("%Y-%m-%d %H:%M:%S")),
                                ('end_datetime', '<=', curr_end_date.strftime("%Y-%m-%d %H:%M:%S")),
                                '|', '&',
                                ('start_datetime', '<=', curr_start_date.strftime("%Y-%m-%d %H:%M:%S")),
                                ('end_datetime', '>', curr_start_date.strftime("%Y-%m-%d %H:%M:%S")),
                                '&',
                                ('start_datetime', '<', curr_end_date.strftime("%Y-%m-%d %H:%M:%S")),
                                ('end_datetime', '>=', curr_end_date.strftime("%Y-%m-%d %H:%M:%S")),
                            ])
                            if chk_faculty and line.similarity == False:
                                # raise ValidationError(
                                #     "Instructor " + faculty.name + " is busy for " + calendar.day_name[
                                #         int(line.day)] + ' ' + line.timing_id.name + ' to ' + line.to_timing_id.name)

                                msg = (" "+"busy faculty: " + faculty.name + " for subject: "+ line.subject_id.name + ' ' + calendar.day_name[int(line.day)] + ' ' + line.timing_id.name + ' to ' + line.to_timing_id.name + '\n')
                                missed_session_lines += msg
                                faculty_warn = True
                        if faculty_warn:
                            continue
                        already = self.env['op.session'].search([
                            ('subject_id', '=', line.subject_id.id),
                            ('course_id', '=', session.course_id.id),
                            ('batch_id', '=', session.batch_id.id),
                            ('timing_id', '=', line.timing_id.id),
                            ('to_timing_id', '=', line.to_timing_id.id),
                            ('classroom_id', '=', line.classroom_id.id),
                            ('facility_id', '=', line.facility_id.id),
                            ('sub_classroom', '=', line.sub_classroom_id.name),
                            ('session_type', '=', line.session_type),
                            ('session_date', '=', curr_start_date.strftime("%Y-%m-%d %H:%M:%S")),
                            ('type', '=', calendar.day_name[int(line.day)]),
                            ('student_count', '=', line.student_count),
                        ])
                        if not already:
                            classroom_exist = self.env['op.classroom'].search(
                                        [('course_id', '=', session.batch_id.course_id.id),
                                         ('batch_id', '=', session.batch_id.id)])
                            if classroom_exist:
                               
                                if not line.classroom_id:
                                    classroom = self.env['op.classroom'].search(
                                        [('course_id', '=', session.batch_id.course_id.id),
                                         ('batch_id', '=', session.batch_id.id)]).ids
                                    teams = self.env['student.study.groups'].sudo().search(
                                        [('study_group_id', 'in', classroom)])
                                    student_ids = teams.mapped('student_id').ids
                                elif line.sub_classroom_id:
                                    classroom = self.env['op.classroom'].search([('id', '=', line.classroom_id.id), (
                                        'course_id', '=', session.batch_id.course_id.id),
                                        ('batch_id', '=', session.batch_id.id)],
                                                                                limit=1).id
                                    teams = self.env['student.study.groups'].sudo().search(
                                        [('study_group_id', '=', classroom),
                                         ('sub_classroom', '=', line.sub_classroom_id.name)])
                                    student_ids = teams.mapped('student_id').ids
                                else:
                                    classroom = self.env['op.classroom'].search([('id', '=', line.classroom_id.id), (
                                        'course_id', '=', session.batch_id.course_id.id),
                                        ('batch_id', '=', session.batch_id.id)],
                                                                                limit=1).id
                                    teams = self.env['student.study.groups'].sudo().search(
                                        [('study_group_id', '=', classroom)])
                                    student_ids = teams.mapped('student_id').ids
                                self.env['op.session'].create({
                                    'faculty_id': line.faculty_id.id,
                                    'faculty_ids': [(6, 0, line.faculty_ids.ids)],
                                    'q_faculty_ids': [(6, 0, line.faculty_ids.ids)],
                                    'student_ids': [(6, 0, student_ids)],
                                    'subject_id': line.subject_id.id,
                                    'course_id': session.course_id.id,
                                    'batch_id': session.batch_id.id,
                                    'timing_id': line.timing_id.id,
                                    'to_timing_id': line.to_timing_id.id,
                                    'classroom_id': line.classroom_id.id,
                                    'facility_id': line.facility_id.id,
                                    'sub_classroom': 0 if line.session_type == "Lecture" else line.sub_classroom_id.name,
                                    'session_type': line.session_type,
                                    'session_date':curr_start_date.strftime("%Y-%m-%d %H:%M:%S"),
                                    #Added to compute start and end date
                                    'start_datetime': datetime.combine(curr_start_date.date(), time_obj_start),
                                    'end_datetime': datetime.combine(curr_end_date.date(), time_obj_end),
                                    #end
                                    'type': calendar.day_name[int(line.day)],
                                    'student_count': line.student_count,
                                    'similarity': line.similarity,
                                })
                                # create calendar events for generated sessions
                                # partners = []
                                # if line.faculty_ids:
                                #     for fac in line.faculty_ids:
                                #         partners.append(fac.partner_id.id)
                                # self.env["calendar.event"].create({
                                #     'name': line.subject_id.name.split('|')[0]+'/'+str(line.session_type),
                                #     'privacy': 'public',
                                #     'show_as': 'busy',
                                #     'start': datetime.combine(curr_start_date.date(), time_obj_start),
                                #     'stop': datetime.combine(curr_end_date.date(), time_obj_end),
                                #     'location': line.facility_id.name,
                                #     'partner_id': self.env.user.partner_id,
                                #     'partner_ids': [(6, 0, partners)],
                                # })
                            else:
                                # print("start date:-----------------", datetime.combine(curr_start_date.date(), time_obj_start))
                                self.env['op.session'].create({
                                    'faculty_id': line.faculty_id.id,
                                    'faculty_ids': [(6, 0, line.faculty_ids.ids)],
                                    'q_faculty_ids': [(6, 0, line.faculty_ids.ids)],
                                    'subject_id': line.subject_id.id,
                                    'course_id': session.course_id.id,
                                    'batch_id': session.batch_id.id,
                                    'timing_id': line.timing_id.id,
                                    'to_timing_id': line.to_timing_id.id,
                                    'classroom_id': line.classroom_id.id,
                                    'facility_id': line.facility_id.id,     
                                    'sub_classroom': 0 if line.session_type == "Lecture" else line.sub_classroom_id.name,
                                    'session_type': line.session_type,
                                    'session_date':curr_start_date.strftime("%Y-%m-%d %H:%M:%S"),
                                    #Added to compute start and end date
                                    'start_datetime': datetime.combine(curr_start_date.date(), time_obj_start),
                                    'end_datetime': datetime.combine(curr_end_date.date(), time_obj_end),
                                    #end
                                    'type': calendar.day_name[int(line.day)],
                                    'student_count': line.student_count,
                                    'similarity': line.similarity,
                                })
                                # create calendar events for generated sessions
                                # partners = []
                                # if line.faculty_ids:
                                #     for fac in line.faculty_ids:
                                #         partners.append(fac.partner_id.id)
                                # self.env["calendar.event"].create({
                                #     'name': line.subject_id.name.split('|')[0]+'/'+str(line.session_type),
                                #     'privacy': 'public',
                                #     'show_as': 'busy',
                                #     'start': datetime.combine(curr_start_date.date(), time_obj_start),
                                #     'stop': datetime.combine(curr_end_date.date(), time_obj_end),
                                #     'location': line.facility_id.name,
                                #     'partner_id': self.env.user.partner_id,
                                #     'partner_ids': [(6, 0, partners)],
                                # })
            print("yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy")
            if missed_session_lines != '_':
                print("missed_session_lines", missed_session_lines)
                raise ValidationError(missed_session_lines)
            else:
                raise ValidationError("You are all set, You can generate timetable now!")    
                # action = {
                #     'type': 'ir.actions.client',
                #     'tag': 'display_notification',
                #     'params': {
                #         'message': _('Those session lines not created ' + missed_session_lines),
                #         'sticky': True,
                #         'type': 'danger',# types: success, warning, danger, info
                #         # 'next': {'type': 'ir.actions.act_window_close'},
                #     },
                # }
                # return action
            # calendars = self.env["calendar.event"].search([])
            # print("calendars", calendars)
            # return {'type': 'ir.actions.act_window_close'}

    
    def validate_gen_time_table_red_text(self):
        missed_session_lines = "_"
        sessions_to_create = []
        facility_check_lines = []
        faculty_check_lines = []
        for session in self:
            print("session.time_table_lines:---------", session.time_table_lines)
            #Added validation for duplicated sessions
            for line in session.time_table_lines:
                temp_time = line.timing_id.time
                duration = line.timing_id.duration
                temp_start_timing = line.timing_id
                #to keep track of table line sessions this handels session timming according to groups and sections
                while temp_time < line.to_timing_id.time:
                    temp_time += duration
                    temp_end_timing = self.env['op.timing'].search([('time','=',temp_time)])
                    if not temp_end_timing:
                        raise ValidationError("please update your timing duration configurations")
                    #validations for facilty
                    facility_line = (line.day, line.facility_id, temp_start_timing, temp_end_timing)
                    if facility_line in facility_check_lines:
                        msg = (" "+"busy facilty: " + line.facility_id.name + " for subject: "+ line.subject_id.name + ' ' + calendar.day_name[int(line.day)] + ' ' + line.timing_id.name + ' to ' + line.to_timing_id.name + '\n')
                        line.write({'validation_error':True,}) 
                        if not msg in missed_session_lines: 
                                missed_session_lines += msg
                                print("missed_session_lines-3:------", missed_session_lines)
                    else:
                        facility_check_lines.append(facility_line)
                    #end
                    #validation for faculities
                    for faculty in line.faculty_ids:
                        faculty_line = (line.day, faculty, temp_start_timing, temp_end_timing)
                        if faculty_line in faculty_check_lines:
                            msg = (" "+"busy faculty: " + faculty.name + " for subject: "+ line.subject_id.name + ' ' + calendar.day_name[int(line.day)] + ' ' + line.timing_id.name + ' to ' + line.to_timing_id.name + '\n')
                            line.write({'validation_error':True,})
                            if not msg in missed_session_lines: 
                                missed_session_lines += msg
                                print("missed_session_lines-4:------", missed_session_lines)
                        else:
                            faculty_check_lines.append(faculty_line)
                    #end
                    #conditions for lecture check
                    if line.session_type == 'Lecture':
                        line_data = (line.day, line.classroom_id, temp_start_timing, temp_end_timing)
                        if line_data in sessions_to_create:
                            msg = (" " +"you have a duplicated session at "+ str(calendar.day_name[int(line.day)])+ " for subject: "+ line.subject_id.name + " At timing: "+ line.timing_id.name + "\n")
                            line.write({'validation_error':True,})
                            if not msg in missed_session_lines: 
                                missed_session_lines += msg
                                print("missed_session_lines-1:------", missed_session_lines)
                        #this added to check if any of the group sections have an assigned lab or section on the lecture time
                        i = 0
                        while i < 20: #20 represents max no of sections
                            if (line.day, line.classroom_id, line.classroom_id, temp_start_timing, temp_end_timing, (line.classroom_id.name+str(i))) in sessions_to_create:
                                msg = (" "+"one of this group sections have a section on this time, Please change this session on "+ str(calendar.day_name[int(line.day)])+
                                " for subject: "+ line.subject_id.name + " At timing: "+ line.timing_id.name+"\n")
                                line.write({'validation_error':True,})
                                if not msg in missed_session_lines: 
                                    missed_session_lines += msg
                            i+=1 
                        print("missed_session_lines-2:------", missed_session_lines)
                        sessions_to_create.append(line_data)
                        temp_start_timing = temp_end_timing   
                    #conditions for lab or section check
                    else:
                        temp_line_data = (line.day, line.classroom_id, temp_start_timing, temp_end_timing)
                        if temp_line_data in sessions_to_create:
                            msg = (" "+"students have a lecture on this date, change "+line.session_type+
                                              " at day: "+str(calendar.day_name[int(line.day)])+" time: "+line.timing_id.name+
                                              " For subject: "+line.subject_id.name+"\n")
                            line.write({'validation_error':True,})
                            if not msg in missed_session_lines: 
                                    missed_session_lines += msg
                        else:
                            line_data = (line.day, line.classroom_id, line.classroom_id, temp_start_timing, temp_end_timing, (line.classroom_id.name+str(line.sub_classroom_id.name)))
                            print("(line.classroom_id.name+str(line.sub_classroom_id.name))", (line.classroom_id.name+str(line.sub_classroom_id.name)))
                            if line_data in sessions_to_create:
                                msg = (" "+"you have a duplicated "+ line.session_type + " session at "+ str(calendar.day_name[int(line.day)])+
                                    " for subject: "+ line.subject_id.name + " At timing: "+ line.timing_id.name+"\n")
                                line.write({'validation_error':True,})
                                if not msg in missed_session_lines: 
                                    missed_session_lines += msg
                            else:
                                sessions_to_create.append(line_data)
                                temp_start_timing = temp_end_timing   
                print("sessions_to_create_final:-------------", sessions_to_create)
                #end of validation
            print("------------------------validate_gen_time_table_red_text:-----------------")
            if missed_session_lines != '_':
                #how to refresh view with the same data
                # return {
                #     'type': 'ir.actions.act_window',
                #     'res_model': 'generate.time.table',
                #     'res_id': self.id,
                #     'view_mode': 'form',
                #     'target': 'new',
                #     # Pass additional context to help trigger the notification in JS
                #     'context': {'show_notification': True, 'notification_message': "Those session lines can't be created: " + missed_session_lines},
                #     'next' : {
                        
                #     }
                # }

                action = {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': _("Those session lines can't be created: " + "\n" + missed_session_lines),
                        'sticky': True,
                        'type': 'warning',  # types: success, warning, danger, info
                    },
                }
                return action
            else:
                action = {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': _("You are all set, You can generate timetable now!"),
                        'sticky': True,
                        'type': 'success',# types: success, warning, danger, info
                    },
                }
                return action

    
class GenerateSessionLine(models.TransientModel):
    _inherit = 'gen.time.table.line'
    
    to_timing_id = fields.Many2one('op.timing', 'To Time', domain="[('id', 'in', suitable_to_timing_ids)]")
    suitable_to_timing_ids = fields.Many2many('op.timing', compute='_compute_suitable_to_timing_ids',) #to add domain to timings
    faculty_id = fields.Many2one('op.faculty', 'Faculty', required=False)
    faculty_ids = fields.Many2many('op.faculty', 'gen_faculty_rel', 'gen_id', 'faculty_id', 'Faculties', domain="[('id', 'in', suitable_faculty_ids)]")
    suitable_faculty_ids = fields.Many2many('op.faculty', compute='_compute_suitable_faculty_ids',) #to add domain to faculties
    session_type = fields.Selection([('Lecture', 'Lecture'), ('Section', 'Section'), ('Lab', 'Lab')], 'Type', required=True)
    classroom_id = fields.Many2one('op.classroom', 'Group' ,required =True, domain="[('id', 'in', suitable_classroom_ids)]")
    suitable_classroom_ids = fields.Many2many('op.classroom', compute='_compute_suitable_classroom_ids')
    sub_classroom_id = fields.Many2one('op.section', 'Sections', domain="[('id', 'in', suitable_sub_classroom_ids)]")
    suitable_sub_classroom_ids = fields.Many2many('op.section', compute='_compute_suitable_sub_classroom_ids')
    facility_id = fields.Many2one('op.facility', 'Facility', required=True, domain="[('id', 'in', suitable_facility_ids)]")
    suitable_facility_ids = fields.Many2many('op.facility', compute='_compute_suitable_faculty_ids',) #to add domain to facilities
    student_count = fields.Integer(string='Student Count', required=True)
    similarity = fields.Boolean('Similarity')
    subject_id = fields.Many2one('op.subject', 'Subject', required=True, domain="[('id', 'in', suitable_subject_ids)]")
    suitable_subject_ids = fields.Many2many('op.subject', compute='_compute_suitable_subject_ids') #to add domain to subjects
    validation_error = fields.Boolean()
    
    
    #Add domain to subjects
    @api.onchange('gen_time_table')
    def _compute_suitable_subject_ids(self):
        for m in self:
            m.suitable_subject_ids = self.env['op.subject'].search([])
            if not m.gen_time_table.course_id:
                raise ValidationError("please choose course first")
            if not m.gen_time_table.batch_id:
                raise ValidationError("please choose batch first")
            if m.gen_time_table.batch_id:
                subject_reg_ids = self.env['op.batch'].search([
                    ('id', '=', m.gen_time_table.batch_id.id)]).subject_registration_ids
                
                subject_ids = []
                for reg in subject_reg_ids:
                    subject_ids.append(reg.subject_id.id)
                m.suitable_subject_ids = subject_ids
                        

    #Add domain to classroom groups
    @api.onchange('subject_id')
    def _compute_suitable_classroom_ids(self):
        for m in self:
            print("test:------------------------------")
            parent = m.gen_time_table
            domain = None
            # m.session_type = False
            subject_ids = []
            groups_ids = []
            limit = 0
            if parent.batch_id:
                for course_subject in parent.batch_id.subject_registration_ids:  # course_subjects:
                    if course_subject.subject_id.id not in subject_ids:
                        subject_ids.append(course_subject.subject_id.id)
                    if course_subject.subject_id.id == m.subject_id.id:
                        limit = course_subject.groups_count
                        if limit == 0:
                            raise ValidationError("Groups Count in subject:"+ str(m.subject_id.name) +" should be greater than zero")
                        print("222222222222222222222222222")
                        classroom_exist = self.env['op.classroom'].search([('batch_id', '=', parent.batch_id.id)])
                        print("classroom_exist:------------", classroom_exist)
                        if classroom_exist:
                            groups = self.env['op.classroom'].search([('course_id', '=', parent.batch_id.course_id.id),
                                ('batch_id', '=', parent.batch_id.id)], limit=limit)
                        else:
                            groups = self.env['op.classroom'].search([], limit=limit)
                        print("groups:-------------", groups)
                        if groups:
                            groups_ids = groups.ids
                            print("groups_ids:--------------", groups_ids)
            m.suitable_classroom_ids = groups_ids


    
    #Add domain to sub_classroom groups
    @api.onchange('session_type', 'subject_id')
    def _compute_suitable_sub_classroom_ids(self):
        for rec in self:
            parent = rec.gen_time_table
            domain = None
            subject_ids = []
            sub_groups_ids = []
            limit = 0
            if parent.batch_id:
                for course_subject in parent.batch_id.subject_registration_ids:  # course_subjects:
                    if course_subject.subject_id.id not in subject_ids:
                        subject_ids.append(course_subject.subject_id.id)
                    if course_subject.subject_id.id == rec.subject_id.id:
                        if rec.session_type == 'Section':
                            limit = course_subject.sections_count
                        elif rec.session_type == 'Lab':
                            limit = course_subject.practical_count
                        else:
                            limit = 0
                        
                        if limit == 0:
                            rec.suitable_sub_classroom_ids = sub_groups_ids
                        else:
                            sub_groups = self.env['op.section'].search([], limit=limit)
                            if sub_groups:
                                sub_groups_ids = sub_groups.ids
            rec.suitable_sub_classroom_ids = sub_groups_ids
                
    #Add domain to timing to
    @api.onchange('timing_id')
    def _compute_suitable_to_timing_ids(self):
        for m in self:
            m.suitable_to_timing_ids = False
            parent = m.gen_time_table
            if not parent.batch_id:
                continue
            facility_ids = []
            faculities_ids = []
            crsHrs = 0
            subject_id = self.env['hue.subject.registration'].search(
                [('batch_id', '=', parent.batch_id.id), ('subject_id', '=', m.subject_id.id)], limit=1)
            if m.session_type == "Lecture":
                crsHrs = subject_id.lecture_hours
            elif m.session_type == "Section":
                crsHrs = subject_id.section_hours
            elif m.session_type == "Lab":
                crsHrs = subject_id.practical_hours
                
            session_hours = 0
            domain = []
            if m.session_type == 'Lecture':
                timing_sessions = self.env['op.session'].search([
                    # ('facility_id', '=', facility.id),
                    ('batch_id', '=', parent.batch_id.id),
                    ('session_type', '=', m.session_type),
                    ('subject_id', '=', m.subject_id.id),
                    ('classroom_id', '=', m.classroom_id.id),
                    ('start_datetime', '>=', str(parent.batch_id.default_week_start) + " 00:00:00"),
                    ('end_datetime', '<=', str(parent.batch_id.default_week_end) + " 23:59:00"),
                ])                
            else:
                timing_sessions = self.env['op.session'].search([
                    ('sub_classroom', '=', m.sub_classroom_id.name),
                    ('batch_id', '=', parent.batch_id.id),
                    ('session_type', '=', m.session_type),
                    ('subject_id', '=', m.subject_id.id),
                    ('classroom_id', '=', m.classroom_id.id),
                    ('start_datetime', '>=', str(parent.batch_id.default_week_start) + " 00:00:00"),
                    ('end_datetime', '<=', str(parent.batch_id.default_week_end) + " 23:59:00"),
                ])
            if timing_sessions:
                for timing_session in timing_sessions:
                    session_hours = session_hours + (timing_session.to_timing_id.time - timing_session.timing_id.time)
            hour = crsHrs + m.timing_id.time - session_hours
            timing = self.env['op.timing'].search([]).filtered(lambda r: r.time > m.timing_id.time and r.time <= hour)
            tt = self.env['op.timing'].search([])
            timing = timing.ids
            if timing:
                m.suitable_to_timing_ids = timing
            else:
                m.suitable_to_timing_ids = False
    
    
    #Add domain to facility and faculty ids
    @api.onchange('timing_id','to_timing_id')
    def _compute_suitable_faculty_ids(self):
        for m in self:
            m.suitable_facility_ids = False
            m.suitable_faculty_ids = False
            parent = m.gen_time_table
            college = parent.batch_id.course_id.faculty_id
            domain = None
            facility_ids = []
            faculities_ids = []
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            subject = False
            
            if m.timing_id and m.gen_time_table and m.gen_time_table.batch_id and m.subject_id:
                for course_subject in parent.batch_id.subject_registration_ids:
                    if course_subject.subject_id.id == m.subject_id.id:
                        subject = course_subject
                        break
            
            if m.timing_id and m.to_timing_id:
                facilities = self.env['op.facility'].search([])
                faculities = self.env['op.faculty'].sudo().search([])
                for facility in facilities:
                    other_sessions = self.env['op.session'].search([
                        ('facility_id', '=', facility.id),
                        ('batch_id.academic_year', '=', parent.batch_id.academic_year.id),
                        ('batch_id.semester', '=', parent.batch_id.semester.id),
                        ('type', '=', days[int(self.day)]),
                        '|', '&',
                        ('timing_id', '<=', m.timing_id.id),
                        ('to_timing_id', '>=', m.to_timing_id.id),
                        '|', '&',
                        ('timing_id', '>=', m.timing_id.id),
                        ('to_timing_id', '<=', m.to_timing_id.id),
                        '|', '&',
                        ('timing_id', '<=', m.timing_id.id),
                        ('to_timing_id', '>', m.timing_id.id),
                        '&',
                        ('timing_id', '<', m.to_timing_id.id),
                        ('to_timing_id', '>=', m.to_timing_id.id),
                    ])
                    if other_sessions:
                        print('facility.id', facility.id)
                        print("other_sessions:----------", other_sessions)
                    if not other_sessions:
                        if facility.college_only and facility.college_id.id == college.id:
                            facility_ids.append(facility.id)
                        elif not facility.college_only:
                            facility_ids.append(facility.id)

                for faculty in faculities:
                    other_sessions = self.env['op.session'].search([
                        ('faculty_ids', '=', faculty.id),
                        ('batch_id.academic_year', '=', parent.batch_id.academic_year.id),
                        ('batch_id.semester', '=', parent.batch_id.semester.id),
                        ('type', '=', days[int(m.day)]),
                        '|', '&',
                        ('timing_id', '<=', m.timing_id.id),
                        ('to_timing_id', '>=', m.to_timing_id.id),
                        '|', '&',
                        ('timing_id', '>=', m.timing_id.id),
                        ('to_timing_id', '<=', m.to_timing_id.id),
                        '|', '&',
                        ('timing_id', '<=', m.timing_id.id),
                        ('to_timing_id', '>', m.timing_id.id),
                        '&',
                        ('timing_id', '<', m.to_timing_id.id),
                        ('to_timing_id', '>=', m.to_timing_id.id),
                    ])
                    if faculty.id == 275:
                        print("faculty.id:-------", faculty.id)
                        if other_sessions:
                            print("other_sessions:-------------", other_sessions)
                    if not other_sessions:
                        faculities_ids.append(faculty.id)
            m.suitable_facility_ids = facility_ids
            m.suitable_faculty_ids = faculities_ids


    @api.onchange('facility_id')
    def onchange_facility_id(self):
        if self.facility_id:
            self.student_count = self.facility_id.study_capacity

    
    @api.onchange('session_type')
    def onchange_session_type(self):
        for m in self:
            parent = m.gen_time_table
            if not parent.batch_id:
                continue
            subject_reg_id = self.env['hue.subject.registration'].search(
                    [('batch_id', '=', parent.batch_id.id), ('subject_id', '=', m.subject_id.id)], limit=1)
            if subject_reg_id:
                choice = m.session_type
                print("choice", choice)
                if choice == 'Lecture':
                    if subject_reg_id.lecture_hours == 0:
                        raise ValidationError("lecture Hours equals zero")
                    else:
                        if subject_reg_id.groups_count == 0:
                            raise ValidationError("lecture groups equals zero")
                if choice == 'Section':
                    if subject_reg_id.section_hours ==0:
                        raise ValidationError("section Hours equals zero")
                    else:
                        if subject_reg_id.sections_count == 0:
                            raise ValidationError("section groups equals zero")
                if choice == 'Lab':
                    if subject_reg_id.practical_hours ==0:
                        raise ValidationError("Lab Hours equals zero")
                    else:
                        if subject_reg_id.practical_count == 0:
                            raise ValidationError("practical groups equals zero")
 
    
    @api.onchange('student_count')
    @api.depends('facility_id')
    def onchange_student_count(self):
        if self.facility_id:
            if self.facility_id.study_capacity < self.student_count or self.student_count <= 0:
                raise ValidationError("Valid count should be between 0 and " + str(self.facility_id.study_capacity))
  
  
class OpTimingExt(models.Model):
    _inherit = 'op.timing'
    
    time = fields.Float('Time 24')
    