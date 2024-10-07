from odoo import fields, models, api,_
from datetime import datetime
import random
import string
from odoo.exceptions import UserError, ValidationError
import urllib.request as urllib2
import ssl
import json

class CustomStudent(models.Model):
    _inherit = 'op.student'
    
    
    advisor = fields.Char()
    allow_registration = fields.Boolean(string='Allow Registration', tracking=True)
    already_partner = fields.Boolean(string='Already Partner')
    alumni_academicyear_id = fields.Many2one('op.academic.year', string='Alumni Academic Year')
    alumni_semester_id = fields.Many2one('op.semesters', string='Alumni Semester')
    approval_num = fields.Char("Approval number")
    approval_date = fields.Date(string="Approval Date")
    approval_type = fields.Selection([('استنفاذ مرات رسوب','استنفاذ مرات رسوب'),('السنة الحالية','السنة الحالية'),
                                      ('تقديم مباشر','تقديم مباشر'),('تنسيق داخلي','تنسيق داخلي'),('سنوات سابقة','سنوات سابقة')
                                      ,('محول','محول'),('معوق','معوق'),('مفصول كلية','مفصول كلية'),
                                      ('مكتب تنسيق - انترنت','مكتب تنسيق - انترنت'),('مكتب تنسيق - ورقي','مكتب تنسيق - ورقي'),
                                      ('نقل قيد','نقل قيد')],string='Approval Type')
    bank_account_count = fields.Integer(string='Bank')
    bank_ids = fields.One2many('res.partner.bank', 'partner_id', string='Banks')
    brother_discount = fields.Boolean(string='Sibling discount', tracking=True)
    certificate_degree = fields.Float(string='Certificate Degree')
    certificate_date = fields.Selection([(str(num), str(num)) for num in range((datetime.now().year)-10,(datetime.now().year)+1 )], string='Certificate Date')
    certificate_country = fields.Many2one('hue.nationalities', string='Certificate Country')
    cgpa = fields.Float(tracking=True)
    commercial_partner_country_id = fields.Many2one('res.country', string="Commercial Entity's Country")
    conflict_crh = fields.Boolean(string='Conflict Crh')
    conflict_gpa = fields.Boolean(string='Conflict Gpa')
    contracts_count = fields.Integer(string='Contracts')
    core_crh = fields.Float(string='Core Hours')
    course_id = fields.Many2one('op.course', string='Course', tracking=True,domain="[('parent_id', '=', course_id)]")
    crh = fields.Float(string='Earned Hours')
    customer = fields.Boolean(string='Is a Customer', help='Check this box if this contact is a customer.')
    decisionno = fields.Char(string='Decision Number',tracking=True)
    d_name = fields.Char(string='ID Name')
    elective_crh = fields.Float(string='Elective Hours')
    en_name = fields.Char(string='En Name')
    faculty = fields.Many2one('hue.faculties', tracking=True)
    father_discount = fields.Boolean(string='Staff discount', tracking=True)
    father_job = fields.Char(string='Father Job')
    father_mail = fields.Char(string='Father Mail')
    father_mobile = fields.Char(string='Father Mobile')
    father_name = fields.Char(string='Father Name')
    father_nationality = fields.Many2one('hue.nationalities', string='Father Nationality')
    father_phone = fields.Char(string='Father Phone')
    final_degree = fields.Float(string='Final Degree')
    gardian_mobile = fields.Char(string='Guardian Mobile',tracking=True)
    gardian_name = fields.Char(string='Guardian Name',tracking=True)
    gardian_tele = fields.Char(string='Guardian Phone',tracking=True)
    gardian_type = fields.Selection([('أب','أب'),('أم','أم'),('خال','خال'),('عم','عم'),('أخ','أخ'),('أخت','أخت')] , tracking=True, string="Guardian Type")
    gardian_job = fields.Char(string='Guardian Job')
    graduation_date = fields.Date(string='Graduation Date')
    image = fields.Binary(help='This field holds the image used as avatar for this contact, limited to 1024x1024px')
    image_medium = fields.Binary(string='Medium-sized image', help='Medium-sized image of this contact. It is automatically resized as a 128x128px image, with aspect ratio preserved. Use this field in form views or some kanban views.')
    image_small = fields.Binary(string='Small-sized image', help='Small-sized image of this contact. It is automatically resized as a 64x64px image, with aspect ratio preserved. Use this field anywhere a small image is required.')
    intern_month = fields.Integer(string='Intern Month')
    join_term = fields.Many2one('op.semesters', string='Join Term',tracking=True)
    join_year = fields.Many2one('hue.joining.years', string='Join Year',tracking=True)
    level = fields.Many2one('op.levels', tracking=True)
    library_card_id = fields.Many2one('op.library.card', string='Library Card')
    martyrs_discount = fields.Boolean(string='Martyrs discount', tracking=True)
    mc = fields.Boolean(tracking=True)
    m_graph_id = fields.Char(string='M Graph')
    military_date = fields.Char(string='Military Date',tracking=True)
    militaryno = fields.Char(string='Military Number',tracking=True)
    military_status = fields.Selection([('استثناء','استثناء'),('أدى الخدمة','أدى الخدمة'),('معاف مؤقت','معاف مؤقت'),('معاف نهائي','معاف نهائي'),('مؤجل لسن 28','مؤجل لسن 28'),('مؤجل لسن 29','مؤجل لسن 29'),('تحت الطلب','تحت الطلب')],string='Military Status', tracking=True)
    mother_job = fields.Char(string='Mother Job')
    mother_mail = fields.Char(string='Mother Mail')
    mother_mobile = fields.Char(string='Mother Mobile')
    mother_name = fields.Char(string='Mother Name')
    mother_nationality = fields.Many2one('hue.nationalities', string='Mother Nationality')
    mother_phone = fields.Char(string='Mother Phone')
    national_id = fields.Char(string='National ID', tracking=True)
    national_id_issue_date = fields.Date(string='ID issuance date')
    new_crh = fields.Float(string='New Earned Hours')
    new_gpa = fields.Float(string='New GPA')
    opt_out = fields.Boolean(string='Opt-Out', help="If opt-out is checked, this contact has refused to receive emails for mass mailing and marketing campaign. Filter 'Available for Mass Mailing' allows users to filter the partners when performing mass mailing.")
    partner_ledger_label = fields.Char(string='Partner Ledger Label', help='The label to display on partner ledger button, in form view')
    password = fields.Char()
    payment_next_action = fields.Text(string='Next Action', help='Note regarding the next action.')
    payment_next_action_date = fields.Date(string='Next Action Date', help='The date before which no action should be taken')
    percentage = fields.Float(tracking=True)
    photo_hide = fields.Boolean(string='Hide Photo', tracking=True)
    prequaldegree = fields.Float(string='Degree',tracking=True)
    previous_course_id = fields.Many2one('op.course', string='Previous Course', tracking=True)
    project_crh = fields.Float(string='Project Hours')
    project_gpa = fields.Float(string='Project GPA')
    project_grade = fields.Many2one('op.grades', string='Project Grade')
    project_title = fields.Char(string='Project Title')
    qr_image = fields.Binary(string='QR Code')
    qualyear = fields.Many2one('hue.joining.years', string='Qualyear',tracking=True)
    registration_block_reason = fields.Many2one('hue.block.reason', string='Registration Block Reason',tracking=True)
    reg_timestamp = fields.Datetime(string='Reg Timestamp')
    related_student = fields.Many2one('op.student', string='Student')
    religion = fields.Selection([('m','Muslim - مسلم'),('c','Christian - مسيحي')],tracking=True)
    result_block_reason = fields.Many2one('hue.block.reason', string='Result Block Reason',tracking=True)
    sale_order_count = fields.Integer(string='# of Sales Order')
    scholarship = fields.Selection([(str(num), ('Partial '+ str(num)+ ' %') if num<100 else 'Full') for num in range(5,102,5)],tracking=True)
    sds_tobedeleted = fields.Boolean(string='Sds Tobedeleted',tracking=True)
    seatno = fields.Char(string='Seat Number',tracking=True)
    sibling_id = fields.Char(string='Sibling')
    sibling_name = fields.Char(string='Sibling Name')
    sibling_student_id = fields.Many2one('op.student', string='Sibling Student')
    special_case = fields.Boolean(string='Special Case', tracking=True)
    specialized_faculty = fields.Boolean(string='Specialized Faculty')
    specialneeds = fields.Boolean(string='Special Needs',tracking=True)
    student_birth_place = fields.Many2one('hue.cities', string='Student Birth Place',tracking=True)
    student_certificates = fields.Many2one('hue.certificates', string='Student Certificates',tracking=True)
    student_city = fields.Many2one('hue.cities', string='Student birth Country', tracking=True)
    student_code = fields.Integer(string='Student Code', tracking=True)
    student_nationality = fields.Many2one('hue.nationalities', string='Student Nationality',tracking=True)
    student_school = fields.Char("Student school")
    student_status = fields.Many2one('hue.std.data.status', string='Student Status',tracking=True)
    student_term = fields.Integer(string='Student Term')
    stumobile = fields.Char(string='Mobile',tracking=True)
    stutele = fields.Char(string='Phone',tracking=True)
    subject_degree = fields.Float(string='Subject Degree')
    supplier = fields.Boolean(string="Is a Vendor", help="Check this box if this contact is a vendor. If it's not checked, purchase people will not see it when encoding a purchase order.")
    syndicate_discount = fields.Boolean(string='Syndicate discount', tracking=True)
    task_count = fields.Integer(string='# Tasks')
    timestamp = fields.Datetime(string='Timestamp')
    total_degree = fields.Float(string='Total Degree')
    total_due = fields.Monetary(string='Total Due')
    transfer_type = fields.Selection([('internal', 'internal'), ('external', 'external')])
    Pre_join_year = fields.Many2one('hue.joining.years', string='Pre Join Year')
    pre_transfer_type = fields.Selection([('استنفاذ مرات الرسوب','استنفاذ مرات الرسوب'), ('السنة الحالية', 'السنة الحالية')
                                          , ('تقديم مباشر', 'تقديم مباشر'), ('سنوات سابقة', 'سنوات سابقة')
                                          , ('مقاصة', 'مقاصة')], string="Pre Transfer Typr")
    transferred_from = fields.Char()
    tree_clo_acl_ids = fields.Char(string='Tree Clo Acl')
    university_country = fields.Many2one('res.country', string='University Country',readonly= True)
    user_id = fields.Many2one('res.users', 'Related User')
    unreconciled_aml_ids = fields.One2many('account.move.line', 'partner_id', string='Unreconciled Aml')
    year = fields.Selection([(str(num), str(num)) for num in range((datetime.now().year)-15,(datetime.now().year)+5)])

    @api.model
    def web_search_read(self, domain, specification, offset=0, limit=None, order=None, count_limit=None):
        # Check if there's a search value in the domain
        search_value = None
        for condition in domain:
            if condition[0] == 'name' and condition[1] == 'ilike':
                search_value = condition[2]
                break
        # If a search value exists
        if search_value:
            # Search for a student with the exact student_code
            try:
                student = self.search([('student_code', '=', search_value)], limit=1)
            except:
                student = ""
            if not student:
                # Fallback to searching by name if no student_code match found
                domain = [('name', 'ilike', search_value)]
            else:
                domain = [('id', '=', student.id)]

        return super(CustomStudent, self).web_search_read(domain, specification, offset, limit, order, count_limit)

    def randomStringwithDigitsAndSymbols(self,stringLength=8):
        """Generate a random string of letters, digits and special characters """
        lettersAndDigits = string.ascii_letters + string.digits
        return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))
    
    @api.constrains('birth_date')
    def _check_birthdate(self):
        for record in self:
            if record.birth_date:
                if record.birth_date > fields.Date.today():
                    raise ValidationError(_(
                        "Birth Date can't be greater than current date!"))

    @api.onchange('first_name', 'middle_name', 'last_name')
    def _onchange_name(self):
        pass
    
    def validate_student_code(self):
        for obj in self:
            domain = [
                ('student_code', '=', obj.student_code),
                ('id', '!=', obj.id),
            ]
            data = self.sudo().search_count(domain)
            if data:
                raise ValidationError(('Student Code alredy exist, Try again '))
            return True
    
    def randomString(self,stringLength=6):
        return ''.join(random.choice(str(random.randint(1,9))) for i in range(stringLength))
    
    
    @api.model
    def get_hue_basic_students_fun(self):
        hue_student = self.env['op.student']
        url = "https://sys.mc.edu.eg/WebServiceMCI?index=GetStudentBasicData&userName=myd777myd&password=lo@stmm&ProgID=2"
        req = urllib2.Request(url, headers={ 'X-Mashape-Key': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX' })
        gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)  # Only for gangstars
        webURL = urllib2.urlopen(req, context=gcontext)
        data = webURL.read()
        encoding = webURL.info().get_content_charset('utf-8')
        data = json.loads(data.decode(encoding))
        for  val in data:
            if len(val) == 1:
                continue
            stu_id = val['StudentID']
            stu = hue_student.search([('student_code','=',stu_id)],limit=1)
            if not stu:
                #join year
                join_year_id = self.env['hue.joining.years'].search([('d_id','=',val['JoiningYearID'])],limit=1).id
                if not join_year_id:
                    raise UserError('Please update your join year table, recieived Id not exsisting')
                #city
                city_id = self.env['hue.cities'].search([('d_id','=',val['CityID'])],limit=1).id
                if not city_id:
                    raise UserError('Please update your cities, recieived Id not exsisting')
                #student status
                student_status_id = self.env['hue.std.data.status'].search([('d_id','=',val['StudentStatusID'])],limit=1).id
                if not student_status_id:
                    raise UserError('Please update your cities, recieived Id not exsisting')
                #Nationality
                nationality_id = self.env['hue.nationalities'].search([('d_id','=',val['NationalityID'])],limit=1).id
                if not nationality_id:
                    raise UserError('Please update your cities, recieived Id not exsisting')
                #create student
                hue_student.create({'name':val['Studentname'], 'student_code':val['StudentID'],
                                    'stumobile':val['Phone'], 'crh':val['EarnedHours'], 'join_year':join_year_id,
                                    'student_birth_place':city_id,'student_status':student_status_id, 'mc':val['MC'],
                                    'cgpa':val['CGPA'], 'student_nationality':nationality_id})  
    
    
    @api.model
    def modify_student_data_fun_2(self):
        hue_student = self.env['op.student']
        stus = hue_student.search([])
        for stu in stus:
            stu.write({'faculty':1})
    
    @api.model
    def diable_ldap_user(self):
        ldap_conn = self.env["ldap.directory"]._ldap_connect()
        conn = ldap_conn[0]
        conn.start_tls()
        ldap_base = ldap_conn[1]
        print("11111111111")
        status_ids = self.env['hue.std.data.status'].sudo().search([('name', 'not in',['مستجد'])])._ids
        i = 1
        for rec in self.search([('student_status', 'in', status_ids)]):
            ldap_base = 'OU=HUE-Faculties,DC=mca,DC=edu,DC=eg'
            search_dn = conn.search(format(ldap_base),search_filter='(|(sAMAccountName='+str(rec.student_code)+')(mail='+rec.email+'))',search_scope=SUBTREE,attributes=['distinguishedName','userAccountControl'])
            if search_dn:
                userdn = str(conn.response[0]['attributes']['distinguishedName'])
                userAccountControl = str(conn.response[0]['attributes']['userAccountControl'])
                if userAccountControl == '66048' :
                    conn.modify(userdn, {'userAccountControl': [('MODIFY_REPLACE', 2)]})
                    print("_________________________" + str(i) + "__________________________")
                    i = i+1
    
    #Button in student form
    def create_student_user(self):
        user_group = self.env.ref("base.group_portal") or False
        users_res = self.env['res.users']
        for record in self:
            if not record.user_id:
                if record.password:
                    user_id = users_res.create({
                        'name': record.name,
                        'partner_id': record.partner_id.id,
                        'login': record.email,
                        'groups_id': user_group,
                        'password': record.password,
                        'is_student': True,
                        'tz': self._context.get('tz'),
                    })
                    record.user_id = user_id
                else:
                    user_id = users_res.create({
                        'name': record.name,
                        'partner_id': record.partner_id.id,
                        'login': record.email,
                        'groups_id': user_group,
                        'is_student': True,
                        'tz': self._context.get('tz'),
                    })
                    record.user_id = user_id


    def create_user(self):
        print("______________Create user for student")
        ldap_conn = self.env["ldap.directory"]._ldap_connect()
        conn = ldap_conn[0]
        conn.start_tls()
        conn.raise_exceptions = True
        ldap_base = ldap_conn[1]
        print('000000000000000000000')
        # create user
        for rec in self:
            if not rec.password:
                print('11111111111111111111111')
                userdn = 'CN=' + str(rec.student_code) + ',' + rec.faculty.ldap_dn
                username = str(rec.student_code)
                application_en_full_name = self.env['op.admission'].search([('Student_code', '=', rec.student_code)], limit=1).english_name
                ldap_base = 'OU=HUE-Faculties,DC=mca,DC=edu,DC=eg'
                search_dn = conn.search(format(ldap_base), search_filter='(|(sAMAccountName=' + str(
                    rec.student_code) + ')(mail=' + rec.email + '))', search_scope=SUBTREE,
                                        attributes=['distinguishedName', 'userAccountControl'])
                for entry in conn.entries:
                    print(entry)
                if search_dn:
                    print(search_dn)
                    userdn = str(conn.response[0]['attributes']['distinguishedName'])
                    print(userdn)
                    password = self.randomString(6)
                    data = conn.extend.microsoft.modify_password(userdn, password)
                    # for entry in conn.entries:
                    # 	print(entry)
                    data =  conn.modify(userdn, {'userAccountControl': [('MODIFY_REPLACE', 512)]})
                    data =  conn.modify(userdn, {'sTUGR': [('MODIFY_REPLACE', rec.student_status.id)]})
                    print('qqqqqqqqqqqqq')
                    print(data)
                    # for entry in conn.entries:
                    # 	print(entry)
                    password_expire = {"pwdLastSet": [('MODIFY_REPLACE', 0)] }  # // use 0 instead of -1.
                    conn.modify(dn=userdn, changes=password_expire)
                    rec.password = password
                if not search_dn:
                    data = conn.add(userdn, attributes={
                        'objectClass': ['organizationalPerson', 'person', 'top', 'user'],
                        'sAMAccountName': username,
                        'userPrincipalName': "{}@{}".format(username, "mca.edu.eg"),
                        'displayName': application_en_full_name,
                        'mail': str(rec.student_code) + "@mca.edu.eg"  # optional
                    })
                    # Print the resulting entries.
                    # for entry in conn.entries:
                    # 	print(entry)
                    password = self.randomString(6)
                    data = conn.extend.microsoft.modify_password(userdn, password)
                    # for entry in conn.entries:
                    # 	print(entry)
                    data =  conn.modify(userdn, {'userAccountControl': [('MODIFY_REPLACE', 512)]})
                    # for entry in conn.entries:
                    # 	print(entry)
                    password_expire = {"pwdLastSet": [('MODIFY_REPLACE', 0)] }  # // use 0 instead of -1.
                    conn.modify(dn=userdn, changes=password_expire)
                    rec.password = password
            #return True
            else:
                ldap_conn = self.env["ldap.directory"]._ldap_connect()
                username = str(rec.student_code)
                conn = ldap_conn[0]
                ldap_base = ldap_conn[1]
                # data =  conn.modify(userdn, {'studentsstaus': [('MODIFY_REPLACE', rec.student_status.id)]})
                search_dn = conn.search(format(ldap_base),search_filter= "(sAMAccountName="+username+")", search_scope=SUBTREE, attributes=['distinguishedName'])
                if search_dn:
                    userdn = str(conn.response[0]['dn'])
                    conn.modify(userdn, {'sTUGR': [('MODIFY_REPLACE', rec.student_status.id)]})
                    print('qqqqqqqqqqqqq')
                    # print(data)
            oauth_provider = self.env['auth.oauth.provider'].search([('enabled','=', True )],limit=1)
            if oauth_provider:
                provider = oauth_provider.id
            else:
                provider = 0

            if(rec.student_code):
                if rec.last_name:
                    last_name = str(rec.last_name)
                else:
                    last_name = ''
                group_portal = self.env.ref('base.group_portal', False)
                values = {
                    'name': str(rec.name) +" "+ last_name,
                    'image': rec.image,
                    'partner_id': rec.partner_id.id,
                    'login': str(rec.student_code)+"@mca.edu.eg",
                    'active': True,
                    'oauth_provider_id': provider,
                    'oauth_uid': str(rec.student_code)+"@mca.edu.eg",
                    'is_student': True,
                    'groups_id': [(6, 0, [group_portal.id])]
                }
                if rec.user_id:
                    rec.user_id.write(values)
                    user_id = rec.user_id
                else:
                    new_user_id = self.env['res.users'].create(values)
                    rec.user_id = new_user_id.id

                rec.already_partner = True	
                
            else:
                raise UserError('Student code must be set!')					

            
class PartnernData(models.Model):
    _inherit = 'res.partner'
    
    related_student=  fields.Many2one('op.student','Student')
    faculty = fields.Many2one('hue.faculties','faculty')
    mc = fields.Boolean()
    level = fields.Many2one('op.levels','level')
    student_code = fields.Integer('Student Code')
    student_nationality = fields.Many2one('hue.nationalities')
    student_city = fields.Many2one('hue.cities')
    student_status = fields.Many2one('hue.std.data.status')
    student_certificates = fields.Many2one('hue.certificates')
    join_year = fields.Many2one('hue.joining.years',string="Join Year")
    cgpa = fields.Float('cgpa')
    percentage =  fields.Float('Percentage')
    year = fields.Selection([(str(num), str(num)) for num in range((datetime.now().year)-15,(datetime.now().year)+5)])
    name = fields.Char(tracking=True)