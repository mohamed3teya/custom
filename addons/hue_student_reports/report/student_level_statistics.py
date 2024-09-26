# -*- coding: utf-8 -*-
import time
from odoo import api, models


class StudentLevelStatistics(models.AbstractModel):
    _name = 'report.hue_student_reports.report_student_level_statistics'
    _description = "Student Level Statistics"

    @api.model
    def _get_report_values(self, docids, data=None):
        active_term = self.env['op.academic.term'].sudo().search([('active_run', '=', True)],limit=1)
        active_year = active_term.academic_year_id.name.split(":")[1].strip()
        term_name = active_term.semester_id.name.split("|")[0].strip()
        courses = self.env['op.course'].sudo().search([])

        docs = {'active_year':active_year,'term_name':term_name}
        docargs = {
            'docs': docs,
            'courses': courses,
            'get_male_student_count': self.get_male_student_count,
            'get_female_student_count': self.get_female_student_count,
            'get_total_student_count': self.get_total_student_count,
        }
        return docargs
    
    def get_male_student_count(self, course_id, level):
           students_count = self.env['op.student'].sudo().search(
               [('course_id', '=', course_id.id), ('level', '=', level.id), ('gender', '=', 'm')])
           return len(students_count)
       
    def get_female_student_count(self, course_id, level):
           students_count = self.env['op.student'].sudo().search(
               [('course_id', '=', course_id.id), ('level', '=', level.id), ('gender', '=', 'f')])
           return len(students_count)
    
    def get_total_student_count(self, course_id, level):
           students_count = self.env['op.student'].sudo().search(
               [('course_id', '=', course_id.id), ('level', '=', level.id), ('gender', 'in', ['m','f'])])
           return len(students_count)
    