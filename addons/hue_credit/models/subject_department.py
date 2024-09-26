from odoo import models,fields

class CourseSubjectsDepartment(models.Model):
    _name = 'op.subject.department'
    _description = 'Add subject department'
    _rec_name = 'division_name'
    
    faculty_id = fields.Many2one('hue.faculties')
    division_name = fields.Char()
    head_of_division = fields.Many2one('op.faculty')
    
    
class opSubjects(models.Model):
    _inherit = 'op.subject'
    
    division_id = fields.Many2one('op.subject.department')
    subject_types = fields.Many2one('op.subjecttypes', string='Subject Type', required=False)