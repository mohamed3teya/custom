# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import logging
from datetime import date, datetime
from odoo.exceptions import UserError
from odoo import http
from odoo.http import request


class WebsiteRegistration(http.Controller):

    # HELPER METHODS #
    def _get_data(self, student_id):
        # request.session['student'] = False
        user = request.env['res.users'].sudo().browse(request.uid)
        # request.session = []
        academic_year = None
        semester = None
        closed = True
        closed_invoice = False
        closed_block = False
        calendar = None
        batch = None
        batch2 = None
        calendar_j = False
        admin_user = False
        adviser = False
        event_type = 'student_registration'
        # print(admin_user)

        if student_id and (request.env.ref('HUE_openeducat_core.group_service_manager') in user.groups_id or request.env.ref(
                'openeducat_core.group_op_back_office') in user.groups_id or request.env.ref(
                'HUE_openeducat_core.group_advisor_admin') in user.groups_id):
            student = request.env['op.student'].sudo().search([('id', '=', student_id)], limit=1)
        else:
            student = request.env['op.student'].sudo().search([('user_id', '=', request.uid)], limit=1)

        student_fields_to_read = ['first_name', 'middle_name', 'last_name', 'blood_group', 'gender', 'nationality', 'emergency_contact', 'visa_info', 'id_number', 'partner_id', 'user_id', 'gr_no', 'category_id', 'course_detail_ids', 'active', 'id', 'fees_detail_ids', 'fees_details_count', 'parent_ids', 'library_card_id', 'media_movement_lines', 'media_movement_lines_count', 'advisor', 'allow_registration', 'already_partner', 'alumni_academicyear_id', 'alumni_semester_id', 'approval_num', 'approval_type', 'bank_account_count', 'bank_ids', 'brother_discount', 'certificate_degree', 'certificate_country', 'cgpa', 'commercial_partner_country_id', 'conflict_crh', 'conflict_gpa', 'contracts_count', 'core_crh', 'course_id', 'crh', 'customer', 'decisionno', 'd_name', 'elective_crh', 'en_name', 'faculty', 'father_discount', 'father_job', 'father_mail', 'father_mobile', 'father_name', 'father_nationality', 'father_phone', 'final_degree', 'gardian_mobile', 'gardian_name', 'gardian_tele', 'gardian_type', 'gardian_job', 'intern_month', 'join_term', 'join_year', 'level', 'martyrs_discount', 'mc', 'm_graph_id', 'militaryno', 'military_status', 'mother_job', 'mother_mail', 'mother_mobile', 'mother_name', 'mother_nationality', 'mother_phone', 'national_id', 'new_crh', 'new_gpa', 'opt_out', 'partner_ledger_label', 'password', 'payment_next_action', 'percentage', 'photo_hide', 'prequaldegree', 'previous_course_id', 'project_crh', 'project_gpa', 'project_grade', 'project_title', 'qualyear', 'registration_block_reason', 'related_student', 'religion', 'result_block_reason', 'sale_order_count', 'scholarship', 'sds_tobedeleted', 'seatno', 'sibling_id', 'sibling_name', 'sibling_student_id', 'special_case', 'specialized_faculty', 'specialneeds', 'student_birth_place', 'student_certificates', 'student_city', 'student_code', 'student_nationality', 'student_school', 'student_status', 'student_term', 'stumobile', 'stutele', 'subject_degree', 'supplier', 'syndicate_discount', 'task_count', 'total_degree', 'total_due', 'transfer_type', 'Pre_join_year', 'pre_transfer_type', 'transferred_from','university_country', 'unreconciled_aml_ids', 'year', 'student_accumlative_ids', 'student_semesters_accumlative_ids', 'student_attendance_ids', 'transport_ids', 'military_done', 'military_id', 'done_military_id', 'military_notes', 'session_tmp_ids', 'university_name', 'session_ids', 'student_advisor_id', 'website_id', 'website_published', 'is_published', 'can_publish', 'website_url', 'email_normalized', 'is_blacklisted', 'name', 'complete_name', 'title', 'parent_id', 'parent_name', 'child_ids', 'ref', 'lang', 'active_lang_count', 'tz', 'tz_offset', 'vat', 'same_vat_partner_id', 'same_company_registry_partner_id', 'company_registry', 'website', 'comment', 'employee', 'function', 'type', 'street', 'street2', 'zip', 'city', 'state_id', 'country_id', 'country_code', 'partner_latitude', 'partner_longitude', 'email', 'email_formatted', 'phone', 'mobile', 'is_company', 'is_public', 'industry_id', 'company_type', 'company_id', 'color', 'user_ids', 'partner_share', 'contact_address', 'commercial_partner_id', 'commercial_company_name', 'company_name', 'barcode', 'self', 'im_status', 'channel_ids', 'contact_address_inline', 'starred_message_ids', 'signup_valid', 'signup_url', 'meeting_count', 'meeting_ids', 'property_product_pricelist', 'team_id', 'partner_gid', 'additional_info', 'phone_sanitized', 'phone_sanitized_blacklisted', 'phone_blacklisted', 'mobile_blacklisted', 'phone_mobile_search', 'certifications_count', 'certifications_company_count', 'payment_token_ids', 'payment_token_count', 'fiscal_country_codes', 'days_sales_outstanding', 'debit_limit', 'currency_id', 'journal_item_count', 'property_account_payable_id', 'property_account_receivable_id', 'property_account_position_id', 'property_payment_term_id', 'property_supplier_payment_term_id', 'ref_company_ids', 'has_unreconciled_entries', 'invoice_ids', 'contract_ids', 'trust', 'invoice_warn', 'invoice_warn_msg', 'supplier_rank', 'customer_rank', 'duplicated_bank_account_partners_count', 'property_stock_supplier', 'picking_warn','is_parent', 'is_student', 'sale_order_ids', 'is_venue']
        request.session['student'] = json.dumps(student.read(student_fields_to_read))
        print(request.session['student'])
        if 'student' in request.session and request.session['student'] == True:
            student_j = json.loads(request.session['student'])[0]

        if student_id or ('student' in request.session and student and int(student_j['id']) != student.id):
            if student_id:
                # admin_user = True
                # event_type = 'admin_registration'
                print('//////////////////////////////// User is ...')
                if request.env.ref('HUE_openeducat_core.group_service_manager') in user.groups_id or request.env.ref(
                        'openeducat_core.group_op_back_office') in user.groups_id:
                    print('//////////////////////////////// Admin')
                    admin_user = True
                    event_type = 'admin_registration'
                elif request.env.ref('HUE_openeducat_core.group_advisor_admin') in user.groups_id:
                    print('//////////////////////////////// Adviser')
                    adviser = True
                    event_type = 'adviser_registration'
            request.session['student'] = False
            request.session['prerequisites'] = False
            request.session['stu_course'] = False
            request.session['course_subjects'] = False
            request.session['course_loadhourslevels_ids'] = False
            request.session['calendar'] = False


        if student_id and (request.env.ref('HUE_openeducat_core.group_service_manager') in user.groups_id or request.env.ref(
                'openeducat_core.group_op_back_office') in user.groups_id or request.env.ref(
                'openeducat_core.group_op_back_office_admin') in user.groups_id or request.env.ref(
                'HUE_openeducat_core.group_advisor_admin') in user.groups_id):
            student = request.env['op.student'].sudo().search([('id', '=', int(student_id))], limit=1)

        else:
            student = request.env['op.student'].sudo().search([('user_id', '=', request.uid)], limit=1)
        student = request.env['op.student'].sudo().search([('id', '=', student_id)], limit=1)
        # print((student.read(['id', 'student_accumlative_ids', 'student_attendance_ids', 'faculty'])))
        request.session['student'] = json.dumps(
            student.read(['level', 'id', 'cgpa', 'new_gpa', 'name', 'student_code' ,'new_crh','elective_crh' ,'project_crh','core_crh','crh']), ensure_ascii=False)
        student_j = json.loads(request.session['student'])[0]

        course_fields_to_read = ['name', 'code', 'parent_id', 'evaluation_type', 'subject_ids', 'max_unit_load', 'min_unit_load', 'department_id', 'active', 'id', 'display_name', 'fees_term_id', 'origin', 'access_token', 'refund_invoice_id', 'number', 'move_name', 'reference', 'control_email', 'corehours', 'course_cotrolgrades_ids', 'course_grade_eqiv_ids', 'course_grade_ids', 'course_level_ids', 'course_loadhours_ids', 'course_loadhourslevels_ids', 'course_resultspublish_ids', 'subjects_ids', 'credithours', 'cretificate_arabicname', 'cretificate_englishname', 'deduction_grade_first', 'deduction_grade_second', 'electivehours', 'enhancment', 'faculty_id', 'faculty_ids', 'farouk_id', 'freehours', 'fr_percent', 'gpafailscount', 'honors_gpa', 'intern_year', 'loadhourstype', 'pass_degree', 'projecthours', 'sds_tobedeleted', 'second_pass_degree', 'section', 'traininghours']
        # fields = request.env['op.course.loadhours'].fields_get()
        # field_names = list(fields.keys())
        # print("course_loadhours_field_names:----------", field_names)
        subject_fields_to_read = ['name', 'code', 'grade_weightage', 'type', 'subject_type', 'department_id', 'active', 'id', 'display_name','course_id', 'parent_course_id', 'prerequisites_count', 'required_hours', 'subject_assessmentsdegree', 'subject_credithours', 'subject_lecturehours', 'subject_level', 'subject_oralhours', 'subject_passpercentage', 'subject_practhours', 'subject_sectionhours', 'subject_prerequisites', 'subject_semester', 'subject_total', 'subject_core_type', 'summer_training', 'ethics', 'intern_subject', 'subject_addtogpa', 'subject_addtohours', 'subject_credithours_invoice', 'subject_passorfail', 'subject_satisfied', 'subject_requiredfrom', 'subject_elective', 'division_id', 'subject_types']
        calendar_fields_to_read = ['course_id', 'type', 'academic_year', 'semester', 'level', 'gpa_from', 'gpa_to', 'student_id', 'max_level', 'id', 'display_name']
        course_load_hours_to_read = ['course_id', 'gpa_from', 'gpa_to', 'hours_from', 'hours_to', 'level_id', 'semester_id', 'id', 'display_name']
        try:
            prerequisites_j = json.loads(request.session['prerequisites'])
            stu_course_j = json.loads(request.session['stu_course'])[0]
            course_subjects_j = json.loads(request.session['course_subjects'])
            course_loadhourslevels_ids_j = json.loads(request.session['course_loadhourslevels_ids'])
            course_loadhours_ids_j = json.loads(request.session['course_loadhours_ids'])
        except:
            stu_course = student.course_id
            request.session['course_loadhourslevels_ids'] = json.dumps(stu_course.course_loadhourslevels_ids.read())
            request.session['course_loadhours_ids'] = json.dumps(stu_course.course_loadhours_ids.read(course_load_hours_to_read))
            request.session['stu_course'] = json.dumps(stu_course.read(course_fields_to_read))
            prerequisites = []
            for cs in stu_course.subjects_ids:
                for prereq in cs.subject_prerequisites:
                    obj = {'id': cs.id, 'pre': prereq.id}
                    prerequisites.append(obj)
            for cs in stu_course.parent_id.subjects_ids:                
                for prereq in cs.subject_prerequisites:
                    print(prereq.name)
                    obj = {'id': cs.id, 'pre': prereq.id}
                    prerequisites.append(obj)  
            request.session['prerequisites'] = json.dumps(prerequisites)
            request.session['course_subjects'] = json.dumps(stu_course.subjects_ids.read(subject_fields_to_read))
            prerequisites_j = json.loads(request.session['prerequisites'])
            stu_course_j = json.loads(request.session['stu_course'])
            course_subjects_j = json.loads(request.session['course_subjects'])
            course_loadhourslevels_ids_j = json.loads(request.session['course_loadhourslevels_ids'])
            course_loadhours_ids_j = json.loads(request.session['course_loadhours_ids'])
        
        if stu_course_j:
            request.session['calendar'] = False
            if 'calendar' not in request.session or not request.session['calendar']:
                if admin_user:
                    calendar = request.env['hue.event.calendar'].sudo().search(
                        [('type', '=', 'admin_registration'), ('course_id', '=', stu_course_j[0]['id']),
                         ('start_date', '<=', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                         ('end_date', '>=', datetime.now().strftime("%Y-%m-%d %H:%M:%S")), ('type', '=', event_type)],
                        limit=1)
                elif adviser:
                    calendar = request.env['hue.event.calendar'].sudo().search(
                        [('type', '=', 'adviser_registration'), ('course_id', '=', stu_course_j[0]['id']),
                         ('start_date', '<=', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                         ('end_date', '>=', datetime.now().strftime("%Y-%m-%d %H:%M:%S")), ('type', '=', event_type),
                         ('gpa_from', '<=', student.new_gpa), ('gpa_to', '>', student.new_gpa),
                         ('level', '=', student.level.id)], limit=1)
                else:
                    calendar = request.env['hue.event.calendar'].sudo().search(
                        [('type', '=', 'student_registration'), ('course_id', '=', stu_course_j[0]['id']),
                         ('start_date', '<=', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                         ('end_date', '>=', datetime.now().strftime("%Y-%m-%d %H:%M:%S")), ('type', '=', event_type),
                         ('gpa_from', '<=', student.new_gpa), ('gpa_to', '>', student.new_gpa),
                         ('level', '=', student.level.id)], limit=1)
                    if not calendar:
                        # print('______________ NOT GPA')
                        # print(student.cgpa)
                        calendar = request.env['hue.event.calendar'].sudo().search(
                            [('type', '=', 'student_registration'), ('course_id', '=', stu_course_j[0]['id']),
                             ('start_date', '<=', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                             ('end_date', '>=', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                             ('type', '=', event_type), ('gpa_from', '<=', student.new_gpa),
                             ('gpa_to', '>', student.new_gpa), ('level', '=', None)], limit=1)
                
                if calendar:
                    # print("calendar")
                    # print(calendar)
                    # print(calendar.student_id)
                    if calendar.student_id:
                        if student.id in calendar.student_id.ids:
                            request.session['calendar'] = json.dumps(calendar.read(calendar_fields_to_read))
                            calendar_j = json.loads(request.session['calendar'])[0]
                    else:
                        request.session['calendar'] = json.dumps(calendar.read(calendar_fields_to_read))
                        calendar_j = json.loads(request.session['calendar'])[0]
            else:
                calendar_j = json.loads(request.session['calendar'])[0]
            print(stu_course.name)
            print('_______________calendar_jcalendar_jcalendar_j____________________')
            print(calendar_j)
            if calendar_j:
                closed = False
                # print("stu_course_j[0]['id']:---------", stu_course_j[0]['id'])
                print("calendar_j['academic_year'][0]:------------", calendar_j['academic_year'][0])
                print("calendar_j['semester'][0]:----------------", calendar_j['semester'][0])
                batch = request.env['op.batch'].sudo().search(
                    [('course_id', '=', stu_course_j[0]['id']), ('academic_year', '=', calendar_j['academic_year'][0]),
                     ('semester', '=', calendar_j['semester'][0]), ('intern_batch', '=', False)], limit=1)
                # batch2 = False
                if stu_course_j[0]['parent_id']:
                    batch2 = request.env['op.batch'].sudo().search([('course_id', '=', stu_course_j[0]['parent_id'][0]), (
                    'academic_year', '=', calendar_j['academic_year'][0]), ('semester', '=', calendar_j['semester'][0]),
                                                                    ('intern_batch', '=', False)], limit=1)
                academic_year = calendar_j['academic_year'][1]
                semester = calendar_j['semester'][1].split('|')[1]
        # print(stu_course_j)
        print("calendar_j:-----------------------", calendar_j)
        print("batch:-----------------------", batch)
        if calendar_j and batch:
            if batch2:
                print("2222222222222222222222222222222222222222222222")
                print("batch2:---------------", batch2)
                sessions = request.env['op.session'].sudo().search([
                    # ('subject_id', '=', subject_id.subject_id.id),
                    # ('course_id','=',subject_id.course_id.id),
                    '|',
                    ('batch_id', '=', batch.id),
                    ('batch_id', '=', batch2.id),
                    ('start_datetime', '>=', batch.default_week_start),
                    ('end_datetime', '<=', str(batch.default_week_end) + ' 23:59:59'),
                ])
                print("Sessions2222222222222:---------------", sessions)
            else:
                print("333333333333333333333333333333333333333333333333")
                sessions = request.env['op.session'].sudo().search([
                    # ('subject_id', '=', subject_id.subject_id.id),
                    # ('course_id','=', subject_id.course_id.id),
                    ('batch_id', '=', batch.id),
                    ('start_datetime', '>=', batch.default_week_start),
                    ('end_datetime', '<=', str(batch.default_week_end) + ' 23:59:59'),
                ])
        else:
            sessions = []
        # print("sessions:----------------", sessions)

        #############################################################
        ################### Subjects in Timetable ###################
        #############################################################
        all_subjects = []
        for session in sessions:
            # print('____________________')
            # print("session:---------------------", session)
            if session.subject_id not in all_subjects:
                all_subjects.append(session.subject_id)
        # print("all_subjects:------", all_subjects)
        ######################################################
        ################### Taken Subjects ###################
        ######################################################
        accumulative_ids = request.env['op.student.accumulative'].sudo().search([('student_id', '=', student_j['id'])])
        core_hours = 0
        elec_hours = 0
        project_hours = 0
        taken_subjects = []
        for acc in accumulative_ids:
            subjects_in_course = []
            for subject_in_course in acc.sudo().course_id.subjects_ids:
                subjects_in_course.append(subject_in_course)
            if acc.sudo().course_id.parent_id:
                for subject_in_parent in acc.sudo().course_id.parent_id.subjects_ids:
                    subjects_in_course.append(subject_in_parent)
            # print(acc)
            # print(acc.sudo().course_id.name)
            for sem in acc.accum_semesters_ids:
                # print(sem)
                if sem.transferred == False:
                    for sub in sem.accum_semesters_subjects_ids:
                        # print(sub.subject_id)
                        for course_subject in subjects_in_course:
                            # print(course_subject)
                            if sub.subject_id.id == course_subject.id:
                                # print('____ in student')
                                # if course_subject.subject_passpercentage:
                                #     degree = int(course_subject.subject_passpercentage)
                                # else:
                                #     degree = 60
                                if sub.final_grade and sub.final_grade.pass_grade:  # / course_subject.subject_total * 100 >= degree:
                                    print('_____PASSED')
                                    if course_subject.id not in taken_subjects:
                                        taken_subjects.append(course_subject.id)
    
                                    if course_subject.subject_type == 'compulsory':
                                        core_hours += course_subject.subject_credithours
                                    elif course_subject.subject_type == 'elective':
                                        elec_hours += course_subject.subject_credithours
                                    elif course_subject.subject_type == 'project':
                                        project_hours += course_subject.subject_credithours

        ###################################
        ##### Subjects to select from #####
        ###################################
        # print(course_subjects_j[0])
        subjects = []
        subjects_j = []
        action_plan = False
        if calendar_j:
            action_plan = request.env['hue.gpa.calculator'].sudo().search(
                [('student_id', '=', student_j['id']), ('suggested_plan_ids', '!=', False),
                 ('academic_year_id', '=', calendar_j['academic_year'][0]),
                 ('semester_id', '=', calendar_j['semester'][0])])

        if action_plan  :   #and request.env.ref('hr_extention.group_service_manager') not in user.groups_id
            # print('33333333333333333333333333333333333')
            ap_subjects = []
            if not admin_user:  # and not adviser
                all_subjects = []

            for ap in action_plan.suggested_plan_ids:
                ap_subjects.append(ap.subject_id.id)
                if ap.subject_id not in all_subjects:
                    all_subjects.append(ap.subject_id)
            for subject in all_subjects:
                # if subject.id not in taken_subjects:
                if subject.id in ap_subjects:
                    take = True
                    if (admin_user) and subject.id not in ap_subjects:  # or adviser
                        for course_subject in course_subjects_j:
                            if course_subject['subject_id'][0] == subject.id:
                                # print('_-_-_-_ AP')
                                pre_count = 0
                                for prereq in prerequisites_j:
                                    if prereq['id'] == subject.id and prereq['pre'] in taken_subjects:
                                        pre_count += 1
                                    if prereq['id'] == subject.id and prereq['pre'] not in taken_subjects:
                                        # print('___No Add___')
                                        take = False
                                if int(course_subject['prerequisites_count']) != 0 and pre_count >= int(
                                        course_subject['prerequisites_count']):
                                    take = True
                    if take:
                        # print('__Add__')
                        subjects.append(subject)
                        subjects_j.append(subject.read())

        else:
            # print("111111111111111111111111111111111111111111111")
            # print("all_subjects:--------------", all_subjects)
            # print("taken_subjects:--------------------", taken_subjects)
            for subject in all_subjects:
                if subject.id not in taken_subjects:
                    take = True
                    # print('323232323232323232323232323')
                    allsubjects = []
                    for sub in stu_course.subjects_ids:
                        allsubjects.append(sub)
                    for subp in stu_course.parent_id.subjects_ids:  
                        allsubjects.append(subp)
                    for course_subject in allsubjects:
                        if course_subject.id == subject.id:
                            # print('_-_-_-_')
                            # print(prerequisites_j)
                            pre_count = 0
                            if request.env.ref('HUE_openeducat_core.group_service_manager') in user.groups_id:
                                take = True
                            else:                                
                                for prereq in prerequisites_j:                                    
                                    if prereq['id'] == subject.id and prereq['pre'] in taken_subjects:
                                        pre_count += 1
                                    if prereq['id'] == subject.id and prereq['pre'] not in taken_subjects:
                                        print('___No Add___')
                                        take = False
                                if int(course_subject['prerequisites_count']) != 0 and pre_count >= int(
                                        course_subject['prerequisites_count']):
                                    take = True
                        # print(course_subject['subject_id'][0])
                        # print(subject.id)
                    if take:
                        # print('__Add__')
                        subjects.append(subject)
                        subjects_j.append(subject.read())
        # print("subjects:-----------------------------------------", subjects)
        #############################################
        ################### level ###################
        #############################################
        min_hours = 0
        max_hours = 0
        # print(course_loadhourslevels_ids_j)
        if calendar_j:
            for lev in course_loadhours_ids_j:
                try:
                    student_lev_int = request.env['op.levels'].sudo().search([('name','=', student_j['level'][1])], limit=1).name
                    # print("student_lev_int:-------", student_lev_int)
                    # print("lev['level_id'][1]:----------------", lev['level_id'][1])
                    # print("student_j['level'][1].split()[1]:---------------------", student_j['level'])#[1].split()[1]
                    # print("calendar_j['semester'][0]:-----------------------", calendar_j['semester'][0])
                    # print("int(lev['semester_id'][0]):----------", int(lev['semester_id'][0]))
                    # print("float(lev['gpa_from']):----------", float(lev['gpa_from']))
                    # print("float(student_j['new_gpa']):-----------------",float(student_j['new_gpa']))
                    # print("float(lev['gpa_to']:----------------", float(lev['gpa_to']))
                    if str(lev['level_id'][1]) == str(student_lev_int) and calendar_j['semester'][
                        0] == int(lev['semester_id'][0]) and float(lev['gpa_from']) <= float(
                            student_j['new_gpa']) < float(lev['gpa_to']):
                        print('________________')
                        print("lev:------------------------------", lev)
                        min_hours = lev['hours_from']
                        max_hours = lev['hours_to']
                    elif float(lev['gpa_to']) == 4 and int(lev['level_id'][1]) == int(student_lev_int) and calendar_j['semester'][0] == int(
                            lev['semester_id'][0]) and float(lev['gpa_from']) <= float(student_j['new_gpa']) <= float(
                            lev['gpa_to']):
                        print('________________4')
                        min_hours = lev['hours_from']
                        max_hours = lev['hours_to']
                    
                except:
                    print("-------------------------------pass")
                    pass
        print("min_hours:------------------------------", min_hours)
        print("max_hours:------------------------------", max_hours)
        partner = student.partner_id
        domain = [
            ('invoice_type', 'in', ['out_invoice']),
            ('invoice_date_due', '<=', date.today()),

            ('partner_id', '=', partner.commercial_partner_id.id),
            ('state', 'in', ['draft'])
        ]
        invoice_count = request.env['account.move'].sudo().search_count(domain)
        if invoice_count > 0:
            closed_invoice = True
        # print(student_j)
        ##################
        #this fixed max_hours Added for test remove after testing
        # max_hours = 100
        data = {'student': student_j,
                'student_obj': student,
                'academic_year': academic_year,
                'semester': semester,
                'stu_course': stu_course_j,
                'batch': batch,
                'batch2': batch2,
                'sessions': sessions,
                'subjects': subjects,
                'core_hours': core_hours,
                'elec_hours': elec_hours,
                'project_hours': project_hours,
                'closed': closed,
                'closed_invoice': closed_invoice,
                'min_hours': min_hours or 0,
                'max_hours': max_hours or 0,
                'admin_user': admin_user,
                'adviser': adviser,
                }

        return data

    ###########################################################################################
    ###########################################################################################
    ###########################################################################################

    # def dumps(self, obj):
    #     return json.dumps(obj, cls=json.JSONEncoder).encode('utf-8')
    #
    # def loads(self, data):
    #     return json.loads(data.decode('utf-8'), object_hook=serialize_hook)

    ###################################################################################################
    #########################################  Course Subjects  #######################################
    ###################################################################################################
    def _get_course_subject(self, course_id, subject_id):
        co_subject = request.env['op.subject'].sudo().search([
            ('course_id', '=', int(course_id[0]['id'])),
            ('id', '=', int(subject_id)),
        ])
        if not co_subject:
            print('______======')
            if course_id[0]['parent_id']:
                co_subject = request.env['op.subject'].sudo().search([
                    ('course_id', '=', int(course_id[0]['parent_id'][0])),
                    ('id', '=', int(subject_id)),
                ])
        if not co_subject:
            print(subject_id)
        return co_subject
    
    def _get_group(self):
        if request.env.ref('HUE_openeducat_core.group_service_manager') in request.env.user.groups_id:
            return True
        else :
            return False
    
    ##################################open reg button ###############################
    def get_user(self, student_id):
        security=0
        if request.env.ref('HUE_openeducat_core.group_service_manager') in request.env.user.groups_id:
            security=1
        else :
            employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
            print("employee_id:----------", employee_id)
            faculty = request.env['op.faculty'].sudo().search([('emp_id', '=', employee_id.id)], limit=1)
            print("faculty:--------------", faculty)
            hue_direction_lines = request.env['hue.academic.direction.line'].sudo().search([
                ('to_date', '=', False),('faculty_id', '=',faculty.id),('student_id', '=',  student_id)])
            if hue_direction_lines :
                security=1
            else :
                security=0
        print("security:----", security)
        return security

    ###########################################################################################
    ##################################### Is Registered #######################################
    ###########################################################################################

    def _is_reg(self, batch_id, student_id, session_id):
        stu_reg = request.env['hue.student.registration'].sudo().search([
            ('batch_id', '=', int(batch_id)),
            ('student_id', '=', int(student_id)),
            ('session_id', '=', int(session_id)),
        ], limit=1)
        # print(batch_id)
        # print(student_id)
        # print(session_id)
        # print(stu_reg)
        if stu_reg:
            return stu_reg
        else:
            return False

    ###################################################################################################
    ########################################  Registered Hours  #######################################
    ###################################################################################################

    def _get_invoiced_reg_hours(self, rdata):
        if rdata['batch']:
            regs = request.env['hue.student.registration'].sudo().search(
                [('batch_id', '=', rdata['batch'].id), ('student_id', '=', rdata['student']['id'])])
            hours = 0
            subjects = []
            for reg in regs:
                co_subject = self._get_course_subject(rdata['stu_course'], reg.session_id.subject_id.id)
                if co_subject and co_subject.id not in subjects:
                    if not co_subject.subject_credithours_invoice:
                        hours += co_subject.subject_credithours
                    subjects.append(co_subject.id)
            return hours

    def _get_reg_hours(self, rdata):
        if rdata['batch']:
            regs = request.env['hue.student.registration'].sudo().search(
                [('batch_id', '=', rdata['batch'].id), ('student_id', '=', rdata['student']['id'])])
            hours = 0
            subjects = []
            for reg in regs:
                # print('============================================ Registered Hours')
                co_subject = self._get_course_subject(rdata['stu_course'], reg.session_id.subject_id.id)
                if co_subject and co_subject.id not in subjects:
                    hours += co_subject.subject_credithours
                    subjects.append(co_subject.id)
                # print(session.start_datetime)
                # print(session.end_datetime)
                # print(reg.session_id.start_datetime)
                # print(reg.session_id.end_datetime)
            # print(hours)
            return hours

    ###########################################################################################
    #####################################  Check Conflict  ####################################
    ###########################################################################################

    def _check_reg(self, rdata, session, post, check_all=True, sessions=False):
        # if sessions:
        #     for session in sessions:
        #         if post['subject'] + '_' + str(session.id) in post and post[post['subject'] + '_' + str(session.id)] == str(session.id):
        #
        #             pass

        regs = request.env['hue.student.registration'].sudo().search(
            [('batch_id', '=', rdata['batch'].id), ('student_id', '=', rdata['student']['id'])])
        accept = 'OK'
        subjects = []
        for reg in regs:
            if reg.session_id.subject_id.id not in subjects:
                subjects.append(reg.session_id.subject_id.id)

        for reg in regs:
            # print('============================================ check')
            if reg.status == 'Approved' and not rdata['admin_user'] and not rdata['adviser']:
                accept = 'The Registration already Approved and can not be modified! Please contact your adviser'
                return accept

            reg_hours = self._get_reg_hours(rdata)
            if session.subject_id.id not in subjects:
                co_subject = self._get_course_subject(rdata['stu_course'], session.subject_id.id)
                user = request.env['res.users'].sudo().browse(request.uid)
                if check_all and reg_hours + co_subject.subject_credithours > rdata['max_hours'] and request.env.ref(
                        'HUE_openeducat_core.group_service_manager') not in user.groups_id:
                    print("check_reg rdata['max_hours']", rdata['max_hours'])
                    accept = 'Can not register to Session "' + session.name + '". Max hours Reached!'
                    return accept

            if check_all and reg.session_id.id != session.id:
                if (reg.session_id.start_datetime <= session.start_datetime < reg.session_id.end_datetime) or (
                        reg.session_id.start_datetime < session.end_datetime <= reg.session_id.end_datetime) or (
                        reg.session_id.start_datetime >= session.start_datetime and session.end_datetime >= reg.session_id.end_datetime) or (
                        reg.session_id.start_datetime <= session.start_datetime and session.end_datetime <= reg.session_id.end_datetime):
                    # print('------------ conflict')
                    accept = 'Can not register to Session "' + session.name + '" due to conflict with Session: "' + reg.session_id.name + '"'
                    return accept

            if session.student_count - session.reg_student_count < 0:  # and reg.status == 'Draft'
                accept = 'Can not register to Session "' + session.name + '". No place! Session is full.'
                return accept
            # print('============================================ check')
        return accept

    ###########################################################################################
    ##########################################  Save  #########################################
    ###########################################################################################

    def _save_reg(self, rdata, post, sessions):
        err = False
        registers = []
        session_types = []
        reg_session_types = []
        all_reg_session_types = []
        if 'subject' in post:
            subject_id = post['subject']
            stu_sess = []
            if rdata['batch'] and subject_id:

                for session in sessions:

                    if session.session_type not in session_types:
                        session_types.append(session.session_type)
                    stu_reg = request.env['hue.student.registration'].sudo().search([
                        ('batch_id', '=', rdata['batch'].id),
                        ('student_id', '=', rdata['student']['id']),
                        ('session_id', '=', session.id), ], limit=1)

                    # print(post['subject'])
                    if post['subject'] + '_' + str(session.id) in post:
                        all_reg_session_types.append(session.session_type)
                    # print("dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd")
                    if post['subject'] + '_' + str(session.id) in post and post[
                        post['subject'] + '_' + str(session.id)] == str(session.id):
                        # print('||||||||||||||')

                        if not stu_reg:
                            # print('|||||||||||||| CREATE')
                            check_session = self._check_reg(rdata, session, post, True, sessions)
                            if check_session == 'OK':

                                registers.append({'batch_id': rdata['batch'].id, 'student_id': rdata['student']['id'],
                                                  'session_id': session.id, 'status': 'Draft'})
                                if session.session_type not in reg_session_types:
                                    reg_session_types.append(session.session_type)
                            else:
                                err = check_session
                                # all_reg_session_types.append(session.session_type)
                                return check_session
                        elif stu_reg:
                            if session.session_type not in reg_session_types:
                                reg_session_types.append(session.session_type)
                    else:
                        # all_reg_session_types.append(session.session_type)
                        # print("@#############################################################")
                        # print("@#############################################################")
                        # print("@#############################################################")
                        # print(reg_session_types)
                        # print(session_types)nn
                        # for stype in session_types:
                        #     if stype not in reg_session_types:
                        #         return 'Please select all types of sessions!'

                        if stu_reg.status == 'Draft' or stu_reg.status == 'Pending' or rdata['admin_user'] or rdata[
                            'adviser']:
                            print('|||||||||||||| DELETE |||||||||||||||||||')

                            stu_reg.unlink()
                            request.env.cr.commit()

        if not err:
            print(reg_session_types)
            print(session_types)

            for stype in session_types:
                if stype not in reg_session_types:
                    return 'Please select all types of sessions!'

            for register in registers:
                request.env['hue.student.registration'].sudo().create(register) 
            request.env.cr.commit()

            return 'OK'
            
        else:
            return err

    ###########################################################################################
    #######################################  Finish  ##########################################
    ###########################################################################################
    def _finish_reg(self, rdata, post):
        # ret = self._save_reg(rdata, post)
        # if ret != 'OK':
        #     return ret
        reg_hours = self._get_reg_hours(rdata)
        # print("reg_hours:----------------------", reg_hours)
        stu_regs_count = int(self._get_invoiced_reg_hours(rdata))
        # print("stu_regs_count:---------------------------", stu_regs_count)
        # print('============================')
        # print(reg_hours)
        # print(rdata['min_hours'])
        user = request.env['res.users'].sudo().browse(request.uid)
        if int(reg_hours) != 0 and int(reg_hours) < int(rdata['min_hours']) and not rdata['admin_user'] and request.env.ref(
                'HUE_openeducat_core.group_service_manager') not in user.groups_id:
            return 'Sorry, Can not Finish registration. Minimum hours is Not Reached!'

        # if rdata['admin_user'] or rdata['adviser']:
        # print('____________________ Finish Registration')
        stu_regs = request.env['hue.student.registration'].sudo().search([
            ('batch_id', '=', rdata['batch'].id),
            ('student_id', '=', rdata['student']['id']),
        ])
        # stu_regs_count = []
        stu_regs_subject = []
        for reg in stu_regs:
            stu_regs_subject.append(reg.session_id.subject_id.id)
        stuAccID = request.env['op.student.accumulative'].sudo().search(
            [('student_id', '=', rdata['student']['id']), ('course_id', '=', rdata['batch'].course_id.sudo().id),
             ('academicyear_id', '=', rdata['batch'].academic_year.sudo().id)], limit=1)
        if stuAccID:
            StuAccSemID = request.env['op.student.accumlative.semesters'].sudo().search(
                [('student_accum_id', '=', stuAccID.sudo().id),
                 ('semester_id', '=', rdata['batch'].semester.sudo().id)])
            if StuAccSemID:
                stuSemSubIDs = request.env['op.student.semesters.subjects'].sudo().search(
                    [('student_semester_id', '=', StuAccSemID.sudo().id)])
                for stuSemSub_obj in stuSemSubIDs:
                    if stuSemSub_obj.subject_id.id not in stu_regs_subject :
                        stuSemSub_obj.sudo().unlink()
                # if not StuAccSemID.accum_semesters_subjects_ids :
                #     StuAccSemID.sudo().unlink()
        sessions = []
        for reg in stu_regs:
            # if reg.session_id.subject_id.id not in stu_regs_count:
            #     stu_regs_count.append(reg.session_id.subject_id.id)
            print(reg)
            print(request.env.user.id)
            print(request.env.user.id)
            print(request.env.user.id)

            print('AEAFEEEEEEEEEEEEEESSSSSSSSSSSSSSSSSSSSsss')
            if reg.session_id.id not in rdata['student_obj'].session_ids.ids:
                check_session = self._check_reg(rdata, reg.session_id, post, False, False)
                if check_session != 'OK':
                    return check_session
            if rdata['admin_user'] or rdata['adviser']:
                reg.status = 'Approved'
                print('11111111155555555555555551111111111')
                stuAccID = request.env['op.student.accumulative'].sudo().search(
                    [('student_id', '=', rdata['student']['id']), ('course_id', '=', rdata['batch'].course_id.id),
                     ('academicyear_id', '=', rdata['batch'].academic_year.id)], limit=1)
                if not stuAccID:
                    stuAccID = request.env['op.student.accumulative'].sudo().create(
                        {'student_id': rdata['student']['id'], 'course_id': rdata['batch'].course_id.id,
                         'academicyear_id': rdata['batch'].academic_year.id})

                StuAccSemID = request.env['op.student.accumlative.semesters'].sudo().search(
                    [('student_accum_id', '=', stuAccID.id), ('semester_id', '=', rdata['batch'].semester.id)])

                if not StuAccSemID:
                    StuAccSemID = request.env['op.student.accumlative.semesters'].sudo().create(
                        {'student_accum_id': stuAccID.id, 'academicyear_id': rdata['batch'].academic_year.id,
                         'semester_id': rdata['batch'].semester.id, 'semester_status': 2})
                    # StuAccSemID.student_id.write({'timestamp':StuAccSemID.create_date })
                stuSemSubID = request.env['op.student.semesters.subjects'].sudo().search(
                    [('student_semester_id', '=', StuAccSemID.id), (
                    'subject_id', '=', self._get_course_subject(rdata['stu_course'], reg.session_id.subject_id.id).id)])
                print(stuSemSubID.approved_by)
                print('2222222222222222222222222222222222')

                if not stuSemSubID:
                    request.env['op.student.semesters.subjects'].sudo().create(
                        {'approved_by': request.env.user.id, 'student_semester_id': StuAccSemID.id,
                         'subject_id': self._get_course_subject(rdata['stu_course'], reg.session_id.subject_id.id).id})

                # print(StuAccSemID)
                # print(stuSemSubID)
            else:
                reg.status = 'Pending'
            request.env.cr.commit()
            sessions.append(reg.session_id.id)
        # if sessions:
        print("sessions")
        print(sessions)
        #add registered sessions to student
        rdata['student_obj'].session_ids = [(6, 0, sessions)]
        #Add the same odoo calendar sessions to the same student
        for sess in sessions:
            event = request.env['calendar.event'].search([('session_id','=',int(sess))])
            if event:
                event_partners = event.partner_ids.ids
                student_partner = rdata['student_obj'].partner_id.id
                event_partners.append(student_partner)
                event.partner_ids = [(6, 0, event_partners)]
        request.env.cr.commit()
        if rdata['batch'].allow_registration_invoicing:
            print("sessions")
            term_id = request.env['op.academic.term'].sudo().search([('id', '=', 29)], limit=1).id
            inv_obj = request.env['account.move']
            partner_id = request.env['op.student'].sudo().search([('id', '=', rdata['student']['id']),
                                                                  ], limit=1).partner_id
            invoice_draft = inv_obj.sudo().search(
                [('state', '=', 'draft'), ('partner_id', '=', partner_id.id), ('academic_term', '=', term_id),
                 ])
            invoice_open = inv_obj.sudo().search(
                [('state', '=', 'posted'), ('partner_id', '=', partner_id.id), ('academic_term', '=', term_id),
                 ('payment_state', '=', 'not_paid')])
            invoice_paid = inv_obj.sudo().search(
                [('state', '=', 'posted'), ('partner_id', '=', partner_id.id), ('academic_term', '=', term_id),
                 ('payment_state', '=', 'paid')])
            if invoice_draft:
                for draft in invoice_draft:
                    draft.unlink()
            if invoice_open:
                for open in invoice_open:
                    open.sudo().action_invoice_cancel()
            if invoice_paid:
                invoice_paid_qty = 0
                refund_paid_qty = 0
                for inv_paid in invoice_paid:
                    if inv_paid.move_type == 'out_invoice':
                        invoice_paid_qty = invoice_paid_qty + inv_paid.invoice_line_ids[0].quantity
                    if inv_paid.move_type == 'out_refund':
                        refund_paid_qty = refund_paid_qty + inv_paid.invoice_line_ids[0].quantity
                total_qty = invoice_paid_qty - refund_paid_qty
                if total_qty == stu_regs_count:
                    stu_regs_count = 0
                elif total_qty > stu_regs_count:
                    stu_regs_count = total_qty - stu_regs_count
                    invoice_lines = []
                    account_id = False
                    product = rdata['batch'].product_id

                    if not account_id:
                        account_id = product.property_account_income_id.id
                    elif product.id:
                        account_id = product.categ_id.property_account_income_categ_id.id
                    if not account_id:
                        raise UserError(
                            _('There is no income account defined for this product: "%s". \
                               You may have to install a chart of account from Accounting \
                               app, settings menu.') % (product.name,))
                    invoice_lines.append((0, 0, {'name': product.name, 'account_id': account_id,
                                                 'price_unit': product.lst_price, 'quantity': stu_regs_count,
                                                 'product_id': product.id}))

                    stu_regs_count = 0
                elif total_qty < stu_regs_count:
                    stu_regs_count = stu_regs_count - total_qty

            # partner_id = partner_id
            if stu_regs_count > 0:
                invoice_lines = []
                account_id = False
                product = rdata['batch'].product_id

                if not account_id:
                    account_id = product.property_account_income_id.id
                elif product.id:
                    account_id = product.categ_id.property_account_income_categ_id.id
                if not account_id:
                    raise UserError(
                        _('There is no income account defined for this product: "%s". \
                           You may have to install a chart of account from Accounting \
                           app, settings menu.') % (product.name,))
                invoice_lines.append((0, 0, {'name': product.name, 'account_id': account_id,
                                             'price_unit': product.lst_price, 'quantity': stu_regs_count,
                                             'product_id': product.id}))
                invoice = inv_obj.sudo().create({
                    # 'name': self.name,
                    'origin': rdata['batch'].name,
                    'invoice_type': 'summer',
                    'is_application': 0,
                    'move_type': 'out_invoice',
                    'academic_year': rdata['batch'].sudo().academic_year.id,
                    'academic_term': term_id,
                    'date_invoice': datetime.today(),
                    'reference': False,
                    'account_id': partner_id.property_account_receivable_id.id,
                    'partner_id': partner_id.id,
                    'invoice_line_ids': invoice_lines,
                })

        date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        stuAccID = request.env['op.student'].sudo().search(
                    [('id', '=', rdata['student']['id'])], limit=1)
        stuAccID.write({'timestamp':date_now })
        if rdata['admin_user'] or rdata['adviser']:
            if rdata['admin_user']:
                registerer = 'Admin'
            else:
                registerer = 'Adviser'
            request.env['hue.student.registration.log'].sudo().create(
                {'batch_id': rdata['batch'].id, 'student_id': rdata['student']['id'], 'session_ids': [(6, 0, sessions)],
                 'status': 'Approved', 'registerer': registerer, 'user_id': request.uid, 'update_time': datetime.now()})
        else:
            request.env['hue.student.registration.log'].sudo().create(
                {'batch_id': rdata['batch'].id, 'student_id': rdata['student']['id'], 'session_ids': [(6, 0, sessions)],
                 'status': 'Pending', 'registerer': 'Student', 'user_id': request.uid, 'update_time': datetime.now()})
        # send mail
        auth_id = request.env['res.users'].sudo().search([('id', '=',1)])
        advisor_mail_cc = request.env['res.users'].sudo().browse(request.uid)
        std_mail_to = request.env['op.student'].sudo().search([('id', '=', rdata['student']['id'])], limit=1).user_id
        mail_content = "Your registration has been confirmed , Please check your timetable , Thank you ..."
        main_content = {
            'subject': ('Registration Request Approve'),
            'author_id':  auth_id.partner_id.id,
            'body_html': mail_content,
            'email_from' : "Regadmin@horus.edu.eg",
            'email_to': std_mail_to.login,
            'email_cc':advisor_mail_cc.login,
            'state': 'outgoing',
            'message_type': 'email',            
        }
        email_send= request.env['mail.mail'].sudo().create(main_content).send()
        return 'OK'
    ###########################################################################################
    ################################## Registration reject #####################################
    ###########################################################################################
    def rejected_registration(self, rdata, post):
        auth_id = request.env['res.users'].sudo().search([('id', '=',1)])
        advisor_mail_cc = request.env['res.users'].sudo().browse(request.uid)
        std_mail_to = request.env['op.student'].sudo().search(
            [('id', '=', rdata['student']['id'])], limit=1).user_id
        mail_content = "Your registration has been rejected , please contact your advisor ..."
        main_content = {
            'subject': ('Registration Request Rejection'),
            'author_id': auth_id.partner_id.id,
            'body_html': mail_content,
            'email_from' : "Regadmin@horus.edu.eg",
            'email_to': std_mail_to.login,
            'email_cc':advisor_mail_cc.login,
            'state': 'outgoing',
            'message_type': 'email',            
        }
        email_send= request.env['mail.mail'].sudo().create(main_content).send()
        if email_send :
            return 'OK'
        else:
            return "False"
        
    ###########################################################################################
    ################################## Registration start #####################################
    ###########################################################################################
    @http.route(['/registration',
                 '/my/registration/<student_id>', '/registration/<student_id>'],
                type='http', auth='public', website=True)
    def start_reg(self, student_id=None, **post):
        err_msg = ''
        request.session['rdata'] = False
        if 'rdata' in request.session and request.session['rdata']:
            rdata = request.session['rdata']
        else:
            rdata = self._get_data(student_id)
        sessions = []
        if 'subject' in post:
            subject_id = post['subject']
            if subject_id:
                if rdata['batch2']:
                    sessions = request.env['op.session'].sudo().search([
                        ('subject_id', '=', int(subject_id)),
                        '|',
                        ('batch_id', '=', rdata['batch'].id),
                        ('batch_id', '=', rdata['batch2'].id),
                        ('start_datetime', '>=', rdata['batch'].default_week_start),
                        ('end_datetime', '<=', str(rdata['batch'].default_week_end) + ' 23:59:59'),
                    ], order="classroom_id, sub_classroom")
                elif rdata['batch']:
                    sessions = request.env['op.session'].sudo().search([
                        ('subject_id', '=', int(subject_id)),
                        ('batch_id', '=', rdata['batch'].id),
                        ('start_datetime', '>=', rdata['batch'].default_week_start),
                        ('end_datetime', '<=', str(rdata['batch'].default_week_end) + ' 23:59:59'),
                    ], order="classroom_id, sub_classroom")

            if 'button_save' in post:
                ret = self._save_reg(rdata, post, sessions)
                if ret != 'OK':
                    err_msg = ret
            elif 'button_finish' in post:
                ret = self._finish_reg(rdata, post)
                if ret != 'OK':
                    err_msg = ret
            elif 'rejected_registration' in post:
                ret = self.rejected_registration(rdata, post)
                if ret != 'OK':
                    err_msg = ret
        reg_hours = self._get_reg_hours(rdata)

        approved = False
        reg_sess = []
        subjects = []
        # print('_________________    ________________')
        # print(rdata['batch'])
        if rdata['batch']:
            registered = request.env['hue.student.registration'].sudo().search(
                [('batch_id', '=', rdata['batch'].id), ('student_id', '=', rdata['student']['id'])])
            reg_sess_ids = []
            for register in registered:
                if register.status == 'Approved' and not rdata['admin_user'] and not rdata['adviser']:
                    approved = True
                reg_sess_ids.append(register.session_id.id)
                if register.session_id.subject_id.id not in subjects:
                    subjects.append(register.session_id.subject_id.id)
            reg_sess = request.env['op.session'].sudo().search([('id', 'in', reg_sess_ids)], order='start_datetime')

        data = {'data': rdata,
                'post': post,
                'err_msg': err_msg,
                'sessions': sessions,
                'reg_sess': reg_sess,
                'subjects': subjects,
                '_is_reg': self._is_reg,
                'student_id': student_id,
                '_get_course_subject': self._get_course_subject,
                '_get_group' :self._get_group ,
                'get_user' :self.get_user,
                'reg_hours': reg_hours,
                'active': 'registration',
                'approved': approved,
                }
        return request.render('hue_register.registration', data)


