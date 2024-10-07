from odoo import api, models


class registrationStatistics(models.AbstractModel): 
    _name = 'report.hue_register.registration_statistics'
    _description = " registration statistics"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        print("model:-------------", model)
        docs = self.env[model].browse(self.env.context.get('active_id'))
        course_id =docs.course_id
        subject_id =docs.subject_id
        student_registration =[]
        prerequisites =[]
        student_no_registration =[]
        subjects = self.env['op.subject'].sudo().search(
                [('course_id', '=', course_id.id)])
        status_ids = self.env['hue.std.data.status'].search([('active_invoice', '=', True)])._ids
        student_ids = self.env['op.student'].sudo().search(
                [('course_id', '=', course_id.id), ('student_status', 'in', status_ids)])
        if subject_id :
            student_registration = self.env['op.student.semesters.subjects'].sudo().search(
                [('student_id.student_status', 'in', status_ids),('student_id.course_id', '=', course_id.id),('subject_id', '=', subject_id.id),('final_grade.pass_grade', '=', True)]) 
            student_registration = student_registration.mapped('student_id')       
            std_no_register = self.env['op.student'].sudo().search(
                    [('course_id', '=', course_id.id), ('student_status', 'in', status_ids),
                         ('id', 'not in', student_registration.ids)])
            if subject_id.prerequisites_count >= 1 :
                for std in std_no_register:
                    pre_count = 0
                    for pre_subj in subject_id.subject_prerequisites:
                        student_registration_prereq = self.env['op.student.semesters.subjects'].sudo().search(
                        [('student_id', '=', std.id),('student_id.course_id', '=', course_id.id),('subject_id', '=', pre_subj.id),('final_grade.pass_grade', '=', True)]) 
                        if student_registration_prereq :
                            pre_count = pre_count+1
                            if pre_count == subject_id.prerequisites_count :
                                prerequisites.append(std)
                student_no_registration = len(prerequisites)
            else:
                student_no_registration = len(student_ids) - len(student_registration)
        
            
        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'docs': docs,
            'student_registration':student_registration ,
            'student_ids' :student_ids,
            'student_no_registration':student_no_registration,
            'prerequisites':prerequisites,
            'subjects':subjects,
            'get_reg':self.get_reg

            
        }
        return docargs
    def get_reg(self,course_id,subjects):
        status_ids = self.env['hue.std.data.status'].search([('active_invoice', '=', True)])._ids
        student_ids = self.env['op.student'].sudo().search(
                [('course_id', '=', course_id.id), ('student_status', 'in', status_ids)])
        student_registration = self.env['op.student.semesters.subjects'].sudo().search(
        [('student_id.student_status', 'in', status_ids),('student_id.course_id', '=', course_id.id),('subject_id', '=', subjects.id),('final_grade.pass_grade', '=', True)]) 
        student_registration = student_registration.mapped('student_id')       
        std_no_register = self.env['op.student'].sudo().search(
                [('course_id', '=', course_id.id), ('student_status', 'in', status_ids),
                     ('id', 'not in', student_registration.ids)])
        prerequisites =[]
        if subjects.prerequisites_count >= 1 :
            for std in std_no_register:
                pre_count = 0
                for pre_subj in subjects.subject_prerequisites:
                    student_registration_prereq = self.env['op.student.semesters.subjects'].sudo().search(
                    [('student_id', '=', std.id),('student_id.course_id', '=', course_id.id),('subject_id', '=', pre_subj.id),('final_grade.pass_grade', '=', True)]) 
                    if student_registration_prereq :
                        pre_count = pre_count+1
                        if pre_count == subjects.prerequisites_count :
                            prerequisites.append(std)
            student_no_registration = len(prerequisites)
        else:
            student_no_registration = len(student_ids) - len(student_registration)
    
        return [student_registration ,student_no_registration]
    