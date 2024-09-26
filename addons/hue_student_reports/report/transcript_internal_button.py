import time
from odoo import api, models


class StudentTranscriptReport2(models.AbstractModel):
    _name = 'report.hue_student_reports.report_transcript_internal'
    _description = "Student Transcript Report"

    def is_published(self, courseid, acadyear, semester):
        published = self.env['op.course.resultspublish'].sudo().search(
            [('course_id', '=', courseid), ('acadyears', '=', acadyear), ('semesters', '=', semester)]).publishflag
        if published:
            if published == 'publish':
                return True
        return False
    
    def get_gpa_ch(self,student_id):
        curr_academic_year = self.env['op.semesters'].sudo().search([('enroll_semester', '=', True)], limit=1).term_id.academic_year_id
        academic_years = self.env['op.academic.year'].sudo().search([('sequence', '!=', 0)], order='sequence asc')
        semesters = self.env['op.semesters'].sudo().search([], order='sequence asc')
        AcadYearID = self.env['op.academic.year'].sudo().search([('run_semester_gpa', '=', True)], limit=1).id
        semester_id = self.env['op.semesters'].sudo().search([('run_semester_gpa', '=', True)], limit=1).id
        # semester_id = self.env['op.semesters'].sudo().search([('id', '=', 2)], limit=1).id
        subjects =[]
        hours_without_improve =0
        invoice_count = 0
        if not student_id.allow_registration:
            domain = [
                ('move_type', 'in', ['out_invoice']),
                # ('date_due', '<=', date.today()),
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
                                sub_without_improve = self.env['op.student.semesters.subjects'].sudo().search([('academicyear_id', '=', item.academicyear_id.id),
                                    ('semester_id', '=', item.semester_id.id),('student_id', '=', student_id.id)])
                                for sub_improve in sub_without_improve :
                                    if sub_improve.subject_grade.pass_grade == True :
                                        if sub_improve.subject_id not in subjects:
                                            subjects.append(sub_improve.subject_id)
                                totalhours += item.semester_hr
                                totalgpa = item.current_gpa
                        else:
                            sub_without_improve = self.env['op.student.semesters.subjects'].sudo().search([('academicyear_id', '=', item.academicyear_id.id),
                                    ('semester_id', '=', item.semester_id.id),('student_id', '=', student_id.id)])
                            for sub_improve in sub_without_improve :
                                if sub_improve.subject_grade.pass_grade == True :
                                    if sub_improve.subject_id not in subjects:
                                        subjects.append(sub_improve.subject_id)
                            totalhours += item.semester_hr
                            totalgpa = item.current_gpa                  
        for x in subjects :
            hours_without_improve += x.subject_credithours
        return [totalgpa, totalhours, hours_without_improve]
    
    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        student_id = self.env[model].browse(self.env.context.get('active_id'))
        if not student_id:
            student_id = self._context.get('student_id')
        docs = {'student_id': student_id, 'report_type': 'transcript', 'language': 'ar', 'student_code_show': True,
                'title': False, 'logo': False, 'student_pic': False, 'course': True, 'level': True,
                'national_id': False, 'nationality': False, 'birthday': False, 'birth_place': False, 'address': False,
                'prev_cert': False, 'military': False, 'results': False, 'to': '', 'notes': '', 'results': True}
        # student_id = student
        # student_code = docs.student_code
        # docs = list(docs)
        # print('________________________________________________________________')
        # print(docs['title'])
        # student = self.env['op.student.accumulative'].sudo().search([('accum_semesters_ids.transferred', '=', False),('student_id', '=', student_id.id),'|',('course_id', '=', student_id.course_id.id),('course_id', '=', student_id.course_id.parent_id.id)],order = 'academicyear_id desc')
        student = []
        curr_academic_year = self.env['op.semesters'].sudo().search([('enroll_semester', '=', True)], limit=1).term_id.academic_year_id
        academicyear = self.env['op.academic.year'].sudo().search([('sequence', '!=', 0)],order = 'sequence asc')
        semesters = self.env['op.semesters'].sudo().search([],order = 'sequence asc')
        for year in academicyear :
            for semester in semesters :
                batch_student = self.env['op.student.accumlative.semesters'].sudo().search([('transferred', '=', False),('student_id', '=', student_id.id),'|',('course_id', '=', student_id.course_id.id),
                ('course_id', '=', student_id.course_id.parent_id.id),('academicyear_id', '=', year.id),
                ('semester_id', '=', semester.id),('accum_semesters_subjects_ids', '!=', False)])
                if batch_student :
                    student.append(batch_student)
        invoice_count = 0
        if not student_id.allow_registration:
            domain = [
                ('move_type', 'in', ['out_invoice']),
                # ('date_due', '<=', date.today()),
                ('invoice_date_due', '<=',curr_academic_year.invoice_date),
                ('partner_id', '=', student_id.partner_id.id),
                ('state', 'in', ['draft'])
            ]
            invoice_count = self.env['account.move'].sudo().search_count(domain)
        # AcadYearID = self.env['hue.academic.years'].sudo().search([('run_semester_gpa', '=', True)], limit=1).id
        # semester_id = self.env['op.semesters'].sudo().search([('run_semester_gpa', '=', True)], limit=1).id
        accum_semesters = self.env['op.student.accumlative.semesters'].sudo().search(
            [('student_id', '=', student_id.id),('semester_gpa', '!=', False),
             ('transferred', '=', False),('accum_semesters_subjects_ids', '!=', False)],order="id desc",limit=1)
        AcadYearID = accum_semesters.academicyear_id.id
        semester_id = accum_semesters.semester_id.id
        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'docs': docs,
            'time': time,
            'student': student,
            'is_published': self.is_published,
            'AcadYearID': AcadYearID,
            'semester_id': semester_id,
            'get_gpa_ch' : self.get_gpa_ch,
            'invoice_count': invoice_count,
            'get_med_above_semester_six':self.get_med_above_semester_six
        }
        return docargs
    
    def get_med_above_semester_six(self,subject_id):
        subj_above_semester_six = self.env['op.course.subjects'].sudo().search(
            [('id', '=', subject_id.id),('subject_level.level_id.d_id', '>=', 6)])
        if subj_above_semester_six :
            return True
        else :
            return False