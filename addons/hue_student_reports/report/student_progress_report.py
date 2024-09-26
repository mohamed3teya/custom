# -*- coding: utf-8 -*-
import time
from odoo import api, models


class StudentProgressReport2(models.AbstractModel):
    _name = 'report.hue_student_reports.student_progress_report_stu'
    _description = "Student Progress Report"

    def is_published(self, courseid,acadyear,semester):
         published = self.env['op.course.resultspublish'].sudo().search([('course_id', '=', courseid),('acadyears', '=', acadyear),('semesters', '=', semester)]).publishflag
         if published:
             if published == 'publish':
                 return True
         return False

    @api.model
    def _get_report_values(self, docids, data=None):
        print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        model = self.env.context.get('active_model')
        doc_id = self.env[model].browse(self.env.context.get('active_id'))

        try:
            student_id = doc_id.student_id
        except:
            student_id = doc_id
        try:
            language = doc_id.language
        except:
            language = 'ar'
        print("language:----------", language)
        #self.env['op.student'].sudo().getstuEdu_data(student_id.student_code)

        course_id = self.env['op.student.accumulative'].sudo().search([('student_id', '=', student_id.id)],
                                                                      order="id DESC", limit=1).course_id
        course_arr = course_id.ids
        if course_id.parent_id:
            course_arr.append(course_id.parent_id.id)
        print('________________________')
        print('________________________')
        print('________________________')
        print('________________________')

        print(course_id.write_date)

        course_id2 = self.env['op.student.accumulative'].sudo().search(
            [('student_id', '=', student_id.id), ('write_date', '<', '2020-12-23 00:00:00')], order="id DESC")
        if course_id2:
            print('________________________')
            # self.env['op.student'].sudo().getstuEdu_data(student_id.student_code)

        course_subjects = self.env['op.subject'].sudo().search([('course_id', 'in', course_arr),('intern_subject', '=', False)],
                                                                       order="subject_level ASC , subject_semester ASC ")
        
        # , subject_semester ASC
        docs = {'student_id': student_id, 'report_type': 'transcript', 'language': language, 'student_code_show': True,
                'title': False, 'logo': False, 'student_pic': False, 'course': True, 'level': True,'new_crh':True,'cgpa':True,
                'national_id': False, 'nationality': False, 'birthday': False, 'birth_place': False, 'address': False,
                'prev_cert': False, 'military': False, 'results': False, 'to': '', 'notes': '', 'results': True}

        student = self.env['op.student.accumulative'].sudo().search([('student_id', '=', student_id.id)])
        curr_academic_year = self.env['op.semesters'].sudo().search([('enroll_semester', '=', True)], limit=1).term_id.academic_year_id

          # ('date_due', '<=', '2023-01-31'),
        domain = [
            ('move_type', 'in', ['out_invoice']),
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
            'student': student,
            'student_id': student_id,
            'course_subjects': course_subjects,
            'get_subject_data': self.get_subject_data,
            'get_adviser': self.get_adviser,
            'get_grade':self.get_grade,
            'get_semesters_count':self.get_semesters_count,
            'get_semesters_count_no_summer':self.get_semesters_count_no_summer,
            'get_gpa_ch' : self.get_gpa_ch,
            'invoice_count': invoice_count
        }
        return docargs
    # adviser
    def get_adviser(self, student):
        adviser_name = self.env['hue.academic.direction.line'].sudo().search(
            [('student_id', '=', student.id), ('to_date', '=', False)])

        return adviser_name
    # grade
    def get_grade(self, student,course_subject):
        curr_academic_year = self.env['op.semesters'].sudo().search([('enroll_semester', '=', True)], limit=1).term_id.academic_year_id
        grade = self.env['op.student.semesters.subjects'].sudo().search(
            [('student_id', '=', student.id),('subject_id', '=', course_subject.id),('final_grade','!=', False)])
        allgrd=''
        
        # ('date_due', '<=', '2023-01-31'),
        domain = [
                ('move_type', 'in', ['out_invoice']),
                ('partner_id', '=', student.partner_id.id),
                ('invoice_date_due', '<=',curr_academic_year.invoice_date),
                ('state', 'in', ['draft'])
            ]
        invoice_count = self.env['account.move'].sudo().search_count(domain)
        AcadYearID = self.env['op.academic.year'].sudo().search([('run_semester_gpa', '=', True)], limit=1).id
        semester_id = self.env['op.semesters'].sudo().search([('run_semester_gpa', '=', True)], limit=1).id
        for grd in grade:
            if not grd.student_semester_id.transferred:
                if self.is_published(grd.course_id.id, grd.academicyear_id.id,grd.semester_id.id)  :
                    if grd :
                            if grd.academicyear_id.id == AcadYearID and grd.semester_id.id == semester_id:
                                if invoice_count == 0 and   not grd.student_semester_id.block_result and  student.questionnaire_done():
                                    allgrd += str(grd.final_grade.name.split('|')[1])+' , '
                            else:
                                allgrd += str(grd.final_grade.name.split('|')[1])+' , '
        return allgrd
 # semster count
    def get_semesters_count(self, course_id, student):
           semester_count = self.env['op.student.accumlative.semesters'].sudo().search(
               [('course_id', '=', course_id.id), ('student_id', '=', student.id), ('transferred', '!=', True)])
           return len(semester_count)

    def get_semesters_count_no_summer(self, course_id, student):
        semester_count = self.env['op.student.accumlative.semesters'].sudo().search(
            [('course_id', '=', course_id.id), ('student_id', '=', student.id), ('semester_id', '!=', 3), ('transferred', '!=', True)])
        return len(semester_count)

    def get_gpa_ch(self,student_id):
        curr_academic_year = self.env['op.semesters'].sudo().search([('enroll_semester', '=', True)], limit=1).term_id.academic_year_id
        academic_years = self.env['op.academic.year'].sudo().search([('sequence', '!=', 0)], order='sequence asc')
        semesters = self.env['op.semesters'].sudo().search([], order='sequence asc')
        AcadYearID = self.env['op.academic.year'].sudo().search([('run_semester_gpa', '=', True)], limit=1).id
        semester_id = self.env['op.semesters'].sudo().search([('run_semester_gpa', '=', True)], limit=1).id
        curr_academic_year = self.env['op.semesters'].sudo().search([('enroll_semester', '=', True)], limit=1).term_id.academic_year_id
        # semester_id = self.env['op.semesters'].sudo().search([('id', '=', 1)], limit=1).id
        # ('date_due', '<=', date.today()),
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


    def get_subject_data(self, course_id, student_id, subject_id, course_subject):
        curr_academic_year = self.env['op.semesters'].sudo().search([('enroll_semester', '=', True)], limit=1).term_id.academic_year_id
        accumulative_ids = self.env['op.student.accumulative'].sudo().search(
            [('student_id', '=', student_id)])

        stuid = self.env['op.student'].sudo().search([('id', '=', student_id)])
        # ('date_due', '<=', '2023-01-31'),
        domain = [
            ('move_type', 'in', ['out_invoice']),
            ('invoice_date_due', '<=',curr_academic_year.invoice_date),
            ('partner_id', 'in', [stuid.partner_id.id]),
            ('state', 'in', ['draft'])
        ]
        invoice_count = self.env['account.move'].sudo().search_count(domain)

        AcadYearID = self.env['op.academic.year'].sudo().search([('run_semester_gpa', '=', True)], limit=1).id
        #semester_id = self.env['op.semesters'].sudo().search([('current', '=', True)], limit=1).id
        semester_id = self.env['op.semesters'].sudo().search([('run_semester_gpa', '=', True)], limit=1).id

        arr = []
        for acc in accumulative_ids:
            for sem in acc.accum_semesters_ids:
                if not sem.transferred:
                    if self.is_published(course_id, sem.academicyear_id.id,sem.semester_id.id) :
                        for sub in sem.accum_semesters_subjects_ids:
                            if course_subject.subject_passpercentage:
                                degree = int(course_subject.subject_passpercentage)
                            else:
                                degree = 60
                            if sub.subject_id.id == subject_id:
                                if sub.final_grade.pass_grade or sub.final_grade.name == 'P|P' or sub.final_grade.name == 'P' or sub.final_grade.name == 'PC|PC' or sub.final_grade.name == 'PC' or sub.semester_id.id == 4:
                                    if sem.academicyear_id.id == AcadYearID and sem.semester_id.id == semester_id:
                                        if invoice_count == 0 and   not sub.student_semester_id.block_result and  stuid.questionnaire_done():
                                            return sem.academicyear_id.name.split(':')[1] + ' ' + sem.semester_id.name.split('|')[1]

                                    else:
                                        return sem.academicyear_id.name.split(':')[1] + ' ' + sem.semester_id.name.split('|')[1]

        return ''
