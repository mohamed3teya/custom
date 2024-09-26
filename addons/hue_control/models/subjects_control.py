from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import ValidationError
import math
import base64
from xlrd import open_workbook


class SubjectsControl(models.Model):
    _name = 'subjects.control'
    _description = 'subjects.control'
    _inherit = ['mail.thread']
    _rec_name = 'subject_id'


    active = fields.Boolean(default=True)
    changed = fields.Char()
    student_list = fields.One2many('subjects.control.student.list', 'connect_id', string="Students")
    control_type = fields.Selection([('all', 'All'), ('student', 'Student')])
    xls_list = fields.One2many('control.subjects.assessment.xls', 'connect_id', string="Upload Results")
    course_id = fields.Many2one('op.course', string='Course', required=True)
    batch_id = fields.Many2one('op.batch', required=True)
    subject_id = fields.Many2one('op.subject', string='Subject', required=True)
    date = fields.Date(string='Date', required=True, default=datetime.today())
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], string='State', required=True, default='draft', tracking=True)
    degree_tb = fields.Html(compute='_subject_id', store="True")
    flag_grade_final = fields.Boolean(default=False, compute='_subject_id', store="True")
    flag_grade_quiz = fields.Boolean(default=False, compute='_subject_id', store="True")
    flag_grade_activity = fields.Boolean(default=False, compute='_subject_id', store="True")
    flag_grade_attendance = fields.Boolean(default=False, compute='_subject_id', store="True")
    flag_grade_pract = fields.Boolean(default=False, compute='_subject_id', store="True")
    flag_grade_pract2 = fields.Boolean(default=False, compute='_subject_id', store="True")
    flag_grade_oral = fields.Boolean(default=False, compute='_subject_id', store="True")
    flag_grade_medterm = fields.Boolean(default=False, compute='_subject_id', store="True")
    flag_grade_coursework = fields.Boolean(default=False, compute='_subject_id', store="True")
    flag_grade_pract_oral = fields.Boolean(default=False, compute='_subject_id', store="True")
    flag_grade_clinic = fields.Boolean(default=False, compute='_subject_id', store="True")
    flag_grade_mcq = fields.Boolean(default=False, compute='_subject_id', store="True")
    flag_grade_eassy = fields.Boolean(default=False, compute='_subject_id', store="True")
    flag_grade_skilllab = fields.Boolean(default=False, compute='_subject_id', store="True")
    flag_grade_pbl  = fields.Boolean(default=False, compute='_subject_id', store="True")
    flag_grade_portfolio  = fields.Boolean(default=False, compute='_subject_id', store="True")
    flag_grade_logbook	  = fields.Boolean(default=False, compute='_subject_id', store="True")
    flag_grade_sdl  = fields.Boolean(default=False, compute='_subject_id', store="True")
    flag_grade_fieldstudy  = fields.Boolean(default=False, compute='_subject_id', store="True")
    flag_grade_skillexam  = fields.Boolean(default=False, compute='_subject_id', store="True")
    flag_grade_practical = fields.Boolean(default=False, compute='_subject_id', store="True")
    grade_final = fields.Float('Final', compute='_subject_id', store="True")
    grade_quiz = fields.Float('Quiz', compute='_subject_id', store="True")
    grade_activity = fields.Float('Activity', compute='_subject_id', store="True")
    grade_attendance = fields.Float('Attendance', compute='_subject_id', store="True")
    grade_pract = fields.Float('Practical', compute='_subject_id', store="True")
    grade_pract2 = fields.Float('Practical 2', compute='_subject_id', store="True")
    grade_oral = fields.Float('Oral', compute='_subject_id', store="True")
    grade_medterm = fields.Float('Med term', compute='_subject_id', store="True")
    grade_coursework = fields.Float('Course Work', compute='_subject_id', store="True")
    grade_pract_oral = fields.Float('Pract & Oral', compute='_subject_id', store="True")
    grade_clinic = fields.Float('Clinic Work', compute='_subject_id', store="True")
    grade_mcq = fields.Float('MCQ', compute='_subject_id', store="True")
    grade_eassy = fields.Float('Essay', compute='_subject_id', store="True")
    grade_skilllab = fields.Float('SkillLab', compute='_subject_id', store="True")
    grade_pbl = fields.Float('PBL', compute='_subject_id', store="True")
    grade_portfolio = fields.Float('Portfolio', compute='_subject_id', store="True")
    grade_logbook = fields.Float('Log Book', compute='_subject_id', store="True")
    grade_sdl = fields.Float('SDL', compute='_subject_id', store="True")
    grade_fieldstudy = fields.Float('Field Study', compute='_subject_id', store="True")
    grade_skillexam = fields.Float('Skill Exam', compute='_subject_id', store="True")
    grade_practical = fields.Float('Practical', compute='_subject_id', store="True")
    tree_clo_acl_ids = fields.Char()#compute="_compute_tree_clo_acl_ids", search='tree_clo_acl_ids_search'
    all_students = fields.Boolean('All Students Registered !')
    no_of_student = fields.Integer(compute='_no_of_student', store="True")
    assessment_sum = fields.Integer(related='subject_id.subject_total', readonly=True)
    factor = fields.Float()
    exam_url = fields.Char('Exam URL' , tracking=True)
    

    def write(self, values):
        if 'student_list' in values:
            student_list = values['student_list']
            message = "<div>\n"
            for std in student_list :
                if std[0] == 1 :
                    student = self.env['subjects.control.student.list'].sudo().search([('id', '=', std[1])])
                    message += "<strong>Student : " + student.student_id.name + "</strong>  <br/>   "
                    message += "<strong> Control Assessment : </strong>  <br/>   "
                    message += "<ul class=\"o_mail_thread_message_tracking\"> \n"
                    for key, value in std[2].items():
                        student_ass = student.read([str(key)])
                        message += "<li> <span>  " + str(key) + " : </span><span>" + str(student_ass[0][str(key)]) + "</span> <span> --> </span><span>" + str(value) + "</span></li> \n"
                    message += "</ul>"
            message += "</div>"
            self.message_post(body=message, subject="Mark Changed")
        print("values")
        res = super(SubjectsControl, self).write(values)
        return res


    @api.depends('student_list')
    def _no_of_student(self):
        self.no_of_student = len(self.student_list)


    @api.depends('subject_id')
    def _compute_tree_clo_acl_ids(self):
        print('View My Tree CLO ACL')

 
    def tree_clo_acl_ids_search(self, operator, operand):
        # if self.env.ref('hr_extention.group_service_manager') in self.env.user.groups_id:
        #     return [('id', 'in', self.sudo().search([]).ids)]
        emp = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)])
        subjects = self.env['subjects.control.security'].sudo().search(
            [('user', '=', emp.id), ('batch_id.control_allowed', '=', True)])
        courses = emp.course_ids.ids
        subjects = subjects.mapped('subject_id').ids
        records = self.sudo().search([('course_id', 'in', courses),('subject_id', 'in', subjects)]).ids
        return [('id', 'in', records)]


    @api.depends('subject_id')
    def _subject_id(self):
        for rec in self:
            assessments = rec.subject_id.subject_assessmentsdegree
            tb = "<table class='table table-bordered'>"
            for assessment in assessments:
                if assessment.assessment_id.control_field == 'grade_final':
                    rec.flag_grade_final = True
                    rec.grade_final = assessment.degree
                    tb += "<tr><td>Final</td>"
                    tb += "<td>" + str(assessment.degree) + "</td></tr>"
                elif assessment.assessment_id.control_field == 'grade_quiz':
                    rec.flag_grade_quiz = True
                    rec.grade_quiz = assessment.degree
                    tb += "<tr><td>Quiz</td>"
                    tb += "<td>" + str(assessment.degree) + "</td></tr>"
                elif assessment.assessment_id.control_field == 'grade_activity':
                    rec.flag_grade_activity = True
                    rec.grade_activity = assessment.degree
                    tb += "<tr><td>Activity</td>"
                    tb += "<td>" + str(assessment.degree) + "</td></tr>"
                elif assessment.assessment_id.control_field == 'grade_attendance':
                    rec.flag_grade_attendance = True
                    rec.grade_attendance = assessment.degree
                    tb += "<tr><td>Attendance</td>"
                    tb += "<td>" + str(assessment.degree) + "</td></tr>"
                elif assessment.assessment_id.control_field == 'grade_pract':
                    rec.flag_grade_pract = True
                    rec.grade_pract = assessment.degree
                    tb += "<tr><td>Practical</td>"
                    tb += "<td>" + str(assessment.degree) + "</td></tr>"
                elif assessment.assessment_id.control_field == 'grade_pract2':
                    rec.flag_grade_pract2 = True
                    rec.grade_pract2 = assessment.degree
                    tb += "<tr><td>Practical 2</td>"
                    tb += "<td>" + str(assessment.degree) + "</td></tr>"
                elif assessment.assessment_id.control_field == 'grade_oral':
                    rec.flag_grade_oral = True
                    rec.grade_oral = assessment.degree
                    tb += "<tr><td>Oral</td>"
                    tb += "<td>" + str(assessment.degree) + "</td></tr>"
                elif assessment.assessment_id.control_field == 'grade_medterm':
                    rec.flag_grade_medterm = True
                    rec.grade_medterm = assessment.degree
                    tb += "<tr><td>Med Term</td>"
                    tb += "<td>" + str(assessment.degree) + "</td></tr>"
                elif assessment.assessment_id.control_field == 'grade_coursework':
                    rec.flag_grade_coursework = True
                    rec.grade_coursework = assessment.degree
                    tb += "<tr><td>Course Work</td>"
                    tb += "<td>" + str(assessment.degree) + "</td></tr>"
                elif assessment.assessment_id.control_field == 'grade_pract_oral':
                    rec.flag_grade_pract_oral = True
                    rec.grade_pract_oral = assessment.degree
                    tb += "<tr><td>Pract & Oral</td>"
                    tb += "<td>" + str(assessment.degree) + "</td></tr>"
                elif assessment.assessment_id.control_field == 'grade_clinic':
                    rec.flag_grade_clinic = True
                    rec.grade_clinic = assessment.degree
                    tb += "<tr><td>Clinic Work</td>"
                    tb += "<td>" + str(assessment.degree) + "</td></tr>"
                elif assessment.assessment_id.control_field == 'grade_mcq':
                    rec.flag_grade_mcq = True
                    rec.grade_mcq = assessment.degree
                    tb += "<tr><td>MCQ</td>"
                    tb += "<td>" + str(assessment.degree) + "</td></tr>"
                elif assessment.assessment_id.control_field == 'grade_eassy':
                    rec.flag_grade_eassy = True
                    rec.grade_eassy = assessment.degree
                    tb += "<tr><td>Essay</td>"
                    tb += "<td>" + str(assessment.degree) + "</td></tr>"
                elif assessment.assessment_id.control_field == 'grade_skilllab':
                    rec.flag_grade_skilllab = True
                    rec.grade_skilllab = assessment.degree
                    tb += "<tr><td>Skill Lab</td>"
                    tb += "<td>" + str(assessment.degree) + "</td></tr>"
                elif assessment.assessment_id.control_field == 'grade_pbl':
                    rec.flag_grade_pbl = True
                    rec.grade_pbl = assessment.degree
                    tb += "<tr><td>PBL</td>"
                    tb += "<td>" + str(assessment.degree) + "</td></tr>"
                elif assessment.assessment_id.control_field == 'grade_pbl':
                    rec.flag_grade_pbl = True
                    rec.grade_pbl = assessment.degree
                    tb += "<tr><td>PBL</td>"
                    tb += "<td>" + str(assessment.degree) + "</td></tr>"
                elif assessment.assessment_id.control_field == 'grade_pbl':
                    rec.flag_grade_pbl = True
                    rec.grade_pbl = assessment.degree
                    tb += "<tr><td>PBL</td>"
                    tb += "<td>" + str(assessment.degree) + "</td></tr>"
                elif assessment.assessment_id.control_field == 'grade_portfolio':
                    rec.flag_grade_portfolio = True
                    rec.grade_portfolio = assessment.degree
                    tb += "<tr><td>Portfolio</td>"
                    tb += "<td>" + str(assessment.degree) + "</td></tr>"
                elif assessment.assessment_id.control_field == 'grade_logbook':
                    rec.flag_grade_logbook = True
                    rec.grade_logbook = assessment.degree
                    tb += "<tr><td>Log Book</td>"
                    tb += "<td>" + str(assessment.degree) + "</td></tr>"
                elif assessment.assessment_id.control_field == 'grade_sdl':
                    rec.flag_grade_sdl = True
                    rec.grade_sdl = assessment.degree
                    tb += "<tr><td>SDL</td>"
                    tb += "<td>" + str(assessment.degree) + "</td></tr>"
                elif assessment.assessment_id.control_field == 'grade_fieldstudy':
                    rec.flag_grade_fieldstudy = True
                    rec.grade_fieldstudy = assessment.degree
                    tb += "<tr><td>Field Study</td>"
                    tb += "<td>" + str(assessment.degree) + "</td></tr>"
                elif assessment.assessment_id.control_field == 'grade_skillexam':
                    rec.flag_grade_skillexam = True
                    rec.grade_skillexam = assessment.degree
                    tb += "<tr><td>Skill Exam</td>"
                    tb += "<td>" + str(assessment.degree) + "</td></tr>"
                elif assessment.assessment_id.control_field == 'grade_practical':
                    rec.flag_grade_practical = True
                    rec.grade_practical = assessment.degree
                    tb += "<tr><td>Practical</td>"
                    tb += "<td>" + str(assessment.degree) + "</td></tr>"
            tb += "</table>"
            rec.degree_tb = tb
            if assessments:
                rec.changed = "yes"


    @api.onchange('course_id')
    def onchange_course_id(self):
        for rec in self:
            rec.batch_id = False
            rec.subject_id = False
            emp = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)]).id
            courses_data = self.env['subjects.control.security'].sudo().search([('user', '=', emp)])
            courses = courses_data.mapped('course_id').ids
            batches = self.env['op.batch'].sudo().search(
                [('control_allowed', '=', True), ('course_id', '=', rec.course_id.id)]).ids
            domain = {'course_id': [('id', 'in', courses)], 'batch_id': [('id', 'in', batches)]}
            return {'domain': domain}


    @api.onchange('batch_id')
    def onchange_batch_id(self):
        for rec in self:
            emp = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)]).id
            subjects = self.env['subjects.control.security'].sudo().search(
                [('user', '=', emp), ('batch_id', '=', rec.batch_id.id)])
            subjects = subjects.mapped('subject_id').ids
            domain = {'subject_id': [('id', 'in', subjects)]}
            return {'domain': domain}


    def readXls(self, att):
        if att:
            try:
                xml = base64.b64decode(att)
                # xml_filename = att.datas_fname
                wb = open_workbook(file_contents=xml)
                all_data = []
                for s in wb.sheets():
                    for row in range(s.nrows):
                        data_row = []
                        for col in range(s.ncols):
                            value = (s.cell(row, col).value)
                            data_row.append(value)
                        all_data.append(data_row)
                return all_data
            except:
                 raise ValidationError("Please ensure that the file is excel file!")
        else:
            return []


    def importXls(self):
        for att in self.xls_list:
            if att.xls_type !='form' and att.status == 'active' :
                data = self.readXls(att.xls)
                i = 0
                for row in data:
                    if i >= 1:
                        scode = str(row[2])
                        student_code = int(scode.split('@')[0])
                        mark = str(row[3]).strip()
                        student = self.env['subjects.control.student.list'].sudo().search(
                            [('student_code', '=', student_code), ('connect_id', '=', att.connect_id.id)], limit=1)
                        if student:
                            student.write({att.assessment_id.control_field: mark})
                    i += 1


    def import_form_Xls(self):
        for att in self.xls_list:
            if att.xls_type =='form' and att.status == 'active' :
                data = self.readXls(att.xls)
                i = 0
                for row in data:
                    if i >= 1:
                        scode = str(row[3])
                        student_code = int(scode.split('@')[0])
                        mark = str(row[5]).strip()
                        student = self.env['subjects.control.student.list'].sudo().search(
                            [('student_code', '=', student_code), ('connect_id', '=', att.connect_id.id)], limit=1)
                        if student:
                            student.write({att.assessment_id.control_field: mark})
                    i += 1


    def fill_mark(self, assessment, degree):
        lists = self.env['subjects.control.student.list'].sudo().search([('connect_id', '=', self.id)])
        for rec in lists:
            if degree.is_integer():
                rec.write({assessment: int(degree)})
            else:
                rec.write({assessment: degree})


    def button_fill_grade_final(self):
        for rec in self.student_list:
            if rec.grade_final == False:
                if self.grade_final.is_integer():
                    rec.grade_final = int(self.grade_final)
                else:
                    rec.grade_final = (self.grade_final)


    def button_fill_grade_quiz(self):
        lists = self.env['subjects.control.student.list'].sudo().search([('connect_id', '=', self.id)])
        for rec in lists:
            if rec.grade_quiz == False:
                if self.grade_quiz.is_integer():
                    rec.write({'grade_quiz': int(self.grade_quiz)})
                else:
                    rec.write({'grade_quiz': self.grade_quiz})


    def button_fill_grade_activity(self):
        lists = self.env['subjects.control.student.list'].sudo().search([('connect_id', '=', self.id)])
        for rec in lists:
            if rec.grade_activity == False:
                if self.grade_activity.is_integer():
                    rec.write({'grade_activity': int(self.grade_activity)})
                else:
                    rec.write({'grade_activity': self.grade_activity})


    def button_get_student_grade_activity(self):
        lists = self.env['subjects.control.student.list'].sudo().search([('connect_id', '=', self.id)])
        for rec in lists:
            grade_activity = self.env['op.student.semesters.subjects'].sudo().search([('subject_id', '=', self.subject_id.id), ('course_id', '=', self.course_id.id),
                ('academicyear_id', '=', self.batch_id.academic_year.id),('semester_id', '!=', self.batch_id.semester.id),('student_id', '=', rec.student_id.id)])
            if grade_activity  :
                if grade_activity.grade_activity == -1:
                    rec.write({'grade_activity': 'غ'})
                else:
                    rec.write({'grade_activity': grade_activity.grade_activity})

                
    def button_get_student_grade_skilllab(self):
        lists = self.env['subjects.control.student.list'].sudo().search([('connect_id', '=', self.id)])
        for rec in lists:
            grade_skilllab = self.env['op.student.semesters.subjects'].sudo().search([('subject_id', '=', self.subject_id.id), ('course_id', '=', self.course_id.id),
                ('academicyear_id', '=', self.batch_id.academic_year.id),('semester_id', '!=', self.batch_id.semester.id),('student_id', '=', rec.student_id.id)])
            if grade_skilllab  :
                if grade_skilllab.grade_skilllab == -1:
                    rec.write({'grade_skilllab': 'غ'})
                else:
                    rec.write({'grade_skilllab': grade_skilllab.grade_skilllab})


    def button_get_student_grade_pbl(self):
        lists = self.env['subjects.control.student.list'].sudo().search([('connect_id', '=', self.id)])
        for rec in lists:
            grade_pbl = self.env['op.student.semesters.subjects'].sudo().search([('subject_id', '=', self.subject_id.id), ('course_id', '=', self.course_id.id),
                ('academicyear_id', '=', self.batch_id.academic_year.id),('semester_id', '!=', self.batch_id.semester.id),('student_id', '=', rec.student_id.id)])
            if grade_pbl  :
                rec.write({'grade_pbl': grade_pbl.grade_pbl})
    

    def button_get_student_grade_portfolio(self):
        lists = self.env['subjects.control.student.list'].sudo().search([('connect_id', '=', self.id)])
        for rec in lists:
            grade_portfolio = self.env['op.student.semesters.subjects'].sudo().search([('subject_id', '=', self.subject_id.id), ('course_id', '=', self.course_id.id),
                ('academicyear_id', '=', self.batch_id.academic_year.id),('semester_id', '!=', self.batch_id.semester.id),('student_id', '=', rec.student_id.id)])
            if grade_portfolio  :
                rec.write({'grade_portfolio': grade_portfolio.grade_portfolio})
    

    def button_get_student_grade_logbook(self):
        lists = self.env['subjects.control.student.list'].sudo().search([('connect_id', '=', self.id)])
        for rec in lists:
            grade_logbook = self.env['op.student.semesters.subjects'].sudo().search([('subject_id', '=', self.subject_id.id), ('course_id', '=', self.course_id.id),
                ('academicyear_id', '=', self.batch_id.academic_year.id),('semester_id', '!=', self.batch_id.semester.id),('student_id', '=', rec.student_id.id)])
            if grade_logbook  :
                rec.write({'grade_logbook': grade_logbook.grade_logbook})
                

    def button_get_student_grade_sdl(self):
        lists = self.env['subjects.control.student.list'].sudo().search([('connect_id', '=', self.id)])
        for rec in lists:
            grade_sdl = self.env['op.student.semesters.subjects'].sudo().search([('subject_id', '=', self.subject_id.id), ('course_id', '=', self.course_id.id),
                ('academicyear_id', '=', self.batch_id.academic_year.id),('semester_id', '!=', self.batch_id.semester.id),('student_id', '=', rec.student_id.id)])
            if grade_sdl  :
                rec.write({'grade_sdl': grade_sdl.grade_sdl})
    

    def button_get_student_grade_fieldstudy(self):
        lists = self.env['subjects.control.student.list'].sudo().search([('connect_id', '=', self.id)])
        for rec in lists:
            grade_fieldstudy = self.env['op.student.semesters.subjects'].sudo().search([('subject_id', '=', self.subject_id.id), ('course_id', '=', self.course_id.id),
                ('academicyear_id', '=', self.batch_id.academic_year.id),('semester_id', '!=', self.batch_id.semester.id),('student_id', '=', rec.student_id.id)])
            if grade_fieldstudy  :
                rec.write({'grade_fieldstudy': grade_fieldstudy.grade_fieldstudy})
    

    def button_get_student_grade_skillexam(self):
        lists = self.env['subjects.control.student.list'].sudo().search([('connect_id', '=', self.id)])
        for rec in lists:
            grade_skillexam = self.env['op.student.semesters.subjects'].sudo().search([('subject_id', '=', self.subject_id.id), ('course_id', '=', self.course_id.id),
                ('academicyear_id', '=', self.batch_id.academic_year.id),('semester_id', '!=', self.batch_id.semester.id),('student_id', '=', rec.student_id.id)])
            if grade_skillexam  :
                rec.write({'grade_skillexam': grade_skillexam.grade_skillexam})
                

    def button_fill_grade_attendance(self):
        lists = self.env['subjects.control.student.list'].sudo().search([('connect_id', '=', self.id)])
        for rec in lists:
            if rec.grade_attendance == False:
                if self.grade_attendance.is_integer():
                    rec.write({'grade_attendance': int(self.grade_attendance)})
                else:
                    rec.write({'grade_attendance': self.grade_attendance})


    def button_fill_grade_pract(self):
        lists = self.env['subjects.control.student.list'].sudo().search([('connect_id', '=', self.id)])
        for rec in lists:
            if rec.grade_pract == False:
                if self.grade_pract.is_integer():
                    rec.write({'grade_pract': int(self.grade_pract)})
                else:
                    rec.write({'grade_pract': self.grade_pract})


    def button_fill_grade_pract2(self):
        lists = self.env['subjects.control.student.list'].sudo().search([('connect_id', '=', self.id)])
        for rec in lists:
            if rec.grade_pract2 == False:
                if self.grade_pract2.is_integer():
                    rec.write({'grade_pract2': int(self.grade_pract2)})
                else:
                    rec.write({'grade_pract2': self.grade_pract2})


    def button_fill_grade_oral(self):
        lists = self.env['subjects.control.student.list'].sudo().search([('connect_id', '=', self.id)])
        for rec in lists:
            if rec.grade_oral == False:
                if self.grade_oral.is_integer():
                    rec.write({'grade_oral': int(self.grade_oral)})
                else:
                    rec.write({'grade_oral': self.grade_oral})


    def button_fill_grade_medterm(self):
        lists = self.env['subjects.control.student.list'].sudo().search([('connect_id', '=', self.id)])
        for rec in lists:
            if rec.grade_medterm == False:
                if self.grade_medterm.is_integer():
                    rec.write({'grade_medterm': int(self.grade_medterm)})
                else:
                    rec.write({'grade_medterm': self.grade_medterm})


    def button_fill_grade_coursework(self):
        lists = self.env['subjects.control.student.list'].sudo().search([('connect_id', '=', self.id)])
        for rec in lists:
            if rec.grade_coursework == False:
                if self.grade_coursework.is_integer():
                    rec.write({'grade_coursework': int(self.grade_coursework)})
                else:
                    rec.write({'grade_coursework': self.grade_coursework})


    def button_fill_grade_pract_oral(self):
        lists = self.env['subjects.control.student.list'].sudo().search([('connect_id', '=', self.id)])
        for rec in lists:
            if rec.grade_pract_oral == False:
                if self.grade_pract_oral.is_integer():
                    rec.write({'grade_pract_oral': int(self.grade_pract_oral)})
                else:
                    rec.write({'grade_pract_oral': self.grade_pract_oral})


    def button_fill_grade_clinic(self):
        lists = self.env['subjects.control.student.list'].sudo().search([('connect_id', '=', self.id)])
        for rec in lists:
            if rec.grade_clinic == False:
                if self.grade_clinic.is_integer():
                    rec.write({'grade_clinic': int(self.grade_clinic)})
                else:
                    rec.write({'grade_clinic': self.grade_clinic})


    def button_fill_grade_mcq(self):
        lists = self.env['subjects.control.student.list'].sudo().search([('connect_id', '=', self.id)])
        for rec in lists:
            if rec.grade_mcq == False:
                if self.grade_mcq.is_integer():
                    rec.write({'grade_mcq': int(self.grade_mcq)})
                else:
                    rec.write({'grade_mcq': self.grade_mcq})


    def button_fill_grade_eassy(self):
        lists = self.env['subjects.control.student.list'].sudo().search([('connect_id', '=', self.id)])
        for rec in lists:
            if rec.grade_eassy == False:
                if self.grade_eassy.is_integer():
                    rec.write({'grade_eassy': int(self.grade_eassy)})
                else:
                    rec.write({'grade_eassy': self.grade_eassy})
    

    def button_fill_grade_skilllab(self):
        lists = self.env['subjects.control.student.list'].sudo().search([('connect_id', '=', self.id)])
        for rec in lists:
            if rec.grade_skilllab == False:
                if self.grade_skilllab.is_integer():
                    rec.write({'grade_skilllab': int(self.grade_skilllab)})
                else:
                    rec.write({'grade_skilllab': self.grade_skilllab})
    

    def button_fill_grade_pbl(self):
        lists = self.env['subjects.control.student.list'].sudo().search([('connect_id', '=', self.id)])
        for rec in lists:
            if rec.grade_pbl == False:
                if self.grade_pbl.is_integer():
                    rec.write({'grade_pbl': int(self.grade_pbl)})
                else:
                    rec.write({'grade_pbl': self.grade_pbl})
                    

    def button_fill_grade_portfolio(self):
        lists = self.env['subjects.control.student.list'].sudo().search([('connect_id', '=', self.id)])
        for rec in lists:
            if rec.grade_portfolio == False:
                if self.grade_portfolio.is_integer():
                    rec.write({'grade_portfolio': int(self.grade_portfolio)})
                else:
                    rec.write({'grade_portfolio': self.grade_portfolio})
    

    def button_fill_grade_logbook(self):
        lists = self.env['subjects.control.student.list'].sudo().search([('connect_id', '=', self.id)])
        for rec in lists:
            if rec.grade_logbook == False:
                if self.grade_logbook.is_integer():
                    rec.write({'grade_logbook': int(self.grade_logbook)})
                else:
                    rec.write({'grade_logbook': self.grade_logbook})
                    

    def button_fill_grade_sdl(self):
        lists = self.env['subjects.control.student.list'].sudo().search([('connect_id', '=', self.id)])
        for rec in lists:
            if rec.grade_sdl == False:
                if self.grade_sdl.is_integer():
                    rec.write({'grade_sdl': int(self.grade_sdl)})
                else:
                    rec.write({'grade_sdl': self.grade_sdl})
                    

    def button_fill_grade_fieldstudy(self):
        lists = self.env['subjects.control.student.list'].sudo().search([('connect_id', '=', self.id)])
        for rec in lists:
            if rec.grade_fieldstudy == False:
                if self.grade_fieldstudy.is_integer():
                    rec.write({'grade_fieldstudy': int(self.grade_fieldstudy)})
                else:
                    rec.write({'grade_fieldstudy': self.grade_fieldstudy})
    

    def button_fill_grade_skillexam(self):
        lists = self.env['subjects.control.student.list'].sudo().search([('connect_id', '=', self.id)])
        for rec in lists:
            if rec.grade_skillexam == False:
                if self.grade_skillexam.is_integer():
                    rec.write({'grade_skillexam': int(self.grade_skillexam)})
                else:
                    rec.write({'grade_skillexam': self.grade_skillexam})


    def button_fill_grade_practical(self):
        lists = self.env['subjects.control.student.list'].sudo().search([('connect_id', '=', self.id)])
        for rec in lists:
            if rec.grade_practical == False:
                if self.grade_practical.is_integer():
                    rec.write({'grade_practical': int(self.grade_practical)})
                else:
                    rec.write({'grade_practical': self.grade_practical})


    def button_add_1_att(self):
        lists = self.env['subjects.control.student.list'].sudo().search([('connect_id', '=', self.id)])
        for rec in lists:
            if rec.grade_eassy and rec.grade_eassy != 'غ':
                grade_eassy = float(rec.grade_eassy) - 1
                rec.write({'grade_eassy': grade_eassy}) 


    def button_add_2_att(self):
        lists = self.env['subjects.control.student.list'].sudo().search([('connect_id', '=', self.id)])
        for rec in lists:
            if rec.grade_eassy and rec.grade_eassy != 'غ' :
                grade_eassy = float(rec.grade_eassy) + 1
                rec.write({'grade_eassy': grade_eassy})
    

    def med_summer_grade(self):
        lists = self.env['subjects.control.student.list'].sudo().search([('connect_id', '=', self.id)])
        for rec in lists:
            std = self.env['op.student.semesters.subjects'].sudo().search([('student_id', '=', rec.student_id.id),
                ('student_semester_id.grade.pass_grade', '=', False),('academicyear_id.sequence', '<=', self.batch_id.academic_year.sequence),
                ('subject_id', '=', self.subject_id.id),('final_grade.pass_grade', '=', True)],order='id desc' ,limit=1)
            if std :
                rec.write({'grade_final': std.grade_final, 'grade_quiz': std.grade_quiz, 'grade_activity': std.grade_activity,
                 'grade_attendance': std.grade_attendance, 'grade_pract': std.grade_pract,
                 'grade_pract2': std.grade_pract2,
                 'grade_oral': std.grade_oral, 'grade_medterm': std.grade_medterm,
                 'grade_coursework': std.grade_coursework, 'grade_pract_oral': std.grade_pract_oral,
                 'grade_clinic': std.grade_clinic,
                 'grade_mcq': std.grade_mcq, 'grade_eassy': std.grade_eassy,'grade_skilllab': std.grade_skilllab,
                 'grade_pbl': std.grade_pbl, 'grade_portfolio': std.grade_portfolio, 'grade_logbook': std.grade_logbook,
                 'grade_sdl': std.grade_sdl, 'grade_fieldstudy	': std.grade_fieldstudy, 'grade_skillexam': std.grade_skillexam,
                 'grade_practical': std.grade_practical,
                 
                 })


    @api.constrains('course_id', 'batch_id', 'subject_id')
    def _check_control(self):
        control = self.env['subjects.control'].sudo().search(
            [('course_id', '=', self.course_id.id), ('subject_id', '=', self.subject_id.id), ('id', '!=', self.id),
             ('batch_id', '=', self.batch_id.id)])
        if control:
            raise ValidationError(('Subject at same Batch already added before'))


    def unlink(self):
        """return validation error on deleting the academic year"""
        for rec in self:
            if rec.state == 'done':
                raise ValidationError(_("Can't delete done grades."))
            elif rec.state == 'draft':
                lists = self.env['subjects.control.student.list'].sudo().search([('connect_id', '=', rec.id)])
                for list in lists:
                    # list.student_semester_subject_id.unlink()
                    list.student_semester_subject_id.write(
                        {'grade_final': 0, 'grade_quiz': 0, 'grade_activity': 0,
                         'grade_attendance': 0, 'grade_pract': 0,
                         'grade_pract2': 0,
                         'grade_oral': 0, 'grade_medterm': 0,
                         'grade_coursework': 0, 'grade_pract_oral': 0, 'grade_clinic': 0,
                         'grade_mcq': 0, 'grade_eassy': 0,'grade_skilllab': 0, 'grade_practical': 0,
                         'grade_pbl': 0 ,'grade_portfolio': 0 ,'grade_logbook': 0 ,'grade_sdl': 0 ,'grade_fieldstudy': 0 ,'grade_skillexam': 0 ,
                         'subject_degree': 0, 'subject_grade': False,
                         'control_grade': False, 'control_degree': 0})
        res = super(SubjectsControl, self).unlink()
        return res


    def button_done(self):
        lists = self.env['subjects.control.student.list'].sudo().search([('connect_id', '=', self.id)])
        for rec in lists:
            if not rec.total or not rec.grade:
                raise ValidationError(
                    'Empty Grade,check students Grade *** Student Name: %s' % rec.student_id.name)
            else:
                grade_final = -1 if rec.grade_final == 'غ' else float(rec.grade_final)
                grade_quiz = -1 if rec.grade_quiz == 'غ' else float(rec.grade_quiz)
                grade_activity = -1 if rec.grade_activity == 'غ' else float(rec.grade_activity)
                grade_attendance = -1 if rec.grade_attendance == 'غ' else float(rec.grade_attendance)
                grade_pract = -1 if rec.grade_pract == 'غ' else float(rec.grade_pract)
                grade_pract2 = -1 if rec.grade_pract2 == 'غ' else float(rec.grade_pract2)
                grade_medterm = -1 if rec.grade_medterm == 'غ' else float(rec.grade_medterm)
                grade_oral = -1 if rec.grade_oral == 'غ' else float(rec.grade_oral)
                grade_coursework = -1 if rec.grade_coursework == 'غ' else float(rec.grade_coursework)
                grade_clinic = -1 if rec.grade_clinic == 'غ' else float(rec.grade_clinic)
                grade_pract_oral = -1 if rec.grade_pract_oral == 'غ' else float(rec.grade_pract_oral)
                grade_mcq = -1 if rec.grade_mcq == 'غ' else float(rec.grade_mcq)
                grade_eassy = -1 if rec.grade_eassy == 'غ' else float(rec.grade_eassy)
                grade_skilllab = -1 if rec.grade_skilllab == 'غ' else float(rec.grade_skilllab)
                grade_pbl = -1 if rec.grade_pbl == 'غ' else float(rec.grade_pbl)
                grade_portfolio = -1 if rec.grade_portfolio == 'غ' else float(rec.grade_portfolio)
                grade_logbook	 = -1 if rec.grade_logbook == 'غ' else float(rec.grade_logbook)
                grade_sdl = -1 if rec.grade_sdl == 'غ' else float(rec.grade_sdl)
                grade_fieldstudy = -1 if rec.grade_fieldstudy == 'غ' else float(rec.grade_fieldstudy)
                grade_skillexam = -1 if rec.grade_skillexam == 'غ' else float(rec.grade_skillexam)
                grade_practical = -1 if rec.grade_practical == 'غ' else float(rec.grade_practical)
                total = 0 if rec.total == 'غ' else float(rec.total)
                # control_degree = -1 if rec.grade_coursework != 'غ' else float(rec.grade_coursework)
                if not rec.student_semester_subject_id :
                    StuSubjectIDs = self.env['op.student.semesters.subjects'].sudo().search(
                        [('student_id', '=', rec.student_id.id),('subject_id', '=', rec.connect_id.subject_id.id),
                         ('academicyear_id', '=', rec.connect_id.batch_id.academic_year.id),
                         ('semester_id', '=', rec.connect_id.batch_id.semester.id), ('course_id', '=', rec.connect_id.course_id.id)],
                        limit=1)
                    rec.write({'student_semester_subject_id': StuSubjectIDs.id})
                    # student_ids = StuSubjectIDs.mapped('student_id').ids
                rec.student_semester_subject_id.write(
                    {'grade_final': grade_final, 'grade_quiz': grade_quiz, 'grade_activity': grade_activity,
                     'grade_attendance': grade_attendance, 'grade_pract': grade_pract,
                     'grade_pract2': grade_pract2,
                     'grade_oral': grade_oral, 'grade_medterm': grade_medterm,
                     'grade_coursework': grade_coursework, 'grade_pract_oral': grade_pract_oral,
                     'grade_clinic': grade_clinic,
                     'grade_mcq': grade_mcq, 'grade_eassy': grade_eassy,'grade_skilllab': grade_skilllab,
                     'grade_pbl': grade_pbl, 'grade_portfolio': grade_portfolio, 'grade_logbook': grade_logbook,
                     'grade_sdl': grade_sdl, 'grade_fieldstudy	': grade_fieldstudy, 'grade_skillexam': grade_skillexam,
                     'grade_practical': grade_practical,
                     'subject_degree': (total), 'subject_grade': rec.grade.id,
                     'control_grade': rec.control_grade.id, 'control_degree': float(rec.control_degree)})

                self.write({'state': 'done'})


    def button_draft(self):
        for rec in self:
            rec.write({'state': 'draft'})


    def get_student_list(self):
        # self.check_student = True
        """returns the list of students applied to join the selected class"""
        for rec in self:
            lines = self.env['subjects.control.student.list'].sudo().search([('connect_id', '=', rec.id)])
            curr_student_ids = lines.mapped('student_id').ids
            status_ids = self.env['hue.std.data.status'].sudo().search([('active_invoice', '=', True)])._ids


            if rec.all_students:
                StuSubjectIDs = self.env['op.student.semesters.subjects'].sudo().search(
                    [('subject_id', '=', rec.subject_id.id),
                     ('academicyear_id', '=', rec.batch_id.academic_year.id),
                     ('semester_id', '=', rec.batch_id.semester.id), ('student_semester_id.semester_status', 'in', status_ids)],
                    order='student_code')
            else:
                StuSubjectIDs = self.env['op.student.semesters.subjects'].sudo().search(
                    [('subject_id', '=', rec.subject_id.id),
                     ('academicyear_id', '=', rec.batch_id.academic_year.id),
                     ('semester_id', '=', rec.batch_id.semester.id), ('course_id', '=', rec.course_id.id), ('student_semester_id.semester_status', 'in', status_ids)],
                    order='student_code')
            i = len(lines) + 1
            for stud in StuSubjectIDs:
                if stud.student_id.id not in curr_student_ids:
                    stud_line = {
                        'seq': i,
                        'student_id': stud.student_id.id,
                        'connect_id': rec.id,
                        'student_semester_subject_id': stud.id,
                        'subject_id': stud.subject_id.id,
                    }
                    rec.student_line = self.env['subjects.control.student.list'].sudo().create(stud_line)
                    i = i + 1