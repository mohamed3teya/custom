from odoo import fields, models, api
from odoo.exceptions import ValidationError


class SubjectRegistration(models.Model):
    _name= 'hue.subject.registration'
    _description = 'hue.subject.registration'
    
    batch_id = fields.Many2one('op.batch', string='Batch',ondelete='restrict')
    groups_count = fields.Integer(string='Groups')
    lecture_hours = fields.Float(string='Lect. Hrs')
    practical_count = fields.Integer(string='Practical/group')
    practical_hours = fields.Float(string='Pract. Hrs')
    section_hours = fields.Float(string='Sec. Hrs')
    sections_count = fields.Integer(string='Sections/group')
    subject_id = fields.Many2one('op.subject', string='Subject',required=True, domain="[('id', 'in', suitable_subject_ids)]")
    suitable_subject_ids = fields.Many2many('op.subject', compute='_compute_suitable_subject_ids')
    subject_level = fields.Many2one('op.levels', string='Level',compute="_compute_subject_level")
    
    
    #Add domain to subjects
    @api.depends('batch_id')
    def _compute_suitable_subject_ids(self):
        for m in self:
            m.suitable_subject_ids = False
            m.suitable_subject_ids = self.env['op.subject'].search([])
            if m.batch_id:
                course_id = m.batch_id.course_id
                subject_ids = self.env['op.subject'].search([('course_id','=',course_id.id)])
                m.suitable_subject_ids = subject_ids.ids
    
    
    @api.depends('subject_id', 'batch_id')
    def _compute_subject_level(self):
        for rec in self:
            if rec.batch_id and rec.subject_id:
                course_subject = self.env['op.subject'].search(
                    [('course_id', '=', rec.batch_id.course_id.id), ('id', '=', rec.subject_id.id)], limit=1)
                rec.subject_level = course_subject.subject_level.id
            else:
                rec.subject_level = ""


    @api.onchange('subject_id')
    def onchange_subject_id(self):
        if self.batch_id:
            course_subjects = self.env['op.subject'].search([('course_id', '=', self.batch_id.course_id.id)])
            subject_list = []
            if course_subjects:
                for course_subject in course_subjects:
                    if course_subject.id not in subject_list:
                        subject_list.append(course_subject.id)
                        print("3333333333333333333333333333333333333333333333333333333333333333333333333333")
                        print(course_subject.subject_level)
                        if self.subject_id.id == course_subject.id:
                            self.lecture_hours = course_subject.subject_lecturehours
                            self.practical_hours = course_subject.subject_practhours
                            self.section_hours = course_subject.subject_oralhours
                            self.subject_level = course_subject.subject_level.id
         
            
    @api.constrains('subject_id')
    def _check_subject(self):
        for rec in self:
            domain = [
                ('subject_id', '=', rec.subject_id.id),
                ('batch_id', '=', rec.batch_id.id),
                ('id', '!=', rec.id),
            ]
            std_subj = rec.search(domain)         
            if std_subj:
                raise ValidationError(('You can not have 2  record  of the same subject ! "' + rec.subject_id.name + ' " '))
