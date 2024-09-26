from odoo import models, fields, api
import ssl
import xml.etree.ElementTree as ET
import urllib.request as urllib2, urllib.parse, urllib.error


class opSubjects(models.Model):
    _inherit = 'op.subject'
    
    
    subject_type = fields.Selection(selection_add=[('project','Project')], ondelete={'project': 'cascade'})
    course_id = fields.Many2one('op.course', string='Course')
    parent_course_id = fields.Many2one('op.course', string='Parent Course',related='course_id.parent_id')
    prerequisites_count = fields.Integer(string='No. of Prerequisites')
    required_hours = fields.Float(string='Required Hours')
    subject_assessmentsdegree = fields.One2many('op.course.assessments.dgrees','subject_id', string="Assessments")
    subject_credithours = fields.Integer(string='Credit Hours',required=True)
    subject_lecturehours = fields.Integer(string='Lecture Hours')
    subject_level = fields.Many2one('op.levels', string='Level',required=True)
    subject_oralhours = fields.Integer(string='Oral Hours')
    subject_passpercentage = fields.Char(string='Pass Percentage')
    subject_practhours = fields.Integer(string='Practical Hours')
    subject_sectionhours = fields.Integer(string='Section Hours')
    subject_prerequisites = fields.Many2many('op.subject', 'prerequisites', 'col_1', 'col_2',
                                             string="Prerequisites",
                                             domain="['|',('course_id', '=', course_id),('course_id', '=', parent_course_id)]")
    subject_semester = fields.Many2one('op.semesters', string='Semester',required=True)
    subject_total = fields.Integer(string='Total Degree',compute='_compute_total',required=True)
    subject_core_type = fields.Selection([('core','Core'),('elective','Elective'),('project','Project')],string="Core type?")
    summer_training = fields.Boolean(string='Summer Training',default=False)
    ethics = fields.Boolean()
    intern_subject = fields.Boolean(string='Intern Subject',default=False)
    subject_addtogpa = fields.Boolean(string='Add to GPA',default=True)
    subject_addtohours = fields.Boolean(string='Add to Hours')
    subject_credithours_invoice = fields.Boolean(string='Credit Hours Not Invoiced')
    subject_passorfail = fields.Boolean(string='Pass or Fail')
    subject_satisfied = fields.Boolean(string='S or U')
    
    
    _sql_constraints = [
        ('unique_subject_code',
         'Check(1=1)', 'Cancel unique code!')]
    
    
    @api.depends('subject_assessmentsdegree')
    def _compute_total(self):
        total = 0
        for rec in self.subject_assessmentsdegree:
            total += rec.degree
            self.subject_total = total
        self.subject_total = total
    
    # @api.model
    # def name_search(self, name, args=None, operator='ilike', limit=100):
    #     if name:
    #         recs = self.search(['|', ('name', operator, name), ('code', operator, name)] + (args or []), limit=limit)
    #         # if not recs:
    #         # 	recs = self.search([('student_code', operator, name)] + (args or []), limit=limit)
    #         return recs.name_get()
    #     return super(opSubjects, self).name_search(name, args=args, operator=operator, limit=limit)
    
    
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if self.env.context.get('get_subjects', False):
            lst = []
            lst.append(self.env.context.get('batch_id'))
            batches = self.env['op.batch'].browse(lst)
            subject_reg_ids = self.env['op.batch'].search([
                    ('id', '=', lst)]).subject_registration_ids
            subject_ids = []
            for reg in subject_reg_ids:
                subject_ids.append(reg.subject_id.id)
            print(subject_ids)
            subjects = self.env['op.subject'].browse(subject_ids)
            return subjects.name_get()
        return super(opSubjects, self).name_search(
            name, args, operator=operator, limit=limit)
    

    @api.model
    def getsubject_data(self):
        print('33333333333333333333333333333')
        url = "https://me.horus.edu.eg/horusDataWebservice?index=coursesData"
        req = urllib2.Request(url, headers={'X-Mashape-Key': ''})
        gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)  # Only for gangstars
        webURL = urllib2.urlopen(req, context=gcontext)
        data = webURL.read()
        print(url)
        tree = ET.fromstring(data)
        lst = tree.findall('course')
        i = 1
        for each in lst:
            subjectName = each.find('courseName')
            subjectCode = each.find('courseCode')
            subjectCH = each.find('creditHours')
            courseName = each.find('ProgramName')
            faculty_name = each.find('facultyName')
            Assesments = each.findall('CourseAssesments/Assesments')
    
            # Courses
            crsName = self.env['op.course'].search([('name', '=', courseName.text)])
            # print(faculty_name.text)
            # print(faculty_name.text.split('|')[1])
            faculty_id = self.env['hue.faculties'].search(
                [('name', '=ilike', (faculty_name.text.split('|')[1]).strip())]).id
            # print(faculty_id)
            if not crsName:
                crsName = self.env['op.course'].create(
                    {'name': courseName.text, 'code': i, 'credithours': 180, 'faculty_id': faculty_id})
            # Subjects
            code = self.search([('code', '=', subjectCode.text)])
            if not code and subjectName.text != None:
                code = self.create({'name': subjectName.text, 'code': subjectCode.text})
            # Courses Subjects
    
            if crsName and code:
                crsSubject = self.env['op.subject'].search(
                    [('id', '=', code.id), ('course_id', '=', crsName.id)])
                if not crsSubject:
                    crsSubject = self.env['op.subject'].create(
                        {'subject_id': code.id, 'course_id': crsName.id, 'name': subjectName.text,
                         'code': subjectCode.text, 'subject_semester': 1, 'subject_level': 1, 'subject_type': 1,
                         'subject_total': 100, 'subject_credithours': subjectCH.text})
    
                for every in Assesments:
    
                    assessment = self.search([('name', '=', every.text.split('|')[0])])
    
                    if not assessment:
                        assessment = self.env['op.assessments'].create({'name': every.text.split('|')[0]})
    
                    assessmntSearch = self.env['op.course.assessments.dgrees'].search(
                        [('assessment_id', '=', assessment.id), ('course_subject_id', '=', crsSubject.id)])
    
                    if not assessmntSearch:
                        self.env['op.course.assessments.dgrees'].create(
                            {'course_subject_id': crsSubject.id, 'assessment_id': assessment.id,
                             'degree': every.text.split('|')[1]})
            i += 1
            

    @api.model
    def get_hue_subject_fun(self):
        print('33333333333333333333333333333')
        url = "https://sys.mc.edu.eg/WebServiceMCI?index=coursesData"
        req = urllib2.Request(url, headers={'X-Mashape-Key': ''})
        gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)  # Only for gangstars
        webURL = urllib2.urlopen(req, context=gcontext)
        data = webURL.read()
        print(url)
        tree = ET.fromstring(data)
        lst = tree.findall('course')
        i = 1
        #to make sure that course code is unique
        crs_lst = self.env['op.course'].search([])
        code_lst = []
        max_code = False
        for crs in crs_lst:
            code_lst.append(int(crs.code))
        if code_lst:
            max_code = max(code_lst)
        if max_code:
            i=int(max_code)+1    
        for each in lst:
            subjectName = each.find('courseName')
            subjectCode = each.find('courseCode')
            subjectCH = each.find('creditHours')
            courseName = each.find('ProgramName')
            faculty_name = each.find('facultyName')
            Assesments = each.findall('CourseAssesments/Assesments')
            subtype = each.find('CourseType')
            subtype = subtype.text.split('|')[1].lower()
            subjectCode = subjectCode.text.split('|')[0]
            print
            # Courses
            crsName = self.env['op.course'].search([('name', '=', courseName.text)])
            faculty_id = self.env['hue.faculties'].search([('name_ar', 'ilike', faculty_name.text.split('|')[0].split()[0])]).id
            if not crsName:
                crsName = self.env['op.course'].create(
                    {'name': courseName.text, 'code': i, 'credithours': 180, 'faculty_id': faculty_id})
            # Subjects
            sub = self.search([('code', '=', subjectCode), ('course_id', '=', crsName.id)])
            sub_sem = self.env['op.semesters'].search([],limit=1)
            sub_lev = self.env['op.levels'].search([],limit=1)
            if not sub and subjectName.text != None and crsName:
                sub = self.create({'course_id': crsName.id, 'name': subjectName.text,
                         'code': subjectCode, 'subject_semester': sub_sem.id, 'subject_level': sub_lev.id, 'subject_type': subtype,
                         'subject_total': 100, 'subject_credithours': subjectCH.text})
                
                for every in Assesments:
    
                    assessment = self.search([('name', '=', every.text.split('|')[0])])
    
                    if not assessment:
                        assessment = self.env['op.assessments'].create({'name': every.text.split('|')[0]})
    
                    assessmntSearch = self.env['op.course.assessments.dgrees'].search(
                        [('assessment_id', '=', assessment.id), ('subject_id', '=', sub.id)])
    
                    if not assessmntSearch:
                        self.env['op.course.assessments.dgrees'].create(
                            {'subject_id': sub.id, 'assessment_id': assessment.id,
                             'degree': every.text.split('|')[1]})
            i += 1
