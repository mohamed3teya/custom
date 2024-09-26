
import calendar
import pytz
import time
from datetime import datetime
from odoo import models, api, _, fields, tools


class MiliteryStudentReport(models.AbstractModel):
    _name = "report.hue_student_reports_yasmin.military_education_student"
    _description = "Military Education Student Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        faculty_id = docs.faculty_id
        academic_year_id = docs.academic_year_id
        semester_id = docs.semester_id
        military_num = docs.military_num
        level = docs.level
        student_status = docs.student_status
        no_military = docs.no_military

        domain = []
        domain.append(('gender', '=', 'm'))
        if faculty_id:
            domain.append(('faculty', '=', faculty_id.id))
            
        if academic_year_id:
            domain.append(('done_military_id.academic_year_id', '=', academic_year_id.id))
          
        if semester_id:
            domain.append(('done_military_id.semester_id', '=', semester_id.id))
           
        if military_num:
            domain.append(('done_military_id', '=', military_num.id))
            
        if level:
            domain.append(('level.level_id', '=', level.id))
          
        if no_military:
            domain.append(('military_done', '=', False))
            
        if student_status:
            domain.append(('student_status', 'in',docs.student_status.ids))
         
       
        students = self.env['op.student'].sudo().search(domain ,order=" student_code,level")
        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'docs': docs,
            'students':students,            
        }
        return docargs
