from odoo import fields, models

class ResultsPublishTypes(models.Model):
    _name = 'op.resultspublishtypes'
    _description = 'Add Publish Results Types'
    
    name = fields.Char('Name')
    

class BlockResult(models.Model):
    _name = 'op.blockresult'
    _description = 'Add Block Reasons'
    
    name = fields.Char('Name')