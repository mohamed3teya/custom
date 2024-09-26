# -*- coding: utf-8 -*-
import datetime
from datetime import date, timedelta,datetime
import time
from dateutil.relativedelta import relativedelta
from odoo import api, models
from dateutil.parser import parse
from odoo.exceptions import UserError


class StudentTranscriptReport(models.AbstractModel):
    _name = 'report.hue_student_reports.report_transcript'
    _description = "Student Transcript Report"

    def is_published(self, courseid,acadyear,semester):
        published = self.env['op.course.resultspublish'].sudo().search([('course_id', '=', courseid),('acadyears', '=', acadyear),('semesters', '=', semester)]).publishflag
        print("published:---------", published)
        if published:
            if published=='publish':
                return True
        return False

    def get_gpa_ch(self,student_id):
        curr_academic_year = self.env['op.semesters'].sudo().search([('enroll_semester', '=', True)], limit=1).term_id.term_id
        academic_years = self.env['op.academic.year'].sudo().search([('sequence', '!=', 0)], order='sequence asc')
        semesters = self.env['op.semesters'].sudo().search([], order='sequence asc')
        AcadYearID = self.env['op.academic.year'].sudo().search([('run_semester_gpa', '=', True)], limit=1).id
        semester_id = self.env['op.semesters'].sudo().search([('run_semester_gpa', '=', True)], limit=1).id
        # semester_id = self.env['op.semesters'].sudo().search([('id', '=', 2)], limit=1).id
        invoice_count = 0
        if not student_id.allow_registration:
            # ('date_due', '<=', '2023-01-31'),
            domain = [
                ('move_type', 'in', ['out_invoice']),
                ('invoice_date_due', '<=',curr_academic_year.invoice_date),
                ('partner_id', '=', student_id.partner_id.id),
                ('state', 'in', ['draft'])
            ]
            invoice_count = self.env['account.move'].sudo().search_count(domain)
        qdone = student_id.questionnaire_done()
        totalhours = 0
        totalgpa = 0
        for academic_year in academic_years:
            print("############################################")
            print(academic_year.name)
            for semester in semesters:
                print("############################################")
                print(semester.name)
                accum_semesters = self.env['op.student.accumlative.semesters'].sudo().search(
                    [('student_id', '=', student_id.id), ('academicyear_id', '=', academic_year.id),
                     ('semester_id', '=', semester.id),
                     ('transferred', '=', False)])
                for item in accum_semesters:
                    if self.is_published(item.course_id.id, item.academicyear_id.id,
                                         item.semester_id.id):

                        if item.academicyear_id.id == AcadYearID and item.semester_id.id == semester_id:
                            print(item.current_gpa)
                            if qdone and invoice_count == 0 and not item.block_result:
                                totalhours += item.semester_hr
                                totalgpa = item.current_gpa
                        else:
                            totalhours += item.semester_hr
                            totalgpa = item.current_gpa

        return [totalgpa, totalhours]


    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        student_id = docs.student_id
        student_code = docs.student_id.student_code

        accum_semesters = self.env['op.student.accumlative.semesters'].sudo().search(
            [('student_id', '=', student_id.id),('semester_gpa', '!=', False),
             ('transferred', '=', False),('accum_semesters_subjects_ids', '!=', False)],order="id desc",limit=1)
        AcadYearID = accum_semesters.academicyear_id.id
        semester_id = accum_semesters.semester_id.id
        # AcadYearID = self.env['hue.academic.years'].sudo().search([('run_semester_gpa', '=', True)], limit=1).id
        # semester_id = self.env['op.semesters'].sudo().search([('run_semester_gpa', '=', True)], limit=1).id
        # semester_id = self.env['op.semesters'].sudo().search([('id', '=', 2)], limit=1).id
        
        company_details =self.env['res.company'].sudo().search([('id' ,'=' ,1)])


        # student = self.env['op.student.accumulative'].sudo().search([('accum_semesters_ids.transferred', '=', False),('student_id', '=', student_id.id)
        #     ,'|',('course_id', '=', student_id.course_id.id),('course_id', '=', student_id.course_id.parent_id.id)],order = 'academicyear_id desc')
        student = []
        curr_academic_year = self.env['op.semesters'].sudo().search([('enroll_semester', '=', True)], limit=1).term_id.academic_year_id
        academicyear = self.env['op.academic.year'].sudo().search([('sequence', '!=', 0)],order = 'sequence asc')
        semesters = self.env['op.semesters'].sudo().search([],order = 'sequence asc')
        for year in academicyear :
            for semester in semesters :
                if docs.transferred :
                    batchs_student = self.env['op.student.accumlative.semesters'].sudo().search([('student_id', '=', student_id.id),('academicyear_id', '=', year.id),
                    ('semester_id', '=', semester.id)], order="id desc") #,('accum_semesters_subjects_ids', '!=', False)('transferred', '=', False), ,'|',('course_id', '=', student_id.course_id.id),('course_id', '=', student_id.course_id.parent_id.id)
                
                else:
                    batchs_student = self.env['op.student.accumlative.semesters'].sudo().search([('student_id', '=', student_id.id),('academicyear_id', '=', year.id),
                    ('semester_id', '=', semester.id)], order="id desc", limit=1) #,('accum_semesters_subjects_ids', '!=', False)('transferred', '=', False), ,'|',('course_id', '=', student_id.course_id.id),('course_id', '=', student_id.course_id.parent_id.id)
                    
                if batchs_student :
                    for batch_student in batchs_student :
                        student.append(batch_student)
        student.sort(key=lambda r: r.transferred , reverse=True)
                
        invoice_count = 0
        if not student_id.allow_registration:
            domain = [
                ('move_type', 'in', ['out_invoice']),
                # ('date_due', '<=', date.today()),
                # ('date_due', '<=', '2023-09-19'),
                ('invoice_date_due', '<=',curr_academic_year.invoice_date),
                ('partner_id', '=', [student_id.partner_id.id]),
                ('state', 'in', ['draft'])
            ]
            invoice_count = self.env['account.move'].sudo().search_count(domain)

        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'docs': docs,
            'time': time,
            'student' : student,
            'is_published' : self.is_published,
            'AcadYearID' : AcadYearID,
            'semester_id' : semester_id,
            'invoice_count' : invoice_count,
            'curr_academic_year':curr_academic_year,
            'get_gpa_ch' : self.get_gpa_ch,
            'get_semester':self.get_semester ,
            'company_details' :company_details ,
            'get_course_grade' :self.get_course_grade ,
            'get_course_grade_eqiv': self.get_course_grade_eqiv ,
            'get_course_grade_eqiv_point':self.get_course_grade_eqiv_point ,
            'get_grades_eqiv' :self.get_grades_eqiv,
            'chk_summer':self.chk_summer,
            'get_med_above_semester_six':self.get_med_above_semester_six

        }
        return docargs
    
    def get_semester(self,student_id):
        semesters=  self.env['op.student.accumlative.semesters'].sudo().search([('student_id', '=', student_id.id)])                                                  
        return semesters
    
    def get_med_above_semester_six(self,subject_id):
        subj_above_semester_six = self.env['op.course.subjects'].sudo().search(
            [('id', '=', subject_id.id),('subject_level.level_id.d_id', '>=', 6)])
        if subj_above_semester_six :
            return True
        else :
            return False
        
        semesters=  self.env['op.student.accumlative.semesters'].sudo().search([('student_id', '=', student_id.id)])                                                  
        return semesters
    
    def get_course_grade(self,course_id):
        grades=  self.env['op.course.grades'].sudo().search([('grade_id.pass_grade', '=', True),
            ('course_id', '=', course_id.id), ('points_from', '!=', 0)]).sorted(key=lambda r: r.grade_id.sequence )                                               
        return grades
    
    def get_course_grade_eqiv(self,course_id):
        grades=  self.env['op.course.grades'].sudo().search([('grade_id.pass_grade', '=', True),
            ('course_id', '=', course_id.id)])
        grades_eqivalent = grades.mapped('grade_Eqiv')
        return grades_eqivalent
    
    def get_course_grade_eqiv_point(self,course_id,grade_Eqiv):
        grade_Eqiv_point=  self.env['op.course.grades'].sudo().search([('grade_id.pass_grade', '=', True),
            ('course_id', '=', course_id.id),('grade_Eqiv', '=', grade_Eqiv.id)],limit=1 ,order='id desc')
        return grade_Eqiv_point
    
    def get_grades_eqiv(self,course_id):
        grades_eqiv=  self.env['op.course.gradeseqiv'].sudo().search([('course_id', '=', course_id.id)])                                                  
        return grades_eqiv
    
    def chk_summer(self, subject_id,student_id):
        student_subjects = self.env['op.student.semesters.subjects'].sudo().search([('student_id', '=', student_id.id)
                    , ('subject_id', '=', subject_id),('academicyear_id' , '=' , 69533), ('semester_id', '=', 3)])
        if student_subjects:
            if student_subjects.final_grade.pass_grade == False :
                return True
            else:
                return False
        else:
            return False