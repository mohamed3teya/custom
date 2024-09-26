import logging
import uuid
import math
from decimal import Decimal, ROUND_HALF_UP
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import UserError, ValidationError
import datetime
from datetime import date, datetime

_logger = logging.getLogger(__name__)


class HUEGpaCalculator(models.Model):
    _name = 'hue.gpa.calculator'
    _description = 'Gpa Calculator'

    student_id = fields.Many2one('op.student', 'Student')
    student_name = fields.Char('Student Name', compute='_get_student_name')
    semester_id = fields.Many2one('op.semesters', compute='_get_semester_id', store=True)
    academic_year_id = fields.Many2one('op.academic.year', compute='_get_academic_year_id', store=True)
    current_gpa = fields.Float('Current Gpa', compute='_get_new_gpa')
    ex_gpa = fields.Float('Expected Gpa')
    suggested_plan_ids = fields.One2many('hue.suggested.plan', 'gpa_calculator_id', string='Suggested Plan')
    token = fields.Char('Identification token', default=lambda self: str(uuid.uuid4()), readonly=True, required=True,
                        copy=False)
    advisor_id = fields.Many2one('op.faculty', compute='_get_advisor_id', store=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('unique_token', 'UNIQUE (token)', 'A token must be unique!,Try Again'),
        ('unique_gpa', 'Check(1=1)', 'Invoice Number must be unique per Company!'),
    ]

    @api.constrains('student_id', 'semester_id', 'academic_year_id')
    def _check_data(self):        
        for rec in self:
            print("active_ids",type(self.browse(self.env.context['active_ids'])))
            if self.browse(self.env.context['active_ids']):
                student = self.browse(self.env.context['active_ids'])
            if rec.student_id:
                student = rec.student_id
            
            print("rec_id", rec.id)
            print("rec_student", rec.student_id)
            domain = [
                ('semester_id', '=', rec.semester_id.id),
                ('academic_year_id', '=', rec.academic_year_id.id),
                ('student_id', '=', student.id),
                ('id', '!=', rec.id),
            ]
            data = self.env['hue.gpa.calculator'].search(domain)
            print("data:--------------", data.student_id)
            if data:
                raise ValidationError('Gpa for Academic year and semester already created!')

    @api.model
    def create(self, vals):
        print("5555555555555555555555555555555555")
        # Check if context contains student_id and assign it to the record being created
        if self.env.context.get('default_student_id'):
            vals['student_id'] = self.env.context.get('default_student_id')
        
        return super(HUEGpaCalculator, self).create(vals)

    def _get_student_name(self):
        for rec in self:
            rec.student_name = rec.student_id.name
            
    def _get_new_gpa(self):
        for rec in self:
            rec.current_gpa = rec.student_id.new_gpa

    @api.depends('student_id')
    def _get_advisor_id(self):
        for rec in self:
            rec.advisor_id = self.env['hue.academic.direction.line'].sudo().search(
                [('student_id', '=', rec.student_id.id), ('to_date', '=', False)], limit=1).faculty_id.id

    @api.depends('student_id')
    def _get_semester_id(self):
        for rec in self:
            rec.semester_id = self.env['op.semesters'].sudo().search([('gpa_current', '=', True)], limit=1).id

    @api.depends('student_id')
    def _get_academic_year_id(self):
        for rec in self:
            rec.academic_year_id = self.env['op.academic.year'].sudo().search([('gpa_current', '=', True)], limit=1).id

    
    def check_block(self, student_id):
        blocked = False
        domain = [
            ('move_type', 'in', ['out_invoice']),
            ('partner_id', '=', student_id.partner_id.id),
            ('state', 'in', ['draft', 'posted'])
        ]
        invoice_count = self.env['account.move'].sudo().search_count(domain)

        accum_semesters = self.env['op.student.accumlative.semesters'].sudo().search(
            [('student_id', '=', student_id.id),
             ('transferred', '=', False)])
        for semss in accum_semesters:
            if not student_id.questionnaire_done() or invoice_count > 0 or semss.block_result:
                blocked = True
                break

        return blocked
    
    def action_start_advising(self):
        # blocked = False
        # if blocked == False:
        #     raise ValidationError('Student Blocked !!!!')
        for rec in self:
            blocked = False
            # ('date_due', '<=', '2023-01-31'),
            domain = [
                ('move_type', 'in', ['out_invoice']),
                ('partner_id', '=', rec.student_id.partner_id.id),
                ('invoice_date_due', '<=', date.today()),
                ('state', 'in', ['draft', 'posted'])
            ]
            invoice_count = self.env['account.move'].sudo().search_count(domain)
        
            accum_semesters = self.env['op.student.accumlative.semesters'].sudo().search(
                [('student_id', '=', rec.student_id.id),
                 ('academicyear_id.run_semester_gpa', '=', True),
                 ('semester_id.run_semester_gpa', '=', True),
                 ('transferred', '=', False)])
            for semss in accum_semesters:
                if  invoice_count > 0 or semss.block_result:
                    blocked = True          
        if blocked == True :
            if rec.student_id.allow_registration == False:
                raise ValidationError('Student Blocked !!!!')
        
        if rec.student_id.new_gpa >= 2:
            raise ValidationError('Student GPA is already greater than 2')

        """ Open the website page with the survey form into test mode"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'name': "Start Advising",
            'target': 'self',
            'url': self.env['ir.config_parameter'].sudo().get_param('web.base.url') + "/advising/" + slug(self)
        }
    
class HUESuggestedPlan(models.Model):
    _name = 'hue.suggested.plan'
    _description = 'Suggested Plan'

    subject_id = fields.Many2one('op.subject', 'Subject')
    gpa_calculator_id = fields.Many2one('hue.gpa.calculator')
    ex_grades = fields.Many2one('op.course.grades')
    student_id = fields.Many2one('op.student', 'Student', related='gpa_calculator_id.student_id', store=True)
    
    
class OpStdClass(models.Model):
    _inherit = 'op.student'
    _order = 'name asc'
    
    student_advisor_id = fields.Many2one('op.faculty')
    tree_clo_acl_ids_2 = fields.Char(compute="_compute_tree_clo_acl_ids_2", search='tree_clo_acl_ids_search_2')
   
    @api.depends('course_id')
    def _compute_tree_clo_acl_ids_2(self):
        print('View My Tree CLO ACL')
 
    def tree_clo_acl_ids_search_2(self, operator, operand):
 
        students = self.env['hue.academic.direction.line'].sudo().search([('faculty_id.emp_id.user_id', '=', self.env.user.id),
                           ('to_date', '=',False)])
        students.mapped('student_id')
        students =students.mapped('student_id')
        return [('id', 'in', students.ids)]
                
    def check_block(self, student_id):
        blocked = False
        domain = [
            ('move_type', 'in', ['out_invoice']),
            ('partner_id', '=', student_id.partner_id.id),
            ('state', 'in', ['draft', 'posted'])
        ]
        invoice_count = self.env['account.move'].sudo().search_count(domain)

        accum_semesters = self.env['op.student.accumlative.semesters'].sudo().search(
            [('student_id', '=', student_id.id),
             ('transferred', '=', False)])
        for semss in accum_semesters:
            if not student_id.questionnaire_done() or invoice_count > 0 or semss.block_result:
                blocked = True
                break

        return blocked
    
    def check_is_published(self, courseid, acadyear, semester):
        published = self.env['op.course.resultspublish'].sudo().search(
            [('course_id', '=', courseid), ('acadyears', '=', acadyear), ('semesters', '=', semester)]).publishflag
        if published:
            if published == 'publish' or published == 'close':
                return True
        return False
    
    @api.model
    def _cron_calculate_level(self, course_id=None, std_id=None):
        if course_id:
            students = self.env['op.student'].sudo().search([('course_id', '=', int(course_id))])
        elif std_id:
            students = self.env['op.student'].sudo().search([('id', '=', int(std_id))])
        else:
            students = self.env['op.student'].sudo().search([])
        for student in students:
            level = self.env['op.course.levels'].sudo().search(
                [('course_id', '=', student.course_id.id),
                 ('hours_from', '<=', student.new_crh),
                 ('hours_to', '>', student.new_crh)], limit=1).level_id.level_id.id  # 'level': (level),
            student.write({'level': level})
        _logger.info("Cron job executed successfully.")
            
            
    def student_calculate_semester_data(self, student, academic_year_id, semester_id):
        domain_academic = []
        domain_academic.append(('sequence', '!=', 0))
        if academic_year_id:
            domain_academic.append(('id', '=', academic_year_id.id))
        domain_semester = []
        if semester_id:
            domain_semester.append(('id', '=', semester_id.id))
        academic_years = self.env['op.academic.year'].sudo().search(domain_academic, order='sequence asc')
        semesters = self.env['op.semesters'].sudo().search(domain_semester, order='sequence asc')
        
        print("############IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII#############")
        print(self.check_block)
        print("############IIIIIIIIITTTTTTTIIIIIIIIIII#############")
        if self.check_block != False:
            raise ValidationError('Student Blocked !!!!')
        for academic_year in academic_years:
            print("#############1111111111111111111111############")
            print(academic_year.name)
            for semester in semesters:
                print("##############1111111111111111111###############")
                print(semester.name)
                earned_hours = 0
                registered_hours = 0
                actual_hours = 0
                semester_points = 0
                semester_current_gpa = 0
                accum_semesters = self.env['op.student.accumlative.semesters'].sudo().search(
                    [('student_id', '=', student.id),
                     ('academicyear_id', '=', academic_year.id), ('semester_id', '=', semester.id),
                     ('transferred', '=', False)])
                print("accum_semesters")
                print(accum_semesters)
                for subject in accum_semesters.accum_semesters_subjects_ids:
                    print("111111111111111111111111111")
                    print(subject.subject_id.id)
                    if subject.subject_grade:
                        published = self.check_is_published(subject.course_id.id,
                                                      subject.academicyear_id.id,
                                                      subject.semester_id.id)
                        if not published:
                            continue
                        print(subject.subject_id)
                        credit_hours = subject.subject_id.subject_credithours
                        registered_hours = registered_hours + credit_hours
                        if subject.final_grade.pass_grade:
                            earned_hours = earned_hours + credit_hours
                        if subject.subject_id.subject_addtogpa and subject.final_grade.add_to_gpa:
                            actual_hours = actual_hours + credit_hours
                        points = subject.course_id.course_grade_ids.filtered(
                            lambda l: l.grade_id.id == subject.final_grade.id).points_from
                        semester_points = semester_points + (points * credit_hours)
                if actual_hours > 0:
                    semester_current_gpa = (semester_points / actual_hours)
                # new_gpa = self.calc_student_gpa(student)
                accum_semesters.sudo().write(
                    {'semester_gpa': float(semester_current_gpa), 'current_gpa':float(semester_current_gpa),
                     'semester_hr': earned_hours, 'earned_hours': earned_hours,
                     'registered_hours': registered_hours,
                     'actual_hours': actual_hours, 'semester_points': semester_points,
                     'semester_current_gpa': float(semester_current_gpa)})
    
    
    def student_calculate_transferred_data(self, student, academic_year_id, semester_id):
        print("ddddddddddddddddddddd")
        semester_id = 4
        domain_academic = []
        domain_academic.append(('sequence', '!=', 0))
        domain_academic.append(('id', '=', academic_year_id.id))
        domain_semester = []
        domain_semester.append(('id', '=', semester_id))
        academic_years = self.env['op.academic.year'].sudo().search(domain_academic, order='sequence asc')
        semesters = self.env['op.semesters'].sudo().search(domain_semester, order='sequence asc')
        # print("############IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII#############")
        # print(self.check_block)
        # print("############IIIIIIIIITTTTTTTIIIIIIIIIII#############")
        # if self.check_block != False:
        #     raise ValidationError('Student Blocked !!!!')
        for academic_year in academic_years:
            for semester in semesters:
                if student.course_id.id == 15:
                    numerator = 0  # بسط فوق
                    denominator = 0  # مقام
                    crh_denominator = 0
                    final_degree = 0
                    total_essay_mcq = 0
                    essay_mcq_degree = 0
                    final_total_essay_mcq = 0
                    grade = False
                    semester_current_gpa = 0
                    accum_semesters = self.env['op.student.accumlative.semesters'].sudo().search(
                        [('student_id', '=', student.id),
                         ('academicyear_id', '=', academic_year.id), ('semester_id', '=', semester.id),
                         ('transferred', '=', False)], order='id desc',limit =1)

                    for subject in accum_semesters.accum_semesters_subjects_ids:
                        published = self.check_is_published(subject.course_id.id,
                                                      subject.academicyear_id.id,
                                                      subject.semester_id.id)
                        if not published:
                            continue
                        subject_grade = subject.final_grade
                        if subject.subject_id.subject_addtohours and subject.subject_id.subject_addtogpa:
                            crh_denominator = crh_denominator + subject.subject_id.subject_credithours
                        elif subject.subject_id.subject_addtohours and  subject_grade.pass_grade:
                            crh_denominator = crh_denominator + subject.subject_id.subject_credithours
                        if subject.subject_id.subject_addtogpa:
                            # total_essay_mcq = total_essay_mcq + 55
                            essay_mcq_degree = essay_mcq_degree + subject.grade_mcq + subject.grade_eassy

                            denominator = denominator + subject.subject_id.subject_total
                            numerator = numerator + subject.final_degree
                    if denominator > 0:
                        numerator = round(numerator, 2)
                        final_degree = numerator / denominator
                        final_degree = round(final_degree, 2) * 100
                        print(numerator)
                        print(denominator)
                        total_essay_mcq = 190
                        grade = self.env['op.course.grades'].sudo().search(
                            [('course_id', '=', student.course_id.id), ('percent_to', '>', final_degree),
                             ('percent_from', '<=', final_degree)])
                        final_total_essay_mcq = (round(essay_mcq_degree, 2) / total_essay_mcq) * 100
                        curr_grade = grade.grade_id.id
                        semester_current_gpa = grade.points_to
                        print(final_total_essay_mcq)
                        if final_total_essay_mcq < 40:
                            curr_grade = False
                            crh_denominator = 0
                    accum_semesters.sudo().write(
                        {'semester_gpa': float(semester_current_gpa), 'current_gpa': float(semester_current_gpa),
                         'semester_hr': crh_denominator, 'earned_hours': crh_denominator,
                         'semester_current_gpa': float(semester_current_gpa),
                         'total_degree': numerator,
                         'total_max': denominator,
                         'percentage': final_degree,
                         'grade':curr_grade,
                         })
                else:
                    earned_hours = 0
                    registered_hours = 0
                    actual_hours = 0
                    semester_points = 0
                    semester_current_gpa = 0
                    accum_semesters = self.env['op.student.accumlative.semesters'].sudo().search(
                        [('student_id', '=', student.id),
                         ('academicyear_id', '=', academic_year.id), ('semester_id', '=', semester.id),
                         ('transferred', '=', False)], order='id desc',limit =1)
                    for subject in accum_semesters.accum_semesters_subjects_ids:
                        print(subject.subject_id)
                        if subject.subject_grade:
                            published = self.check_is_published(subject.course_id.id,
                                                          subject.academicyear_id.id,
                                                          subject.semester_id.id)
                            if not published:
                                continue
                            print(subject.subject_id)
                            credit_hours = subject.subject_id.subject_credithours
                            registered_hours = registered_hours + credit_hours
                            if subject.final_grade.pass_grade:
                                earned_hours = earned_hours + credit_hours
                            if subject.subject_id.subject_addtogpa and subject.final_grade.add_to_gpa:
                                actual_hours = actual_hours + credit_hours
                            points = subject.course_id.course_grade_ids.filtered(
                                lambda l: l.grade_id.id == subject.final_grade.id).points_from
                            semester_points = semester_points + (points * credit_hours)
                    if actual_hours > 0:
                        semester_current_gpa = (semester_points / actual_hours)
                    accum_semesters.sudo().write(
                        {'semester_gpa': float(semester_current_gpa), 'current_gpa': float(semester_current_gpa),
                         'semester_hr': earned_hours, 'earned_hours': earned_hours,
                         'registered_hours': registered_hours,
                         'actual_hours': actual_hours, 'semester_points': semester_points,
                         'semester_current_gpa': float(semester_current_gpa)})
                    level = self.env['op.course.levels'].sudo().search(
                    [('course_id', '=', student.course_id.id),
                     ('hours_from', '<=', student.new_crh),
                     ('hours_to', '>', student.new_crh)], limit=1).level_id.id  # 'level': (level),
                
                    student.write({'level': level, 'new_gpa': float(semester_current_gpa),
                                   'new_crh': earned_hours})
    
    
    @api.model
    def _cron_calculate_student_semster_gpa_hours(self, course_id=None, std_id=None):
        if course_id:
            students = self.env['op.student'].sudo().search([('course_id', '=', int(course_id))])
        elif std_id:
            students = self.env['op.student'].sudo().search([('id', '=', int(std_id))])
        else:
            students = self.env['op.student'].sudo().search([])
        academic_years = self.env['op.academic.year'].sudo().search([('sequence', '!=', 0)], order='sequence asc')
        semesters = self.env['op.semesters'].sudo().search([], order='id asc')
        print("############IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII#############")
        print(self.check_block)
        print("############IIIIIIIIITTTTTTTIIIIIIIIIII#############")
        if self.check_block != False:
            raise ValidationError('Student Blocked !!!!')
        for student in students:
            for academic_year in academic_years:
                print("###############3333333333333333##########")
                print(academic_year.name)
                for semester in semesters:
                    print("#################333333333333333333#############")
                    print(semester.name)
                    accum_semesters_subjects = self.env['op.student.semesters.subjects'].sudo().search(
                        [('subject_grade', '!=', False), ('student_id', '=', student.id),
                         ('academicyear_id', '=', academic_year.id), ('semester_id', '=', semester.id),
                         ('student_semester_id.transferred', '=', False)])
                    accum_semesters_subjects = accum_semesters_subjects
                    subject_ids = accum_semesters_subjects.mapped('subject_id').ids
                    subject_ids = list(dict.fromkeys(subject_ids))
                    numerator = 0  # بسط فوق
                    denominator = 0  # مقام
                    crh_denominator = 0
                    crh_core = 0
                    crh_elective = 0
                    crh_project = 0
                    for subject in subject_ids:
                        accum_subject = self.env['op.student.semesters.subjects'].sudo().search(
                            [('subject_grade', '!=', False), ('subject_id', '=', subject),
                             ('student_id', '=', student.id)])
    
                        published = self.check_is_published(accum_subject.course_id.id, accum_subject.academicyear_id.id,
                                                      accum_subject.semester_id.id)
                        if not published:
                            continue
                        # print(accum_subject.subject_id.subject_name)
                        subject_grade = accum_subject.final_grade
                        if subject_grade.pass_grade:
                            crh_denominator = crh_denominator + accum_subject.subject_id.subject_credithours
                            if accum_subject.subject_id.subject_type.id == 1:
                                crh_core += accum_subject.subject_id.subject_credithours
                            if accum_subject.subject_id.subject_type.id == 2:
                                crh_elective += accum_subject.subject_id.subject_credithours
                            if accum_subject.subject_id.subject_type.id == 3:
                                crh_project += accum_subject.subject_id.subject_credithours
                        if accum_subject.subject_id.subject_addtogpa and subject_grade.add_to_gpa:
                            # print(accum_subject.subject_id.subject_name)
                            grade_points = self.env['op.course.grades'].sudo().search(
                                [('course_id', '=', student.course_id.id),
                                 ('grade_id', '=', subject_grade.id)], limit=1).points_from
                            denominator = denominator + accum_subject.subject_id.subject_credithours
                            numerator = numerator + (
                                round((grade_points * accum_subject.subject_id.subject_credithours), 3))
                    if subject_ids:
                        if denominator > 0:
                            print(numerator)
                            print(denominator)
                            numerator = round(numerator, 2)
                            new_gpa = numerator / denominator
                            new_gpa = round(new_gpa, 2)
                            print(new_gpa)
                            print(crh_core)
        _logger.info("Cron job executed successfully.")
    
    
    @api.model
    def _cron_calculate_degree(self, course_id=None, std_id=None , lmt=100, ofst=0):
        if course_id:
            students = self.env['op.student'].sudo().search(
                [('student_status', 'in', (48,55)),('final_degree', '=', False), ('course_id', '=', int(course_id))],limit=lmt, offset=ofst)
        elif std_id:
            students = self.env['op.student'].sudo().search([('student_status', 'in', (48,55)),('level', '=', False), ('id', '=', int(std_id))])
        else:
            students = self.env['op.student'].sudo().search([('student_status', 'in', (48,55)),('level', '=', False)])
        for student in students:
            print(student)
            gpa = 0
            accum_semesters_subjects = self.env['op.student.semesters.subjects'].sudo().search(
                [('subject_grade', '!=', False), ('student_id', '=', student.id),
                 ('final_grade.pass_grade', '=', True), ('final_grade', 'not in', [20, 4, 6,27]),
                 ('student_semester_id.transferred', '=', False)])
            accum_semesters_subjects = accum_semesters_subjects
            subject_ids = accum_semesters_subjects.mapped('subject_id').ids
            subject_ids = list(dict.fromkeys(subject_ids))
            numerator = 0  # بسط فوق
            denominator = 0  # مقام
            for subject in subject_ids:
                accum_subject = self.env['op.student.semesters.subjects'].sudo().search(
                    [('subject_grade', '!=', False), ('subject_id', '=', subject),
                     ('final_grade.pass_grade', '=', True), ('final_grade', 'not in', [20, 4, 6,27]),
                     ('student_id', '=', student.id), ('student_semester_id.transferred', '=', False)], order='final_degree desc', limit=1)
                # for accum_subjec in accum_subject:
                #     print(accum_subjec.subject_id.subject_name)
                #     print(accum_subjec.final_degree)
                published = self.check_is_published(accum_subject.course_id.id, accum_subject.academicyear_id.id,
                                              accum_subject.semester_id.id)
                if not published:
                    continue
                subject_grade = accum_subject.final_grade
                if subject_grade.pass_grade and subject_grade.id not in [20, 4, 6,27]:
                    print(accum_subject.subject_id.subject_name)
                    print(accum_subject.final_degree)
                    denominator = denominator + accum_subject.subject_id.subject_total
                    numerator = numerator + accum_subject.final_degree
            if subject_ids:
                if denominator > 0:
                    print(numerator)
                    print(denominator)
                    numerator = numerator
                    final_degree = numerator / denominator
                    print('111111111111111111111111')
                    print(final_degree)
                    final_degree = final_degree * 100
                    final_degree = round(final_degree+10**(-len(str(final_degree))-1), 2)  
                    print(final_degree)
                    #final_degree = round(final_degree+10**(-len(str(final_degree))-1), 2) * 100
                    print(final_degree)
                    print('2222222222222222222222222')
                    total_degree = numerator
                    subject_degree = denominator
                    student.write(
                        {'final_degree': final_degree, 'total_degree': total_degree, 'subject_degree': subject_degree})               
        
        _logger.info("Cron job executed successfully.")
    
    
    
    def calc_student_gpa2(self, student , subject , hours):
        studentcrh =0
        studentnewcrh =0
        studentcore =0
        if hours : 
            studentcrh = student.crh - subject.subject_credithours
            studentnewcrh = student.new_crh - subject.subject_credithours
            studentcore = student.project_crh - subject.subject_credithours
            stuSubs = self.env['op.student.semesters.subjects'].sudo().search([('subject_id', '=', subject.id),('student_id', '=', student.id)]) 
            if stuSubs: 
                student.sudo().write({'crh': studentcrh, 'new_crh': studentnewcrh, 'project_crh': studentcore
                                      , 'timestamp' : datetime.today().strftime("%Y-%m-%d %H:%M:%S")})
        else:
            studentcrh = student.crh + subject.subject_credithours
            studentnewcrh = student.new_crh + subject.subject_credithours
            studentcore = student.project_crh + subject.subject_credithours
            stuSubs = self.env['op.student.semesters.subjects'].sudo().search([('subject_id', '=', subject.id),('student_id', '=', student.id)]) 
            if stuSubs:
                student.sudo().write({'crh': studentcrh, 'new_crh': studentnewcrh, 'project_crh': studentcore
                                      , 'timestamp' : datetime.today().strftime("%Y-%m-%d %H:%M:%S")})
                
    
    
    def calc_student_gpa(self):
        gpa = 0
        accum_semesters_subjects = self.env['op.student.semesters.subjects'].sudo().search(
            [('subject_grade', '!=', False), ('student_id', '=', self.id),
             ('student_semester_id.transferred', '=', False)])
        accum_semesters_subjects = accum_semesters_subjects
        subject_ids = accum_semesters_subjects.mapped('subject_id').ids
        subject_ids = list(dict.fromkeys(subject_ids))
        numerator = 0  # بسط فوق
        denominator = 0  # مقام
        crh_denominator = 0
        crh_core = 0
        crh_elective = 0
        crh_project = 0
        new_gpa = 0
        for subject in subject_ids:

            accum_subject = self.env['op.student.semesters.subjects'].sudo().search(
                [('subject_grade', '!=', False), ('subject_id', '=', subject), ('student_id', '=', self.id),
                 ('student_semester_id.transferred', '=', False)])
            if len(accum_subject) > 1:
                sel_accum_subjects = self.env['op.student.semesters.subjects'].sudo().search(
                    [('subject_grade', '!=', False), ('subject_id', '=', subject),
                     ('student_id', '=', self.id)],
                    order='academicyear_id  asc,semester_id desc')
                for sel_accum_subject in sel_accum_subjects:
                    published = self.check_is_published(sel_accum_subject.course_id.id,
                                                  sel_accum_subject.academicyear_id.id,
                                                  sel_accum_subject.semester_id.id)
                    if not published:
                        continue
                    subject_grade = sel_accum_subject.final_grade
                    if not subject_grade.pass_grade and not subject_grade.add_to_gpa:
                        continue
                    elif not subject_grade.pass_grade and subject_grade.add_to_gpa:
                        if sel_accum_subject.subject_id.subject_addtogpa:
                            grade_points = self.env['op.course.grades'].sudo().search(
                                [('course_id', '=', self.course_id.id),
                                 ('grade_id', '=', subject_grade.id)],
                                limit=1).points_from

                            denominator = denominator + sel_accum_subject.subject_id.subject_credithours
                            numerator = numerator + (
                                round((grade_points * sel_accum_subject.subject_id.subject_credithours), 3))
                            break
                    elif subject_grade.pass_grade and subject_grade.add_to_gpa:
                        de_accum_subjects = self.env['op.student.semesters.subjects'].sudo().search(
                            [('subject_grade', '!=', False), ('subject_id', '=', subject),
                             ('student_id', '=', self.id), ('id', '!=', sel_accum_subject.id),
                             ], order='final_degree  desc')
                        for de_accum_subject in de_accum_subjects.sorted(key=lambda r: r.final_degree,
                                                                         reverse=True):
                            published = self.check_is_published(de_accum_subject.course_id.id,
                                                          de_accum_subject.academicyear_id.id,
                                                          de_accum_subject.semester_id.id)
                            if not published:
                                continue
                            if de_accum_subject.final_degree > sel_accum_subject.final_degree:
                                subject_grade = de_accum_subject.final_grade
                                if subject_grade.pass_grade and subject_grade.add_to_gpa:
                                    sel_accum_subject = de_accum_subject
                                    break
                        crh_denominator = crh_denominator + sel_accum_subject.subject_id.subject_credithours
                        if sel_accum_subject.subject_id.subject_type.id == 1:
                            crh_core += sel_accum_subject.subject_id.subject_credithours
                        if sel_accum_subject.subject_id.subject_type.id == 2:
                            crh_elective += sel_accum_subject.subject_id.subject_credithours
                        if sel_accum_subject.subject_id.subject_type.id == 3:
                            crh_project += sel_accum_subject.subject_id.subject_credithours

                        if sel_accum_subject.subject_id.subject_addtogpa:
                            grade_points = self.env['op.course.grades'].sudo().search(
                                [('course_id', '=', self.course_id.id),
                                 ('grade_id', '=', subject_grade.id)],
                                limit=1).points_from

                            denominator = denominator + sel_accum_subject.subject_id.subject_credithours
                            numerator = numerator + (round((
                                    grade_points * sel_accum_subject.subject_id.subject_credithours), 3))
                            break
                    elif subject_grade.pass_grade and not subject_grade.add_to_gpa:
                        crh_denominator = crh_denominator + sel_accum_subject.subject_id.subject_credithours
                        if sel_accum_subject.subject_id.subject_type.id == 1:
                            crh_core += sel_accum_subject.subject_id.subject_credithours
                        if sel_accum_subject.subject_id.subject_type.id == 2:
                            crh_elective += sel_accum_subject.subject_id.subject_credithours
                        if sel_accum_subject.subject_id.subject_type.id == 3:
                            crh_project += sel_accum_subject.subject_id.subject_credithours
                        break

            else:
                published = self.check_is_published(accum_subject.course_id.id, accum_subject.academicyear_id.id,
                                              accum_subject.semester_id.id)
                if not published:
                    continue
                subject_grade = accum_subject.final_grade
                if subject_grade.pass_grade:
                    crh_denominator = crh_denominator + accum_subject.subject_id.subject_credithours
                    if accum_subject.subject_id.subject_type.id == 1:
                        crh_core += accum_subject.subject_id.subject_credithours
                    if accum_subject.subject_id.subject_type.id == 2:
                        crh_elective += accum_subject.subject_id.subject_credithours
                    if accum_subject.subject_id.subject_type.id == 3:
                        crh_project += accum_subject.subject_id.subject_credithours
                if accum_subject.subject_id.subject_addtogpa and subject_grade.add_to_gpa:
                    grade_points = self.env['op.course.grades'].sudo().search(
                        [('course_id', '=', self.course_id.id),
                         ('grade_id', '=', subject_grade.id)], limit=1).points_from
                    denominator = denominator + accum_subject.subject_id.subject_credithours
                    numerator = numerator + (
                        round((grade_points * accum_subject.subject_id.subject_credithours), 3))
        if subject_ids:
            if denominator > 0:
                numerator = round(numerator, 2)
                new_gpa = numerator / denominator
                new_gpa = round(new_gpa, 2)
        return new_gpa
    
    
    
    @api.model
    def _cron_calculate_gpa(self, course_id=None, std_id=None):
        if course_id:
            students = self.env['op.student'].sudo().search([('course_id', '=', int(course_id))])
        elif std_id:
            students = self.env['op.student'].sudo().search([('id', '=', int(std_id))])
        else:
            students = self.env['op.student'].sudo().search([])
    
        for student in students:
            print(student)
            gpa = 0
            accum_semesters_subjects = self.env['op.student.semesters.subjects'].sudo().search(
                [('subject_grade', '!=', False), ('student_id', '=', student.id),
                 ('student_semester_id.transferred', '=', False)])
    
            accum_semesters_subjects = accum_semesters_subjects
            print(accum_semesters_subjects)
            subject_ids = accum_semesters_subjects.mapped('subject_id').ids
            subject_ids = list(dict.fromkeys(subject_ids))
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
                        [('subject_grade', '!=', False), ('subject_id', '=', subject), ('student_id', '=', student.id)],
                        order='academicyear_id  asc,semester_id desc')
                    print("sssssssssss")
                    print(sel_accum_subjects)
                    print("sssssssssss")
                    for sel_accum_subject in sel_accum_subjects:
                        print("newwwwwwwwwwwwwww")
                        print(sel_accum_subject.subject_id.subject_name)
                        print(sel_accum_subject)
                        print("newwwwwwwwwwwwwww")
                        published = self.check_is_published(sel_accum_subject.course_id.id,
                                                      sel_accum_subject.academicyear_id.id,
                                                      sel_accum_subject.semester_id.id)
                        if not published:
                            continue
                        print("newwwwwwwwwwwwwww1111")
                        print(sel_accum_subject)
                        print("newwwwwwwwwwwwwww1111")
                        print("0")
                        print(sel_accum_subject.subject_id.subject_name)
                        subject_grade = sel_accum_subject.final_grade
                        if not subject_grade.pass_grade and not subject_grade.add_to_gpa:
                            print("1")
                            print(sel_accum_subject.subject_id.subject_name)
                            continue
                        elif not subject_grade.pass_grade and subject_grade.add_to_gpa:
                            print("2")
                            if sel_accum_subject.subject_id.subject_addtogpa:
                                print("2")
                                print(sel_accum_subject.subject_id.subject_name)
                                grade_points = self.env['op.course.grades'].sudo().search(
                                    [('course_id', '=', student.course_id.id),
                                     ('grade_id', '=', subject_grade.id)],
                                    limit=1).points_from
    
                                denominator = denominator + sel_accum_subject.subject_id.subject_credithours
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
                                 ('student_id', '=', student.id), ('id', '!=', sel_accum_subject.id),
                                 ], order='final_degree  desc')
                            for de_accum_subject in de_accum_subjects.sorted(key=lambda r: r.final_degree,
                                                                             reverse=True):
                                published = self.check_is_published(de_accum_subject.course_id.id,
                                                              de_accum_subject.academicyear_id.id,
                                                              de_accum_subject.semester_id.id)
                                if not published:
                                    continue
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
                            if sel_accum_subject.subject_id.subject_type.id == 1:
                                crh_core += sel_accum_subject.subject_id.subject_credithours
                            if sel_accum_subject.subject_id.subject_type.id == 2:
                                crh_elective += sel_accum_subject.subject_id.subject_credithours
                            if sel_accum_subject.subject_id.subject_type.id == 3:
                                crh_project += sel_accum_subject.subject_id.subject_credithours
    
                            if sel_accum_subject.subject_id.subject_addtogpa:
                                grade_points = self.env['op.course.grades'].sudo().search(
                                    [('course_id', '=', student.course_id.id),
                                     ('grade_id', '=', subject_grade.id)],
                                    limit=1).points_from
    
                                denominator = denominator + sel_accum_subject.subject_id.subject_credithours
                                numerator = numerator + (round((
                                        grade_points * sel_accum_subject.subject_id.subject_credithours), 3))
                                break
                        elif subject_grade.pass_grade and not subject_grade.add_to_gpa:
                            print("4")
                            print(sel_accum_subject.subject_id.subject_name)
                            crh_denominator = crh_denominator + sel_accum_subject.subject_id.subject_credithours
                            if sel_accum_subject.subject_id.subject_type.id == 1:
                                crh_core += sel_accum_subject.subject_id.subject_credithours
                            if sel_accum_subject.subject_id.subject_type.id == 2:
                                crh_elective += sel_accum_subject.subject_id.subject_credithours
                            if sel_accum_subject.subject_id.subject_type.id == 3:
                                crh_project += sel_accum_subject.subject_id.subject_credithours
                            break
    
                else:
                    published = self.check_is_published(accum_subject.course_id.id, accum_subject.academicyear_id.id,
                                                  accum_subject.semester_id.id)
                    if not published:
                        continue
                    # print(accum_subject.subject_id.subject_name)
                    subject_grade = accum_subject.final_grade
                    print("ddddddddd")
                    print(accum_subject.subject_id.subject_name)
                    if subject_grade.pass_grade:
                        crh_denominator = crh_denominator + accum_subject.subject_id.subject_credithours
                        if accum_subject.subject_id.subject_type.id == 1:
                            crh_core += accum_subject.subject_id.subject_credithours
                        if accum_subject.subject_id.subject_type.id == 2:
                            crh_elective += accum_subject.subject_id.subject_credithours
                        if accum_subject.subject_id.subject_type.id == 3:
                            crh_project += accum_subject.subject_id.subject_credithours
                    if accum_subject.subject_id.subject_addtogpa and subject_grade.add_to_gpa:
                        # print(accum_subject.subject_id.subject_name)
                        grade_points = self.env['op.course.grades'].sudo().search(
                            [('course_id', '=', student.course_id.id),
                             ('grade_id', '=', subject_grade.id)], limit=1).points_from
                        denominator = denominator + accum_subject.subject_id.subject_credithours
                        numerator = numerator + (
                            round((grade_points * accum_subject.subject_id.subject_credithours), 3))
                        print(accum_subject.subject_id.subject_name)
                        print((grade_points * accum_subject.subject_id.subject_credithours))
            if subject_ids:
                print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
                if denominator > 0:
                    print(numerator)
                    print(denominator)
                    numerator = round(numerator, 2)
                    new_gpa = numerator / denominator
                    print(new_gpa)
                    new_gpa = round(new_gpa, 2)
                    print(new_gpa)
                    print(Decimal(new_gpa).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP))
                    print(crh_core)
                    conflict_gpa = False
                    conflict_crh = False
                    if new_gpa != student.cgpa:
                        conflict_gpa = True
                    if crh_denominator != student.crh:
                        conflict_crh = True
                    student.write({'conflict_gpa': (conflict_gpa), 'conflict_crh': (conflict_crh), 'new_gpa': (new_gpa),
                                   'new_crh': crh_denominator, 'core_crh': crh_core, 'elective_crh': crh_elective,
                                   'project_crh': crh_project})
        
        _logger.info("Cron job executed successfully.")
    
    
    
    def round_decimals_up(self, number, decimals=2):
        """
        Returns a value rounded up to a specific number of decimal places.
        """
        if not isinstance(decimals, int):
            raise TypeError("decimal places must be an integer")
        elif decimals < 0:
            raise ValueError("decimal places has to be 0 or more")
        elif decimals == 0:
            return math.ceil(number)

        factor = 10 ** decimals
        return math.ceil(number * factor) / factor
    
    
    
    def gpa_calc_view(self):
        self.ensure_one()
        print("111111111111111111111111111111")
        print("student:-----------", self.id)
        domain = [
            ('student_id', '=', self.id)]
        return {
            'name': _('Gpa Calculator'),
            'domain': domain,
            'res_model': 'hue.gpa.calculator',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                           Click to Create for New Gpa Calculator
                        </p>'''),
            'limit': 80,
            'context': "{'default_student_id': '%s'}" % self.id
        }
    
    #transferred from registration missing model for trial
    def student_registration(self):
        """ Open the website page with the survey form into test mode"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'name': "Start Advising",
            'target': 'self',
            'url': self.env['ir.config_parameter'].sudo().get_param('web.base.url') + "/registration/" + str(self.id)
        }