from odoo import models, fields


class PresidentCompany(models.Model):
    _inherit = 'res.company'

    university_president = fields.Char()
    vice_university_president = fields.Char()
    head_alumni_affairs = fields.Char()
    head_admission_registration = fields.Char()