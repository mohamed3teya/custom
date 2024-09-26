from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class TransportStudent(models.Model):
    _name = 'hue.student.transport'
    _description = 'Student Transport'
    _inherit = ['mail.thread']

    student_id = fields.Many2one('op.student' ,string='Student' ,required=True)
    line = fields.Many2one('hue.transport', string='Line Name', required=True)
    acadyears = fields.Many2one('op.academic.year',string='Academic Year', readonly=True, required=True)  # joining
    semesters = fields.Many2one('op.semesters',string='Semester', readonly=True, required=True)    
    student_code = fields.Integer(related='student_id.student_code', readonly=True, store=True)
    faculty = fields.Many2one(related='student_id.faculty', readonly=True, store=True)
    level = fields.Many2one(related='student_id.level', readonly=True, store=True)
    printed = fields.Boolean()
    printed_date = fields.Datetime(readonly=True)
    printed_count = fields.Integer(readonly=True)
    inv_data = fields.Char(string='Invoice ID')
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')],
                string='State', required=True, default='draft', tracking=True)
    inv_state = fields.Char(string='Invoice State', compute='call_invoice' , store =True)
    

    @api.depends('inv_data')
    def call_invoice(self):
        self.inv_state = ''
        invoice = self.env['account.move'].search([('id', '=', self.inv_data)], limit=1)
        if invoice.state == 'draft':
            self.inv_state = 'Draft'
        if invoice.payment_state == 'paid':
            invoice = self.env['account.move'].search([('origin', '=', invoice.number)], limit=1)
            if invoice:
                self.inv_state = 'Cancel'
            else:
                self.inv_state = 'Paid'
        if invoice.state == 'posted':
            self.inv_state = 'Open'      
        return invoice.state


    def button_done(self):
        invoice_data = self.env['account.move'].sudo().create({
            'academic_term':self.semesters.term_id.id,
            'invoice_type':'bus',
            'currency_id' : 77,
            'account_id': self.student_id.partner_id.property_account_receivable_id.id,
            'move_type': 'out_invoice',
            'ref': False,
            'faculty':self.student_id.faculty.id,
            'student_code':self.student_id.student_code,
            'academic_year':self.acadyears.id,
            'invoice_date_due':self.semesters.term_id.term_start_date,
            'date_invoice':self.semesters.term_id.term_start_date,
            'partner_id':self.student_id.partner_id.id,
            'state': 'draft'
            })
            
        account_id = False
        product = self.line.product_id
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
        print(invoice_data.id)
        print('55555555555555555555555555555555555')
        for rec in self:
            rec.write({'state': 'done'})
            rec.write({'inv_data': invoice_data.id})
            # rec.write({'inv_state': 'draft'})
            
            
    @api.constrains('student_id','acadyears','semesters')
    def _check_date(self):
        domain = [
            ('student_id', '=', self.student_id.id),
            ('acadyears', '=', self.acadyears.id),
            ('semesters', '=', self.semesters.id),
            ('id', '!=', self.id),
        ]
        std_transport = self.search(domain)         
        if std_transport:
            raise ValidationError(('You can not have 2  transportation line in the same academic year and semester!'))
        
        
    def unlink(self): 
        for rec in self:
            if rec.inv_state == 'Paid':
                raise ValidationError(("Can't delete paid invvoice state."))
        res = super(TransportStudent, self).unlink()
        return res
    
    
    @api.model
    def invoice_state_cron(self):
        curr_semester = self.env['op.semesters'].sudo().search([('enroll_semester', '=', True)], limit=1).id
        curr_academic_year = self.env['op.semesters'].sudo().search([('enroll_semester', '=', True)], limit=1).term_id.term_id.id
        student_transporte_invoice = self.env['hue.student.transport'].search([('acadyears','=',curr_academic_year),('semesters','=',curr_semester)])
        
        for invoice in student_transporte_invoice :
            inv_state = self.env['account.move'].search([('id', '=', invoice.inv_data),('student_code', '=', invoice.student_id.student_code)])
            inv = False
            if inv_state.state == 'paid':
                inv = self.env['account.move'].search([('origin', '=', inv_state.number)], limit=1)
            if inv:
                invoice.write({'inv_state': 'cancel'})
            else:
                invoice.write({'inv_state': inv_state.state})
    
    
    @api.model
    def service_invoice_state_cron(self):
        curr_semester = self.env['op.semesters'].sudo().search([('enroll_semester', '=', True)], limit=1).id
        curr_academic_year = self.env['op.semesters'].sudo().search([('enroll_semester', '=', True)], limit=1).term_id.term_id.id
        student_service_invoice = self.env['hue.student.service'].search([('academic_year_id','=',curr_academic_year),('semester_id','=',curr_semester)])
        
        for invoice in student_service_invoice :
            inv_state = self.env['account.move'].search([('id', '=', invoice.inv_data),('student_code', '=', invoice.student_id.student_code)])
            inv = False
            if inv_state.state == 'paid':
                inv = self.env['account.move'].search([('origin', '=', inv_state.number)], limit=1)
            if inv:
                invoice.write({'inv_state': 'cancel'})
            else:
                invoice.write({'inv_state': inv_state.state})
                

class Transportation(models.Model):
    _name = 'hue.transport'
    _description = 'hue.transport'
    _inherit = ['mail.thread']
    _rec_name = 'line_ar_name'


    line_name = fields.Char( string='Line Name', required=True)
    line_ar_name = fields.Char( string='Line Arabic Name', required=True)
    line_code = fields.Integer( string='Line Code', required=True)
    product_id = fields.Many2one('product.product', 'Product', required=True)
    academic_years = fields.Many2one('op.academic.year', string='Academic Year', required=True)  
    semester_id = fields.Many2one('op.semesters', string='Semester', required=True)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')],
                                 string='State', required=True, default='draft', tracking=True)
    active = fields.Boolean('Active',default=True)
    
    def name_get(self):
        res =[]
        for rec in self:
            line_ar_name = str(rec.line_code) +'_'+ rec.line_ar_name
            res.append((rec.id , line_ar_name))
        return res