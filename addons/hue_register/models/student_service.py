from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class StudentService(models.Model):
    _name = 'hue.student.service'
    _description = 'hue.student.service'
    _inherit = ['mail.thread']
    _rec_name = 'student_id'

    student_id = fields.Many2one('op.student' ,required=True , tracking=True)
    service_id = fields.Many2one('hue.service',required=True)
    category = fields.Char(compute="_category")
    academic_year_id = fields.Many2one('op.academic.year' , related='service_id.academic_years', required=True , store=True)
    semester_id = fields.Many2one('op.semesters', related='service_id.semester_id', required=True , store=True)
    student_code = fields.Integer(related='student_id.student_code', readonly=True, store=True)
    faculty = fields.Many2one(related='student_id.faculty', readonly=True, store=True)
    course = fields.Many2one(related='student_id.course_id', readonly=True, store=True)
    count = fields.Integer(default ="1")
    printed = fields.Boolean()
    printed_date = fields.Datetime(readonly=True)
    printed_count = fields.Integer(readonly=True)
    inv_data = fields.Char(string='Invoice ID')
    inv_date = fields.Datetime(string='Invoice Date')
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')],
                                 string='State', required=True, default='draft', tracking=True)
    inv_state = fields.Char(string='Invoice State', compute='call_invoice' , store =True)
    alumni_academic_year_id = fields.Many2one('op.academic.year', related='student_id.alumni_academicyear_id' , readonly=True)  
    alumni_semester_id = fields.Many2one('op.semesters' , related='student_id.alumni_semester_id' , readonly=True)  
    tree_clo_acl_ids = fields.Char()#compute="_compute_tree_clo_acl_ids", search='tree_clo_acl_ids_search'
     
    
    @api.depends('category')
    def _compute_tree_clo_acl_ids(self):
        print('View My Tree CLO ACL')
    
    def tree_clo_acl_ids_search(self, operator, operand):
        if self.env.ref('hr_extention.group_service_manager') in self.env.user.groups_id:
            categories = ['Alumni','Admission']
        elif  self.env.ref('__export__.res_groups_223_b4325ee4') in self.env.user.groups_id or self.env.ref('__export__.res_groups_224_d1c8b527') in self.env.user.groups_id:
            categories = ['Alumni']
        elif  self.env.ref('__export__.res_groups_225_0d2f06a7') in self.env.user.groups_id or self.env.ref('__export__.res_groups_226_18f43b34') in self.env.user.groups_id:
            categories = ['Admission']
        records = self.sudo().search([('service_id.category', 'in', categories)]).ids
        return [('id', 'in', records)]
   
   
    @api.depends('service_id')
    def _category(self):
        service_id = self.env['hue.service'].sudo().search([('id', '=', self.service_id.id)])
        self.category = service_id.category

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
            self.inv_state = 'posted'      
        return invoice.state
    
    # @api.onchange('service_id')
    # def onchange_service_id(self):
    #     for rec in self:
    #         if self.env.ref('hr_extention.group_service_manager') in self.env.user.groups_id :
    #             services = self.env['hue.service'].sudo().search([])
    #         elif  self.env.ref('__export__.res_groups_223_b4325ee4') in self.env.user.groups_id or self.env.ref('__export__.res_groups_224_d1c8b527') in self.env.user.groups_id:
    #             services = self.env['hue.service'].sudo().search([('category','=','Alumni')])
    #         elif  self.env.ref('__export__.res_groups_225_0d2f06a7') in self.env.user.groups_id or self.env.ref('__export__.res_groups_226_18f43b34') in self.env.user.groups_id:
    #             services = self.env['hue.service'].sudo().search([('category','=','Admission')])
    #         domain = {'service_id': [('id', 'in', services.ids)]}
    #         return {'domain': domain}
        

    def button_done(self):
        invoice_data = self.env['account.move'].sudo().create({
            'academic_term':self.semester_id.term_id.id,
            'invoice_type':'miscellaneous',
            # 'currency_id' : 77,
            'account_id': self.student_id.partner_id.property_account_receivable_id.id,
            'move_type': 'out_invoice',
            'ref': False,
            'faculty':self.student_id.faculty.id,
            'student_code':self.student_id.student_code,
            'academic_year':self.academic_year_id.id,
            'invoice_date_due':datetime.now(),
            'date_invoice':datetime.now(),
            'partner_id':self.student_id.partner_id.id,
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
                        'quantity':self.count,
                        # 'uom_id':1,
                        'move_id':invoice_data.id,
                        'product_id':product.id
                        })
        for rec in self:
            rec.write({'state': 'done'})
            rec.write({'inv_data': invoice_data.id})
            rec.write({'inv_date': invoice_data.date_invoice})
              
    def unlink(self): 
        for rec in self:
            if rec.inv_state == 'Paid':
                raise ValidationError(("Can't delete paid invoice state."))
        res = super(StudentService, self).unlink()
        return res