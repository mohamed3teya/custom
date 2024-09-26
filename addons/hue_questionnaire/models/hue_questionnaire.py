from odoo import models, fields, api
from datetime import datetime


class HUEQuestionnaire(models.Model):
    _name = 'hue.questionnaire'
    _description = 'hue.questionnaire'
    
    
    name = fields.Char('Name')
    faculty_id = fields.Many2one('hue.faculties', 'College', required=True)
    survey_id = fields.Many2one('survey.survey', 'Subject Survey', required=True)
    instructor_survey_id = fields.Many2one('survey.survey', 'Instructor Survey', required=True)
    t_assistant_survey_id = fields.Many2one('survey.survey', 'T Assistant Survey', required=True)
    service_survey_id = fields.Many2one('survey.survey', 'Service Survey', required=True)
    active = fields.Boolean('Active', default=True)
    validation_min_date = fields.Date('Start Date')
    validation_max_date = fields.Date('End Date')
    notes = fields.Text('Notes')
    done_count = fields.Integer(compute="_compute_done", string='Done Count')
    all_count = fields.Integer(string='All Count')
    count_percentage = fields.Integer(string='Count %')


    def _compute_done(self):
        all_count = 0
        count = 0
        self.done_count = count
        self.all_count = all_count


    def validate_date(self):
        self.ensure_one()
        try:
            date_from_string = fields.Date.from_string
            dateanswer = datetime.now().date()
            min_date = date_from_string(self.validation_min_date)
            max_date = date_from_string(self.validation_max_date)
            if min_date and max_date and not (min_date <= dateanswer <= max_date):
                return False
            elif min_date and not min_date <= dateanswer:
                return False
            elif max_date and not dateanswer <= max_date:
                return False
            else:
                return True
        except ValueError:  # check that it is a date has been done hereunder
            pass
        return True
    
    
class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"
    
    college_id = fields.Many2one('hue.faculties', 'College')
    instructor_id = fields.Many2one('op.faculty', 'Instructor')
    subject_id = fields.Many2one('op.subject', 'Subject')
    student_id = fields.Many2one('op.student', 'Student')
    academic_year = fields.Many2one('op.academic.year', string='Academic Year')
    semester = fields.Many2one('op.semesters', string='Semester')
    

class QSession(models.Model):
	_inherit = 'op.session'

	tree_clo_acl_ids = fields.Char(compute="_compute_tree_clo_acl_ids", search='tree_clo_acl_ids_search')


	def _compute_tree_clo_acl_ids(self):
		print('View My Tree CLO ACL')


	def tree_clo_acl_ids_search(self, operator, operand):
		available_ids = []
		academic_year = self.env['op.academic.year'].sudo().search([('current', '=', True)], limit=1)
		semester = self.env['op.semesters'].sudo().search([('current', '=', True)], limit=1)
		batch = self.env['op.batch'].sudo().search([('academic_year', '=', academic_year.id), ('semester', '=', semester.id)])
		emp = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)])
		if not emp:
			emp = self.env.user.employee_id
		course_ids = emp.course_ids
		for x in batch :
			start_date = x.default_week_start
			end_date = x.default_week_end
			sessions = self.env['op.session'].sudo().search([('course_id', 'in', course_ids.ids),('batch_id', 'in', batch.ids)])
			for session in sessions:
				if session.day_date >= start_date and session.day_date <= end_date:
					available_ids.append(session.id)
			return [('id', 'in', available_ids)]


class StudentExtensionExt(models.Model):
    _inherit = 'op.student'
    
    
    def subject_questionnaire_done(self, subject_id):
        academic_year = self.env['op.academic.year'].sudo().search([('current', '=', True)], limit=1)
        semester = self.env['op.semesters'].sudo().search([('id', '=', 2)], limit=1)
        UserInput = self.env['survey.user_input']
        std_session= []
        sessionsID= self.env['op.session'].sudo().search([('batch_id.academic_year', '=',academic_year.id ),('batch_id.semester', '=',semester.id ),('course_id', '=',self.course_id.id )])
        if sessionsID :
            for x in sessionsID :
                if self.id  in x.student_ids.ids:
                    std_session.append(x)
        if self.faculty.id == 8 or self.faculty.id == 12:
            return True
        faculties = []
        for session in self.session_ids:
            if session.subject_id.id == subject_id:
                for faculty in session.q_faculty_ids:
                    if faculty not in faculties:
                        faculties.append(faculty)
        for faculty in faculties:
            faculty_user_input = UserInput.sudo().search([('college_id', '=', self.faculty.id), ('subject_id', '=', int(subject_id)), ('student_id', '=', self.id), ('instructor_id', '=', faculty.id), ('academic_year', '=', academic_year.id), ('semester', '=', semester.id), ('state', '=', 'done')], limit=1)
            if not faculty_user_input:
                return False
        user_input = UserInput.sudo().search([('college_id', '=', self.faculty.id), ('subject_id', '=', subject_id), ('student_id', '=', self.id), ('instructor_id', '=', False), ('academic_year', '=', academic_year.id), ('semester', '=', semester.id), ('state', '=', 'done')], limit=1)
        if not user_input:
            return False
        return True
    
    
    def questionnaire_done(self, subject_id=False):
        academic_year = self.env['op.academic.year'].sudo().search([('run_semester_gpa', '=', True)], limit=1)		
        semester = self.env['op.semesters'].sudo().search([('run_semester_gpa', '=', True)], limit=1) 
        UserInput = self.env['survey.user_input']
        subjectIDs = self.env['op.student.semesters.subjects'].sudo().search([('academicyear_id', '=',academic_year.id ),('semester_id', '=',semester.id ),
            ('student_id', '=',self.id )])
        
        if self.faculty.check_questionnaire == False :
            return True
        subjects = []
        for session in self.session_ids:
            if session.subject_id not in subjects:
                subjects.append(session.subject_id)
        for subject in subjects:
            if not self.subject_questionnaire_done(subject.id):
                return False
        user_input = UserInput.sudo().search([('college_id', '=', self.faculty.id), ('subject_id', '=', False), ('student_id', '=', self.id), ('instructor_id', '=', False), ('academic_year', '=', academic_year.id), ('semester', '=', semester.id), ('state', '=', 'done')], limit=1)	
        if not user_input:
            return False
        return True
    
    
    def questionnaire_done_mark(self, subject_id=False):
        academic_year = self.env['op.academic.year'].sudo().search([('current', '=', True)], limit=1)		
        semester = self.env['op.semesters'].sudo().search([('id', '=', 2)], limit=1) 
        UserInput = self.env['survey.user_input']
        subjectIDs = self.env['op.student.semesters.subjects'].sudo().search([('academicyear_id', '=',academic_year.id ),('semester_id', '=',semester.id ),
            ('student_id', '=',self.id )])
        subjects = []
        for session in self.session_ids:
            if session.subject_id not in subjects:
                subjects.append(session.subject_id)
        for subject in subjects:
            if not self.subject_questionnaire_done(subject.id):
                return False
        user_input = UserInput.sudo().search([('college_id', '=', self.faculty.id), ('subject_id', '=', False), ('student_id', '=', self.id), ('instructor_id', '=', False), ('academic_year', '=', academic_year.id), ('semester', '=', semester.id), ('state', '=', 'done')], limit=1)
        
        if not user_input:
            return False
        return True