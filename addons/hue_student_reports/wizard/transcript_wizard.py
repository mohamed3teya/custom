# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import datetime
from datetime import date, timedelta, datetime
import time
from dateutil import tz
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError


class StudentTranscriptWizardd(models.TransientModel):
    _name = "student.transcript.wizard"
    _description = "Student Transcript"

    student_status = fields.Many2one('hue.std.data.status' , required=True)
    student_id = fields.Many2one('op.student', string='Student', required=True, domain="[('id', 'in', suitable_student_ids)]")
    suitable_student_ids = fields.Many2many('op.student', compute='_compute_onchange_student_status')
    student_code = fields.Char(string='Student Code')
    report_type = fields.Selection([('transcript', 'Transcript'), ('status', 'Status'),('registration certificate','Registration certificate')], 'Report', default='transcript')
    language = fields.Selection([('ar', 'Arabic'), ('en', 'English')], 'Language')
    student_code_show = fields.Boolean(string='Show Code', default=True)
    title = fields.Boolean(string='Show Title', default=True)
    # logo = fields.Boolean(string='Show Logo', default=True)
    student_pic = fields.Boolean(string='Show Student Picture')
    course = fields.Boolean(string='Show Course', default=True)
    level = fields.Boolean(string='Show Level', default=True)
    national_id = fields.Boolean(string='Show National ID', default=True)
    nationality = fields.Boolean(string='Show Nationality', default=True)
    birthday = fields.Boolean(string='Show Birthday')
    birth_place = fields.Boolean(string='Show Birth Place')
    address = fields.Boolean(string='Show address')
    prev_cert = fields.Boolean(string='Show Previous Certificate')
    military = fields.Boolean(string='Show Military State')
    results = fields.Boolean(string='Show Results', default=True)
    to = fields.Char(string='Submitted To:')
    no_subjects = fields.Boolean(string='WithOut Subjects')
    notes = fields.Text(string='Notes')
    transferred = fields.Boolean()

    # date_from = fields.Date(string='Start Date')
    # date_to = fields.Date(string='End Date', default=fields.Date.today())
    # p_type = fields.Selection([('normal', 'No Action'),('allowance', 'Allowance'),('deduction', 'Deduction')], string='Payroll Type')
    # month_period = fields.Many2one('working.periods', string='Month')
    
    
    @api.onchange('student_status')
    def _compute_onchange_student_status(self):
        for rec in self:
            students = []
            rec.suitable_student_ids = False
            # rec.university_id = False
            # if self.env.ref('hr_extention.group_service_manager') in self.env.user.groups_id or self.env.ref('openeducat_core.group_op_back_office_admin') in self.env.user.groups_id or self.env.ref('openeducat_core.group_op_back_office') in self.env.user.groups_id :
            #     students = self.env['op.student'].sudo().search([('student_status', '=', rec.student_status.id)]).ids
            # else:
            emp = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)])
            fuc = self.env['op.faculty'].sudo().search([('emp_id', '=', emp.id)])
            if not emp:
                emp = self.env.user.employee_id
            courses = emp.course_ids.ids
            # if self.env.ref('hue_timetable.group_timetable_reports') in self.env.user.groups_id :
            students = self.env['op.student'].sudo().search([('student_status', '=', rec.student_status.id)]).ids  #,('course_id', 'in', courses)
            if fuc :
                for x in fuc:
                    hue_direction_lines = self.env['hue.academic.direction.line'].sudo().search([('student_id.student_status','=',rec.student_status.id),('faculty_id', '=', x.id), ('to_date', '=', None)])
                    for hue_direction_line in hue_direction_lines:
                        students.append(hue_direction_line.student_id.id)
            else :
                students = self.env['op.student'].sudo().search([('student_status', '=', rec.student_status.id)]).ids  #,('course_id', 'in', courses) Add this condition later                    
            rec.suitable_student_ids = students

        
    @api.onchange('student_code')
    def fiter_student_list(self):
        if self.student_code:
            self.student_id = self.env['op.student'].sudo().search([['student_code', '=', self.student_code]])


    # def check_report(self):
    #     print("11111111111111111111111111111111111111")
    #     data = {'form': self.read(['student_id', 'student_code', 'report_type', 'student_code_show', 'language',  'student_pic', 'course', 'level', 'national_id', 'nationality', 'birthday', 'birth_place', 'address', 'title', 'prev_cert', 'military', 'results', 'to', 'notes'])[0]}
    #     return self._print_report(data)


    def generate_report(self):
        data = {
            'form': self.read([
                'student_id', 'student_code', 'report_type', 'student_code_show', 'language', 'no_subjects',
                'student_pic', 'course', 'level', 'national_id', 'nationality', 'birthday',
                'birth_place', 'address', 'title', 'prev_cert', 'military', 'results', 'to', 'notes'
            ])[0]
        }
        print("Wizard_Data:---------", data)
        return self.env.ref('hue_student_reports.action_report_transcript').report_action(self, data=data, config=False)
    
    def check_progress(self):
        print("999999999999999999999999999999999999999999")
        data = {'form': self.read(['student_id', 'student_code',  'report_type', 'student_code_show', 'language', 'student_pic', 'course', 'level', 'national_id', 'nationality', 'birthday', 'birth_place', 'address', 'title', 'prev_cert', 'military', 'results', 'to', 'notes'])[0]}
        return self.env.ref('hue_student_reports.action_report_student_transcript_progress').report_action(self, data=data, config=False)
    
    def check_report_data(self):
        data = {'form': self.read(['student_id'])[0]}
        return self.env.ref('hue_student_reports.action_students_adviser_data_report').report_action(self, data=data, config=False)