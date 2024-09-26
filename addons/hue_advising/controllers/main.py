# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import werkzeug
import itertools
from odoo import http, api
from odoo.http import request


class WebsiteAdvising(http.Controller):
    # HELPER METHODS #

    def _check_bad_cases(self, survey):
        # In case of bad survey, redirect to surveys list
        if not survey.sudo().exists():
            return werkzeug.utils.redirect("/survey/")

        # Everything seems to be ok
        return None

    def get_subject_taken(self, student_id, subject, subject_id):
        semesters_subject_data = request.env['op.student.semesters.subjects'].sudo().search(
            [('subject_grade', '!=', False), ('subject_id', '=', subject), ('student_id', '=', student_id.id)])
        academic_years_ids = semesters_subject_data.mapped('academicyear_id').ids
        semesters_ids = semesters_subject_data.mapped('semester_id').ids
        academic_years = request.env['op.academic.year'].sudo().search(
            [('id', 'in', academic_years_ids), ('sequence', '!=', 0)], order='sequence asc')
        semesters = request.env['op.semesters'].sudo().search([('id', 'in', semesters_ids)], order='sequence asc')
        semesters_subject_list = []
        accum_semesters_subject = []
        for academic_year in academic_years:
            print("############################################")
            for semester in semesters:
                print("############################################")
                semesters_subject = request.env['op.student.semesters.subjects'].sudo().search(
                    [('subject_grade', '!=', False), ('subject_id', '=', subject), ('student_id', '=', student_id.id),
                     ('academicyear_id', '=', academic_year.id), ('semester_id', '=', semester.id), ('student_semester_id.transferred', '=', False)])
                published = self.is_published(semesters_subject.course_id.id,
                                              semesters_subject.academicyear_id.id,
                                              semesters_subject.semester_id.id)
                if published:
                    semesters_subject_list.append(semesters_subject.final_grade.name)
                    if len(semesters_subject_data) == 1:
                        accum_semesters_subject = (semesters_subject)
                    elif len(semesters_subject_data) > 1:
                        if semesters_subject.final_grade.id != 1:
                            accum_semesters_subject = (semesters_subject)
        # accum_semesters_subject = request.env['op.student.semesters.subjects'].sudo().search(
        #     [('subject_grade', '!=', False), ('subject_id', '=', subject), ('student_id', '=', student_id),('subject_grade', '!=', 1)],
        #     order='academicyear_id  desc,semester_id desc', limit=1)

        # if not published:
        #     accum_semesters_subject = False
        accum_fail_subject_count = request.env['op.student.semesters.subjects'].sudo().search_count(
            [('subject_id', '=', subject), ('student_id', '=', student_id.id), ('final_grade.pass_grade', '=', False),
             ('subject_grade', '!=', False), ('final_grade', '!=', 1)])

        curr_academic_year = request.env['op.academic.year'].sudo().search([], limit=1).id
        curr_semester = request.env['op.semesters'].sudo().search([('gpa_current', '=', True)], limit=1).id
        batch_courses = request.env['op.batch'].sudo().search(
            [('semester', '=', curr_semester), ('academic_year', '=', curr_academic_year)]).ids
        subject_registration_found = request.env['hue.subject.registration'].sudo().search_count(
            [('subject_id', '=', subject_id.id), ('batch_id', 'in', batch_courses)])
        if subject_registration_found > 0 :
            found = True
        else:
            found = False
        # all_accum_semesters_subject = request.env['op.student.semesters.subjects'].sudo().search(
        #     [('subject_grade', '!=', False), ('subject_id', '=', subject), ('student_id', '=', student_id)])
        # semesters_subject_list = []
        # for semesters_subject in all_accum_semesters_subject:
        #     published = self.is_published(semesters_subject.course_id.id,
        #                                   semesters_subject.academicyear_id.id,
        #                                   semesters_subject.semester_id.id)
        #     if  published:
        #         semesters_subject_list.append(semesters_subject.subject_grade.name)
        # all_accum_semesters_subject = all_accum_semesters_subject.subject_grade
        return [accum_semesters_subject, accum_fail_subject_count, semesters_subject_list,found]

    def is_published(self, courseid, acadyear, semester):
        published = request.env['op.course.resultspublish'].sudo().search(
            [('course_id', '=', courseid), ('acadyears', '=', acadyear), ('semesters', '=', semester)]).publishflag
        if published:
            if published == 'publish':
                return True
        return False

    ## ROUTES HANDLERS ##

    # Advising displaying
    @http.route(['/advising/<model("hue.gpa.calculator"):gpa_calculator>'], type='http', auth='public', website=True)
    def gpa_calculator(self, gpa_calculator, **post):
        '''Display and validates '''
        curr_academic_year = request.env['op.academic.year'].sudo().search([('gpa_current', '=', True)], limit=1).id
        curr_semester = request.env['op.semesters'].sudo().search([('gpa_current', '=', True)], limit=1).id
        course_id = gpa_calculator.student_id.course_id  # request.env['op.course'].sudo().search([('id','=',gpa_calculator.student_id.course_id.id)],limit=1).id
        deduction_grade_first = request.env['op.course.grades'].sudo().search(
            [('grade_id', '=', course_id.deduction_grade_first.id)], limit=1).points_from
        deduction_grade_second = request.env['op.course.grades'].sudo().search(
            [('grade_id', '=', course_id.deduction_grade_second.id)], limit=1).points_from
        # deduction_grade_second = course_\/id.deduction_grade_second
        # course_level_ids = request.env['op.course.grades'].sudo().search([('faculty_id','=',gpa_calculator.student_id.faculty.id)],limit=1).course_level_ids

        batch_courses = request.env['op.batch'].sudo().search(
            ['|', ('course_id', '=', course_id.parent_id.id), ('course_id', '=', course_id.id),
             ('semester', '=', curr_semester), ('academic_year', '=', curr_academic_year)]).ids
        print(batch_courses)
        print(batch_courses)
        print(batch_courses)
        subject_registration = request.env['hue.subject.registration'].sudo().search(
            [('batch_id', 'in', batch_courses)])
        batch_courses_ids = subject_registration.mapped('subject_id').ids
        for subject_registration_obj in subject_registration:
            pre_count = 0

            op_course_subject_prerequisites = request.env['op.subject'].sudo().search(
                [('id', '=', subject_registration_obj.subject_id.id), ('course_id', '=', course_id.id),
                 ('prerequisites_count', '!=', 0)], limit=1)
            prerequisites_count = op_course_subject_prerequisites.prerequisites_count
            for prerequisite in op_course_subject_prerequisites.subject_prerequisites:
                accum_semesters_subject_obj = request.env['op.student.semesters.subjects'].sudo().search(
                    [('student_id', '=', gpa_calculator.student_id.id), ('final_grade.pass_grade', '=', True),
                     ('subject_grade', '!=', False), ('subject_id', '=', prerequisite.id)], limit=1).id
                if accum_semesters_subject_obj:
                    pre_count += 1
                #
            if int(prerequisites_count) != 0 and pre_count < int(prerequisites_count):
                # if not accum_semesters_subject_obj:
                #     print(batch_courses_ids)
                #     print(subject_registration_obj.subject_id.id)
                if subject_registration_obj.subject_id.id in batch_courses_ids:
                    batch_courses_ids.remove(subject_registration_obj.subject_id.id)
                print(subject_registration_obj)

        print(batch_courses_ids)
        level_ids = request.env['op.levels'].sudo().search([])
        if level_ids:
            print(level_ids)
        gpa_limit_hours = request.env['op.course.loadhours'].sudo().search(
            [('semester_id', '=', gpa_calculator.semester_id.id),
             ('level_id', '=', gpa_calculator.student_id.level.id),
             ('course_id', '=', gpa_calculator.student_id.course_id.id),
             ('gpa_from', '<=', gpa_calculator.student_id.new_gpa),
             ('gpa_to', '>', gpa_calculator.student_id.new_gpa)]).hours_to
        # accum_semesters_subjects = survey.student_id.taken_accum_semesters_subjects()
        # accum_semesters_subjects = accum_semesters_subjects[1].mapped('subject_id').ids
        # accum_semesters_subjects =  request.env['op.student.semesters.subjects'].search([('student_id','=',survey.student_id.id)])
        # print(accum_semesters_subjects)
        accum_semesters_subjects = request.env['op.student.semesters.subjects'].sudo().search(
            [('student_id', '=', gpa_calculator.student_id.id), ('student_semester_id.transferred', '=', False)])
        accum_semesters_subject_data = accum_semesters_subjects.mapped('subject_id').ids

        grades = gpa_calculator.student_id.course_id.sudo().course_grade_ids
        accum_semesters_subjects = []
        for subject in accum_semesters_subject_data:
            accum_subject = request.env['op.student.semesters.subjects'].sudo().search(
                [('subject_grade', '!=', False), ('subject_id', '=', subject),
                 ('student_id', '=', gpa_calculator.student_id.id),
                 ('student_semester_id.transferred', '=', False)], limit=1)
            published = self.is_published(accum_subject.course_id.id,
                                          accum_subject.academicyear_id.id,
                                          accum_subject.semester_id.id)
            if published:
                accum_semesters_subjects.append(subject)
        advisor = request.env['hue.academic.direction.line'].sudo().search(
            [('student_id', '=', gpa_calculator.student_id.id), ('to_date', '=', False)], limit=1).faculty_id.name
        levels_list = []
        all_subjects_list = []
        for level in level_ids:
            subjects_list = []
            level_subjects = request.env['op.subject'].sudo().search(
                ['|', ('id', 'in', accum_semesters_subjects),
                 ('id', 'in', batch_courses_ids), ('subject_level', '=', level.id), '|',
                 ('course_id', '=', course_id.parent_id.id), ('course_id', '=', course_id.id)])  #
            print(level.name)
            print(level_subjects)
            if level_subjects:
                subjects_list.append(level.name)
                subjects_list.append(level_subjects)
                all_subjects_list.append(level_subjects.ids)
                levels_list.append(subjects_list)

        all_subjects_list = list(itertools.chain(*all_subjects_list))
        print(all_subjects_list)
        data = {'advisor': advisor, 'gpa_limit_hours': gpa_limit_hours, 'advising': gpa_calculator, 'grades': grades,
                'levels': levels_list, 'get_subject_taken': self.get_subject_taken,
                'all_subjects_list': all_subjects_list, 'suggested_plan': gpa_calculator.suggested_plan_ids,
                'deduction_grade_first': deduction_grade_first,
                'deduction_grade_second': deduction_grade_second}  # , 'page': page, 'page_nr': page_nr, 'token': user_input.token}
        return request.render('hue_advising.gpa_calculator', data)

    @http.route(['/gpa/fill/<model("hue.gpa.calculator"):gpa_calculator>'], type='http', methods=['POST'],
                auth='public', website=True)
    def submit(self, gpa_calculator, **post):
        csrf_token = post.get('csrf_token', False)
        all_subjects_list = post.get('all_subjects_list', False)
        gpa_calculator.current_gpa = post.get('new_gpa', False)
        gpa_calculator.ex_gpa = post.get('ex_gpa', False)
        all_subjects_list = all_subjects_list.strip('][').split(', ')
        gpa_subjects = []
        for subject_id in all_subjects_list:
            reg_subject = post.get('reg_subject[' + subject_id + ']', False)
            if reg_subject:
                gpa_subjects.append(int(subject_id))
                exist_suggested_plan = request.env['hue.suggested.plan'].search(
                    [('gpa_calculator_id', '=', int(gpa_calculator.id)), ('subject_id', '=', int(subject_id))])
                print(exist_suggested_plan)
                if exist_suggested_plan:
                    exist_suggested_plan.write({'ex_grades': reg_subject})
                else:
                    request.env['hue.suggested.plan'].create(
                        {'gpa_calculator_id': gpa_calculator.id, 'subject_id': subject_id, 'ex_grades': reg_subject})
        print(gpa_subjects)
        for suggested_plan in gpa_calculator.suggested_plan_ids:
            if suggested_plan.subject_id.id not in gpa_subjects:
                suggested_plan.unlink()
        gpa_calculator.suggested_plan_ids.mapped
        all_subjects_list = list(all_subjects_list)
        print(all_subjects_list)
        print(gpa_calculator)
        print("dddddddddddddddddd")

        return request.redirect('/advising/%s' % (gpa_calculator.id))