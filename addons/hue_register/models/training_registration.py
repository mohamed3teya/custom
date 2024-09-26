from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class SubjectReg(models.Model):
    _name = 'training.field.registration'
    _description = 'training.field.registration'
    _inherit = ['mail.thread']

    student_ids = fields.One2many('training.students','std_subject_id', string="Students")
    course_id = fields.Many2one('op.course', string='Course', required=True , tracking=True)
    academic_year_id = fields.Many2one('op.academic.year', string='Academic Year', required=True , tracking=True)
    semester_id = fields.Many2one('op.semesters', string='Semester', required=True , tracking=True)
    subject_id = fields.Many2one('op.subject', string='Subject', required=True , tracking=True)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')],
                                 string='State', required=True, default='draft', tracking=True)
    tree_clo_acl_ids = fields.Char()#compute='_compute_tree_clo_acl_ids', search='tree_clo_acl_ids_search'
    
    @api.depends('course_id')
    def _compute_tree_clo_acl_ids(self):
        print('View My Tree CLO ACL')
    
    def tree_clo_acl_ids_search(self, operator, operand):
        if self.env.ref('hr_extention.group_service_manager') in self.env.user.groups_id:
            return [('id', 'in', self.sudo().search([]).ids)]
        emp = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)])
        courses = emp.course_ids.ids
        records = self.sudo().search([('course_id', 'in', courses)]).ids
        return [('id', 'in', records)]

  
     
    # @api.onchange('course_id')
    # def onchange_course_id(self):
    #     for rec in self:
    #         rec.subject_id = False
    #         subjects = self.env['op.subject'].sudo().search(['|',('course_id', '=', rec.course_id.id),('course_id', '=', rec.course_id.parent_id.id),('summer_training', '=',True)])
    #         if self.env.ref('hr_extention.group_service_manager') in self.env.user.groups_id :
    #             course_id = self.env['op.course'].sudo().search([])
    #         else:
    #             emp = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)])
    #             course_id = self.env['op.course'].sudo().search([('id', '=', emp.course_ids.ids)])
    #   
    #         domain = {'course_id': [('id', 'in', course_id.ids)],'subject_id': [('id', 'in', subjects.ids)]}
    #         return {'domain': domain}
    
    
    def get_draft(self):
        self.write({'state': 'draft'})
        
    def button_done(self):              
        for stud in self.student_ids:
            before_semster_id = self.semester_id.id - 1
            stuAccID = self.env['op.student.accumulative'].sudo().search([('student_id', '=', stud.student_id.id), ('course_id', '=',self.course_id.id),('academicyear_id', '=', self.academic_year_id.id)])
            if not stuAccID:
                stuAccID = self.env['op.student.accumulative'].sudo().create({'student_id': stud.student_id.id, 'course_id': self.course_id.id, 'academicyear_id': self.academic_year_id.id})
            StuAccSemID = self.env['op.student.accumlative.semesters'].sudo().search([('student_accum_id', '=', stuAccID.id), ('semester_id', '=', self.semester_id.id)])
            if not StuAccSemID:
                StuAccSemID = self.env['op.student.accumlative.semesters'].sudo().create({'student_accum_id': stuAccID.id, 'academicyear_id': self.academic_year_id.id, 'semester_id': self.semester_id.id, 'semester_status':2})    
                if before_semster_id != 0 :
                    before_semster = self.env['op.student.accumlative.semesters'].sudo().search([('academicyear_id', '=', self.academic_year_id.id),('student_id', '=', stud.student_id.id),('semester_id', '=', before_semster_id)])
                    StuAccSemID.write({'current_gpa':before_semster.current_gpa })   
            stuSemSubID = self.env['op.student.semesters.subjects'].sudo().search([('student_semester_id', '=', StuAccSemID.id),('subject_id', '=', self.subject_id.id),('semester_id', '=', self.semester_id.id),
                ('academicyear_id', '=', self.academic_year_id.id),('student_id', '=', stud.student_id.id)])
            xx=self.env['op.student.accumlative.semesters'].sudo().search([('semester_id', '=', self.semester_id.id),
                ('academicyear_id', '=', self.academic_year_id.id),('student_id', '=', stud.student_id.id)])
            for y in xx.accum_semesters_subjects_ids :
                if len(xx.accum_semesters_subjects_ids) == 1 :
                    if y.subject_id.id  == self.subject_id.id :
                        before_semster_id = self.semester_id.id - 1
                    if before_semster_id != 0 :
                        before_semster = self.env['op.student.accumlative.semesters'].sudo().search([('academicyear_id', '=', self.academic_year_id.id),('student_id', '=', stud.student_id.id),('semester_id', '=', before_semster_id)])
                        StuAccSemID.write({'current_gpa':before_semster.current_gpa })   
                    
                    
            if not stuSemSubID:    
                stdrec=self.env['op.student.semesters.subjects'].sudo().create(
                        {'academicyear_id': self.academic_year_id.id,'semester_id':self.semester_id.id,'student_semester_id': StuAccSemID.id, 'subject_id': self.subject_id.id ,'student_id': stud.student_id.id ,'subject_grade': 27 ,'final_grade': 27}) 
            
                data = self.env['op.student'].calc_student_gpa2(stud.student_id,self.subject_id,False)
                semesterHr = self.env['op.student.accumlative.semesters'].sudo().search([('student_accum_id', '=', stuAccID.id), ('semester_id', '=', self.semester_id.id),
                    ('academicyear_id', '=', self.academic_year_id.id),('student_id', '=', stud.student_id.id)])
                semesterHr.write({'semester_hr':semesterHr.semester_hr+self.subject_id.subject_credithours })
              # DELETE
            stuSubs = self.env['op.student.semesters.subjects'].sudo().search([('subject_id', '=', self.subject_id.id),('semester_id', '=', self.semester_id.id),
                ('academicyear_id', '=', self.academic_year_id.id)])            
        self.write({'state': 'done'})
    
    
    def write(self, values):
        if 'student_ids' in values:
            student_ids =values['student_ids']
            message = "<div>\n"
            for std in student_ids :
                if std[0] ==1 :
                    student = self.env['training.students'].sudo().search([('id', '=', std[1])])
                    message += "<strong>Edit student : " + student.student_id.name + "</strong>  <br/>   "
                elif std[0] ==2 :
                    student = self.env['training.students'].sudo().search([('id', '=', std[1])])
                    message += "<strong>Delete student : " + student.student_id.name + "</strong>  <br/>   "
                    recId = self.env['training.students'].sudo().search([('id', '=', std[1])]) 
                    stdID = self.env['op.student.semesters.subjects'].sudo().search([('subject_id', '=', self.subject_id.id),('semester_id', '=', self.semester_id.id),
                            ('academicyear_id', '=', self.academic_year_id.id),('student_id', '=', recId.student_id.id)])       
                    data = self.env['op.student'].calc_student_gpa2(recId.student_id,self.subject_id,True)
                    semesterHr = self.env['op.student.accumlative.semesters'].sudo().search([('semester_id', '=', self.semester_id.id),
                    ('academicyear_id', '=', self.academic_year_id.id),('student_id', '=', recId.student_id.id)])
                    semesterHr.write({'semester_hr':semesterHr.semester_hr-self.subject_id.subject_credithours })
                    stdID.unlink()
                    batchID = self.env['op.student.accumlative.semesters'].sudo().search([('accum_semesters_subjects_ids', '=', False),('semester_id', '=', self.semester_id.id),
                            ('academicyear_id', '=', self.academic_year_id.id),('student_id', '=', recId.student_id.id)])
                    if batchID :
                        batchID.unlink()
            message += "</div>"
            self.message_post(body=message, student="Mark Changed")
        res = super(SubjectReg, self).write(values)
        return res    
        
        
    def unlink(self):
        for rec in self:
            stuAccID = self.env['op.student.accumulative'].sudo().search([('student_id', 'in', rec.student_ids.mapped('student_id').ids), ('course_id', '=',rec.course_id.id),('academicyear_id', '=', rec.academic_year_id.id)])   
            StuAccSemID = self.env['op.student.accumlative.semesters'].sudo().search([('student_accum_id', 'in', stuAccID.ids), ('semester_id', '=', rec.semester_id.id)])
            StuAccSemIDREC = self.env['op.student.semesters.subjects'].sudo().search([('student_semester_id', 'in', StuAccSemID.ids),('subject_id', '=', rec.subject_id.id),('semester_id', '=', rec.semester_id.id),
                ('academicyear_id', '=', rec.academic_year_id.id)]) 
            if StuAccSemIDREC:
                data = self.env['op.student'].calc_student_gpa2(rec.student_ids.student_id,self.subject_id,True)
                semesterHr = self.env['op.student.accumlative.semesters'].sudo().search([('student_accum_id', 'in', stuAccID.ids), ('semester_id', '=', rec.semester_id.id),
                    ('academicyear_id', '=', rec.academic_year_id.id),('student_id', '=', rec.student_ids.mapped('student_id').ids)])
                semesterHr.write({'semester_hr':semesterHr.semester_hr-self.subject_id.subject_credithours })
                StuAccSemIDREC.unlink()       
            super(SubjectReg, rec).unlink()   
    
    @api.constrains('semester_id','subject_id' ,'academic_year_id','course_id')
    def _check_date(self):
        for rec in self:
            domain = [
                ('semester_id', '=', rec.semester_id.id),
                ('academic_year_id', '=', rec.academic_year_id.id),
                ('subject_id', '=', rec.subject_id.id),
                ('course_id', '=', rec.course_id.id),
                ('id', '!=', self.id),
            ]
            sbj_training = self.search(domain)
            if sbj_training :   
                raise ValidationError(( 'the training subject has recored before in the same semester and academicyear !'))


class StudentSubjects(models.Model):
    _name = 'training.students'
    _description = 'training.students'
    
    std_subject_id = fields.Many2one('training.field.registration', string='Control', ondelete='cascade', required=True, index=True)
    seq = fields.Integer('#', readonly=True)
    course_id = fields.Many2one(related='std_subject_id.course_id', store='true')
    sub_id = fields.Many2one(related='std_subject_id.subject_id', store='true')
    student_id = fields.Many2one('op.student', 'Student')
    student_code = fields.Integer(related='student_id.student_code',readonly=True, store=True)
    
    
    @api.onchange('student_id')
    def onchange_student_id(self):
        for rec in self:
            status_ids = self.env['hue.std.data.status'].sudo().search([('active_invoice', '=', True)])._ids
            course_students = self.env['op.student'].sudo().search([('student_status', 'in', status_ids),('course_id', '=', rec.std_subject_id.course_id.id),('new_crh', '>=', rec.std_subject_id.subject_id.required_hours)])
            domain = {'student_id': [('id', 'in', course_students.ids)]}
            return {'domain': domain}
    
        
    @api.constrains('student_id','subject')
    def _check_date(self):
        for rec in self:
            domain = [
                ('student_id', '=', rec.student_id.id),
                ('id', '!=', self.id),
                ('sub_id', '=', rec.std_subject_id.subject_id.id)
                
            ]
            std_training = self.search(domain)
            stdID = self.env['op.student.semesters.subjects'].sudo().search([('subject_id', '=', rec.std_subject_id.subject_id.id),
                    ('student_id', '=',rec.student_id.id)])
            if stdID or std_training :   
                raise ValidationError(( "Student" + "  '  " + rec.student_id.name +"  '  "+'You can not have 2 training subject !'))