from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class Advisor(models.Model):
    _name = 'student.without.advisor'
    _description = 'student.without.advisor'
    _inherit = ['mail.thread']
    _rec_name = 'advisor'
    
    student_no_advisor_ids = fields.One2many('student.advisor.done','std_advisor_id', string="Students")
    advisor = fields.Many2one('op.faculty', string='Advisor', required=True,domain="[('id', 'in', suitable_advisor_ids)]")
    suitable_advisor_ids = fields.Many2many('op.faculty', compute='_compute_suitable_advisor_ids') 
    fromdate = fields.Date(string='From Date ', required=True, default=fields.Date.today)
    course_id = fields.Many2one('op.course', string='Course', required=True)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')],
                                 string='State', required=True, default='draft', tracking=True)
    advisor_count = fields.Integer('Students Count', default=10)
    # , compute="_compute_students_count"
    

    #Add domain to classroom groups
    @api.onchange('advisor')
    def _compute_suitable_advisor_ids(self):
        for rec in self:
            advisor_ids = []
            acad_directions = self.env["hue.academic.direction"].search([])
            if acad_directions:
                for acad in acad_directions:
                    advisor_ids.append(acad.faculty_id.id)
            rec.suitable_advisor_ids = advisor_ids


    @api.depends('advisor')
    def _compute_students_count(self):
        for record in self:
            if record.advisor:
                x = self.env['hue.academic.direction.line'].search_count([('faculty_id', '=', record.advisor.id), ('to_date', '=', False)])
                record.advisor_count = self.env['hue.academic.direction.line'].search_count(
                    [('faculty_id', '=', record.advisor.id), ('to_date', '=', False)])
            else:
                record.advisor_count = 0

    def get_student_list(self):
        print("2222222222222222222222222222222222222")
        limit = self.advisor_count
        status_ids = self.env['hue.std.data.status'].sudo().search([('id', '=', 2)])._ids
        students_advisor =self.env['hue.academic.direction.line'].sudo().search([('to_date', '=', False)])
        students_advisor = students_advisor.mapped('student_id').ids
        
        students_no_advisor =self.env['op.student'].sudo().search([('id', 'not in', students_advisor),('student_status', 'in', status_ids),('course_id', '=', self.course_id.id)] ,order="student_status", limit=limit)
        # students_no_advisor =students_no_advisor.mapped('student_id')
        i = 1
        for stud in students_no_advisor:
            if limit == 0:
                stud_line = {
                    'seq': i,
                    'std_advisor_id': self.id,
                    'student_id': stud.id,
                    'done': False,
                }
            else:
                stud_line = {
                    'seq': i,
                    'std_advisor_id': self.id,
                    'student_id': stud.id,
                    'done': True,
                }            
            # all_students_no_advisor = self.env['hue.academic.direction.line'].sudo().search([('student_id', '=', stud.id)    ])
            all_students_no_advisor = self.env['student.advisor.done'].sudo().search([('student_id', '=', stud.id),('std_advisor_id', '=', self.id)])
            if not all_students_no_advisor:
                all_students_no_advisor = self.env['student.advisor.done'].sudo().create(stud_line)
            i = i + 1


    def button_done(self):
        print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        acdAdv = self.env['hue.academic.direction'].sudo().search([('faculty_id', '=', self.advisor.id)], limit=1).id
        print("acdAdv", acdAdv)
        lists = self.env['student.advisor.done'].sudo().search([('std_advisor_id', '=', self.id)])
        print("lists", lists)
        for stud in lists:
            # stuAdv = self.env['hue.academic.direction.line'].sudo().search([('student_id', '=', stud.id),('to_date', '=', False)])
            # if not stuAdv:
            if stud.done:
                stuAdv = self.env['hue.academic.direction.line'].create({'college_id':stud.student_id.faculty.id,'acad_dir_id':acdAdv,'student_id': stud.student_id.id, 'faculty_id': self.advisor.id ,'from_date':self.fromdate})       
                print("stuAdv", stuAdv.acad_dir_id)
                student_advisor= self.env['op.student'].search([('id', '=', stud.student_id.id)])
                student_advisor.write({'advisor': self.advisor.name })
                stud.unlink()
        # self.write({'state': 'done'})
        

class StudentAdvisorDone(models.Model):
    _name = 'student.advisor.done'
    _description = 'student.advisor.done'
    
    std_advisor_id = fields.Many2one('student.without.advisor', string='Control', ondelete='cascade', required=True, index=True)
    seq = fields.Integer('#', readonly=True)
    student_id = fields.Many2one('op.student', string='Student', readonly=True)
    code = fields.Integer(related='student_id.student_code', readonly=True, store=True)
    course_id = fields.Many2one(related='student_id.course_id',string='Course', readonly=True , store=True)
    done = fields.Boolean(string='Done',default=False)
    std_level = fields.Char(related='student_id.level.name', store=True, string="Level")
    std_gpa = fields.Float(related='student_id.new_gpa', string="GPA")