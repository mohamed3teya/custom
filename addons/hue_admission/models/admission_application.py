from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class CustomeAccountmove(models.Model):
    _inherit = 'account.move'
    
    def assign_outstanding_credit(self, credit_aml_id):
        print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXtttttttt')
        print(self.env.user.login)
        print(self.env.user.id)
        # msgbody = self.name
        self.env['mail.message'].sudo().create({
                    # 'subject': _('Invitation to follow %s: %s') % (model_name, document.name_get()[0][1]),
                    'body': "Payment has been Added by clicking Add",
                    # 'record_name': document.name_get()[0][1],
                    'email_from': self.env.user.login,
                    'author_id': self.env.user.partner_id.id,
                    # 'reply_to': email_from,
                    'model': "account.move",
                    'res_id': self.id,
                    'subtype_id': 2,
                })
        self.ensure_one()
        credit_aml = self.env['account.move.line'].browse(credit_aml_id)
        if not credit_aml.currency_id and self.currency_id != self.company_id.currency_id:
            credit_aml.with_context(allow_amount_currency=True, check_move_validity=False).write({
                'amount_currency': self.company_id.currency_id.with_context(date=credit_aml.date).compute(credit_aml.balance, self.currency_id),
                'currency_id': self.currency_id.id})
        if credit_aml.payment_id:
            credit_aml.payment_id.write({'invoice_ids': [(4, self.id, None)]})
        return self.env['account.payment.register'].with_context(active_model='account.move', active_ids=credit_aml).create({})._create_payments()
        # return self.register_payment(credit_aml)


class AdmissionApplication(models.Model):
    _name= 'op.admission.application'
    _description = 'op.admission.application'
    _rec_name = 'register_id'
    
    
    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, rec.register_id.name))
        return res
    
    
    admission_id = fields.Many2one('op.admission', string="Admission",ondelete='cascade')
    course_id = fields.Many2one('op.course', string="Course",required=True)
    fees_term_id = fields.Many2one('product.product', string="Fees Term")
    application_status = fields.Selection(
        [('draft', 'Draft'), ('paid', 'Paid'),
         ('refund', 'Refund'), ('enroll', 'Enrolled')],
        'Status',default='draft', required=True,readonly = True)
    register_id = fields.Many2one('op.admission.register', string="Application Register",required=True)
    invoice_id = fields.Many2one('account.move', string="Invoice", readonly=True)
    fees = fields.Float(compute="_compute_fees")
    application_date = fields.Datetime(string="Application Date", default=lambda self: fields.datetime.now(),readonly= True,required=True,copy=False)
    refund_id = fields.Many2one('account.move', string="credit note",readonly=True)
    
    @api.constrains('register_id')
    def validate_register_id(self):
        for rec in self:
            domain = [
                ('application_status', '!=', 'refund'),
                ('register_id', '=', rec.register_id.id),
                ('admission_id', '=', rec.admission_id.id),
                ('id', '!=', rec.id),
            ]
            data = self.search_count(domain)
            if data:
                raise ValidationError(('You have 2 Admission Register with same Course!'))
    
    
    @api.depends("register_id")
    def _compute_fees(self):
        for reg in self:
            reg.fees = reg.register_id.product_id.list_price or False
    
 
    @api.onchange('register_id')
    def onchange_register(self):
        self.course_id = False
        for rec in self:
            rec.course_id = rec.register_id.course_id
            rec.fees = rec.register_id.product_id.list_price
            rec.fees_term_id = rec.register_id.product_id.id
            
    def unlink(self):
       for record in self:
           if record.application_status != 'draft':
               raise ValidationError(_("You can delete draft application only !!!!!"))
       return super(OpAdmissionApplication, self).unlink()
 
            
    def change_application(self):
        inv_obj = self.env['account.move']
        partner_id  = self.admission_id.partner_id
        invoice_lines = []
        if self.application_status == 'paid':
            account_id = False
            payment = self.invoice_id.payment_move_line_ids
            self.invoice_id.payment_move_line_ids.remove_move_reconcile()
            save_invoice_number =  self.invoice_id.number
            save_payment_id = self.env['account.payment'].search([('notes', '=', save_invoice_number)], limit=1).id
            save_payment_name = self.env['account.payment'].search([('notes', '=', save_invoice_number)], limit=1).name
            self.invoice_id.button_cancel_posted_moves()
            self.invoice_id.update({'state': 'draft'})
            print("1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxmmmmmmmmmmmmmmmmmmmmm")
            # self.invoice_id.invoice_line_ids.unlink()
            print("2-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxmmmmmmmmmmmmmmmmmmmmm")
            product = self.register_id.product_id
            if product.id:
                account_id = product.categ_id.property_account_income_categ_id.id
            if not account_id:
                account_id = product.property_account_income_id.id
            if not account_id:
                raise UserError(
                    _('There is no income account defined for this product: "%s". \
                       You may have to install a chart of account from Accounting \
                       app, settings menu.') % (product.name,))
            invoice_line_data = self.env['account.move.line'].sudo().update({
                            'name':product.name,
                            'account_id':account_id,
                            'price_unit':self.fees,
                            'quantity':1,
                            'move_id':self.invoice_id.id,
                            'product_id':product.id
                            })            #product.list_price
            self.invoice_id.action_post()
            # self.invoice_id.assign_outstanding_credit(payment.id)
            
            admission = self.env['op.hue.admission'].sudo().search([('active_admission', '=', True)], limit=1)
            code = self.env['op.admission'].sudo().search(
                [('application_number_sequence', '!=', 0), ('horus_admission_id', '=', admission.id)],
                order='application_number_sequence desc', limit=1).application_number_sequence
            if code:
                new_code = (code) + 1
            else:
                new_code = '1001'
            
            app_idetifier = ""
            app_idetifier = self.register_id.identifier
            print('PSPSPSPSPS')
            print(app_idetifier)
            print(new_code)
            self.admission_id.application_number = str(app_idetifier) + str(new_code)
            self.admission_id.application_number_sequence = new_code
            
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'تم تغيير الرغبة بنجاح إلى ' + ( str(product.name) ),
                'img_url': '/force_delete_multi_invoice/static/description/deleted.png',
                'type': 'rainbow_man',
            }
        }
    
    #Check this
    def cancel_enroll_student(self):
        # if self.env.user.id == 1 or self.env.user.id == 13:
        student_id = self.admission_id.student_id
        
        #registraion
        regs = self.env['hue.student.registration'].sudo().search([('student_id', '=', student_id.id)])
        if regs:
            regs.unlink()
        regs_log = self.env['hue.student.registration.log'].sudo().search([('student_id', '=', student_id.id)])
        if regs_log:
            regs_log.unlink()
        att_lines = self.env['op.attendance.line'].sudo().search([('student_id', '=', student_id.id)])
        if att_lines:
            att_lines.unlink()
        acc_semesters = self.env['op.student.accumlative.semesters'].sudo().search([('student_id', '=', student_id.id)])
        if acc_semesters:
            acc_semesters.unlink()
        advisor = self.env['hue.academic.direction.line'].sudo().search([('student_id', '=', student_id.id)])
        if advisor:
            advisor.unlink()
        
        student_id.unlink()
        self.admission_id.student_id = False
        self.admission_id.state = 'confirm'
        self.application_status = 'paid'
        
    
    def print_enroll_application(self):
        self.ensure_one()
        data = {'admission_id': self.admission_id}
        return self.env.ref('hue_admission.enroll_application_report_view').report_action(None, data=data)
    
    def print_application(self):
        self.ensure_one()
        data = {'payment_ids', self.invoice_id.payment_ids.id}
        return self.env.ref('hue_admission.admission_report_payment_receipt').report_action(None, data=data)
    
    
    def print_refund(self):
        return self.env.ref('openeducat_admission.admission_report_payment_receipt').report_action(self.refund_id.payment_ids.id)
        
    
    def enroll_student(self):
        hue_joining_years = self.env['hue.joining.years']
        hue_academic_years = self.env['op.academic.year']
        financial_years = self.env['hue.years']
        hue_installments = self.env['hue.installments']
        product = self.env['product.product']
        invoice = self.env['account.move']
        invoice_line = self.env['account.move.line']
        student_status = self.env['hue.student.status']
        academic_years = self.env['op.academic.year']
        terms = self.env['op.academic.term']
        increase_years = self.env['hue.years.increase']
        student =  self.env['op.student']
        hr_faculties = self.env['hue.faculties']
        Studentname = self.admission_id.name
        TransportationState = self.admission_id.transportation_state
        HousingState = self.admission_id.housing_state
        Certificate_id = self.admission_id.certificate_id.id
        StudentStatus_id = self.admission_id.std_status_id.id
        City_id = self.admission_id.city_id.id
        JoiningYear_id = self.admission_id.join_year_id.id
        NationalityID = self.admission_id.nationality_id.id
        nationality_data = self.admission_id.nationality_id
        partner_id = self.admission_id.partner_id
        mc = self.admission_id.mc
        scholarship = self.admission_id.scholarship
        special_case = self.admission_id.special_case
        staff_dis = self.admission_id.staff_dis
        sibling_dis = self.admission_id.sibling_dis
        martyrs_dis = self.admission_id.martyrs_dis
        syndicate_dis = self.admission_id.syndicate_dis
        cgpa = 0
        CertificatePercentage = self.admission_id.certificate_percentage
        semster_id = self.admission_id.semster_id.id
        school_name	 = self.admission_id.school_name
        faculty_id_data = self.register_id.course_id.faculty_id.id
        course_id = self.register_id.course_id.id
        year = hue_academic_years.sudo().search([('join_year','=',JoiningYear_id)],limit=1).year
        facult_identifier = self.register_id.course_id.faculty_id.identifier
        code_year = str(year)[-2:]
        # semester_code = 1
        semester_code =self.env['op.semesters'].sudo().search([('enroll_semester', '!=', False)]).id
        print("semester_code: ", semester_code)
        year = int(year)
        # new added
        gender = self.admission_id.gender
        birthdate = self.admission_id.birth_date
        religion = self.admission_id.religion
        englishname = self.admission_id.english_name
        address = self.admission_id.address
        mobile = self.admission_id.mobile_number
        certcountry = self.admission_id.certificate_country
        certpercentage = self.admission_id.certificate_percentage
        certdegree = self.admission_id.certificate_degree
        certdegree = self.admission_id.certificate_degree
        school_name = self.admission_id.school_name
        government = self.admission_id.city_id
        city = self.admission_id.city
        fathername = self.admission_id.father_name
        fatherjob = self.admission_id.father_job
        fathermobile = self.admission_id.father_mobile
        fathernationality = self.admission_id.father_nationality.id
        fathermail = self.admission_id.father_mail
        mothername = self.admission_id.mother_name
        motherjob = self.admission_id.mother_job
        mothermobile = self.admission_id.mother_mobile
        mothernationality = self.admission_id.mother_nationality.id
        mothermail = self.admission_id.mother_mail
        religion = self.admission_id.religion
        # if self.register_id.course_id.faculty_id.id == 9:
        #     level = 6
        # else:
        #     level = 7
        level=1    
        print('5555555555555555555555555555555555555555')
        print(faculty_id_data)
        print(JoiningYear_id)
        if special_case:
            print('aaaaaaaaaaaaaaaaaaaaaaaaaaa')
            student_last_code = student.sudo().search([('special_case','=',True),('join_term','=',semester_code),('faculty','=',faculty_id_data),('join_year','=',JoiningYear_id)],order='student_code DESC',limit=1).student_code
        else:
            print('bbbbbbbbbbbbbbbbbbbbbbbb')
            student_last_code = student.sudo().search([('special_case','=',False),('join_term','=',semester_code),('faculty','=',faculty_id_data),('join_year','=',JoiningYear_id)],order='student_code DESC',limit=1).student_code
        print('2222222222222222222222222888888888888')
        print(student_last_code)
        if student_last_code == 0 or student_last_code == False:
            last_code = "001"
        else:
            student_last_code = student_last_code+1
            last_code = str(student_last_code)[-3:]
        if special_case:
            Studentcode = int(str(facult_identifier)+code_year+str(semester_code+2)+str(last_code))
        else:
            print("facult_identifier: ",facult_identifier)
            print("code_year: ", code_year)
            print("semester_code: ", semester_code)
            print("semester_code: ", last_code)
            Studentcode = int(str(facult_identifier)+code_year+str(semester_code)+str(last_code))
            
        std = student.sudo().search([('student_code','=',Studentcode)],limit=1)
        email = str(Studentcode)+"@horus.edu.eg"

        self.admission_id.email  =email
        self.admission_id.student_code =Studentcode
        
        self.admission_id.state ='done'
        self.application_status ='enroll'
        if (CertificatePercentage != 0):
            if not std:
                student_data = student.sudo().create({'mc': int(mc), 'partner_id': partner_id.id, 'name': Studentname
                                                         , 'course_id': self.register_id.course_id.id,
                                                        'student_nationality': NationalityID
                                                         , 'percentage': CertificatePercentage, 'email': email,
                                                        'student_status': StudentStatus_id
                                                         , 'student_certificates': Certificate_id,
                                                        'student_birth_place': City_id
                                                         , 'student_code': Studentcode, 'faculty': faculty_id_data
                                                         , 'year': str(year), 'cgpa': cgpa, 'join_year': JoiningYear_id
                                                         , 'national_id': self.admission_id.national_id
                                                         , 'gender': self.admission_id.gender
                                                         , 'en_name': self.admission_id.english_name
                                                         , 'd_name': self.admission_id.d_name
                                                         , 'birth_date': self.admission_id.birth_date
                                                         , 'religion': religion
                                                         , 'visa_info': self.admission_id.address
                                                         , 'stumobile': self.admission_id.mobile_number
                                                         , 'student_nationality': self.admission_id.nationality_id.id
                                                         , 'level': level
                                                         , 'certificate_degree': self.admission_id.certificate_degree
                                                         , 'certificate_country': self.admission_id.certificate_country.id
                                                         , 'certificate_date': self.admission_id.certificate_date
                                                         , 'father_name': fathername
                                                         , 'father_mobile': fathermobile
                                                         , 'father_nationality' : fathernationality
                                                         , 'father_job' : fatherjob
                                                         , 'father_mail' : fathermail
                                                         , 'mother_name': mothername
                                                         , 'mother_mobile': mothermobile
                                                         , 'mother_nationality' : mothernationality
                                                         , 'mother_job' : motherjob
                                                         , 'mother_mail' : mothermail
                                                         , 'join_term' : semester_code
                                                         , 'image' : False
                                                         , 'scholarship' : scholarship
                                                         , 'special_case' : special_case
                                                         , 'father_discount' : staff_dis
                                                         , 'brother_discount' : sibling_dis
                                                         , 'martyrs_discount' : martyrs_dis
                                                         , 'syndicate_discount' : syndicate_dis
                                                         , 'sibling_student_id' : self.admission_id.sibling_student_id.id
                                                         , 'seatno': self.admission_id.seat_no
                                                         })
                student_sibling = self.env['op.student'].sudo().search([('id', '=', self.admission_id.sibling_student_id.id)])
                student_sibling.write({'sibling_student_id': student_data.id})
                self.admission_id.student_id =student_data.id
                # partner_id.sudo().write({'already_partner': 1, 'mc': int(mc), 'student_nationality': NationalityID,
                #                          'percentage': CertificatePercentage, 'student_status': StudentStatus_id,
                #                          'student_certificates': Certificate_id, 'student_birth_place': City_id,
                #                          'student_code': Studentcode, 'faculty': faculty_id_data, 'year': (year),
                #                          'cgpa': cgpa, 'join_year': JoiningYear_id})
                student_data.sudo().write({'already_partner': 1, 'mc': int(mc), 'student_nationality': NationalityID,
                                         'percentage': CertificatePercentage, 'student_status': StudentStatus_id,
                                         'student_certificates': Certificate_id, 'student_birth_place': City_id,
                                         'student_code': Studentcode, 'faculty': faculty_id_data, 'year': str(year),
                                         'cgpa': cgpa, 'join_year': JoiningYear_id})
                financial_year = financial_years.sudo().search([('join_year', '=', JoiningYear_id), ('faculty', '=', faculty_id_data), ('course_id', '=', self.register_id.course_id.id)],limit=1)
                print('000000000000000000000000000')
                print(JoiningYear_id)
                academic_year  = academic_years.sudo().search([('join_year', '=', JoiningYear_id)],limit=1)
                print(academic_year)
                if financial_year:
                    print("TTTTTTTTTTTTTTTTTT")
                    print(nationality_data.foreign_nationality)
                    if nationality_data.foreign_nationality :
                        print('A111111111111111111111111111111111111111')
                        installments = hue_installments.sudo().search([('years_id', '=', financial_year.id),('one_time', '=', False),('foreign_nationality','=',True),('special_case','=',False)])
                        increases = increase_years.sudo().search([('year_id', '=', financial_year.id),('foreign_nationality','=',True),('special_case','=',False)])
                    elif special_case:
                        print('B111111111111111111111111111111111111111')
                        installments = hue_installments.sudo().search([('years_id', '=', financial_year.id),('special_case','=',True),('one_time', '=', False),('foreign_nationality','=',False)])
                        increases = increase_years.sudo().search([('year_id', '=', financial_year.id),('special_case','=',True)])
                    else:
                        print('C111111111111111111111111111111111111111')
                        installments = hue_installments.sudo().search([('years_id', '=', financial_year.id),('one_time', '=', False),('special_case', '=', False),('foreign_nationality','=',False)])
                        increases = increase_years.sudo().search([('year_id', '=', financial_year.id),('foreign_nationality','=',False),('special_case','=',False)])

                    for installment in installments:
                        global_term_id = installment.term_id.id
                        term_data = terms.sudo().search([('term_id','=',academic_year.id), ('global_term_id','=', global_term_id)],limit=1)
                        from_date = term_data.from_date
                        to_date = term_data.from_date
                        name = term_data.name
                        print(name)
                        currency = installment.currency
                        invoice_data = invoice.sudo().create({
                            'academic_term':term_data.id,
                            'notes':financial_year.notes,
                            'invoice_type':'regular',
                            'currency_id' : currency.id,
                            'account_id': partner_id.property_account_receivable_id.id,
                            'move_type': 'out_invoice',
                            'ref': False,
                            'faculty':faculty_id_data,
                            'student_code':Studentcode,
                            'academic_year':academic_year.id,
                            'invoice_date_due':to_date,
                            'date_invoice':from_date,
                            'partner_id':partner_id.id,
                            'state': 'draft',
                            'dis_inv': installment.extra_inv
                            })
                        print(invoice_data)
                        inv_product = product.sudo().search([('installments_id', '=', installment.id)])
                        account_id = False
                        if inv_product.id:
                            account_id = inv_product.property_account_income_id.id
                        if not account_id:
                            account_id = inv_product.categ_id.property_account_income_categ_id.id
                        if not account_id:
                            raise UserError(
                                _('There is no income account defined for this5555 product: "%s". \
                                   You may have to install a chart of account from Accounting \
                                   app, settings menu.') % (product.name,))
                        invoice_line_data = invoice_line.sudo().create({
                            'name':inv_product.name,
                            'account_id':account_id,
                            'price_unit':inv_product.list_price,
                            'quantity':1,
                            'move_id':invoice_data.id,
                            'product_id':inv_product.id
                            })
                        
                        invoice_data.action_post()
                        
                        account_id = False
                        if increases:
                            for increase in increases:
                                if increase.id:
                                    account_id = increase.property_account_income_id.id
                                if not account_id:
                                    account_id = increase.categ_id.property_account_income_categ_id.id
                                if not account_id:
                                    raise UserError(
                                        _('There is no income account defined for this7777 product: "%s". \
                                           You may have to install a chart of account from Accounting \
                                           app, settings menu.') % (product.name,))
                                if increase.increase_type == 'percentage':
                                    standard_price = increase.list_price
                                elif increase.increase_type == 'amount':
                                    standard_price =( increase.amount /2 )
                                invoice_line_data = invoice_line.sudo().create({
                                    'name':increase.name,
                                    'account_id':account_id,
                                    'price_unit':standard_price,
                                    'quantity':1,
                                    'move_id':invoice_data.id,
                                    'product_id':increase.product_id.id
                                    })


                        discounts = self.env['hue.discounts'].sudo().search([('percentage_from', '<=', CertificatePercentage),
                        ('percentage_to', '>=',CertificatePercentage),('nationality_id', '=',NationalityID),
                        ('certificate_id', '=',Certificate_id),
                        ('join_year_id', '=',JoiningYear_id), ('faculty_ids', '=',faculty_id_data)])

                if academic_year.join_year.id == JoiningYear_id:
                    if nationality_data.foreign_nationality == False:
                        installments = hue_installments.sudo().search([('years_id', '=', financial_year.id),('one_time', '=', True)])
    
                        for installment in installments:
                            global_term_id = installment.term_id.id
                            term_data = terms.sudo().search([('term_id','=',academic_year.id), ('global_term_id','=', global_term_id)],limit=1)
                            from_date = term_data.from_date
                            to_date = term_data.from_date
                            name = term_data.name
                            print(name)
                            currency = installment.currency
                            invoice_data = invoice.sudo().create({
                                'academic_term':term_data.id,
                                'invoice_type':'one',
                                'faculty':faculty_id_data,
                                'currency_id' : currency.id,
                                'account_id': partner_id.property_account_receivable_id.id,
                                'move_type': 'out_invoice',
                                'ref': False,
                                'student_code':Studentcode,
                                'academic_year':academic_year.id,
                                'invoice_date_due':to_date,
                                'date_invoice':from_date,
                                'partner_id':partner_id.id,
                                'state': 'draft'
                                })
                            inv_product = product.sudo().search([('installments_id', '=', installment.id)])
                            account_id = False
                            if inv_product.id:
                                account_id = inv_product.property_account_income_id.id
                            if not account_id:
                                account_id = inv_product.categ_id.property_account_income_categ_id.id
                            if not account_id:
                                raise UserError(
                                    _('There is no income account defined for this99999 product: "%s". \
                                       You may have to install a chart of account from Accounting \
                                       app, settings menu.') % (product.name,))
                            invoice_line_data = invoice_line.sudo().create({
                                'name':inv_product.name,
                                'account_id':account_id,
                                'price_unit':inv_product.list_price,
                                'quantity':1,
                                'move_id':invoice_data.id,
                                'product_id':inv_product.id})
    
                            invoice_data.action_post()
                
                discounts_data = []
                print('DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD')
                print(JoiningYear_id)
                print(scholarship)
                if scholarship:
                    print('11111111111111111111')
                    discounts = self.env['hue.discounts'].sudo().search(
                    [('percentage_from', '<=', CertificatePercentage),
                     ('percentage_to', '>=', CertificatePercentage), ('nationality_id', '=', NationalityID),
                     ('certificate_id', '=', Certificate_id),
                     ('join_year_id', '=', JoiningYear_id), ('course_id', '=', self.register_id.course_id.id),
                     ('faculty_ids', '=', faculty_id_data),('scholarship','=',scholarship)])
                    print(discounts)
                    print('11111111111111111111')
                else:
                    print('22222222222222222222')
                    # staff_dis = self.admission_id.staff_dis
                    # sibling_dis = self.admission_id.sibling_dis
                    # martyrs_dis = self.admission_id.martyrs_dis
                    # syndicate_dis = self.admission_id.syndicate_dis
                    print(staff_dis)
                    print('mccccccccccccccccccccccccccccccc')
                    if mc:
                        print('1-----------------')
                        discounts = self.env['hue.discounts'].sudo().search(
                            [('mc', '=', 1), ('percentage_from', '<=', CertificatePercentage),
                             ('percentage_to', '>=', CertificatePercentage), ('nationality_id', '=', NationalityID),
                             ('certificate_id', '=', Certificate_id),
                             ('join_year_id', '=', JoiningYear_id), ('course_id', '=', self.register_id.course_id.id),
                             ('faculty_ids', '=', faculty_id_data),('scholarship','=',False)])
                    elif staff_dis:
                        print('2-----------------')
                        discounts = self.env['hue.discounts'].sudo().search(
                            [('staff_discount', '=', True), ('percentage_from', '<=', CertificatePercentage),
                             ('percentage_to', '>=', CertificatePercentage), ('nationality_id', '=', NationalityID),
                             ('certificate_id', '=', Certificate_id),
                             ('join_year_id', '=', JoiningYear_id), ('course_id', '=', self.register_id.course_id.id),
                             ('faculty_ids', '=', faculty_id_data),('scholarship','=',False)])
                    elif sibling_dis:
                        print('3-----------------')
                        discounts = self.env['hue.discounts'].sudo().search(
                            [('sibling_discount', '=', True), ('percentage_from', '<=', CertificatePercentage),
                             ('percentage_to', '>=', CertificatePercentage), ('nationality_id', '=', NationalityID),
                             ('certificate_id', '=', Certificate_id),
                             ('join_year_id', '=', JoiningYear_id), ('course_id', '=', self.register_id.course_id.id),
                             ('faculty_ids', '=', faculty_id_data),('scholarship','=',False)])
                    elif martyrs_dis:
                        print('4-----------------')
                        discounts = self.env['hue.discounts'].sudo().search(
                            [('martyrs_discount', '=', True), ('percentage_from', '<=', CertificatePercentage),
                             ('percentage_to', '>=', CertificatePercentage), ('nationality_id', '=', NationalityID),
                             ('certificate_id', '=', Certificate_id),
                             ('join_year_id', '=', JoiningYear_id), ('course_id', '=', self.register_id.course_id.id),
                             ('faculty_ids', '=', faculty_id_data),('scholarship','=',False)])
                    elif syndicate_dis:
                        print('5-----------------')
                        discounts = self.env['hue.discounts'].sudo().search(
                            [('syndicate_discount', '=', True), ('percentage_from', '<=', CertificatePercentage),
                             ('percentage_to', '>=', CertificatePercentage), ('nationality_id', '=', NationalityID),
                             ('certificate_id', '=', Certificate_id),
                             ('join_year_id', '=', JoiningYear_id), ('course_id', '=', self.register_id.course_id.id),
                             ('faculty_ids', '=', faculty_id_data),('scholarship','=',False)])
                    else:
                        print('6-----------------')
                        discounts = self.env['hue.discounts'].sudo().search(
                            [('syndicate_discount', '=', False),('martyrs_discount', '=', False),('sibling_discount', '=', False),('staff_discount', '=', False),('mc', '=', 0),
                             ('percentage_from', '<=', CertificatePercentage),
                             ('percentage_to', '>=', CertificatePercentage), ('nationality_id', '=', NationalityID),
                             ('certificate_id', '=', Certificate_id),
                             ('join_year_id', '=', JoiningYear_id), ('course_id', '=', self.register_id.course_id.id),
                             ('faculty_ids', '=', faculty_id_data),('scholarship','=',False)])
                    print(discounts)
                    print('22222222222222222222')
                # if not discounts:
                #     print('d22222222222')
                #     print(scholarship)
                #     if scholarship:
                #         discounts = self.env['hue.discounts'].sudo().search(
                #             [('mc', '=', 0), ('percentage_from', '<=', CertificatePercentage),
                #              ('percentage_to', '>=', CertificatePercentage), ('nationality_id', '=', NationalityID),
                #              ('certificate_id', '=', Certificate_id),
                #              ('join_year_id', '=', JoiningYear_id),
                #              ('faculty_ids', '=', faculty_id_data), ('course_id', '=', False),('scholarship','=',scholarship)])
                #     else:
                #         discounts = self.env['hue.discounts'].sudo().search(
                #             [('mc', '=', 0), ('percentage_from', '<=', CertificatePercentage),
                #              ('percentage_to', '>=', CertificatePercentage), ('nationality_id', '=', NationalityID),
                #              ('certificate_id', '=', Certificate_id),
                #              ('join_year_id', '=', JoiningYear_id),
                #              ('faculty_ids', '=', faculty_id_data), ('course_id', '=', False)])
                for dis in discounts:
                    discounts_data.append(dis)
                    print("discountsssssssssssssssssssssssssssssssssssssssssssss11")
                    print(discounts)
                # raise UserError(
                #     _('There is no income account defined for this product: \
                #        You may have to install a chart of account from Accounting \
                #        app, settings menu.'))
                for discount in discounts_data:
                    print('SSSSSSSSSSSSSS0000000000000000SSSSSSSS')
                    print(discount.id)
                    product_data = product.sudo().search([('discount_id', '=', discount.id)])
                    print(product_data)
                    acadmic_year_data = self.env['hue.academic.years'].search([('join_year', '=', JoiningYear_id)]).id
                    invoices_data_count = len(invoice.sudo().search(
                        [('state', '=', 'open'), ('partner_id', '=', partner_id.id), ('invoice_type', '=', 'regular'),
                         ('academic_year', '=', acadmic_year_data) , ('dis_inv', '=', True) ],limit = 2)._ids)
                    invoices_data = invoice.sudo().search(
                        [('state', '=', 'open'), ('partner_id', '=', partner_id.id), ('invoice_type', '=', 'regular'),
                         ('academic_year', '=', acadmic_year_data), ('dis_inv', '=', True)],limit = 2)
                    account_id = False
                    if product_data.id:
                        account_id = product_data.property_account_income_id.id
                    if not account_id:
                        account_id = product_data.categ_id.property_account_income_categ_id.id
                    if not account_id:
                        raise UserError(
                            _('There is no income account defined for this product: "%s". \
                               You may have to install a chart of account from Accounting \
                               app, settings menu.') % (product.name,))
                    if invoices_data:
                        print(invoices_data)
                        for invoice_data in invoices_data:
                            print(product_data.list_price)
                            print(invoices_data_count)
                            price_unit = product_data.list_price / invoices_data_count
                            # invoice_line_data = invoice_line.sudo().create({
                            #     'name': product_data.name,
                            #     'account_id': account_id,
                            #     'price_unit': price_unit,
                            #     'quantity': 1,
                            #     'invoice_id': invoice_data.id,
                            #     'product_id': product_data.id
                            # })
                            
                            credit_note_data = invoice.sudo().create({
                                'academic_term':invoice_data.academic_term.id,
                                'origin':invoice_data.number,
                                'notes':financial_year.notes,
                                'invoice_type':'regular',
                                'currency_id' : currency.id,
                                'move_type': 'out_refund',
                                'account_id': partner_id.property_account_receivable_id.id,
                                'ref': False,
                                'faculty':faculty_id_data,
                                'student_code':self.admission_id.Student_code,
                                'academic_year':invoice_data.academic_year.id,
                                'invoice_date_due':invoice_data.academic_term.from_date,
                                'date_invoice':invoice_data.academic_term.from_date,
                                'partner_id':partner_id.id,
                                'state': 'draft'
                            })
                            
                            if invoices_data:
                                price_unit = product_data.list_price / invoices_data_count
                                invoice_line_data = invoice_line.sudo().create({
                                    'name': product_data.name,
                                    'account_id': account_id,
                                    'price_unit': price_unit,
                                    'quantity': 1,
                                    'move_id': credit_note_data.id,
                                    'product_id': product_data.id
                                })
                                    
                            credit_note_data.action_post()
                            
                            credit_notes = self.env['account.move'].search([('origin', '=', invoice_data.number)])
                            credit_note_ids = []
                            for cr in credit_notes:
                                credit_note_ids.append(cr.id)
                            
                            domain = [('move_id', 'in', credit_note_ids),('account_id', '=', invoice_data.account_id.id), ('partner_id', '=', invoice_data.env['res.partner']._find_accounting_partner(invoice_data.partner_id).id), ('reconciled', '=', False), '|', ('amount_residual', '!=', 0.0), ('amount_residual_currency', '!=', 0.0)]
                            if invoice_data.move_type in ('out_invoice', 'in_refund'):
                                domain.extend([('credit', '>', 0), ('debit', '=', 0)])
                                type_payment = _('Outstanding credits')
                            else:
                                domain.extend([('credit', '=', 0), ('debit', '>', 0)])
                                type_payment = _('Outstanding debits')
                            info = {'title': '', 'outstanding': True, 'content': [], 'move_id': invoice_data.id}
                            lines = invoice_data.env['account.move.line'].search(domain)
                            currency_id = invoice_data.currency_id
                            
                            if len(lines) != 0:
                                for line in lines:
                                    self.assign_outstanding_credit(line.id,invoice_data)
                                    
    
    def delete_application(self):
        inv_obj = self.env['account.move']
        partner_id  = self.admission_id.partner_id
        invoice_lines = []
        if self.application_status == 'paid':
            account_id = False
            product = self.register_id.product_id
            if product.id:
                account_id = product.categ_id.property_account_income_categ_id.id
            if not account_id:
                account_id = product.property_account_income_id.id
            if not account_id:
                raise UserError(
                    _('There is no income account defined for this product: "%s". \
                       You may have to install a chart of account from Accounting \
                       app, settings menu.') % (product.name,))
            invoice_lines.append((0, 0,{'name':self.fees_term_id.name,'account_id':account_id,'price_unit':self.fees,'quantity':1,'product_id':self.fees_term_id.id})) #self.fees_term_id.list_price
            invoice = inv_obj.create({
                    #'name': self.name,
                    'origin': self.invoice_id.origin,
                    'invoice_type':'application',
                    'is_application':1,
                    'move_type': 'out_refund',
                    'ref': False,
                    'account_id': partner_id.property_account_receivable_id.id,
                    'partner_id': partner_id.id,
                    'invoice_line_ids':  invoice_lines,
                })
            invoice.action_post()
            payment = self.env['account.payment']
            
            payment_method_line = self.journal_id.inbound_payment_method_line_ids\
             .filtered(lambda l: l.company_id == self.company_id)
            payment._check_payment_method_line_id()
            if len(payment_method_line) == 0:
                raise ValidationError(_("Journal should have at least one payment method"))
            print("payment_method_line", payment_method_line[0])
            
            if self.admission_id.journal_id:
                journal_id = self.admission_id.journal_id.id
            else:
                journal_id = 6
            vals = {
                'payment_method_line_id': payment_method_line[0].id,
                'journal_id': journal_id,
                'payment_method_id': 1,
                # 'payment_date': self.admission_date,
                'communication': '',
                'invoice_ids': [(6, 0, invoice.ids)],
                'payment_type': 'outbound',
                'amount': abs(invoice.amount_total),
                'currency_id': 77,
                'partner_id': invoice.commercial_partner_id.id,
                'partner_type': 'customer',
                }

            payments = payment.create(vals)
            payments.action_post()
            self.refund_id = invoice.id
            self.application_status = 'refund'
            self.admission_id.application_number = self.admission_id.application_number.replace(self.register_id.identifier, '')
            return self.env.ref('openeducat_admission.admission_report_payment_receipt').report_action(payments.id)
        return True
    
    def clean_internal_number(self):
        for rec in self:           
            if 'document_sequence_id' in rec._fields and \
                    rec.document_sequence_id:
                rec.write({
                    'move_name': False,
                    'document_number': False})
            else:
                rec.write({'move_name': False})
                
    
    def register_payment(self, payment_line ,inv_id = False, writeoff_acc_id=False, writeoff_journal_id=False ):
        """ Reconcile payable/receivable lines from the invoice with payment_line """
        line_to_reconcile = inv_id.env['account.move.line']
        for inv in inv_id:
            line_to_reconcile += inv.move_id.line_ids.filtered(lambda r: not r.reconciled and r.account_id.internal_type in ('payable', 'receivable'))
        return (line_to_reconcile + payment_line).reconcile(writeoff_acc_id, writeoff_journal_id)

    def assign_outstanding_credit(self, credit_aml_id , inv_id):
        inv_id.ensure_one()
        credit_aml = self.env['account.move.line'].browse(credit_aml_id)
        if not credit_aml.currency_id and inv_id.currency_id != inv_id.company_id.currency_id:
            credit_aml.with_context(allow_amount_currency=True, check_move_validity=False).write({
                'amount_currency': inv_id.company_id.currency_id.with_context(date=credit_aml.date).compute(credit_aml.balance, inv_id.currency_id),
                'currency_id': inv_id.currency_id.id})
        if credit_aml.payment_id:
            credit_aml.payment_id.write({'invoice_line_ids': [(4, inv_id.id, None)]})
        return self.register_payment(credit_aml,inv_id)

    