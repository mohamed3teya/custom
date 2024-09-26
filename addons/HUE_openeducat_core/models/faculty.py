from odoo import models, fields, api, _
import json
import urllib.request as urllib2
import ssl
import logging

_logger = logging.getLogger(__name__)

class HueFaculties(models.Model):
    _name = 'hue.faculties'
    _description = 'The Main faculties of the university'


    name = fields.Char()
    faculty_create_ou = fields.Many2one('student.ldap.directory', string="faculty create ou")
    farouk_id = fields.Integer(string="Farouk Mapping")
    check_questionnaire = fields.Boolean(default=False, string="Check Questionnaire")
    name_ar = fields.Char(string="Arabic Name")
    identifier = fields.Char()
    ldap_dn = fields.Char()
    intern_year = fields.Boolean(default=False, string="Intern Year")
    
    
    @api.model
    def hue_regular_student_data(self):
        hue_cer = self.env['hue.certificates']
        hue_nationalities = self.env['hue.nationalities']
        hue_levels = self.env['op.levels']
        hue_cities = self.env['hue.cities']
        hue_std_status = self.env['hue.std.data.status']
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
        ###   Get Student Data ####
        student = self.env['op.student']
        hr_faculties = self.env['hue.faculties']
        faculties = hr_faculties.search([])
        for faculty in faculties:
            identifier = faculty.identifier
            url = "https://me.horus.edu.eg/WebServiceHorus?index=GetStudentBasicData&userName=myd777myd&password=lo@stmm&collegeID=" + str(
                identifier)
            req = urllib2.Request(url, headers={'X-Mashape-Key': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'})
            gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)  # Only for gangstars
            webURL = urllib2.urlopen(req, context=gcontext)
            data = webURL.read()
            encoding = webURL.info().get_content_charset('utf-8')
            data = json.loads(data.decode(encoding))
            # print the keys and values
            print(type(data))
            if (type(data) == dict):
                return False
            # return False
            print(type(data))
            index = 0
            for val in data:
                if (index != 0):
                    print("#######################")
                    print(data[index]['StudentID'])
                    # print(data[index]['Studentname'])
                    # print(identifier)
                    Studentname = data[index]['Studentname']
                    Studentcode = data[index]['StudentID']
                    cgpa = data[index]['CGPA']
                    level = data[index]['StudentLevel']
                    phone = data[index]['phone']
                    TransportationState = data[index]['TransportationState']
                    HousingState = data[index]['HousingState']
                    EarnedHours = data[index]['EarnedHours']
                    CertificateID = data[index]['CertificateID']
                    StudentStatusID = data[index]['StudentStatusID']
                    CityID = data[index]['CityID']
                    JoiningYearID = data[index]['JoiningYearID']
                    NationalityID = data[index]['NationalityID']
                    mc = data[index]['MC']
                    CertificatePercentage = data[index]['CertificatePercentage']
                    if CertificatePercentage:
                        CertificatePercentage = float(CertificatePercentage)
                    else:
                        CertificatePercentage = 0
                    std = student.search([('student_code', '=', Studentcode)], limit=1)
                    faculty_id = hr_faculties.search([('identifier', '=', identifier)], limit=1).id
                    Certificate_id = hue_cer.search([('d_id', '=', CertificateID)], limit=1).id
                    StudentStatus_id = hue_std_status.search([('d_id', '=', StudentStatusID)], limit=1).id
                    City_id = hue_cities.search([('d_id', '=', CityID)], limit=1).id
                    JoiningYear_id = hue_joining_years.search([('d_id', '=', JoiningYearID)], limit=1).id
                    NationalityID = hue_nationalities.search([('d_id', '=', NationalityID)], limit=1).id
                    levelID = hue_levels.search([('d_id', '=', level)], limit=1).id
                    year = hue_academic_years.search([('join_year', '=', JoiningYear_id)], limit=1).year
                    year = int(year)
                    email = Studentcode + "@horus.edu.eg"
                    print(CertificatePercentage)
                    if (CertificatePercentage != 0):
                        if not std:
                            atten_id = student.create(
                                {'mc': int(mc), 'name': Studentname, 'student_nationality': NationalityID,
                                 'percentage': CertificatePercentage, 'email': email,
                                 'student_status': StudentStatus_id, 'student_certificates': Certificate_id,
                                 'student_city': City_id, 'student_code': Studentcode, 'faculty': faculty_id,
                                 'year': (year), 'cgpa': cgpa, 'level': levelID, 'join_year': JoiningYear_id})
                            atten_id.partner_id.write({'mc': int(mc), 'student_nationality': NationalityID,
                                                       'percentage': CertificatePercentage,
                                                       'student_status': StudentStatus_id,
                                                       'student_certificates': Certificate_id, 'student_city': City_id,
                                                       'student_code': Studentcode, 'faculty': faculty_id,
                                                       'year': (year), 'cgpa': cgpa, 'level': levelID,
                                                       'join_year': JoiningYear_id})
                            financial_year = financial_years.search(
                                [('join_year', '=', JoiningYear_id), ('faculty', '=', faculty_id)], limit=1)
                            academic_year = academic_years.search([('join_year', '=', JoiningYear_id)], limit=1)
                            if NationalityID == 1:
                                if financial_year:
                                    print("TTTTTTTTTTTTTTTTTT")
                                    installments = hue_installments.search(
                                        [('years_id', '=', financial_year.id), ('one_time', '=', False)])
                                    for installment in installments:
                                        global_term_id = installment.term_id.id
                                        term_data = terms.search([('term_id', '=', academic_year.id),
                                                                  ('global_term_id', '=', global_term_id)], limit=1)
                                        from_date = term_data.from_date
                                        to_date = term_data.from_date
                                        name = term_data.name
                                        print(name)
                                        student_status_assigned = student_status.search(
                                            [('student_id', '=', atten_id.id), ('academic_id', '=', academic_year.id),
                                             ('one_time', '=', 0), ('academic_term_id', '=', term_data.id)],
                                            limit=1).assigned
                                        if not student_status_assigned:
                                            invoice_data = invoice.create(
                                                {'academic_term': term_data.id, 'notes': financial_year.notes,
                                                 'invoice_type': 'regular', 'faculty': faculty_id,
                                                 'student_code': Studentcode, 'academic_year': academic_year.id,
                                                 'invoice_date_due': to_date, 'date_invoice': from_date,
                                                 'partner_id': atten_id.partner_id.id, 'state': 'draft'})
                                            print(invoice_data)
                                            inv_product = product.search([('installments_id', '=', installment.id)])
                                            invoice_line_data = invoice_line.create(
                                                {'name': inv_product.name, 'account_id': self._uid,
                                                 'price_unit': inv_product.standard_price, 'quantity': 1,
                                                 'move_id': invoice_data.id, 'product_id': inv_product.id})
                                            student_status = student_status.create(
                                                {'one_time': False, 'student_id': atten_id.id,
                                                 'academic_id': academic_year.id, 'academic_term_id': term_data.id,
                                                 'invoice_id': invoice_data.id, 'assigned': 1})
                                            discounts = self.env['hue.discounts'].search(
                                                [('percentage_from', '<=', CertificatePercentage),
                                                 ('percentage_to', '>=', CertificatePercentage),
                                                 ('nationality_id', '=', NationalityID),
                                                 ('certificate_id', '=', Certificate_id),
                                                 ('join_year_id', '=', JoiningYear_id),
                                                 ('faculty_ids', '=', faculty_id)])
                                            if not discounts:
                                                if (int(mc) == 0):
                                                    invoice_data.action_invoice_open()

                                if academic_year.join_year.id == JoiningYear_id:
                                    installments = hue_installments.search(
                                        [('years_id', '=', financial_year.id), ('one_time', '=', True)])
                                    student_status_assigned = student_status.search(
                                        [('student_id', '=', atten_id.id), ('academic_id', '=', academic_year.id),
                                         ('one_time', '=', 1)], limit=1).assigned
                                    if not student_status_assigned:
                                        for installment in installments:
                                            global_term_id = installment.term_id.id
                                            term_data = terms.search([('term_id', '=', academic_year.id),
                                                                      ('global_term_id', '=', global_term_id)], limit=1)
                                            from_date = term_data.from_date
                                            to_date = term_data.from_date
                                            name = term_data.name
                                            print(name)
                                            invoice_data = invoice.create(
                                                {'academic_term': term_data.id, 'invoice_type': 'one',
                                                 'faculty': faculty_id, 'student_code': Studentcode,
                                                 'academic_year': academic_year.id, 'invoice_date_due': to_date,
                                                 'date_invoice': from_date, 'partner_id': atten_id.partner_id.id,
                                                 'state': 'draft'})
                                            inv_product = product.search([('installments_id', '=', installment.id)])
                                            invoice_line_data = invoice_line.create(
                                                {'name': inv_product.name, 'account_id': self._uid,
                                                 'price_unit': inv_product.standard_price, 'quantity': 1,
                                                 'move_id': invoice_data.id, 'product_id': inv_product.id})
                                            student_status = student_status.create(
                                                {'student_id': atten_id.id, 'academic_id': academic_year.id,
                                                 'one_time': 1, 'invoice_id': invoice_data.id, 'assigned': 1})
                                            invoice_data.action_invoice_open()

                                discounts = self.env['hue.discounts'].search(
                                    [('percentage_from', '<=', CertificatePercentage),
                                     ('percentage_to', '>=', CertificatePercentage),
                                     ('nationality_id', '=', NationalityID),
                                     ('certificate_id', '=', Certificate_id),
                                     ('join_year_id', '=', JoiningYear_id), ('faculty_ids', '=', faculty_id)])
                                for discount in discounts:
                                    product_data = product.search([('discount_id', '=', discount.id)])
                                    partner_id = (atten_id.partner_id)
                                    invoices_data_count = len(invoice.search(
                                        [('partner_id', '=', partner_id.id), ('invoice_type', '=', 'regular'),
                                         ('academic_year', '=', product_data.academic_id.id)])._ids)
                                    invoices_data = invoice.search(
                                        [('partner_id', '=', partner_id.id), ('invoice_type', '=', 'regular'),
                                         ('academic_year', '=', product_data.academic_id.id)])
                                    if invoices_data:
                                        print(invoices_data)
                                        for invoice_data in invoices_data:
                                            price_unit = product_data.standard_price / invoices_data_count
                                            invoice_line_data = invoice_line.create(
                                                {'name': product_data.name, 'account_id': self._uid,
                                                 'price_unit': price_unit, 'quantity': 1, 'movee_id': invoice_data.id,
                                                 'product_id': product_data.id})
                                            if (int(mc) == 0):
                                                invoice_data.action_invoice_open()
                                if (int(mc) == 1):
                                    mc_discounts = self.env['hue.discounts'].search([('mc', '=', 1),
                                                                                     ('join_year_id', '=',
                                                                                      JoiningYear_id),
                                                                                     ('faculty_ids', '=', faculty_id)])
                                    for discount in mc_discounts:
                                        product_data = product.search([('discount_id', '=', discount.id)])
                                        partner_id = (atten_id.partner_id)
                                        invoices_data_count = len(invoice.search(
                                            [('partner_id', '=', partner_id.id), ('invoice_type', '=', 'regular'),
                                             ('academic_year', '=', product_data.academic_id.id)])._ids)
                                        invoices_data = invoice.search(
                                            [('partner_id', '=', partner_id.id), ('invoice_type', '=', 'regular'),
                                             ('academic_year', '=', product_data.academic_id.id)])
                                        if invoices_data:
                                            print(invoices_data)
                                            for invoice_data in invoices_data:
                                                price_unit = product_data.standard_price / invoices_data_count
                                                invoice_line_data = invoice_line.create(
                                                    {'name': product_data.name, 'account_id': self._uid,
                                                     'price_unit': price_unit, 'quantity': 1,
                                                     'move_id': invoice_data.id, 'product_id': product_data.id})
                                                invoice_data.action_invoice_open()
                                print(discounts)

                index += 1


    @api.model
    def hue_joining_year(self):
        hue_cer = self.env['hue.certificates']
        hue_nationalities = self.env['hue.nationalities']
        hue_levels = self.env['op.levels']
        hue_cities = self.env['hue.cities']
        hue_std_status = self.env['hue.std.data.status']
        hue_joining_years = self.env['hue.joining.years']
        hue_academic_years = self.env['op.academic.year']
        print("##########")
        student = self.env['op.student']
        hr_faculties = self.env['hue.faculties']
        faculties = hr_faculties.search([])
        for faculty in faculties:
            identifier = faculty.identifier
            url = "https://me.horus.edu.eg/WebServiceHorus?index=GetStudentBasicData&userName=myd777myd&password=lo@stmm&collegeID=" + str(
                identifier)
            req = urllib2.Request(url, headers={'X-Mashape-Key': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'})
            gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)  # Only for gangstars
            webURL = urllib2.urlopen(req, context=gcontext)
            data = webURL.read()
            encoding = webURL.info().get_content_charset('utf-8')
            data = json.loads(data.decode(encoding))
            # print the keys and values
            print(type(data))
            if (type(data) == dict):
                return False
            # return False
            print(type(data))
            index = 0
            for val in data:
                if (index != 0):
                    print("#######################")
                    Studentname = data[index]['Studentname']
                    Studentcode = data[index]['StudentID']
                    cgpa = data[index]['CGPA']
                    level = data[index]['StudentLevel']
                    StudentStatusID = data[index]['StudentStatusID']
                    std = student.search([('student_code', '=', Studentcode)], limit=1)
                    StudentStatus_id = hue_std_status.search([('d_id', '=', StudentStatusID)], limit=1).id
                    levelID = hue_levels.search([('d_id', '=', level)], limit=1).id
                    if std:
                        std.write({'cgpa': cgpa})
                        std.partner_id.write({'cgpa': cgpa})

                index += 1