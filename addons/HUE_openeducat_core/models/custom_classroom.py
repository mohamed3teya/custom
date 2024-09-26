from odoo import fields, models, api
from odoo.exceptions import ValidationError

class CustomClassRoom(models.Model):
    _name= 'op.classroom'
    _inherit = ['mail.thread','op.classroom']
    
    academic_year_id = fields.Many2one('op.academic.year', string='Academic Year', tracking=True, required=True)
    join_term = fields.Many2one('op.semesters', string='Join Term', tracking=True)
    join_year = fields.Many2one('hue.joining.years', string='Join Year', tracking=True)
    lecture = fields.Boolean()
    no_capacity = fields.Integer(string='No Capacity')
    semester_id = fields.Many2one('op.semesters', string='Semester', tracking=True, required=True)
    sequence =fields.Integer()
    status_ids = fields.Many2many('hue.std.data.status', string='Status', tracking=True)
    student_study_ids = fields.One2many('student.study.groups', 'study_group_id', string='Student Study')
    subjects = fields.Many2many('op.subject', string='Subjects',domain="[('course_id', '=', course_id)]")
    t_level = fields.Many2one('op.course.levels', string='T.level', tracking=True, domain="[('course_id', '=', course_id)]")
    student_level = fields.Many2one('op.course.levels' ,tracking=True ,domain="[('course_id', '=', course_id)]")
    capacity = fields.Integer(compute='_capacity_count')
    
    @api.depends('student_study_ids')
    def _capacity_count(self):
        for rec in self:
            count = 0
            for std in rec.student_study_ids :
                count += 1
            rec.capacity = count
            
    def write(self, values):
        if 'student_study_ids' in values:
            student_study_ids = values['student_study_ids']
            message = "<div>\n"
            for std in student_study_ids :
                if std[0] == 0 :
                    student = self.env['op.student'].sudo().search([('id', '=', std[2]['student_id'])])
                    if student :
                        message += "<strong>create Student : " + student.name + "</strong>  <br/>   "
                        message += "<ul class=\"o_mail_thread_message_tracking\"> \n"
                        message += "</ul>"
                elif std[0] == 2 :
                    student = self.env['student.study.groups'].sudo().search([('id', '=', std[1])])
                    if student.student_id :
                        message += "<strong>delete Student : " + student.student_id.name + "</strong>  <br/>   "
                elif std[0] == 1 :
                    student = self.env['student.study.groups'].sudo().search([('id', '=', std[1])])
                    if student :
                        message += "<strong>edit Student : " + student.student_id.name + "</strong>  <br/>   "
         
            message += "</div>"
            self.message_post(body=message, subject="Mark Changed")
        print("values")

        res = super(CustomClassRoom, self).write(values)
        return res
    
    def get_student_list(self):
        # self.check_student = True
        """returns the list of students applied to join the selected class"""
        for rec in self:
            lines = self.env['student.study.groups'].sudo().search([('study_group_id', '=', rec.id)])
            curr_student_ids = lines.mapped('student_id').ids
            
            another_classes = self.env['op.classroom'].sudo().search([('lecture', '=', rec.lecture),('batch_id', '=', rec.batch_id.id),('join_year', '=', rec.join_year.id),('join_term', '=', rec.join_term.id),('course_id', '=', rec.course_id.id),('id', '!=', rec.id)]).ids
            another_lines = self.env['student.study.groups'].sudo().search([('study_group_id', 'in', another_classes)])
            another_classes_std = another_lines.mapped('student_id').ids
            domain=[]
            domain.append(('id', 'not in', another_classes_std))
            if rec.join_year :
                domain.append(('join_year', '=', rec.join_year.id))
            if rec.join_term :
                domain.append(('join_term', '=', rec.join_term.id))
            if rec.student_level :
                domain.append(('level', '=', rec.student_level.level_id.level_id.id))
            domain.append(('student_status', 'in', rec.status_ids.ids))
            domain.append(('course_id', '=', rec.course_id.id))

            stds = self.env['op.student'].sudo().search(domain,order='student_code',limit=rec.no_capacity)
            students = list(stds)
            if rec.t_level :
                transfer_student = self.env['transferred.student'].sudo().search([('t_level', '=', rec.t_level.id),
                    ('student_id.student_status', 'in', rec.status_ids.ids),('student_id', 'not in', another_classes_std),
                    ('course_id', '=', rec.course_id.id),('state', '=', 'done')])
                for std_id in transfer_student:
                    students.append(std_id.student_id)
            # if rec.student_level :
            #     std_by_level = self.env['op.student'].sudo().search([('id', 'not in', another_classes_std),
            #         ('level', '=', rec.student_level.level_id.level_id.id)  ,                  
            #         ('student_status', 'in', rec.status_ids.ids),('course_id', '=', rec.course_id.id)])
            #     for std_id in std_by_level:
            #         students.append(std_id)
                   
            for stud in students:
                invoice_count = 0
                if stud.id not in curr_student_ids:
                    if not stud.allow_registration:
                        domain = [
                            ('type', 'in', ['out_invoice']),
                            ('date_due', '<=', date.today()),
                            ('partner_id', '=', [stud.partner_id.id]),
                            ('state', 'in', ['draft','open'])
                        ]
                        invoice_count = self.env['account.move'].sudo().search_count(domain)
                    if invoice_count == 0 :
                        stud_line = {
                            'student_id': stud.id,
                            'study_group_id': rec.id,
                            'course_id': rec.course_id.id,
                        }
                        self.env['student.study.groups'].sudo().create(stud_line)
            all_stds = self.env['op.student'].sudo().search([('id', 'in', curr_student_ids)])
            for std in all_stds:
                invoice_count = 0
                if not std.allow_registration:
                    domain = [
                        ('type', 'in', ['out_invoice']),
                        ('date_due', '<=', date.today()),
                        ('partner_id', '=', [std.partner_id.id]),
                        ('state', 'in', ['draft','open'])
                    ]
                    invoice_count = self.env['account.move'].sudo().search_count(domain)
                if invoice_count != 0  :
                    line = self.env['student.study.groups'].sudo().search([('study_group_id', '=', rec.id),
                        ('student_id', '=', std.id)])
                    line.unlink()
                    
    def sync_session(self):
        for rec in self:
            batch_sub = self.env['hue.subject.registration'].search([('batch_id', '=', rec.batch_id.id)])
            all_sub = batch_sub.mapped('subject_id').ids
            session = self.env['op.session'].search([('course_id', '=', rec.course_id.id),
            ('batch_id', '=', rec.batch_id.id), ('subject_id', 'in',all_sub ),
            ('classroom_id', '=', rec.id)])
            for sec in session :
                for stud in rec.student_study_ids :
                    if stud.student_id.id not in  sec.student_ids.ids :
                        if sec.sub_classroom == 0 and  not stud.sub_classroom :
                            sec.write({'student_ids': [(4,stud.student_id.id)] })
                        else :
                            if str(stud.sub_classroom) == str(sec.sub_classroom) :
                                sec.write({'student_ids': [(4,stud.student_id.id)] })
                                
    def get_retake_student_list(self):
        # self.check_student = True
        """returns the list of students applied to join the selected class"""
        # AcadYearID = self.env['hue.academic.years'].sudo().search([('current', '=', True)], limit=1).id
        # semester_id = self.env['op.semesters'].sudo().search([('current', '=', True)], limit=1).id
        
        for rec in self:
            lines = self.env['student.study.groups'].sudo().search([('study_group_id', '=', rec.id)])
            curr_student_ids = lines.mapped('student_id').ids
            stds = self.env['op.student.accumlative.semesters'].sudo().search([
                ('final_grade', 'in', (19,25)),('course_id', '=', self.course_id.id)
                ,('academicyear_id', '=', self.academic_year_id.id) ,('semester_id' , '=', self.semester_id.id)])
                
            print('*************************************************')
            mapped_stds = stds.mapped('student_id').ids
            mapped_stds_ = self.env['op.student'].search([('id', 'in', mapped_stds),('join_year', '=', self.join_year.id),('student_status', 'in', self.status_ids.ids)]).ids
            print(stds)
            count=0
            for stud in mapped_stds_:
                count = count+1
                if stud not in curr_student_ids:
                    stud_line = {
                        'student_id': stud,
                        'study_group_id': rec.id,
                        'course_id': rec.course_id.id,
                        'index': count
                    }
                    print('stud_line...........................')
                    print(stud_line)
                    self.env['student.study.groups'].sudo().create(stud_line)
                    
    def save_student_subjects(self):
        AcadYearID = self.env['op.academic.year'].sudo().search([('current', '=', True)], limit=1).id
        semester = self.env['op.semesters'].sudo().search([('current', '=', True)], limit=1).id
        if self.semester_id.id == semester and self.academic_year_id.id == AcadYearID :
            students_ = self.env['student.study.groups'].sudo().search([('study_group_id', '=', self.id)])
            students_ids = students_.mapped('student_id').ids
            students = self.env['op.student'].search([('id', 'in', students_ids),('student_status', '=', 2)])
            
            
            for student in students:
                stuAccID = self.env['op.student.accumulative'].sudo().search(
                    [('student_id', '=', student.id), ('course_id', '=', student.course_id.id),
                     ('academicyear_id', '=', self.academic_year_id.id)], limit=1)
                if not stuAccID:
                    stuAccID = self.env['op.student.accumulative'].sudo().create(
                        {'student_id': student.id, 'course_id': student.course_id.id, 'academicyear_id': self.academic_year_id.id})
                StuAccSemID = self.env['op.student.accumlative.semesters'].sudo().search(
                    [('student_accum_id', '=', stuAccID.id), ('semester_id', '=', self.semester_id.id)])
                if not StuAccSemID:
                    StuAccSemID = self.env['op.student.accumlative.semesters'].sudo().create(
                        {'student_accum_id': stuAccID.id, 'academicyear_id': self.academic_year_id.id, 'semester_id': self.semester_id.id, 'semester_status': 2})
                    
                stucourses = self.env['op.subjects'].search([('id', 'in', self.subjects.ids)])
                for sub in stucourses:
                    stuSemSubID = self.env['op.student.semesters.subjects'].sudo().search(
                        [('student_semester_id', '=', StuAccSemID.id), ('subject_id', '=', sub.id)])
                    if not stuSemSubID:
                        self.env['op.student.semesters.subjects'].sudo().create(
                            {'student_semester_id': StuAccSemID.id, 'subject_id': sub.id})
            
        else:
            raise ValidationError("academinyear and semester should be current")