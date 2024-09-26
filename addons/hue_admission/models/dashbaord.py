from odoo import models, api, fields, _
from odoo.exceptions import UserError

import logging
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.http import request
from odoo.tools import float_utils
import random

_logger = logging.getLogger(__name__)

class OpAdmissionDashboard(models.Model):
    _inherit = 'op.admission'

    def random_color(self):
        colors = ["#E52B50","#FFBF00","#9966CC","#FBCEB1","#007FFF","#8A2BE2","#A7FC00","#008080","#40826D",'#00A86B','#DC143C','#483C32']
        random.shuffle(colors)
        return colors[0]
    
    @api.model
    def get_admission_details(self):
        uid = request.session.uid
        employee = []
        faculties = self.env['hue.faculties'].sudo().search_count([])
        hue_admission = self.env['op.hue.admission'].sudo().search([('active_admission','=',True)],limit=1)
        applicants = self.env['op.admission'].sudo().search_count([('horus_admission_id','=',hue_admission.id)])
        admission_registers = self.env['op.admission.register'].sudo().search([('hue_admission_id','=',hue_admission.id)])
        total_Applications  = self.env['op.admission.application'].sudo().search_count([('application_status','in',['paid','enroll']),('admission_id.horus_admission_id','=',hue_admission.id)])        
        # cr = self._cr
        # self._cr.execute("""
        # select e.name as name , e.id as id from op_admission_register e inner join op_hue_admission j on (j.id = '%s')
        # """ % (hue_admission.id))                
        # admission_registers = cr.dictfetchall()
        certificate_total = self.env['op.admission'].read_group(domain=False, fields=False, groupby='certificate_id', offset=0, limit=None, orderby=False, lazy=True)
        
        ### Certificate and Nationality
        cr = self._cr
        cr.execute("""select DISTINCT ON (certificate_id)certificate_id from op_admission""")
        certificate_total = cr.dictfetchall()        
        certificate_label = []
        
        for certificate in certificate_total:
            certificate_name = self.env['hue.certificates'].sudo().search([('id','=',certificate['certificate_id'])],limit=1).name
            if certificate_name:
                certificate_label.append(certificate_name)
            
        #Nationality Data
        cr.execute("""select DISTINCT ON (nationality_id)nationality_id from op_admission""")
        nationality_total = cr.dictfetchall()        
        nationality_label = []
        
        for nationality in nationality_total:
            nationality_name = self.env['hue.nationalities'].sudo().search([('id','=',nationality['nationality_id'])],limit=1).name
            if nationality_name:
                nationality_label.append(nationality_name)

        #certificate Data
        certificate_data = []
        candidate_certificate_sum = []
        enrolled_data = []
        enrolled_certificate_sum = []        
        for admission_register in admission_registers:
            candidate_certificate_data = []
            enrolled_certificate_data = []
            for certificate in certificate_total:
                certificate_name = self.env['hue.certificates'].sudo().search([('id','=',certificate['certificate_id'])],limit=1).name
                if certificate_name:
                    candidate_certificate_total = self.env['op.admission.application'].sudo().search_count([('admission_id.certificate_id','=',certificate['certificate_id']),('register_id','=',admission_register.id),('application_status','=','paid'),('admission_id.state','=','admission'),('admission_id.horus_admission_id','=',hue_admission.id)])
                    enrolled_certificate_total = self.env['op.admission.application'].sudo().search_count([('admission_id.certificate_id','=',certificate['certificate_id']),('register_id','=',admission_register.id),('application_status','=','enroll'),('admission_id.state','=','done'),('admission_id.horus_admission_id','=',hue_admission.id)])                
                    candidate_certificate_data.append(candidate_certificate_total)
                    enrolled_certificate_data.append(enrolled_certificate_total)
            candidate_certificate_sum.append(candidate_certificate_data)
            enrolled_certificate_sum.append(enrolled_certificate_data)
            b = {'label':admission_register.name,'backgroundColor':self.random_color(),'borderWidth':1,'data':candidate_certificate_data}
            certificate_data.append(dict(b))
            b = {'label':admission_register.name,'backgroundColor':self.random_color(),'borderWidth':1,'data':enrolled_certificate_data}
            enrolled_data.append(dict(b))            
        enrolled_certificate_sum = [sum(elts) for elts in zip(*enrolled_certificate_sum)]
        candidate_certificate_sum = [sum(elts) for elts in zip(*candidate_certificate_sum)]  
        


        #Nationality Data
        nationality_data = []
        candidate_nationality_sum = []
        enrolled_nationality_data_all = []
        enrolled_nationality_sum = []        
        for admission_register in admission_registers:
            candidate_nationality_data = []
            enrolled_nationality_data = []
            for nationality in nationality_total:
                nationality_name = self.env['hue.nationalities'].sudo().search([('id','=',nationality['nationality_id'])],limit=1).name
                if nationality_name :
                    candidate_nationality_total = self.env['op.admission.application'].sudo().search_count([('admission_id.nationality_id','=',nationality['nationality_id']),('register_id','=',admission_register.id),('application_status','=','paid'),('admission_id.state','=','admission'),('admission_id.horus_admission_id','=',hue_admission.id)])
                    enrolled_nationality_total = self.env['op.admission.application'].sudo().search_count([('admission_id.nationality_id','=',nationality['nationality_id']),('register_id','=',admission_register.id),('application_status','=','enroll'),('admission_id.state','=','done'),('admission_id.horus_admission_id','=',hue_admission.id)])                
                    candidate_nationality_data.append(candidate_nationality_total)                    
                    enrolled_nationality_data.append(enrolled_nationality_total)
            candidate_nationality_sum.append(candidate_nationality_data)
            print("###############")
            print(enrolled_nationality_data)
            enrolled_nationality_sum.append(enrolled_nationality_data)
            print("@@@@@@@@@@@@@@@")
            print(enrolled_nationality_sum)
            print("@@@@@@@@@@@@@@@@")
            b = {'label':admission_register.name,'backgroundColor':self.random_color(),'borderWidth':1,'data':candidate_nationality_data}
            nationality_data.append(dict(b))
            b = {'label':admission_register.name,'backgroundColor':self.random_color(),'borderWidth':1,'data':enrolled_nationality_data}
            enrolled_nationality_data_all.append(dict(b))
        print(candidate_nationality_sum)
        print(enrolled_nationality_sum)
        candidate_nationality_sum = [sum(elts) for elts in zip(*candidate_nationality_sum)]            
        enrolled_nationality_sum = [sum(elts) for elts in zip(*enrolled_nationality_sum)]               
            

    
        admission_register_applicants  = []
        admission_register_candidate   = []
        admission_register_enrolled   = []
        admission_register_label = []
        admission_register_tb = []
        for admission_register in admission_registers:
            admission_register_arr_tb = []
            applicants_total = self.env['op.admission.application'].sudo().search_count([('register_id','=',admission_register.id),('application_status','=','paid'),('admission_id.state','=','confirm'),('admission_id.horus_admission_id','=',hue_admission.id)])
            admission_register_applicants.append(applicants_total)
            candidate_total = self.env['op.admission.application'].sudo().search_count([('register_id','=',admission_register.id),('application_status','=','paid'),('admission_id.state','=','admission'),('admission_id.horus_admission_id','=',hue_admission.id)])
            admission_register_candidate.append(candidate_total)
            enrolled_total = self.env['op.admission.application'].sudo().search_count([('register_id','=',admission_register.id),('application_status','=','enroll'),('admission_id.state','=','done'),('admission_id.horus_admission_id','=',hue_admission.id)])
            admission_register_enrolled.append(enrolled_total)
            admission_register_label.append(admission_register.name)
            admission_register_arr_tb.append(admission_register.name)
            admission_register_arr_tb.append(applicants_total)
            admission_register_arr_tb.append(candidate_total)
            admission_register_arr_tb.append(enrolled_total)
            admission_register_tb.append(admission_register_arr_tb)
        # payroll Datas for Bar chart
        


        #get registered student table
        cr = self.env.cr
        query = """
            select j.application_number as application_number,j.id as admission_id, e.application_date as date , j.name as name , d.name as admission_register ,j.state
            from op_admission_application e 
            inner join op_admission j on (j.id = e.admission_id)
            inner join op_admission_register d on (d.id = e.register_id)
            where e.application_status ='paid' and j.horus_admission_id = """+str(hue_admission.id)+""" and j.state = 'confirm'"""
        print(query)
        cr.execute(query)
        
        registred_table = cr.dictfetchall()
        query = """
            select j.application_number as application_number,j.id as admission_id, e.application_date as date , j.name as name , d.name as admission_register ,j.state
            from op_admission_application e 
            inner join op_admission j on (j.id = e.admission_id)
            inner join op_admission_register d on (d.id = e.register_id)
            where e.application_status ='paid' and j.horus_admission_id = """+str(hue_admission.id)+""" and j.state = 'admission'""" 
        cr.execute(query)
        
        candidate_table = cr.dictfetchall()
        query = """
            select j.application_number as application_number,j.id as admission_id, e.application_date as date , j.name as name , d.name as admission_register ,j.state
            from op_admission_application e 
            inner join op_admission j on (j.id = e.admission_id)
            inner join op_admission_register d on (d.id = e.register_id)
            where e.application_status ='enroll' and j.horus_admission_id = """+str(hue_admission.id)+""" and j.state = 'done'""" 
        cr.execute(query)
        enrolled_table = cr.dictfetchall()
        
        print(registred_table)
        data = {
            'faculties':faculties,
            'hue_admission':hue_admission.name,
            'total_registered_students':applicants,
            'admission_registers':admission_register_tb,
             'admission_register_label': admission_register_label,
             'admission_registers_count':len(admission_registers),
             'total_registers_count':len(registred_table),
             'total_Applications':(total_Applications),
             'total_admission_register_candidate':admission_register_candidate,
             'total_admission_register_applicants':admission_register_applicants,
             'total_admission_register_enrolled':admission_register_enrolled,
             'certificate_total':certificate_total,
             'certificate_label':certificate_label,
             'certificate_data':certificate_data,
             'candidate_certificate_sum':candidate_certificate_sum,
             'nationality_label':nationality_label,
             'nationality_data':nationality_data,
             'candidate_nationality_sum':candidate_nationality_sum,
             'registred_table':registred_table,
             'candidate_table':candidate_table,
             'total_candidate_count':len(candidate_table),
             'enrolled_data':enrolled_data,
             'enrolled_certificate_sum':enrolled_certificate_sum,
             'enrolled_nationality_data':enrolled_nationality_data_all,
             'enrolled_nationality_sum':enrolled_nationality_sum,
             "enrolled_table":enrolled_table,
             'total_erolled_count':len(enrolled_table),
        }
        # employee[0].update(data)
        return data


    @api.model
    def get_dept_employee(self):
        cr = self._cr
        cr.execute(
            'select department_id, hr_department.name,count(*) from hr_employee join hr_department on hr_department.id=hr_employee.department_id group by hr_employee.department_id,hr_department.name')
        dat = cr.fetchall()
        data = []
        for i in range(0, len(dat)):
            data.append({'label': dat[i][1], 'value': dat[i][2]})
        return data