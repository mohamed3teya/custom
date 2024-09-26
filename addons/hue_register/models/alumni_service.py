from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging
from datetime import datetime

class AlumniService(models.Model):
    _name = 'hue.alumni.service'
    _description = 'hue.alumni.service'
    _inherit = ['mail.thread']

    course_id = fields.Many2one('op.course' ,required=True , tracking=True)
    service_id = fields.Many2one('hue.service',required=True)
    alumni_academicyear_id = fields.Many2one('op.academic.year')
    alumni_semester_id = fields.Many2one('op.semesters')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'),('done', 'Done')],
                                 string='State', required=True, default='draft', tracking=True)
    
   
    @api.constrains('course_id','alumni_academicyear_id','alumni_semester_id','service_id')
    def _check_date(self):
        domain = [
            ('course_id', '=', self.course_id.id),
            ('alumni_academicyear_id', '=', self.alumni_academicyear_id.id),
            ('alumni_semester_id', '=', self.alumni_semester_id.id),
            ('service_id', '=', self.service_id.id),
            ('id', '!=', self.id),
        ]
        course_service = self.search(domain)         
        if course_service:
            raise ValidationError(('You can not have 2  service in the same academic year and semester!'))
        

    def create_service(self):
        students = self.env['op.student'].sudo().search(['|',('student_status', '=', 48),('student_status', '=', 55),
                 ('course_id', '=', self.course_id.id),('alumni_academicyear_id', '=', self.alumni_academicyear_id.id),('alumni_semester_id', '=', self.alumni_semester_id.id)])
        for std in students:
            service_std_data = self.env['hue.student.service'].sudo().search([('student_id', '=', std.id),
                ('service_id', '=', self.service_id.id)])
            if not service_std_data  :    
                service_data = self.env['hue.student.service'].sudo().create({
                            'student_id': std.id,
                            'service_id':self.service_id.id,
                            'academic_year_id': self.service_id.academic_years.id,
                            'semester_id':self.service_id.semester_id.id,
                            'alumni_academic_year_id': self.alumni_academicyear_id.id,
                            'alumni_semester_id':self.alumni_semester_id.id,
                            'count':1,
                            'state':'draft',
                            })
        self.write({'state': 'confirm'})
                
        
            
    def create_invoice(self):
        students = self.env['op.student'].sudo().search(['|',('student_status', '=', 48),('student_status', '=', 55),
                 ('course_id', '=', self.course_id.id),('alumni_academicyear_id', '=', self.alumni_academicyear_id.id)
                 ,('alumni_semester_id', '=', self.alumni_semester_id.id)],limit=500 , offset=100, order="student_code")
    
        for std in students :
            _logger.info('***********AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA****')
            _logger.info(std.student_code)
            invoice_data = self.env['account.move'].sudo().create({
                'academic_term':self.service_id.semester_id.term_id.id,
                'invoice_type':'miscellaneous',
                'currency_id' : 77,
                'account_id': std.partner_id.property_account_receivable_id.id,
                'move_type': 'out_invoice',
                'ref': False,
                'faculty':std.faculty.id,
                'student_code':std.student_code,
                'academic_year':self.service_id.academic_years.id,
                'invoice_date_due':datetime.now(),
                'date_invoice':datetime.now(),
                'partner_id':std.partner_id.id,
                'state': 'draft'
                })
            account_id = False
            product = self.service_id.product_id
            if product.id:
                account_id = product.categ_id.property_account_income_categ_id.id
            if not account_id:
                account_id = product.property_account_income_id.id
            if not account_id:
                raise UserError(
                    _('There is no income account defined for this product: "%s". \
                       You may have to install a chart of account from Accounting \
                       app, settings menu.') % (product.name,))
            
            invoice_line_data = self.env['account.move.line'].sudo().create({
                            'name': product.name,
                            'account_id':account_id,
                            'price_unit':product.list_price,
                            'quantity':1,
                            # 'uom_id':1,
                            'move_id':invoice_data.id,
                            'product_id':product.id
                            })
            _logger.info('***********BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB****')
            service_std_data = self.env['hue.student.service'].sudo().search([('student_id', '=', std.id),
                ('service_id', '=', self.service_id.id)])
            service_std_data.write({'state': 'done'})
            service_std_data.write({'inv_data': invoice_data.id})
            _logger.info('***********ccccccccccccccccccccccccccccccccc****')
        self.write({'state': 'done'})