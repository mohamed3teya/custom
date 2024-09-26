from odoo import models, fields, api, _
import logging


_logger = logging.getLogger(__name__)


class HueDiscounts(models.Model):
    _name = 'hue.discounts'
    _description = 'Horus discounts'


    name = fields.Char()
    dataa = fields.Selection([('percent', 'Percentage'),('amount', 'Amount')], string='Discount Type',required=True)
    certificate_id = fields.Many2many('hue.certificates', string="Certificate")
    nationality_id = fields.Many2many('hue.nationalities', string="Nationality")
    join_year_id = fields.Many2one('hue.joining.years', string="Join Year",required=True)
    faculty_ids = fields.Many2one('hue.faculties', string="Faculties Data",required=True)
    course_id = fields.Many2one('op.course', string='course')
    cgpa_from = fields.Float(string="CGPA From")
    cgpa_to = fields.Float(string="CGPA To")
    percentage_from = fields.Float(string="Percentage From")
    percentage_to = fields.Float(string="Percentage To")
    discount_rate = fields.Float(string="Discount Amount",required=True)
    scholarship = fields.Selection([(str(num), ('Partial '+ str(num)+ ' %') if num<100 else 'Full') for num in range(5,102,5)], string='Discount Type')
    mc = fields.Boolean()
    staff_discount = fields.Boolean(string="Staff Discount")
    sibling_discount = fields.Boolean(string="Sibling Discount")
    syndicate_discount = fields.Boolean(string="Syndicate Discount")
    martyrs_discount = fields.Boolean(string="Martyrs Discount")
    active = fields.Boolean(default=True)
    

    @api.model_create_multi
    def create(self,values):
        academic_years = self.env['op.academic.year']
        hue_years = self.env['hue.years']
        rec = super(HueDiscounts, self).create(values)
        values = values[0]
        academic_year_id = academic_years.search([('id','=',values['join_year_id'])],limit=1).id
        faculty_ids = self.env['hue.faculties'].search([('id','=',values['faculty_ids'])],limit=1).id
        if 'course_id' in values:
            fin_total = hue_years.search([('join_year','=',values['join_year_id']),('course_id','=',values['course_id']),('faculty','=',values['faculty_ids'])],limit=1).total
        else:
            fin_total = hue_years.search([('join_year', '=', values['join_year_id']),
                ('faculty', '=', values['faculty_ids'])], limit=1).total
        if values['dataa'] =='percent':
            total = (fin_total * values['discount_rate'])/100
        else :
            total = values['discount_rate']
            
        product = self.env['product.product']
        product.create({'discount_id':rec.id,'join_year':values['join_year_id'],'academic_id':academic_year_id,'type':'service','faculty_id':faculty_ids,'list_price':total,'standard_price':total,'name':values['name']})
        return rec
    
    
    def write(self, values):
        academic_years = self.env['op.academic.year']
        hue_years = self.env['hue.years']
        product = self.env['product.product']
        rec = super(HueDiscounts, self).write(values)
        values = values[0]
        discount_id = product.search([('discount_id','=',self.id)],limit=1)
        try:
            name = values['name']
        except KeyError:
            name = self.name
        try:
            faculty_ids = values['faculty_ids']
        except KeyError:
            faculty_ids = self.faculty_ids.id
        try:
            course_id = values['course_id']
        except KeyError:
            course_id = self.course_id.id
        try:
            join_year_id = values['join_year_id']
        except KeyError:
            join_year_id = self.join_year_id.id
        try:
            discount_rate = values['discount_rate']
        except KeyError:
            discount_rate = self.discount_rate
        try:
            scholarship = values['scholarship']
        except KeyError:
            scholarship = self.scholarship
        try:
            dataa = values['dataa']
        except KeyError:
            dataa = self.dataa
        if discount_id:
            academic_year_id = academic_years.search([('id','=',join_year_id)],limit=1).id
            faculty_ids = self.env['hue.faculties'].search([('id','=',faculty_ids)],limit=1).id
            if course_id:
                if scholarship == False:
                    fin_total = hue_years.search([('join_year','=',join_year_id),('course_id','=',course_id),('faculty','=',faculty_ids)],limit=1).total
                else:
                    fin_total = hue_years.search([('join_year','=',join_year_id),('course_id','=',course_id),('scholarship','=',True),('faculty','=',faculty_ids)],limit=1).total
            else:
                if scholarship == False:
                    fin_total = hue_years.search([('join_year', '=', join_year_id), ('faculty', '=', faculty_ids)],limit=1).total
                else:
                    fin_total = hue_years.search([('join_year', '=', join_year_id), ('faculty', '=', faculty_ids),('scholarship','=',True)],limit=1).total
            if dataa =='percent':
                total = (fin_total * discount_rate)/100
            else :
                total = discount_rate
            discount_id.write({'academic_id':academic_year_id,'join_year':join_year_id,'type':'service','faculty_id':faculty_ids,'list_price':total,'standard_price':total,'name':name})
            return rec
        else:
            academic_year_id = academic_years.search([('id','=',join_year_id)],limit=1).id
            faculty_ids = self.env['hue.faculties'].search([('id','=',faculty_ids)],limit=1).id
            if course_id:
                fin_total = hue_years.search([('join_year','=',join_year_id),('course_id','=',course_id),('faculty','=',faculty_ids)],limit=1).total
            else:
                fin_total = hue_years.search([('join_year', '=', join_year_id), ('faculty', '=', faculty_ids)],limit=1).total
            if dataa =='percent':
                total = (fin_total * discount_rate)/100
            else :
                total = discount_rate
            product.create({'discount_id':self.id,'join_year':join_year_id,'academic_id':academic_year_id,'faculty_id':faculty_ids,'type':'service','list_price':total,'standard_price':total,'name':name})
            return rec
        return False
    
    
    def unlink(self):
        product = self.env['product.product']
        discount_id = product.search([('discount_id','=',self.id)],limit=1)
        if discount_id:
            discount_id.unlink()
        campus_unlink = super(HueDiscounts,self).unlink()
        return campus_unlink
    
    
    def generate_discount(self, cr, context=None):
        self.ensure_one()
        IfExistSQL =('select * from op_student where id in (' + ','.join(map(str, self.faculty_ids.ids)) + ')')
        #("select * from op_student  where join_year = '"+ str(self.join_year_id.id)+"'  AND faculty IN (" + ",".join(map(str, self.faculty_ids.ids)) + "))
        #self.env.cr.execute(IfExistSQL)
        #students =self.env.cr.dictfetchall()
        if self.nationality_id.ids:
            nationality_prams = ('student_nationality', 'in', self.nationality_id.ids)
        else:
            nationality_prams = ('student_nationality', '!=', False)
        if self.certificate_id.ids:
            certificates_prams = ('student_certificates', 'in', self.certificate_id.ids)
        else:
            certificates_prams = ('student_certificates', '!=', False)
        if self.percentage_from:
            percentage_from_prams = ('percentage', '>=', self.percentage_from)
        else:
            percentage_from_prams = ('percentage', '!=', False)
        if self.percentage_to:
            percentage_to_prams = ('percentage', '<=', self.percentage_to)
        else:
            percentage_to_prams = ('percentage', '!=', False)
        if self.cgpa_from:
            cgpa_from_prams = ('cgpa', '>=', self.cgpa_from)
        else:
            cgpa_from_prams = ('cgpa', '!=', False)
        if self.cgpa_to:
            cgpa_to_prams = ('cgpa', '<=', self.cgpa_to)
        else:
            cgpa_to_prams = ('cgpa', '!=', False)

        students = self.env['op.student'].search([cgpa_from_prams,cgpa_to_prams,nationality_prams,certificates_prams,percentage_from_prams,
                                                  percentage_to_prams,('join_year', '=', self.join_year_id.id), ('faculty', 'in', self.faculty_ids.ids)])
        invoice = self.env['account.move']
        invoice_line = self.env['account.move.line']
        product = self.env['product.product']
        product_data = product.search([('discount_id', '=', self.id)])
        for student in students:
            partner_id  = (student.partner_id)
            print("$$$$$$$$$$$$$$$$$$$$$$")
            print(student.id)
            print("$$$$$$$$$$$$$$$$$$$$$$")
            invoices_data_count = len(invoice.search([('partner_id', '=', partner_id.id),('invoice_type','=','regular'),('academic_year','=',product_data.academic_id.id)])._ids)
            invoices_data = invoice.search([('partner_id', '=', partner_id.id),('invoice_type','=','regular'),('academic_year','=',product_data.academic_id.id)])
            if invoices_data:
                for invoice_data in invoices_data:
                    price_unit = product_data.standard_price / invoices_data_count
                    invoice_line_data = invoice_line.create({'name':product_data.name,'account_id':self._uid,'price_unit':price_unit,'quantity':1,'move_id':invoice_data.id,'product_id':product_data.id})