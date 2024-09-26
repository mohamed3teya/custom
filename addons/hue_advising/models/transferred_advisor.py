from odoo import models, fields, api, _
import logging
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class NewAdvisor(models.Model):
    _name = 'transferred.advisor'
    _description = 'transferred.advisor'
    _inherit = ['mail.thread']

    student_advisor_ids = fields.One2many('hue.academic.direction.line','transfer_advisor_id', string="Students")
    advisor = fields.Many2one('op.faculty', string='Advisor', required=True, domain="[('id', 'in', suitable_advisor_ids)]")
    new_advisor = fields.Many2one('op.faculty', string='New Advisor', domain="[('id', 'in', suitable_advisor_ids)]")
    suitable_advisor_ids = fields.Many2many('op.faculty', compute='_compute_suitable_advisor_ids') 
    fromdate = fields.Date(string=' Date ', required=True, default=fields.Date.today)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')],
                                 string='State', required=True, default='draft', tracking=True)
    
    
    #Add domain to advisors
    @api.onchange('advisor','new_advisor')
    def _compute_suitable_advisor_ids(self):
        for rec in self:
            advisor_ids = []
            acad_directions = self.env["hue.academic.direction"].search([])
            if acad_directions:
                for acad in acad_directions:
                    advisor_ids.append(acad.faculty_id.id)
            rec.suitable_advisor_ids = advisor_ids
            
    def get_student_list(self):
        students_advisor =self.env['hue.academic.direction.line'].sudo().search([('student_id.student_status.name', '=', 'مستجد'),('to_date', '=', False),('faculty_id', '=',  self.advisor.id)])
        self.student_advisor_ids = [(6,0,students_advisor.ids)] 

                                      
    def button_done(self):
        status_ids = self.env['hue.std.data.status'].sudo().search([('active_invoice', '=', True)])._ids
        print("status_ids", status_ids)
        acdAdv = self.env['hue.academic.direction'].sudo().search([('faculty_id', '=', self.advisor.id)], limit=1).id
        print("acdAdv", acdAdv)
        acdNewAdv = self.env['hue.academic.direction'].sudo().search([('faculty_id', '=', self.new_advisor.id)], limit=1).id
        if not acdNewAdv:
            raise ValidationError("Please choose a valid advisor to transfer students to")
        print("acdNewAdv", acdNewAdv)
        lists =self.env['hue.academic.direction.line'].sudo().search([('to_date', '=', False),('faculty_id', '=',  self.advisor.id)])
        print("lists", lists)
        for stud in lists:
            if self.new_advisor.id:
                print("1111111111111111111111111111111111111111")
                stuNewAdv = self.env['hue.academic.direction.line'].create({'acad_dir_id':acdNewAdv,'student_id': stud.student_id.id, 'faculty_id': self.new_advisor.id ,'from_date':self.fromdate ,'college_id':stud.student_id.faculty.id})            
                stud.write({'to_date':self.fromdate})
                student_advisor= self.env['op.student'].search([('id', '=', stud.student_id.id)])
                student_advisor.write({'advisor': self.new_advisor.name })
            else:
                stud.write({'to_date':self.fromdate})
                student_advisor= self.env['op.student'].search([('id', '=', stud.student_id.id)])
                student_advisor.write({'advisor':None })
