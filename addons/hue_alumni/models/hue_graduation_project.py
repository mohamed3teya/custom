from odoo import models, fields, api
from odoo.exceptions import ValidationError


class GraduationProject(models.Model):
    _name = 'hue.graduation.project'
    _description = 'hue.graduation.project'
    _inherit = ['mail.thread']


    student_ids = fields.One2many('hue.graduation.project.students','project_id', string="Students")
    course_id = fields.Many2one('op.course', string='Course' ,tracking=True)
    name = fields.Char(tracking=True, required=True)
    en_name = fields.Char(string ="English name" ,tracking=True, required=True)
    academic_year_id = fields.Many2one('op.academic.year', string='Academic Year', required=True , tracking=True)
    semester_id = fields.Many2one('op.semesters', string='Joined Semester', required=True , tracking=True)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], string='State', required=True, default='draft', tracking=True)


    def get_draft(self):
        self.write({'state': 'draft'})
    

    def button_done(self):
        students = self.env['hue.graduation.project.students'].sudo().search([('project_id', '=', self.id)])  
        for rec in students :
            rec.student_id.write({'project_title': self.name +'|'+ self.en_name})
        self.write({'state': 'done'})


    def write(self, values):
        if 'student_ids' in values:
            student_ids = values['student_ids']
            message = "<div>\n"
            for std in student_ids :
                if std[0] == 1 :
                    student = self.env['hue.graduation.project.students'].sudo().search([('id', '=', std[1])])
                    message += "<strong>Edit student : " + student.student_id.name + "</strong>  <br/>   "
                elif std[0] == 2 :
                    student = self.env['hue.graduation.project.students'].sudo().search([('id', '=', std[1])])
                    message += "<strong>Delete student : " + student.student_id.name + "</strong>  <br/>   "
                elif std[0] == 0 :
                    student = self.env['op.student'].sudo().search([('id', '=', std[2]['student_id'])])
                    message += "<strong>Create student : " + student.name  + "</strong>  <br/>   "
            message += "</div>"
            self.message_post(body=message, subject="Mark Changed")
        res = super(GraduationProject, self).write(values)
        return res
    
    
class GraduationProjectStudent(models.Model):
    _name = 'hue.graduation.project.students'
    _description = 'hue.graduation.project.students'
    inherit = ['mail.thread']


    project_id = fields.Many2one('hue.graduation.project', string='Control', ondelete='cascade', required=True, index=True)
    student_id = fields.Many2one('op.student')
    student_code = fields.Integer(related='student_id.student_code', readonly=True, store=True)
    
    
    @api.onchange('student_id')
    def onchange_student_id(self):
        for rec in self:
            students = self.env['op.student'].sudo().search([('alumni_semester_id', '=', rec.project_id.semester_id.id),
                    ('alumni_academicyear_id', '=', rec.project_id.academic_year_id.id), ('course_id', '=', rec.project_id.course_id.id)])
            domain = {'student_id': [('id', 'in', students.ids)]}
            return {'domain': domain}
    
    
    @api.constrains('student_id')
    def _check_date(self):
        domain = [
            ('student_id', '=', self.student_id.id),
            ('id', '!=', self.id),
        ]
        std_id = self.search(domain)         
        if std_id:
            raise ValidationError('You can not have 2  record  of the same student !')
