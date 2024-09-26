from odoo import fields, models, api, _
import logging
import datetime
import math
import ssl
import urllib.request as urllib2, urllib.parse, urllib.error
import xml.etree.ElementTree as ET
import json

_logger = logging.getLogger(__name__)

class opStudentsEduData(models.Model):
    _inherit = 'op.student'
    
    student_accumlative_ids = fields.One2many('op.student.accumulative', 'student_id')
    student_semesters_accumlative_ids = fields.One2many('op.student.accumlative.semesters', 'student_id')
    
    def logfile(self, stucode, subjectcode, msg):
        f = open("/odoo/logfile.txt", "w")
        f.write(str(stucode) + "|" + str(subjectcode) + "|" + str(msg) + "\n")
        f.close()
        
    def write(self, values):
        if 'student_semesters_accumlative_ids' in values:
            student_semesters_accumlative_ids = values['student_semesters_accumlative_ids']
            for accum in student_semesters_accumlative_ids :
                if accum[0] ==1  :
                    recId = self.env['op.student.accumlative.semesters'].sudo().search([('id', '=', accum[1])])
                    stdInvoice = self.env['account.move'].sudo().search([('academic_term.semester_id', '=', recId.semester_id.id),
                            ('academic_year', '=', recId.academicyear_id.id),('student_code', '=', recId.student_id.student_code)])       
                    if stdInvoice :
                        for invoice in stdInvoice:
                            invoice.write({'student_status': accum[2]['semester_status']})
        res = super(opStudentsEduData, self).write(values)
        return res
    
    @api.model
    def _cron_total_hr(self):
        semesters = self.env['op.student.accumlative.semesters'].search([])
        for semester_rec in semesters:
            total = 0
            if semester_rec.semester_hr == 0.0 or semester_rec.semester_hr > 30:
                for rec in semester_rec.accum_semesters_subjects_ids:
                    total += rec.subject_id.subject_credithours
                print(semester_rec.semester_hr)
                semester_rec.write({'semester_hr': total})

    @api.model
    def getstuEdu_data(self, stucode=False, faculty=False, lmt=100, ofst=0, all_data=True):

        cur_academic_year_id = self.env['op.academic.year'].sudo().search([('current', '=', True)], limit=1)
        cur_semester_id = self.env['op.semesters'].sudo().search([('current', '=', True)], limit=1)
        status_ids = (self.env['hue.std.data.status'].sudo().search([])._ids)
        #('active_invoice', '=', True)
        if not stucode and faculty:
            students = self.env['op.student'].sudo().search(
                [('course_id', '=', faculty), ('student_status', 'in', status_ids)],
                limit=lmt, offset=ofst, order="student_code")
        elif not faculty and stucode:
            students = self.env['op.student'].sudo().search(
                [('student_code', '=', stucode), ('student_status', 'in', status_ids)])  # ,limit = 50)

        print('222222222222222222222')
        print(stucode)
        for student in students:
            print('1111111111111111777777777777')
            # if records before 2020-08-26 delete
            course_id2 = self.env['op.student.accumulative'].sudo().search(
                [('student_id', '=', student.id), ('write_date', '<', '2021-02-23 00:00:00')], order="id DESC",
                limit=1).course_id
            # if course_id2:
            #     student.student_accumlative_ids.sudo().unlink()

            url = "https://ibn.horus.edu.eg/horusDataWebservice?index=GetStudentCoursesGrades&ID=" + str(
                student.student_code)
            print(
                '================================================================================================ Student Data')
            print(url)
            print(
                '================================================================================================ Student Data')
            req = urllib2.Request(url, headers={'X-Mashape-Key': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'})
            gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)  # Only for gangstars
            webURL = urllib2.urlopen(req, context=gcontext)
            data = webURL.read()
            encoding = webURL.info().get_content_charset('utf-8')

            stuid = student.id
            stufacultyid = student.faculty.id

            CourseID = student.course_id.id
            data = json.loads(data.decode(encoding))

            if not data:
                self.logfile(stuid, student.student_code, 'No Data')
                continue

            if not 'StuSemesterData' in data:
                continue

            index = 0
            for val in data["StuSemesterData"]:
                if val['AcadYearName'] == 84:
                    continue
                AcadYear = val['AcadYearName']
                StuLevel = val['StudyYearOrLevel']
                cumGPA = val['cumGPA']
                cumHrs = val['cumHrs']
                CGPA = val['CGPA']
                AcadYearID = self.env['op.academic.year'].sudo().search([('join_year', '=', AcadYear)])

                # IF CURRENT YEAR #
                if AcadYearID.id == cur_academic_year_id.id or all_data:
                    stuAccID = self.env['op.student.accumulative'].sudo().search(
                        [('student_id', '=', student.id), ('course_id', '=', CourseID),
                         ('academicyear_id', '=', AcadYearID.id)], limit=1)
                    if stuAccID:
                        stuAccID.sudo().write({'acumgpa': cumGPA, 'acumhr': cumHrs})
                    else:
                        stuAccID = self.env['op.student.accumulative'].sudo().create(
                            {'student_id': student.id, 'course_id': CourseID, 'academicyear_id': AcadYearID.id,
                             'acumgpa': cumGPA, 'acumhr': cumHrs})
                    # print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
                    # print(stuAccID)
                    ii = 0
                    for val2 in val['Semesters']:
                        Semester = val2['SemesterName']
                        SemesterGPA = val2['GPA']
                        SemesterCH = val2['CurrCH']
                        GPAtillCurrSemester = val2['CurrGPA']
                        stuStatus = val2['studentStatus']
                        print("$$$$$$$$$$$$$$$4")
                        print(stuStatus)
                        studentStatusName = 2
                        if stuStatus:
                            studentStatusName = self.env['hue.std.data.status'].sudo().search(
                                [('name', 'like', stuStatus)]).id
                        if not studentStatusName:
                            studentStatusName = 2
                        print(studentStatusName)
                        if val2['BlockResult'] != '':
                            # print('33333333333333333')
                            BR = self.env['op.blockresult'].sudo().search([('name', '=', val2['BlockResult'])])
                            if not BR:
                                BR = self.env['op.blockresult'].sudo().create({'name': val2['BlockResult']})
                            BlockResult = BR.id

                        SemesterID = self.env['op.semesters'].sudo().search([('name', 'ilike', Semester)])

                        # IF CURRENT SEMESTER #
                        if SemesterID.id == cur_semester_id.id or all_data:
                            ii += 1

                            StuAccSemID = self.env['op.student.accumlative.semesters'].sudo().search(
                                [('student_accum_id', '=', stuAccID.id), ('semester_id', '=', SemesterID.id)])
                            if StuAccSemID:
                                if val2['BlockResult'] != '':
                                    StuAccSemID.sudo().write({'semester_gpa': SemesterGPA, 'semester_hr': SemesterCH,
                                                              'current_gpa': GPAtillCurrSemester,
                                                              'block_result': BlockResult,
                                                              'semester_status': studentStatusName})
                                else:
                                    StuAccSemID.sudo().write({'semester_gpa': SemesterGPA, 'semester_hr': SemesterCH,
                                                              'current_gpa': GPAtillCurrSemester,
                                                              'semester_status': studentStatusName})
                            else:
                                if val2['BlockResult'] != '':
                                    StuAccSemID = self.env['op.student.accumlative.semesters'].sudo().create(
                                        {'student_accum_id': stuAccID.id, 'academicyear_id': AcadYearID.id,
                                         'semester_id': SemesterID.id, 'semester_gpa': SemesterGPA,
                                         'semester_hr': SemesterCH, 'current_gpa': GPAtillCurrSemester,
                                         'block_result': BlockResult, 'semester_status': studentStatusName})
                                else:
                                    StuAccSemID = self.env['op.student.accumlative.semesters'].sudo().create(
                                        {'student_accum_id': stuAccID.id, 'academicyear_id': AcadYearID.id,
                                         'semester_id': SemesterID.id, 'semester_gpa': SemesterGPA,
                                         'semester_hr': SemesterCH, 'current_gpa': GPAtillCurrSemester,
                                         'semester_status': studentStatusName})

                            # StuAccSemID = self.env['op.student.accumlative.semesters'].create({'student_accum_id':stuAccID.id,'academicyear_id':AcadYearID.id ,'semester_id':SemesterID.id ,'semester_gpa':SemesterGPA ,'semester_hr':SemesterCH,'current_gpa': GPAtillCurrSemester ,'semester_status': 1 })
                            # print('BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB')
                            # print(StuAccSemID)
                            for val3 in val2['Courses']:

                                # print("=========(========)(((((((((((((((========")
                                # print(val3['CourseCode'])
                                # print(student.student_code)
                                Grade = ''
                                if 'Grade' in val3:
                                    Grade = val3['Grade']
                                    # print(Grade)
                                # else:
                                #     continue

                                if Grade != '' and Grade != None:
                                    Degree = val3['Degree']
                                    # print(Degree)
                                    if Degree != 'Z' and Degree != 'W' and Degree != 'T' and Degree != 'I':
                                        if float(Degree) == False and Degree != '0':
                                            # print('11111112223333333333333331111111')
                                            self.logfile(val3['CourseCode'], student.student_code, 'No Degree')
                                            continue
                                    FinalDegree = val3['FinaltermDegree']
                                    MCQDegree = val3['MCQDegree']
                                    ActivityDegree = val3['ReportsDegree']
                                    AttendanceDegree = val3['ModelDDegree']
                                    ParctDegree = val3['PractDegree']
                                    Parct2Degree = val3['Midterm1Degree']
                                    OralDegree = val3['OralDegree']
                                    MidTermDegree = val3['MidtermDegree']
                                    ProgramID = val3['CourseID']
                                    SubjectCode = val3['CourseCode']
                                    CloseFlag = val3['CloseFlag']
                                    # print(SubjectCode.split('|')[0])
                                    # print(courseid.id)
                                    # print('VVVVVVVVVVVVVVLLLLLLLLLLLLLLVVVVVVVVVVVVVVVVVV')
                                    # print(ProgramID)
                                    # progID = self.env['op.course'].sudo().search([('code', '=', ProgramID.split('.')[0])])
                                    # stuAccID.write({'course_id': progID.id  })
                                    # print(progID)
                                    print('___________ Result _______ ' + str(student.student_code) + ' _______')
                                    _logger.info('___________ Result _______ ' + str(student.student_code) + ' _______')

                                    SubjectID = self.env['op.subject'].search(
                                        [('subject_code', '=', SubjectCode), ('course_id', '=', student.course_id.id)],
                                        limit=1)

                                    if not SubjectID:
                                        SubjectID = self.env['op.subject'].search(
                                            [('subject_code', '=', SubjectCode + '|' + SubjectCode),
                                             ('course_id', '=', student.course_id.id)], limit=1)
                                    if not SubjectID:
                                        SubjectID = self.env['op.subject'].search(
                                            [('subject_code', 'ilike', SubjectCode.split('|')[0]),
                                             ('course_id', '=', student.course_id.id)], limit=1)

                                    if not SubjectID:
                                        SubjectID = self.env['op.subject'].search(
                                            [('subject_code', '=', SubjectCode),
                                             ('course_id', '=', student.course_id.parent_id.id)], limit=1)
                                    if not SubjectID:
                                        SubjectID = self.env['op.subject'].search(
                                            [('subject_code', '=', SubjectCode + '|' + SubjectCode),
                                             ('course_id', '=', student.course_id.parent_id.id)], limit=1)
                                    if not SubjectID:
                                        SubjectID = self.env['op.subject'].search(
                                            [('subject_code', 'ilike', SubjectCode.split('|')[0]),
                                             ('course_id', '=', student.course_id.parent_id.id)], limit=1)
                                    if not SubjectID:
                                        # print(SubjectCode)
                                        continue
                                    print('\-\-\-\-\-\-\-\-\-\-\-\-\-')
                                    print(SubjectID)
                                    GradeID = self.env['op.grades'].sudo().search([('name', 'ilike', Grade)])
                                    if not GradeID:
                                        self.logfile(val3['CourseCode'], student.student_code, 'No Grade')
                                        continue
                                    # self.env['op.student.semesters.subjects'].create({'student_semester_id':StuAccSemID.id,'subject_id':SubjectID.id ,'subject_degree': Degree ,'subject_grade': GradeID.id ,'grade_final': FinalDegree ,'grade_quiz': MCQDegree , 'grade_activity': ActivityDegree , 'grade_attendance':AttendanceDegree, 'grade_pract':ParctDegree, 'grade_oral':OralDegree,'grade_medterm':MidTermDegree,'grade_pract2':Parct2Degree })
                                    if SubjectID.id:
                                        print(SubjectID.subject_id.name)
                                        print('1111111111111111111111111')
                                        print('1111111111111111111111111')
                                        print('1111111111111111111111111')
                                        stuSemSubID = self.env['op.student.semesters.subjects'].sudo().search(
                                            [('student_semester_id', '=', StuAccSemID.id),
                                             ('subject_id', '=', SubjectID.id)])
                                        if stuSemSubID:
                                            # if student.student_code == '3171189':
                                            #   stuSemSubID.sudo().write(
                                            #     {'subject_grade': GradeID.id})
                                            if Degree != 'Z' and Degree != 'W' and Degree != 'T' and Degree != 'I' and MidTermDegree != 'غ' and MCQDegree != 'غ' and FinalDegree != 'غ' and MidTermDegree != 'z' and FinalDegree != 'z' and FinalDegree != 'w' and MCQDegree != 'z' and MidTermDegree != 'w' and MCQDegree != 'w' and ActivityDegree != 'غ' and ActivityDegree != 'w' and ActivityDegree != 'z' and AttendanceDegree != 'غ' and AttendanceDegree != 'w' and AttendanceDegree != 'z' and ParctDegree != 'غ' and ParctDegree != 'w' and ParctDegree != 'z' and Parct2Degree != 'غ' and Parct2Degree != 'w' and Parct2Degree != 'z' and OralDegree != 'غ' and OralDegree != 'w' and OralDegree != 'z':
                                                # print('99999999999999999999999999999')
                                                stuSemSubID.sudo().write(
                                                    {'grade_activity': ActivityDegree,
                                                     'grade_attendance': AttendanceDegree,
                                                     'grade_pract': ParctDegree,
                                                     'grade_pract2': Parct2Degree,
                                                     'grade_oral': OralDegree})
                                                    # 'subject_degree': Degree, 'subject_grade': GradeID.id,
                                                    #  'grade_final': FinalDegree, 'grade_quiz': MCQDegree,
                                                    #  'grade_medterm': MidTermDegree,
                                            else:
                                                stuSemSubID.sudo().write(
                                                    {'subject_degree': Degree, 'subject_grade': GradeID.id})
                                        else:
                                            if student.student_code == '3171189':
                                                self.env['op.student.semesters.subjects'].sudo().create(
                                                    {'student_semester_id': StuAccSemID.id, 'subject_id': SubjectID.id,
                                                     'subject_grade': GradeID.id})
                                            if Degree != 'Z' and Degree != 'W' and Degree != 'T' and Degree != 'I' and MidTermDegree != 'غ' and MCQDegree != 'غ' and FinalDegree != 'غ' and MidTermDegree != 'z' and FinalDegree != 'z' and FinalDegree != 'w' and MCQDegree != 'z' and MidTermDegree != 'w' and MCQDegree != 'w':
                                                # print('99999999999999999999999999999')
                                                self.env['op.student.semesters.subjects'].sudo().create(
                                                    {'student_semester_id': StuAccSemID.id, 'subject_id': SubjectID.id,
                                                     'subject_degree': Degree, 'subject_grade': GradeID.id,
                                                     'grade_final': FinalDegree, 'grade_quiz': MCQDegree,
                                                     'grade_medterm': MidTermDegree})
                                            else:
                                                self.env['op.student.semesters.subjects'].sudo().create(
                                                    {'student_semester_id': StuAccSemID.id, 'subject_id': SubjectID.id,
                                                     'subject_degree': Degree, 'subject_grade': GradeID.id})

                                else:

                                    # print('RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR')
                                    # print(CourseID)
                                    # print('VVVVVVVVVVRRRRRRRRRRRRRRRRRRggggVVVVVVVVVVVVVVV')
                                    # progID = self.env['op.course'].sudo().search([('code', '=', val3['CourseID'].split('.')[0])])
                                    #
                                    # stuAccID.write({'course_id': progID.id  })
                                    # print(progID.id)
                                    # print('eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
                                    SubjectCode = val3['CourseCode']
                                    MidTermDegree = ''
                                    MCQDegree = ''
                                    if 'MidtermDegree' in val3:
                                        MidTermDegree = val3['MidtermDegree']
                                    if 'MCQDegree' in val3:
                                        MCQDegree = val3['MCQDegree']
                                    # print(SubjectCode.split('|')[0])
                                    # print(courseid.id)

                                    CloseFlag = val3['CloseFlag']
                                    # SubjectID = self.env['op.course.subjects'].search([('subject_code', '=', SubjectCode.split('|')[0]),('course_id', '=', progID.id)],limit = 1)
                                    # print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAa')
                                    # print(progID.id)
                                    # print(SubjectID)
                                    # print(SubjectCode)
                                    # print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAa33333')
                                    # if not SubjectID:
                                    SubjectID = self.env['op.subject'].search(
                                        [('subject_code', '=', SubjectCode), ('course_id', '=', student.course_id.id)],
                                        limit=1)

                                    if not SubjectID:
                                        SubjectID = self.env['op.subject'].search(
                                            [('subject_code', '=', SubjectCode + '|' + SubjectCode),
                                             ('course_id', '=', student.course_id.id)], limit=1)
                                    if not SubjectID:
                                        SubjectID = self.env['op.subject'].search(
                                            [('subject_code', 'ilike', SubjectCode.split('|')[0]),
                                             ('course_id', '=', student.course_id.id)], limit=1)

                                    if not SubjectID:
                                        SubjectID = self.env['op.subject'].search(
                                            [('subject_code', '=', SubjectCode),
                                             ('course_id', '=', student.course_id.parent_id.id)], limit=1)
                                    if not SubjectID:
                                        SubjectID = self.env['op.subject'].search(
                                            [('subject_code', '=', SubjectCode + '|' + SubjectCode),
                                             ('course_id', '=', student.course_id.parent_id.id)], limit=1)
                                    if not SubjectID:
                                        SubjectID = self.env['op.subject'].search(
                                            [('subject_code', 'ilike', SubjectCode.split('|')[0]),
                                             ('course_id', '=', student.course_id.parent_id.id)], limit=1)
                                    if not SubjectID:
                                        # print(SubjectCode)
                                        continue
                                    GradeID = self.env['op.grades'].sudo().search([('name', 'ilike', Grade)])
                                    # if not GradeID
                                    #     continue
                                    # self.env['op.student.semesters.subjects'].create({'student_semester_id':StuAccSemID.id,'subject_id':SubjectID.id ,'subject_degree': Degree ,'subject_grade': GradeID.id ,'grade_final': FinalDegree ,'grade_quiz': MCQDegree , 'grade_activity': ActivityDegree , 'grade_attendance':AttendanceDegree, 'grade_pract':ParctDegree, 'grade_oral':OralDegree,'grade_medterm':MidTermDegree,'grade_pract2':Parct2Degree })
                                    if SubjectID.id:
                                        # print('2222222222222222222222')
                                        stuSemSubID = self.env['op.student.semesters.subjects'].sudo().search(
                                            [('student_semester_id', '=', StuAccSemID.id),
                                             ('subject_id', '=', SubjectID.id)])
                                        if stuSemSubID:
                                            if MidTermDegree != 'غ' and MCQDegree != 'غ' and MidTermDegree != 'z' and MidTermDegree != 'w' and MidTermDegree != 'T' and MidTermDegree != 'I' and MCQDegree != 'z' and MCQDegree != 'w' and MCQDegree != 'T' and MCQDegree != 'I':
                                                # print('99999999999999999999999999999')
                                                stuSemSubID.sudo().write(
                                                    {'closeflag': CloseFlag, 'grade_quiz': MCQDegree,
                                                     'grade_medterm': MidTermDegree})
                                            else:
                                                stuSemSubID.sudo().write({'closeflag': CloseFlag})
                                        else:
                                            if MidTermDegree != 'غ' and MCQDegree != 'غ' and MidTermDegree != 'z' and MidTermDegree != 'w' and MidTermDegree != 'T' and MidTermDegree != 'I' and MCQDegree != 'z' and MCQDegree != 'w' and MCQDegree != 'T' and MCQDegree != 'I':
                                                self.env['op.student.semesters.subjects'].sudo().create(
                                                    {'student_semester_id': StuAccSemID.id, 'subject_id': SubjectID.id,
                                                     'closeflag': CloseFlag, 'grade_quiz': MCQDegree,
                                                     'grade_medterm': MidTermDegree})
                                            else:
                                                self.env['op.student.semesters.subjects'].sudo().create(
                                                    {'student_semester_id': StuAccSemID.id, 'subject_id': SubjectID.id,
                                                     'closeflag': CloseFlag})


class opStudentsQuesData(models.Model):
    _inherit = 'op.student'


    @api.model
    def getstuQues_data(self):
        # ('student_code','!=',3161110)('faculty','=',6),('student_code','=',5171122)
        # print('QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ')
        status_ids = (self.env['hue.std.data.status'].search([('active_invoice', '=', True)])._ids)
        students = self.env['op.student'].search(
            [('faculty', '=', 10), ('student_status', 'in', status_ids)])  # ,limit = 50)
        for student in students:
            url = "https://me.horus.edu.eg/WebServiceFarouk?index=StudentQuesStatus&StuCode=" + str(
                student.student_code)

            req = urllib2.Request(url, headers={'X-Mashape-Key': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'})
            gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)  # Only for gangstars
            webURL = urllib2.urlopen(req, context=gcontext)
            data = webURL.read()
            encoding = webURL.info().get_content_charset('utf-8')

            stuid = student.id
            stufacultyid = student.faculty.id
            courseid = self.env['op.course'].search([('faculty_id', '=', stufacultyid)], limit=1)

            data = json.loads(data.decode(encoding))
            # print(data)
            if not data:
                continue

            for val in data:
                AcadSemester = val["AcadSemester"]
                AcadYear = val["AcadYear"]
                SubjectCode = val["CourseCode"]
                Questionaire = val["questionaire"]

                AcadSemesterID = self.env['op.semesters'].search([('name', '=', AcadSemester)])
                AcadYearID = self.env['hue.joining.years'].search([('name', '=', AcadYear)])

                StudentAccID = self.env['op.student.accumulative'].search(
                    [('student_id', '=', stuid), ('course_id', '=', courseid.id),
                     ('academicyear_id', '=', AcadYearID.id)])
                StudentSemesterID = self.env['op.student.accumlative.semesters'].search(
                    [('student_accum_id', '=', StudentAccID.id), ('semester_id', '=', AcadSemesterID.id),
                     ('academicyear_id', '=', AcadYearID.id)])

                SubjectID = self.env['op.subject'].search([('subject_code', '=', SubjectCode)])
                StudentSubjectID = self.env['op.student.semesters.subjects'].search(
                    [('student_semester_id', '=', StudentSemesterID.id), ('id', '=', SubjectID.id)])

                StudentSubjectID.write({'quesflag': Questionaire})

                # print(student.student_code)
                # print(SubjectID.id)
                # print(Questionaire)


class opMoveStudentsIbnAlhitham(models.Model):
    _inherit = 'op.student'


    @api.model
    def getmovestudents(self, stucode=False):
        xx = 0
        status_ids = (self.env['hue.std.data.status'].search([('active_invoice', '=', True)])._ids)
        print(len(status_ids))
        if stucode == False:
            students = self.env['op.student'].search([('student_status', 'in', status_ids), (
                'year', '=', '2020')])  # ,limit = 50) ('faculty','=',10), ,('student_code','=',3171229)
        else:
            students = self.env['op.student'].search(
                [('student_status', 'in', status_ids), ('year', '=', '2020'), ('student_code', '=', stucode)])
        # students = self.env['op.student'].search([('student_status','in',status_ids),('year','=','2020'),('faculty','=',int(faculty))])
        print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
        print(len(students))
        for student in students:
            print('ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ')
            print((student))
            StudentApp = self.env['op.admission'].sudo().search([('student_id', '=', student.id)])
            ProgramID = ""
            FacultyID = ""
            # print("####################################################")
            # print(StudentApp.faculty)
            if StudentApp.faculty.id == 6:
                ProgramID = "22cd08cc-cf0b-11e9-a9fc-00155df1fe0e"
                FacultyID = "229971a8-cf0b-11e9-a9fc-00155df1fe0e"
            if StudentApp.faculty.id == 7:
                ProgramID = "22cd034e-cf0b-11e9-a9fc-00155df1fe0e"
                FacultyID = "22997462-cf0b-11e9-a9fc-00155df1fe0e"
            if StudentApp.faculty.id == 8:
                ProgramID = "22d22ce1-cf0b-11e9-a9fc-00155df1fe0e"
                FacultyID = "22997277-cf0b-11e9-a9fc-00155df1fe0e"
            if StudentApp.faculty.id == 9:
                ProgramID = "22d53ebf-cf0b-11e9-a9fc-00155df1fe0e"
                FacultyID = "22997320-cf0b-11e9-a9fc-00155df1fe0e"
            if StudentApp.faculty.id == 10:
                ProgramID = "22c8e811-cf0b-11e9-a9fc-00155df1fe0e"
                FacultyID = "229973c2-cf0b-11e9-a9fc-00155df1fe0e"
            if StudentApp.faculty.id == 12:
                ProgramID = "36537fd4240311eb8af400155d06c901"
                FacultyID = "7e195213238e11eb8af400155d06c901"

            if StudentApp.gender == 'm':
                Gender = "cc6541856bcf11e8adef00155df1fe0e"
            else:
                Gender = "cc6541e56bcf11e8adef00155df1fe0e"

            social = "cc6504486bcf11e8adef00155df1fe0e"
            idType = "cc8d6c356bcf11e8adef00155df1fe0e"
            relegion = "cc6353d06bcf11e8adef00155df1fe0e"
            cerDate = "0d270a537dd811e8bbcd00155df1fe0e"
            cert = "cc8ed10e6bcf11e8adef00155df1fe0e"
            turn = "cc8f29576bcf11e8adef00155df1fe0e"
            # print('TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT')
            # print(StudentApp.birth_date)
            dt = ""
            if (StudentApp.birth_date):
                dt = datetime.datetime.strptime(StudentApp.birth_date, '%Y-%m-%d').strftime('%d/%m/%Y')
            else:
                dt = "01/01/2021"
            # url = "https://me.horus.edu.eg/WebServiceHorus?index=AddNewStudent&arName="+student.partner_id.name+"&arName="+student.partner_id.name+"&" #  +str(student.student_code)
            url = "https://me.horus.edu.eg/WebServiceHorus?index=AddNewStudent&arName=" + urllib.parse.quote(
                str(StudentApp.arabic_name)) + "&enName=" + urllib.parse.quote(
                str(StudentApp.english_name)) + "&gender=" + urllib.parse.quote(str(Gender)) + "&dOB=" + str(
                dt) + "&birthPlace=" + urllib.parse.quote(
                str(StudentApp.city_id.d_id)) + "&nationality=" + urllib.parse.quote(
                str(StudentApp.nationality_id.d_id)) + "&nationalId=" + str(
                StudentApp.national_id) + "&acadSemester=" + urllib.parse.quote(
                "cc8f47b36bcf11e8adef00155df1fe0e") + "&acadYear=" + urllib.parse.quote(
                "916811fdc1c811eaa10d00155d06c800") + "&scopeId=" + urllib.parse.quote(
                str(FacultyID)) + "&progId=" + urllib.parse.quote(str(ProgramID)) + "&studentCode=" + str(
                StudentApp.Student_code) + "&certificate=" + urllib.parse.quote(
                str(cert)) + "&degree=" + urllib.parse.quote(
                str(StudentApp.certificate_degree)) + "&percentage=" + urllib.parse.quote(
                str(StudentApp.certificate_percentage)) + "&email=" + urllib.parse.quote(
                str(StudentApp.email)) + "&mobile=" + urllib.parse.quote(
                str(StudentApp.mobile_number)) + "&seatno=" + urllib.parse.quote(
                str(StudentApp.seat_no)) + "&certificatedate=" + urllib.parse.quote(
                str(cerDate)) + "&relegion=" + urllib.parse.quote(str(relegion)) + "&idType=" + urllib.parse.quote(
                str(idType)) + "&socialStatus=" + urllib.parse.quote(str(social)) + "&mobileTel=" + urllib.parse.quote(
                str(StudentApp.mobile_number)) + "&addressRegion=" + urllib.parse.quote(
                str(StudentApp.city_id.d_id)) + "&PreQualification=" + urllib.parse.quote(
                str(cert)) + "&School=" + urllib.parse.quote(
                str(StudentApp.school_name)) + "&PreQualificationYear=" + urllib.parse.quote(
                str(cert)) + "&PreQualificationDegree=" + urllib.parse.quote(
                str(StudentApp.certificate_degree)) + "&certificatedate=" + urllib.parse.quote(
                str(StudentApp.certificate_percentage)) + "&stuCode=" + urllib.parse.quote(
                str(StudentApp.Student_code)) + "&PreQualificationTurn=" + urllib.parse.quote(str(turn))
            # url = "https://me.horus.edu.eg/WebServiceHorus?index=AddNewStudent&arName="+urllib.parse.quote(str(StudentApp.arabic_name))+"&enName="+urllib.parse.quote(str(StudentApp.english_name))+"&gender="+urllib.parse.quote(str(Gender))+"&dOB="+str(dt)+"&birthPlace="+urllib.parse.quote(str(StudentApp.city_id.d_id))+"&nationality="+urllib.parse.quote(str(StudentApp.nationality_id.d_id))+"&nationalId="+str(StudentApp.national_id)+"&acadSemester="+urllib.parse.quote("cc8f47b36bcf11e8adef00155df1fe0e")+"&acadYear="+urllib.parse.quote("916811fdc1c811eaa10d00155d06c800")+"&scopeId="+urllib.parse.quote(str(FacultyID))+"&progId="+urllib.parse.quote(str(ProgramID))+"&studentCode="+str(StudentApp.Student_code)+"&certificate="+urllib.parse.quote(str(cert))+"&degree=396.00&percentage=96.58&email=3191001@horus.edu.eg&mobileTel=01064737612&seatno=705538&certificatedate="+urllib.parse.quote(str(StudentApp.certificate_date))+"&relegion="+urllib.parse.quote(str(relegion))+"&idType="+urllib.parse.quote(str(idType))+"&socialStatus="+urllib.parse.quote(str(social))+"&PreQualification="+urllib.parse.quote(str(StudentApp.certificate_id.d_id))+"&School="+urllib.parse.quote(str(StudentApp.school_name))+"&Percentage="+urllib.parse.quote(str(StudentApp.certificate_percentage))+"&stuCode="+urllib.parse.quote(str(StudentApp.Student_code))+"&PreQualificationYear="+urllib.parse.quote(str(cerDate))+"&PreQualificationTurn="+urllib.parse.quote(str(turn))+"&PreQualificationDegree="+urllib.parse.quote(str(StudentApp.certificate_degree))+""
            xx = xx + 1
            print('______________________________________________________')
            print(url)
            # print(StudentApp.Student_code)
            req = urllib2.Request(url, headers={'X-Mashape-Key': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'})
            gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)  # Only for gangstars
            webURL = urllib2.urlopen(req, context=gcontext)
            print(webURL)


class opMoveEductionalDataIbnAlhitham(models.Model):
    _inherit = 'op.student'


    @api.model
    def getmoveeductionaldata(self, stucode=''):
        xx = 0
        status_ids = (self.env['hue.std.data.status'].search([('active_invoice', '=', True)])._ids)
        if stucode == '':
            students = self.env['op.student'].search([('student_status', 'in', status_ids), (
                'year', '=', '2020')])  # ,limit = 50) ('faculty','=',10), ,('student_code','=',3171229)
        else:
            students = self.env['op.student'].search(
                [('student_status', 'in', status_ids), ('year', '=', '2020'), ('student_code', '=', stucode)])
        # print('ZZZZZZZZZddddddddddddddZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ')
        for student in students:
            # print('ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ')
            StudentApp = self.env['op.admission'].sudo().search([('student_id', '=', student.id)])
            ProgramID = ""
            FacultyID = ""
            # print("####################################################")
            # print(StudentApp.faculty)
            if StudentApp.faculty.id == 6:
                ProgramID = "22cd08cc-cf0b-11e9-a9fc-00155df1fe0e"
                FacultyID = "229971a8-cf0b-11e9-a9fc-00155df1fe0e"
            if StudentApp.faculty.id == 7:
                ProgramID = "22cd034e-cf0b-11e9-a9fc-00155df1fe0e"
                FacultyID = "22997462-cf0b-11e9-a9fc-00155df1fe0e"
            if StudentApp.faculty.id == 8:
                ProgramID = "22d22ce1-cf0b-11e9-a9fc-00155df1fe0e"
                FacultyID = "22997277-cf0b-11e9-a9fc-00155df1fe0e"
            if StudentApp.faculty.id == 9:
                ProgramID = "22d53ebf-cf0b-11e9-a9fc-00155df1fe0e"
                FacultyID = "22997320-cf0b-11e9-a9fc-00155df1fe0e"
            if StudentApp.faculty.id == 10:
                ProgramID = "22c8e811-cf0b-11e9-a9fc-00155df1fe0e"
                FacultyID = "229973c2-cf0b-11e9-a9fc-00155df1fe0e"

            if StudentApp.gender == 'm':
                Gender = "cc6541856bcf11e8adef00155df1fe0e"
            else:
                Gender = "cc6541e56bcf11e8adef00155df1fe0e"

            social = "cc6504486bcf11e8adef00155df1fe0e"
            idType = "cc8d6c356bcf11e8adef00155df1fe0e"
            relegion = "cc6353d06bcf11e8adef00155df1fe0e"
            cerDate = "0d270a537dd811e8bbcd00155df1fe0e"
            cert = "cc8ed10e6bcf11e8adef00155df1fe0e"
            turn = "cc8f29576bcf11e8adef00155df1fe0e"
            # print('TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT')
            # print(StudentApp.birth_date)
            dt = ""
            if (StudentApp.birth_date):
                dt = datetime.datetime.strptime(StudentApp.birth_date, '%Y-%m-%d').strftime('%d/%m/%Y')
            else:
                dt = "01/01/2020"
            url = "https://me.horus.edu.eg/WebServiceHorus?index=AddQualificationStudents&PreQualification=" + urllib.parse.quote(
                str(StudentApp.certificate_id.d_id)) + "&School=" + urllib.parse.quote(
                str(StudentApp.school_name)) + "&SeatNo=" + urllib.parse.quote(str(
                StudentApp.seat_no)) + "&PreQualificationYear=916811fdc1c811eaa10d00155d06c800&PreQualificationTurn=cc8f2a426bcf11e8adef00155df1fe0e&PreQualificationDegree=" + urllib.parse.quote(
                str(StudentApp.certificate_degree)) + "&Percentage=" + urllib.parse.quote(str(
                StudentApp.certificate_percentage)) + "&Sat1=1245&Sat2=1246&AcceptType=cc8fc68c6bcf11e8adef00155df1fe0e&CoordNo=15454%20&CoordDate=1/1/2019&Institute=%D8%A7%D9%84%D8%BA%D8%B1%D8%A8%D9%8A%D8%A9&InstJoinYear=916811fdc1c811eaa10d00155d06c800&scopeId=" + urllib.parse.quote(
                str(FacultyID)) + "&progId=" + urllib.parse.quote(str(ProgramID)) + "&stuCode=" + urllib.parse.quote(
                str(StudentApp.Student_code)) + "&transformType=cc6538586bcf11e8adef00155df1fe0e"
            # url = "https://me.horus.edu.eg/WebServiceHorus?index=AddQualificationStudents&PreQualification="+urllib.parse.quote(str(StudentApp.certificate_id.d_id))+"&School="+urllib.parse.quote(str(StudentApp.school_name))+"&SeatNo="+urllib.parse.quote(str(StudentApp.seat_no))+"&PreQualificationYear="+urllib.parse.quote(str(cert))+"&PreQualificationTurn=cc8f2a426bcf11e8adef00155df1fe0e&PreQualificationDegree="+urllib.parse.quote(str(StudentApp.certificate_degree))+"&Percentage="+urllib.parse.quote(str(StudentApp.certificate_percentage))+"&Sat1=&Sat2=&AcceptType=cc8fc68c6bcf11e8adef00155df1fe0e&CoordNo=&CoordDate=&Institute=&InstJoinYear=cc8f54386bcf11e8adef00155df1fe0e&scopeId="+urllib.parse.quote(str(FacultyID))+"&progId="+urllib.parse.quote(str(ProgramID))+"&stuCode="+urllib.parse.quote(str(StudentApp.Student_code))+"&transformType="
            xx = xx + 1
            print(url)
            # print(StudentApp.Student_code)
            req = urllib2.Request(url, headers={'X-Mashape-Key': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'})
            gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)  # Only for gangstars
            webURL = urllib2.urlopen(req, context=gcontext)


class opStudentsStudyTimetable(models.Model):
    _inherit = 'op.student'

    # student_timetable_ids = fields.One2many('op.studytimetable','student_id')
    @api.model
    def getstustudyTimetable_data_old(self, stucode=''):
        # ('student_code','!=',3161110)('faculty','=',6),('student_code','=',5171122)
        xx = 0
        status_ids = (self.env['hue.std.data.status'].search([('active_invoice', '=', True)])._ids)
        if stucode == '':
            students = self.env['op.student'].sudo().search([('student_status', 'in', status_ids)])  # ,limit = 50)
        else:
            students = self.env['op.student'].sudo().search(
                [('student_code', '=', stucode), ('student_status', 'in', status_ids)])  # ,limit = 50)
        #
        # else :
        #     students = self.env['op.student'].sudo().search([('student_code','=',stucode),('student_status','in',status_ids)])#,limit = 50)

        for student in students:
            # student.student_timetable_ids.sudo().unlink()
            url = "https://me.horus.edu.eg/WebServiceFarouk?index=GetStudentTimetable&studentCode=" + str(
                student.student_code) + "&year=916811fdc1c811eaa10d00155d06c800&semester=cc8f49106bcf11e8adef00155df1fe0e"  # +str(student.student_code)
            xx = xx + 1
            # print(url)
            # print(xx)
            req = urllib2.Request(url, headers={'X-Mashape-Key': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'})
            gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)  # Only for gangstars
            webURL = urllib2.urlopen(req, context=gcontext)
            data = webURL.read()
            encoding = webURL.info().get_content_charset('utf-8')

            stuid = student.id
            stufacultyid = student.faculty.id
            CourseID = ''
            courseid = self.env['op.student.accumulative'].search(
                [('student_id', '=', stuid), ('academicyear_id', '=', 117)], limit=1)
            CourseID = courseid.course_id.id
            if not courseid:
                courseid = self.env['op.course'].search([('faculty_id', '=', stufacultyid)], limit=1)
                CourseID = courseid.id

            data = json.loads(data.decode(encoding))
            AcadYearID = 117
            stuAccID = self.env['op.student.accumulative'].sudo().search(
                [('student_id', '=', student.id), ('course_id', '=', CourseID), ('academicyear_id', '=', AcadYearID)])
            if not stuAccID:
                stuAccID = self.env['op.student.accumulative'].sudo().create(
                    {'student_id': student.id, 'course_id': courseid.id, 'academicyear_id': AcadYearID})

            StuAccSemID = self.env['op.student.accumlative.semesters'].sudo().search(
                [('student_accum_id', '=', stuAccID.id), ('semester_id', '=', 2)])
            if not StuAccSemID:
                StuAccSemID = self.env['op.student.accumlative.semesters'].sudo().create(
                    {'student_accum_id': stuAccID.id, 'academicyear_id': 117, 'semester_id': 2, 'semester_status': 2})

            self.env['op.student.semesters.subjects'].sudo().search(
                [('student_semester_id', '=', StuAccSemID.id)]).unlink()

            if not data:
                continue
            if not 'studentTimetable' in data:
                continue
            for val in data["studentTimetable"]:
                if 'subjectName' in val:
                    SubjectName = val["subjectName"]
                    SubjectCode = val["subjectCode"]
                    for val2 in val['courseTimetable']:
                        Lecturer = val2["lecturer"]
                        FromDate = val2["fromDate"]
                        ToDate = val2["toDate"]
                        PlaceCode = val2["place"]
                        StudentSection = val2["studentSection"]
                        StudentGroup = val2["studentGroup"]
                        Place = val2["placeCode"]
                        Type = val2["type"]
                        Day = val2["day"]
                        Lecturer = val2["lecturer"]
                        LecturerIDs = val2["lecturerIDs"]

                        SubjectID = self.env['op.subject'].search([('subject_code', '=', SubjectCode)], limit=1)
                        print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAa')
                        print(SubjectCode)
                        print(SubjectID)
                        if not SubjectID:
                            print('BBBBBBBBBBBBBBBBBBB')
                            SubjectID = self.env['op.subject'].search(
                                [('subject_code', '=', SubjectCode + '|' + SubjectCode)], limit=1)
                        if not SubjectID:
                            print('BBBBBBBBBBBBBBBBBBB')
                            SubjectID = self.env['op.subject'].search(
                                [('subject_code', 'ilike', SubjectCode.split('|')[0])], limit=1)
                        if not SubjectID:
                            # print('DDDDDDDDDDDDDDDDDDDDDDDDDDD')
                            # print(SubjectCode)
                            continue

                        Place = self.env['op.places'].sudo().search([('code', '=', PlaceCode)], limit=1)
                        if not Place:
                            Place = self.env['op.places'].sudo().create({'code': PlaceCode})
                        PlaceID = Place.id

                        StudyType = self.env['op.studytypes'].sudo().search([('name', '=', Type)])
                        if not StudyType:
                            StudyType = self.env['op.studytypes'].sudo().create({'name': Type})
                        StudyTypeID = StudyType.id

                        StudyTimeTable = self.env['op.studytimetable'].sudo().search(
                            [('subject_id', '=', SubjectID.id), ('course_id', '=', CourseID),
                             ('studytype', '=', StudyTypeID), ('from_date', '=', FromDate), ('daydate', '=', Day),
                             ('groupno', '=', StudentGroup), ('sectionno', '=', StudentSection), ('acadyear', '=', 117),
                             ('semester', '=', 2)], limit=1)
                        # print('11111111111111111111111111111')
                        if not StudyTimeTable:
                            # print('22222222222222222222222222222')
                            StudyTimeTable = self.env['op.studytimetable'].sudo().create(
                                {'course_id': CourseID, 'subject_id': SubjectID.id, 'acadyear': '117', 'semester': '2',
                                 'from_date': FromDate, 'to_date': ToDate, 'placeid': PlaceID, 'daydate': Day,
                                 'groupno': StudentGroup, 'sectionno': StudentSection, 'studytype': StudyTypeID,
                                 'lecturer': Lecturer, 'lecturernids': LecturerIDs})

                        StudyTimeTableID = StudyTimeTable.id

                        StuSubjectID = self.env['op.student.semesters.subjects'].sudo().search(
                            [('student_semester_id', '=', StuAccSemID.id), ('subject_id', '=', SubjectID.id)])
                        if not StuSubjectID:
                            StuSubjectID = self.env['op.student.semesters.subjects'].sudo().create(
                                {'student_semester_id': StuAccSemID.id, 'subject_id': SubjectID.id})

                        if StuSubjectID and StudyTimeTableID:
                            StuSubjectID.sudo().write({'studytable_id': StudyTimeTableID, 'group_id': StudentGroup})

                        if StudentSection != '':
                            StuSubjectID.sudo().write({'section_id': StudentSection})

                        if not StudyTimeTable.placeid:
                            StuSubjectID.sudo().write({'placeid': PlaceID})


class opStudentsAttendance(models.Model):
    _inherit = 'op.student'
    student_attendance_ids = fields.One2many('op.attendance', 'student_id')

    @api.model
    def getstuattendance_data(self, stucode='', lmt=100, ofst=0):
        # ('student_code','!=',3161110)('faculty','=',6),('student_code','=',5171122)
        xx = 0
        status_ids = (self.env['hue.std.data.status'].sudo().search([('active_invoice', '=', True)])._ids)
        if stucode == '':
            students = self.env['op.student'].sudo().search([('student_status', 'in', status_ids)],
                                                            order='student_code', limit=lmt,
                                                            offset=ofst)  # ,limit = 50)
        else:
            students = self.env['op.student'].sudo().search([('student_code', '=', stucode)])  # ,limit = 50)

        for student in students:
            student.student_attendance_ids.sudo().unlink()
            url = "https://me.horus.edu.eg/WebServiceHorus?index=GetPerStudentAbsenceReport&userName=myd777myd&passWord=lo@stmm&studentID=" + str(
                student.student_code) + "&studyYear=2019-2020&studySemester=2:8000"
            xx = xx + 1
            print('-------WADOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOD------- ' + str(student.student_code))
            # print('Number : '+xx+)
            print(xx)
            req = urllib2.Request(url, headers={'X-Mashape-Key': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'})
            gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)  # Only for gangstars
            webURL = urllib2.urlopen(req, context=gcontext)
            data = webURL.read()
            encoding = webURL.info().get_content_charset('utf-8')

            stuid = student.id
            stufacultyid = student.faculty.id
            courseid = self.env['op.course'].search([('faculty_id', '=', stufacultyid)], limit=1)
            data = json.loads(data.decode())
            if not data:
                continue
            # print(data)
            if 'Data' in data:
                for val in data["Data"]:
                    for val2 in data["Data"][val]:
                        for val3 in val2:
                            AbsenceDate = val2["Absence_date"]
                            percentage = val2["percentage"]
                            datatype = val2["type"]
                            AbsenceNo = val2["counts"]
                            SubjectCode = val2["crsCode"]
                            Type = val2["type"]
                            subjectmapid = val2["crsID"]
                            # StuAccID = request.env['op.student.accumulative'].sudo().search([('student_id', '=', stuid)])#
                            # SubjectID = self.env['op.course.subjects'].search([('subject_code', '=', SubjectCode)],limit =1)
                            SubjectID = self.env['op.subject'].search([('subject_code', '=', SubjectCode)],
                                                                              limit=1)

                            print(SubjectCode)
                            print(SubjectID)
                            if not SubjectID:
                                # print('BBBBBBBBBBBBBBBBBBB')
                                SubjectID = self.env['op.subject'].search(
                                    [('subject_code', '=', SubjectCode + '|' + SubjectCode)], limit=1)
                            if not SubjectID:
                                # print('BBBBBBBBBBBBBBBBBBB')
                                SubjectID = self.env['op.subject'].search(
                                    [('subject_code', 'ilike', SubjectCode.split('|')[0])], limit=1)
                            if not SubjectID:
                                # print('DDDDDDDDDDDDDDDDDDDDDDDDDDD')
                                # print(SubjectCode)
                                continue
                            semesterID = self.env['op.semesters'].sudo().search([('id', '=', '2')])
                            acadyearID = self.env['op.academic.year'].sudo().search([('year', '=', '2019')])

                            StudyType = self.env['op.studytypes'].sudo().search([('name', '=', Type)])
                            if not StudyType:
                                StudyType = self.env['op.studytypes'].sudo().create({'name': Type})
                            StudyTypeID = StudyType.id

                            AttendanceID = self.env['op.attendance'].sudo().search(
                                [('student_id', '=', stuid), ('course_id', '=', courseid.id),
                                 ('subject_id', '=', SubjectID.id), ('acadyear', '=', acadyearID.id),
                                 ('absencedate', '=', AbsenceDate), ('semester', '=', semesterID.id),
                                 ('attendancetype', '=', StudyTypeID)])
                            if not AttendanceID:
                                AttendanceID = self.env['op.attendance'].sudo().create(
                                    {'course_id': courseid.id, 'student_id': stuid, 'subject_id': SubjectID.id,
                                     'acadyear': acadyearID.id, 'semester': semesterID.id, 'absencedate': AbsenceDate,
                                     'percentage': percentage, 'absenceno': AbsenceNo, 'attendancetype': StudyTypeID,
                                     'subjectmapid': subjectmapid})
                            AttendanceID = AttendanceID.id

                            if 'Allstd' in data:
                                for XX in data["Allstd"]:
                                    StuAttendanceID = self.env['op.attendance'].sudo().search(
                                        [('student_id', '=', stuid), ('course_id', '=', courseid.id),
                                         ('subject_id', '=', SubjectID.id), ('acadyear', '=', acadyearID.id),
                                         ('semester', '=', semesterID.id), ('attendancetype', '=', StudyTypeID),
                                         ('subjectmapid', '=', subjectmapid)])
                                    # print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
                                    # print(StuAttendanceID)
                                    # print(AbsenceDate)
                                    # print(XX)
                                    StuAttendanceID.sudo().write({'totpercentage': data["Allstd"][subjectmapid]})


class opStudentsExamTimetable(models.Model):
    _inherit = 'op.student'

    @api.model
    def getstuExamTimetable_data(self, stucode):
        # ('student_code','!=',3161110)('faculty','=',6),('student_code','=',5171122)
        xx = 0
        status_ids = (self.env['hue.std.data.status'].search([('active_invoice', '=', True)])._ids)
        if stucode == '':
            students = self.env['op.student'].sudo().search(
                [('faculty', '=', 7), ('student_status', 'in', status_ids)])  # ,limit = 50)
        else:
            students = self.env['op.student'].sudo().search(
                [('student_code', '=', stucode), ('student_status', 'in', status_ids)])  # ,limit = 50)
        AcadYearID = self.env['op.academic.year'].sudo().search([('current', '=', True)], limit=1).id
        semester_id = self.env['op.semesters'].sudo().search([('current', '=', True)], limit=1).id

        for student in students:
            url = "https://me.horus.edu.eg/WebServiceHorus?index=GetStudentExamTimeTable&userName=myd777myd&password=lo@stmm&studentID=" + str(
                student.student_code)
            xx = xx + 1
            req = urllib2.Request(url, headers={'X-Mashape-Key': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'})
            gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)  # Only for gangstars
            webURL = urllib2.urlopen(req, context=gcontext)
            data = webURL.read()
            encoding = webURL.info().get_content_charset('utf-8')

            stuid = student.id
            stufacultyid = student.faculty.id
            # courseid = self.env['op.course'].search([('faculty_id', '=', stufacultyid)],limit = 1)
            courseid = student.course_id
            data = json.loads(data.decode(encoding))
            print("datadatadatadata")
            print(data["Data"])
            print(data["Data"])
            if data["Data"] == None:
                continue
            for val in data["Data"]:
                if not val["FromDate"]:
                    continue
                if 'CourseName' in val:
                    CourseName = val["CourseName"]
                    CourseCode = val["CourseCode"]
                    SeatNum = val["SeatNum"]
                    FromDate = val["FromDate"]
                    ToDate = val["ToDate"]
                    BuildingName = val["BuildingName"]
                    PlaceCode = val["PlaceCode"]
                    CommitteeName = val["CommitteeName"]
                    DayDate = val["DayDate"]
                    # acadyear = "2019-2020"
                    # semester = "الثانى"
                    print(DayDate)

                    SubjectID = self.env['op.subject'].search(
                        [('subject_code', '=', CourseCode), ('course_id', '=', courseid.id)], limit=1)
                    if not SubjectID:
                        SubjectID = self.env['op.subject'].search(
                            [('subject_code', '=', CourseCode + '|' + CourseCode), ('course_id', '=', courseid.id)],
                            limit=1)
                    if not SubjectID:
                        SubjectID = self.env['op.subject'].search(
                            [('subject_code', 'ilike', CourseCode.split('|')[0]), ('course_id', '=', courseid.id)],
                            limit=1)
                    if not SubjectID:
                        SubjectID = self.env['op.subject'].search(
                            [('subject_code', '=', CourseCode), ('course_id', '=', courseid.parent_id.id)], limit=1)
                    if not SubjectID:
                        SubjectID = self.env['op.subject'].search(
                            [('subject_code', '=', CourseCode + '|' + CourseCode),
                             ('course_id', '=', courseid.parent_id.id)], limit=1)
                    if not SubjectID:
                        SubjectID = self.env['op.subject'].search(
                            [('subject_code', 'ilike', CourseCode.split('|')[0]),
                             ('course_id', '=', courseid.parent_id.id)], limit=1)

                    # SubjectID = self.env['op.course.subjects'].search([('subject_code', '=', CourseCode), '|', ('course_id', '=', courseid.id), ('course_id', '=', courseid.parent_id.id)],limit = 1)
                    # if not SubjectID:
                    #     SubjectID = self.env['op.course.subjects'].search([('subject_code', 'ilike', CourseCode.split('|')[0]), '|', ('course_id', '=', courseid.id), ('course_id', '=', courseid.parent_id.id)],limit = 1)
                    print('1111111111111111111111111111')
                    print(CourseCode)
                    print(SubjectID.id)
                    Committee = self.env['op.committees'].sudo().search([('name', '=', val['CommitteeName'])], limit=1)
                    if not Committee:
                        Committee = self.env['op.committees'].sudo().create({'name': val['CommitteeName']})
                    CommitteeID = Committee.id

                    Place = self.env['op.places'].sudo().search([('code', '=', val['PlaceCode'])], limit=1)
                    if not Place:
                        Place = self.env['op.places'].sudo().create({'code': val['PlaceCode']})
                    PlaceID = Place.id

                    Building = self.env['op.buildings'].sudo().search([('name', '=', val['BuildingName'])])
                    if not Building:
                        Building = self.env['op.buildings'].sudo().create({'name': val['BuildingName']})
                    BuildingID = Building.id

                    # semesterID = self.env['op.semesters'].sudo().search([('name', 'ilike', semester)])

                    # acadyearID = self.env['hue.joining.years'].sudo().search([('name', '=', acadyear)])

                    ExamCommittee = self.env['op.exam.committees'].sudo().search(
                        [('course_id', '=', courseid.id), ('committeeid', '=', CommitteeID),
                         ('subject_id', '=', SubjectID.id), ('acadyear', '=', AcadYearID),
                         ('semester', '=', semester_id), ('from_date', '=', FromDate), ('daydate', '=', DayDate)],
                        limit=1)
                    print('____________________________')
                    print(ExamCommittee)
                    if not ExamCommittee:
                        ExamCommittee = self.env['op.exam.committees'].sudo().create(
                            {'course_id': courseid.id, 'subject_id': SubjectID.id, 'acadyear': AcadYearID,
                             'semester': semester_id, 'from_date': FromDate, 'to_date': ToDate, 'placeid': PlaceID,
                             'buildingid': BuildingID, 'committeeid': CommitteeID, 'daydate': DayDate})
                        print(ExamCommittee)
                    ExamCommitteeID = ExamCommittee.id

                    StuAccID = self.env['op.student.accumulative'].sudo().search(
                        [('student_id', '=', student.id), ('academicyear_id', '=', AcadYearID)], limit=1)  #
                    StuSemesterID = self.env['op.student.accumlative.semesters'].sudo().search(
                        [('student_accum_id', '=', StuAccID.id), ('academicyear_id', '=', AcadYearID),
                         ('semester_id', '=', semester_id)], limit=1)
                    StuSubjectID = self.env['op.student.semesters.subjects'].sudo().search(
                        [('student_semester_id', '=', StuSemesterID.id), ('subject_id', '=', SubjectID.id)])
                    print(StuSubjectID)
                    print('===============================')
                    if StuSubjectID and ExamCommitteeID:
                        print('999999999999999999999999999999999999999')
                        StuSubjectID.sudo().write({'seatno': SeatNum, 'committee_id': ExamCommitteeID})


class opStudentsAdvisorsext(models.Model):
    _inherit = 'op.student'
    
    def semester_is_published(self, courseid, acadyear, semester):
        published = self.env['op.course.resultspublish'].sudo().search(
            [('course_id', '=', courseid), ('acadyears', '=', acadyear), ('semesters', '=', semester)]).publishflag
        # print(published)
        if published:
            if published == 'publish':
                return True
        return False;

    def checkblock(self):
        blocked = False
        invoice_count = 0
        #  # ('date_due', '<=', date.today()), 
        if not self.allow_registration:
            domain = [
                ('move_type', 'in', ['out_invoice']),
                ('invoice_date_due', '<=', '2023-09-19'),             
                ('partner_id', '=', self.partner_id.id),
                ('state', 'in', ['draft'])
            ]
            invoice_count = self.env['account.move'].sudo().search_count(domain)

        accum_semesters = self.env['op.student.accumlative.semesters'].sudo().search(
            [('student_id', '=', self.id),('semester_gpa', '!=', False),
             ('transferred', '=', False)],order="id desc",limit=1) #,('academicyear_id.run_semester_gpa', '=', True),('semester_id.run_semester_gpa', '=', True)
        for semss in accum_semesters:
            # if semss.course_id.faculty_id.check_questionnaire :
            #     if not self.questionnaire_done() :
            #         blocked = True
            #         break
            
            if not self.semester_is_published(semss.course_id.id, semss.academicyear_id.id,semss.semester_id.id) :
                blocked = True
                break
            if    invoice_count > 0 or  semss.block_result:
                blocked = True
                break
        print("blocked:--------------------------------------------------", blocked)
        return blocked

    @api.model
    def getstuAdvisor_data(self, stucode):
        status_ids = (self.env['hue.std.data.status'].search([('active_invoice', '=', True)])._ids)
        # students = self.env['op.student'].search([('student_status', 'in', status_ids)])  # ,limit = 50)
        if stucode == '':
            students = self.env['op.student'].search([('student_status', 'in', status_ids)])
        else:
            students = self.env['op.student'].sudo().search(
                [('student_code', '=', stucode), ('student_status', 'in', status_ids)])  # ,limit = 50)

        for student in students:
            url = "https://me.horus.edu.eg/WebServiceHorus?index=GetStudentAdvisorData&studentID=" + str(
                student.student_code) + "&userName=myd777myd&password=lo@stmm"

            req = urllib2.Request(url, headers={'X-Mashape-Key': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'})
            gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)  # Only for gangstars
            webURL = urllib2.urlopen(req, context=gcontext)
            data = webURL.read()
            encoding = webURL.info().get_content_charset('utf-8')

            stuid = student.id
            stufacultyid = student.faculty.id
            courseid = self.env['op.course'].search([('faculty_id', '=', stufacultyid)], limit=1)

            data = json.loads(data.decode(encoding))
            print(data)
            print(student.student_code)
            if not data:
                continue

            for val in data['data']:
                DrID = val["DrID"]
                StartDate = datetime.datetime.strptime(str(val["SartDate"]), '%d/%m/%Y').strftime('%Y-%m-%d')
                print(StartDate)
                if val["EndDate"]:
                    EndDate = datetime.datetime.strptime(str(val["EndDate"]), '%d/%m/%Y').strftime('%Y-%m-%d')
                else:
                    EndDate = ''
                Dr_ID = self.env['op.faculty'].search([('id_number', '=', DrID)], limit=1)
                if Dr_ID:
                    Advisor = self.env['hue.academic.direction'].sudo().search([('faculty_id', '=', Dr_ID.id)], limit=1)

                    if not Advisor:
                        Advisor = self.env['hue.academic.direction'].sudo().create(
                            {'college_id': stufacultyid, 'faculty_id': Dr_ID.id})
                        print(Advisor)

                    AdvisorID = Advisor.id
                    StuAdvisor = self.env['hue.academic.direction.line'].sudo().create(
                        {'acad_dir_id': AdvisorID, 'student_id': stuid, 'from_date': str(StartDate),
                         'to_date': str(EndDate)})

    @api.model
    def medregistration_data(self,student_level,subject_level,subject_semester,semester,groupid):
        status_ids = (self.env['hue.std.data.status'].search([('active_invoice', '=', True)])._ids)
        if semester == 3:
            students_ = self.env['student.study.groups'].sudo().search([('study_group_id', '=', groupid)])
            students_ids = students_.mapped('student_id').ids
            students = self.env['op.student'].search([('id', 'in', students_ids)]) 
        else:
            students = self.env['op.student'].search(
                [('student_status', 'in', status_ids), ('faculty', '=', 12), ('level', '=', student_level)])  # ,limit = 50)
        
        for student in students:
            stuAccID = self.env['op.student.accumulative'].sudo().search(
                [('student_id', '=', student.id), ('course_id', '=', student.course_id.id),
                 ('academicyear_id', '=', 69533)], limit=1)
            if not stuAccID:
                stuAccID = self.env['op.student.accumulative'].sudo().create(
                    {'student_id': student.id, 'course_id': student.course_id.id, 'academicyear_id': 69533})
            StuAccSemID = self.env['op.student.accumlative.semesters'].sudo().search(
                [('student_accum_id', '=', stuAccID.id), ('semester_id', '=', semester)])
            if not StuAccSemID:
                StuAccSemID = self.env['op.student.accumlative.semesters'].sudo().create(
                    {'student_accum_id': stuAccID.id, 'academicyear_id': 69533, 'semester_id': semester, 'semester_status': 2})

            # stucourses = self.env['op.course.subjects'].search(
            #     [('course_id', '=', 15), ('subject_level', '=', subject_level), ('subject_semester', '=', subject_semester)])
            stucourses = self.env['op.subject'].search([('id', 'in', subject_level)])
            print('323232323233333333333332222')
            print(stucourses)
            for sub in stucourses:
                stuSemSubID = self.env['op.student.semesters.subjects'].sudo().search(
                    [('student_semester_id', '=', StuAccSemID.id), ('subject_id', '=', sub.id)])
                if not stuSemSubID:
                    self.env['op.student.semesters.subjects'].sudo().create(
                        {'student_semester_id': StuAccSemID.id, 'subject_id': sub.id})
                    
                        
    @api.model
    def accumulated_hours(self,course):
        parent_course = self.env['op.course'].search([('id', '=', course)])
        status_ids = self.env['hue.std.data.status'].search([('active_invoice', '=', True)])._ids
        students = self.env['op.student.accumlative.semesters'].search(['|' ,('course_id', '=', course),('course_id', '=', parent_course.parent_id.id),('student_id.student_status', 'in', status_ids),
                    ('transferred' , '=' , False)])
        students = students.mapped('student_id')
        for student in students:
            earned_hour =0 
            accu_hours = 0
            semester_hour = 0
            subjects =[]
            academicyear =self.env['op.student.accumulative'].search(['|' ,('course_id', '=', course),('course_id', '=', parent_course.parent_id.id),('student_id', '=', student.id)],order="academicyear_id desc")
            for x in academicyear :
                last_level_earned_hours = self.env['op.student.accumlative.semesters'].sudo().search(['|' ,('course_id', '=', course),('course_id', '=', parent_course.parent_id.id),('student_id', '=', student.id),
                                ('academicyear_id', '=', x.academicyear_id.id),('transferred' , '=' , False)]) #,order="semester_id"
                for accu_sem in last_level_earned_hours.sorted(key=lambda r: r.semester_id.sequence ) :
                    if accu_sem.student_id.semester_is_published(course, accu_sem.academicyear_id.id,accu_sem.semester_id.id) :
                        if accu_sem.student_id.course_id.id == 15:
                            if accu_sem.semester_id.id != 3 :
                                if  accu_sem.grade.pass_grade or accu_sem.control_grade.pass_grade :
                                    earned_hour =0 
                                    for sub in accu_sem.accum_semesters_subjects_ids :
                                        if  sub.subject_id.subject_addtogpa and sub.subject_id.subject_credithours :
                                            earned_hour = earned_hour + sub.subject_credit
                                        elif  not sub.subject_id.subject_addtogpa and sub.subject_id.subject_credithours :
                                            if  sub.final_grade.pass_grade :
                                                earned_hour = earned_hour + sub.subject_credit
                                            else :
                                                summer_acc = self.env['op.student.semesters.subjects'].sudo().search([('student_id', '=', student.id),
                                                    ('subject_id', '=', sub.subject_id.id) ,('semester_id', '=', 3) ,('academicyear_id', '=', accu_sem.academicyear_id.id),
                                                    ('student_semester_id.transferred' , '=' , False)]) 
                                                if summer_acc.final_grade.pass_grade :
                                                    earned_hour = earned_hour + sub.subject_credit
                                    accu_sem.write({'semester_hr': earned_hour})
                                    accu_sem.write({'earned_hours': earned_hour})
                                    accu_hours = accu_hours + accu_sem.semester_hr
                                    accu_sem.write({'accumulated_hours': accu_hours})
                                else :
                                    accu_sem.write({'semester_hr': 0})
                                    accu_sem.write({'earned_hours': 0})
                                    accu_hours = accu_hours + accu_sem.semester_hr
                                    accu_sem.write({'accumulated_hours': accu_hours})
                            else :
                                before_summer_earned_hours = self.env['op.student.accumlative.semesters'].sudo().search([('student_id', '=', student.id),
                                         ('semester_id', '!=', 3) ,('academicyear_id', '=', accu_sem.academicyear_id.id),('transferred' , '=' , False)],order="semester_id desc" ,limit=1) 
                                accu_sem.write({'semester_hr': 0})
                                accu_sem.write({'earned_hours': 0})
                                accu_sem.write({'accumulated_hours': before_summer_earned_hours.accumulated_hours})
                            student.write({'new_crh': accu_hours})
                            level = self.env['op.course.levels'].sudo().search(
                                [('course_id', '=', student.course_id.id),
                                 ('hours_from', '<=', student.new_crh),
                                 ('hours_to', '>', student.new_crh)], limit=1).level_id.level_id.id 
                            student.write({'level': level})
                        else :
                            for subj in accu_sem.accum_semesters_subjects_ids :
                                if subj.final_grade.pass_grade :
                                    if subj.subject_id.id not in  subjects :
                                        semester_hour = semester_hour + subj.subject_credit
                                        subjects.append(subj.subject_id.id)
                            accu_sem.write({'accumulated_hours': semester_hour})
    
                
                      
    @api.model
    def med_summer_result(self,course):
        academic_year = self.env['op.academic.year'].sudo().search([('sequence', '!=', 0)])
        curr_semester = self.env['op.semesters'].sudo().search([('id', '=', 3)], limit=1).id
        for year in academic_year :
            students_semesters = self.env['op.student.accumlative.semesters'].search([('course_id', '=', 15),
                        ('semester_id' , '=' , 3),('academicyear_id' , '=' , year.id),
                        ('transferred' , '=' ,False)])
            
            semesters = self.env['op.semesters'].sudo().search([('id', '<', 3)])
                                
            for student_semester in students_semesters:
                for semester in semesters:
                    numerator = 0  # بسط فوق
                    denominator = 0  # مقام
                    crh_denominator = 0
                    final_degree = 0
                    total_essay_mcq = 0
                    essay_mcq_degree = 0
                    final_total_essay_mcq = 0
                    grade = False
                    curr_grade = False
                    semester_current_gpa = 0
                    done_subject= self.env['op.student.semesters.subjects'].sudo().search([
                            ('semester_id', '!=', 3),('student_id', '=', student_semester.student_id.id)])
                    done_subject = done_subject.mapped('subject_id').ids 
                    student_subjects = self.env['op.student.semesters.subjects'].sudo().search([('student_semester_id', '=', student_semester.id)
                       ,('subject_id', 'in',done_subject) , ('subject_id.subject_semester', '=', semester.id),('student_id', '=', student_semester.student_id.id)])
                    
                    for subject in student_subjects:
                        subject_grade = subject.final_grade
                        if subject.subject_id.subject_addtohours and subject.subject_id.subject_addtogpa:
                            crh_denominator = crh_denominator + subject.subject_id.subject_credithours
                        elif subject.subject_id.subject_addtohours and  subject_grade.pass_grade:
                            crh_denominator = crh_denominator + subject.subject_id.subject_credithours
                        if subject.subject_id.subject_addtogpa:
                            # total_essay_mcq = total_essay_mcq + 55
                            essay_mcq_degree = essay_mcq_degree + subject.grade_mcq + subject.grade_eassy
                            denominator = denominator + subject.subject_id.subject_total
                            numerator = numerator + subject.final_degree
                        
                        chk_subject = self.env['op.student.semesters.subjects'].sudo().search([('subject_id', '=', subject.subject_id.id)
                            , ('semester_id', '!=', 3),('student_id', '=', student_semester.student_id.id),('academicyear_id' , '=' , year.id)])
                       
                    if denominator > 0:
                        final_degree = math.ceil(numerator) / denominator
                        final_degree = final_degree * 100
                        final_degree = round(final_degree , 2)
                        
                        student = student_semester.student_id
                        if student.level.id == 2:
                            total_essay_mcq = 190
                        elif student.level.id  == 3:
                            total_essay_mcq = 220
                        elif student.level.id  == 4:
                            total_essay_mcq = 220
                        elif student.level.id  == 5:
                            total_essay_mcq = 210
                        else:
                            total_essay_mcq = 220
                        
                        grade = self.env['op.course.grades'].sudo().search(
                            [('course_id', '=', student.course_id.id), ('percent_to', '>', final_degree),
                             ('percent_from', '<=', final_degree)])
                        final_total_essay_mcq = (round(essay_mcq_degree, 2) / total_essay_mcq) * 100
                        curr_grade = grade.grade_id.id
                        semester_current_gpa = grade.points_from
                        if final_total_essay_mcq < 40:
                            curr_grade = 25
                            crh_denominator = 0
                        if grade.grade_id.pass_grade:
                            if chk_subject.student_semester_id.grade.id not in [1,26] :
                                deduction_grade_first = self.env['op.course.grades'].sudo().search(
                                    [('course_id', '=', student.course_id.id),
                                     ('grade_id', '=', student.course_id.deduction_grade_first.id)],
                                    limit=1).percent_to
                                if deduction_grade_first <= final_degree:
                                    final_degree = float(
                                        (deduction_grade_first * denominator) / 100) - 0.5
                                    final_degree = (final_degree / denominator )*100
                                    curr_grade = student.course_id.deduction_grade_first.id
                        print("jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj")
                        print(chk_subject.student_semester_id)
                        chk_subject.student_semester_id.sudo().write(
                            {'semester_gpa': float(semester_current_gpa), 'current_gpa': float(semester_current_gpa),
                             # 'semester_hr': crh_denominator, 'earned_hours': crh_denominator,
                             # 'accumulated_hours': tot_crh_denominator,
                             'semester_current_gpa': float(semester_current_gpa),
                             'total_degree': math.ceil(numerator),
                             'total_max': denominator,
                             'control_degree': final_degree,
                             'control_grade':curr_grade,
                             })
                                   
    @api.model
    def get_student_degree(self,course_id , gpa):
        curr_academic_year = self.env['op.academic.year'].sudo().search([('id', '=', 69533)], limit=1)
        curr_semester = self.env['op.semesters'].sudo().search([('id', '=', 2)], limit=1)
        status_ids = self.env['hue.std.data.status'].search([('active_invoice', '=', True)])._ids
        students = self.env['op.student.accumlative.semesters'].sudo().search([('course_id', '=', course_id),
            ('student_id.student_status', 'in', status_ids),('current_gpa', '>=', gpa), ('transferred', '=', False),
            ('academicyear_id', '=',curr_academic_year.id),('semester_id', '=',curr_semester.id)])
        for student in students :
            if not student.accumulated_degree :
                accum_semesters_subjects = self.env['op.student.semesters.subjects'].sudo().search(
                    [('subject_grade', '!=', False), ('student_id', '=', student.student_id.id),
                     ('final_grade.pass_grade', '=', True), ('final_grade', 'not in', [20, 4, 6,27]),
                     ('student_semester_id.transferred', '=', False),
                     ('academicyear_id.sequence', '<=',curr_academic_year.sequence)])
                subject_ids = accum_semesters_subjects.mapped('subject_id').ids
                subject_ids = list(dict.fromkeys(subject_ids))
                numerator = 0  # بسط فوق
                denominator = 0  # مقام
                for subject in subject_ids:
                    if student.student_id.faculty.id == 9 :
                        accum_subject = self.env['op.student.semesters.subjects'].sudo().search(
                        [('subject_grade', '!=', False), ('subject_id', '=', subject),
                         ('final_grade.pass_grade', '=', True), ('final_grade', 'not in', [20, 4, 6,27]),
                         ('student_id', '=', student.student_id.id), ('student_semester_id.transferred', '=', False),
                         ('academicyear_id.sequence', '<=', curr_academic_year.sequence)
                         ], order='id desc', limit=1)
                    else :
                        accum_subject = self.env['op.student.semesters.subjects'].sudo().search(
                            [('subject_grade', '!=', False), ('subject_id', '=', subject),
                             ('final_grade.pass_grade', '=', True), ('final_grade', 'not in', [20, 4, 6,27]),
                             ('student_id', '=', student.student_id.id), ('student_semester_id.transferred', '=', False),
                             ('academicyear_id.sequence', '<=',curr_academic_year.sequence)
                             ], order='final_degree desc', limit=1)
                    subject_grade = accum_subject.final_grade
                    if subject_grade.pass_grade and subject_grade.id not in [20, 4, 6,27]:
                        if  accum_subject.academicyear_id.id == 69533:
                            if  accum_subject.semester_id.id != 3 :
                                numerator = numerator + accum_subject.final_degree
                        else :
                            numerator = numerator + accum_subject.final_degree
                if subject_ids:
                    numerator = round(numerator, 2) 
                    total_degree = numerator
                    accum_semester = self.env['op.student.accumlative.semesters'].sudo().search(
                            [('student_id', '=', student.student_id.id), ('transferred', '=', False),
                             ('academicyear_id', '=',curr_academic_year.id),('semester_id', '=',curr_semester.id),
                             ('accum_semesters_subjects_ids', '!=',False)] ,limit=1)
                    accum_semester.write({'accumulated_degree': total_degree})
                    
    @api.model
    def calc_student_project_gpa(self):
        gpa = 0
        status_ids = (self.env['hue.std.data.status'].search(['|',('id', '=', 2),('id', '=', 48)])._ids)
        students = self.env['op.student'].sudo().search([('faculty', '=', 9), ('student_status', 'in', status_ids)])
        for student  in students :
            accum_semesters_subjects = self.env['op.student.semesters.subjects'].sudo().search(
                [('subject_grade', '!=', False),('subject_id.subject_type', '=', 3),('student_id', '=', student.id),('student_semester_id.transferred', '=', False)])
            if accum_semesters_subjects :
                numerator = 0  
                denominator = 0  
                project_gpa = 0
                for std_accum_subject in accum_semesters_subjects :
                    subject_grade = std_accum_subject.final_grade
                    grade_points = self.env['op.course.grades'].sudo().search(
                        [('course_id', '=', student.course_id.id),
                         ('grade_id', '=', subject_grade.id)],
                        limit=1).points_from
                    denominator = denominator + std_accum_subject.subject_id.subject_credithours
                    numerator = numerator + (round((
                            grade_points * std_accum_subject.subject_id.subject_credithours), 3))
                if denominator > 0:
                    numerator = round(numerator, 2)
                    project_gpa = numerator / denominator
                    project_gpa =round(project_gpa+10**(-len(str(project_gpa))-1), 2)
                    project_grade = self.env['op.course.grades'].sudo().search(
                        [('course_id', '=', student.course_id.id),
                         ('points_from', '<=', project_gpa)],order ='points_from desc' ,
                        limit=1).grade_id.id
                    student.write(
                        {'project_gpa': project_gpa,'project_grade': project_grade})