from odoo import fields, models,api
from datetime import date

class StudentStudyGroups(models.Model):
    _name = 'student.study.groups'
    _description = 'student.study.groups'
    
    course_id = fields.Many2one(related='study_group_id.course_id', store='true')
    index = fields.Integer()
    student_code = fields.Integer(related='student_id.student_code',store=True,string='Student Code')
    student_id = fields.Many2one('op.student',domain="[('course_id', '=', course_id)]", string='Student')
    study_group_id = fields.Many2one('op.classroom', ondelete='cascade',string='Study Group')
    sub_classroom = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'),
        ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8')], string="Team")
    
    @api.onchange('student_id')
    def onchange_student_id(self):
        for rec in self:
            students =[]
            all_students = self.env['op.student'].sudo().search(
                    [('course_id', '=', rec.study_group_id.course_id.id),('student_status', '=', 2)])
            for stud in all_students :
                invoice_count = 0
                if not stud.allow_registration:
                    domain = [('move_type', 'in', ['out_invoice']),
                              ('date_due', '<=', date.today()),
                              ('partner_id', '=', [stud.partner_id.id]),
                              ('state', 'in', ['draft','posted'])]
                    invoice_count = self.env['account.move'].sudo().search_count(domain)
                if invoice_count == 0  :
                    students.append(stud.id)
            domain = {'student_id': [('id', 'in', students)]}
            return {'domain': domain}