
import calendar
import pytz
import time
from datetime import datetime
from odoo import models, api, _, fields, tools


class MiliteryrecruitmentReport(models.AbstractModel):
    _name = "report.hue_student_reports_yasmin.military_recruitment_data"
    _description = "Military recruitment Data Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        domain = []
        domain.append(('gender', '=', 'm'))
        domain.append(('student_nationality', '=', 1))
        status_ids = self.env['hue.std.data.status'].sudo().search([('active_invoice', '=', True)])._ids              
        if docs.faculty:
            domain.append(('faculty', '=',docs.faculty.id))
        if docs.student_city:
            domain.append(('student_city', '=',docs.student_city.id))
        if docs.student_certificate:
            domain.append(('student_certificates', '=',docs.student_certificate.id))       
        if docs.level:
            domain.append(('level', '=',docs.level.id))
        if docs.student_status:
            domain.append(('student_status', 'in',docs.student_status.ids))
        if docs.military_status:
            domain.append(('military_status', '=',docs.military_status))
        else :
            if docs.all_military_status :
                domain.append(('military_status', '!=',False))
        if docs.join_year:
            domain.append(('join_year', '=',docs.join_year.id))
        if docs.age and docs.age_date:
            stds_age = self.env['op.student'].sudo().search([('student_nationality', '=', 1),('gender', '=', 'm'),('birth_date', '!=',False)]) 
            stds = []
            for std in stds_age:
                if  (datetime.strptime( docs.age_date, '%Y-%m-%d') - datetime.strptime( std.birth_date, '%Y-%m-%d')).days  >= docs.age *365 :
                    stds.append(std.id)
            domain.append(('id', 'in',stds))
        students = self.env['op.student'].sudo().search(domain ,order="student_code") 
        students_lst = list(students)
        each_pages = docs.std_per_page
        students_data = [students_lst[x:x + each_pages] for x in range(0, len(students_lst), each_pages)]
        
        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'docs': docs,
            'students':students,
            'students_data':students_data,            
        }
        return docargs
