
import calendar
import pytz
import time
from datetime import datetime
from odoo import models, api, _, fields, tools


class StudentPasswordReport(models.AbstractModel):
    _name = "report.hue_student_reports_yasmin.student_password_view"
    _description = "student password Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        student = self.env['op.student'].sudo().search([('id', '=',docs.student_id.id)]) 
       
        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'docs': docs,
            'students':student,
        }
        return docargs
