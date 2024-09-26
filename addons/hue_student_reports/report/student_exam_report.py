# -*- coding: utf-8 -*-
from pytz import timezone
import time
from odoo import api, models

#  student exam report
class StudentExamReport(models.AbstractModel):
    _name = 'report.hue_student_reports.student_exam_report_template'
    _description = "Student Exam Report"


    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        domain = []

        if 'batch_id' in docs :            
            batch_id = docs.batch_id
            date= docs.date
            exam_type = docs.exam_type
            show_student =docs.show_student
            course_id = docs.course_id
            domain.append('|')
            domain.append(('course_id', '=', course_id.id))
            domain.append(('course_id', '=', course_id.parent_id.id))
            domain.append(('batch_id.semester', '=', batch_id.semester.id))
            domain.append(('batch_id.academic_year', '=', batch_id.academic_year.id))
        else:
            curr_academic_year = self.env['op.academic.year'].sudo().search([('current', '=', True)], limit=1).id
            curr_semester = self.env['op.semesters'].sudo().search([('current', '=', True)], limit=1).id
            domain.append(('batch_id.semester', '=', curr_semester))
            domain.append(('batch_id.academic_year', '=', curr_academic_year))
        if 'student_id' in docs :
            student_id = docs.student_id
            if student_id:
                domain.append(('student_id', '=', student_id.id))
        else:
            student_id = docs
            if student_id:
                domain.append(('student_id', '=', student_id.id))
                
        if 'exam_type' in docs :
            exam_type = docs.exam_type    
            if exam_type:
                domain.append(('exam_id.session_id.exam_type', '=', exam_type.id))
        else:
            if model == "op.exam":
                docs.exam_type=False        
        if 'date' in docs :
            date =docs.date
            if date:
                domain.append(('start_time', '>=', date + " 00:00:00"))
                domain.append(('start_time', '<=', date + " 23:59:00"))
        else :
            domain.append(('start_time', '>', '2022-01-01 00:00:00'))
    
        all_exams = self.env['op.exam.attendees'].sudo().search(domain ,order="start_time asc")
        exams=all_exams.mapped('exam_id')
        
        all_student = ''
        std_id = []
        if 'show_student' in docs :
            show_student =docs.show_student
            if show_student:
                all_student = self.env['op.exam.attendees'].sudo().search(
                    ['|',('course_id', '=', course_id.id),('course_id', '=', course_id.parent_id.id),('batch_id', '=', batch_id.id), ('start_time', '>', '2021-01-01 00:00:00')])
                std_id = all_student.mapped('student_id')
        else:
            if model == "op.exam":
                docs.show_student=False
            else:
                show_student = False
        print("show_student", show_student)        
        docargs = {
                'doc_ids': self.ids,
                'doc_model': model,
                'docs': docs,
                'timezone': timezone,
                'show_student': show_student,
                'exams':exams ,
                'student_id':student_id,
                'std_id':std_id,
                'all_exams':all_exams,  
                'all_student':all_student,
                'is_exam_block': self.is_exam_block,
                'get_stds': self.get_stds,
        }
        return docargs
       
    def get_stds(self,student,batch_id):
        all_student = self.env['op.exam.attendees'].sudo().search([('student_id', '=',student.id), ('batch_id', '=', batch_id.id)])
        return  all_student
    
    
    def is_exam_block(self, student, subject):
    
        StuAccID = self.env['op.session.registration.student'].sudo().search([('student_id', '=', student.id), ('subject_id', '=', subject.id)])  #
        if StuAccID.exam_block:
            return False
        else:
            return True