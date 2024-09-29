from odoo import http
from odoo.http import request
from datetime import time, datetime, timedelta ,date
import json
import logging
import werkzeug
import random
import string
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)


class HUECourseController(http.Controller):

    #helper functions
    def checkblock(self,std=None,acadyear=None,semester=None):
        print('99999999999999999999999999999999999999999')
        curr_academic_year_invoice = request.env['op.semesters'].sudo().search([('enroll_semester', '=', True)], limit=1).term_id.academic_year_id
        blocked = False
        invoice_count = 0
        student = request.env['op.student'].sudo().search([('id','=',std)])
        if not student.allow_registration:
            domain = [
                ('move_type', 'in', ['out_invoice']),
                # ('date_due', '<=', date.today()),
                ('invoice_date_due', '<=',curr_academic_year_invoice.invoice_date),
                ('partner_id', '=', student.partner_id.id),
                ('state', 'in', ['draft'])
            ]
            invoice_count = request.env['account.move'].sudo().search_count(domain)

        accum_semesters = request.env['op.student.accumlative.semesters'].sudo().search(
            [('student_id', '=', student.id),('academicyear_id', '=', int(acadyear)),('semester_id', '=', int(semester)),
             ('transferred', '=', False)])
        
        for semss in accum_semesters:
            if not self.semester_is_published(semss.course_id.id, acadyear,semester) :
                blocked = True
                break
            if invoice_count > 0 or  semss.block_result:
                blocked = True
                break
        return blocked
    
    def semester_is_published(self, courseid, acadyear, semester):
        publish_flag = False
        published = request.env['op.course.resultspublish'].sudo().search(
            [('course_id', '=', int(courseid)), ('acadyears', '=', int(acadyear)), ('semesters', '=', int(semester))])
        if published:
            if published.publishflag == 'publish':
                publish_flag = True
            else:
                publish_flag = False
        return publish_flag
    
    def is_closed(self, courseid, acadyear, semester):
        closed = request.env['op.course.resultspublish'].sudo().search(
            [('course_id', '=', courseid), ('acadyears', '=', acadyear), ('semesters', '=', semester)]).publishflag
        if closed:
            if closed == 'close' or  closed == 'publish':
                return True
        return False
    
    def _response(self, headers, body, status=200):
        try:
            fixed_headers = {str(k): v for k, v in list(headers.items())}
        except Exception as e:
            fixed_headers = headers
        response = werkzeug.Response(
            response=body, status=status, headers=fixed_headers)
        """It will return response of auth2"""
        return response
    
    def getdatezone(self, x_date):
        date_time_obj = datetime.strptime(str(x_date), '%Y-%m-%d %H:%M:%S.%f')
        final_date=datetime.strftime(date_time_obj,'%Y-%m-%dT%H:%M:%S.%fZ')
        return final_date
    
    def getcourselevel(self, levelid):
        level = ''
        if levelid.name == '0':
            level = 'PR'
        elif levelid.name == '1':
            level = '01'
        elif levelid.name == '2':
            level = '02'
        elif levelid.name == '3':
            level = '03'
        elif levelid.name == '4':
            level = '04'
        elif levelid.name == '5':
            level = '05'
        return level
    
    
    #APIS
    #courses
    @http.route(['/WSNJ/HUEcourses'], type="http", auth="none", methods=["GET"], csrf=False)
    def NJS_HUEcourses(self, index=None, **payload):
        if index == 'CourseData':
            course_data = request.env['op.course']
            courses = course_data.sudo().search([])
            coursesdata = []
            
            for course in courses:
                item = {
                    "ID": course.id,
                    "Name": course.name,
                    "FacultyID": course.faculty_id.id,
                    "CreditHours": course.credithours,
                    "CoreHours": course.corehours,
                    "ElectiveHours": course.electivehours,
                    "ProjectHours": course.projecthours,
                    "ParentID": course.parent_id.id,
                }
                coursesdata.append(item)
            
            data = {"courses": coursesdata}
            body = json.dumps(data)
            headers = [("Content-Type", "application/json; charset=utf-8")]
            return http.Response(body, headers=headers, status=200)

        # In case index doesn't match 'CourseData'
        return http.Response("Invalid index", status=400)


    # students
    @http.route(['/WSNJ/HUEdata'], type="http", auth="none", methods=["GET"], csrf=False)
    def NJS_HUEstudents(self, index=None, **payload):
        if index == 'StudentData':
            student_data = request.env['op.student']
            students = student_data.sudo().search([('student_status', '=', 2)])
            print()
            studentsdata = []
            for student in students:
                if student:
                    item = {"ID": student.id, 
                                'enName': student.en_name,
                                'Code': student.student_code,
                                'NationalID': student.national_id,
                                'FacultyID' : student.faculty.id,
                                'CourseID' : student.course_id.id,
                                }
                    studentsdata.append(item)                 
            data = {"students" : studentsdata}
            if data:
                body = json.dumps(data)
                headers = [("Content-Type", "application/json; charset=utf-8")]
                return http.Response(body, headers=headers, status=200)
        
        # In case index doesn't match 'CourseData'
        return http.Response("Invalid index", status=400)


    #subjects    
    @http.route(['/WSNJ/HUEcoursesSubjects'], type="http", auth="none", methods=["GET"], csrf=False)
    def NJS_HUEcoursesSubjects(self, index=None, **payload):
        if index == 'CourseSubjectsData':
            course_subjects_data = request.env['op.subject']
            courses_subjects = course_subjects_data.sudo().search([])
            coursessubjectsdata = []
            for courses_subject in courses_subjects:
                if courses_subject:
                    item = {"ID": courses_subject.id, 
                                'Name': courses_subject.name,
                                'Code': courses_subject.code,
                                'CourseID': courses_subject.course_id.id,
                                'CreditHours': courses_subject.subject_credithours,
                                'Level': courses_subject.subject_level.name,
                                'Type': courses_subject.subject_type,
                                'prerequisites':  courses_subject.subject_prerequisites.ids
                                }
                    coursessubjectsdata.append(item)                 
            data = {"coursessubjects" : coursessubjectsdata}
            if data:
                body = json.dumps(data)
                headers = [("Content-Type", "application/json; charset=utf-8")]
                return http.Response(body, headers=headers, status=200)
        
        # In case index doesn't match 'CourseData'
        return http.Response("Invalid index", status=400)


    #Staff data
    @http.route(['/WSNJ/HUEstaff'], type="http", auth="none", methods=["GET"], csrf=False)
    def NJS_HUEstaff(self, index=None, **payload):
        if index == 'staffData':
            # curr_academic_year = request.env['op.academic.year'].sudo().search([('current', '=', True)]).id
            # curr_semester = request.env['op.semesters'].sudo().search([('current', '=', True)]).id
            staff_data = request.env['op.faculty']
            staff_data_ = staff_data.sudo().search([])
            staff_datalist = []
            for staff in staff_data_:
                if staff:
                    item = {"ID": staff.id, 
                            'Name': staff.emp_id.name ,
                            'type': staff.job_id.contract_type_id if staff.job_id.contract_type_id else "",
                                }
                    staff_datalist.append(item)                 
            data = {"staffdata" : staff_datalist}
            if data:
                body = json.dumps(data)
                headers = [("Content-Type", "application/json; charset=utf-8")]
                return http.Response(body, headers=headers, status=200)
        
        # In case index doesn't match 'CourseData'
        return http.Response("Invalid index", status=400)

    # Academic_year
    @http.route(['/WSNJ/HUEAcadYear'], type="http", auth="none", methods=["GET"], csrf=False)
    def NJS_HUEAcadYear(self, index=None, **payload):
        if index == 'AcadYearData':
            acadyear_data = request.env['op.academic.year']
            acadyear_data = acadyear_data.sudo().search([],limit = 20)
            acadyearlist = []
            for acadyear in acadyear_data:
                if acadyear:
                    item = {"ID": acadyear.id, 
                                'Name': acadyear.name,
                                'Active': acadyear.current
                                }
                    acadyearlist.append(item)                 
            data = {"acadyeardata" : acadyearlist}
            if data:
                body = json.dumps(data)
                headers = [("Content-Type", "application/json; charset=utf-8")]
                return http.Response(body, headers=headers, status=200)
        
        # In case index doesn't match 'CourseData'
        return http.Response("Invalid index", status=400)

    
    #semesters
    @http.route(['/WSNJ/HUESemester'], type="http", auth="none", methods=["GET"], csrf=False)
    def NJS_HUESemester(self, index=None, **payload):
        if index == 'SemesterData':
            semester_data = request.env['op.semesters']
            semester_data = semester_data.sudo().search([],limit = 20)
            semesterlist = []
            for semester in semester_data:
                if semester:
                    item = {"ID": semester.id, 
                                'Name': semester.name,
                                'Active': semester.current
                                }
                    semesterlist.append(item)                 
            data = {"semesterdata" : semesterlist}
            if data:
                body = json.dumps(data)
                headers = [("Content-Type", "application/json; charset=utf-8")]
                return http.Response(body, headers=headers, status=200)
        
        # In case index doesn't match 'CourseData'
        return http.Response("Invalid index", status=400)

    
    # levels
    @http.route(['/WSNJ/HUELevels'], type="http", auth="none", methods=["GET"], csrf=False)
    def NJS_HUELevels(self, index=None, **payload):
        if index == 'LevelsData':
            level_data = request.env['op.levels']
            level_data = level_data.sudo().search([],limit = 20)
            levellist = []
            for level in level_data:
                if level:
                    item = {"ID": level.id, 
                                'Name': level.name
                                }
                    levellist.append(item)                 
            data = {"leveldata" : levellist}
            if data:
                body = json.dumps(data)
                headers = [("Content-Type", "application/json; charset=utf-8")]
                return http.Response(body, headers=headers, status=200)

        # In case index doesn't match 'CourseData'
        return http.Response("Invalid index", status=400)

    #grades
    @http.route(['/WSNJ/HUEGrades'], type="http", auth="none", methods=["GET"], csrf=False)
    def NJS_HUEGrades(self, index=None, **payload):
        if index == 'GradesData':
            grades_data = request.env['op.grades']
            grades_data = grades_data.sudo().search([])
            gradeslist = []
            for grade in grades_data:
                if grade:
                    item = {"ID": grade.id, 
                                'Name': grade.name,
                                'Active': grade.pass_grade
                                }
                    gradeslist.append(item)                 
            data = {"gradesdata" : gradeslist}
            if data:
                body = json.dumps(data)
                headers = [("Content-Type", "application/json; charset=utf-8")]
                return http.Response(body, headers=headers, status=200)

        # In case index doesn't match 'CourseData'
        return http.Response("Invalid index", status=400)

    #question types
    @http.route(['/WSNJ/HUEQuesCat'], type="http", auth="none", methods=["GET"], csrf=False)
    def NJS_HUEQuesCat(self, index=None, **payload):
        if index == 'QuesCatData':
            questype_data = request.env['question.types']
            questype_data = questype_data.sudo().search([('enable','=',True)])
            questypelist = []
            for questype in questype_data:
                if questype:
                    item = {"id": questype.id, 
                                'name': questype.category_name ,
                                'type': questype.types
                                }
                    questypelist.append(item)                 
            data = {"questype_data" : questypelist}
            if data:
                body = json.dumps(data)
                headers = [("Content-Type", "application/json; charset=utf-8")]
                return http.Response(body, headers=headers, status=200)

        # In case index doesn't match 'CourseData'
        return http.Response("Invalid index", status=400)
    
    # QuesServicesData
    @http.route(['/WSNJ/HUEQuesServices'], type="http", auth="none", methods=["GET"], csrf=False)
    def NJS_HUEQuesServices(self, index=None, **payload):
        if index == 'QuesServicesData':
            questype_data = request.env['question.types']
            questype_data = questype_data.sudo().search([('id','>','4'),('enable','=',True)])
            questypelist = []
            for questype in questype_data:
                if questype:
                    item = {"id": questype.id, 
                                'name': questype.category_name ,
                                'type': questype.types
                                }
                    questypelist.append(item)                 
            data = {"questype_data" : questypelist}
            if data:
                body = json.dumps(data)
                headers = [("Content-Type", "application/json; charset=utf-8")]
                return http.Response(body, headers=headers, status=200)

        # In case index doesn't match 'CourseData'
        return http.Response("Invalid index", status=400)

    # QuestionsData
    @http.route(['/WSNJ/HUEQuestions'], type="http", auth="none", methods=["GET"], csrf=False)
    def NJS_HUEQuestions(self, index=None, **payload):
        if index == 'QuestionsData':
            questions_data = request.env['questions']            
            questions_data = questions_data.sudo().search([('enable','=',True)])
            questionslist = []
            for question in questions_data:
                if question:
                    item = {"id": question.id,
                            'question_type': question.category.id,
                            'description': question.name                                
                                }
                    questionslist.append(item)                 
            data = {"questions_data" : questionslist}
            if data:
                body = json.dumps(data)
                headers = [("Content-Type", "application/json; charset=utf-8")]
                return http.Response(body, headers=headers, status=200)

        # In case index doesn't match 'CourseData'
        return http.Response("Invalid index", status=400)

    
    #FacultyData
    @http.route(['/WSNJ/HUEFaculty'], type="http", auth="none", methods=["GET"], csrf=False)
    def NJS_HUEFaculty(self, index=None, **payload):
        if index == 'FacultyData':
            faculty_data = request.env['hue.faculties']
            faculty_data = faculty_data.sudo().search([],limit = 20)
            facultylist = []
            for faculty in faculty_data:
                if faculty_data:
                    item = {"ID": faculty.id, 
                                'Name': faculty.name
                                }
                    facultylist.append(item)                 
            data = {"facultydata" : facultylist}
            if data:
                body = json.dumps(data)
                headers = [("Content-Type", "application/json; charset=utf-8")]
                return http.Response(body, headers=headers, status=200)

        # In case index doesn't match 'CourseData'
        return http.Response("Invalid index", status=400)

    # StudentTotalsData
    @http.route(['/WSNJ/HUETotals'], type="http" ,auth="none", methods=["GET"], csrf=False)
    def NJS_HUETotals(self, index=None,course_id=None,student_id=None, **payload):
        if index == 'TotalsData':
            totals_data = request.env['op.student']
            if course_id:
                totals_data = totals_data.sudo().search([('course_id','=',int(course_id))])
            elif student_id:
                totals_data = totals_data.sudo().search([('id','=',int(student_id))])
            print(totals_data)    
            totalslist = []
            for total in totals_data:
                if total:
                    advisor = request.env['hue.academic.direction.line'].sudo().search([('student_id','=',total.id),('to_date','=',False)],limit=1)
                    if total.timestamp:
                        updatedAt = total.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        updatedAt = total.timestamp
                    item = {"ID": total.id, 
                                'gpa': total.new_gpa if total.course_id.id != 15 else False,
                                'hours': total.new_crh,
                                'level': total.level.id,
                                'advisor': advisor.faculty_id.id,
                                'updatedAt': updatedAt
                                # 'editat': total.timestamp
                                }
                    totalslist.append(item)                 
            data = {"totals_data" : totalslist}
            if data:
                body = json.dumps(data)
                headers = [("Content-Type", "application/json; charset=utf-8")]
                return http.Response(body, headers=headers, status=200)

        # In case index doesn't match 'CourseData'
        return http.Response("Invalid index", status=400)

    # StudentQues
    @http.route(['/WSNJ/HUEQuesdata'], type="http", auth="none", methods=["GET"], csrf=False)
    def NJS_HUEquestionaire(self, index=None, faculty_id=None, **payload):
        if index == 'StudentQues':
            student_data = request.env['op.student']
            print('AAAAADDDDDDDDFFFFFFFFFGGGGGGGGG')
            print(faculty_id)
            curr_academic_year = request.env['op.academic.year'].sudo().search([('current', '=', True)]).id
            curr_semester = request.env['op.semesters'].sudo().search([('current', '=', True)]).id
            
            studs = student_data.sudo().search([('student_status', '=', 2),('faculty', '=', int(faculty_id))])._ids
            # if studs == False:
            #     break
            if faculty_id != '12' : 
                sql = ("select distinct student_id,(select id from op_subject where id = (select subject_id from op_session where id = t1.session_id) limit 1) subject_id,t2.faculty_id , '"+str(curr_academic_year)+"' acadyear , '"+str(curr_semester)+"' semester \n"
                            + " from hue_student_registration t1 left join session_q_faculty_rel t2 \n"
                            + " on t1.session_id = t2.session_id \n"
                            + " where batch_id in (SELECT id from op_batch where academic_year = "+str(curr_academic_year)+" and semester = "+str(curr_semester)+") \n"
                            + " and student_id in "+str(studs)+""
                            + " order by student_id   \n")
            else:
                sql = ("select student_id,subject_id,'' faculty_id, '"+str(curr_academic_year)+"' acadyear , '"+str(curr_semester)+"' semester \n"
                        + " from op_student_semesters_subjects where  "
                        + "academicyear_id = "+str(curr_academic_year)+" and semester_id =  "+str(curr_semester)+"  and student_id in "+str(studs)+" order by student_id \n")
            
            request.cr.execute(sql)
            students = request.cr.dictfetchall()
            
            studentsdata = []
            for student in students:
                if student:
                    _logger.info('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
                    _logger.info(student)
                    item = {"StudentID": student['student_id'], 
                                'SubjectID': student['subject_id'],
                                'FacultyID': student['faculty_id'],
                                'AcadYear': student['acadyear'],
                                'Semester': student['semester'],
                                }
                    studentsdata.append(item)                 
            data = {"students" : studentsdata}
            if data:
                body = json.dumps(data)
                headers = [("Content-Type", "application/json; charset=utf-8")]
                return http.Response(body, headers=headers, status=200)

        # In case index doesn't match 'CourseData'
        return http.Response("Invalid index", status=400)
    
    # StudentSemesters
    @http.route(['/WSNJ/HUESemesters'], type="http", auth="none", methods=["GET"], csrf=False)
    def HUESemesters(self, index=None, course_id=None, **payload):
        if index == 'StudentSemesters':
            student_data = request.env['op.student']
            if not course_id:
                # In case index doesn't match 'CourseData'
                return http.Response("No Course ID added", status=400)
            sql = ("  select id,student_id,academicyear_id,semester_id,course_id,semester_gpa,semester_hr,current_gpa,final_grade \n"
                    + " from op_student_accumlative_semesters tt \n"
                    + " where course_id = "+course_id+" and (transferred is null or transferred = false)  \n"
                    + " and (select publishflag from op_course_resultspublish \n"
                    + " 	 where course_id = tt.course_id and acadyears = tt.academicyear_id\n"
                    + " 	 and semesters = tt.semester_id) = 'publish' \n")  
            request.env.cr.execute(sql)
            students = request.env.cr.dictfetchall()
            
            studentsdata = []
            
            for student in students:
                if student:
                    print("self", self)
                    #_logger.info('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
                    #_logger.info(student)
                    chkblock = self.checkblock(student['student_id'],student['academicyear_id'],student['semester_id'])
                    f_grade = student['final_grade']
                    if f_grade == 25:
                        f_grade = 19
                    item = {"StudentID": student['student_id'], 
                                'CourseID': student['course_id'],
                                'AcadYear': student['academicyear_id'],
                                'Semester': student['semester_id'],
                                'SemesterGPA': student['semester_gpa'],
                                'SemesterHR': student['semester_hr'],
                                'CurrentGPA': student['current_gpa'],
                                'ID': student['id'],
                                'final_grade': f_grade,
                                'blocked' : chkblock
                                }
                    studentsdata.append(item)                 
            data = {"students" : studentsdata}
            if data:
                body = json.dumps(data)
                headers = [("Content-Type", "application/json; charset=utf-8")]
                return http.Response(body, headers=headers, status=200)

        # In case index doesn't match 'CourseData'
        return http.Response("Invalid index", status=400)
    
    #StudentTranscript
    @http.route(['/WSNJ/HUETranscript'], type="http", auth="none", methods=["GET"], csrf=False)
    def HUETranscript(self, index=None, course_id=None, **payload):
        if index == 'StudentTranscript':
            student_data = request.env['op.student']
            if not course_id:
                # In case index doesn't match 'CourseData'
                return http.Response("No Course ID added", status=400)
            sql = ("select student_id,subject_id,(select subject_credithours from op_subject where id = tt.subject_id) subject_ch, "
                    + " (select subject_addtogpa from op_subject where id = tt.subject_id) added ,  \n"
                    + "course_id,final_grade,academicyear_id , semester_id ,student_semester_id \n"
                    + " from op_student_semesters_subjects tt \n"
                    + " where course_id = "+course_id+" and final_grade is not null order by student_semester_id   \n")  
            request.env.cr.execute(sql)
            students = request.env.cr.dictfetchall()
            
            studentsdata = []
            for student in students:
                hidegrade_value = student['added']
                if student:
                    item = {"StudentID": student['student_id'], 
                                'SubjectID': student['subject_id'],
                                'SubjectCH': student['subject_ch'],
                                'CourseID': student['course_id'],
                                'AcadYear': student['academicyear_id'],
                                'Semester': student['semester_id'],
                                'Grade': student['final_grade'],
                                'hidegrade' : hidegrade_value,
                                'FK': student['student_semester_id'],
                                }
                    studentsdata.append(item)                 
            data = {"students" : studentsdata}
            if data:
                body = json.dumps(data)
                headers = [("Content-Type", "application/json; charset=utf-8")]
                return http.Response(body, headers=headers, status=200)

        # In case index doesn't match 'CourseData'
        return http.Response("Invalid index", status=400)
    
    
    #StudentCurrentSemesters
    @http.route(['/WSNJ/HUECurrentSemesters'], type="http", auth="none", methods=["GET"], csrf=False)
    def HUECurrentSemesters(self, index=None, course_id=None,student_id=None,curr_academic_year=None,curr_semester=None, **payload):
        
        if student_id:
            curr_academic_year = request.env['op.academic.year'].sudo().search([('current', '=', True)]).id
            curr_semester = request.env['op.semesters'].sudo().search([('run_semester_gpa', '=', True)]).id
        if index == 'StudentCurrentSemesters':
            student_data = request.env['op.student']
            if not curr_academic_year:
                return http.Response("curr_academic_year is not specified, Add curr_academic_year or add student_id", status=400)
            if not curr_semester:
                return http.Response("curr_semester is not specified, Add curr_semester or add student_id", status=400)
            if course_id:
                sql = ("  select id,student_id,academicyear_id,semester_id,course_id,semester_gpa,semester_hr,current_gpa,final_grade \n"
                        + " from op_student_accumlative_semesters tt \n"
                        + " where course_id = "+str(course_id)+" and (transferred is null or transferred = false)   \n"
                        # + " and student_id in (395,399) \n"
                        # + " and student_id in (8464,8465,8466,8467,8469,8473,8474,8476,8477,8480,8481,8482,8484,8485,8486,8488,8489,8490,8492,8496,8497,8498,8499,8500,8504,8506,8510,8511,8514,8517,8520,8521,8522,8523,8524,8526,8527,8529,8531,8534,8535,8537,8539,8540,8544,8545,8546,8548,8552,8564,8571,8573,8574,8585,8587,8593,8594,8603,8611,8613,8635,8636,10077,10574,13956,13957,14048,14267,16928,16934,17035,17179,17188,17191,17220,17431,17451,17501,17519,17568,17570,17571,17572,17573,17574,17575,17576,17578,17581,17585,17588,17596,17609,17611,17615,17617,17618,17620,17621,17627,17630,17634,17639,17642,17644,17645,17646,17650,17656,17661,17663,17666,17667,17670,17671,17672,17674,17677,17678,17681,17684,17692,17697,17699,17703,17705,17709,17713,17715,17718,17720,17722,17724,17725,17726,17727,17729,17730,17731,17733,17735,17737,17738,17739,17741,17744,17745,17746,17747,17750,17751,17752,17753,17754,17755,17756,17780,17784,17787,17790,17793,17794,17813,17819,17834,17844,17845,17863,17865,17877,17882,17884,17886,17887,17902,17909,17910,17933,17934,17936,17941,17943,17953,17961,17968,17970,17971,17977,17979,17985,17986,17987,17989,17990,17992,17993,18003,18004,18012,18020,18022,18024,18029,18030,18031,18036,18039,18043,18044,18049,18050,18054,18059,18061,18063,18070,18076,18079,18100,18101,18102,18103,18106,18108,18113,18162,18201,18267,18275,18276,18279,18280,18299,18322,18329,18340,18366,18367,18371,18372,18373,18386,18396,18430,18439,18441,18443,18450,18455,18471,18476,18477,18479,18496,18507,18508,18518,18535,18538,18541,18542,18552,18582,18584,18585,18587,18595,18619,18624,18632,18633,18652,18664,18669,18673,18674,18676,18679,18684,18685,18695,18697,18701,18703,18706,18710,18713,18727,18738,18739,18756,18761,18762,18781,18793,18802,18816,18829,18837,18844,18865,18955,18979,18984,18997,19028,19029,19030,19083,19085,19089) "
                        + " and academicyear_id = "+str(curr_academic_year)+" and semester_id = "+str(curr_semester)+" \n" )
            elif student_id:
                sql = ("  select id,student_id,academicyear_id,semester_id,course_id,semester_gpa,semester_hr,current_gpa,final_grade \n"
                        + " from op_student_accumlative_semesters tt \n"
                        + " where student_id = "+str(student_id)+" and (transferred is null or transferred = false)   \n"
                        # + " and academicyear_id = "+str(curr_academic_year)+" and semester_id = "+str(curr_semester)+" \n"
                        )
                
            request.env.cr.execute(sql)
            students = request.env.cr.dictfetchall()
            
            studentsdata = []
            xx = 0
            for student in students:
                xx = xx+1
                _logger.info('***********************_____________________________   '+str(xx)+'    __________________________******************************')
                if student:
                    sds_tobedeleted_show_result = True
                    chkblock = False
                    if course_id:
                        published = self.semester_is_published(student['course_id'], curr_academic_year,curr_semester)
                    else:
                        published = self.semester_is_published(student['course_id'], student["academicyear_id"],student["semester_id"])
                     
                    print('!!!!!!!!!@@@@@@@@@@@@@@@@@@@@@@@@')
                    print(published)
                    if student["academicyear_id"] == curr_academic_year and student["semester_id"] == curr_semester :
                        print('******************************')
                        chkblock = self.checkblock(student['student_id'],curr_academic_year,curr_semester)
                    f_grade = student['final_grade']
                    if f_grade == 25:
                        f_grade = 19

                    current_gpa =student['current_gpa']
                    if published == False:
                        item = {"StudentID": student['student_id'], 
                                    'CourseID': student['course_id'],
                                    'AcadYear': student['academicyear_id'],
                                    'Semester': student['semester_id'],
                                    'SemesterGPA': False,
                                    'SemesterHR': False,
                                    'CurrentGPA': False,
                                    'ID': student['id'],
                                    'final_grade': False,
                                    'blocked' : True
                                    }
                    else:
                        item = {"StudentID": student['student_id'], 
                                    'CourseID': student['course_id'],
                                    'AcadYear': student['academicyear_id'],
                                    'Semester': student['semester_id'],
                                    'SemesterGPA': student['semester_gpa'] if sds_tobedeleted_show_result else False,
                                    'SemesterHR': student['semester_hr'] if sds_tobedeleted_show_result else False,
                                    'CurrentGPA': current_gpa,
                                    'ID': student['id'],
                                    'final_grade': f_grade if sds_tobedeleted_show_result else False,
                                    'blocked' : True
                                    }
                    studentsdata.append(item)                 
            data = {"students" : studentsdata}
            if data:
                body = json.dumps(data)
                headers = [("Content-Type", "application/json; charset=utf-8")]
                return http.Response(body, headers=headers, status=200)

        # In case index doesn't match 'CourseData'
        return http.Response("Invalid index", status=400)
    
    
    #StudentCurrentTranscript
    @http.route(['/WSNJ/HUECurrentTranscript'], type="http", auth="none", methods=["GET"], csrf=False)
    def HUECurrentTranscript(self, index=None, course_id=None, student_id=None,curr_academic_year=None,curr_semester=None, **payload):
        if student_id:
            curr_academic_year = request.env['op.academic.year'].sudo().search([('current', '=', True)]).id
            curr_semester = request.env['op.semesters'].sudo().search([('run_semester_gpa', '=', True)]).id
            
        if index == 'StudentCurrentTranscript':
            student_data = request.env['op.student']
            if not curr_academic_year:
                return http.Response("curr_academic_year is not specified, Add curr_academic_year or add student_id", status=400)
            if not curr_semester:
                return http.Response("curr_semester is not specified, Add curr_semester or add student_id", status=400)
            if course_id:
                sql = ("select student_id,subject_id,(select subject_credithours from op_subject where id = tt.subject_id) subject_ch,(select subject_addtogpa from op_subject where id = tt.subject_id) added ,course_id,final_grade,academicyear_id , semester_id ,student_semester_id \n"
                        + " from op_student_semesters_subjects tt \n"
                        + " where course_id = "+str(course_id)
                        # + " and student_id in (8610,8990,9188,9465,10534,10556,10599,10607,10613,10683) "
                        + " and academicyear_id = "+str(curr_academic_year)+" and semester_id = "+str(curr_semester)+"  order by student_semester_id   \n")
            elif student_id:
                sql = ("select student_id,subject_id,academicyear_id,semester_id,(select subject_credithours from op_subject where id = tt.subject_id) subject_ch,(select subject_addtogpa from op_subject where id = tt.subject_id) added ,course_id,final_grade,academicyear_id , semester_id ,student_semester_id \n"
                        + " from op_student_semesters_subjects tt \n"
                        + " where student_id = "+str(student_id)
                        + " order by student_semester_id   \n")
           
            request.env.cr.execute(sql)
            students = request.env.cr.dictfetchall()
            
            studentsdata = []
            xx = 0
            for student in students:
                xx = xx+1
                _logger.info('***********************_____________________________   '+str(xx)+'    __________________________******************************')
                if student:
                    hidegrade_value = student['added']
                    if course_id:
                        published = self.semester_is_published(student['course_id'], curr_academic_year,curr_semester)
                    else:
                        published = self.semester_is_published(student['course_id'], student["academicyear_id"],student["semester_id"])
                        
                    if published == False:
                        if student['student_id']:
                            item = {"StudentID": student['student_id'], 
                                        'SubjectID': student['subject_id'],
                                        'SubjectCH': student['subject_ch'],
                                        'CourseID': student['course_id'],
                                        'AcadYear': student['academicyear_id'],
                                        'Semester': student['semester_id'],
                                        'Grade': False,
                                        'hidegrade' : hidegrade_value,
                                        'FK': student['student_semester_id'],
                                        }
                    else:
                        if student['student_id']:
                            item = {"StudentID": student['student_id'], 
                                        'SubjectID': student['subject_id'],
                                        'SubjectCH': student['subject_ch'],
                                        'CourseID': student['course_id'],
                                        'AcadYear': student['academicyear_id'],
                                        'Semester': student['semester_id'],
                                        'Grade': student['final_grade'],
                                        'hidegrade' : hidegrade_value,
                                        'FK': student['student_semester_id'],
                                        }
                    studentsdata.append(item)                 
            data = {"students" : studentsdata}
            if data:
                body = json.dumps(data)
                headers = [("Content-Type", "application/json; charset=utf-8")]
                return http.Response(body, headers=headers, status=200)

        # In case index doesn't match 'CourseData'
        return http.Response("Invalid index", status=400)
    
    #StuFeesData
    @http.route(['/WSNJ/HUEStuFees'], type="http" ,auth="none", methods=["GET"], csrf=False)
    def NJS_HUEStuFees(self, index=None,student_id=None, **payload):
        if index == 'StuFeesData':
            if not student_id:
                return http.Response("student_id is not specified", status=400)
            std = request.env['op.student'].sudo().search([('id','=',student_id)])
            domain = [
                ('move_type', 'in', ['out_invoice']),
                ('invoice_date_due', '<=', date.today()),
                ('partner_id', '=', std.partner_id.id),
                ('state', 'in', ['draft'])
            ]
            invoices = request.env['account.move'].sudo().search(domain)
            invoiceslist = []
            print('111111111111111')
            print(invoices)
            for invoice in invoices:
                if invoice:
                    inv_name =  request.env['account.move.line'].sudo().search([('move_id', '=', invoice.id)],limit = 1)
                    if invoice.name:
                        item = {"ID": invoice.id, 
                                    'number': invoice.number,
                                    'name' : inv_name.name + '-' + invoice.name,
                                    'state': invoice.state,
                                    'date_due': invoice.invoice_date_due,
                                    'amount': invoice.residual,
                                    'currency': invoice.currency_id.name,
                                    }
                    else:
                        item = {"ID": invoice.id, 
                                    'number': invoice.number,
                                    'name' : inv_name.name,
                                    'state': invoice.state,
                                    'date_due': invoice.invoice_date_due,
                                    'amount': invoice.residual,
                                    'currency': invoice.currency_id.name,
                                    }
                    invoiceslist.append(item)
                    
            data = {"invoices_data" : invoiceslist}
            if data:
                body = json.dumps(data)
                headers = [("Content-Type", "application/json; charset=utf-8")]
                return http.Response(body, headers=headers, status=200)
                
            if not invoices:
                print('2222222222222222')
                data = {"invoices_data" : "There is no Invoices Unpaid"}
                body = json.dumps(data)
                headers = [("Content-Type", "application/json; charset=utf-8")]
                return http.Response(body, headers=headers, status=200)
            
        # In case index doesn't match 'CourseData'
        return http.Response("Invalid index", status=400)
    
    # StudyTimetable
    @http.route(['/WSNJ/HUEStudyTimetable'], type="http" ,auth="none", methods=["GET"], csrf=False)
    def NJS_HUEStudyTimetable(self, index=None,student_id=None, **payload):
        if index == 'StudyTimetable':
            AcadYearID = request.env['op.academic.year'].sudo().search([('timetable_current', '=', True)], limit=1).id
            semester_id = request.env['op.semesters'].sudo().search([('timetable_current', '=', True)], limit=1).id
            
            print('1111111111111112222222222222222222')
            print(AcadYearID)
            print(semester_id)
        
            student = request.env['op.student'].sudo().search([('id', '=', student_id)], limit=1)
            batchid = request.env['op.batch'].sudo().search(
            [('academic_year', '=', AcadYearID), ('semester', '=', semester_id),
             '|', ('course_id', '=', student.course_id.id), ('course_id', '=', student.course_id.parent_id.id)])
                
            print(student.course_id.id)
            print(batchid)
            sessions = request.env['op.session'].sudo().search([('student_ids', '=', student.id),('batch_id', 'in', batchid.ids)], order="start_datetime")
            print(sessions)
            sessionslist = []
            
            for session in sessions:
                if session:
                    faculties = []
                    for faculty in session.faculty_ids:
                        faculties.append(faculty.name)
                    
                    item = {"ID": session.id, 
                                'Day': session.type,
                                'Type' : session.session_type,
                                'Subject': session.subject_id.name,
                                'Place': session.facility_id.name,
                                'from': session.timing_id.name,
                                'to': session.to_timing_id.name,
                                'group': session.classroom_id.name,
                                'section': session.sub_classroom,
                                'faculty_ids' : faculties
                                }
                    sessionslist.append(item)                 
            
            data = {"sessions_data" : sessionslist}
            if data:
                body = json.dumps(data)
                headers = [("Content-Type", "application/json; charset=utf-8")]
                return http.Response(body, headers=headers, status=200)
            
            if not sessions:
                print('2222222222222222')
                data = {"sessions_data" : "There is no Study Timetable"}
                body = json.dumps(data)
                headers = [("Content-Type", "application/json; charset=utf-8")]
                return http.Response(body, headers=headers, status=200)
            
        # In case index doesn't match 'CourseData'
        return http.Response("Invalid index", status=400)
    
    #ExamTimetable
    @http.route(['/WSNJ/HUEExamTimetable'], type="http" ,auth="none", methods=["GET"], csrf=False)
    def NJS_HUEExamTimetable(self, index=None,student_id=None, **payload):
        if index == 'ExamTimetable':
            stuID = request.env['op.student'].sudo().search([('id', '=', student_id)], limit=1)
            calendar = request.env['hue.event.calendar'].sudo().search(
            [('type', '=', 'exam_timetable'), ('course_id', '=', stuID.course_id.id),
             ('start_date', '<=', datetime.today().strftime("%Y-%m-%d %H:%M:%S")),
             ('end_date', '>=', datetime.today().strftime("%Y-%m-%d %H:%M:%S"))], limit=1)
            
            print('CCCCCCCCCCCCCCC')
            print(calendar)
            exam_sessions = []
            if calendar:
                exam_sessions = request.env['op.exam.attendees'].sudo().search(
                    [('student_id', '=', stuID.id), ('start_time', '>=', calendar.start_date), ('end_time', '>=', calendar.start_date)], order="start_time")
            else:
                print('2222222222222222')
                data = {"exams_data" : "There is no Exam Timetable"}
                body = json.dumps(data)
                headers = [("Content-Type", "application/json; charset=utf-8")]
                return http.Response(body, headers=headers, status=200)
                
            examslist = []
            
            for exam in exam_sessions:
                if exam:
                    item = {"ID": exam.id, 
                                'Exam': exam.exam_id.id,
                                'Date': exam.start_time.split(' ')[0],
                                
                                'From': datetime.strptime(exam.start_time, '%Y-%m-%d %H:%M:%S').astimezone(pytz.timezone("Africa/Cairo")).strftime("%Y-%m-%d %H:%M:%S").split(' ')[1],
                                'To': datetime.strptime(exam.end_time, '%Y-%m-%d %H:%M:%S').astimezone(pytz.timezone("Africa/Cairo")).strftime("%Y-%m-%d %H:%M:%S").split(' ')[1],
                                'SeatNo': exam.seat_no,
                                'Room': exam.room_id.name,
                                'Type': exam.exam_type.name,
                                'Subject': exam.exam_id.subject_id.name,
                                }
                    examslist.append(item)                 
            data = {"exams_data" : examslist}
            if data:
                body = json.dumps(data)
                headers = [("Content-Type", "application/json; charset=utf-8")]
                return http.Response(body, headers=headers, status=200)
            
            if not exam_sessions:
                print('2222222222222222')
                data = {"exams_data" : "There is no Exam Timetable"}
                body = json.dumps(data)
                headers = [("Content-Type", "application/json; charset=utf-8")]
                return http.Response(body, headers=headers, status=200)
            
        # In case index doesn't match 'ExamTimetable'
        return http.Response("Invalid index", status=400)
    
    #Attendance
    @http.route(['/WSNJ/HUEAttendance'], type="http" ,auth="none", methods=["GET"], csrf=False)
    def NJS_HUEAttendance(self, index=None,studentID=None, **payload):
        if index == 'Attendance':
            academic_year = request.env['op.academic.year'].sudo().search([('current', '=', True)], limit=1)
            semester = request.env['op.semesters'].sudo().search([('current', '=', True)], limit=1)
            
            student_id = request.env['op.student'].sudo().search([('id', '=', studentID)], limit=1)
            batch = request.env['op.batch'].sudo().search([('academic_year', '=', academic_year.id)
                ,('semester', '=', semester.id),'|', ('course_id', '=', student_id.course_id.id), ('course_id', '=', student_id.course_id.parent_id.id)])
            
            student_attendances = request.env['op.attendance.line'].sudo().search([('student_id', '=', student_id.id)
                ,('permitted', '=', False), ('present', '=', False) ,
                ('batch_id', 'in', batch.ids )])
            attendancelist = []
            subjects = []
            for student_attendance in student_attendances:
                if student_attendance:
                    subject = {}
                    check = True
                    for rec in subjects:
                        if rec['subject'] == student_attendance.session_id.subject_id:
                            check = False
                    if check:
                        without_reg_day = request.env['op.student.accumlative.semesters'].sudo().search([('student_id', '=', student_id.id),('academicyear_id', '=', academic_year.id)
                                ,('semester_id', '=',semester.id)])
                        subject['subject'] = student_attendance.session_id.subject_id
                        sessions = self.get_registrations(student_id, student_attendance.session_id.subject_id.id)
                        subject['all_count'] = sessions['sessions_count']
                        leave_days = self.get_student_leaves(student_id.id)
                        
                        
                        student_absence_count =0
                        student_absence=[]
                        absence_days =[]
                        if student_id.course_id.id != 15 :
                            if without_reg_day.create_date :
                                student_absence_count = request.env['op.attendance.line'].sudo().search_count([('attendance_date', '>', without_reg_day.create_date),('student_id', '=', student_id.id), ('permitted', '=', False), ('present', '=', False), ('session_id', 'in', sessions['session_ids']), ('attendance_date', 'not in', leave_days)])
                                student_absence = request.env['op.attendance.line'].sudo().search([('attendance_date', '>', without_reg_day.create_date),('student_id', '=', student_id.id), ('present', '=', False), ('session_id', 'in', sessions['session_ids']),
                                    ('attendance_date', 'not in', leave_days)])
                        else :
                            student_absence_count = request.env['op.attendance.line'].sudo().search_count([('student_id', '=', student_id.id), ('permitted', '=', False), ('present', '=', False), ('session_id', 'in', sessions['session_ids']), ('attendance_date', 'not in', leave_days)])
                            student_absence = request.env['op.attendance.line'].sudo().search([('student_id', '=', student_id.id), ('present', '=', False), ('session_id', 'in', sessions['session_ids']),
                            ('attendance_date', 'not in', leave_days)])
                            
                        subject['absence_count'] = student_absence_count
                        subject['attendance_lines'] = student_absence
        
                        subject['percentage'] = 0
                        if sessions['sessions_count'] > 0:
                            subject['percentage'] = int(student_absence_count / (sessions['sessions_count']) * 100)
                        
                        subjects.append(subject)
                        for date in student_absence:
                            days = date.attendance_date
                            types = date.session_id.session_type
                            from_time = date.session_id.timing_id.name
                            to_time =date.session_id.to_timing_id.name
                            datetype = str(days) + ' from '+ str(from_time)+' to '+str(to_time) + ' - ' + str(types) 
                            absence_days.append(datetype)
                        
                        per = 0
                        if subject['percentage'] > 0 and subject['percentage'] < 11:
                            per = 0
                        elif subject['percentage'] > 10  and subject['percentage'] < 21:
                            per = 1
                        elif subject['percentage'] > 20 and subject['percentage'] < 26:
                            per = 2
                        elif subject['percentage'] > 25 and subject['percentage'] < 101:
                            per = 3
                            
                        item = {"ID": student_id.id, 
                                'Subject': subject['subject'].name,
                                'Count': subject['absence_count'],
                                'AbsenceDays': absence_days,
                                'Percentage': per,
                                'NO of absence' : str(student_absence_count)+" from " +str(sessions['sessions_count']) + " sessions "
                                
                                }
                        
                        attendancelist.append(item)
                        
            data = {"attendance_data" : attendancelist}
            if data:
                body = json.dumps(data)
                headers = [("Content-Type", "application/json; charset=utf-8")]
                
            
            if not student_attendances:
                data = {"attendance_data" : "There is no Absence"}
                body = json.dumps(data)
                headers = [("Content-Type", "application/json; charset=utf-8")]
            
            return http.Response(body, headers=headers, status=200)
        
        # In case index doesn't match 'ExamTimetable'
        return http.Response("Invalid index", status=400)
    
    #StudentResults
    @http.route(['/WSNJ/HUEStudentResults'], type="http", auth="none", methods=["GET"], csrf=False)
    def NJS_HUEStudentResults(self, index=None ,studentID=None, **payload):
        #8792
        if index == 'StudentResults':
            AcadYearID = request.env['op.academic.year'].sudo().search([('current', '=', True)], limit=1).id
            semester_id = request.env['op.semesters'].sudo().search([('current', '=', True)], limit=1).id
            invoice_count = 0
            print(studentID)
            student = request.env['op.student'].sudo().search([('id', '=', studentID)], limit=1)
            check_close = self.is_closed(student.course_id.id,AcadYearID,semester_id)
            StudentGrades = False
            print('AAAAAEEEEEEEEEEEEEEEEEEEEEEEEE')
            print(student)
            print(check_close)
            if check_close:
                StudentGrades = request.env['subjects.control.student.list'].sudo().search(
                    [('student_id', '=', int(studentID)), ('connect_id.batch_id.academic_year', '=', AcadYearID),
                     ('connect_id.batch_id.semester', '=', semester_id),('subject_id','!=', '61')])
                print('AAAAAEEEEEEEEEEEEEEEEEEEEEEEEE')
                print(StudentGrades)
                degreelist = []
                for degree in StudentGrades:
                    if degree.connect_id.grade_medterm:
                        if degree.grade_medterm:
                            if  student.course_id.id == 5 :
                                item = {"subjectID": degree.subject_id.name,
                                        "subjectCode": degree.subject_id.code,
                                        "subjectHr": degree.subject_id.subject_credithours, 
                                        'Medterm': degree.grade_medterm + '|' + str(degree.connect_id.grade_medterm),
                                        'Quiz': degree.grade_quiz + '|' + str(degree.connect_id.grade_quiz) if degree.grade_quiz else str(0.0) + '|' + str(degree.connect_id.grade_quiz),
                                            }
                            else :
                                item = {"subjectID": degree.subject_id.name,
                                    "subjectCode": degree.subject_id.code,
                                    "subjectHr": degree.subject_id.subject_credithours, 
                                    'Medterm': degree.grade_medterm + '|' + str(degree.connect_id.grade_medterm),     
                                        }
                            degreelist.append(item)                 
                data = {"degreesdata" : degreelist}
                if data:
                    body = json.dumps(data)
                    headers = [("Content-Type", "application/json; charset=utf-8")]
                
            if not StudentGrades:
                data = {"degreesdata" : "There is no Degrees Available"}
                body = json.dumps(data)
                headers = [("Content-Type", "application/json; charset=utf-8")]
            
            return http.Response(body, headers=headers, status=200)
               
        # In case index doesn't match 'ExamTimetable'
        return http.Response("Invalid index", status=400)
    
    #StudentCheckBlock
    @http.route(['/WSNJ/HUECheckBlock'], type="http", auth="none", methods=["GET"], csrf=False)
    def HUECheckBlock(self, index=None, student_id=None, **payload):
        if index == 'StudentCheckBlock':
            student_data = request.env['op.student'].sudo().search([('id', '=', student_id)])
            blocked = ""
            invoice_count = 0
            curr_academic_year_invoice = request.env['op.semesters'].sudo().search([('enroll_semester', '=', True)], limit=1).term_id.academic_year_id
            if not student_data.allow_registration:
                domain = [
                    ('move_type', 'in', ['out_invoice']),
                    # ('date_due', '<=', date.today()),
                    ('invoice_date_due', '<=',curr_academic_year_invoice.invoice_date),
                    ('partner_id', '=', student_data.partner_id.id),
                    ('state', 'in', ['draft'])
                ]
                invoice_count = request.env['account.move'].sudo().search_count(domain)
    
            accum_semesters = request.env['op.student.accumlative.semesters'].sudo().search(
                [('student_id', '=', student_data.id),
                 ('transferred', '=', False)])
            for semss in accum_semesters:
                print('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF')
                print(invoice_count)
                if  invoice_count > 0:
                    print('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF')
                    blocked = "Student is Fees Blocked"
                    break
                if semss.block_result:
                    print('AASAAAAAAAAAAWWWWWWWWWWWWWWWW')
                    print(semss.block_result)
                    blocked = "Student is Blocked..." + semss.block_result.name
                    break
            
            items = []
            item = {"BlockReason": blocked}
            items.append(item)                 
            data = {"Block" : items}
            if data:
                body = json.dumps(data)
                headers = [("Content-Type", "application/json; charset=utf-8")]
                return http.Response(body, headers=headers, status=200)
        
        # In case index doesn't match 'ExamTimetable'
        return http.Response("Invalid index", status=400)
    
############################ New SDS #############################################
    @http.route(["/ims/oneroster2/v1p1/academicSessions"], type="http", auth="none", methods=["GET"], csrf=False)
    def oneroster_academicSessions2(self, id=None, **payload):
        domain = []
        limit = False
        offset = False
        check = False
        check2 = False
        filters = False
        if payload.get("offset"):
            offset = int(payload["offset"])
        if payload.get("limit"):
            limit = int(payload.get("limit"))
        role = False
        if payload.get("filter"):
            filters = (payload.get("filter"))
            dict_Of_filters = {}
        curr_academic_year = request.env['op.academic.year'].sudo().search([('current', '=', True)])
        curr_semester = request.env['op.semesters'].sudo().search([('sds_current', '=', True)])
            # role = str(filters.split('=')[1]).replace("'", "")
            # role = role.replace("AND status", "").replace(" ", "")
        try:
            if role:
                domain.append(('school_year', '=', role))
            if filters:
                if "dateLastModified" in filters:
                    check = True
                    check2 == False
                if "sourcedId" in filters :
                    check2 = True
                    academicSessions_json = []
                    batches_count = 0
            academicSessions_json = []
            children = []
            batches_count = 0
            if check2 == False:
                if check:
                    batches = request.env['op.batch'].sudo().search([('semester', '=', curr_semester.id), ('academic_year', '=', curr_academic_year.id),('write_date','>',filters.split('>')[1])], offset=offset,limit=limit)
                    batches_count = request.env['op.batch'].sudo().search_count([('semester', '=', curr_semester.id), ('academic_year', '=', curr_academic_year.id),('write_date','>',filters.split('>')[1])])
                else:
                    batches = request.env['op.batch'].sudo().search([('semester', '=', curr_semester.id), ('academic_year', '=', curr_academic_year.id)], offset=offset,limit=limit)
                    batches_count = request.env['op.batch'].sudo().search_count([('semester', '=', curr_semester.id), ('academic_year', '=', curr_academic_year.id)])
                parent = {
                        "href": "/ims/oneroster2/v1p1/academicSessions",                
                        "sourcedId": str(curr_academic_year.id),
                        "type" : "schoolYear",
                        }
                if batches:
                    for batch in batches:
                        print("batch.write_date", batch.write_date)
                        item = {"sourcedId": str(batch.id),
                                "status": 'active',
                                'dateLastModified' : self.getdatezone(batch.write_date),
                                'title': batch.name,
                                'startDate': str(batch.start_date),
                                'endDate': str(batch.end_date),
                                'parent' : parent,
                                'type': 'term',
                                'schoolYear': str(int(batch.academic_year.year)+1)
                        }
                        item2 = {
                            "href": "/ims/oneroster2/v1p1/academicSessions",                
                            "sourcedId":str(batch.id),
                            "type" : "academicSession",
                        }
                        children.append(item2)
                        academicSessions_json.append(item)
                    academicSessions_json.append(
                            {"sourcedId": str(curr_academic_year.id),
                             "status": 'active',
                             'dateLastModified' : self.getdatezone(curr_academic_year.write_date),
                             # "dateLastModified": datetime.strptime(curr_academic_year.write_date, "%Y-%m-%dT%H:%M:%S.%f%Z"),
                             'title': curr_academic_year.name,
                             "children" : children,
                             'startDate': str(curr_academic_year.start_date),
                             'endDate': str(curr_academic_year.end_date),
                             'type': 'schoolYear',
                             'schoolYear': str(int(curr_academic_year.year)+1)
                                }
                    )
            data = {"academicSessions": academicSessions_json}
            print("data", data)
            if data:
                body = json.dumps(data)
               
                headers = [
                    ("X-Total-Count", batches_count),
                    ("Content-Type", "application/json; charset=utf-8")]
                status = 200
                return self._response(headers, body, status)
        except Exception as e:
            return http.Response(json.dumps({'error': e.__str__(), 'status_code': 500},
                                       sort_keys=True, indent=4),
                            content_type='application/json;charset=utf-8', status=200) 
    
    # Classes
    @http.route(["/ims/oneroster2/v1p1/classes"], type="http", auth="none", methods=["GET"],csrf=False)
    def oneroster_classes2(self, id=None, school_id=None, **payload):
        domain = []
        limit = False
        offset = False
        check = False
        check2 = False
        filters = False
        if payload.get("offset"):
            offset = int(payload["offset"])
        if payload.get("limit"):
            limit = int(payload.get("limit"))
        if payload.get("filter"):
            filters = (payload.get("filter"))
        classes_json = []
        curr_classes_count = 0
        company = request.env['res.company'].sudo().search([], limit=1).id
        class_obj = request.env['op.session.registration']
        # try:
        curr_academic_year = request.env['op.academic.year'].sudo().search([('current', '=', True)])
        curr_semester = request.env['op.semesters'].sudo().search([('sds_current', '=', True)]).id
        print('curr_academic_year', curr_academic_year,'curr_semester', curr_semester)
        classes_objc = "classes"
        if filters:
            if "dateLastModified" in filters:
                check = True
                check2 == False
            if "sourcedId" in filters :
                check2 = True
                classes_json = []
                classes_count = 0
        if check2 == False:
            if check:
                batches = request.env['op.batch'].sudo().search([('semester','=',curr_semester),('academic_year','=',curr_academic_year.id),('write_date','>',filters.split('>')[1])]).ids
            else:
                batches = request.env['op.batch'].sudo().search([('semester','=',curr_semester),('academic_year','=',curr_academic_year.id)]).ids
            domain.append(('batch_id', 'in', batches))
            domain.append(('session_sync_type', '=', 'team'))
            classes_count = class_obj.sudo().search_count(domain)
            classes = class_obj.sudo().search(domain, offset=offset, limit=limit)
            print("classes", classes)
            if classes:
                for classe in classes:
                    if classe.status == 'inactive':
                        status = 'tobedeleted'
                    else:
                        status = 'active'
                    course = {
                            "href": "/ims/oneroster2/v1p1/courses" ,               
                            "sourcedId":str(classe.subject_id.id+1000),
                            "type" : "course",
                            }
                    school = {
                        "href": "/ims/oneroster2/v1p1/orgs",
                        "sourcedId": str(classe.course_id.id),
                        "type": "program",
                    }
        
                    term = [{
                        "href": "/ims/oneroster2/v1p1/academicSessions",
                        "sourcedId": str(classe.batch_id.id),
                        "type": "term",
                    }]
                    sem = ''
                    if curr_semester == 1:
                        sem = 'Fall'
                    elif curr_semester == 2:
                        sem = 'Spring'
                    elif curr_semester == 3:
                        sem = 'Summer'
                    
                    yearcode = curr_academic_year.year_code
                    # yearcode_ = curr_academic_year.split(" ")[0]
                    print(yearcode)
                    # print(yearcode_) 
                    item = {"sourcedId": str(classe.id),
                            "status": status,
                            "dateLastModified": self.getdatezone(classe.write_date),
                            'title':  sem + '-'+ str(yearcode) +'-'+ classe.name,
                            'classCode': classe.subject_id.code,
                            'classType': 'scheduled',
                            # 'location': classe.facility_id.name,
                            # 'subjectCodes': [classe.subject_id.code],
                            # 'periods':[session.timing_id.name],
                            'subjects': [classe.subject_id.name],
                            'course':course,
                            'school': school,
                            'terms': term,
                            'grades' : [self.getsubjectlevel(classe.subject_id,classe.course_id)]
                            }
                    
                    classes_json.append(item)
        data = {classes_objc: classes_json}
        if data:
            # print(data)
            body = json.dumps(data)
            headers = [
                ("X-Total-Count", classes_count),
                ("Content-Type", "application/json; charset=utf-8")]
            status = 200
            return self._response(headers, body, status)    
    
    #Courses = Subjects
    @http.route(["/ims/oneroster2/v1p1/courses"], type="http", auth="none",methods=["GET"], csrf=False)
    def oneroster_courses2(self, id=None, **kw):
        domain = []
        courses_objc = 'courses'
        limit = False
        offset = False
        filters = False
        check = False
        check2 = False
        if kw.get("offset"):
            offset = int(kw["offset"])
        if kw.get("limit"):
            limit = int(kw.get("limit"))
        if kw.get("filter"):
            filters = (kw.get("filter"))
        # courses = request.env['op.subject'].sudo().search([], offset=offset, limit=limit)
        
        curr_academic_year = request.env['op.academic.year'].sudo().search([('current', '=', True)]).id
        curr_semester = request.env['op.semesters'].sudo().search([('sds_current', '=', True)]).id
        courses = []
        course_count = 0
        try:
            if filters:
                # print(filters.split('=')[1])
                if "dateLastModified" in filters:
                    check = True
                    check2 == False
                if "sourcedId" in filters :
                    check2 = True
                    courses = []
                    course_count = 0
            if check2 == False:
                if check:
                    batches = request.env['hue.subject.registration'].sudo().search([('batch_id.academic_year','=',curr_academic_year),('batch_id.semester','=',curr_semester),('write_date','>',filters.split('>')[1])], offset=offset, limit=limit)
                    course_count = request.env['hue.subject.registration'].sudo().search_count([('batch_id.academic_year','=',curr_academic_year),('batch_id.semester','=',curr_semester),('write_date','>',filters.split('>')[1])])
                else:
                    batches = request.env['hue.subject.registration'].sudo().search([('batch_id.academic_year','=',curr_academic_year),('batch_id.semester','=',curr_semester)], offset=offset, limit=limit)
                    course_count = request.env['hue.subject.registration'].sudo().search_count([('batch_id.academic_year','=',curr_academic_year),('batch_id.semester','=',curr_semester)])
                for course in batches:
                    item = ""
                    academicsession = {
                        "href": "/ims/oneroster2/v1p1/academicSessions",
                        "sourcedId": str(course.batch_id.id),
                        "type": "term",
                        }
                    schools = {
                        "href": "/ims/oneroster2/v1p1/orgs",
                        "sourcedId": str(course.batch_id.course_id.id),
                        "type": "program",
                        }
                    item = {"sourcedId": str(course.subject_id.id+1000),
                           "status": 'active',
                           "dateLastModified": self.getdatezone(course.write_date),
                           "title": str(course.subject_id.name),
                           "schoolYear": academicsession,
                           "courseCode": course.subject_id.code,
                           "grades": [self.getcourselevel(course.subject_level)],
                           "subjects": [str(course.subject_id.name)],
                           "org" : schools
                           }
                    courses.append(item)
            data = {courses_objc: courses}
            body = json.dumps(data)
            headers = [
                ("X-Total-Count", course_count),
                ("Content-Type", "application/json; charset=utf-8")]
            status = 200
            return self._response(headers, body, status)
        except Exception as e:
            return http.Response(json.dumps({'error': e.__str__(), 'status_code': 500},
                                       sort_keys=True, indent=4),
                            content_type='application/json;charset=utf-8', status=200)
    
    #Enrollments
    @http.route(["/ims/oneroster2/v1p1/enrollments"],type="http", auth="none", methods=["GET"], csrf=False)
    def oneroster_enrollments2(self, id=None, **payload):
        domain = []
        limit = False
        offset = False
        filters = False
        check = False
        check2 = False
        if payload.get("offset"):
            offset = int(payload["offset"])
        if payload.get("limit"):
            limit = int(payload.get("limit"))
        if payload.get("filter"):
            filters = (payload.get("filter"))
        enrollments_json = []
        enrollments_objc = ""
        enrollment_count = 0
        # if offset == 100 :
        # offset = 100000000000
        status_ids = request.env['hue.std.data.status'].sudo().search([('active_invoice', '=', True)])._ids
        try:
            enrollments_objc = "enrollments"
            # if filters:
            #     role = str(filters.split('=')[1]).replace("'", "")
            # else:
            #     role = False
            # _school_id = int(school_id)
            curr_academic_year = request.env['op.academic.year'].sudo().search([('current', '=', True)]).id
            curr_semester = request.env['op.semesters'].sudo().search([('sds_current', '=', True)]).id
            batches = request.env['op.batch'].sudo().search([('semester','=',curr_semester),('academic_year','=',curr_academic_year)]).ids
            
            domain.append(('batch_id', 'in', batches))
            domain.append(('session_sync_type', '=', 'team'))   
            sessions = request.env['op.session.registration'].sudo().search(domain).ids
            print(len(sessions))
            if filters:
                if "dateLastModified" in filters:
                    check = True
                    check2 == False
                if "sourcedId" in filters :
                    check2 = True
                    enrollments_json = []
                    enrollment_count = 0
            if check2 == False:
                if check:
                    enrollment_ids = request.env['op.session.registration.enrollment'].sudo().search([('registration_enrollment_id', 'in', sessions),('write_date','>',filters.split('>')[1])], offset=offset, limit=limit)
                    enrollment_count = request.env['op.session.registration.enrollment'].sudo().search_count([('registration_enrollment_id', 'in', sessions),('write_date','>',filters.split('>')[1])])
                else:
                    enrollment_ids = request.env['op.session.registration.enrollment'].sudo().search([('registration_enrollment_id', 'in', sessions)], offset=offset, limit=limit)
                    enrollment_count = request.env['op.session.registration.enrollment'].sudo().search_count([('registration_enrollment_id', 'in', sessions)])
                    
                if enrollment_ids:
                    for enrollment in enrollment_ids:
                        school = {
                            "href": "/ims/oneroster2/v1p1/orgs",
                            "sourcedId": str(enrollment.course_id.id),
                            "type": "program",
                            }
                        student_class = {
                            "href": "/ims/oneroster2/v1p1/classes",
                            "sourcedId": str(enrollment.registration_enrollment_id.id),
                            "type": "class",
                        }
                        if enrollment.role == 'student':
                            if enrollment.student_id.student_status.id not in status_ids:
                                continue
        
                            user = {
                                "href": "/ims/oneroster2/v1p1/users",
                                "sourcedId": str(int(enrollment.student_id.id)+2000000),
                                "type": "user",
                            }
                            role = 'student'
                        if enrollment.role == 'teacher':
                            user = {
                                "href": "/ims/oneroster2/v1p1/users",
                                "sourcedId": str(int(enrollment.teacher_id.id)+1000000),
                                "type": "user",
                            }
                            role = 'teacher'
                        if enrollment.role == 'administrator':
                            user = {
                                "href": "/ims/oneroster2/v1p1/users",
                                "sourcedId": str(int(enrollment.teacher_id.id)+1000000),
                                "type": "user",
                            }
                            role = 'administrator'
                        
                        status = 'active'
                        if enrollment.status == 'inactive':
                            status = 'tobedeleted'
                        if enrollment.id == 1495904:
                            item = {"sourcedId": str(enrollment.id),
                                    "status": status,
                                    # "dateLastModified": self.getdatezone(enrollment.write_date),
                                    "dateLastModified": "2023-07-26T13:01:01.521Z",
                                    'role': role,
                                    'primary': enrollment.primary,
                                    'user': user,
                                    'class': student_class,
                                    'school': school,
                                    'beginDate': str(enrollment.registration_enrollment_id.batch_id.start_date),
                                    'endDate': str(enrollment.registration_enrollment_id.batch_id.end_date),
                                }
                        else:
                            item = {"sourcedId": str(enrollment.id),
                                    "status": status,
                                    #"dateLastModified": self.getdatezone(enrollment.write_date),
                                    "dateLastModified": "2023-11-15T13:00:00.000000Z",
                                    'role': role,
                                    'primary': enrollment.primary,
                                    'user': user,
                                    'class': student_class,
                                    'school': school,
                                    'beginDate': str(enrollment.registration_enrollment_id.batch_id.start_date),
                                    'endDate': str(enrollment.registration_enrollment_id.batch_id.end_date),
                                }
                        enrollments_json.append(item)
            
            data = {enrollments_objc: enrollments_json}
            if data:
                body = json.dumps(data)
                # print(data)
                headers = [
                    ("X-Total-Count", enrollment_count),
                    ("Content-Type", "application/json; charset=utf-8"), ("Cache-Control", "no-store"),
                    ("Pragma", "no-cache")]
                status = 200
                return self._response(headers, body, status)
        except Exception as e:
            return http.Response(json.dumps({'error': e.__str__(), 'status_code': 500},
                                       sort_keys=True, indent=4),
                            content_type='application/json;charset=utf-8', status=200)
    
    # Users    
    @http.route(["/ims/oneroster2/v1p1/users"], type="http", auth="none", methods=["GET"], csrf=False)
    def oneroster_users2(self, id=None, **payload):
        limit = False
        offset = False
        filters = False
        check = False
        check2 = False
        Stds = request.env['op.student']
        teachers = request.env['op.faculty']
        status_ids = request.env['hue.std.data.status'].sudo().search([('active_invoice', '=', True)])._ids
        domain = []
        domain_t = []
        if payload.get("offset"):
            offset = int(payload["offset"])
        if payload.get("limit"):
            limit = int(payload.get("limit"))
        if payload.get("filter"):
            filters = (payload.get("filter"))
        users_json = []
        
        try:
            users_objc = "users"
            curr_academic_year = request.env['op.academic.year'].sudo().search([('current', '=', True)]).id
            curr_semester = request.env['op.semesters'].sudo().search([('sds_current', '=', True)]).id
            
            # domain.append(('student_status', 'in', status_ids))
            students_count = Stds.sudo().search_count(domain)
            users = Stds.sudo().search(domain, offset=offset, limit=limit)
            ##### teachers
            users_count = 0
            if filters:
                # print(filters.split('=')[1])
                if "dateLastModified" in filters:
                    check = True
                    check2 == False
                if "sourcedId" in filters :
                    check2 = True
                    users_json = []
                    # students_count = 0
                    # teachers_count = 0
                    users_count = 0
            if check2 == False:
                if check:
                    batches = request.env['op.batch'].sudo().search([('semester', '=', curr_semester), ('academic_year', '=', curr_academic_year)]).ids
                    # users = request.env['op.student'].sudo().search([('student_status', 'in', status_ids),('write_date','>',filters.split('>')[1])], offset=offset, limit=limit) ,('write_date','>',filters.split('>')[1])
                else:
                    batches = request.env['op.batch'].sudo().search([('semester', '=', curr_semester), ('academic_year', '=', curr_academic_year)]).ids
                    
                sessions_ids = request.env['op.session.registration'].sudo().search([('batch_id', 'in', batches)]).ids
    
                sessions = request.env['op.session.registration.enrollment'].sudo().search(
                    [('registration_enrollment_id', 'in', sessions_ids), ('role', 'in', ['teacher', 'administrator', 'student'])])
                print("sessions", sessions)
                allusers = []
                faculty_ids = sessions.mapped('teacher_id')
                print("faculty_ids", faculty_ids)
                allusers.append(faculty_ids)
                student_ids = sessions.mapped('student_id')
                allusers.append(student_ids)
                sql = ("select id,(select name from hr_employee where id = t1.emp_id) username \n"
                        + " ,(select work_email from hr_employee where id = t1.emp_id) email \n"
                        + " ,(select mobile_phone from hr_employee where id = t1.emp_id) mobile,'1000' course_id,write_date,'teacher' usertype from op_faculty t1 where id in "+str(faculty_ids._ids)+" \n"
                        + " union \n"
                        + " select id,en_name username,cast(student_code as varchar),stumobile,course_id,write_date,'student' usertype from op_student where en_name is not null and student_status in "+str(status_ids)+" \n"
                        )
                request.env.cr.execute(sql)
                users = request.env.cr.dictfetchall()
                users_count = len(users)
                if limit :
                    sql = ("select id,(select name from hr_employee where id = t1.emp_id) username \n"
                            + " ,(select work_email from hr_employee where id = t1.emp_id) email \n"
                            + " ,(select mobile_phone from hr_employee where id = t1.emp_id) mobile,'1000' course_id,write_date,'teacher' usertype from op_faculty t1 where id in "+str(faculty_ids._ids)+" \n"
                            + " union \n"
                            + " select id,en_name username,cast(student_code as varchar),stumobile,course_id,write_date,'student' usertype from op_student where en_name is not null and student_status in "+str(status_ids)+" \n"
                            + " LIMIT "+str(limit)+" OFFSET "+ str(offset)
                            )
                    request.env.cr.execute(sql)
                    users = request.env.cr.dictfetchall()
                _logger.info('sql..............................')
                _logger.info(sql)
                _logger.info('sssssssssssssssssssssssssssssssssssssss')
                for user in users:
                    if user["username"] != '':
                        name = (user["username"]).lstrip(' ')
                        data = name.split(" ")
                        try:
                            familyName = data[1]
                        except:
                            familyName = data[0]
                    else:
                        name = ''
                        familyName = ''
                    email = ''
                    userid = ''
                    levelID = False
                    if user["usertype"] == 'teacher' or user["usertype"] == 'administrator':
                        orgs = [{
                            "href": "/ims/oneroster2/v1p1/orgs",
                            "sourcedId": "1000",
                            "type": "university",
                        }]
                        email = user["email"]
                        userid = str(user["id"])
                    else:
                        orgs = [{
                            "href": "/ims/oneroster2/v1p1/orgs",
                            "sourcedId": str(user["course_id"]),
                            "type": "program",
                        }]
                        email = user["email"]+'@horus.edu.eg'
                        userid = str(user["id"])
                        stuID = request.env['op.student'].sudo().search([('id', '=', int(user["id"]))], limit=1)
                        levelID = self.getstulevel(stuID.level.id)
                                    
                    username = email.split("@", 1)
                    if user["mobile"] != None:
                        if levelID:
                            item = {"sourcedId": str(int(userid)+2000000),
                                "status": 'active',
                                "dateLastModified": self.getdatezone2(user["write_date"]),
                                'username': username[0],
                                'givenName': data[0],
                                'familyName': familyName,
                                'enabledUser': 'true',
                                'role': str(user["usertype"]),
                                'email': email,
                                'identifier': str(user["email"]),
                                'sms': '+2'+str(user["mobile"]),
                                'phone': '+2'+str(user["mobile"]),
                                'orgs': orgs,
                                'grades': [levelID],
                                }
                        else:
                            item = {"sourcedId": str(int(userid)+1000000),
                                "status": 'active',
                                "dateLastModified": self.getdatezone2(user["write_date"]),
                                'username': username[0],
                                'givenName': data[0],
                                'familyName': familyName,
                                'enabledUser': 'true',
                                'role': str(user["usertype"]),
                                'email': email,
                                'identifier': str(user["email"]),
                                'sms': '+2'+str(user["mobile"]),
                                'phone': '+2'+str(user["mobile"]),
                                'orgs': orgs,
                                }
                    else:
                        if levelID:
                            item = {"sourcedId": str(int(userid)+2000000),
                                "status": 'active',
                                "dateLastModified": self.getdatezone2(user["write_date"]),
                                'username': username[0],
                                'givenName': data[0],
                                'familyName': familyName,
                                'enabledUser': 'true',
                                'role': str(user["usertype"]),
                                'email': email,
                                'identifier': str(user["email"]),
                                'orgs': orgs,
                                'grades': [levelID],
                                }
                        else:
                            item = {"sourcedId": str(int(userid)+1000000),
                                "status": 'active',
                                "dateLastModified": self.getdatezone2(user["write_date"]),
                                'username': username[0],
                                'givenName': data[0],
                                'familyName': familyName,
                                'enabledUser': 'true',
                                'role': str(user["usertype"]),
                                'email': email,
                                'identifier': str(user["email"]),
                                'orgs': orgs
                                }
                    users_json.append(item)
                
            data = {users_objc: users_json}
            if data:
                # print(users_json)
                body = json.dumps(data)
                headers = [
                    ("X-Total-Count", users_count),
                    ("Content-Type", "application/json; charset=utf-8"), ("Cache-Control", "no-store"),
                    ("Pragma", "no-cache")]
                status = 200
                return self._response(headers, body, status)
        except Exception as e:
            return http.Response(json.dumps({'error': e.__str__(), 'status_code': 500},
                                       sort_keys=True, indent=4),
                            content_type='application/json;charset=utf-8', status=200)    
    
    # Org 
    @http.route(["/ims/oneroster2/v1p1/orgs"], type="http", auth="none",methods=["GET"], csrf=False)
    def oneroster_org2(self, id=None, **kw):
        faculty = request.env['hue.faculties']
        domain = []
        org_objc = 'orgs'
        limit = False
        offset = False
        filters = False
        check = False
        check2 = False
        if kw.get("offset"):
            offset = int(kw["offset"])
        if kw.get("limit"):
            limit = int(kw.get("limit"))
        if kw.get("filter"):
            filters = (kw.get("filter"))
            
        curr_academic_year = request.env['op.academic.year'].sudo().search([('current', '=', True)]).id
        curr_semester = request.env['op.semesters'].sudo().search([('sds_current', '=', True)]).id
        # curr_semester = 1
        try:
            if filters:
                # print(filters.split('=')[1])
                if "dateLastModified" in filters:
                    check = True
                    check2 == False
                if "sourcedId" in filters :
                    check2 = True
                    courses = []
                    orgs_count = 0
            if check2 == False:
                if check:
                    orgs = faculty.sudo().search([('write_date','>',filters.split('>')[1])], offset=offset, limit=limit)
                    orgs_count = faculty.sudo().search_count([('write_date','>',filters.split('>')[1])])
                else:
                    orgs = faculty.sudo().search([], offset=offset, limit=limit)
                    orgs_count = faculty.sudo().search_count(domain)
                faculty = []
                courses = []
                if orgs:
                    for fac in orgs:
                        schools = []
                        domain = []
                        domain.append(('faculty_id', '=', fac.id))
                        schools_data = request.env['op.course'].sudo().search(domain, offset=offset, limit=limit)
                        
                        faculty.append(
                            {
                            "href": "/ims/oneroster2/v1p1/orgs",                
                            "sourcedId":str(fac.id+100),
                            "type" : "college",
                            }
                        )
                        
                        parent = {
                                "href": "/ims/oneroster2/v1p1/orgs",                
                                "sourcedId":str("1000"),
                                "type" : "university",
                                }
                        for school in schools_data:
                            item = {
                                "href": "/ims/oneroster2/v1p1/orgs",
                                "sourcedId": str(school.id),
                                "type": "program",
                            }
                            schools.append(item)
                        
                        children = [schools]
                        org = {"sourcedId": str(fac.id+100),
                                   "status": 'active',
                                   "dateLastModified": self.getdatezone(fac.write_date),
                                   "name": str(fac.name),
                                   "type": 'college',
                                   "identifier": str(fac.name),
                                   "children" : children,
                                   "parent" : parent
                                   # "org" : schools
                                   }
                        courses.append(org)
                    
                    hue_data = request.env['res.company'].sudo().search([])
                    courses.append(
                            {"sourcedId": 1000,
                                   "status": 'active',
                                   "dateLastModified": self.getdatezone(fac.write_date),
                                   "name": hue_data.vat,
                                   "type": 'university',
                                   "identifier": hue_data.name,
                                   "children" : faculty
                            })
                    
                    schools_data = request.env['op.course'].sudo().search([])
                    
                    for school in schools_data:
                        parent_fac = {
                                "href": "/ims/oneroster2/v1p1/orgs",                
                                "sourcedId":str(school.faculty_id.id+100),
                                "type" : "college",
                                }
                        item ={
                            "sourcedId": str(school.id),
                               "status": 'active',
                               "dateLastModified": self.getdatezone(school.write_date),
                               "name": str(school.name),
                               "type": 'program',
                               "identifier": str(school.name),
                               "parent" : parent_fac,
                        }
                        courses.append(item)
            
            data = {org_objc: courses}
            body = json.dumps(data)
            print(body)
            headers = [
                ("X-Total-Count", orgs_count),
                ("Content-Type", "application/json; charset=utf-8")]
            status = 200
            return self._response(headers, body, status)
        except Exception as e:
            return http.Response(json.dumps({'error': e.__str__(), 'status_code': 500},
                                       sort_keys=True, indent=4),
                            content_type='application/json;charset=utf-8', status=200)
            
    
    @http.route('/oauth2/access_token', type='http', methods=["POST"], auth='public', csrf=False)
    def access_token(self, **kw):
        """This method is used for generate access token for auth2 as a service"""
        _logger.info('token...........111111111111111111111..................................')
        grant_type = kw.get('grant_type', False)
        client_id = kw.get('client_id', False)
        client_secret = kw.get('client_secret', False)
        error = {}
        ACCESS_TOKEN_EXPIRE_SECONDS = 60 * 60
        expires = datetime.now() + timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS)
        access_token = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(40)])
        body = json.dumps({
            'access_token': access_token,
            'token_type': 'bearer',
            'access_token_validity': expires.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            # 'refresh_token': refresh_token,
        })
        headers = [("Cache-Control", "no-store"), ("Pragma", "no-cache")]
        status = 200
        token_vals = {
            'access_token': access_token,
            'access_token_validity': expires.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
        }
        
        _logger.info(token_vals)
        _logger.info('token.............................................')
        print("token_vals")
        print(token_vals)
        return self._response(headers, body, status)