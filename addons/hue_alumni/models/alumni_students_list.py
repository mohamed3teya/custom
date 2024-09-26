from odoo import models, fields, api


class AlumniStudentList(models.Model):
    _name = 'alumni.students.list'
    _description = 'alumni.students.list'
    
    
    chkstudent = fields.Boolean(default=True)
    alumni_id = fields.Many2one('alumni.students', string='Alumni', ondelete='cascade', required=True, index=True)
    student_id = fields.Many2one('op.student', string='Student', readonly=True)
    student_code = fields.Integer(related='student_id.student_code', readonly=True, store=True)
    student_crh = fields.Float(related='student_id.new_crh', readonly=True, store=True)
    student_core = fields.Float(related='student_id.core_crh', readonly=True, store=True)
    student_elective = fields.Float(related='student_id.elective_crh', readonly=True, store=True)
    student_project = fields.Float(related='student_id.project_crh', readonly=True, store=True)
    student_gpa = fields.Float(related='student_id.new_gpa', readonly=True, store=True)
    semester_count = fields.Float(compute='_semester_count', readonly=True, store=True)
    seq = fields.Integer('#',readonly=True)
    isalumni = fields.Boolean()
    acadyear = fields.Many2one('op.academic.year', string='Academic Year', readonly=True, store=True)  
    semester = fields.Many2one('op.semesters', string='Semester', readonly=True, store=True)
    place = fields.Many2one(related='student_id.student_birth_place' , string='birth place',readonly=True)
    nationality = fields.Many2one(related='student_id.student_nationality',string='nationality' ,readonly=True)
    national = fields.Char( compute='_get_national_id' , readonly=True)
    total_degree = fields.Float(related='student_id.total_degree', readonly=True)
    total_degree_max = fields.Float(related='student_id.subject_degree', readonly=True)
    percent = fields.Float(related='student_id.final_degree', string='percent',readonly=True)
    grade= fields.Char(compute='_get_grade' , readonly=True)
    

    @api.depends('student_id')
    def _get_grade(self):
        grade = self.env['op.course.grades'].sudo().search(
            [('course_id', '=', self.student_id.course_id.id),('points_from', '<=', self.student_id.new_gpa)],order='percent_from desc',limit=1)
        grade_honor = self.student_id.course_id.honors_gpa
        if self.student_id.new_gpa >= grade_honor:
            if self.student_id.course_id.id == 6:
                self.grade = grade.grade_Eqiv.name.split('|')[0]
            elif self.student_id.faculty.id == 10 :
                acount_honers = 1
                accum_semester = self.env['op.student.accumlative.semesters'].sudo().search([('student_id', '=', self.student_id.id),('transferred', '=', False),('semester_id', '!=', 3 )]) #,('semester_gpa', '!=', 0 )
                for semester in accum_semester :
                    if semester.semester_id.id != 2 and semester.academicyear_id.id != 117:
                        if semester.semester_gpa < 3 :
                            acount_honers =0
                            break
                if acount_honers == 1 :
                    chk_fails = self.env['op.student.semesters.subjects'].sudo().search_count([('student_id', '=', self.student_id.id),('final_grade.pass_grade', '=', False),('final_grade', '!=', 1),('student_semester_id.transferred', '=', False)])
                    if chk_fails == 0 :
                        self.grade = grade.grade_Eqiv.name.split('|')[0]+"مع مرتبة الشرف"
            else :
                chk_fails = self.env['op.student.semesters.subjects'].sudo().search_count([('student_id', '=', self.student_id.id),('final_grade.pass_grade', '=', False),('final_grade', '!=', 1),('student_semester_id.transferred', '=', False)])
                if chk_fails == 0 :
                    self.grade = grade.grade_Eqiv.name.split('|')[0]+"مع مرتبة الشرف"
                else:
                    self.grade = grade.grade_Eqiv.name.split('|')[0]
        else :
            self.grade = grade.grade_Eqiv.name.split('|')[0]


    @api.depends('student_id')
    def _get_national_id(self):
        self.national = self.student_id.national_id
            
            
    @api.depends('student_id')
    def _semester_count(self):
        self.semester_count = self.env['op.student.accumlative.semesters'].sudo().search_count(
                                             [('student_id', '=', self.student_id.id), ('semester_id', '!=', 3), ('transferred', '!=', True)])