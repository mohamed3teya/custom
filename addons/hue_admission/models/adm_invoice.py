from odoo import fields, models, api

class HueAccountInvoice(models.Model):
    _inherit = 'account.move'
    
    invoice_type = fields.Selection([('regular','Regular'), ('one','One Time'),('bus','Buses'), ('hostel','Hostel'),('miscellaneous','Miscellaneous'),('summer','Summer'),('adjustment','Financial Adjustment'),('application','Application'),('intern','Intern')],string="Invoice Type",required=True)
    academic_term = fields.Many2one('op.academic.term', string='Academic Term')
    academic_year = fields.Many2one('op.academic.year', string='Academic Year')
    account_id = fields.Many2one('account.account', string='Account', help='The partner account used for this invoice.')
    amount_total_company_signed = fields.Monetary(string='Total in Company Currency',help='Total amount in the currency of the company, negative for credit notes.')
    comment = fields.Text(string='Additional Information')
    date_invoice = fields.Date(string='Invoice Date Keep empty to use the current date')
    deactive = fields.Boolean(string='Is deactive')
    dis_inv = fields.Boolean(string='Allow Discount')
    faculty = fields.Many2one('hue.faculties',store=True,related='partner_id.faculty')
    is_application = fields.Boolean(string='Is Application')
    join_year = fields.Many2one('hue.joining.years', string='Join Year',store=True,related='partner_id.join_year') 
    mc = fields.Boolean(string='MC',related='partner_id.mc')
    notes = fields.Char(string='Total Notes')
    number = fields.Char(string='Number')
    payment_move_line_ids = fields.Many2many('account.move.line',string='Payment Move Lines')
    portal_url = fields.Char(string='Portal Access URL',help='Customer Portal URL')
    refund_invoice_id = fields.Many2one('account.move',string='Invoice for which this invoice is the credit note')
    refund_invoice_ids = fields.One2many('account.move','refund_invoice_id',string='Refund Invoices')
    residual_company_signed = fields.Monetary(string='Amount Due in Company Currency', help='Remaining amount due in the currency of the company.')
    special_case = fields.Boolean(string='Special Case',store=True, readonly=True,related='partner_id.related_student.special_case') 
    student_code = fields.Integer(string='Student Code',store=False,related='partner_id.student_code')
    student_status = fields.Many2one('hue.std.data.status',string='Student Status',store=True,compute='_get_status')    
    
    @api.depends('student_code','academic_year' ,'academic_term')
    def _get_status(self):
        print("self1------------------",self)
        for inv in self:
            semester = self.env['op.semesters'].sudo().search([('term_id', '=', inv.academic_term.id)])	
            student_acc_status = self.env['op.student.accumlative.semesters'].sudo().search([('student_id.student_code', '=', inv.student_code),
                ('academicyear_id', '=', inv.academic_year.id) , ('semester_id', '=', semester.id)])
            if student_acc_status :
                inv.student_status = student_acc_status.semester_status.id
            else :
                std_status = self.env['op.student'].sudo().search([('student_code', '=', inv.student_code)])
                inv.student_status = std_status.student_status.id
    
    @api.depends('student_code')
    def _get_join_year(self):
        self.ensure_one()
        student = self.env['op.student'].sudo().search([('student_code', '=', self.student_code)])
        self.join_year = student.join_year.id
    
    def _get_default_access_token(self):
        return str(uuid.uuid4())
    
    def action_invoice_deactive(self):
        self.write({'deactive' :True})
        return True
    
    # def action_invoice_open(self): use action post instead
    #     invoice =  self.env['account.move']
    #     inv = invoice.search([('id','=',self.id)],limit=1)
    #     if inv:
    #         inv.write({'user_id':self._uid})
    #     to_open_invoices = self.filtered(lambda inv: inv.state != 'posted')	
    #     if to_open_invoices.filtered(lambda inv: inv.state != 'draft'):	
    #         raise UserError(_("Invoice must be in draft state in order to validate it."))
    #     if to_open_invoices.filtered(lambda inv: inv.amount_total < 0):
    #         raise UserError(_("You cannot validate an invoice with a negative total amount. You should create a credit note instead."))	
    #     to_open_invoices.action_date_assign()	
    #     to_open_invoices.action_move_create()
    #     return to_open_invoices.invoice_validate()

class HueAccountInvoiceLine(models.Model):
    _inherit = 'account.move.line'
    
    def _compute_invoice_type(self):
        print("self2------------------",self)
        for line in self:
            line.invoice_type=line.move_id.invoice_type
    
    academic_year  =  fields.Many2one('op.academic.year',store=True,related='move_id.academic_year')
    faculty  =  fields.Many2one('hue.faculties',store=True,related='move_id.faculty')
    invoice_type  =  fields.Selection([('regular', 'Regular'), ('one', 'One Time'),('bus', 'Buses'), ('hostel', 'Hostel'),('miscellaneous', 'Miscellaneous'),('summer', 'Summer'),('adjustment', 'Financial Adjustment'),('application', 'Application'),('intern', 'Intern') ],store=True,compute=_compute_invoice_type)
    partner_id  =  fields.Many2one('res.partner',store=True,related='move_id.partner_id')    
    
    
    
    
    
    
    
    
    
    