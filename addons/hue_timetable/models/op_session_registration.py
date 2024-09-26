from odoo import models, fields, api
import requests
import json
import ldap3
from ldap3 import Server, Connection, ALL, NTLM


class OpSessionRegistration(models.Model):
    _name = 'op.session.registration'
    _description = 'op.session.registration'
    _inherit = ['mail.thread']
    _token = None
    
    
    active = fields.Boolean(default=True)
    name = fields.Char(compute='_compute_name', string='Name', store=False)
    course_id = fields.Many2one('op.course', readonly=False)
    subject_id = fields.Many2one('op.subject', readonly=False)
    batch_id = fields.Many2one('op.batch', readonly=False)
    session_type = fields.Selection([('Lecture', 'Lecture'), ('Section', 'Section'), ('Lab', 'Lab')], 'Type',default='Lecture')
    enrollment_ids = fields.One2many('op.session.registration.enrollment', 'registration_enrollment_id','Session Registration Enrollment', copy=True)
    graph_group_id = fields.Char()
    sub_classroom = fields.Integer('Section', tracking=True)
    exam_block = fields.Boolean(tracking=True)
    classroom_id = fields.Many2one('op.classroom', 'Group', readonly=True)
    facility_id = fields.Many2one('op.facility', 'Facility', tracking=True, required=True)
    owners = fields.Many2many('hr.employee')
    exam_id = fields.Many2one('op.exam', compute='_compute_exam', store=True, readonly=True)
    exam_date = fields.Date('Exam Date', compute='_compute_exam_date', store=True, readonly=True)
    teams_member_count = fields.Integer(readonly=True)
    session_parent_id = fields.Many2one('op.session.registration', string='Parent Session', index=True, ondelete='cascade')
    relative_session_ids = fields.One2many('op.session.registration', 'session_parent_id', string='Related Session')
    session_sync_type = fields.Selection([('team', 'Team'), ('channel', 'Channel')], 'Sync Type', default='team')
    graph_channel_id = fields.Char()
    status = fields.Selection([('active', 'Active'), ('inactive', 'Inactive')])
    
    @api.depends('subject_id','session_type','sub_classroom')
    def _compute_name(self):
        for session in self:
            if session.subject_id:
                if session.session_type != 'Lecture':
                    session.name = str(session.classroom_id.name) + '' + str(session.sub_classroom)
                else:
                    if session.classroom_id:
                        session.name = str(session.course_id.section) + '-' + session.sudo().subject_id.name.split('|')[0] + '-' + session.classroom_id.name
                    else:
                        session.name = str(session.course_id.section) + '-' + session.sudo().subject_id.name.split('|')[0] 
            else:
                session.name = False
                
    @api.onchange('course_id')
    def onchange_course_id(self):
        batches = self.env['op.batch'].sudo().search([('course_id', '=', self.course_id.id)])
        domain = {'batch_id': [('id', 'in', batches.ids)]}
        return {'domain': domain}

    @api.depends('subject_id', 'batch_id')
    def _compute_exam(self):
        subject_id = self.subject_id.id
        batch_id = self.batch_id.id
        exam = self.env['op.exam'].sudo().search([('subject_id', '=', subject_id), ('batch_id', '=', batch_id)],limit=1)
        self.exam_id = exam.id


    @api.depends('subject_id', 'batch_id')
    def _compute_exam_date(self):
        subject_id = self.subject_id.id
        batch_id = self.batch_id.id
        exam = self.env['op.exam'].sudo().search([('subject_id', '=', subject_id), ('batch_id', '=', batch_id)],limit=1)
        if exam.start_time:
            self.exam_date = exam.start_time.split('|')[0]
                
                
    # @api.onchange('exam_block')
    # def onchange_exam_block(self):
    #     for student in self.student_ids:
    #         student.exam_block = self.exam_block
 

    