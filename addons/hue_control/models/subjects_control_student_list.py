from odoo import models, fields, api
from odoo.exceptions import ValidationError


class EvaluationGradesStudentList(models.Model):
    _name = 'subjects.control.student.list'
    _description = 'subjects.control.student.list'


    connect_id = fields.Many2one('subjects.control', string='Control', ondelete='cascade', required=True, index=True)
    student_id = fields.Many2one('op.student', string='Student', readonly=True)
    student_code = fields.Integer(related='student_id.student_code',readonly=True, store=True) 
    seq = fields.Integer('#', readonly=True)
    student_semester_subject_id = fields.Many2one('op.student.semesters.subjects', readonly=True)
    subject_id = fields.Many2one('op.subject', string='Subject', required=True)
    total = fields.Char(compute='_get_total', readonly=True, store=True)
    grade = fields.Many2one('op.grades', readonly=True, compute='_get_grade', store=True)
    control_degree = fields.Char(compute='_get_grade', inverse='_get_final_control_degree', store=True)
    final_control_degree = fields.Char()
    control_grade = fields.Many2one('op.grades', compute='_get_grade', inverse='_get_final_control_grade', store=True)
    final_control_grade = fields.Many2one('op.grades')
    tree_clo_acl_ids = fields.Char()#compute="_compute_tree_clo_acl_ids", search='tree_clo_acl_ids_search'
    grade_final = fields.Char('Final')
    grade_quiz = fields.Char('Quiz')
    grade_activity = fields.Char('Activity')
    grade_attendance = fields.Char('Attendance')
    grade_pract = fields.Char('Practical')
    grade_pract2 = fields.Char('Practical 2')
    grade_oral = fields.Char('Oral')
    grade_medterm = fields.Char('Med term')
    grade_coursework = fields.Char('Course Work')
    grade_pract_oral = fields.Char('Pract & Oral')
    grade_clinic = fields.Char('Clinic')
    grade_mcq = fields.Char('MCQ')
    grade_eassy = fields.Char('Essay')
    grade_skilllab = fields.Char('SkillLab')
    grade_pbl = fields.Char('pbl')
    grade_portfolio = fields.Char('Portfolio')
    grade_logbook = fields.Char('Log Book')
    grade_sdl = fields.Char('SDL')
    grade_fieldstudy = fields.Char('Field Study')
    grade_skillexam = fields.Char('Skill Exam')
    grade_practical = fields.Char('Practical')


    @api.depends('student_id')
    def _compute_tree_clo_acl_ids(self):
        print('View My Tree CLO ACL')


    def tree_clo_acl_ids_search(self, operator, operand):
        return [('id', 'in', [2928,3302])]


    def _get_final_control_degree(self):
        for rec in self:
            rec.final_control_degree = rec.control_degree


    def _get_final_control_grade(self):
        for rec in self:
            rec.final_control_grade = rec.control_grade


    @api.onchange('grade_final')
    def onchange_grade_final(self):
        if self.connect_id.flag_grade_final:
            if self.grade_final and self.grade_final != 'غ':
                try:
                    grade_final = float(self.grade_final)
                except ValueError:
                    raise ValidationError(
                        'Invalid Grade,check students Grade *** Student Name: %s' % self.student_id.name)
                if grade_final > self.connect_id.grade_final or grade_final < 0:
                    raise ValidationError((
                                              'Invalid Grade,Student Final Grade must be between (0) to (%s) *** Student Name: (%s)  Code: (%s) ') % (
                                              self.connect_id.grade_final, self.student_id.name,
                                              self.student_id.student_code))


    @api.onchange('grade_quiz')
    def onchange_grade_quiz(self):
        if self.connect_id.flag_grade_quiz and self.grade_quiz:
            if self.grade_quiz != 'غ':
                try:
                    grade_quiz = float(self.grade_quiz)
                except ValueError:
                    raise ValidationError(
                        'Invalid Grade,check students Grade *** Student Name: %s' % self.student_id.name)
                if grade_quiz > self.connect_id.grade_quiz or grade_quiz < 0:
                    raise ValidationError((
                                              'Invalid Grade,Student Final Grade must be between (0) to (%s) *** Student Name: (%s)  Code: (%s) ') % (
                                              self.connect_id.grade_quiz, self.student_id.name,
                                              self.student_id.student_code))


    @api.onchange('grade_activity')
    def onchange_grade_activity(self):
        if self.connect_id.flag_grade_activity and self.grade_activity:
            if self.grade_activity != 'غ':
                try:
                    grade_activity = float(self.grade_activity)
                except ValueError:
                    raise ValidationError(
                        'Invalid Grade,check students Grade *** Student Name: %s' % self.student_id.name)
                if grade_activity > self.connect_id.grade_activity or grade_activity < 0:
                    raise ValidationError((
                                              'Invalid Grade,Student Final Grade must be between (0) to (%s) *** Student Name: (%s)  Code: (%s) ') % (
                                              self.connect_id.grade_activity, self.student_id.name,
                                              self.student_id.student_code))


    @api.onchange('grade_attendance')
    def onchange_grade_attendance(self):
        if self.connect_id.flag_grade_attendance and self.grade_attendance:
            if self.grade_attendance != 'غ':
                try:
                    grade_attendance = float(self.grade_attendance)
                except ValueError:
                    raise ValidationError(
                        'Invalid Grade,check students Grade *** Student Name: %s' % self.student_id.name)
                if grade_attendance > self.connect_id.grade_attendance or grade_attendance < 0:
                    raise ValidationError((
                                              'Invalid Grade,Student Final Grade must be between (0) to (%s) *** Student Name: (%s)  Code: (%s) ') % (
                                              self.connect_id.grade_attendance, self.student_id.name,
                                              self.student_id.student_code))


    @api.onchange('grade_pract')
    def onchange_grade_pract(self):
        if self.connect_id.flag_grade_pract and self.grade_pract:
            if self.grade_pract != 'غ':
                try:
                    grade_pract = float(self.grade_pract)
                except ValueError:
                    raise ValidationError(
                        'Invalid Grade,check students Grade *** Student Name: %s' % self.student_id.name)
                if grade_pract > self.connect_id.grade_pract or grade_pract < 0:
                    raise ValidationError((
                                              'Invalid Grade,Student Final Grade must be between (0) to (%s) *** Student Name: (%s)  Code: (%s) ') % (
                                              self.connect_id.grade_pract, self.student_id.name,
                                              self.student_id.student_code))


    @api.onchange('grade_pract2')
    def onchange_grade_pract2(self):
        if self.connect_id.flag_grade_pract2 and self.grade_pract2:
            if self.grade_pract2 != 'غ':
                try:
                    grade_pract2 = float(self.grade_pract2)
                except ValueError:
                    raise ValidationError(
                        'Invalid Grade,check students Grade *** Student Name: %s' % self.student_id.name)
                if grade_pract2 > self.connect_id.grade_pract2 or grade_pract2 < 0:
                    raise ValidationError((
                                              'Invalid Grade,Student Final Grade must be between (0) to (%s) *** Student Name: (%s)  Code: (%s) ') % (
                                              self.connect_id.grade_pract2, self.student_id.name,
                                              self.student_id.student_code))


    @api.onchange('grade_oral')
    def onchange_grade_oral(self):
        if self.connect_id.flag_grade_oral and self.grade_oral:
            if self.grade_oral != 'غ':
                try:
                    grade_oral = float(self.grade_oral)
                except ValueError:
                    raise ValidationError(
                        'Invalid Grade,check students Grade *** Student Name: %s' % self.student_id.name)
                if grade_oral > self.connect_id.grade_oral or grade_oral < 0:
                    raise ValidationError((
                                              'Invalid Grade,Student Final Grade must be between (0) to (%s) *** Student Name: (%s)  Code: (%s) ') % (
                                              self.connect_id.grade_oral, self.student_id.name,
                                              self.student_id.student_code))


    @api.onchange('grade_medterm')
    def onchange_grade_medterm(self):
        if self.connect_id.flag_grade_medterm and self.grade_medterm:
            if self.grade_medterm != 'غ':
                try:
                    grade_medterm = float(self.grade_medterm)
                except ValueError:
                    raise ValidationError(
                        'Invalid Grade,check students Grade *** Student Name: %s' % self.student_id.name)
                if grade_medterm > self.connect_id.grade_medterm or grade_medterm < 0:
                    raise ValidationError((
                                              'Invalid Grade,Student Final Grade must be between (0) to (%s) *** Student Name: (%s)  Code: (%s) ') % (
                                              self.connect_id.grade_medterm, self.student_id.name,
                                              self.student_id.student_code))


    @api.onchange('grade_coursework')
    def onchange_grade_coursework(self):
        if self.connect_id.flag_grade_coursework and self.grade_coursework:
            if self.grade_coursework != 'غ':
                try:
                    grade_coursework = float(self.grade_coursework)
                except ValueError:
                    raise ValidationError(
                        'Invalid Grade,check students Grade *** Student Name: %s' % self.student_id.name)
                if grade_coursework > self.connect_id.grade_coursework or grade_coursework < 0:
                    raise ValidationError((
                                              'Invalid Grade,Student Final Grade must be between (0) to (%s) *** Student Name: (%s)  Code: (%s) ') % (
                                              self.connect_id.grade_coursework, self.student_id.name,
                                              self.student_id.student_code))


    @api.onchange('grade_pract_oral')
    def onchange_grade_pract_oral(self):
        if self.connect_id.flag_grade_pract_oral and self.grade_pract_oral:
            if self.grade_pract_oral != 'غ':
                try:
                    grade_pract_oral = float(self.grade_pract_oral)
                except ValueError:
                    raise ValidationError(
                        'Invalid Grade,check students Grade *** Student Name: %s' % self.student_id.name)
                if grade_pract_oral > self.connect_id.grade_pract_oral or grade_pract_oral < 0:
                    raise ValidationError((
                                              'Invalid Grade,Student Final Grade must be between (0) to (%s) *** Student Name: (%s)  Code: (%s) ') % (
                                              self.connect_id.grade_pract_oral, self.student_id.name,
                                              self.student_id.student_code))


    @api.onchange('grade_clinic')
    def onchange_grade_clinic(self):
        if self.connect_id.flag_grade_clinic and self.grade_clinic:
            if self.grade_clinic != 'غ':
                try:
                    grade_clinic = float(self.grade_clinic)
                except ValueError:
                    raise ValidationError(
                        'Invalid Grade,check students Grade *** Student Name: %s' % self.student_id.name)
                if grade_clinic > self.connect_id.grade_clinic or grade_clinic < 0:
                    raise ValidationError((
                                              'Invalid Grade,Student Final Grade must be between (0) to (%s) *** Student Name: (%s)  Code: (%s) ') % (
                                              self.connect_id.grade_clinic, self.student_id.name,
                                              self.student_id.student_code))


    @api.onchange('grade_mcq')
    def onchange_grade_mcq(self):
        if self.connect_id.flag_grade_mcq and self.grade_mcq:
            if self.grade_mcq != 'غ':
                try:
                    grade_mcq = float(self.grade_mcq)
                except ValueError:
                    raise ValidationError(
                        'Invalid Grade,check students Grade *** Student Name: %s' % self.student_id.name)
                if grade_mcq > self.connect_id.grade_mcq or grade_mcq < 0:
                    raise ValidationError((
                                              'Invalid Grade,Student Final Grade must be between (0) to (%s) *** Student Name: (%s)  Code: (%s) ') % (
                                              self.connect_id.grade_mcq, self.student_id.name,
                                              self.student_id.student_code))


    @api.onchange('grade_eassy')
    def onchange_grade_eassy(self):
        if self.connect_id.flag_grade_eassy and self.grade_eassy:
            if self.grade_eassy != 'غ':
                try:
                    grade_eassy = float(self.grade_eassy)
                except ValueError:
                    raise ValidationError(
                        'Invalid Grade,check students Grade *** Student Name: %s' % self.student_id.name)
                if grade_eassy > self.connect_id.grade_eassy or grade_eassy < 0:
                    raise ValidationError((
                                              'Invalid Grade,Student Final Grade must be between (0) to (%s) *** Student Name: (%s)  Code: (%s) ') % (
                                              self.connect_id.grade_eassy, self.student_id.name,
                                              self.student_id.student_code))
    
    
    @api.onchange('grade_skilllab')
    def onchange_grade_skilllab(self):
        if self.connect_id.flag_grade_skilllab and self.grade_skilllab:
            if self.grade_skilllab != 'غ':
                try:
                    grade_skilllab = float(self.grade_skilllab)
                except ValueError:
                    raise ValidationError(
                        'Invalid Grade,check students Grade *** Student Name: %s' % self.student_id.name)
                if grade_skilllab > self.connect_id.grade_skilllab or grade_skilllab < 0:
                    raise ValidationError((
                                              'Invalid Grade,Student Final Grade must be between (0) to (%s) *** Student Name: (%s)  Code: (%s) ') % (
                                              self.connect_id.grade_skilllab, self.student_id.name,
                                              self.student_id.student_code))
    
    
    @api.onchange('grade_pbl')
    def onchange_grade_pbl(self):
        if self.connect_id.flag_grade_pbl and self.grade_pbl:
            if self.grade_pbl != 'غ':
                try:
                    grade_pbl = float(self.grade_pbl)
                except ValueError:
                    raise ValidationError(
                        'Invalid Grade,check students Grade *** Student Name: %s' % self.student_id.name)
                if grade_pbl > self.connect_id.grade_pbl or grade_pbl < 0:
                    raise ValidationError((
                                              'Invalid Grade,Student Final Grade must be between (0) to (%s) *** Student Name: (%s)  Code: (%s) ') % (
                                              self.connect_id.grade_pbl, self.student_id.name,
                                              self.student_id.student_code))
    
    
    @api.onchange('grade_portfolio')
    def onchange_grade_portfolio(self):
        if self.connect_id.flag_grade_portfolio and self.grade_portfolio:
            if self.grade_portfolio != 'غ':
                try:
                    grade_portfolio = float(self.grade_portfolio)
                except ValueError:
                    raise ValidationError(
                        'Invalid Grade,check students Grade *** Student Name: %s' % self.student_id.name)
                if grade_portfolio > self.connect_id.grade_portfolio or grade_portfolio < 0:
                    raise ValidationError((
                                              'Invalid Grade,Student Final Grade must be between (0) to (%s) *** Student Name: (%s)  Code: (%s) ') % (
                                              self.connect_id.grade_portfolio, self.student_id.name,
                                              self.student_id.student_code))
    
    
    @api.onchange('grade_logbook')
    def onchange_grade_logbook(self):
        if self.connect_id.flag_grade_logbook and self.grade_logbook:
            if self.grade_logbook != 'غ':
                try:
                    grade_logbook = float(self.grade_logbook)
                except ValueError:
                    raise ValidationError(
                        'Invalid Grade,check students Grade *** Student Name: %s' % self.student_id.name)
                if grade_logbook > self.connect_id.grade_logbook or grade_logbook < 0:
                    raise ValidationError((
                                              'Invalid Grade,Student Final Grade must be between (0) to (%s) *** Student Name: (%s)  Code: (%s) ') % (
                                              self.connect_id.grade_logbook, self.student_id.name,
                                              self.student_id.student_code))
    
    
    @api.onchange('grade_sdl')
    def onchange_grade_sdl(self):
        if self.connect_id.flag_grade_sdl and self.grade_sdl:
            if self.grade_sdl != 'غ':
                try:
                    grade_sdl = float(self.grade_sdl)
                except ValueError:
                    raise ValidationError(
                        'Invalid Grade,check students Grade *** Student Name: %s' % self.student_id.name)
                if grade_sdl > self.connect_id.grade_sdl or grade_sdl < 0:
                    raise ValidationError((
                                              'Invalid Grade,Student Final Grade must be between (0) to (%s) *** Student Name: (%s)  Code: (%s) ') % (
                                              self.connect_id.grade_sdl, self.student_id.name,
                                              self.student_id.student_code))
    
    
    @api.onchange('grade_fieldstudy')
    def onchange_grade_fieldstudy(self):
        if self.connect_id.flag_grade_fieldstudy and self.grade_fieldstudy:
            if self.grade_fieldstudy != 'غ':
                try:
                    grade_fieldstudy = float(self.grade_fieldstudy)
                except ValueError:
                    raise ValidationError(
                        'Invalid Grade,check students Grade *** Student Name: %s' % self.student_id.name)
                if grade_fieldstudy > self.connect_id.grade_fieldstudy or grade_fieldstudy < 0:
                    raise ValidationError((
                                              'Invalid Grade,Student Final Grade must be between (0) to (%s) *** Student Name: (%s)  Code: (%s) ') % (
                                              self.connect_id.grade_fieldstudy, self.student_id.name,
                                              self.student_id.student_code))
    
    
    @api.onchange('grade_skillexam')
    def onchange_grade_skillexam(self):
        if self.connect_id.flag_grade_skillexam and self.grade_skillexam:
            if self.grade_skillexam != 'غ':
                try:
                    grade_skillexam = float(self.grade_skillexam)
                except ValueError:
                    raise ValidationError(
                        'Invalid Grade,check students Grade *** Student Name: %s' % self.student_id.name)
                if grade_skillexam > self.connect_id.grade_skillexam or grade_skillexam < 0:
                    raise ValidationError((
                                              'Invalid Grade,Student Final Grade must be between (0) to (%s) *** Student Name: (%s)  Code: (%s) ') % (
                                              self.connect_id.grade_skillexam, self.student_id.name,
                                              self.student_id.student_code))
                
                
    @api.onchange('grade_practical')
    def onchange_grade_practical(self):
        if self.connect_id.flag_grade_practical and self.grade_practical:
            if self.grade_practical != 'غ':
                try:
                    grade_practical = float(self.grade_practical)
                except ValueError:
                    raise ValidationError(
                        'Invalid Grade,check students Grade *** Student Name: %s' % self.student_id.name)
                if grade_practical > self.connect_id.grade_practical or grade_practical < 0:
                    raise ValidationError((
                                              'Invalid Grade,Student Final Grade must be between (0) to (%s) *** Student Name: (%s)  Code: (%s) ') % (
                                              self.connect_id.grade_practical,
                                              self.student_id.name,
                                              self.student_id.student_code))


    @api.depends('grade_final', 'grade_quiz', 'grade_activity', 'grade_attendance', 'grade_pract', 'grade_pract2',
                 'grade_oral', 'grade_medterm', 'grade_coursework', 'grade_pract_oral', 'grade_clinic', 'grade_mcq',
                 'grade_eassy','grade_skilllab','grade_pbl','grade_portfolio','grade_logbook','grade_sdl'
                 ,'grade_fieldstudy','grade_skillexam', 'grade_practical')
    def _get_total(self):
        for rec in self:
            if rec.connect_id.flag_grade_final and not rec.grade_final:
                rec.total = False
                continue
            elif rec.connect_id.flag_grade_final and rec.grade_final == 'غ':
                rec.total = 'غ'
                continue
            if rec.connect_id.flag_grade_quiz and not rec.grade_quiz:
                rec.total = False
                continue
            if rec.connect_id.flag_grade_activity and not rec.grade_activity:
                rec.total = False
                continue
            if rec.connect_id.flag_grade_attendance and not rec.grade_attendance:
                rec.total = False
                continue
            if rec.connect_id.flag_grade_pract and not rec.grade_pract:
                rec.total = False
                continue
            if rec.connect_id.flag_grade_pract2 and not rec.grade_pract2:
                rec.total = False
                continue
            if rec.connect_id.flag_grade_oral and not rec.grade_oral:
                rec.total = False
                continue
            if rec.connect_id.flag_grade_medterm and not rec.connect_id.factor and not rec.grade_medterm:
                rec.total = False
                continue
            if rec.connect_id.flag_grade_coursework and not rec.grade_coursework:
                rec.total = False
                continue
            if rec.connect_id.flag_grade_pract_oral and not rec.grade_pract_oral:
                rec.total = False
                continue
            if rec.connect_id.flag_grade_clinic and not rec.grade_clinic:
                rec.total = False
                continue
            if rec.connect_id.flag_grade_mcq and not rec.grade_mcq:
                rec.total = False
                continue
            if rec.connect_id.flag_grade_eassy and not rec.grade_eassy:
                rec.total = False
                continue
            if rec.connect_id.flag_grade_skilllab and not rec.grade_skilllab:
                rec.total = False
                continue
            if rec.connect_id.flag_grade_pbl and not rec.grade_pbl:
                rec.total = False
                continue
            if rec.connect_id.flag_grade_portfolio and not rec.grade_portfolio:
                rec.total = False
                continue
            if rec.connect_id.flag_grade_logbook and not rec.grade_logbook:
                rec.total = False
                continue
            if rec.connect_id.flag_grade_sdl and not rec.grade_sdl:
                rec.total = False
                continue
            if rec.connect_id.flag_grade_fieldstudy and not rec.grade_fieldstudy:
                rec.total = False
                continue
            if rec.connect_id.flag_grade_skillexam and not rec.grade_skillexam:
                rec.total = False
                continue
            if rec.connect_id.flag_grade_practical and not rec.grade_practical:
                rec.total = False
                continue
            try:
                grade_final = 0 if rec.grade_final == 'غ' else float(rec.grade_final)
                grade_quiz = 0 if rec.grade_quiz == 'غ' else float(rec.grade_quiz)
                grade_activity = 0 if rec.grade_activity == 'غ' else float(rec.grade_activity)
                grade_attendance = 0 if rec.grade_attendance == 'غ' else float(rec.grade_attendance)
                grade_pract = 0 if rec.grade_pract == 'غ' else float(rec.grade_pract)
                grade_pract2 = 0 if rec.grade_pract2 == 'غ' else float(rec.grade_pract2)
                grade_medterm = 0 if rec.grade_medterm == 'غ' else float(rec.grade_medterm)
                grade_oral = 0 if rec.grade_oral == 'غ' else float(rec.grade_oral)
                grade_coursework = 0 if rec.grade_coursework == 'غ' else float(rec.grade_coursework)
                grade_pract_oral = 0 if rec.grade_pract_oral == 'غ' else float(rec.grade_pract_oral)
                grade_clinic = 0 if rec.grade_clinic == 'غ' else float(rec.grade_clinic)
                grade_mcq = 0 if rec.grade_mcq == 'غ' else float(rec.grade_mcq)
                grade_eassy = 0 if rec.grade_eassy == 'غ' else float(rec.grade_eassy)
                grade_skilllab = 0 if rec.grade_skilllab == 'غ' else float(rec.grade_skilllab)
                grade_pbl = 0 if rec.grade_pbl == 'غ' else float(rec.grade_pbl)
                grade_portfolio = 0 if rec.grade_portfolio == 'غ' else float(rec.grade_portfolio)
                grade_logbook = 0 if rec.grade_logbook == 'غ' else float(rec.grade_logbook)
                grade_sdl = 0 if rec.grade_sdl == 'غ' else float(rec.grade_sdl)
                grade_fieldstudy = 0 if rec.grade_fieldstudy == 'غ' else float(rec.grade_fieldstudy)
                grade_skillexam = 0 if rec.grade_skillexam == 'غ' else float(rec.grade_skillexam)
                grade_practical = 0 if rec.grade_practical == 'غ' else float(rec.grade_practical)
            except ValueError:
                raise ValidationError('Invalid Grade,check students Grade *** Student Name: %s' % rec.student_id.name)
            if rec.connect_id.factor > 0 and not grade_medterm:
                total = grade_final + grade_quiz + grade_activity + grade_attendance + grade_pract + grade_pract2 + grade_oral  + grade_coursework + grade_clinic + grade_pract_oral + grade_mcq + grade_eassy + grade_skilllab + grade_pbl + grade_portfolio + grade_logbook + grade_sdl + grade_fieldstudy + grade_skillexam + grade_practical
            else:
                total = grade_final + grade_quiz + grade_activity + grade_attendance + grade_pract + grade_pract2 + grade_oral + grade_medterm + grade_coursework + grade_clinic + grade_pract_oral + grade_mcq + grade_eassy + grade_skilllab + grade_pbl + grade_portfolio + grade_logbook + grade_sdl + grade_fieldstudy + grade_skillexam + grade_practical
            if rec.connect_id.course_id.faculty_id.id == 12:
                rec.total = float(total)
            else:
                rec.total = math.ceil(float(total))


    @api.depends('total')
    def _get_grade(self):
        for rec in self:
            # assessments_degree = sum(rec.connect_id.subject_id.subject_assessmentsdegree.mapped('degree'))
            if rec.total == 'غ':
                absent_grade_grade = self.env['op.grades'].sudo().search(
                    [('absent_grade', '=', True)], limit=1).id
                rec.grade = absent_grade_grade
                # rec.control_degree = False
                # rec.control_grade = False
                continue
            if rec.total:

                total = ((float(rec.total) * 100) / rec.connect_id.subject_id.subject_total)
                # print(sum(rec.connect_id.subject_id.subject_assessmentsdegree.mapped('degree')))
                if total >= 100:
                    if rec.connect_id.subject_id.subject_passorfail:
                        rec.grade = 20
                        rec.control_degree = False
                        rec.control_grade = False
                    elif rec.connect_id.subject_id.subject_satisfied:
                        rec.grade = 27
                        rec.control_degree = False
                        rec.control_grade = False
                    else:
                        total_grade = 100
                        grade = self.env['op.course.grades'].sudo().search(
                            [('course_id', '=', rec.connect_id.course_id.id), ('percent_to', '=', float(total_grade))])
                        rec.grade = grade.grade_id
                        accum_subjects = 0
                        accum_subjects_data = self.env['op.student.semesters.subjects'].sudo().search(
                            [('subject_grade', '!=', False), ('subject_id', '=', rec.connect_id.subject_id.id),('final_grade.pass_grade', '=', False),
                             ('student_id', '=', rec.student_id.id) ,('final_grade.id', 'not in', [1,26])])

                        for acccc in accum_subjects_data:
                            if not (
                                    acccc.semester_id.id == rec.connect_id.batch_id.semester.id and acccc.academicyear_id.id == rec.connect_id.batch_id.academic_year.id):
                                accum_subjects = accum_subjects + 1
                        if accum_subjects == 1:
                            if grade.grade_id.pass_grade and rec.connect_id.course_id.faculty_id.id != 12:
                                deduction_grade_first = self.env['op.course.grades'].sudo().search(
                                    [('course_id', '=', rec.connect_id.course_id.id),
                                     ('grade_id', '=', rec.connect_id.course_id.deduction_grade_first.id)],
                                    limit=1).percent_to
                                if deduction_grade_first <= total:
                                    rec.control_degree = float(
                                        (deduction_grade_first * rec.connect_id.subject_id.subject_total) / 100) - 0.5
                                    rec.control_grade = rec.connect_id.course_id.deduction_grade_first.id
                                else:
                                    rec.control_degree = False
                                    rec.control_grade = False
                            else:
                                rec.control_degree = False
                                rec.control_grade = False
                        elif accum_subjects > 1:
                            if grade.grade_id.pass_grade and rec.connect_id.course_id.faculty_id.id != 12:
                                deduction_grade_second = self.env['op.course.grades'].sudo().search(
                                    [('course_id', '=', rec.connect_id.course_id.id),
                                     ('grade_id', '=', rec.connect_id.course_id.deduction_grade_second.id)],
                                    limit=1).percent_to
                                # print()
                                if deduction_grade_second <= total:
                                    rec.control_degree = float(
                                        (deduction_grade_second * rec.connect_id.subject_id.subject_total) / 100) - 0.5
                                    rec.control_grade = rec.connect_id.course_id.deduction_grade_second.id
                                else:
                                    rec.control_degree = False
                                    rec.control_grade = False
                            else:
                                rec.control_degree = False
                                rec.control_grade = False

                    continue
                if rec.connect_id.subject_id.subject_passorfail:
                    first_pass_grade = self.env['op.course.grades'].sudo().search(
                        [('course_id', '=', rec.connect_id.course_id.id), ('first_pass_grade', '=', True)], limit=1)
                    if rec.connect_id.subject_id.subject_passpercentage:
                        percent_from = float(rec.connect_id.subject_id.subject_passpercentage)
                    else:
                        percent_from = first_pass_grade.percent_from
                    course_pass_degree = ((percent_from * rec.connect_id.subject_id.subject_total) / 100)
                    first_course_pass_degree = ((
                                                        percent_from * rec.connect_id.subject_id.subject_total) / 100) - rec.connect_id.course_id.pass_degree

                    if float(rec.total) >= course_pass_degree:
                        rec.grade = 20
                        rec.control_degree = False
                        rec.control_grade = False
                    else:
                        rec.grade = 21
                        rec.control_degree = False
                        rec.control_grade = False
                    if first_course_pass_degree <= float(rec.total) < course_pass_degree:
                        rec.grade = 21
                        rec.control_degree = course_pass_degree
                        rec.control_grade = 20
                elif rec.connect_id.subject_id.subject_satisfied:
                    first_pass_grade = self.env['op.course.grades'].sudo().search(
                        [('course_id', '=', rec.connect_id.course_id.id), ('first_pass_grade', '=', True)], limit=1)
                    if rec.connect_id.subject_id.subject_passpercentage:
                        percent_from = float(rec.connect_id.subject_id.subject_passpercentage)
                    else:
                        percent_from = first_pass_grade.percent_from
                    course_pass_degree = ((percent_from * rec.connect_id.subject_id.subject_total) / 100)
                    first_course_pass_degree = ((percent_from * rec.connect_id.subject_id.subject_total) / 100) - rec.connect_id.course_id.pass_degree

                    if float(rec.total) >= course_pass_degree:
                        rec.grade = 27
                        rec.control_degree = False
                        rec.control_grade = False
                    else:
                        rec.grade = 22
                        rec.control_degree = False
                        rec.control_grade = False
                    if first_course_pass_degree <= float(rec.total) < course_pass_degree:
                        rec.grade = 22
                        rec.control_degree = course_pass_degree
                        rec.control_grade = 27
                else:
                    print("elseelseelseelseelseelseelseelseelseelse")
                    grade = self.env['op.course.grades'].sudo().search(
                        [('course_id', '=', rec.connect_id.course_id.id), ('percent_to', '>', total),
                         ('percent_from', '<=', total)])
                    rec.grade = grade.grade_id
                    # rec.control_degree = 60
                    print("1111111111111111111111111111111111111111")
                    accum_subjects = 0
                    accum_subjects_data = self.env['op.student.semesters.subjects'].sudo().search(
                        [('subject_grade', '!=', False), ('subject_id', '=', rec.connect_id.subject_id.id),('final_grade.pass_grade', '=', False),
                         ('student_id', '=', rec.student_id.id),('final_grade.id', 'not in', [1,26])])
                    for acccc in accum_subjects_data:
                        print(acccc.final_grade.id)
                        if not (
                                acccc.semester_id.id == rec.connect_id.batch_id.semester.id and acccc.academicyear_id.id == rec.connect_id.batch_id.academic_year.id):
                            accum_subjects = accum_subjects + 1
                    # accum_subjectss = self.env['op.student.semesters.subjects'].sudo().search(
                    #     [('subject_grade', '!=', False), ('subject_id', '=', rec.connect_id.subject_id.id),
                    #      ('student_id', '=', rec.student_id.id)])
                    print("2222222222222222222222222222222222")
                    first_pass_grade = self.env['op.course.grades'].sudo().search(
                        [('course_id', '=', rec.connect_id.course_id.id), ('first_pass_grade', '=', True)], limit=1)
                    second_pass_grade = self.env['op.course.grades'].sudo().search(
                        [('course_id', '=', rec.connect_id.course_id.id), ('second_pass_grade', '=', True)], limit=1)
                    course_pass_degree = ((
                                                  first_pass_grade.percent_from * rec.connect_id.subject_id.subject_total) / 100) - rec.connect_id.course_id.pass_degree
                    course_second_pass_degree = ((
                                                         second_pass_grade.percent_from * rec.connect_id.subject_id.subject_total) / 100) - rec.connect_id.course_id.second_pass_degree
                    pass_degree = math.ceil((float(rec.total) * 100) / rec.connect_id.subject_id.subject_total)
                    # pass_degree_without_cell =((float(rec.total) * 100) / rec.connect_id.subject_id.subject_total)
                    pass_degree_without_cell = float(rec.total)  # * 100) / rec.connect_id.subject_id.subject_total)
                    first_pass_grade_degree = (
                            (first_pass_grade.percent_from * rec.connect_id.subject_id.subject_total) / 100)
                    second_pass_grade_degree = (
                            (second_pass_grade.percent_from * rec.connect_id.subject_id.subject_total) / 100)
                    if course_pass_degree <= pass_degree_without_cell < first_pass_grade_degree:
                        rec.control_degree = float(
                            (first_pass_grade.percent_from * rec.connect_id.subject_id.subject_total) / 100)
                        rec.control_grade = first_pass_grade.grade_id.id



                    elif course_second_pass_degree <= pass_degree_without_cell < second_pass_grade_degree:
                        rec.control_degree = float(
                            (second_pass_grade.percent_from * rec.connect_id.subject_id.subject_total) / 100)
                        rec.control_grade = second_pass_grade.grade_id.id
                    else:
                        rec.control_degree = False
                        rec.control_grade = False
                        # print(accum_subjectss)
                        print(accum_subjects)
                        if accum_subjects == 1:
                            if grade.grade_id.pass_grade and rec.connect_id.course_id.faculty_id.id != 12 :
                                deduction_grade_first = self.env['op.course.grades'].sudo().search(
                                    [('course_id', '=', rec.connect_id.course_id.id),
                                     ('grade_id', '=', rec.connect_id.course_id.deduction_grade_first.id)],
                                    limit=1).percent_to
                                if deduction_grade_first <= total:
                                    rec.control_degree = float(
                                        (deduction_grade_first * rec.connect_id.subject_id.subject_total) / 100) - 0.5
                                    rec.control_grade = rec.connect_id.course_id.deduction_grade_first.id
                                else:
                                    rec.control_degree = False
                                    rec.control_grade = False
                            else:
                                rec.control_degree = False
                                rec.control_grade = False
                        elif accum_subjects > 1:
                            if grade.grade_id.pass_grade and rec.connect_id.course_id.faculty_id.id != 12:
                                deduction_grade_second = self.env['op.course.grades'].sudo().search(
                                    [('course_id', '=', rec.connect_id.course_id.id),
                                     ('grade_id', '=', rec.connect_id.course_id.deduction_grade_second.id)],
                                    limit=1).percent_to
                                if deduction_grade_second <= total:
                                    rec.control_degree = float(
                                        (deduction_grade_second * rec.connect_id.subject_id.subject_total) / 100) - 0.5
                                    rec.control_grade = rec.connect_id.course_id.deduction_grade_second.id
                                else:
                                    rec.control_degree = False
                                    rec.control_grade = False
                            else:
                                rec.control_degree = False
                                rec.control_grade = False

                if rec.grade_final:
                    grade_fr_percent = math.floor(
                        (float(rec.connect_id.course_id.fr_percent) * rec.connect_id.grade_final) / 100)
                    grade_final_precentage = float(rec.grade_final)
                    if grade_fr_percent > grade_final_precentage:
                        fr_percent_grade = self.env['op.grades'].sudo().search(
                            [('theoretical_fail', '=', True)], limit=1).id
                        fr_percent_from = self.env['op.course.grades'].sudo().search(
                            [('course_id', '=', rec.connect_id.course_id.id), ('grade_id', '=', fr_percent_grade)],
                            limit=1).percent_from
                        rec.control_degree = float(fr_percent_from)
                        if rec.connect_id.subject_id.subject_passorfail:
                            rec.control_grade = 21
                        else :  
                            rec.control_grade = fr_percent_grade
            else:
                rec.control_degree = False
                rec.control_grade = False
            if rec.connect_id.course_id.faculty_id.id == 12:
                if  rec.connect_id.factor :
                    if  rec.grade_medterm != 'غ':
                        if not rec.grade_medterm :
                            std_degree = float(rec.total) * rec.connect_id.assessment_sum
                            std_control_degree = std_degree / rec.connect_id.factor
                            rec.control_degree = math.ceil(std_control_degree)
                            grade_control_degree =  ( float(rec.control_degree) / float(rec.connect_id.subject_id.subject_total) ) * 100
                            grade = self.env['op.course.grades'].sudo().search(
                                [('course_id', '=', rec.connect_id.course_id.id), ('percent_to', '>=', grade_control_degree),
                                 ('percent_from', '<=', grade_control_degree)],limit=1)
                            
                            rec.control_grade = grade.grade_id
                else :
                    med_std_last_try = self.env['op.student.semesters.subjects'].sudo().search([('student_id', '=', rec.student_id.id),
                        ('student_semester_id.grade.pass_grade', '=', False),('academicyear_id.sequence', '<=', self.connect_id.batch_id.academic_year.sequence),
                        ('course_id.faculty_id', '=',12),('subject_id', '=', self.connect_id.subject_id.id),('final_grade.pass_grade', '=', True)],order='id desc' ,limit=1)
                    
                    if med_std_last_try :
                        rec.control_grade = med_std_last_try.control_grade.id
                        rec.control_degree = med_std_last_try.control_degree