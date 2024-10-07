# -*- coding: utf-8 -*-
from odoo import api, fields, models


class RegistrationByLevelWizard(models.TransientModel):
    _name = "registration.level.wizard"
    _description = "Registration By Level"

    course_id = fields.Many2one('op.course', domain="[('id', 'in', suitable_course_ids)]")
    suitable_course_ids = fields.Many2many('op.course', compute='_compute_suitable_course_ids')
    batch_id = fields.Many2one('op.batch', domain="[('id', 'in', suitable_batch_ids)]")
    suitable_batch_ids = fields.Many2many('op.batch', compute='_compute_suitable_course_ids')
    subject_id = fields.Many2one('op.subject', domain="[('id', 'in', suitable_subject_ids)]")
    suitable_subject_ids = fields.Many2many('op.subject', compute='_compute_suitable_subject_ids')
    show_std = fields.Boolean('Show Student Not Registered Yet !')
    show_missing = fields.Boolean('Show Missing Sessions !')


    @api.onchange('course_id')
    def _compute_suitable_course_ids(self):
        for rec in self:
            courses = []
            subjects = []
            batches = self.env['op.batch'].sudo().search([])        
            if self.env.ref('HUE_openeducat_core.group_service_manager') in self.env.user.groups_id:
                batches = self.env['op.batch'].sudo().search([('course_id', '=', rec.course_id.id)])
                courses = self.env['op.course'].search([]).ids   #('id', '!=', 15)
            else:
                emp = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)])
                if not emp:
                    emp = self.env.user.employee_id
                courses = emp.course_ids.ids
                # for i in courses:
                #     if i == 15 :
                #         all_courses = courses.remove(15)
                # if self.env.ref('hue_timetable.group_timetable_user') in self.env.user.groups_id :
                #     batches = self.env['op.batch'].sudo().search([('course_id', '=', rec.course_id.id),('intern_batch', '!=', True)])
                # elif self.env.ref('hue_timetable.group_timetable_reports') in self.env.user.groups_id :
                #     batches = self.env['op.batch'].sudo().search([('course_id', '=', rec.course_id.id),('intern_batch', '!=', True)])
                # elif self.env.ref('__export__.res_groups_128_be2a877a') in self.env.user.groups_id :
                #     batches = self.env['op.batch'].sudo().search([('course_id', '=', self.course_id.id),('intern_batch', '=', True)])
                # else :
                batches = self.env['op.batch'].sudo().search([('course_id', '=', rec.course_id.id)])

            # domain = {'course_id': [('id', 'in', courses)] , 'batch_id': [('id', 'in', batches.ids)]}
            # return {'domain': domain}
            rec.suitable_course_ids = courses
            rec.suitable_batch_ids = batches.ids

    @api.onchange('batch_id')
    def _compute_suitable_subject_ids(self):
        for rec in self:
            subject_ids = []
            for course_subject in rec.batch_id.sudo().subject_registration_ids:
                if course_subject.sudo().subject_id.id not in subject_ids:
                    subject_ids.append(course_subject.sudo().subject_id.id)
            rec.suitable_subject_ids = subject_ids
            # domain = {'subject_id': [('id', 'in', subject_ids)]}
            # return {'domain': domain}

    def check_report(self):
        data = {'form': self.read(['course_id', 'batch_id', 'subject_id','show_missing'])[0]}
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['course_id', 'batch_id', 'subject_id','show_missing'])[0])
        return self.env.ref('hue_register.action_registration_by_level_report').report_action(self, data=data, config=False)

