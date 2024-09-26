from odoo import fields, models


class StudyTypes(models.Model):
    _name = 'op.studytypes'
    _description = 'Add Study Types'
    
    name = fields.Char('Name')


class Places(models.Model):
    _name = 'op.places'
    _description = 'Add Places'
    
    name = fields.Char('Name')
    code = fields.Char('Code')


class Buildings(models.Model):
    _name = 'op.buildings'
    _description = 'Add Buildings'
    
    name = fields.Char('Name')
    code = fields.Char('Code')
    
    
class StudyTimeTable(models.Model):
    _name = 'op.studytimetable'
    _description = 'Add Study Timetable'
    
    course_id = fields.Many2one('op.course')
    subject_id = fields.Many2one('op.subject')
    acadyear = fields.Many2one('op.academic.year', required=True)
    semester = fields.Many2one('op.semesters', required=True)
    from_date = fields.Char('FromDate', required=True)
    to_date = fields.Char('ToDate', required=True)
    placeid = fields.Many2one('op.places', required=True)
    groupno = fields.Integer('GroupNo', required=True)
    sectionno = fields.Integer('SectionNo', required=True)
    daydate = fields.Char('Day Date', required=True)
    studytype = fields.Many2one('op.studytypes', required=True)
    lecturer = fields.Char('Lecturer', required=True)
    lecturernids = fields.Char('Lecturer IDs', required=True)


class studentattendance(models.Model):
    _name = 'op.attendance'
    _description = 'Student Attendance'
    
    course_id = fields.Many2one('op.course')
    subject_id = fields.Many2one('op.subject')
    student_id = fields.Many2one('op.student')
    acadyear = fields.Many2one('op.academic.year')
    semester = fields.Many2one('op.semesters')
    absencedate = fields.Char('FromDate')
    percentage = fields.Float('ToDate')
    absenceno = fields.Integer('absenceno')
    attendancetype = fields.Many2one('op.studytypes')
    subjectmapid = fields.Char('SubjectMapID')
    totpercentage = fields.Float('totPercentage')