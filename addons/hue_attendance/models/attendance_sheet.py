from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import ValidationError


class OPAttendanceLineExt(models.Model):
    _inherit = 'op.attendance.sheet'


    name = fields.Char(compute='_compute_name', string='Name', store=True, required=False, size=32)
    total_present = fields.Integer('Total Present', compute='_compute_total_present',tracking=True)
    total_absent = fields.Integer('Total Absent', compute='_compute_total_absent',tracking=True)
    
    def action_open_kiosk_url(self):
        action = self.env.ref('hr_attendance.open_kiosk_url').read()[0]
        # Ensure that you have the correct model name
        action['domain'] = [('id', '=', self.id)]
        return action
    
    def attendance_scan(self, barcode, session_id):
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        student = self.env['op.student'].search([('barcode', '=', barcode)], limit=1)
        if not student:
            return {'success': False, 'error': 'Student not found'}
        sheet = self.search([('session_id', '=', session_id), ('student_id', '=', student.id)], limit=1)
        if not sheet:
            return {'success': False, 'error': 'Student not registered for this session'}
        # sheet.write({'check_in': fields.Datetime.now()})
        print("success:11111111111111111111111111111111111111111111")
        return {'success': True}
    
    @api.depends('attendance_line.present')
    def _compute_total_present(self):
        for record in self:
            record.total_present = self.env['op.attendance.line'].search_count(
                [('present', '=', True), ('attendance_id', '=', record.id)])


    @api.depends('attendance_line.present')
    def _compute_total_absent(self):
        for record in self:
            record.total_absent = self.env['op.attendance.line'].search_count(
                [('present', '=', False), ('attendance_id', '=', record.id)])
    
    
    @api.depends('session_id')
    def _compute_name(self):
        for session in self:
            active_session = self.env.context.get('active_id')
            if active_session:
                session.session_id = active_session
                sess_obj = self.env['op.session'].search([('id', '=', active_session)], limit=1)
                register = self.env['op.attendance.register'].search(
                    [('course_id', '=', sess_obj.course_id.id),
                     ('batch_id', '=', sess_obj.batch_id.id)], limit=1)
                if register:
                    session.register_id = register.id
                    
            if session.session_id:
                session.name = str(session.session_id.classroom_id.name)+str(session.session_id.sub_classroom)+' '+str(session.session_id.session_date) + ' ' + str(session.session_id.sudo().timing_id.name) + ' ' + str(session.session_id.sudo().subject_id.name)
            else:
                session.name = ''


    @api.model
    def attendance_scan(self, barcode, active_id):
        """ Receive a barcode scanned from the Kiosk Mode and change the attendances of corresponding employee.
            Returns either an action or a warning.
        """
        sheet_browse = self.env['op.attendance.sheet'].browse(int(active_id))
        emp = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)])
        # print(sheet_browse)
        student = self.env['op.student'].search([('student_code', '=', barcode)], limit=1)
        if not student:
            return     {'warning': _('No student corresponding to barcode %(barcode)s') % {'barcode': barcode}}
        else:
            # print(sheet_browse.register_id.batch_id.default_week_start)
            session = self.env['op.session'].search([('start_datetime', '>=', sheet_browse.register_id.batch_id.default_week_start + ' 00:00:00'), ('start_datetime', '<=', sheet_browse.register_id.batch_id.default_week_end + ' 23:59:59'), ('course_id', '=', sheet_browse.register_id.course_id.id), ('batch_id', '=', sheet_browse.register_id.batch_id.id), ('type', '=', sheet_browse.session_id.type), ('timing_id', '=', sheet_browse.session_id.timing_id.id), ('to_timing_id', '=', sheet_browse.session_id.to_timing_id.id), ('classroom_id', '=', sheet_browse.session_id.classroom_id.id), ('sub_classroom', '=', sheet_browse.session_id.sub_classroom), ('facility_id', '=', sheet_browse.session_id.facility_id.id)], limit=1)
            # print(session)
            records = self.env['op.student'].search([('session_ids', '=', session.id)])
            # print(student)
            # print(records)
            if student in records:
                action_message = self.env.ref('hue_attendance.action_kiosk_mode').read()[0]
                action_message['previous_attendance_change_date'] = 'sss'
                action_message['next_action'] = 'hue_attendance.action_kiosk_mode'
                action_message['action_date'] = fields.Datetime.now()
                action_message['active_id'] = active_id
                action_message['student_id'] = student.id
                action_message['photo_hide'] = student.photo_hide
                # action_message['view_type'] = view_type
                # action_message['model'] = model
                # action_message['action'] = action
                date = fields.Date.today()
                vals = {
                    'attendance_id': active_id,
                    'student_id': student.id,
                    'present': True,
                    'emp_id' : emp.id
                }
                already = self.env['op.attendance.line'].sudo().search([('attendance_id','=',int(active_id)),('student_id','=',student.id)],limit=1)
                # attend.write({'state':'done'})
                if not already:
                    modified_attendance =  self.env['op.attendance.line'].sudo().create(vals)
                    action_message['attendance'] = modified_attendance.read()[0]
                    action_message['employee_name'] = ' '+student.name
                    return {'action': action_message}
                else:
                    action_message['attendance'] = already.read()[0]
                    action_message['employee_name'] = 'you already check before '+student.name
                    already.present = True
                    return {'action': action_message}
            else:
                return {'warning': _('The student corresponding to barcode %(barcode)s is not in this session') % {'barcode': barcode}}


    @api.onchange('attendance_date')
    def fill_session_id(self):
        # if self.env.ref('hr_extention.group_service_manager') in self.env.user.groups_id:
        #     records = self.env['op.session'].search([('start_datetime', '>=', self.attendance_date + ' 00:00:00'), ('start_datetime', '<=', self.attendance_date + ' 23:59:59'), ('course_id', '=', self.course_id.id), ('batch_id', '=', self.batch_id.id)])
        # else:
        emp = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
        fuc = self.env['op.faculty'].sudo().search([('emp_id', '=', emp.id)], limit=1)
        print("fuc", fuc)
        records = self.env['op.session'].search([
            ('start_datetime', '>=', str(self.attendance_date) + ' 00:00:00'),
            ('start_datetime', '<=', str(self.attendance_date) + ' 23:59:59'),
            ('course_id', '=', self.course_id.id),
            ('batch_id', '=', self.batch_id.id),
            ('faculty_ids', '=', fuc.id)
        ])
        self.session_id = records.ids
        
        
    @api.onchange('register_id')
    def fill_session_id2(self):
        if self.attendance_date:
            # if self.env.ref('hr_extention.group_service_manager') in self.env.user.groups_id:
                # records = self.env['op.session'].search([('start_datetime', '>=', self.attendance_date + ' 00:00:00'), ('start_datetime', '<=', self.attendance_date + ' 23:59:59'), ('course_id', '=', self.course_id.id), ('batch_id', '=', self.batch_id.id)])
            # else:
            emp = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
            fuc = self.env['op.faculty'].sudo().search([('emp_id', '=', emp.id)], limit=1)

            records = self.env['op.session'].search([('start_datetime', '>=', str(self.attendance_date) + ' 00:00:00'), ('start_datetime', '<=', str(self.attendance_date) + ' 23:59:59'), ('course_id', '=', self.course_id.id), ('batch_id', '=', self.batch_id.id), ('faculty_ids', '=', fuc.id)])

            domain = {'session_id': [('id', 'in', records.ids)]}
            return {'domain': domain}


    def clear_sessions(self):
        sessions = self.env['op.session'].search([('start_datetime', '>=', '2020-02-08 00:00:00'), ('start_datetime', '<=', '2020-02-14 23:59:59'), ('student_ids', '=', False)])
        print('===========================')
        print(sessions)
        # sessions.unlink()
        
        cnt = 0
        for session in sessions:
            print(session.name)
            died_sessions = self.env['op.session'].search([('course_id', '=', session.course_id.id), ('batch_id', '=', session.batch_id.id), ('type', '=', session.type), ('session_type', '=', session.session_type), ('timing_id', '=', session.timing_id.id), ('to_timing_id', '=', session.to_timing_id.id), ('classroom_id', '=', session.classroom_id.id), ('sub_classroom', '=', session.sub_classroom), ('facility_id', '=', session.facility_id.id)])
            for died_session in died_sessions:
                try:
                    # died_session.unlink()
                    cnt = cnt  + 1
                    print('..........')
                    print(cnt)
                    print('..........')
                except:
                    continue
        if cnt == 0:
            raise ValidationError(sessions)
        print(sessions)


    def attendance_done(self):
        all_attends = self.env['op.attendance.line'].sudo().search([('attendance_id', '=', self.id)])
        if all_attends:
            self.state = 'done'

            session = self.env['op.session'].search([('start_datetime', '>=', self.batch_id.default_week_start + ' 00:00:00'), ('start_datetime', '<=', self.batch_id.default_week_end + ' 23:59:59'), ('course_id', '=', self.course_id.id), ('batch_id', '=', self.batch_id.id), ('type', '=', self.session_id.type), ('timing_id', '=', self.session_id.timing_id.id), ('to_timing_id', '=', self.session_id.to_timing_id.id), ('classroom_id', '=', self.session_id.classroom_id.id), ('sub_classroom', '=', self.session_id.sub_classroom), ('facility_id', '=', self.session_id.facility_id.id)], limit=1)

            records = self.env['op.student'].search([('session_ids', '=', session.id)])
            for record in records:
                vals = {
                    'attendance_id': self.id,
                    'student_id': record.id,
                    'present': False,
                }

                already = self.env['op.attendance.line'].sudo().search([('attendance_id', '=', self.id), ('student_id', '=', record.id)], limit=1)
                if not already:
                    modified_attendance = self.env['op.attendance.line'].sudo().create(vals)
        else:
            raise ValidationError("You can not close with empty attendance!")

    tree_clo_acl_ids=fields.Char()#compute="_compute_tree_clo_acl_ids",search='tree_clo_acl_ids_search'


    @api.depends('session_id')
    def _compute_tree_clo_acl_ids(self):
        print('View My Tree CLO ACL')


    def tree_clo_acl_ids_search(self, operator, operand):
        employee_id = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id), '|', ('active', '=', True), ('active', '=', False)], limit=1)
        faculty = self.env['op.faculty'].sudo().search([('emp_id', '=', employee_id.id)], limit=1)
        available_ids = []
        today = datetime.now().strftime('%Y-%m-%d')
        if self.env.ref('hr_extention.group_service_manager') in self.env.user.groups_id:
            return [('id', 'in', self.sudo().search([]).ids)]
        elif self.env.ref('__export__.res_groups_203_874eb7fa') in self.env.user.groups_id:
            return [('id', 'in', self.sudo().search([]).ids)]
        elif faculty:
            sessions = self.env['op.session'].sudo().search([('faculty_ids', '=', faculty.id), ('day_date', '=', today)])
            for session in sessions:
                # print(session.name)
                rec = self.sudo().search([('session_id', '=', session.id)])
                if not rec:
                    reg = self.env['op.attendance.register'].sudo().search([('batch_id', '=', session.batch_id.id), ('course_id', '=', session.course_id.id)])
                    if not reg:
                        reg = self.env['op.attendance.register'].sudo().create({'name': session.batch_id.name, 'code': session.batch_id.name, 'batch_id': session.batch_id.id, 'course_id': session.course_id.id})
                    rec = self.sudo().create({'register_id': reg.id, 'session_id': session.id, 'attendance_date': session.day_date, 'state': 'start'})

            records = self.sudo().search([('session_id', 'in', sessions.ids)]).ids
        else:
            raise ValidationError("Please contact system manager for related faculty!")

        return [('id', 'in', records)]


    def create_old_attendance(self, start='2020-02-07', end='2020-02-15'):
        today = datetime.now().strftime('%Y-%m-%d')
        if self.env.ref('hr_extention.group_service_manager') in self.env.user.groups_id:
            sessions = self.env['op.session'].sudo().search([('day_date', '>=', start),('day_date', '<=', end)])
            for session in sessions:
                dd = datetime.strptime(session.day_date,'%Y-%m-%d')
                print(dd.strftime("%d/%m/%Y"))
                already_sheet = self.sudo().search([('session_id', '=', session.id)])
                # if op.attendance.sheet is not exist the create it
                if not already_sheet:
                    print('___________________________ NEW SHEET _______________________________')
                    reg = self.env['op.attendance.register'].sudo().search([('batch_id', '=', session.batch_id.id), ('course_id', '=', session.course_id.id)])
                    if not reg:
                        reg = self.env['op.attendance.register'].sudo().create({'name': session.batch_id.name, 'code': session.batch_id.name, 'batch_id': session.batch_id.id, 'course_id': session.course_id.id})
                    rec = self.env['op.attendance.sheet'].sudo().create({'register_id': reg.id, 'session_id': session.id, 'attendance_date': session.day_date, 'state': 'start'})

                    # Set session_type
                    session_type = 0
                    if session.session_type == 'Lecture':
                        session_type = 2
                    elif session.session_type == 'Section':
                        session_type = 4
                    elif session.session_type == 'Lab':
                        session_type = 3

                    # create student attendances for rec
                    org_session = self.env['op.session'].search([('start_datetime', '>=', rec.register_id.batch_id.default_week_start + ' 00:00:00'), ('start_datetime', '<=', rec.register_id.batch_id.default_week_end + ' 23:59:59'), ('course_id', '=', rec.register_id.course_id.id), ('batch_id', '=', rec.register_id.batch_id.id), ('type', '=', rec.session_id.type), ('timing_id', '=', rec.session_id.timing_id.id), ('to_timing_id', '=', rec.session_id.to_timing_id.id), ('classroom_id', '=', rec.session_id.classroom_id.id), ('sub_classroom', '=', rec.session_id.sub_classroom), ('facility_id', '=', rec.session_id.facility_id.id)], limit=1)
                    records = self.env['op.student'].search([('session_ids', '=', org_session.id)])
                    for record in records:
                        present = True
                        # modify attendance
                        course_subject = self.env['op.course.subjects'].sudo().search([('course_id', '=', session.course_id.id), ('subject_id', '=', session.subject_id.id)],limit=1)
                        if course_subject:
                            absence = self.env['op.attendance'].sudo().search([('student_id', '=', record.id),  ('subject_id', '=', course_subject.id), ('acadyear', '=',session.batch_id.academic_year.id ), ('semester', '=', session.batch_id.semester.id), ('absencedate', 'ilike', '%'+dd.strftime("%d/%m/%Y")+'%'), ('attendancetype', '=', session_type)]) #('course_id', '=', session.course_id.id),
                            if absence:
                                present = False
                                print(' _____ ' + str(present))
                        print('___________________________ student ____________________________ '+str(present))
                        print(session.subject_id.id)
                        print(session.subject_id.name)
                        print(session_type)
                        print(session.batch_id.academic_year.id)
                        print(session.batch_id.semester.id)
                        print(dd.strftime("%d/%m/%Y"))
                        vals = {
                            'attendance_id': rec.id,
                            'student_id': record.id,
                            'present': present,
                        }
                        already = self.env['op.attendance.line'].sudo().search([('attendance_id', '=', rec.id), ('student_id', '=', record.id)], limit=1)
                        if already:
                            already.present = present
                        else:
                            already = self.env['op.attendance.line'].sudo().create(vals)
                    rec.state = 'done'
                    # rec.attendance_done()
                else:
                    print('__________ SHEET EXISTS _________')
    
    
    @api.model
    def close_attendance_cron(self):
        today =datetime.now().strftime('%Y-%m-%d')
        dt = '2023-03-01'
        curr_academic_year = self.env['hue.academic.years'].sudo().search([('current', '=', True)], limit=1).id
        curr_semester = self.env['op.semesters'].sudo().search([('current', '=', True)], limit=1).id
        att_sheet = self.env['op.attendance.sheet'].search([('attendance_date', '>', dt),('attendance_date', '<=', today),('attendance_line', '>=', 1),('state', '=', 'start')
            ,('batch_id.academic_year', '=', curr_academic_year),('batch_id.semester', '=', curr_semester)]) 
        for sheet in att_sheet :
            all_attends = self.env['op.attendance.line'].sudo().search([('attendance_id', '=', sheet.id)])
            if all_attends:
                sheet.state = 'done'
                session = self.env['op.session'].search([('start_datetime', '>=', sheet.batch_id.default_week_start + ' 00:00:00'),
                    ('start_datetime', '<=', sheet.batch_id.default_week_end + ' 23:59:59'), ('course_id', '=', sheet.course_id.id),
                    ('batch_id', '=', sheet.batch_id.id), ('type', '=', sheet.session_id.type), ('timing_id', '=', sheet.session_id.timing_id.id),
                    ('to_timing_id', '=', sheet.session_id.to_timing_id.id), ('classroom_id', '=', sheet.session_id.classroom_id.id),
                    ('sub_classroom', '=', sheet.session_id.sub_classroom), ('facility_id', '=', sheet.session_id.facility_id.id)], limit=1)
                records = self.env['op.student'].search([('session_ids', '=', session.id)])
                for record in records:
                    vals = {
                        'attendance_id': sheet.id,
                        'student_id': record.id,
                        'present': False,
                    }
                    already = self.env['op.attendance.line'].sudo().search([('attendance_id', '=', sheet.id), ('student_id', '=', record.id)], limit=1)
                    if not already:
                        modified_attendance = self.env['op.attendance.line'].sudo().create(vals)