# -*- coding: utf-8 -*-
import time
from odoo import api, models


class RegularStudentsReport(models.AbstractModel):
    _name = 'report.hue_student_reports.report_regular_students'
    _description = "Regular Students Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        students = self.env['op.student'].sudo().search([],order="course_id asc")
        print("students_", students)
        docs = {}
        docargs = {
            'docs': docs,
            'students': students,
        }
        return docargs

    
    