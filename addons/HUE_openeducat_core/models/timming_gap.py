from odoo import models, fields, api


class HueJoiningYears(models.Model):
    _name = 'hue.timing.gap'
    _description = 'hue.timing.gap'
	
    gap = fields.Integer("Timing Gap", readonly=True, compute="_compute_gap")
    summer = fields.Boolean(string="Summer Timimg")	
    country_id = fields.Many2one('hue.nationalities', 'Country')
    
    
    @api.depends('summer')
    def _compute_gap(self):
        for x in self:
            if x.summer:
                x.gap = 2
            else:
                x.gap = 2