from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class Service(models.Model):
    _name = 'hue.service'
    _description = 'hue.service'
    _inherit = ['mail.thread']

    name = fields.Char(required=True , tracking=True)
    product_id = fields.Many2one('product.product', 'Product')
    amount = fields.Float(tracking=True)
    category = fields.Selection([('Admission', 'Admission'), ('Alumni', 'Alumni')])
    academic_years = fields.Many2one('op.academic.year', string='Academic Year', required=True, tracking=True)  
    semester_id = fields.Many2one('op.semesters', string='Semester', required=True, tracking=True)
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
        records = self.sudo().search([('category', 'in', categories)]).ids
        return [('id', 'in', records)]