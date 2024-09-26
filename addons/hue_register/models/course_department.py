from odoo import models, fields, api


class CourseDepartment(models.Model):
    _name = 'hue.course.department'
    _description = 'hue.course.department'
    _inherit = ['mail.thread']
    
    student_ids = fields.One2many('hue.student.course.department','std_course_id', string="Students")
    course_id = fields.Many2one('op.course', string='Course', required=True , tracking=True, domain="[('id', 'in', suitable_course_ids)]")
    suitable_course_ids = fields.Many2many('op.course', compute='_compute_suitable_course_ids',) #to add domain to course_id
    new_course_id = fields.Many2one('op.course', required=True , tracking=True, domain="[('id', 'in', suitable_new_course_ids)]")
    suitable_new_course_ids = fields.Many2many('op.course', compute='_compute_suitable_course_ids',) #to add domain to new_course_id
    
    @api.onchange('course_id')
    def _compute_suitable_course_ids(self):
        for rec in self:
            parent_courses =[]
            courses = self.env['op.course'].sudo().search([('parent_id', '!=', False)])
            parent_courses = courses.mapped('parent_id').ids
            child_courses = self.env['op.course'].sudo().search([('parent_id', '=', self.course_id.id)])
            rec.suitable_course_ids = parent_courses
            rec.suitable_new_course_ids = child_courses.ids
        
    def get_student_list(self):
        status_ids = self.env['hue.std.data.status'].sudo().search([('id', '=', 2)])._ids
        students=self.env['op.student'].sudo().search([('course_id', '=', self.course_id.id),('student_status', 'in', status_ids)])        
        for stud in students:
            stud_line = {
                'student_id': stud.id,
                'std_course_id': self.id,
            }            
            all_students = self.env['hue.student.course.department'].sudo().search([('student_id', '=', stud.id),('std_course_id', '=', self.id)])
            if not all_students:
                student_course = self.env['hue.student.course.department'].sudo().create(stud_line)

    def button_done(self):
        lists = self.env['hue.student.course.department'].sudo().search([('std_course_id', '=', self.id)])
        for stud in lists:
            if stud.transfer_course:
                student= self.env['op.student'].search([('id', '=', stud.student_id.id)])
                student.write({'course_id': self.new_course_id.id})
                stud.unlink()
                
                
class StudentCourseDepartment(models.Model):
    _name = 'hue.student.course.department'
    _description = 'hue.student.course.department'

    std_course_id = fields.Many2one('hue.course.department',  ondelete='cascade', required=True, index=True)
    student_id = fields.Many2one('op.student', string='Student', readonly=True)
    student_code = fields.Integer(related='student_id.student_code', readonly=True, store=True)
    transfer_course = fields.Boolean(default=False)
    std_level = fields.Char(related='student_id.level.name', store=True, string="Level")
    std_gpa = fields.Float(related='student_id.new_gpa', string="GPA")
