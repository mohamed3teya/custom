from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class CustomBatch(models.Model):
    _inherit = 'op.batch'
    _order = "end_date desc"
    
    academic_year = fields.Many2one('op.academic.year', string='Academic Year')
    allow_registration_invoicing = fields.Boolean(string='Allow Registration Invoicing', default=False)
    control_allowed = fields.Boolean(string='Allowed For Control', default=False)
    default_week_end = fields.Date(string='Default week end', required=True, tracking=True)
    default_week_start = fields.Date(required=True, tracking=True)
    start_date = fields.Date('Start Date', required=True, default=fields.Date.today(), tracking=True)
    end_date = fields.Date('End Date', required=True, tracking=True)
    intern_batch = fields.Boolean(string='Intern Batch')
    product_id = fields.Many2one('product.product', string='Product Cost per Hour')
    semester = fields.Many2one('op.semesters',required=True, tracking=True)
    subject_registration_ids = fields.One2many('hue.subject.registration', 'batch_id', string='Subject Registrations', tracking=True)
    tree_clo_acl_ids = fields.Char(string='Tree Clo Acl',compute="_compute_tree_clo_acl_ids", search='tree_clo_acl_ids_search')
    
    
    @api.constrains('default_week_start', 'end_date')
    def check_dates(self):
        for record in self:
            start_date = fields.Date.from_string(record.default_week_start)
            end_date = fields.Date.from_string(record.default_week_end)
            if start_date > end_date:
                raise ValidationError(
                    _("Default End Date cannot be set before Default Start Date."))
    
    
    def write(self, values):
        if 'subject_registration_ids' in values:
            subject_registration_ids = values['subject_registration_ids']
            message = "<div>\n"
            for subj in subject_registration_ids :
                if subj[0] == 1 :
                    subject = self.env['hue.subject.registration'].sudo().search([('id', '=', subj[1])])
                    message += "<strong>subject upadate : " + subject.subject_id.name + "</strong>  <br/>   "
                    message += "<ul class=\"o_mail_thread_message_tracking\"> \n"
                    message += "</ul>"
                elif subj[0] == 2 :
                    subject = self.env['hue.subject.registration'].sudo().search([('id', '=', subj[1])])
                    message += "<strong>Delete subject : " + subject.subject_id.name + "</strong>  <br/>   "
                elif subj[0] == 0 :
                    subject = self.env['op.subject'].sudo().search([('id', '=', subj[2]['subject_id'])])
                    message += "<strong>Create subject : " + subject.name  + "</strong>  <br/>   "
                    
            message += "</div>"
            self.message_post(body=message, subject="Mark Changed")
        res = super(CustomBatch, self).write(values)
        return res
    
    
    @api.depends('course_id')
    def _compute_tree_clo_acl_ids(self):
        print('View My Tree CLO ACL')
        
    def tree_clo_acl_ids_search(self, operator, operand):
        records = []
        if self.env.ref('hr_extention.group_service_manager') in self.env.user.groups_id:
            return [('id', 'in', self.sudo().search([]).ids)]
        else:
            employee_id = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
            AcadYearID = self.env['op.academic.year'].sudo().search([('timetable_current', '=', True)], limit=1).id
            semester_id = self.env['op.semesters'].sudo().search([('timetable_current', '=', True)], limit=1).id
            if employee_id and employee_id.course_ids.ids:
                # batch_ids = self.env['op.batch'].sudo().search([('course_id', 'in', employee_id.course_ids.ids)]) #('academic_year', '=', AcadYearID), ('semester', '=', semester_id),
                # start_date = datetime.datetime.strptime(batch_ids[0].default_week_start, '%Y-%m-%d')
                # end_date = datetime.datetime.strptime(batch_ids[0].default_week_end, '%Y-%m-%d')
                # print("__________ f =============" + str(employee_id.id))
                # print(batch_ids)
                if employee_id:
                    records = self.search([('course_id', 'in', employee_id.course_ids.ids)]).ids
            return [('id', 'in', records)]