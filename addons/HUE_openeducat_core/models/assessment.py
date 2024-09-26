from odoo import fields, models

class Assessment(models.Model):
    _name= 'op.assessments'
    _description = 'Activities to evaluate student performance'
    
    name = fields.Char()
    control_field = fields.Selection(
        [('grade_quiz', 'grade_quiz'), ('grade_medterm', 'grade_medterm'), ('grade_coursework', 'grade_coursework')
            , ('grade_oral', 'grade_oral'), ('grade_attendance', 'grade_attendance'),
         ('grade_activity', 'grade_activity')
            , ('grade_pract', 'grade_pract'), ('grade_pract2', 'grade_pract2')
            , ('grade_mcq', 'grade_mcq'), ('grade_practical', 'grade_practical'), ('grade_eassy', 'grade_eassy')
            , ('grade_clinic', 'grade_clinic'), ('grade_pract_oral', 'grade_pract_oral'),
         ('grade_final', 'grade_final'),('grade_skilllab', 'grade_skilllab'),('grade_pbl', 'grade_pbl'),('grade_portfolio', 'grade_portfolio'),('grade_logbook', 'grade_logbook'),
         ('grade_sdl', 'grade_sdl'),('grade_fieldstudy', 'grade_fieldstudy'),('grade_skillexam', 'grade_skillexam')], string='control field')