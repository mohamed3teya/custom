from odoo import models, fields, api


class HUEExam(models.Model):
    _inherit = 'op.exam'


    course_id = fields.Many2one('op.course',required=True)
    session_id = fields.Many2one('op.exam.session', 'Exam Session', domain="[('id', 'in', suitable_session_ids)]")
    suitable_session_ids = fields.Many2many('op.exam.session', compute='_compute_suitable_session_ids',) #to add domain to timings
    exam_code = fields.Char('Exam Code', related='subject_id.code' , readonly=True)
    similarity = fields.Boolean()
    course_only = fields.Boolean()
    name = fields.Char('Exam', size=256, required=False, related='subject_id.name', readonly=True)
    total_marks = fields.Integer('Total Marks', required=True, default=100)
    min_marks = fields.Integer('Passing Marks', required=True, default=60)
    subject_code = fields.Char('Code', related='subject_id.code', store = True)
    exam_type = fields.Many2one('op.exam.type', related='session_id.exam_type', store=True)
    tree_clo_acl_ids = fields.Char()#compute="_compute_tree_clo_acl_ids", search='tree_clo_acl_ids_search'
    
    
    @api.depends('course_id')
    def _compute_tree_clo_acl_ids(self):
        print('View My Tree CLO ACL')
    

    @api.onchange('course_id')
    def _compute_suitable_session_ids(self):
        for rec in self:
            curr_academic_year = self.env['op.academic.year'].sudo().search([('current', '=', True)], limit=1).id
            curr_semester = self.env['op.semesters'].sudo().search([('current', '=', True)], limit=1).id
            sessions = self.env['op.exam.session'].sudo().search([('course_id' ,'=', rec.course_id.id)
                ,('batch_id.academic_year' ,'=', curr_academic_year),('batch_id.semester' ,'=', curr_semester)]).ids
            rec.suitable_session_ids = sessions


    # @api.onchange('course_id')
    # def _onchange_course_id(self):
    #     curr_academic_year = self.env['op.academic.year'].sudo().search([('current', '=', True)], limit=1).id
    #     curr_semester = self.env['op.semesters'].sudo().search([('current', '=', True)], limit=1).id
    #     sessions = self.env['op.exam.session'].sudo().search([('course_id' ,'=', self.course_id.id)
    #         ,('batch_id.academic_year' ,'=', curr_academic_year),('batch_id.semester' ,'=', curr_semester)]).ids
    #     domain = {'session_id': [('id', 'in', sessions)]}
    #     return {'domain': domain}
    

    def tree_clo_acl_ids_search(self, operator, operand):
        if self.env.ref('hr_extention.group_service_manager') in self.env.user.groups_id:
            return [('id', 'in', self.sudo().search([]).ids)]
        emp = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)])
        courses = emp.course_ids.ids
        records = self.sudo().search([('course_id', 'in', courses)]).ids
        return [('id', 'in', records)]

    
    def act_cancel(self):
        self.attendees_line.unlink()
        self.state = 'cancel'


    @api.constrains('subject_id')
    def _check_subject(self):
        for rec in self:
            domain = [
                ('subject_id', '=', rec.subject_id.id),
                ('session_id.batch_id', '>=', rec.session_id.batch_id.id),
                ('session_id.course_id', '=', rec.session_id.course_id.id),
                ('id', '!=', rec.id),
                ('session_id', '=', rec.session_id.id),
                ('session_id.exam_type', '=', rec.session_id.exam_type.id)
            ]
            data = self.search_count(domain)
            if data and rec.session_id.course_id.faculty_id.id not in [12,8,9]:
                raise ValidationError('Subject already has exam in same batch !....')


    @api.onchange('session_id')
    def onchange_session_id(self):
        curr_academic_year = self.env['op.academic.year'].sudo().search([('current', '=', True)], limit=1).id
        curr_semester = self.env['op.semesters'].sudo().search([('current', '=', True)], limit=1).id
        self.subject_id = False
        # if self.env.ref('hr_extention.group_service_manager') in self.env.user.groups_id:
        #     courses = self.env['op.course'].sudo().search([]).ids
        #     sessions = self.env['op.exam.session'].sudo().search([]).ids
        # else:
        emp = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)])
        if not emp:
            emp = self.env.user.employee_id
        # courses = emp.course_ids.ids
        courses = self.env['op.course'].sudo().search([]).ids # till hr_extention.group_service_manager is added
        sessions = self.env['op.exam.session'].sudo().search([('course_id' ,'in', courses),('batch_id.academic_year' ,'=', curr_academic_year),
            ('batch_id.semester' ,'=', curr_semester)]).ids

        course_subjects = self.env['op.subject'].sudo().search([('course_id', '=', self.session_id.course_id.id)])
        subjects = []
        for course_subject in course_subjects:
            subjects.append(course_subject.id)
        subject_ids =[]
        if self.session_id.batch_id:
            for course_subject in self.session_id.batch_id.sudo().subject_registration_ids:  # course_subjects:
                if course_subject.sudo().id not in subject_ids:
                    subject_ids.append(course_subject.sudo().id)
        domain = {'subject_id': [('id', 'in', subject_ids)], 'course_id': [('id', 'in', courses)],'session_id': [('id', 'in', sessions)]}
        return {'domain': domain}


class OpExamType(models.Model):
    _inherit = 'op.exam.type'

    assessment_id = fields.Many2one('op.assessments', required=True)
    farouk_id = fields.Integer(string='Farouk Mapping')