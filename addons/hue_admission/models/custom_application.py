from odoo import fields, models, api, _
from datetime import datetime
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta
import uuid
import re

class Custom_Application(models.Model):
    _inherit = 'op.admission'
    _rec_name = 'name'
    _order = "application_number_sequence desc"
    
    
    def _default_hue_admission(self):
        return self.env['op.hue.admission'].sudo().search([('active_admission', '=', True)], limit=1).id
    
    
    state = fields.Selection(selection_add=[('online_draft','Online Draft'), ('draft',)],default='draft',tracking=True)
    register_id = fields.Many2one('op.admission.register', required=False)
    first_name = fields.Char(required=False)
    last_name = fields.Char(required=False)
    amount_total = fields.Float(string='Total Amount', compute="_compute_amount_total")
    national_id = fields.Char(string="National ID",size=14, required=True , tracking=True)
    admission_application_ids = fields.One2many('op.admission.application','admission_id', string=" Admission Applications")
    horus_admission_id = fields.Many2one('op.hue.admission', string="Hue Admission",default=_default_hue_admission)
    application_number_sequence = fields.Integer(string="Application Number Seq",copy=False)
    mobile_number = fields.Char(string="Mobile Number",size=11)
    parent_mobile = fields.Char(string="Other Mobile Number",size=11)
    faculty = fields.Many2one('hue.faculties',related='partner_id.faculty',store=True)
    enroll_date = fields.Datetime(string="Enroll Date",compute='compute_enroll_date',store=True)
    arabic_name = fields.Char(string="Arabic Name")
    english_name = fields.Char(string="English Name")
    d_name = fields.Char(string="ID Name")
    birth_date_certificate = fields.Date(string="Date of Birth Certificate")
    ref_number = fields.Char(string="ref",size=14)
    student_code = fields.Char(string='Student Code', readonly=True if state=='done' else False)
    join_year_id = fields.Many2one('hue.joining.years', string="Join Year",readonly=True , related ='horus_admission_id.join_year_id')
    semster_id = fields.Many2one('op.semesters', string="semester",readonly=True, related ='horus_admission_id.semster_id')
    std_status_id = fields.Many2one('hue.std.data.status', string="student Status",readonly=True, related ='horus_admission_id.std_status_id')
    certificate_id = fields.Many2one('hue.certificates', string="Certificate")
    city_id = fields.Many2one('hue.cities', string="Egypt Governorate")
    mc = fields.Boolean(string="Mansoura College Student", readonly=True if state=='done' else False)
    staff_dis = fields.Boolean(string="Staff discount", readonly=True if state=='done' else False)
    sibling_dis = fields.Boolean(string="Sibling discount", readonly=True if state=='done' else False)
    syndicate_dis = fields.Boolean(string="Syndicate discount", readonly=True if state=='done' else False)
    martyrs_dis = fields.Boolean(string="Matrys discount", readonly=True if state=='done' else False)
    nationality_id = fields.Many2one('hue.nationalities', string="Nationality")
    school_name = fields.Char('School Name')
    certificate_date = fields.Selection([(str(num), str(num)) for num in range(1990, (datetime.now().year)+1 )], string='Certificate Date')
    certificate_country = fields.Many2one('hue.nationalities', string='Certificate Country')
    transportation_state = fields.Char(string="Transportation State")
    certificate_percentage = fields.Float(string='Certificate Percentage',default="")
    housing_state = fields.Char(string='Housing State')
    seat_no = fields.Char(string='Seat no',size=10)
    certificate_degree = fields.Float(string="Certificate Degree")
    required_field = fields.Boolean(string='Required Field',compute='_compute_required_field')
    scholarship = fields.Selection([(str(num), ('Partial '+ str(num)+ ' %') if num<100 else 'Full') for num in range(5,102,5)], tracking=True)
    special_case = fields.Boolean(string='Special Case',tracking=True, readonly=True if state=='done' else False)
    religion = fields.Selection([('m','Muslim - مسلم'),('c','Christian - مسيحي')],default='m', readonly=True if state=='done' else False)
    father_name = fields.Char(string='Father Name')
    father_job = fields.Char(string='Father Job')
    father_mobile = fields.Char(string='Father Mobile', size=11)
    father_mail = fields.Char(string='Father Mail')
    father_phone = fields.Char(string='Father Phone')
    father_nationality = fields.Many2one('hue.nationalities', string='Father Nationality')
    mother_name = fields.Char(string='Mother Name')
    mother_job = fields.Char(string='Mother Job')
    mother_mobile = fields.Char(string='Mother Mobile', size=11)
    mother_phone = fields.Char(string='Mother Phone')
    mother_mail = fields.Char(string='Mother Mail')
    mother_nationality = fields.Many2one('hue.nationalities', string="Mother Nationality")
    sibling_name = fields.Char(string='Sibling Name')
    sibling_id = fields.Char(string='Sibling')
    sibling_student_id = fields.Many2one('op.student', string="Sibling Student")
    governorate = fields.Char()
    address = fields.Text()
    home_number = fields.Char(string='Home Number')
    birth_certificate = fields.Binary(string="Birth Certificate")
    journal_id = fields.Many2one('account.journal', string='Transfer To',domain=[('type', 'in', ('bank', 'cash'))])
    name = fields.Char(string="Name",required=True,size=328, tracking=True, readonly= True if state=='done' else False)
    phone = fields.Char('Phone', readonly=True if state=='done' else False, required=False if state=='done' else True)
    batch_id = fields.Many2one('op.batch', 'Batch', required=False, readonly=True if state=='done' else False)
    mobile = fields.Char('Mobile', readonly=True if state=='done' else False, required=False if state=='submit' else True)
    course_id = fields.Many2one('op.course', 'Course', readonly=True if state=='done' else False)
    # store_id = fields.Char()
    
    # Cancel inherited constrains
    @api.constrains('register_id', 'application_date')
    def _check_admission_register(self):
        return True
    
    @api.onchange('first_name', 'middle_name', 'last_name')
    def _onchange_name(self):
        pass
    
    #constrains
    @api.constrains('mobile_number','parent_mobile')
    def validate_mobile(self):
        for obj in self:
            print(obj.mobile_number)
            if obj.mobile_number:
                if re.match("^[0-9]{11}$|^[0-9]{11}$", obj.mobile_number) == None:
                    raise ValidationError("Please Provide valid  Mobile Number !")
            if obj.parent_mobile:
                if re.match("^[0-9]{11}$|^[0-9]{11}$", obj.parent_mobile) == None:
                    raise ValidationError("Please Provide valid parent Mobile Number !")
            else:
                return True
    
    @api.constrains('national_id')
    def validate_national_id(self):
        for obj in self:
            #if re.match("^[0-9]{14}$|^[0-9]{14}$", obj.national_id) == None:
                #raise ValidationError("Please Provide valid National ID: %s" % obj.national_id)
            #else:
            domain = [
                ('national_id', '=', obj.national_id),
                ('horus_admission_id', '=', obj.horus_admission_id.id),
                ('id', '!=', obj.id),
            ]
            data = self.sudo().search_count(domain)
            if data:
                raise ValidationError(('National ID already has Admission Application '))
            return True
        
    def _compute_required_field(self):
        if self.env.user.has_group('hr_extention.group_service_manager'):
            self.required_field = False
        else:
            self.required_field = self.env.user.has_group('openeducat_core.group_op_back_office')
            
    
    # Add computed fields     
    @api.depends("admission_application_ids")
    def _compute_amount_total(self):
        amount_total = 0
        registers = self.admission_application_ids
        for reg in registers:
            product = reg.register_id.product_id
            if product.id:
                amount_total += product.list_price
        self.amount_total = amount_total
    
    @api.depends('admission_application_ids.fees')
    def compute_total(self):
        self.amount_total = sum(line.fees for line in self.admission_application_ids)
    
    @api.depends('admission_application_ids','state')
    def compute_enroll_date(self):
        for application in self.admission_application_ids:
            if application.application_status == 'enroll':
                self.enroll_date = application.write_date
            
    # Customizing form buttons
    def submit_form(self):
        if not self.admission_application_ids:
            raise ValidationError(_("Admission Applications can't be empty"))
        self.state = 'submit'
        for rec in self.admission_application_ids :
            rec.write({'application_date': fields.datetime.today()})      
    
    def confirm_in_progress(self):
        # partner_id = self.env['res.partner'].create({'name': self.name})
        for record in self:
            if not record.partner_id:
                partner_id = self.env['res.partner'].create({'name': record.name})
                record.partner_id = partner_id.id
                partner_id = partner_id
            else:
                partner_id = self.partner_id
        print("Application number",self.application_number)
        if self.application_number == False :
            admission = self.env['op.hue.admission'].sudo().search([('active_admission','=',True)],limit=1)
            code = self.env['op.admission'].sudo().search([('application_number_sequence','!=',0),('horus_admission_id','=',admission.id)], order='application_number_sequence desc', limit=1).application_number_sequence
            if code :
                new_code = (code)+1
            else:
                new_code = '1001'
        else:
            new_code = self.application_number_sequence
        app_idetifier = ""
        # new_invoice
        amount = 0
        invoice_line_ids = []
        for admission_application in self.admission_application_ids:
            if admission_application.application_status != 'refund':
                print('admission_application.register_id_identifier: ',admission_application.register_id.identifier)
                app_idetifier +=  admission_application.register_id.identifier
            if admission_application.application_status == 'draft':
                account_id = False
                product = admission_application.register_id.product_id
                if product.id:
                    account_id = product.property_account_income_id.id
                    amount += product.list_price
                    name = product.name
                    print("Account_id: ", account_id)
                if not account_id:
                    account_id = product.categ_id.property_account_income_categ_id.id
                    print("Account_id: ", account_id)
                if not account_id:
                    raise UserError(
                        _('There is no income account defined for this product: "%s". \
                           You may have to install a chart of account from Accounting \
                           app, settings menu.') % (product.name,))    
                invoice_line_ids.append((0, 0, {
                        'name': name,
                        # 'payment_id': self.id,
                        'account_id': account_id,
                        'price_unit': product.list_price,
                        'quantity': 1.0,
                        'discount': 0.0,
                        # 'uom_id': self.register_id.product_id.uom_id.id,
                        'product_id': product.id,
                    }))
        print("Amount: ", amount)
        if amount <= 0.00:
            raise UserError(
                _('The value of the deposit amount must be positive.'))
        self.state = 'confirm'
        if self.application_number == False :
            self.application_number = str(app_idetifier)+str(new_code)
            self.application_number_sequence = new_code
        ref = uuid.uuid4()
        self.ref_number = ref
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            # 'name': self.name,
            # 'name': self.env['ir.sequence'].next_by_code('account.move') or _('New'),
            'invoice_origin': self.application_number,
            'journal_id': self.journal_id.id,
            'ref': False,
            'is_application':1,
            'account_id': partner_id.property_account_receivable_id.id,
            'partner_id': partner_id.id,
            'invoice_line_ids': invoice_line_ids,
        })
        form_view = self.env.ref('hue_admission.view_hue_op_admission_credit_note_form') 
        tree_view = self.env.ref('account.view_invoice_tree')
        value = {
             'domain': str([('id', '=', invoice.id)]),
             'view_type': 'form',
             'view_mode': 'form',
             'res_model': 'account.move',
             'view_id': False,
             'views': [(form_view and form_view.id or False, 'form'),
                        (tree_view and tree_view.id or False, 'tree')],
             'type': 'ir.actions.act_window',
             'res_id': invoice.id,
             'target': 'current',
             'nodestroy': True
        }
        invoice.action_post()
        # invoice.action_register_payment()
        for admission_application in self.admission_application_ids:
            if admission_application.application_status == 'draft':
                admission_application.invoice_id = invoice.id
                admission_application.application_status = 'paid'
        self.partner_id = partner_id
        
        #Payment
        payment = self.env['account.payment']
        # if self.journal_id:
        #     journal_id  = self.journal_id.id
        #     if journal_id == 6:
        #         raise UserError(
        #             _('برجاء إختيار الخزينة او البنك بشكل صحيح'))
        # else:
        #     journal_id = 6
        #     if journal_id == 6:
        #         raise UserError(
        #             _('برجاء إختيار الخزينة او البنك بشكل صحيح'))
        print("invoice ids", invoice.ids)
        # odoo 16 code
        self.ensure_one()
         
        payment_method_line = self.journal_id.inbound_payment_method_line_ids\
             .filtered(lambda l: l.company_id == self.company_id)
        payment._check_payment_method_line_id()
        if len(payment_method_line) == 0:
            raise ValidationError(_("Journal should have at least one payment method"))
        print("payment_method_line", payment_method_line[0])
        payment_values = {
             'amount': abs(invoice.amount_total),  # A tx may have a negative amount, but a payment must >= 0
             'payment_type': 'inbound' if invoice.amount_total > 0 else 'outbound',
             # 'currency_id': self.currency_id.id,
             'notes': '',
             'partner_id': self.partner_id.commercial_partner_id.id,
             'partner_type': 'customer',
             'journal_id': self.journal_id.id,
             'company_id': self.company_id.id,
             'payment_method_line_id': payment_method_line[0].id,
             # 'payment_token_id': self.token_id.id,
             # 'payment_transaction_id': self.id,
        }
        payment = self.env['account.payment'].create(payment_values)
        payment.action_post()
        self.env['account.payment.register'].with_context(active_model='account.move', active_ids=invoice.ids).create({
            'payment_date': invoice.date,
        })._create_payments()
        # payments = payment.create(vals)
        # payments.action_post()
        return self.env.ref('account.report_payment_receipt')
    
        # return self.env.ref('hue_admission.admission_report_payment_receipt')
        # return value
    
    def admission_confirm(self):
        if self.certificate_percentage <= 0:
            raise ValidationError(_("Certificate Percentage must be grater than 0"))
        self.state = 'admission'
    
    def confirm_cancel(self):
        self.state = 'cancel'
        if self.is_student and self.student_id.fees_detail_ids:
            self.student_id.fees_detail_ids.state = 'cancel'
            
    def get_student_vals(self):
        for student in self:
            student_user = self.env['res.users'].create({
                'name': student.name,
                'login': student.email,
                'image_1920': self.image or False,
                'is_student': True,
                'company_id': self.company_id.id,
                'groups_id': [
                    (6, 0,
                     [self.env.ref('base.group_portal').id])]
            })
            details = {
                'phone': student.phone,
                'mobile': student.mobile_number,
                'email': student.email,
                'street': student.street,
                'street2': student.street2,
                'city': student.city,
                'country_id':
                    student.country_id and student.country_id.id or False,
                'state_id': student.state_id and student.state_id.id or False,
                'image_1920': student.image,
                'zip': student.zip,
            }
            student_user.partner_id.write(details)
            details.update({
                'title': student.title and student.title.id or False,
                'first_name': student.first_name,
                'middle_name': student.middle_name,
                'last_name': student.last_name,
                'birth_date': student.birth_date,
                'gender': student.gender,
                'image_1920': student.image or False,
                'course_detail_ids': [[0, False, {
                    'course_id':
                        student.course_id and student.course_id.id or False,
                    'batch_id':
                        student.batch_id and student.batch_id.id or False,
                    'academic_years_id':
                        student.register_id.academic_years_id.id or False,
                    'academic_term_id':
                        student.register_id.academic_term_id.id or False,
                    'fees_term_id': student.fees_term_id.id,
                    'fees_start_date': student.fees_start_date,
                    'product_id': student.register_id.product_id.id,
                }]],
                'user_id': student_user.id,
                'company_id': self.company_id.id,
                'partner_id': student_user.partner_id.id,
                'course_id': student.course_id and student.course_id.id or False,
                'faculty': student.course_id.faculty_id.id  or False,
                'student_nationality': student.nationality_id.id or False,
                'religion': student.religion or False,
                'student_status': student.std_status_id.id or False,
                'student_code': student.student_code or False,
                'mobile': student.mobile_number or False,
                'stumobile': student.mobile_number or False,
                'stutele': student.home_number or False,
                'en_name': student.english_name or False,
                'join_year': student.join_year_id.id or False,
                'd_name': student.d_name or False,
                'join_term': student.semster_id.id or False,
                'national_id': student.national_id or False,
                'father_name': student.father_name or False,
                'father_mobile': student.father_mobile or False,
                'father_nationality': student.father_nationality.id or False,
                'father_job': student.father_job or False,
                'father_mail': student.father_mail or False,
                'mother_name': student.mother_name or False,
                'mother_job': student.mother_job or False,
                'mother_mobile': student.mother_mobile or False,
                'mother_mail': student.mother_mail or False,
                'mother_nationality': student.mother_nationality.id or False,
                'sibling_name': student.sibling_name or False,
                'sibling_id': student.sibling_id or False,
                'sibling_student_id': student.sibling_student_id.id or False,
                'street': student.address or False,
                'mc': student.mc or False,
                'father_discount': student.staff_dis or False,
                'brother_discount': student.sibling_dis or False,
                'syndicate_discount': student.syndicate_dis or False,
                'martyrs_discount': student.martyrs_dis or False,
                'student_certificates': student.certificate_id.id or False,
                'percentage': student.certificate_percentage or False,
                'certificate_degree': student.certificate_degree,
                'seatno': student.seat_no,
                'qualyear': student.join_year_id.id or False,
                'special_case': student.special_case,
            })
            return details
        
    def enroll_student(self):
        for record in self:
            if record.register_id.max_count:
                total_admission = self.env['op.admission'].search_count(
                    [('register_id', '=', record.register_id.id),
                     ('state', '=', 'done')])
                if not total_admission < record.register_id.max_count:
                    msg = 'Max Admission In Admission Register :- (%s)' % (
                        record.register_id.max_count)
                    raise ValidationError(_(msg))
            if not record.student_id:
                 vals = record.get_student_vals()
                 record.partner_id = vals.get('partner_id')
                 record.student_id = student_id = self.env[
                     'op.student'].create(vals).id
             
            else:
                 student_id = record.student_id.id
                 record.student_id.write({
                     'course_detail_ids': [[0, False, {
                         'course_id':
                              record.course_id and record.course_id.id or False,
                         'batch_id':
                              record.batch_id and record.batch_id.id or False,
                         'fees_term_id': record.fees_term_id.id,
                         'fees_start_date': record.fees_start_date,
                         'product_id': record.register_id.product_id.id,
                     }]],
                 })
            if record.fees_term_id.fees_terms in ['fixed_days', 'fixed_date']:
                 val = []
                 product_id = record.register_id.product_id.id
                 for line in record.fees_term_id.line_ids:
                     no_days = line.due_days
                     per_amount = line.value
                     amount = (per_amount * record.fees) / 100
                     dict_val = {
                         'fees_line_id': line.id,
                         'amount': amount,
                         'fees_factor': per_amount,
                         'product_id': product_id,
                         'discount': record.discount or record.fees_term_id.discount,
                         'state': 'draft',
                         'course_id': record.course_id and record.course_id.id or False,
                         'batch_id': record.batch_id and record.batch_id.id or False,
                     }
                     if line.due_date:
                         date = line.due_date
                         dict_val.update({
                             'date': date
                         })
                     elif self.fees_start_date:
                         date = self.fees_start_date + relativedelta(
                             days=no_days)
                         dict_val.update({
                             'date': date,
                         })
                     else:
                         date_now = (datetime.today() + relativedelta(
                             days=no_days)).date()
                         dict_val.update({
                             'date': date_now,
                         })
                     val.append([0, False, dict_val])
                 record.student_id.write({
                     'fees_detail_ids': val
                 })
            record.write({
                 'nbr': 1,
                 'state': 'done',
                 'admission_date': fields.Date.today(),
                 'student_id': student_id,
                 'is_student': True,
             })
            # reg_id = self.env['op.subject.registration'].create({
            #      'student_id': student_id,
            #      'batch_id': record.batch_id.id,
            #      'course_id': record.course_id.id,
            #      'min_unit_load': record.course_id.min_unit_load or 0.0,
            #      'max_unit_load': record.course_id.max_unit_load or 0.0,
            #      'state': 'draft',
            #  })
            if not record.mobile_number:
                 raise UserError(
                     _('Please fill in the mobile number'))
            # reg_id.get_subjects()
            
            
    def create_invoice(self):
        """ Create invoice for fee payment process of student """

        partner_id = self.env['res.partner'].create({'name': self.name})
        account_id = False
        product = self.register_id.product_id
        if product.id:
            account_id = product.property_account_income_id.id
        if not account_id:
            account_id = product.categ_id.property_account_income_categ_id.id
        if not account_id:
            raise UserError(
                _('There is no income account defined for this product: "%s". \
                   You may have to install a chart of account from Accounting \
                   app, settings menu.') % (product.name,))
        if self.fees <= 0.00:
            raise UserError(
                _('The value of the deposit amount must be positive.'))
        amount = self.fees
        name = product.name
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'name': self.name,
            'invoice_origin': self.application_number,
            'journal_id': self.journal_id.id,
            'ref': False,
            'account_id': partner_id.property_account_receivable_id.id,
            'partner_id': partner_id.id,

            'invoice_line_ids': [(0, 0, {
                'name': name,
                # 'payment_id': self.id,
                'account_id': account_id,
                'price_unit': amount,
                'quantity': 1.0,
                'discount': 0.0,
                # 'uom_id': self.register_id.product_id.uom_id.id,
                'product_id': product.id,
            })],
        })
        # invoice.compute_taxes()
        # form_view = self.env.ref('account.account_invoice_send_wizard_form')
        tree_view = self.env.ref('account.view_invoice_tree')
        value = {
             'domain': str([('id', '=', invoice.id)]),
             'view_type': 'form',
             'view_mode': 'form',
             'res_model': 'account.move',
             'view_id': False,
             # 'views': [(form_view and form_view.id or False, 'form'),
             #           (tree_view and tree_view.id or False, 'tree')],
             'views': [(tree_view and tree_view.id or False, 'tree')],
             'type': 'ir.actions.act_window',
             'res_id': invoice.id,
             'target': 'current',
             'nodestroy': True
        }
        self.partner_id = partner_id
        self.state = 'admission'
        return value
    
    # def change_college(self):
    #     for record in self:
    #         record.state="draft"
    #         if record.national_id:
    #             record.store_id = record.national_id
    #             record.national_id = ""
            