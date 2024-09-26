# -*- coding: utf-8 -*-
from odoo import http, _
from datetime import date, datetime
from odoo.addons.http_routing.models.ir_http import slug
from odoo.http import request
import hashlib
import hmac
import base64
import uuid
class ApplyPortal(http.Controller):
 
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

    def allowed_file(self,filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    def security(self,utc,app_id,total,forename,surname,phone,email,address):
        secret_key = '16d22825d9944f74924fd26ef6d9f9c4cd09c7a492eb45a586f54640e137a7d28eee0a5562024fecbf7397f3e3a6b67cbc5b18aecdc848ad8fb74cfdad0bcd0e8090cf3246ce458795953c18024b0a98984e2af44a4e47219694fa810c95c24e0aa614b02de6456c808dc7a5c44aeadd37598fdccdcc43548573e6d612c2fcb2'
        total = str(total)
        joined = 'access_key=05d30ead93f731cc8f7fc4e029386032,profile_id=34BCD4C0-8BB2-417E-BD21-A5611FAEA2DE,transaction_uuid='+utc+',signed_field_names=access_key,profile_id,transaction_uuid,signed_field_names,unsigned_field_names,signed_date_time,locale,transaction_type,reference_number,amount,currency,bill_to_forename,bill_to_surname,bill_to_phone,bill_to_email,bill_to_address_line1,bill_to_address_line2,bill_to_address_city,bill_to_address_state,bill_to_address_postal_code,bill_to_address_country,unsigned_field_names=,signed_date_time='+utc+',locale=en,transaction_type=sale,reference_number='+app_id+',amount='+total+',currency=EGP,bill_to_forename='+forename+',bill_to_surname='+surname+',bill_to_phone='+phone+',bill_to_email='+email+',bill_to_address_line1='+address+',bill_to_address_line2=,bill_to_address_city=mansoura,bill_to_address_state=,bill_to_address_postal_code=,bill_to_address_country=EG'
        print(joined)
        message = bytes(joined, 'utf-8')
        secret = bytes(secret_key, 'utf-8')
        hash = hmac.new(secret, message, hashlib.sha256)
        hash.hexdigest()
        signature = base64.b64encode(hash.digest())
        return (signature)
        
        
        
    @http.route('/summary', type='http', auth="public", website=True,csrf=False)
    def admission_summary(self, **kw):
        print('111111111111111111111111111111111111111111111')
        print(kw.items())
        params = {}
        for field_name, field_value in kw.items():
            print(field_name)
            print(field_value)
            print('5555555555555555555555555555555555')
            params[field_name] = field_value
        if  params['decision'] == 'CANCEL':
            return request.redirect("/payment/%s"% (params['req_reference_number']))
        if  params['decision'] == 'ERROR':
            return request.redirect("/payment/%s"% (params['req_reference_number']))
        if  params['decision'] == 'DECLINE':
            return request.redirect("/payment/%s"% (params['req_reference_number']))        
        
        if  params['decision'] == 'ACCEPT':
             application = http.request.env['op.admission'].sudo().search([('ref_number','=',params['req_reference_number'])])
             application.online_confirm_in_progress()
            
            #return request.redirect("/payment/%s"% (params['req_reference_number']))        
       
        values={
            'application':application
        }
 
        return request.render("hue_admission.summary",values)
    

    @http.route('/admission', type='http', auth="public", website=True)
    def admission_home(self, **kw):
        return request.render("hue_admission.admission")
    

    # @http.route('/apply', type='http', auth="public", website=True)
    # def admission_apply(self, **kw):
    #     universities = http.request.env['hue.faculties'].sudo().search([])
    #      
    #     utc = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
    #     datetimev = datetime.datetime.now()
    #     ref = int(datetimev.strftime("%Y%m%d%H%M%S"))    
    #     values = {
    #         'universities':universities,
    #         'ref':ref,
    #         'utc':utc
    #     }
    #  
    #  
    #     return request.render("openeducat_admission.apply",values)
    

    @http.route('/payment/<ref_num>', type='http', auth="public", website=True)
    def admission_payment(self,ref_num,**kw):
        universities = http.request.env['hue.faculties'].sudo().search([])
        application = http.request.env['op.admission'].sudo().search([('ref_number','=',ref_num)])
        for x in application.admission_application_ids :
            print("hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh")
            print(x.register_id.name)
       
        params = 0
        utc = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
        datetimev = datetime.now()
        print(utc)
        print(datetimev)
        print('wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww')
        if application:
            english_name  = application.english_name
            data = english_name.split(" ")
            try:
                forename = data[0]
            except IndexError:
                forename = "no name"
            try  :
                surname = data[1]
            except IndexError:
                surname = data[0]
            values = {
                'universities':universities,
                'utc':utc,
                'application':application,
                'forename':forename,
                'surname':surname,
                'phone':application.mobile_number,
                'email':application.email,
                'address':application.address[0:40],
                'sign':self.security,
            }
            return request.render("hue_admission.payment",values)
        else:
            return request.redirect("/apply") 
            
    
    @http.route('/edit/<ref_num>', type='http',csrf=False, auth="public", website=True)
    def admission_edit_ref(self,ref_num, **kw):
        application = http.request.env['op.admission'].sudo().search([('ref_number','=',ref_num)])
        admission = http.request.env['op.hue.admission'].sudo().search([('active_admission','=',True)],limit=1) 
        universities = http.request.env['op.admission.register'].sudo().search([('hue_admission_id','=',admission.id)])
        
        governorates = http.request.env['hue.cities'].sudo().search([]) 
        certificates = http.request.env['hue.certificates'].sudo().search([('certificate_active','=',True)])
        certificates_country = http.request.env['hue.nationalities'].sudo().search([])
        
        if application :
            birth_date =  datetime.strptime(str(application.birth_date), "%Y-%m-%d").date()
            day =birth_date.day
            month =birth_date.month
            year =birth_date.year
            months_choices = []
            for i in range(1,13):
                months_choices.append((i, date(2008, i, 1).strftime('%B')))            
            values = {
                'day':day,
                'days':list(range(1, 32)),
                'years':list(range(1970, 2010)),
                'months':months_choices,
                'month':month,
                'year':year,
                'mode':'edit',
                'application':application,
                'universities':universities,
                'countries':certificates_country,
                'certificates':certificates,
                'certificates_country':certificates_country,
                'governorates':governorates                
            }
            return request.render("hue_admission.edit",values)
        
    @http.route('/edit', type='http',csrf=False, auth="public", website=True)
    def admission_edit(self, **kw):
        if kw.get('national_id', False):
            national_id = kw.get('national_id')
            params= {}
            admission = http.request.env['op.hue.admission'].sudo().search([('active_admission','=',True)],limit=1)
            application = http.request.env['op.admission'].sudo().search([('national_id','=',national_id),('horus_admission_id','=',admission.id)],limit=1)
            if not application :
                values = {
                   'national_id':national_id,
                   'mode':'search',
                }
                return request.render("hue_admission.admission",values)
            if application.state in ['online_draft','draft']:
                return request.redirect("/payment/%s"% (application.ref_number))
            
            if application.state not in ['online_draft','draft']:
                values = {
                    'mode':'view',
                    'application':application,
                }
                return request.render("hue_admission.edit",values)
    
    @http.route('/apply', type='http', auth="public", website=True)
    def admission_apply(self, **kw):
        print("helooooooooooooooooooooooooooooo")
        # return request.redirect("/admission")
        admission_apply = False
        calendar = request.env['hue.event.calendar'].sudo().search(
                    [('type', '=', 'admission_apply'),
                     ('start_date', '<=', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                     ('end_date', '>=', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))], limit=1)
        if calendar :
            admission_apply = True
        admission = http.request.env['op.hue.admission'].sudo().search([('active_admission','=',True)],limit=1) 
        universities = http.request.env['op.admission.register'].sudo().search([('hue_admission_id','=',admission.id)])
        
        governorates = http.request.env['hue.cities'].sudo().search([]) 
        certificates = http.request.env['hue.certificates'].sudo().search([('certificate_active','=',True)])
        certificates_country = http.request.env['hue.nationalities'].sudo().search([])
        datetimev = datetime.now()
        seq = int(datetimev.strftime("%Y%m%d%H%M%S"))
        values = {
            'universities':universities,
            'datetime':seq,
            'countries':certificates_country,
            'certificates':certificates,
            'certificates_country':certificates_country,
            'governorates':governorates ,
            'admission_apply':admission_apply
        }
     
        return request.render("hue_admission.apply",values)
    



    @http.route('/save_edit', methods=['POST'], type='http', auth="public", website=True)
    def admission_save_edit(self, **kw):        
        params= {}
        print(kw.items())
        for field_name, field_value in kw.items():
            params[field_name] = field_value
        if kw.get('ref_number', False):
            ref_number = kw.get('ref_number')    
            admission = http.request.env['op.hue.admission'].sudo().search([('active_admission','=',True)],limit=1)
            application = http.request.env['op.admission'].sudo().search([('ref_number','=',ref_number),('horus_admission_id','=',admission.id)],limit=1)
            if  application :
                params['name'] =  params['arabic_name']
                date1 = date(year=int(params['byear']), month=int(params['bmonth']), day=int(params['bday']))
                params['birth_date'] = date1
                params['birth_certificate'] =  False
                try:
                    application.sudo().write(params)
                    status = 'success'
                except:
                    status = 'fail'
                values = {
                    'mode':'view',
                    'status':status,
                    'application':application,
                }
                return request.render("hue_admission.edit",values)                
            
        
    @http.route('/create', methods=['POST'], type='http', auth="public", website=True)
    def admission_create(self, **kw):        
        universities = http.request.env['hue.faculties'].sudo().search([])
        params= {}
        for field_name, field_value in kw.items():
            if field_name == "passport_id" and field_value != '':
                field_name = "national_id"
            params[field_name] = field_value
        ref = uuid.uuid4()
        if  http.request.env['op.admission'].sudo().search([('ref_number','=',ref)]):
            ref = uuid.uuid4()
        params['name'] =  params['arabic_name']
        params['ref_number'] = ref
        params['state'] = 'online_draft'
        admission = http.request.env['op.hue.admission'].sudo().search([('active_admission','=',True)],limit=1)   
        params['horus_admission_id'] = admission.id
        date1 = date(year=int(params['byear']), month=int(params['bmonth']), day=int(params['bday']))
        params['birth_date'] = date1
        #
        params['birth_certificate'] =  False
        # partner_id = http.request.env['res.partner'].create({
        #             'name': params['arabic_name']
        #         })
        # params['partner_id'] = partner_id.id
        # params['birth_certificate'] = base64.b64encode(attachment)
        exist_application = http.request.env['op.admission'].sudo().search([('horus_admission_id','=',admission.id),('national_id','=',params['national_id'])],limit=1)

        if  exist_application:
            return request.redirect("/payment/%s"% (exist_application.ref_number))
            #return request.render("openeducat_admission.testt",{'faculty':'Must Select Faculty'})
        try:
            faculty1 = params['faculty1']
            try:
                application = http.request.env['op.admission'].sudo().create(params)
            except KeyError as e:
                print("tessssssssssssssst")
                return request.render('hue_admission.404',{'fail':'حدث خطأ ما فى تسجيل الطلب برجاء المحاولة مرة أخري , أو التحدث مع احد ممثلي الجامعة اسفل الصفحة'})
                # return request.render("openeducat_admission.apply",{'fail':'حدث خطأ ما فى تسجيل الطلب برجاء المحاولة مرة أخري , أو التحدث مع احد ممثلي الجامعة اسفل الصفحة'})
                
                # return request.render("openeducat_admission.apply",{'faculty':'Must Select Faculty'})
                
            if kw.get('birth_certificate', False):
                attachments = request.env['ir.attachment']
                name = kw.get('birth_certificate').filename
                file = kw.get('birth_certificate')
                # project_id = kw.get('project_id')
                attachment = file.read()
                attachment_id = attachments.sudo().create({
                    'name': name,
                    'datas_fname': name,
                    'res_name': name,
                    'type': 'binary',
                    'res_model': 'op.admission',
                    'res_id': application.id,
                    'datas': base64.b64encode(attachment),
                })
                application.write({
                    'attachment': [(4, attachment_id.id)],
                    'birth_certificate' : base64.b64encode(attachment)
                })
            admission_register = http.request.env['op.admission.register'].sudo().search([('id','=',faculty1)],limit=1) 
           
            http.request.env['op.admission.application'].sudo().create({'admission_id':application.id,
                                                       'application_status':'draft',
                                                       'register_id':admission_register.id,
                                                       'course_id':admission_register.course_id.id,
                                                       'fees':admission_register.product_id.standard_price,
                                                       'fees_term_id':admission_register.product_id.id
                                                        })            
        except KeyError as e:
            #return request.render("openeducat_admission.apply",{'faculty':'Must Select Faculty'})
            return request.render('hue_admission.500',{'fail':'حدث خطأ ما فى تسجيل الطلب برجاء المحاولة مرة أخري , أو التحدث مع احد ممثلي الجامعة اسفل الصفحة'})
                
        try:
            faculty2 = params['faculty2']
            admission_register = http.request.env['op.admission.register'].sudo().search([('id','=',faculty2)],limit=1)
            http.request.env['op.admission.application'].sudo().create({'admission_id':application.id,
                                                       'application_status':'draft',
                                                       'register_id':admission_register.id,
                                                       'course_id':admission_register.course_id.id,
                                                       'fees':admission_register.product_id.standard_price,
                                                       'fees_term_id':admission_register.product_id.id
                                                        })               
        except KeyError as e:
            print ('I got a KeyError - reason')        

        try:
            faculty3 = params['faculty3']
            admission_register = http.request.env['op.admission.register'].sudo().search([('id','=',faculty3)],limit=1)
            http.request.env['op.admission.application'].sudo().create({'admission_id':application.id,
                                                       'application_status':'draft',
                                                       'register_id':admission_register.id,
                                                       'course_id':admission_register.course_id.id,
                                                       'fees':admission_register.product_id.standard_price,
                                                       'fees_term_id':admission_register.product_id.id
                                                        })               
        except KeyError as e:
            print ('I got a KeyError - reason')        

        try:
            faculty4 = params['faculty4']
            admission_register = http.request.env['op.admission.register'].sudo().search([('id','=',faculty4)],limit=1)
            http.request.env['op.admission.application'].sudo().create({'admission_id':application.id,
                                                       'application_status':'draft',
                                                       'register_id':admission_register.id,
                                                       'course_id':admission_register.course_id.id,
                                                       'fees':admission_register.product_id.standard_price,
                                                       'fees_term_id':admission_register.product_id.id
                                                        })               
        except KeyError as e:
            print ('I got a KeyError - reason')        
             
        try:
            faculty5 = params['faculty5']
            admission_register = http.request.env['op.admission.register'].sudo().search([('id','=',faculty5)],limit=1)
            http.request.env['op.admission.application'].sudo().create({'admission_id':application.id,
                                                       'application_status':'draft',
                                                       'register_id':admission_register.id,
                                                       'course_id':admission_register.course_id.id,
                                                       'fees':admission_register.product_id.standard_price,
                                                       'fees_term_id':admission_register.product_id.id
                                                        })                 
        except KeyError as e:
            print ('I got a KeyError - reason')        

        
        
        

 
        return request.redirect("/payment/%s"% (application.ref_number))
        #return request.render("openeducat_admission.payment",values)
    

