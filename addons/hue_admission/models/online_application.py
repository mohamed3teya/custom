from datetime import datetime
from dateutil.relativedelta import relativedelta
import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class OnlineApplication(models.Model):
    _name = 'online.application'
    _inherit = 'mail.thread'
    _rec_name = 'arabic_name'
    _description = "Online Application"

    arabic_name = fields.Char('Arabic Name')
    english_name = fields.Char('English Name')
    application_faculty_ids = fields.One2many('online.application.faculties','application_id','Applications Faculties')


class OnlineApplicationFaculties(models.Model):
    _name = 'online.application.faculties'
    _description = "Online Application Faculties"
    
    app_faculty_id = fields.Many2one('hue.faculties', 'Faculties')
    application_id = fields.Many2one('online.application', 'Application' , ondelete='cascade')