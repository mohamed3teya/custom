from odoo import fields, models, api
import urllib.request as urllib2
import ssl
import json
from odoo.exceptions import UserError


class Missed_Migrated_data(models.Model):
    _name = 'missed.migrated.data'
    _description = 'missed.migrated.data'
    
    missed_student_migration = fields.Text()
    

class StudentEduData(models.Model):
    _name = 'op.student.accumulative'
    _rec_name = 'academicyear_id'
    _description = 'Student Accumulative Year'
    
    missed_student_migration = fields.Text()
    student_id = fields.Many2one('op.student', string='Student', required=True)
    course_id = fields.Many2one('op.course', string='Course', required=True)
    academicyear_id = fields.Many2one('op.academic.year', string='Academic Year', required=True)
    acumhr = fields.Float('AcumHr')
    acumgpa = fields.Float('AcumGPA')
    accum_semesters_ids = fields.One2many('op.student.accumlative.semesters', 'student_accum_id')
        
    
    @api.model
    def get_hue_student_accumulative_fun(self):
        accum = self.env['op.student.accumulative']
        accum_sem = self.env['op.student.accumlative.semesters']
        sem_sub = self.env['op.student.semesters.subjects']
        students = self.env['op.student'].search([('course_id','=',2)])#2,3,4,5,6,7,8,9,10,11,12,13 done
        codes = []
        for stu in students:
            if stu.student_code and len(str(stu.student_code)) == 4:
                codes.append(stu.student_code)
        print("Number of codes",len(codes))
        # student  = students = self.env['op.student'].search([('student_code','=',4371)]).id
        # print("studentiddddddddddddddd: ",student)
        missed_data = ""
        for stu_code in codes:
            stu_code = 4897
            url = "https://sys.mc.edu.eg/WebServiceMCI?index=GetStudentCoursesGrades&ID=" + str(stu_code)
            # print("URL", url)
            # url = "https://sys.mc.edu.eg/WebServiceMCI?index=GetStudentCoursesGrades&ID=4371"
            # stu_code = url[-4:]
            print("stu_code:------------------", stu_code)
             
            req = urllib2.Request(url, headers={ 'X-Mashape-Key': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX' })
            gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)  # Only for gangstars
            webURL = urllib2.urlopen(req, context=gcontext)
            data = webURL.read()
            encoding = webURL.info().get_content_charset('utf-8')
            data = json.loads(data.decode(encoding))
            # print("1111111111111111111111111111111111111111")
            if len(data)<2:
                missed_data += "student: "+str(stu_code)+" misssed_URL,"
                print("missed_data-11111111111111111111111111111111", missed_data)
                continue
            try:
                data = data["StuSemesterData"]
            except:
                missed_data += "student: "+str(stu_code)+" misssed_URL,"
                print("missed_data-11111111111111111111111111111111", missed_data)
                continue
            for  rec in data:
                # print("rec:-----", rec)
                acad_year = rec["AcadYearName"]
                academic_year = self.env['op.academic.year'].search([('name','ilike',acad_year)]).id
                if not academic_year:
                    raise UserError("Please update your academic year table")
                stu = self.env['op.student'].search([('student_code','=',stu_code)])
                course = stu.course_id
                if not course:
                    raise UserError("Please update your course table")
                print("academic_year:-----------------", academic_year)
                print('course:--------------------', course)
                
                accum_id = accum.search([('student_id','=',stu.id)]).id
                if not accum_id:
                    accum.create({
                        'student_id':stu.id, 
                        'course_id':course.id,
                        'academicyear_id':academic_year,
                        'acumgpa':rec["cumGPA"], 
                        'acumhr':rec["cumHrs"]
                    })
                accum_id = accum.search([('student_id','=',stu.id)]).id
                print("accum_id:-------------",accum_id)
                # op.student.accumulative created
                
                #loop through semesters
                for sem in rec['Semesters']:
                    # print("sem['SemesterName']:-------------------",sem['SemesterName'])
                    sem_name = sem['SemesterName']
                    sem_id = self.env['op.semesters'].search([('name','ilike',sem['SemesterName'])]).id
                    if sem['SemesterName'] == 'موازنة خارجية|Out Transfer':
                        sem_id = self.env['op.semesters'].search([('name','ilike','الموازنة|Transfered')]).id  
                    # print("sem_id:-----------------------",sem_id)
                    if not sem_id:
                        raise UserError("Please update your semester table")
                    semester_statuses = self.env['hue.std.data.status'].search([('name','ilike','مستجد')])
                    if len(semester_statuses)>1:
                        for sta in semester_statuses:
                            if sta.name == 'مستجد':
                                semester_status = sta
                    else:            
                        semester_status = semester_statuses   
                    accum_sem_id = accum_sem.search([('student_id','=',stu.id),('semester_id','=',sem_id),('academicyear_id','=',academic_year)], limit=1).id
                    if not accum_sem_id:
                        accum_sem.create({
                            'student_accum_id' : accum_id,
                            'student_id' : stu.id,
                            'academicyear_id' : academic_year,
                            'semester_id' : sem_id,
                            'semester_gpa' : sem["GPA"],
                            'current_gpa' : sem["CurrGPA"],
                            'semester_hr' : sem["CurrCH"],
                            'semester_status' : semester_status.id,
                        })
                    accum_sem_id = accum_sem.search([('student_id','=',stu.id),('semester_id','=',sem_id),('academicyear_id','=',academic_year)], limit=1).id
                    print("accum_sem_id", accum_sem_id)    
                    # op.student.accumlative.semesters created
                    #loop through subjects
                    for sub in sem["Courses"]:
                        print("CourseCode:--------------",sub["CourseCode"].split('|')[0].strip())
                        sub_id = self.env['op.subject'].search([('code','ilike',sub["CourseCode"].split('|')[0].strip()),('course_id','=',course.id)],limit=1).id
                        if not sub_id:
                            sub_id = self.env['op.subject'].search([('code','ilike',sub["CourseCode"].split('|')[0].strip()),('course_id','=',course.parent_id.id)]).id
                        if not sub_id:
                            missed_data+=('student: '+str(stu_code)+' missed_subject: '+str(sub["CourseCode"].split('|')[0].strip())+'-'+str(acad_year)+'-'+str(sem_name)+",")
                            print("missed_data-22222222222222222222222",missed_data)
                            # self.missed_student_transfer.append("missed subjects"+str(stu_code)+','+str(sub["CourseCode"].split('|')[0].strip())+str(academic_year)+str(sem_id)+",")
                            continue    
                        sem_sub_id = sem_sub.search([('student_id','=',stu.id),('student_semester_id','=',accum_sem_id),('academicyear_id','=',academic_year),('subject_id','=',sub_id)], limit=1)
                        if not sem_sub_id:    
                            print("sub_id:==============", sub_id)
                            if sub["CourseStatus"] == "un unanswerd Questionnaire":
                                missed_data+=('student: '+str(stu_code)+' missed_subject: '+str(sub["CourseCode"].split('|')[0].strip())+'-'+str(acad_year)+'-'+str(sem_name)+",")
                                continue
                            try:
                                grade_final = sub["FinaltermDegree"]
                                if sub["FinaltermDegree"] == "z":
                                    missed_data+=('student: '+str(stu_code)+' missed_subject: '+str(sub["CourseCode"].split('|')[0].strip())+'-'+str(acad_year)+'-'+str(sem_name)+",")
                                    continue
                            except:
                                missed_data+=('student: '+str(stu_code)+' missed_subject: '+str(sub["CourseCode"].split('|')[0].strip())+'-'+str(acad_year)+'-'+str(sem_name)+",")
                                continue
                            if grade_final == 'غ':
                                grade_final = 0.05
                            grade_coursework = sub["CourseWorkDegree"]
                            if grade_coursework == 'غ':
                                grade_coursework = 0.05
                            grade_medterm = sub["MidtermDegree"]
                            if grade_medterm == 'غ':
                                grade_medterm = 0.05
                            if grade_medterm == 'z':
                                grade_medterm = 0.06 
                            grade_pract = sub["PractDegree"]
                            if grade_pract == 'غ':
                                grade_pract = 0.05
                            subject_degree = sub["Degree"]
                            if subject_degree == 'غ':
                                subject_degree = 0.05
                            if subject_degree == 'Z':
                                subject_degree = 0.06
                            if subject_degree == 'z':
                                subject_degree = 0.06 
                            if sub["Grade"]:                           
                                subject_grades = self.env["op.grades"].search([('name','ilike',sub["Grade"].split('|')[0].strip())])
                            else:
                                missed_data+=('student: '+str(stu_code)+' missed_subject: '+str(sub["CourseCode"].split('|')[0].strip())+'-'+str(acad_year)+'-'+str(sem_name)+",")
                                continue
                            if len(subject_grades) > 1:
                                # print("subject_grade",subject_grades)
                                for grade in subject_grades:
                                    if grade.name.split('|')[1].strip() == sub["Grade"].split('|')[0].strip():
                                        subject_grade = grade
                                        break
                            else:
                                subject_grade = subject_grades
                            print("subject_grade:------------------------", subject_grades)
                            sem_sub.create({
                                'academicyear_id' : academic_year,
                                'student_semester_id' : accum_sem_id,
                                'student_id' : stu.id,
                                'semester_id' : sem_id,
                                'student_code' : stu.student_code,
                                'course_id' : course.id,
                                'subject_id' : sub_id,
                                'grade_final' : grade_final,
                                'grade_coursework' : grade_coursework,
                                'grade_medterm' : grade_medterm,
                                'grade_pract' : grade_pract,
                                'subject_degree' : subject_degree,
                                'subject_grade' : subject_grade.id,
                            })
        print("missed_datafinal-333333333333333333", missed_data)
        missed = self.env['missed.migrated.data']
        vals = {
            'missed_student_migration' : missed_data
        }
        missed.create(vals)
   
       
class StudentSemesters(models.Model):
    _name = 'op.student.accumlative.semesters'
    _rec_name = 'academicyear_id'
    _description = 'Student Semesters'
    
    
    student_accum_id = fields.Many2one('op.student.accumulative', string='Student Accumulative Year',
                                       ondelete='cascade')
    student_id = fields.Many2one('op.student', string='Student', related='student_accum_id.student_id', store=True)
    course_id = fields.Many2one('op.course', string='Course', related='student_accum_id.course_id', store=True)
    academicyear_id = fields.Many2one('op.academic.year', string='Academic Year', store=True) #,related='student_accum_id.academicyear_id' comment untill migration complete
    semester_id = fields.Many2one('op.semesters', string='Semester', required=True)
    semester_status = fields.Many2one('hue.std.data.status', string='Status', required=True)
    semester_gpa = fields.Float('GPA')
    semester_hr = fields.Float('CurrCH')
    current_gpa = fields.Float('CurrGPA')
    transferred = fields.Boolean()
    block_result = fields.Many2one('op.blockresult', string='Block Result')
    accum_semesters_subjects_ids = fields.One2many('op.student.semesters.subjects', 'student_semester_id')
    earned_hours = fields.Float()
    registered_hours = fields.Float()
    actual_hours = fields.Float()
    accumulated_hours = fields.Float()
    accumulated_degree = fields.Float()
    semester_points = fields.Float()
    semester_current_gpa = fields.Float()
    total_degree = fields.Float()
    total_max = fields.Float()
    percentage = fields.Float()
    grade = fields.Many2one('op.grades')
    control_grade = fields.Many2one('op.grades')
    control_degree = fields.Float()
    final_degree = fields.Float(string='Final Degree', compute='_compute_degree_grade', store="True")
    final_grade = fields.Many2one('op.grades', string='Final Grade', compute='_compute_degree_grade', store="True")
    timestamp= fields.Datetime()
    
    
    @api.depends('grade', 'total_degree', 'control_grade', 'control_degree')
    def _compute_degree_grade(self):
        for rec in self:
            if rec.control_grade:
                rec.final_grade = rec.control_grade
            else:
                rec.final_grade = rec.grade
            if rec.control_degree:
                rec.final_degree = rec.control_degree
            else:
                rec.final_degree = rec.total_degree