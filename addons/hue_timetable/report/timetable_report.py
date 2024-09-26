
import calendar
import pytz
import time
from datetime import datetime
from odoo import models, api, _, fields, tools


class TimetableReport(models.AbstractModel):
    _name = "report.hue_timetable.timetable_report_view"
    _description = "Timetable Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        curr_academic_year = self.env['op.academic.year'].sudo().search([('timetable_current', '=', True)], limit=1)
        curr_semester = self.env['op.semesters'].sudo().search([('timetable_current', '=', True)], limit=1)
        domain = []
        course_id = docs.course_id
        batch_id = ""
        domain.append('|')
        if course_id:
            domain.append(('course_id', '=', course_id.id))
            domain.append(('course_id', '=', course_id.parent_id.id))
        if 'student_id' in docs :
            student_id = docs.student_id
            if student_id:
                domain.append(('student_ids', '=', student_id.id))
        else:
            student_id = docs
            if student_id:
                domain.append(('student_ids', '=', student_id.id))
            
        if 'batch_id' in docs :   
            print("111111111111111111111111111111111")         
            batch_id = docs.batch_id
            if batch_id:
                domain.append(('batch_id.semester', '=', batch_id.semester.id))
                domain.append(('batch_id.academic_year', '=', batch_id.academic_year.id))
        else:
            print("2222222222222222222222222")
            if course_id:
                print("33333333333333333333333333333333")
                batch_id = self.env['op.batch'].sudo().search([('course_id', '=', course_id.id ) ,('academic_year', '=', curr_academic_year.id ),('semester', '=', curr_semester.id),('intern_batch', '=', False )],limit=1)
                domain.append(('batch_id.semester', '=', batch_id.semester.id))
                domain.append(('batch_id.academic_year', '=', batch_id.academic_year.id))
        if 'subject_id' in docs :
            subject_id = docs.subject_id
            if subject_id:
                domain.append(('subject_id', '=', subject_id.id))
        # else:
        #     docs.subject_id=False
 
        if 'faculty_id' in docs :
            faculty_id = docs.faculty_id
            if faculty_id:
                domain.append(('faculty_ids', '=', faculty_id.id))
        # else:
        #     docs.faculty_id=False
            
        if 'facility_id' in docs :
            facility_id = docs.facility_id
            print("facility_id", facility_id)
            if facility_id:
                domain.append(('facility_id', '=', facility_id.id))
                print("domain", domain)
        # else:
        #     docs.facility_id=False
            
        if 'actual_lectures' in docs :
            actual_lectures = docs.actual_lectures
            if actual_lectures:
                if faculty_id:
                    domain.append(('q_faculty_ids', '=', faculty_id.id))
                else:
                    domain.append(('q_faculty_ids', '!=', False))
                    
        if 'level_id' in docs :
            level_id = docs.level_id
            if level_id:
                domain.append(('subject_level', '=', level_id.id))
        # else:
        #     docs.level_id=False
        if not course_id and not batch_id:
            batchs = self.env['op.batch'].search([('semester','=',curr_semester.id)])
            if batchs:
                if len(domain) < 3:
                    domain.remove('|')
                domain.append(('batch_id', 'in', batchs.ids))
            print("batchs", batchs)
        print("domain", domain)
        sessions = self.env['op.session'].sudo().search(domain, order='start_datetime')
        print("sessions", sessions)
        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'docs': docs,
            'data': data,
            'time': time,
            'sessions':sessions
        }
        return docargs
