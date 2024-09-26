from odoo import models, fields, api
from odoo.exceptions import ValidationError
from xlrd import open_workbook
import base64
import datetime


class StudentOnlineExam(models.Model):
    _name = 'stu.online.exam.student'
    _description = 'Student Online Exam'
    
    
    online_exam_id = fields.Many2one('stu.online.exam', 'Exam')
    course_id = fields.Many2one('op.course', related='online_exam_id.course_id', store = True)
    subject_id = fields.Many2one('op.subject', related='online_exam_id.subject_id', store = True)
    subject_code = fields.Char('Code', related='online_exam_id.subject_id.code', store = True)
    acadyear = fields.Many2one('op.academic.year', related='online_exam_id.acadyear', store = True)
    semester = fields.Many2one('op.semesters', related='online_exam_id.semester', store = True)
    student_id = fields.Many2one('op.student')
    exam_type = fields.Selection([('Trial', 'Trial'), ('Final', 'Final'), ('Retake', 'Retake')], string='Exam Type')
    exam_date = fields.Date('Exam Date', required=True)
    mark = fields.Float('Exam Mark')
    final = fields.Float('Max Mark')
    absent = fields.Boolean('Absent')
    fail = fields.Boolean('Fail',store= True,compute="_compute_fail")
    tree_clo_acl_ids = fields.Char()#compute="_compute_tree_clo_acl_ids", search='tree_clo_acl_ids_search'


    @api.depends('course_id')
    def _compute_tree_clo_acl_ids(self):
        print('View My Tree CLO ACL')


    def tree_clo_acl_ids_search(self, operator, operand):
        # if self.env.ref('hr_extention.group_service_manager') in self.env.user.groups_id:
        #     courses = self.env['op.course'].search([]).ids
        # else:
        emp = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)])
        if not emp:
            emp = self.env.user.employee_id
        courses = emp.course_ids.ids
        # print(emp)

        records = self.sudo().search([('course_id', 'in', courses)]).ids
        return [('id', 'in', records)]


    @api.depends('mark','final')
    def _compute_fail(self):
        exam_max_mark = self.final
        passpercentage = ''
        course_subject = self.env['op.subject'].sudo().search([('course_id', '=', self.course_id.id), ('id', '=', self.subject_id.id)], limit=1 )
        if course_subject:
            passpercentage = course_subject.subject_passpercentage
        print('_______________________________________')
        print(passpercentage)

        for course_grade in self.course_id.sudo().course_grade_ids:
            pto = course_grade.percent_to
            if course_grade.grade_id.name.split('|')[1] == "F":
                if passpercentage:
                    pto = int(passpercentage)
                if self.mark >= course_grade.percent_from * exam_max_mark / 100 and self.mark < pto * exam_max_mark / 100:
                    self.fail = True
                    

class StudentOnlineExam(models.Model):
    _name = 'stu.online.exam'
    _description = 'Online Exam'


    course_id = fields.Many2one('op.course', required=True)
    subject_id = fields.Many2one('op.subject', required=True)
    acadyear = fields.Many2one('op.academic.year', required=True)# ,default=117
    semester = fields.Many2one('op.semesters', required=True, default=2)
    exam_type = fields.Selection([('Trial', 'Trial'), ('Final', 'Final'), ('Retake', 'Retake')], string='Exam Type', required=True)
    exam_date = fields.Date('Exam Date', required=True, default=datetime.datetime.today())
    exam_sheet = fields.Binary(string="Attachment")
    student_ids = fields.One2many('stu.online.exam.student', 'online_exam_id', 'Students')
    fails = fields.Integer('Fails',compute="_compute_fails")
    absence = fields.Integer('Absents', compute="_compute_absence")


    @api.depends('student_ids')
    def _compute_fails(self):
        passpercentage = ''
        course_subject = self.env['op.subject'].sudo().search([('course_id', '=', self.course_id.id), ('id', '=', self.subject_id.id)], limit=1 )
        if course_subject:
            passpercentage = course_subject.subject_passpercentage
        if self.student_ids:
            exam_max_mark = self.student_ids[0].final
        else:
            exam_max_mark = 100
        if self.course_id.sudo().course_grade_ids:
            for course_grade in self.course_id.sudo().course_grade_ids:
                if course_grade.percent_to == 100.00:
                    pto = 200
                else:
                    pto = course_grade.percent_to
    
                if course_grade.grade_id.name.split('|')[1] == "F":
                    if passpercentage:
                        pto = int(passpercentage)
                    exam_student_row_count = self.env['stu.online.exam.student'].sudo().search_count([('online_exam_id', '=', self.id), ('absent', '=', False), ('mark', '>=', course_grade.percent_from * exam_max_mark / 100), ('mark', '<', pto * exam_max_mark / 100)])
                    self.fails = exam_student_row_count
        else:
            self.fails = False


    @api.depends('student_ids')
    def _compute_absence(self):
        print('___Absents')
        exam_student_row_count = self.env['stu.online.exam.student'].sudo().search_count([('online_exam_id', '=', self.id), ('absent', '=', True)])
        self.absence = exam_student_row_count


    @api.onchange('course_id')
    def onchange_course_id(self):
        # if self.env.ref('hr_extention.group_service_manager') in self.env.user.groups_id:
        #     courses = self.env['op.course'].search([]).ids
        # else:
        emp = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)])
        if not emp:
            emp = self.env.user.employee_id
        # courses = emp.course_ids.ids
        courses = self.env['op.course'].search([]).ids #added for trial
            # print(emp)

        course_subjects = self.env['op.subject'].sudo().search([('course_id', '=', self.course_id.id)])
        subjects =[]
        for course_subject in course_subjects:
            subjects.append(course_subject.id)

        domain = {'subject_id': [('id', 'in', subjects)], 'course_id': [('id', 'in', courses)]}
        return {'domain': domain}


    def readXls(self, att):
        if att:
            try:
                xml = base64.b64decode(att)
                # xml_filename = att.datas_fname
                wb = open_workbook(file_contents=xml)
                print('________')
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
        data = self.readXls(self.exam_sheet)
        if data:
            max_final = data[1][4]
            if self.exam_type == 'Final':
                students = self._get_students()
                for student in students:
                    exam_student = self.env['stu.online.exam.student'].sudo().search([('online_exam_id', '=', self.id), ('student_id', '=', student), ('exam_type', '=', self.exam_type), ('exam_date', '=', self.exam_date)])
                    if not exam_student:
                        batch = self.env['op.batch'].sudo().search([('course_id', '=', self.course_id.id), ('academic_year', '=', self.acadyear.id), ('semester', '=', self.semester.id)],limit=1)
                        print('_______________________________ exam batch')
                        print(batch)
                        exam_block = self.env['op.session.registration.student'].sudo().search([('student_id', '=', student), ('subject_id', '=', self.subject_id.id), ('course_id', '=', self.course_id.id), ('batch_id', '=', batch.id)],limit=1)
                        if exam_block and exam_block.exam_block == False:
                            exam_student = self.env['stu.online.exam.student'].sudo().create({'online_exam_id': self.id, 'student_id': student, 'exam_type': self.exam_type, 'exam_date': self.exam_date, 'final': max_final, 'absent': True})

            # end online
            i = 0
            for row in data:
                i+=1
                print(row)
                email = str(row[2])
                mark = row[3]
                max_final = row[4]
                try:
                    scode = int(email.split('@')[0])

                    print(email)
                    print(mark)
                    print(max_final)
                    student = self.env['op.student'].sudo().search([('student_code', '=', int(scode))], limit=1)
                    if student:
                        exam_student_fail = False
                        if mark == '':
                            absent = True
                            exam_student_fail = self.env['stu.online.exam.student'].sudo().search([('student_id', '=', student.id), ('exam_type', '!=', 'Trial'), ('subject_id', '=', self.subject_id.id), ('fail', '=', True)], order="id DESC", limit=1)
                            print(exam_student_fail)
                        else:
                            absent = False
                        vals = {'online_exam_id': self.id, 'student_id': student.id, 'exam_type': self.exam_type, 'exam_date': self.exam_date, 'mark': mark, 'final': max_final, 'absent': absent}

                        exam_student_row = self.env['stu.online.exam.student'].sudo().search([('online_exam_id', '=', self.id), ('student_id', '=', student.id), ('exam_type', '=', self.exam_type), ('exam_date', '=', self.exam_date)])

                        if exam_student_row:
                            exam_student_row.write(vals)
                        if exam_student_fail and not exam_student_row:
                            self.env['stu.online.exam.student'].sudo().create(vals)
                        elif not exam_student_row and absent == False:
                            self.env['stu.online.exam.student'].sudo().create(vals)
                except:
                    pass


    def print_report(self):
        data = {'form': self.read(['course_id', 'subject_id', 'acadyear', 'semester', 'exam_type'])[0]}
        return self.env.ref('hue_exam.action_online_exam_result_report').report_action(self, data=data, config=False)


    def print_students_report(self):
        data = {'form': self.read(['course_id', 'subject_id', 'acadyear', 'semester', 'exam_type'])[0]}
        return self.env.ref('hue_exam.action_online_exam_students_result_report').report_action(self, data=data, config=False)


    def _get_students(self):
        batch = self.env['op.batch'].sudo().search([('course_id', '=', self.course_id.id), ('academic_year', '=', self.acadyear.id), ('semester', '=', self.semester.id)], limit=1)
        student_sessions = self.env['op.session.registration.enrollment'].sudo().search([('role', '=','student'),('registration_enrollment_id.batch_id', '=', batch.id), ('registration_enrollment_id.subject_id', '=', self.subject_id.id)])
        students_arr = []
        for student_session in student_sessions:
            students_arr.append(student_session.student_id.id)
        return students_arr


    tree_clo_acl_ids = fields.Char()#compute="_compute_tree_clo_acl_ids", search='tree_clo_acl_ids_search'


    @api.depends('course_id')
    def _compute_tree_clo_acl_ids(self):
        print('View My Tree CLO ACL')


    def tree_clo_acl_ids_search(self, operator, operand):
        # if self.env.ref('hr_extention.group_service_manager') in self.env.user.groups_id:
        #     courses = self.env['op.course'].search([]).ids
        # else:
        emp = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)])
        if not emp:
            emp = self.env.user.employee_id
        courses = emp.course_ids.ids
    
        records = self.sudo().search([('course_id', 'in', courses)]).ids
        return [('id', 'in', records)]