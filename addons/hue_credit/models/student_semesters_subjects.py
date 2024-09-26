from odoo import models, fields, api

class StudentSubjects(models.Model):
    _name = 'op.student.semesters.subjects'
    _description = 'Student Semester Subjects'
    
    
    student_semester_id = fields.Many2one('op.student.accumlative.semesters', string='Student Semester',ondelete='cascade')
    student_id = fields.Many2one('op.student', string='Student', related='student_semester_id.student_id', store=True)
    student_code = fields.Integer(related='student_semester_id.student_id.student_code', store=True)
    course_id = fields.Many2one('op.course', string='Course', related='student_semester_id.course_id', store=True)
    academicyear_id = fields.Many2one('op.academic.year', string='Academic Year',
                                      related='student_semester_id.academicyear_id', store=True)
    semester_id = fields.Many2one('op.semesters', string='Semester', related='student_semester_id.semester_id',store=True)
    semester_seq = fields.Integer(related='academicyear_id.sequence')
    academicyear_seq = fields.Integer(related='semester_id.sequence')
    subject_id = fields.Many2one('op.subject', string='Subjects', required=True)
    subject_credit = fields.Integer(related='subject_id.subject_credithours', readonly=True, store=True)
    approved_by = fields.Many2one('res.users')
    subject_degree = fields.Float('Degree')
    subject_grade = fields.Many2one('op.grades', string='Grades')
    control_grade = fields.Many2one('op.grades')
    control_degree = fields.Float()
    grade_final = fields.Float('FinalDegree')
    grade_quiz = fields.Float('QuizDegree')
    grade_activity = fields.Float('ActivityDegree')
    grade_attendance = fields.Float('AttendanceDegree')
    grade_pract = fields.Float('PractDegree')
    grade_pract2 = fields.Float('Pract2Degree')
    grade_oral = fields.Float('OralDegree')
    grade_medterm = fields.Float('MedtermDegree')
    grade_coursework = fields.Float('CourseWorkDegree')
    grade_pract_oral = fields.Float('PratOralWorkDegree')
    grade_clinic = fields.Float('ClinicWorkDegree')
    grade_mcq = fields.Float('MCQDegree')
    grade_practical = fields.Float('PracticalDegree')
    grade_essay = fields.Float('EssayDegree')
    grade_eassy = fields.Float('EssayDegree')
    grade_skilllab = fields.Float('SkilllabDegree')
    grade_pbl = fields.Float('pblDegree')
    grade_portfolio = fields.Float('portfolioDegree')
    grade_logbook = fields.Float('logbookDegree')
    grade_sdl = fields.Float('sdlDegree')
    grade_fieldstudy = fields.Float('fieldstudyDegree')
    grade_skillexam = fields.Float('skillexamDegree')
    closeflag = fields.Integer('CloseFlag')
    quesflag = fields.Char('QuesFlag')
    seatno = fields.Integer('SeatNo')
    committee_id = fields.Many2one('op.exam.committees', string='CommitteeID')
    studytable_id = fields.Many2one('op.studytimetable', string='StudyTableID')
    group_id = fields.Integer('GroupID')
    section_id = fields.Integer('SectionID')
    attendance_id = fields.Many2one('op.attendance', string='AttendanceID')
    final_degree = fields.Float(string='Final Degree', compute='_compute_degree_grade', store="True")
    final_grade = fields.Many2one('op.grades', string='Final Grade', compute='_compute_degree_grade', store="True")
    final_grade_sequence = fields.Integer(related='final_grade.sequence', string ='final grade sequence ' , readonly=True, store=True)
    points = fields.Float(string='Points', compute='_compute_grade_points', store="True")
    
    
    @api.depends('subject_grade', 'subject_degree', 'control_grade', 'control_degree')
    def _compute_degree_grade(self):
        for rec in self:
            if rec.control_grade:
                rec.final_grade = rec.control_grade
            else:
                rec.final_grade = rec.subject_grade
            if rec.control_degree:
                rec.final_degree = rec.control_degree
            else:
                rec.final_degree = rec.subject_degree

            
    @api.depends('final_grade', 'subject_credit','course_id')
    def _compute_grade_points(self):
        for rec in self:
            if rec.final_grade:
                grade_points = self.env['op.course.grades'].sudo().search([('course_id', '=', rec.course_id.id), ('grade_id', '=', rec.final_grade.id)])
                rec.points = grade_points.points_from * rec.subject_credit