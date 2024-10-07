# -*- coding: utf-8 -*-
from odoo import api, models


class RegistrationByLevelReport(models.AbstractModel):
    _name = 'report.hue_register.registration_by_level_report'
    _description = "Registration By Level"

    def get_level(self,  course):
        status_ids = self.env['hue.std.data.status'].search([('active_invoice', '=', True)])._ids
        student_ids = self.env['op.student'].sudo().search(
                [('course_id', '=', course.id), ('student_status', 'in', status_ids)])
        levels = student_ids.mapped('level').ids
        levels = self.env['op.levels'].sudo().search([('id', 'in', levels)])
    
        return levels
    
    def get_std(self, level, course, batch,subject):
        status_ids = self.env['hue.std.data.status'].search([('active_invoice', '=', True)])._ids
        active_status_ids = self.env['hue.std.data.status'].search(['|',('name', '=', 'مستجد'),('name', '=', 'مستجد تقدير')])._ids
        student_count = self.env['op.student'].sudo().search_count(
            [('course_id', '=', course.id), ('level', '=', level),
             ('student_status', 'in', status_ids)])

        student_ids = self.env['op.student'].sudo().search([('course_id', '=', course.id), ('level', '=', level),
                                                            ('student_status', 'in', active_status_ids)]).ids
        if batch:
            print("111111111111111111111111111111111")
            student_registration = self.env['op.student.accumlative.semesters'].sudo().search(
                [('accum_semesters_subjects_ids', '!=',False),('course_id', '=', course.id), ('transferred', '=', False),
                 ('academicyear_id', '=', batch.academic_year.id),('semester_id', '=',batch.semester.id), 
                 ('student_id.student_status', 'in', active_status_ids),('semester_status', 'in', active_status_ids),
                 ('student_id', 'in', student_ids)]) 
            print("student_registration:--------------------", student_registration)
        else:
            print("2222222222222222222222222222222222")
            curr_academic_year = self.env['op.academic.year'].sudo().search([('timetable_current', '=', True)], limit=1).id
            curr_semester = self.env['op.semesters'].sudo().search([('timetable_current', '=', True)], limit=1).id
            student_registration = self.env['op.student.accumlative.semesters'].sudo().search(
                [('accum_semesters_subjects_ids', '!=',False),('course_id', '=', course.id), ('transferred', '=', False),
                 ('academicyear_id', '=', curr_academic_year),('semester_id', '=',curr_semester), 
                 ('student_id.student_status', 'in', active_status_ids),('semester_status', 'in', active_status_ids),
                 ('student_id', 'in', student_ids)])

        student_registration = student_registration.mapped('student_id').ids
        return [student_count - len(student_registration), len(student_registration), student_count]

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        batch = docs.batch_id
        course_id = docs.course_id
        subject_id = docs.subject_id
        if subject_id:
            if batch:
                student_registration = self.env['op.student.semesters.subjects'].sudo().search(
                    [('academicyear_id', '=', batch.academic_year.id),('semester_id', '=', batch.semester.id),
                    ('subject_id', '=', subject_id.id)])
            else:
                curr_academic_year = self.env['op.academic.year'].sudo().search([('timetable_current', '=', True)], limit=1).id
                curr_semester = self.env['op.semesters'].sudo().search([('timetable_current', '=', True)], limit=1).id
                student_registration = self.env['op.student.semesters.subjects'].sudo().search(
                    [('academicyear_id', '=', curr_academic_year),('semester_id', '=', curr_semester),
                    ('subject_id', '=', subject_id.id)])
            reg_students = student_registration.mapped('student_id').ids
            courses = self.env['op.student'].sudo().search([('id','in',reg_students)]).mapped('course_id')
        else:
            courses=  self.env['op.course'].sudo().search([])  #('id', '!=', 15)
        status_ids = self.env['hue.std.data.status'].search([('active_invoice', '=', True)])._ids
        active_status_ids = self.env['hue.std.data.status'].search(['|',('name', '=', 'مستجد'),('name', '=', 'مستجد تقدير')])._ids
        if subject_id:
            student_ids = self.env['op.student'].sudo().search(
                [('course_id', 'in', courses.ids), ('student_status', 'in', active_status_ids)])
        else:
            student_ids = self.env['op.student'].sudo().search(
                [('course_id', '=', course_id.id), ('student_status', 'in', active_status_ids)])
        levels =[]
        students =[]
        reg_students =[]
        missing_std = [] 
        if docs.course_id :
            if docs.show_missing:
                for std in student_ids:
                    missing =  []
                    missing.append(std)
                    missing_sessions = []
                    if batch:
                        student_registration = self.env['hue.student.registration'].sudo().search(
                        [('course_id', '=', course_id.id), ('batch_id', '=', batch.id), ('student_id', '=', std.id),
                         ('status', '=', 'Approved')])
                    else:
                        curr_academic_year = self.env['op.academic.year'].sudo().search([('timetable_current', '=', True)], limit=1).id
                        curr_semester = self.env['op.semesters'].sudo().search([('timetable_current', '=', True)], limit=1).id
                        student_registration = self.env['hue.student.registration'].sudo().search(
                            [('course_id', '=', course_id.id),('batch_id.academic_year', '=', curr_academic_year),('batch_id.semester', '=', curr_semester), ('student_id', '=', std.id),
                             ('status', '=', 'Approved')])
                    for reg in student_registration:
                        if reg.session_id.id not in  std.session_ids.ids:
                            missing_sessions.append(reg.session_id)
                    missing.append(missing_sessions)
                    missing_std.append(missing)
            else:
                levels = student_ids.mapped('level').ids
                levels = self.env['op.levels'].sudo().search([('id', 'in', levels)])
    
                students = []
    
                if subject_id:
                    curr_academic_year = self.env['op.academic.year'].sudo().search([('timetable_current', '=', True)], limit=1).id
                    curr_semester = self.env['op.semesters'].sudo().search([('timetable_current', '=', True)], limit=1).id
                    student_registration = self.env['op.student.semesters.subjects'].sudo().search(
                    [('academicyear_id', '=', curr_academic_year),('semester_id', '=', curr_semester)
                        , ('subject_id', '=', subject_id.id)]) 
                else:
                    if batch:
                        student_registration = self.env['op.student.accumlative.semesters'].sudo().search(
                            [('accum_semesters_subjects_ids', '!=',False),('course_id', '=', course_id.id), ('transferred', '=', False),
                             ('academicyear_id', '=', batch.academic_year.id),('semester_id', '=',batch.semester.id), 
                             ('student_id.student_status', 'in', active_status_ids),('semester_status', 'in', active_status_ids),
                             ('student_id', 'in', student_ids.ids)])
                    else:
                        curr_academic_year = self.env['op.academic.year'].sudo().search([('timetable_current', '=', True)], limit=1).id
                        curr_semester = self.env['op.semesters'].sudo().search([('timetable_current', '=', True)], limit=1).id
                        student_registration = self.env['op.student.accumlative.semesters'].sudo().search(
                            [('accum_semesters_subjects_ids', '!=',False),('course_id', '=', course_id.id), ('transferred', '=', False),
                             ('academicyear_id', '=', curr_academic_year),('semester_id', '=',curr_semester), 
                             ('student_id.student_status', 'in', active_status_ids),('semester_status', 'in', active_status_ids),
                             ('student_id', 'in', student_ids.ids)])
                        
                student_registration = student_registration.mapped('student_id').ids
                if subject_id:
                    students = self.env['op.student'].sudo().search([('course_id', 'in', courses.ids), ('student_status', 'in', status_ids), ('id', 'not in', student_registration)], order="level")
                    reg_students = self.env['op.student'].sudo().search([('course_id', 'in', courses.ids), ('student_status', 'in', active_status_ids), ('id', 'in', student_registration)], order="level")
                else:
                    students = self.env['op.student'].sudo().search([('course_id', '=', course_id.id), ('student_status', 'in', status_ids), ('id', 'not in', student_registration)], order="level")
                    reg_students = self.env['op.student'].sudo().search([('course_id', '=', course_id.id), ('student_status', 'in', active_status_ids), ('id', 'in', student_registration)], order="level")
       
            
    
        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'docs': docs,
            'levels': levels,
            'students': students,
            'reg_students': reg_students,
            'get_std': self.get_std,
            'get_level':self.get_level ,
            'courses':courses ,
            'missing_std': missing_std,
        }
        return docargs
