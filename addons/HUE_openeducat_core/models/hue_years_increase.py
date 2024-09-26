from odoo import models, fields, api

class HueYearsIncrease(models.Model):
     _name = 'hue.years.increase'
     _description = 'hue.years.increase'
     _inherits = {'product.product': 'product_id'}
     
     sequence = fields.Integer(required=True)
     year_id = fields.Many2one('hue.years',required=True)
     increase_percentage = fields.Float(required=True)
     foreign_nationality = fields.Boolean(default=False)
     special_case = fields.Boolean(default=False)
     increase_type =  fields.Selection([ ('percentage', 'Percentage'),('amount', 'Amount')],'Type', default='percentage')
     amount = fields.Float()
     product_id = fields.Many2one('product.product', required=True, ondelete='cascade')
     
     
     @api.model_create_multi
     def create(self, vals):
          res = super(HueYearsIncrease, self).create(vals)
          if res.increase_type == 'percentage':
               if res.foreign_nationality:
                    print(res.year_id.total_dollar)
                    increase_percentage = ((res.year_id.total_dollar*res.increase_percentage)/100)
               else:
                    increase_percentage = ((res.year_id.total*res.increase_percentage)/100)
          elif res.increase_type == 'amount':
               increase_percentage = res.amount
               
          res.update({
               'type': 'service',
               'purchase_ok':False, 
               'lst_price':increase_percentage/2,
               'standard_price':increase_percentage/2,
          })
          return res