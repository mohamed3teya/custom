from odoo import models, fields

class MilitaryStudent(models.Model):
    _name = 'military.student'
    _description = 'military.student'
    _inherit = ['mail.thread']
    _rec_name = 'militarynumber'

    student_military_ids = fields.One2many('op.student','military_id', string="Students")
    academic_year_id = fields.Many2one('op.academic.year', string='Academic Year', required=True)
    semester_id = fields.Many2one('op.semesters', string='Joined Semester', required=True)
    fromdate = fields.Date(string='Date From', required=True, default=fields.Date.today())
    todate = fields.Date(string='Date To', required=True, default=fields.Date.today)
    name = fields.Text( string='Military Name', required=True)
    militarynumber = fields.Integer( string='Military Number')
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')],
                                 string='State', required=True, default='draft', tracking=True)
    

    def get_student_list(self):
        status_ids = self.env['hue.std.data.status'].sudo().search([('active_invoice', '=', True)])._ids
        students = self.env['op.student'].sudo().search([('military_done', '=',False),('student_status', 'in', status_ids),('gender', '=', 'm') ])#,('nationality', '=', 65) Not set yet
        self.student_military_ids = [(6,0,students.ids)] 


    def button_done(self):
        for stud in self.student_military_ids:
            if stud.military_done:
                stud.write({'done_military_id': self.id }) 
            else:
                stud.write({'done_military_id': False })


class opStudentsStudyTimetable(models.Model):
    _inherit = 'op.student'

    military_done = fields.Boolean(default=False)
    military_id = fields.Many2one('military.student')
    done_military_id = fields.Many2one('military.student' ,string='Military Data')
    military_notes = fields.Text()
    # session_ids = fields.Many2many('op.session', 'student_session_rel', 'student_id', 'session_id', 'Registrations')
    session_tmp_ids = fields.Many2many('op.session', 'student_session_tmp_rel', 'student_id', 'session_id', 'Registrations')
    advisor = fields.Char(compute='_advisor' , store =True)
    university_name = fields.Many2one('hue.university.transfer', string='University Name',readonly= True)


    #advisor of student
    def _advisor(self):
        for rec in self :
            status_ids = self.env['hue.std.data.status'].sudo().search([('active_invoice', '=', True)]).ids
            advisor_name = self.env['hue.academic.direction.line'].sudo().search([('student_id', '=', rec.id), ('to_date', '=', False),
                ('student_id.student_status', 'in', status_ids)])
            if advisor_name :
                rec.advisor = advisor_name.faculty_id.name