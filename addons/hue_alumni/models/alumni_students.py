from odoo import models, fields, api
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class AlumniStudebts(models.Model):
    _name = 'alumni.students'
    _description = 'alumni.students'
    _inherit = ['mail.thread']
    _rec_name = 'course_id'
    
    
    student_list = fields.One2many('alumni.students.list', 'alumni_id', string="Students")
    course_id = fields.Many2one('op.course', string='Course', required=True)
    academic_year_id = fields.Many2one('op.academic.year', string='Academic Year', required=True)
    semester_id = fields.Many2one('op.semesters', string='Semester', required=True)
    university_date = fields.Date(string='University Date ', required=True, default=fields.Date.today)
    decision_date = fields.Date(string='Decision Date ', required=True, default=fields.Date.today)
    decision_number = fields.Integer( string=' Decision Number', required=True)
    intern_start_date = fields.Date()
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')],string='State', required=True, default='draft', tracking=True)

    
    def button_done(self):
        current_date= datetime.today().strftime("%Y-%m-%d")
        lists = self.env['alumni.students.list'].sudo().search([('alumni_id', '=', self.id)])
        for stud in lists:
            if stud.chkstudent:
                if stud.student_id.course_id.intern_year :
                    if stud.student_id.student_status.id != 48 :
                        stud.student_id.write({'student_status': 55 })
                        intern_std = self.env['intern.student'].sudo().search([('student_id', '=', stud.student_id.id)])
                        if not intern_std :
                            intern_std = self.env['intern.student'].sudo().create({'student_id' : stud.student_id.id , 'course_id': stud.student_id.course_id.id })
                        if intern_std and stud.student_id.course_id.faculty_id.id ==8 and not intern_std.note_list :
                            sample_date = datetime.strptime(self.intern_start_date, '%Y-%m-%d')
                            for x in range(12):
                                if x <= 12 :
                                    start_date_of_this_month = sample_date.replace(day=1)
                                    month = start_date_of_this_month.month
                                    year = start_date_of_this_month.year
                                    if month == 12:
                                        month = 1
                                        year += 1
                                    else:
                                        month += 1
                                    next_month_start_date = start_date_of_this_month.replace(month=month, year=year)
                                    month_end_date = calendar.monthrange(year, month)[1]
                                    this_month_end_date = next_month_start_date.replace(day=month_end_date) 
                                    if x == 0 :
                                        sample_month_end_date = calendar.monthrange(sample_date.year, sample_date.month)[1]
                                        sample_end_date = sample_date.replace(day=sample_month_end_date) 
                                        intern_date =self.env['internships.list'].sudo().create({'intern_id' :intern_std.id,'date_from' :sample_date,
                                                                                 'date_to' :sample_end_date})
                                    else :
                                        sample_date = next_month_start_date
                                        intern_date =self.env['internships.list'].sudo().create({'intern_id' :intern_std.id,'date_from' :next_month_start_date,
                                                                                     'date_to' :this_month_end_date})   
                else :
                    stud.student_id.write({'student_status': 48 })
                std_advisor = self.env['hue.academic.direction.line'].sudo().search([('to_date', '=', False),('student_id', '=', stud.student_id.id)])
                stud.student_id.write({'advisor': False })
                std_advisor.write({'to_date':current_date})
                stud.write({'isalumni': True})
                stud.write({'acadyear': self.academic_year_id.id,'semester': self.semester_id.id})
                stud.student_id.write({'alumni_academicyear_id': self.academic_year_id.id,'alumni_semester_id': self.semester_id.id})


    def get_student_list(self): 
        status_ids = (self.env['hue.std.data.status'].sudo().search([('active_invoice', '=', True)])._ids)
        students = self.env['op.student'].sudo().search([('course_id', '=', self.course_id.id),('new_crh', '>=', self.course_id.credithours)
            ,('new_gpa', '>=', 2),('core_crh', '>=', self.course_id.corehours),('elective_crh', '>=', self.course_id.electivehours),('project_crh', '>=', self.course_id.projecthours)])
        
        i = 1
        for stud in students:
            stud_line = {
                'seq': i,
                'student_id': stud.id,
                'alumni_id': self.id,
            }
            checkstudentAlumni = self.env['alumni.students.list'].sudo().search([('student_id', '=', stud.id),('isalumni', '=', True)])
            if not checkstudentAlumni:
                self.env['alumni.students.list'].sudo().create(stud_line)
                i = i + 1
