from odoo import models, fields, api


class OpAdmissionRegister(models.Model):
    _inherit = 'op.admission.register'
    
    
    @api.model
    def get_admission_applicant(self,admission_register,type):
        return type
    
    
    product_id = fields.Many2one('product.product', string="Product")
    hue_admission_id = fields.Many2one('op.hue.admission', 'HUE Admission', required=True)
    state = fields.Selection([('draft','Draft'),('confirm','Confirmed'),('cancel','Cancelled'),
        ('application','Application Gathering'),('admission','Admission Process'),('done','Done')],
        string='Status',default='draft', tracking=True)
    identifier = fields.Char(string='Register Identifier',required=True,
        readonly=False if state=='draft' else True)
    admission_ids = fields.One2many(
        'op.admission.application', 'register_id', 'Admissions')