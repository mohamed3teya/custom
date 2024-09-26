from odoo import models, fields, api

class HueInstallments(models.Model):
    _name = 'hue.installments'
    _description = 'hue.installments'
    
    name = fields.Char()
    installments = fields.Integer()
    years_id = fields.Many2one('hue.years')
    term_id = fields.Many2one('hue.global.terms', string='Global Term')
    one_time = fields.Boolean()
    extra_inv = fields.Boolean(default=False)
    foreign_nationality = fields.Boolean()
    special_case = fields.Boolean()
    currency = fields.Many2one('res.currency', string='Currency')
    
    @api.model_create_multi
    def create(self, values):
        hue_years = self.env['hue.years']
        hue_joining_years = self.env['hue.joining.years']
        hue_faculties = self.env['hue.faculties']
        rec = super(HueInstallments, self).create(values)
        values = values[0]
        year_name = hue_years.search([('id','=',values['years_id'])],limit=1).name
        join_year = hue_years.search([('id','=',values['years_id'])],limit=1).join_year
        faculty = hue_years.search([('id','=',values['years_id'])],limit=1).faculty
        join_year_name = hue_joining_years.search([('id','=',join_year.id)],limit=1).name
        faculty_name = hue_faculties.search([('id','=',faculty.id)],limit=1).name
        product = self.env['product.product']
        product.create({'installments_id':rec.id,'faculty_id':faculty.id,'type':'service','list_price':values['installments'],'standard_price':values['installments'],'name':values['name']+' / '+year_name+' / '+join_year_name+' / '+faculty_name})
        return rec

class ProductData(models.Model):
    _inherit = 'product.product'
    
    installments_id = fields.Many2one('hue.installments')
    faculty_id = fields.Many2one('hue.faculties')
    academic_id = fields.Many2one('op.academic.year')
    discount_id = fields.Many2one('hue.discounts')
    join_year = fields.Many2one('hue.joining.years', string='Join Year')
    active_disount= fields.Boolean()
    event_ticket = fields.Boolean()