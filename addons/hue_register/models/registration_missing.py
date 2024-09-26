from odoo import models, fields, api

class HUERegistrationMissing(models.Model):
    _name = 'hue.registration.missing'
    _description = 'hue.registration.missing'

    advisor = fields.Char()
    course = fields.Char()
    student_code = fields.Char()
    student_id = fields.Many2one('op.student', 'Student')
    missing_ids = fields.One2many('hue.registration.missing.subj', 'missing_id', string='Missing')


class HUERegistrationMissingSubj(models.Model):
    _name = 'hue.registration.missing.subj'
    _description = 'hue.registration.missing.subj'

    subject = fields.Char()
    type = fields.Char()
    missing_id = fields.Many2one('hue.registration.missing')
    
    
class StudentTransportIds(models.Model):
    _inherit = 'op.student'

    transport_ids = fields.One2many('hue.student.transport', 'student_id')
    
    
    @api.model
    def student_missing_registration(self, course=False):
        curr_academic_year = self.env['op.academic.year'].sudo().search([('current', '=', True)], limit=1).id
        curr_semester = self.env['op.semesters'].sudo().search([('gpa_current', '=', True)], limit=1).id
        batch_courses = self.env['op.batch'].sudo().search(
            [('semester', '=', curr_semester), ('academic_year', '=', curr_academic_year)]).ids
        if course:
            stds = self.env['op.student'].sudo().search([('course_id', '=', course)])
        else:
            stds = self.env['op.student'].sudo().search([])
        for std in stds:
            print(std.name)
            print(std.student_code)
            registration_ids = self.env['hue.student.registration'].sudo().search(
                [('batch_id', 'in', batch_courses), ('session_id.session_type', '=', 'Lecture'),
                 ('student_id', '=', std.id)])
            print(registration_ids)
            for acc in registration_ids:
                subject_id = acc.session_id.subject_id
                batch_id = acc.session_id.batch_id
                subject_registrations = self.env['hue.subject.registration'].sudo().search(
                    [('batch_id', '=', batch_id.id), ('subject_id', '=', subject_id.id)])
                for sub in subject_registrations:
                    if sub.section_hours > 0 or sub.practical_hours > 0 and sub:
                        registration_count = self.env['hue.student.registration'].sudo().search_count(
                            [('session_id.subject_id', '=', subject_id.id), ('batch_id', '=', acc.batch_id.id),
                             ('session_id.session_type', 'in', ['Section', 'Lab']), ('student_id', '=', std.id)])
                        if registration_count <= 0:
                            advisor = self.env['hue.academic.direction.line'].sudo().search(
                                [('student_id', '=', std.id), ('to_date', '=', False)],
                                limit=1).faculty_id.name

                            registration_missing = self.env['hue.registration.missing'].sudo().search(
                                [('student_id', '=', std.id)],limit=1)
                            if not registration_missing:
                                registration_missing = self.env['hue.registration.missing'].sudo().create({'student_code':std.student_code,'student_id':std.id,'course':std.course_id.name,'advisor':advisor})
                            registration_missing.missing_ids.create({'type':'Section','subject':sub.subject_id.name,'missing_id':registration_missing.id})
            registration_ids = self.env['hue.student.registration'].sudo().search(
                [('batch_id', 'in', batch_courses), ('session_id.session_type','in', ['Section', 'Lab']),
                 ('student_id', '=', std.id)])
            print(registration_ids)
            for acc in registration_ids:
                subject_id = acc.session_id.subject_id
                batch_id = acc.session_id.batch_id
                subject_registrations = self.env['hue.subject.registration'].sudo().search(
                    [('batch_id', '=', batch_id.id), ('subject_id', '=', subject_id.id)])
                for sub in subject_registrations:
                    if sub.section_hours > 0 or sub.practical_hours > 0 and sub:
                        registration_count = self.env['hue.student.registration'].sudo().search_count(
                            [('session_id.subject_id', '=', subject_id.id), ('batch_id', '=', acc.batch_id.id),
                             ('session_id.session_type','=', 'Lecture'), ('student_id', '=', std.id)])
                        if registration_count <= 0:
                            advisor = self.env['hue.academic.direction.line'].sudo().search(
                                [('student_id', '=', std.id), ('to_date', '=', False)],
                                limit=1).faculty_id.name

                            registration_missing = self.env['hue.registration.missing'].sudo().search(
                                [('student_id', '=', std.id)],limit=1)
                            if not registration_missing:
                                registration_missing = self.env['hue.registration.missing'].sudo().create({'student_code':std.student_code,'student_id':std.id,'course':std.course_id.name,'advisor':advisor})
                            registration_missing.missing_ids.create({'type':'Lecture','subject':sub.subject_id.name,'missing_id':registration_missing.id})



    def taken_accum_semesters_subjects(self, p=False):
        self.ensure_one()
        accumulative_ids = self.env['op.student.accumulative'].sudo().search([('student_id', '=', self.id)])
        core_hours = 0
        elec_hours = 0
        taken_subjects = []
        for acc in accumulative_ids:
            for sem in acc.accum_semesters_ids:
                if sem.transferred == False:
                    for sub in sem.accum_semesters_subjects_ids:
                        for course_subject in acc.sudo().course_id.course_subjects_ids:
                            if sub.subject_id.subject_id.id == course_subject.subject_id.id:
                                if course_subject.subject_passpercentage:
                                    degree = int(course_subject.subject_passpercentage)
                                else:
                                    degree = 60
                                if p and sub.subject_degree / course_subject.subject_total * 100 >= degree:
                                    if course_subject.subject_id not in taken_subjects:
                                        taken_subjects.append(sub)
                                else:
                                    taken_subjects.append(sub)
        return taken_subjects

    def student_registration(self):
        """ Open the website page with the survey form into test mode"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'name': "Start Advising",
            'target': 'self',
            'url': self.env['ir.config_parameter'].sudo().get_param('web.base.url') + "/registration/" + str(self.id)
        }
    
    
    def get_user(self):        
        security=False
        if self.env.ref('hr_extention.group_service_manager') in self.env.user.groups_id:
           security=False
        elif self.env.ref('hue_attendance.group_student_attendance_user') in self.env.user.groups_id:
            employee_id = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
            faculty = self.env['op.faculty'].sudo().search([('emp_id', '=', employee_id.id)], limit=1)
            hue_direction_lines = self.env['hue.academic.direction.line'].sudo().search(
                [('faculty_id', '=', faculty.id)])
            if hue_direction_lines :
                print("888888888888855555555555555555557777777777777777777777777777777777777777777777777777")
                print(hue_direction_lines)
                security=True
        else:
           security=False
        return security
    
    @api.model
    def student_users_update_groups(self):
        students = self.env['op.student'].sudo().search([])
        for student in students:
            # print(student.student_code)
            group_portal = []
            group_portal.append(self.env.ref('base.group_portal').id)
            student.user_id.groups_id = [(6, 0, group_portal)]
            self.env.cr.commit()