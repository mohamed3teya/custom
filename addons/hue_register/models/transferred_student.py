from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime
import math
import logging

_logger = logging.getLogger(__name__)


class universityTransfer(models.Model):
    _name = 'hue.university.transfer'
    _description = 'hue.university.transfer'
    
    name = fields.Char( string='university name')
    country_id = fields.Many2one('res.country')
    
    
class TransferredStudent(models.Model):
    _name = 'transferred.student'
    _description = 'transferred.student'
    _inherit = ['mail.thread']
    _rec_name = 'student_id'

    
    student_subjects = fields.One2many('transferred.student.subjects','transferred_id', string="Students")
    course_id = fields.Many2one('op.course', string='Course', required=True , tracking=True)
    parent_id = fields.Many2one('op.course', related='course_id.parent_id', store=True)
    student_id = fields.Many2one('op.student',required=True, tracking=True, domain="[('id', 'in', suitable_student_ids)]")
    suitable_student_ids = fields.Many2many('op.student', compute='_compute_suitable_student_ids',) #to add domain to student under course only
    student_code = fields.Integer(related='student_id.student_code', readonly=True, store=True)
    advisor = fields.Char(compute="_advisor")
    academic_year_id = fields.Many2one('op.academic.year', string='Academic Year', required=True , tracking=True)
    semester_id = fields.Many2one('op.semesters', string='Joined Semester', required=True , tracking=True)
    date = fields.Datetime(string='Date', required=True, default=datetime.today())
    transfer_type = fields.Selection([('internal', 'internal'), ('external', 'external')], required=True, default='external', tracking=True)
    university_id = fields.Many2one('hue.university.transfer' , string='T.university',tracking=True)
    university_country = fields.Many2one('res.country' ,string='T.university country')
    earned_hour = fields.Float(compute="_get_gpa" ,string="T.earned hour")
    gpa = fields.Float(compute="_get_gpa" ,string="semester gpa")
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')],
                                 string='State', required=True, default='draft', tracking=True)
    
    
    @api.depends('student_id')
    def _advisor(self):
        for rec in self:
            advisor_name = self.env['hue.academic.direction.line'].sudo().search([('student_id', '=', rec.student_id.id), ('to_date', '=', False)])
            rec.advisor = advisor_name.faculty_id.name                                    
    

    @api.depends('student_id')
    def _get_gpa(self):
        accum_student = self.env['op.student.accumlative.semesters'].sudo().search([('student_id', '=', self.student_id.id),
           ('transferred', '=', False), ('semester_id', '=', 4),('academicyear_id', '=', self.academic_year_id.id)])
        self.earned_hour = accum_student.semester_hr
        self.gpa = accum_student.semester_gpa
        
        
    @api.constrains('student_id' ,'course_id','academic_year_id' ,'semester_id')
    def _check_date(self):
        for rec in self:
            domain = [
                ('student_id', '=', rec.student_id.id),
                ('academic_year_id', '=', rec.academic_year_id.id),
                ('semester_id', '=', rec.semester_id.id), 
                ('id', '!=', rec.id),
            ]
            std_transferred = rec.search(domain)         
            if std_transferred:
                raise ValidationError(('You can not have 2  transferred  of the same student !' ))
    
    
    @api.onchange('course_id')
    def _compute_suitable_student_ids(self):
        for rec in self:
            # rec.student_id = False
            students = self.env['op.student'].sudo().search([('faculty', '=', rec.course_id.faculty_id.id),('student_status.name', '=', 'مستجد')])
            print("students:-------------", students)
            rec.suitable_student_ids = students.ids
    
    
    # def onchange_course_id(self):
    #     for rec in self:
    #         rec.student_id = False
    #         students = self.env['op.student'].sudo().search([('faculty', '=', rec.course_id.faculty_id.id),('student_status', '=', 1)])
    #         #uncomment when group_service_manager is added
    #         # if self.env.ref('hr_extention.group_service_manager') in self.env.user.groups_id :
    #         #     course_id = self.env['op.course'].sudo().search([])
    #         # else:
    #         #     emp = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)])
    #         #     course_id = self.env['op.course'].sudo().search([('id', '=', emp.course_ids.ids)])
    #         course_id = self.env['op.course'].sudo().search([])
    #         domain = {'course_id': [('id', 'in', course_id.ids)] ,'student_id': [('id', 'in', students.ids)]} 
    #         return {'domain': domain}
    
        
    @api.onchange('university_country')
    def onchange_country(self):
        self.university_id = False
        for rec in self:
            rec.university_id = False
            unversities = self.env['hue.university.transfer'].sudo().search([('country_id', '=', rec.university_country.id)])
            domain = {'university_id': [('id', 'in', unversities.ids)]} 
            return {'domain': domain}
    

    def get_draft(self):
        self.write({'state': 'draft'})

        
    def button_done(self):
        Semsters = self.env['op.student.accumlative.semesters'].sudo().search([('student_id', '=', self.student_id.id)])  
        for sem in Semsters :
            if sem.academicyear_id.id < self.academic_year_id.id  :
                sem.write({'transferred': True })
            elif sem.academicyear_id.id == self.academic_year_id.id  :
                if sem.semester_id.id < self.semester_id.id  :
                    sem.write({'transferred': True })
                if sem.semester_id.id == 4  and sem.course_id.id != self.course_id.id :
                    sem.write({'transferred': True })

                        
        stuAccID = self.env['op.student.accumulative'].sudo().search([('student_id', '=', self.student_id.id), ('course_id', '=',self.course_id.id),('academicyear_id', '=', self.academic_year_id.id)])
        if not stuAccID:
            stuAccID = self.env['op.student.accumulative'].sudo().create({'student_id': self.student_id.id, 'course_id': self.course_id.id, 'academicyear_id': self.academic_year_id.id})
        StuAccSemID = self.env['op.student.accumlative.semesters'].sudo().search([('student_accum_id', '=', stuAccID.id), ('semester_id', '=', 4)])
        if not StuAccSemID:
            StuAccSemID = self.env['op.student.accumlative.semesters'].sudo().create({'student_accum_id': stuAccID.id, 'academicyear_id': self.academic_year_id.id, 'semester_id': 4, 'semester_status':2})

        for subject in self.student_subjects :
            stuSemSubID = self.env['op.student.semesters.subjects'].sudo().search([('student_semester_id', '=', StuAccSemID.id),('subject_id', '=', subject.subject_id.id)])
            if stuSemSubID:
                stuSemSubID.sudo().write({'subject_degree': subject.degree, 'subject_grade': subject.grade.id, 'final_grade': subject.grade.id})
                stuSemSubs = self.env['op.student.semesters.subjects'].sudo().search([('student_semester_id', '=', StuAccSemID.id)])
                for subj in stuSemSubs :
                    if subj.subject_id != subject.subject_id:
                        subj.unlink()
            else:
                self.env['op.student.semesters.subjects'].sudo().create(
                    {'academicyear_id': self.academic_year_id.id,'semester_id': 4,'student_semester_id': StuAccSemID.id, 'subject_id': subject.subject_id.id,
                   'subject_degree': subject.degree, 'subject_grade': subject.grade.id, 'final_grade': subject.grade.id})
        data = self.env['op.student'].student_calculate_transferred_data(self.student_id, self.academic_year_id, self.semester_id)
        
        std_previous_course_id = self.env['op.student'].sudo().search([('id', '=', self.student_id.id)])
        previous_course_id = std_previous_course_id.write({'previous_course_id': std_previous_course_id.course_id.id,'transfer_type':self.transfer_type})
        new_course_id = std_previous_course_id.write({'course_id' :self.course_id.id})
        if self.university_id :
            self.student_id.write({'university_name': self.university_id.id})
        if self.university_country :
            self.student_id.write({'university_country':self.university_country.id})
        self.write({'state': 'done'})
    
    
    def unlink(self):
        for rec in self:
            stuAccID = self.env['op.student.accumulative'].sudo().search([('student_id', '=', rec.student_id.id), ('course_id', '=',rec.course_id.id),('academicyear_id', '=', rec.academic_year_id.id)])   
            StuAccSemIDREC = self.env['op.student.accumlative.semesters'].sudo().search([('student_accum_id', '=', stuAccID.id), ('semester_id', '=', 4), ('academicyear_id', '=', rec.academic_year_id.id), ('semester_status', '=', 2)])
            student_id =self.env['op.student'].sudo().search([('id', '=', rec.student_id.id)])
            if StuAccSemIDREC:
                StuAccSemIDREC.unlink()
                std_previous_course_id = self.env['op.student'].sudo().search([('id', '=', rec.student_id.id)])
                new_course_id = std_previous_course_id.write({'course_id': std_previous_course_id.previous_course_id.id})
                pre_course_id = std_previous_course_id.write({'previous_course_id': False,'transfer_type':False})
            if self.university_id:
                student_id.write({'university_name': False})
            if self.university_country:
                student_id.write({'university_country': False})
                
                
            super(TransferredStudent, rec).unlink()


    def get_subjects(self):
        current_subjects  = self.env['transferred.student.subjects'].sudo().search([('transferred_id', '=', self.id)]).mapped('subject_id').ids
        stuSemSubIDs = self.env['op.student.semesters.subjects'].sudo().search([('student_id', '=', self.student_id.id)],order="final_degree DESC")
        for subject in stuSemSubIDs:
            if subject.final_grade :                
                current_subject  = self.env['transferred.student.subjects'].sudo().search([('subject_id', '=', subject.subject_id.id),('transferred_id', '=', self.id)]).id
                if not current_subject  :
                    self.env['transferred.student.subjects'].sudo().create(
                    {'transferred_id': self.id,'subject_id':subject.subject_id.id,'grade': subject.final_grade.id})
                   
                    
    def write(self, values):
        if 'student_subjects' in values:
            student_subjects = values['student_subjects']
            message = "<div>\n"
            for sub in student_subjects :
                if sub[0] == 1 :
                    subject = self.env['transferred.student.subjects'].sudo().search([('id', '=', sub[1])])
                    message += "<strong>Edit subject : " + subject.subject_id.subject_id.name + "</strong>  <br/>   "
                    message += "<strong> Assessment : </strong>  <br/>   "
                    message += "<ul class=\"o_mail_thread_message_tracking\"> \n"
                    for key, value in sub[2].items():
                        subject_ass = subject.read([str(key)])
                        message += "<li> <span>  " + str(key) + " : </span><span>" + str(subject_ass[0][str(key)]) + "</span> <span> --> </span><span>" + str(value) + "</span></li> \n"
                    message += "</ul>"
                elif sub[0] == 2 :
                    subject = self.env['transferred.student.subjects'].sudo().search([('id', '=', sub[1])])
                    message += "<strong>Delete subject : " + subject.subject_id.subject_id.name + "</strong>  <br/>   "
                elif sub[0] == 0 :
                    subject = self.env['op.subject'].sudo().search([('id', '=', sub[2]['subject_id'])])
                    # subject = self.env['transferred.student.subjects'].sudo().search([('subject_id', '=', sub[2]['subject_id'])])
                    message += "<strong>Create subject : " + subject.subject_id.name  + "</strong>  <br/>   "
            message += "</div>"
            self.message_post(body=message, subject="Mark Changed")
        res = super(TransferredStudent, self).write(values)
        return res
    
    
    @api.model_create_multi
    def create(self,values):
        if 'student_subjects' in values:
            student_subjects = values['student_subjects']
            message = "<div>\n"
            for sub in student_subjects :
                if sub[0] == 0 :
                    subject = self.env['op.subject'].sudo().search([('id', '=', sub[2]['subject_id'])])
                    message += "<strong>Create subject : " + subject.subject_id.name  + "</strong>  <br/>   "
            message += "</div>"
            self.message_post(body=message, subject="Mark Changed")
        res = super(TransferredStudent, self).create(values)
        return res
    

class TransferredStudentSubjects(models.Model):
    _name = 'transferred.student.subjects'
    _description = 'transferred.student.subjects'
    inherit = ['mail.thread']


    transferred_id = fields.Many2one('transferred.student', string='Control', ondelete='cascade', required=True, index=True)
    seq = fields.Integer('#', readonly=True)
    subject_id = fields.Many2one('op.subject', string='Subject', required=True, domain="[('id', 'in', suitable_subject_ids)]")
    suitable_subject_ids = fields.Many2many('op.subject', compute='_compute_suitable_subject_ids') #to add domain to subjects
    sub_code = fields.Char(related='subject_id.code', readonly=True, store=True)
    sub_credit = fields.Integer(related='subject_id.subject_credithours', readonly=True, store=True)
    grade = fields.Many2one('op.grades',string='Grade', required=True, domain="[('id', 'in', suitable_grade_ids)]")
    suitable_grade_ids = fields.Many2many('op.grades', compute='_compute_suitable_subject_ids') #to add domain to grades
    degree =fields.Float( string='Degree')
    
    
    @api.onchange('subject_id')
    def _compute_suitable_subject_ids(self):
        for rec in self:
            subjects = self.env['op.subject'].sudo().search(['|',('course_id', '=', rec.transferred_id.course_id.id),('course_id', '=', rec.transferred_id.course_id.parent_id.id)])
            rec.suitable_subject_ids = subjects.ids
            if rec.subject_id.subject_passorfail != False:
                grades = self.env['op.grades'].sudo().search([('name','in',['FC|FC','PC|PC','P|P','NP|NP'])])
            else:
                grades = self.env['op.grades'].sudo().search([])
            rec.suitable_grade_ids = grades.ids


    @api.constrains('subject_id')
    def _check_date(self):
        for rec in self:
            domain = [
                ('subject_id', '=', rec.subject_id.id),
                ('transferred_id', '=', rec.transferred_id.id),
                ('id', '!=', rec.id),
            ]
            std_subj = rec.search(domain)         
            if std_subj:
                raise ValidationError(('You can not have 2  record  of the same subject ! "' + rec.subject_id.name + ' " '))