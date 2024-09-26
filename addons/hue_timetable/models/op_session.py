from odoo import models, fields, api, _
import calendar
from dateutil.relativedelta import relativedelta
import time
import pytz
import json
import requests
from dateutil import tz
from odoo.exceptions import UserError, ValidationError
import math
import logging
import datetime
from datetime import date, timedelta, time

_logger = logging.getLogger(__name__)


class OpSession(models.Model):
    _inherit = 'op.session'
    
    name = fields.Char(compute='_compute_name', string='Name', store=False)
    to_timing_id = fields.Many2one('op.timing', 'To Timing', tracking=True, required=True, domain="[('id', 'in', suitable_to_timing_ids)]")
    suitable_to_timing_ids = fields.Many2many('op.timing', compute='_compute_suitable_to_timing_ids',) #to add domain to timings
    timing_id = fields.Many2one(required=True)
    start_datetime = fields.Datetime(required=False)
    end_datetime = fields.Datetime(required=False)
    session_date = fields.Date()#required=True
    subject_level = fields.Many2one('op.levels', 'Level', store=True , compute="_compute_subject_level")
    session_type = fields.Selection([('Lecture', 'Lecture'), ('Section', 'Section'), ('Lab', 'Lab')], 'Type',default='Lecture',required=True)
    sub_classroom = fields.Integer('Section', tracking=True)
    student_count = fields.Integer(string='Max Count', required=True,compute='_student_count')
    reg_student_count = fields.Integer(string='Registered Count',required=True, tracking=True,compute='_reg_count')
    student_ids = fields.Many2many('op.student', 'student_session_rel', 'session_id', 'student_id','Registration Students', tracking=True)
    similarity = fields.Boolean('Similarity', tracking=True)
    similar_session_ids = fields.Many2many('op.session', 'similar_session_rel', 'session_id', 'similar_id', string='Similar Sessions')
    synced = fields.Boolean()
    is_parent = fields.Boolean()
    parent_session = fields.Many2one('op.session')
    child_session = fields.One2many('op.session','parent_session')
    faculty_id = fields.Many2one('op.faculty', 'Faculty', required=False)
    faculty_ids = fields.Many2many('op.faculty','session_faculty_rel', 'session_id', 'faculty_id', 'Faculties', tracking=True, domain="[('id', 'in', suitable_faculty_ids)]")
    q_faculty_ids = fields.Many2many('op.faculty', 'session_q_faculty_rel', 'session_id', 'faculty_id', 'Q Faculties', tracking=True, domain="[('id', 'in', suitable_faculty_ids)]")
    suitable_faculty_ids = fields.Many2many('op.faculty', compute='_compute_suitable_faculty_ids',) #to add domain to faculties
    facility_id = fields.Many2one('op.facility', 'Facility', required=True, tracking=True, domain="[('id', 'in', suitable_facility_ids)]")
    suitable_facility_ids = fields.Many2many('op.facility', compute='_compute_suitable_faculty_ids',) #to add domain to facilities
    classroom_id = fields.Many2one('op.classroom', 'Group', tracking=True, required=True)    
    
    @api.constrains('start_datetime', 'end_datetime')
    def _check_date_time(self):
        pass
    
    
    #Add domain to facility and faculty ids
    @api.onchange('to_timing_id')
    def _compute_suitable_faculty_ids(self):
        for m in self:
            m.suitable_facility_ids = False
            m.suitable_faculty_ids = False
            college = m.batch_id.course_id.faculty_id
            domain = None
            facility_ids = []
            faculities_ids = []
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            subject = False
            
            if m.timing_id and m.batch_id and m.subject_id:
                for course_subject in m.batch_id.subject_registration_ids:
                    if course_subject.subject_id.id == m.subject_id.id:
                        subject = course_subject
                        break
            
            if m.timing_id and m.to_timing_id:
                facilities = self.env['op.facility'].search([])
                faculities = self.env['op.faculty'].search([])
                for facility in facilities:
                    other_sessions = self.env['op.session'].search([
                        ('facility_id', '=', facility.id),
                        ('batch_id.academic_year', '=', m.batch_id.academic_year.id),
                        ('batch_id.semester', '=', m.batch_id.semester.id),
                        ('type', '=', m.type),
                        '|', '&',
                        ('timing_id.sequence', '<=', m.timing_id.sequence),
                        ('to_timing_id.sequence', '>=', m.to_timing_id.sequence),
                        '|', '&',
                        ('timing_id.sequence', '>=', m.timing_id.sequence),
                        ('to_timing_id.sequence', '<=', m.to_timing_id.sequence),
                        '|', '&',
                        ('timing_id.sequence', '<=', m.timing_id.sequence),
                        ('to_timing_id.sequence', '>', m.timing_id.sequence),
                        '&',
                        ('timing_id.sequence', '<', m.to_timing_id.id),
                        ('to_timing_id.sequence', '>=', m.to_timing_id.sequence),
                    ])

                    if not other_sessions:
                        if facility.college_only and facility.college_id.id == college.id:
                            facility_ids.append(facility.id)
                        elif not facility.college_only:
                            facility_ids.append(facility.id)

                for faculty in faculities:
                    other_sessions = self.env['op.session'].search([
                        ('faculty_ids', '=', faculty.id),
                        ('batch_id.academic_year', '=', m.batch_id.academic_year.id),
                        ('batch_id.semester', '=', m.batch_id.semester.id),
                        ('type', '=', m.type),
                        '|', '&',
                        ('timing_id', '<=', m.timing_id.id),
                        ('to_timing_id', '>=', m.to_timing_id.id),
                        '|', '&',
                        ('timing_id', '>=', m.timing_id.id),
                        ('to_timing_id', '<=', m.to_timing_id.id),
                        '|', '&',
                        ('timing_id', '<=', m.timing_id.id),
                        ('to_timing_id', '>', m.timing_id.id),
                        '&',
                        ('timing_id', '<', m.to_timing_id.id),
                        ('to_timing_id', '>=', m.to_timing_id.id),
                    ])
                    if not other_sessions:
                        faculities_ids.append(faculty.id)
            m.suitable_facility_ids = facility_ids
            m.suitable_faculty_ids = faculities_ids


    #Add domain to timing to
    @api.onchange('timing_id')
    def _compute_suitable_to_timing_ids(self):
        print("777777777777777777777777777777777777777777777777777")
        for m in self:
            facility_ids = []
            faculities_ids = []
            crsHrs = 0
            subject_id = self.env['hue.subject.registration'].search(
                [('batch_id', '=', m.batch_id.id), ('subject_id', '=', m.subject_id.id)], limit=1)
            if m.session_type == "Lecture":
                crsHrs = subject_id.lecture_hours
            elif m.session_type == "Section":
                crsHrs = subject_id.section_hours
            elif m.session_type == "Lab":
                crsHrs = subject_id.practical_hours

            session_hours = 0
            domain = []
            if not m.batch_id.default_week_start:
                m.suitable_to_timing_ids = self.env['op.timing'].search([])
                break
            if not m.batch_id.default_week_end:
                m.suitable_to_timing_ids = self.env['op.timing'].search([])
                break
            if m.session_type == 'Lecture':
                timing_sessions = self.env['op.session'].search([
                    # ('facility_id', '=', facility.id),
                    ('batch_id', '=', m.batch_id.id),
                    ('session_type', '=', m.session_type),
                    ('subject_id', '=', m.subject_id.id),
                    ('classroom_id', '=', m.classroom_id.id),
                    ('start_datetime', '>=', str(m.batch_id.default_week_start) + " 00:00:00"),
                    ('end_datetime', '<=', str(m.batch_id.default_week_end) + " 23:59:00"),
                ])                
            else:
                timing_sessions = self.env['op.session'].search([
                    ('sub_classroom', '=', m.sub_classroom),
                    ('batch_id', '=', m.batch_id.id),
                    ('session_type', '=', m.session_type),
                    ('subject_id', '=', m.subject_id.id),
                    ('classroom_id', '=', m.classroom_id.id),
                    ('start_datetime', '>=', str(m.batch_id.default_week_start) + " 00:00:00"),
                    ('end_datetime', '<=', str(m.batch_id.default_week_end) + " 23:59:00"),
                ])
            if timing_sessions:
                for timing_session in timing_sessions:
                    session_hours = session_hours + (timing_session.to_timing_id.time - timing_session.timing_id.time)
            hour = crsHrs + m.timing_id.time - session_hours
            timing = self.env['op.timing'].search([]).filtered(lambda r: r.time > m.timing_id.time and r.time <= hour)
            tt = self.env['op.timing'].search([])
            timing = timing.ids
            if timing:
                m.suitable_to_timing_ids = timing
            else:
                m.suitable_to_timing_ids = self.env['op.timing'].search([])

    
    #  session  name
    @api.depends('subject_id', 'session_date')
    def _compute_name(self):
        for session in self:
            subc = ''
            if session.session_type != 'Lecture':
                subc = str(session.sub_classroom)
            if session.subject_id and session.session_date:
                session.name = session.subject_id.sudo().name.split('|')[0] + ' / ' + str(session.session_type) + ' ' + str(session.classroom_id.sudo().name) + subc + ' / ' + str(
                    session.session_date) + ' ' + str(session.timing_id.sudo().name) + ' ' + str(session.type)
            else:
                session.name = False
               
                
    #   reg student count
    @api.depends('student_ids')
    def _reg_count(self):
        for session in self:
            cnt = 0
            stu_reg = self.env['hue.student.registration'].sudo().search_count([
                        ('batch_id.semester', '=', session.batch_id.semester.id),
                        ('batch_id.academic_year', '=', session.batch_id.academic_year.id),
                        ('session_id', '=', session.id)])
            cnt +=stu_reg
            for sess in session.similar_session_ids:
                simmilar_stu_reg = self.env['hue.student.registration'].sudo().search_count([
                        ('batch_id.semester', '=', sess.batch_id.semester.id),
                        ('batch_id.academic_year', '=', sess.batch_id.academic_year.id),
                        ('session_id', '=', sess.id)])
                cnt +=simmilar_stu_reg
            session.reg_student_count = cnt
            
            
    #   reg student count
    @api.depends('facility_id')
    def _student_count(self):
        for session in self:
            session.student_count =0
            if session.facility_id:
                session.student_count = session.facility_id.study_capacity
            
            
    #   subject level
    @api.depends('subject_id', 'course_id')
    def _compute_subject_level(self):
        for rec in self:
            if rec.course_id and rec.subject_id:
                course_subject = self.env['op.subject'].search(
                    [('course_id', '=', rec.course_id.id), ('id', '=', rec.subject_id.id)], limit=1)
                rec.subject_level = course_subject.subject_level.id


    @api.depends('start_datetime', 'end_datetime')
    def _compute_timing(self):
        tz = pytz.timezone(self.env.user.tz)
        for session in self:
            if not session.start_datetime:
                session.timing = "00:00"
                continue
            if not session.end_datetime:
                session.timing = "00:00"
                continue
            session.timing = str(session.start_datetime.astimezone(tz).strftime('%I:%M%p')) + ' - ' + str(
                session.end_datetime.astimezone(tz).strftime('%I:%M%p'))   
   
        
    #sync child
    def sync_child_session(self):
        self.write({'synced':True,'is_parent':True})
        start_date = datetime.datetime.strptime(
            str(self.batch_id.default_week_start), '%Y-%m-%d')
        start_date = start_date+relativedelta(days=+7)
        end_date = datetime.datetime.strptime(str(self.batch_id.end_date), '%Y-%m-%d')
        gap = 2
        #Added to compute Start & End
        midnight = datetime.datetime.combine(date.today(), time.min)
        time_delta_start = timedelta(hours=(self.timing_id.time-gap))
        time_delta_end = timedelta(hours=(self.to_timing_id.time-gap))
        time_obj_start = (midnight + time_delta_start).time()
        time_obj_end = (midnight + time_delta_end).time()
        #end
        for n in range((end_date - start_date).days + 1):
            curr_date = start_date + datetime.timedelta(n)
            Day = self.type
            Day = Day.strip()
            if Day == 'Saturday':
                weekday = 5
            if Day == 'Sunday':
                weekday = 6
            if Day == 'Monday':
                weekday = 0
            if Day == 'Tuesday':
                weekday = 1
            if Day == 'Wednesday':
                weekday = 2
            if Day == 'Thursday':
                weekday = 3
            if Day == 'Friday':
                weekday = 4
            if int(weekday) == curr_date.weekday():
                print(curr_date)
                hour = self.timing_id.hour
                to_hour = self.to_timing_id.hour
                if self.timing_id.am_pm == 'pm' and int(hour) != 12:
                    hour = int(hour) + 12
                if self.to_timing_id.am_pm == 'pm' and int(to_hour) != 12:
                    to_hour = int(to_hour) + 12
                per_time = '%s:%s:00' % (hour, self.timing_id.minute)
                per_time_to = '%s:%s:00' % (to_hour, self.to_timing_id.minute)
                final_date = datetime.datetime.strptime(
                    curr_date.strftime('%Y-%m-%d ') +
                    per_time, '%Y-%m-%d %H:%M:%S')
                final_date_to = datetime.datetime.strptime(
                    curr_date.strftime('%Y-%m-%d ') +
                    per_time_to, '%Y-%m-%d %H:%M:%S')
                local_tz = pytz.timezone(
                    self.env.user.partner_id.tz or 'GMT')

                local_dt = local_tz.localize(final_date, is_dst=None)
                utc_dt = local_dt.astimezone(pytz.utc)
                utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")

                local_dt_to = local_tz.localize(final_date_to, is_dst=None)
                utc_dt_to = local_dt_to.astimezone(pytz.utc)
                utc_dt_to = utc_dt_to.strftime("%Y-%m-%d %H:%M:%S")

                curr_start_date = datetime.datetime.strptime(
                    utc_dt, "%Y-%m-%d %H:%M:%S")
                curr_end_date = datetime.datetime.strptime(
                    utc_dt_to, "%Y-%m-%d %H:%M:%S")
                sess = self.env['op.session'].create({
                    'faculty_id': self.faculty_id.id,
                    'faculty_ids': [(6, 0, self.faculty_ids.ids)],
                    'q_faculty_ids': [(6, 0, self.faculty_ids.ids)],
                    'subject_id': self.subject_id.id,
                    'course_id': self.course_id.id,
                    'batch_id': self.batch_id.id,
                    'timing_id': self.timing_id.id,
                    'to_timing_id': self.to_timing_id.id,
                    'classroom_id': self.classroom_id.id,
                    'facility_id': self.facility_id.id,
                    'sub_classroom': self.sub_classroom,
                    'session_type': self.session_type,
                    'session_date':curr_start_date.strftime("%Y-%m-%d %H:%M:%S"),
                    'type': self.type,
                    'student_count': self.student_count,
                    'similarity': self.similarity,
                    'parent_session': self.id,
                    'reg_student_count':0
                })
                #create event calendar for sessions
                partners = []
                if self.faculty_ids:
                    for fac in self.faculty_ids:
                        partners.append(fac.partner_id.id)
                self.env["calendar.event"].create({
                    'name': self.subject_id.name.split('|')[0]+'/'+str(self.session_type),
                    'privacy': 'public',
                    'show_as': 'busy',
                    'start': datetime.datetime.combine(curr_start_date.date(), time_obj_start),
                    'stop': datetime.datetime.combine(curr_end_date.date(), time_obj_end),
                    'location': self.facility_id.name,
                    'partner_id': self.env.user.partner_id,
                    'partner_ids': [(6, 0, partners)],
                    'session_id': sess.id
                })

                
                
    
            
    #unlink        
    def unlink(self):
        for rec in self :
            if rec.reg_student_count > 0  :
                raise ValidationError("There are students in session! Can not delete!")            
            if rec.is_parent:
                if rec.reg_student_count > 0  :
                    raise ValidationError("There are students in session! Can not delete!")
                for child in rec.child_session:
                    super(OpSession, child).unlink()
                    odoo_calendar = self.env["calendar.event"].search([('session_id','=', child.id)])
                    if odoo_calendar:
                        odoo_calendar.unlink()
            super(OpSession, rec).unlink()
            odoo_calendar = self.env["calendar.event"].search([('session_id','=', rec.id)])
            if odoo_calendar:
                odoo_calendar.unlink()
        
        # Refresh the view after deletion
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
        
            
    #constrain  
    @api.constrains('student_count')
    def _check_date(self):
        domain = [('id', '=', self.id)]
        session = self.search(domain)         
        if session.student_count < session.reg_student_count:
            raise ValidationError(('Max count can not be less than register count'))


    #confirm
    def get_subject(self):
        for faculty_id in self.faculty_ids[:1] :
            return 'Lecture of ' + faculty_id.name + \
                ' for ' + self.subject_id.name + ' is ' + self.state        
            
            
    def write(self, values):
        if 'timing_id' in values or 'to_timing_id' in values or 'type' in values or 'facility_id' in values or 'faculty_ids' in values:
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            if 'timing_id' in values:
                timing_id = values['timing_id']
            else:
                timing_id = self.timing_id.id
            if 'to_timing_id' in values:
                to_timing_id = values['to_timing_id']
            else:
                to_timing_id = self.to_timing_id.id
    
            if 'type' in values:
                type = values['type']
            else:
                type = self.type
            if 'timing_id' in values or 'to_timing_id' in values or 'facility_id' in values:
                if 'facility_id' in values:
                    facility_id = values['facility_id']
                else:
                    facility_id = self.facility_id.id
                #Check if facility is available at this time
                other_sessions = self.env['op.session'].search([
                    ('facility_id', '=', facility_id),
                    ('id', '!=', self.id),
                    ('id', 'not in', self.similar_session_ids.ids),
                    ('type', '=', type),
                    ('session_date', '>=', str(self.batch_id.default_week_start)),
                    '|', '&',
                    ('timing_id', '<=', timing_id),
                    ('to_timing_id', '>=', to_timing_id),
                    '|', '&',
                    ('timing_id', '>=', timing_id),
                    ('to_timing_id', '<=', to_timing_id),
                    '|', '&',
                    ('timing_id', '<=', timing_id),
                    ('to_timing_id', '>', timing_id),
                    '&',
                    ('timing_id', '<', to_timing_id),
                    ('to_timing_id', '>=', to_timing_id),
                ])
                if other_sessions:
                    raise ValidationError("Facility used in this time")
    
            if 'timing_id' in values or 'to_timing_id' in values or 'faculty_ids' in values:
                if 'faculty_ids' in values:
                    compare_faculty_ids = []
                    faculty_ids = self.faculty_ids.ids
                    for val in values['faculty_ids']:
                        if val[0] == 3:
                            faculty_ids.remove(val[1])
                        if val[0] == 4:
                            faculty_ids.append(val[1])
                            compare_faculty_ids.append(val[1])
                else:
                    faculty_ids = self.faculty_ids.ids
                print("self.faculty_ids.ids", self.faculty_ids.ids)
                print("faculty_ids", faculty_ids)
                other_sessions_f = self.env['op.session'].search([
                    ('faculty_ids', 'in', compare_faculty_ids),
                    ('id', '!=', self.id),
                    ('id', 'not in', self.similar_session_ids.ids),
                    ('type', '=', type),
                    ('session_date', '>=', str(self.batch_id.default_week_start)),
                    '|', '&',
                    ('timing_id', '<=', timing_id),
                    ('to_timing_id', '>=', to_timing_id),
                    '|', '&',
                    ('timing_id', '>=', timing_id),
                    ('to_timing_id', '<=', to_timing_id),
                    '|', '&',
                    ('timing_id', '<=', timing_id),
                    ('to_timing_id', '>', timing_id),
                    '&',
                    ('timing_id', '<', to_timing_id),
                    ('to_timing_id', '>=', to_timing_id),
                ])
                print("other_sessions_f", other_sessions_f)
                if other_sessions_f:
                    raise ValidationError("Faculty is busy in this time")
    
            sessions = self.env['op.session'].search([
                ('id', '!=', self.id),
                ('subject_id', '=', self.subject_id.id),
                ('course_id', '=', self.course_id.id),
                ('batch_id', '=', self.batch_id.id),
                ('timing_id', '=', self.timing_id.id),
                ('to_timing_id', '=', self.to_timing_id.id),
                ('classroom_id', '=', self.classroom_id.id),
                ('sub_classroom', '=', self.sub_classroom),
                ('facility_id', '=', self.facility_id.id),
                ('session_type', '=', self.session_type),
                ('type', '=', self.type),
            ])
    
        if self.similarity and 'similarity' not in values:
            batches = self.env['op.batch'].sudo().search([
                ('academic_year', '=', self.batch_id.academic_year.id),
                ('semester', '=', self.batch_id.semester.id),
                ('intern_batch', '=', False)
            ])
            sessions = self.env['op.session'].search([
                ('id', '!=', self.id),
                ('batch_id', 'in', batches.ids),
                ('timing_id', '=', self.timing_id.id),
                ('to_timing_id', '=', self.to_timing_id.id),
                ('classroom_id', '=', self.classroom_id.id),
                ('sub_classroom', '=', self.sub_classroom),
                ('facility_id', '=', self.facility_id.id),
                ('session_type', '=', self.session_type),
                ('type', '=', self.type),
                ('similarity', '=', True),
            ])
        else:
            sessions = self.env['op.session'].search([
                ('id', '!=', self.id),
                ('subject_id', '=', self.subject_id.id),
                ('course_id', '=', self.course_id.id),
                ('batch_id', '=', self.batch_id.id),
                ('timing_id', '=', self.timing_id.id),
                ('to_timing_id', '=', self.to_timing_id.id),
                ('classroom_id', '=', self.classroom_id.id),
                ('sub_classroom', '=', self.sub_classroom),
                ('facility_id', '=', self.facility_id.id),
                ('session_type', '=', self.session_type),
                ('type', '=', self.type),
            ])
        
        res = super(OpSession, self).write(values)
        
        # Update faculty_ids for child sessions
        if 'faculty_ids' in values:
            faculty_sessions = self.child_session
            if faculty_sessions:
                for faculty_session in faculty_sessions:
                    faculty_session.write({'faculty_ids': [(6, 0, faculty_ids)]})  # Replace all faculty_ids
        
        for session in sessions:
            if 'timing_id' in values:
                timing_id = values['timing_id']
            else:
                timing_id = self.timing_id.id
            if 'to_timing_id' in values:
                to_timing_id = values['to_timing_id']
            else:
                to_timing_id = self.to_timing_id.id
            time_from = self.timing_id.name.split(":")
            time_to = self.to_timing_id.name.split(":")
            #comment this to check generate timetable
            # values["session_date"] =session.start_datetime
            super(OpSession, session).write(values)
        
        if 'to_timing_id' in values:
            if self.to_timing_id < self.timing_id:
                raise ValidationError("End time must be more than start time")
    
        if 'facility_id' in values:
            self.student_count = self.facility_id.study_capacity
    
        if 'student_count' in values:
            if self.student_count > self.facility_id.study_capacity:
                raise ValidationError("student count must be less than facility capacity")
        return res
    

class HUESimilarityWizard(models.TransientModel):
    _name = 'hue.similarity.wizard'
    _description = 'hue.similarity.wizard'


    course_id = fields.Many2one('op.course', 'Course', required=True)
    subject_id = fields.Many2one('op.subject', 'Subject', required=True, domain="[('id', 'in', suitable_subject_ids)]")
    batch_id = fields.Many2one('op.batch', domain="[('course_id', '=', course_id)]" )
    suitable_subject_ids = fields.Many2many('op.subject', compute='_compute_suitable_subject_ids') #to add domain to subjects
    session_id = fields.Many2one('op.session', string='Session')
    all_subject = fields.Boolean(string='All Subject Sessions', default=False)


    @api.model
    def default_get(self, fields):
        res = super(HUESimilarityWizard, self).default_get(fields)
        active_id = self.env.context.get('active_id', False)
        session = self.env['op.session'].browse(active_id)
        res.update({
            'session_id': session.id,
        })
        return res


    @api.onchange('course_id')
    def _compute_suitable_subject_ids(self):
        subject_list = []
        if self.course_id:
            course_subjects = self.env['op.batch'].search(
                [('course_id', '=', self.course_id.id)])
            print("course_subjects", course_subjects)
            if course_subjects:
                for course_subject in course_subjects.subject_registration_ids:
                    subject_list.append(course_subject.subject_id.id)
        self.suitable_subject_ids = subject_list



    def similar_session(self):
        line = self.session_id
        if self.batch_id :
            print("1111111111111111111111111")
            batch_id = self.batch_id
            similar_classroom = self.group_id
        else :
            print("2222222222222222222222222222222222")
            batch_id = self.env['op.batch'].search(
                [('course_id', '=', self.course_id.id), ('start_date', '=', self.session_id.batch_id.start_date),
                 ('end_date', '=', self.session_id.batch_id.end_date),
                 ('academic_year', '=', self.session_id.batch_id.academic_year.id),
                 ('semester', '=', self.session_id.batch_id.semester.id),('intern_batch', '=', False)])
            print("batch_id", batch_id)
            similar_classroom = line.classroom_id
            
        if batch_id:
            start_date = datetime.datetime.strptime(str(batch_id.start_date), '%Y-%m-%d')
            end_date = datetime.datetime.strptime(str(batch_id.end_date), '%Y-%m-%d')
            if self.all_subject:
                sessions = self.env['op.session'].search([
                    ('subject_id', '=', line.subject_id.id),
                    ('course_id', '=', line.course_id.id),
                    ('batch_id', '=', line.batch_id.id),
                ])
            else:
                sessions = self.env['op.session'].search([
                    ('subject_id', '=', line.subject_id.id),
                    ('course_id', '=', line.course_id.id),
                    ('batch_id', '=', line.batch_id.id),
                    ('timing_id', '=', line.timing_id.id),
                    ('to_timing_id', '=', line.to_timing_id.id),
                    ('classroom_id', '=', line.classroom_id.id),
                    ('facility_id', '=', line.facility_id.id),
                    ('sub_classroom', '=', line.sub_classroom),
                    ('session_type', '=', line.session_type),
                    # ('start_datetime', '=', curr_start_date.strftime("%Y-%m-%d %H:%M:%S")),
                    # ('end_datetime', '=', curr_end_date.strftime("%Y-%m-%d %H:%M:%S")),
                    ('type', '=', line.type),
                    # ('student_count', '=', line.student_count),
                ])
            for line in sessions:

                already = self.env['op.session'].search([
                    ('subject_id', '=', self.subject_id.id),
                    ('course_id', '=', self.course_id.id),
                    ('batch_id', '=', batch_id.id),
                    ('timing_id', '=', line.timing_id.id),
                    ('to_timing_id', '=', line.to_timing_id.id),
                    ('classroom_id', '=', line.classroom_id.id),
                    ('facility_id', '=', line.facility_id.id),
                    ('sub_classroom', '=', line.sub_classroom),
                    ('session_type', '=', line.session_type),
                    # ('start_datetime', '=', curr_start_date.strftime("%Y-%m-%d %H:%M:%S")),
                    # ('end_datetime', '=', curr_end_date.strftime("%Y-%m-%d %H:%M:%S")),
                    ('start_datetime', '=', line.start_datetime),
                    ('end_datetime', '=', line.end_datetime),
                    ('type', '=', line.type),
                    # ('student_count', '=', line.student_count),
                ])
                if not already:
                    # raise ValidationError("Not Created")
                    new_sesion = self.env['op.session'].create({
                        'faculty_id': line.faculty_id.id,
                        'faculty_ids': [(6, 0, line.faculty_ids.ids)],
                        'q_faculty_ids': [(6, 0, line.q_faculty_ids.ids)],
                        'subject_id': self.subject_id.id,
                        'course_id': self.course_id.id,
                        'batch_id': batch_id.id,
                        'timing_id': line.timing_id.id,
                        'to_timing_id': line.to_timing_id.id,
                        'classroom_id': similar_classroom.id,
                        'facility_id': line.facility_id.id,
                        'sub_classroom': line.sub_classroom,
                        'session_type': line.session_type,
                        'start_datetime':
                            line.start_datetime,
                        'end_datetime':
                            line.end_datetime,
                        'type': line.type,
                        'student_count': line.student_count,
                        'similarity': True,
                        'session_date':line.session_date,
                        'similar_session_ids' : [(6, 0, line.ids)],
                    })

                    if self.course_id.faculty_id.id == 12 :
                        if new_sesion :
                            classroom = self.env['op.classroom'].search(
                                        [('course_id', '=', self.course_id.id),
                                         ('batch_id', '=', self.batch_id.id),('id', '=', self.group_id.id)]).ids
                            teams = self.env['student.study.groups'].sudo().search(
                                [('study_group_id', 'in', classroom)])
                            student_ids = teams.mapped('student_id').ids
                            new_sesion.write({
                                'student_ids': [(6, 0, student_ids)],
                                })
                elif line.faculty_ids:
                    raise ValidationError("Already Exists")
                    already.write({
                        'faculty_ids': [(6, 0, line.faculty_ids.ids)],
                        'q_faculty_ids': [(6, 0, line.q_faculty_ids.ids)],
                        'similarity': True,
                    })
                line.write({
                    'similarity': True,
                })
            return {'type': 'ir.actions.act_window_close'}
        else:
            raise ValidationError("Batch is not found!")