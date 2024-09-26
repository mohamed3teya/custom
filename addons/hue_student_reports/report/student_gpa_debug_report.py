import time
from decimal import Decimal, ROUND_HALF_UP
from odoo import api, models


class StudentGpaDebugnReports(models.AbstractModel):
    _name = 'report.hue_student_reports.student_gpa_debug_reports'
    _description = "GPA Debug  Form"


    def is_published(self, courseid, acadyear, semester):
        published = self.env['op.course.resultspublish'].sudo().search(
            [('course_id', '=', courseid), ('acadyears', '=', acadyear), ('semesters', '=', semester)]).publishflag
        if published:
            if published == 'publish' or published == 'close':
                return True
        return False

    def get_semester_subjects(self, student,academic_year, semester):
        accum_semesters_subjects = self.env['op.student.semesters.subjects'].sudo().search(
            [('student_id', '=', student),('academicyear_id', '=', academic_year), ('semester_id', '=', semester),
             ('student_semester_id.transferred', '=', False)])
        return accum_semesters_subjects

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        student = self.env[model].browse(self.env.context.get('active_id'))
        accum_semesters_subjects = self.env['op.student.semesters.subjects'].sudo().search(
            [('subject_grade', '!=', False), ('student_id', '=', student.id),
             ('student_semester_id.transferred', '=', False)])
        accum_semesters_subjects = accum_semesters_subjects
        subject_ids = accum_semesters_subjects.mapped('subject_id').ids
        subject_ids = list(dict.fromkeys(subject_ids))
        new_gpa = 0 
        numerator = 0  # بسط فوق
        denominator = 0  # مقام
        crh_denominator = 0
        crh_core = 0
        crh_elective = 0
        crh_project = 0
        for subject in subject_ids:
            accum_subject = self.env['op.student.semesters.subjects'].sudo().search(
                [('subject_grade', '!=', False), ('subject_id', '=', subject), ('student_id', '=', student.id),
                 ('student_semester_id.transferred', '=', False)])
            # print(accum_subject)
            if len(accum_subject) > 1:
                sel_accum_subjects = self.env['op.student.semesters.subjects'].sudo().search(
                    [('subject_grade', '!=', False), ('subject_id', '=', subject), ('student_id', '=', student.id),('student_semester_id.transferred', '=', False)],
                    ).sorted(key=lambda r: (r.academicyear_id.sequence ,r.semester_id.sequence ), reverse=True)
                fail_grades = self.env['op.grades'].sudo().search([('pass_grade', '=', False)]).ids
                for sel_accum_subject in sel_accum_subjects:
                    published = self.is_published(sel_accum_subject.course_id.id,
                                                  sel_accum_subject.academicyear_id.id,
                                                  sel_accum_subject.semester_id.id)
                    if not published:
                        continue
                    print("0")
                    # print(sel_accum_subject.subject_id.name)
                    subject_grade = sel_accum_subject.final_grade
                    if not subject_grade.pass_grade and not subject_grade.add_to_gpa:
                        print("1")
                        print(sel_accum_subject.subject_id.name)
                        continue
                    elif not subject_grade.pass_grade and subject_grade.add_to_gpa:
                        print("2")
                        if sel_accum_subject.subject_id.subject_addtogpa:
                            print("2")
                            print(sel_accum_subject.subject_id.name)
                            grade_points = self.env['op.course.grades'].sudo().search(
                                [('course_id', '=', student.course_id.id),
                                 ('grade_id', '=', subject_grade.id)],
                                limit=1).points_from
                            chk_fc = self.env['op.student.semesters.subjects'].sudo().search(
                            [('subject_grade', '!=', False), ('subject_id', '=', subject),
                             ('student_id', '=', student.id), ('final_grade', '=', 5)])
                            
                            #if chk_fc == False:
                            denominator = denominator + sel_accum_subject.subject_id.subject_credithours
                            print("denominator")
                            print(sel_accum_subject.subject_id.subject_credithours)
                            print("denominator")
                            numerator = numerator + (
                                round((grade_points * sel_accum_subject.subject_id.subject_credithours), 3))
                            break
                    elif subject_grade.pass_grade and subject_grade.add_to_gpa:
                        print("22222222222")
                        print(sel_accum_subject.final_degree)
                        print(sel_accum_subject.id)
                        print("2222222222")
                        de_accum_subjects = self.env['op.student.semesters.subjects'].sudo().search(
                            [('subject_grade', '!=', False), ('subject_id', '=', subject),
                             ('student_id', '=', student.id), ('id', '!=', sel_accum_subject.id),('student_semester_id.transferred', '=', False),
                             ('final_grade', 'not in', fail_grades)], order='final_degree  desc')
                        for de_accum_subject in de_accum_subjects.sorted(key=lambda r: r.final_degree,
                                                                         reverse=True):
                            published = self.is_published(de_accum_subject.course_id.id,
                                                          de_accum_subject.academicyear_id.id,
                                                          de_accum_subject.semester_id.id)
                            if not published:
                                continue
                            #  engineering
                            if student.faculty.id == 9 :
                                # if sel_accum_subject.id > de_accum_subject.id :
                                if sel_accum_subject.academicyear_id.sequence >= de_accum_subject.academicyear_id.sequence and sel_accum_subject.semester_id.sequence > de_accum_subject.semester_id.sequence:
                                    subject_grade = sel_accum_subject.final_grade
                            else :
                                if de_accum_subject.final_degree > sel_accum_subject.final_degree:
                                    subject_grade = de_accum_subject.final_grade
                                    if subject_grade.pass_grade and subject_grade.add_to_gpa:
                                        print("3333333333")
                                        print(de_accum_subject.final_degree)
                                        print(de_accum_subject.id)
                                        print("333333333333")
                                        sel_accum_subject = de_accum_subject
                                        break
                        crh_denominator = crh_denominator + sel_accum_subject.subject_id.subject_credithours
                        if sel_accum_subject.subject_id.subject_type == 'compulsory':
                            crh_core += sel_accum_subject.subject_id.subject_credithours
                        if sel_accum_subject.subject_id.subject_type == 'elective':
                            crh_elective += sel_accum_subject.subject_id.subject_credithours
                        if sel_accum_subject.subject_id.subject_type == 'project':
                            crh_project += sel_accum_subject.subject_id.subject_credithours

                        if sel_accum_subject.subject_id.subject_addtogpa:
                            grade_points = self.env['op.course.grades'].sudo().search(
                                [('course_id', '=', student.course_id.id),
                                 ('grade_id', '=', subject_grade.id)],
                                limit=1).points_from

                            denominator = denominator + sel_accum_subject.subject_id.subject_credithours
                            print("denominator")
                            print(sel_accum_subject.subject_id.subject_credithours)
                            print("denominator")
                            numerator = numerator + (round((
                                    grade_points * sel_accum_subject.subject_id.subject_credithours), 3))
                            break
                    elif subject_grade.pass_grade and not subject_grade.add_to_gpa:
                        print("4")
                        print(sel_accum_subject.subject_id.name)
                        print(subject_grade.name)
                        crh_denominator = crh_denominator + sel_accum_subject.subject_id.subject_credithours

                        if sel_accum_subject.subject_id.subject_type == 'compulsory':
                            crh_core += sel_accum_subject.subject_id.subject_credithours
                        if sel_accum_subject.subject_id.subject_type == 'elective':
                            crh_elective += sel_accum_subject.subject_id.subject_credithours
                        if sel_accum_subject.subject_id.subject_type == 'project':
                            crh_project += sel_accum_subject.subject_id.subject_credithours
                        break

            else:
                published = self.is_published(accum_subject.course_id.id, accum_subject.academicyear_id.id,
                                              accum_subject.semester_id.id)
                if not published:
                    continue
                # print(accum_subject.subject_id.name)
                subject_grade = accum_subject.final_grade
                print("ddddddddd")
                print(accum_subject.subject_id.name)
                if subject_grade.pass_grade:
                    crh_denominator = crh_denominator + accum_subject.subject_id.subject_credithours
                    if accum_subject.subject_id.subject_type == 'compulsory':
                        crh_core += accum_subject.subject_id.subject_credithours
                    if accum_subject.subject_id.subject_type == 'elective':
                        crh_elective += accum_subject.subject_id.subject_credithours
                    if accum_subject.subject_id.subject_type == 'project':
                        crh_project += accum_subject.subject_id.subject_credithours
                if accum_subject.subject_id.subject_addtogpa and subject_grade.add_to_gpa:
                    # print(accum_subject.subject_id.name)
                    grade_points = self.env['op.course.grades'].sudo().search(
                        [('course_id', '=', student.course_id.id),
                         ('grade_id', '=', subject_grade.id)], limit=1).points_from
                    denominator = denominator + accum_subject.subject_id.subject_credithours
                    print("denominator")
                    print(accum_subject.subject_id.subject_credithours)
                    print("denominator")
                    numerator = numerator + (
                        round((grade_points * accum_subject.subject_id.subject_credithours), 3))
                    print(accum_subject.subject_id.name)
                    print((grade_points * accum_subject.subject_id.subject_credithours))
        if subject_ids:
            print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
            if denominator > 0:
                # print(numerator)
                # print(denominator)
                numerator = round(numerator, 2)
                new_gpa = numerator / denominator
                print(new_gpa)
                print(Decimal(new_gpa).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP))
                
                # new_gpa = round(new_gpa, 3)
                #print(new_gpa2)
                new_gpa =round(new_gpa+10**(-len(str(new_gpa))-1), 2)                
                print(new_gpa)
                
                print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
                print(crh_core)


        academic_years = self.env['op.academic.year'].sudo().search([('sequence', '!=', 0)], order='sequence asc')
        semesters = self.env['op.semesters'].sudo().search([], order='sequence asc')
        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'total_points' : numerator,
            'total_actual_hours' : denominator,
            'time': time,
            'crh_denominator': crh_denominator,
            'student': student,
            'academic_years': academic_years,
            'semesters': semesters,
            'new_gpa': new_gpa,
            'get_semester_subjects': self.get_semester_subjects,
            'is_published': self.is_published,
        }
        return docargs
