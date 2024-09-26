from odoo import models, fields, api


class studentdisciplinary(models.Model):
    _name = "student.disciplinary"
    _description = "Student disciplinary"
    _inherit = ['mail.thread']


    student_id = fields.Many2one('op.student', 'Student', required=True)
    student_code = fields.Integer('Student Code', related='student_id.student_code', readonly=True)
    course_id = fields.Many2one('op.course', related='student_id.course_id', store=True , readonly=True)
    batch_id = fields.Many2one('op.batch', required=True)
    name = fields.Char(string='Name')
    date_from = fields.Date('From Date', required=True)
    date_to = fields.Date('To Date', required=True)
    disciplinary_type = fields.Selection([('disciplinary_attendance', 'disciplinary_attendance')], 'Disciplinary Type', required=True)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')],
                             string='State', required=True, default='draft', tracking=True)
    
    
    @api.onchange('course_id')
    def onchange_course_id(self):
        for rec in self :
            rec.batch_id = False
            batches = self.env['op.batch'].sudo().search([('course_id', '=', rec.student_id.course_id.id)])
            domain = {'batch_id': [('id', 'in', batches.ids)]}
            return {'domain': domain}

    
    def button_done(self):
        student = self.env['op.attendance.line'].sudo().search([('student_id', '=', self.student_id.id),
            ('present', '!=', False),('batch_id', '=', self.batch_id.id),
            ('attendance_date', '>=', self.date_from),('attendance_date', '<=', self.date_to)])
        student.write({'present':False , 'absence_reason':self.disciplinary_type})
        self.write({'state': 'done'})


    def button_draft(self):
        student = self.env['op.attendance.line'].sudo().search([('student_id', '=', self.student_id.id),
            ('present', '=', False),('batch_id', '=', self.batch_id.id),
            ('attendance_date', '>=', self.date_from),('attendance_date', '<=', self.date_to)
            ,('absence_reason', '!=', False)])
        student.write({'present':True , 'absence_reason':None})
        self.write({'state': 'draft'})