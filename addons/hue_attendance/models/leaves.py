from odoo import models, fields, api
import datetime
from dateutil.relativedelta import relativedelta


class globalLeaves(models.Model):
    _name = "op.global.leaves"
    _description = "Global Leaves"


    name = fields.Char(string='Name')
    year = fields.Integer(string='Year', required=True)
    date_from = fields.Date('From Date', required=True)
    date_to = fields.Date('To Date', required=True)
    

class studentLeaves(models.Model):
    _name = "op.student.leaves"
    _description = "Student Leaves"
    _inherit = ['mail.thread']


    student_id = fields.Many2one('op.student', 'Student', required=True , tracking=True)
    student_code = fields.Integer('Student Code', related='student_id.student_code', readonly=True)
    course_id = fields.Many2one('op.course', related='student_id.course_id', readonly=True)
    name = fields.Char(string='Name')
    date_from = fields.Date('From Date', required=True , tracking=True)
    date_to = fields.Date('To Date', compute='_end_date', store=True , tracking=True)
    leave_type = fields.Selection([('sick', 'Sick Leave'), ('sport', 'Sport'), ('traveling', 'Traveling Abroad'), ('social', 'Social Issue'), ('quarter', 'Quarter Offer'), ('military', 'Military training'), ('conference ', 'Conference ')], 'Leave Type', required=True)
    days = fields.Integer ('no of days' , tracking=True)
    

    @api.depends('date_from','days')
    def _end_date(self):
        if self.days :
            date_from =datetime.strptime(self.date_from, '%Y-%m-%d') - relativedelta(days=1)
            self.date_to = ( date_from + relativedelta(days=self.days)).strftime('%Y-%m-%d')


class StudentExtension(models.Model):
    _inherit = 'op.student'
    
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.search([('student_code', operator, name)] + args, limit=limit)
        if not recs.ids:
            return super(StudentExtension, self).name_search(name=name, args=args,operator=operator,limit=limit)
        return recs.name_get()

