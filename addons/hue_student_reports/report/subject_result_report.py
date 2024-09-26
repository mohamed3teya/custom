from odoo import api, models

class StudentExamReport(models.AbstractModel):
    _name = 'report.hue_student_reports.subject_result_template'
    _description = "Student Subject result Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        if 'student_id' in docs :
            student_id = docs.student_id
        else:
            student_id = docs
        AcadYearID = self.env['op.academic.year'].sudo().search([('current', '=', True)], limit=1).id
        semester_id = self.env['op.semesters'].sudo().search([('current', '=', True)], limit=1).id
        invoice_count = 0
        StuAccID = self.env['op.student.accumulative'].sudo().search(
            [('student_id', '=', student_id.id), ('academicyear_id', '=', AcadYearID)],order='id desc', limit=1)  #
        StuSemesterID = self.env['op.student.accumlative.semesters'].sudo().search(
            [('student_accum_id', '=', StuAccID.id), ('semester_id', '=', semester_id), ('academicyear_id', '=', AcadYearID)])
        StuSubjectIDs = self.env['op.student.semesters.subjects'].sudo().search(
            [('student_semester_id', '=', StuSemesterID.id)])
        StudentGrades = self.env['subjects.control.student.list'].sudo().search(
            [('student_id', '=', student_id.id), ('connect_id.batch_id.academic_year', '=', AcadYearID),
             ('connect_id.batch_id.semester', '=', semester_id)])
        
        docargs = {
                'doc_ids': self.ids,
                'doc_model': model,
                'docs': docs,
                'student_id':student_id,
                'studentresults': StudentGrades,
                'academicyear': StuAccID.academicyear_id,
                'semester': StuSemesterID.semester_id,
                'courseid': StuAccID.course_id,
                'getmaxdegree': self.getmaxdegree ,
        }
        return docargs

    def getmaxdegree(self, subjectid, assessment_type):
        getmaxdeg = self.env['op.course.assessments.dgrees'].sudo().search(
            [('course_subject_id', '=', subjectid.id), ('assessment_id', '=', assessment_type)], limit=1).degree
        return getmaxdeg
