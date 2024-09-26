from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
from datetime import datetime


_logger = logging.getLogger(__name__)


class InternStudent(models.Model):
    _name = 'intern.student'
    _description = 'intern.student'
    _inherit = ['mail.thread']
    _rec_name = 'student_id'    
    
    
    note_list = fields.One2many('internships.list', 'intern_id', string="Internships")
    course_id = fields.Many2one('op.course', string='Course', required=True, tracking=True)
    student_id = fields.Many2one('op.student', required=True, tracking=True)
    student_code = fields.Integer(related='student_id.student_code', store=True)
    alumni_academic_year = fields.Many2one(related='student_id.alumni_academicyear_id', store=True, tracking=True)
    alumni_semster = fields.Many2one(related='student_id.alumni_semester_id', store=True , tracking=True)
    total_months = fields.Integer(compute="_total_months_count" , store =True, tracking=True)
    internal_months = fields.Integer(compute="_total_months_count" , store =True, tracking=True)
    external_months = fields.Integer(compute="_total_months_count" , store =True, tracking=True)
    core_months = fields.Integer(compute="_total_months_count" , store =True, tracking=True)
    elective_months = fields.Integer(compute="_total_months_count" , store =True, tracking=True)
    state = fields.Selection([('draft', 'Draft'), ('graduate', 'Graduate')],string='State', required=True, default='draft', tracking=True)
    

    @api.depends('note_list')
    def _total_months_count(self):
        total_months_count = self.env['internships.list'].sudo().search([('intern_id', '=', self.id)])
        month_count =0
        internal_months_count =0
        external_months_count =0
        core_months_count =0
        elective_months_count =0
        for rec in total_months_count:
            if self.course_id.faculty_id.id == 6:
                if rec.training_place.training_type == 'internal' :
                     internal_months_count =internal_months_count + int(rec.month_count)
                elif rec.training_place.training_type == 'external' :
                    external_months_count =external_months_count + int(rec.month_count)
            else :
                if rec.department_id :
                    if rec.elective_department :
                        elective_months_count =elective_months_count + int(rec.month_count)
                    else :
                        core_months_count =core_months_count + int(rec.month_count)
            month_count =month_count + int(rec.month_count)
        self.total_months = month_count
        self.internal_months = internal_months_count
        self.external_months = external_months_count
        self.core_months = core_months_count
        self.elective_months = elective_months_count 
        
    
    @api.onchange('course_id')
    def onchange_course_id(self):
        for rec in self:
            courses = self.env['op.course'].sudo().search([('intern_year', '=', True)]).ids
            students = self.env['op.student'].sudo().search([('student_status', '=', 55), ('course_id', '=', rec.course_id.id)]).ids
            domain = {'course_id': [('id', 'in', courses)], 'student_id': [('id', 'in', students)]}
            return {'domain': domain}


    @api.constrains('student_id')
    def _check_date(self):
        domain = [
            ('student_id', '=', self.student_id.id), 
            ('id', '!=', self.id),
        ]
        std_intern = self.search(domain)         
        if std_intern:
            raise ValidationError(('You can not have 2  intern year of the same student !' ))
    

    def write(self, values):
        if 'note_list' in values:
            note_list = values['note_list']
            message = "<div>\n"
            intern_count =0
            for rec in note_list :
                if rec[0] == 1 :
                    place = self.env['internships.list'].sudo().search([('id', '=', rec[1])])
                    if place.training_place :
                        message += "<strong>Edit intership : " + place.training_place.name + "</strong>  <br/>   "
                    message += "<strong> Assessment : </strong>  <br/>   "
                    message += "<ul class=\"o_mail_thread_message_tracking\"> \n"
                    for key, value in rec[2].items():
                        details = place.read([str(key)])
                        message += "<li> <span>  " + str(key) + " : </span><span>" + str(details[0][str(key)]) + "</span> <span> --> </span><span>" + str(value) + "</span></li> \n"
                    message += "</ul>"
                elif rec[0] == 2 :
                    place = self.env['internships.list'].sudo().search([('id', '=', rec[1])])
                    if place.training_place :
                        message += "<strong>Delete place : " + place.training_place.name + "</strong>  <br/>   "
                message += "</div>"
                self.message_post(body=message, subject="Mark Changed")
                if rec[0] == 1  or rec[0] == 0 :
                    if 'month_count' in rec[2] :
                        intern_count =intern_count + int(rec[2]['month_count'])
                if rec[0] == 4 :
                    months = self.env['internships.list'].sudo().search([('id', '=', rec[1])])
                    intern_count =intern_count + int(months.month_count)
                stdID = self.env['op.student'].sudo().search([('id', '=', self.student_id.id)])
                stdID.write({'intern_month':intern_count })
        res = super(InternStudent, self).write(values)
        return res
    
    
    def button_graduate(self):
        current_date= datetime.today().strftime("%Y-%m-%d")
        for rec in self  :
            student = self.env['intern.student'].sudo().search([('id', '=', rec.id),('total_months', '=', 12),('student_id.student_status', '=', 55)])
            if student :
                graduated = student.student_id.write({'graduation_date': current_date,'student_status': 48})
                if graduated :
                    rec.write({'state': 'graduate'})
            else :
                raise ValidationError("Total months less than 12 month !")
    

    def button_draft(self):
        for rec in self  :
            student = self.env['intern.student'].sudo().search([('id', '=', rec.id),('total_months', '=', 12),('student_id.student_status', '=', 48)])
            if student :
                graduated = student.student_id.write({'graduation_date': False ,'student_status': 55})
                if graduated :
                    self.write({'state': 'draft'})
                    
                    
class InternshipsList(models.Model):
    _name = 'internships.list'
    _description ='internships.list'
    
    
    intern_id = fields.Many2one('intern.student', ondelete='cascade', required=True, index=True)
    date_from = fields.Date()
    date_to = fields.Date()
    month_count = fields.Selection([('1', '1'), ('2', '2'),('3', '3'), ('4', '4'),
        ('5', '5'), ('6', '6'),('7', '7'), ('8', '8'),('9', '9'), ('10', '10'),('11', '11'), ('12', '12')])
    training_place = fields.Many2one('hue.training.places')
    department_id = fields.Many2one('hue.intern.department')
    elective_department = fields.Boolean()
    
    
    @api.constrains('date_from', 'date_to')
    def _check_date_time(self):
        start_time = fields.Datetime.from_string(self.date_from)
        end_time = fields.Datetime.from_string(self.date_to)
        if start_time > end_time:
            raise ValidationError(('End Time cannot be set before Start Time.'))