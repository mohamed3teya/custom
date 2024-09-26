from odoo import models, fields
from xlrd import open_workbook
import base64

class HUEAcademicDirectionLine(models.Model):
    _name = 'hue.academic.direction.line'
    _description = 'hue.academic.direction.line'
    
    acad_dir_id = fields.Many2one('hue.academic.direction', 'Academic Advisor')#, ondelete="cascade"
    college_id = fields.Many2one('hue.faculties', 'College', related='acad_dir_id.college_id')
    faculty_id = fields.Many2one('op.faculty', 'Faculty', related='acad_dir_id.faculty_id', store=True)
    student_id = fields.Many2one('op.student', 'Student Name', required=True)
    student_code = fields.Integer(related='student_id.student_code')
    from_date = fields.Date('From Date', required=True)
    to_date = fields.Date('To Date')
    transfer_advisor_id = fields.Many2one('transferred.advisor')
    
    def write(self, values):
        if 'to_date' in values:
            to_date =values['to_date']
            if to_date :
                recId = self.env['hue.academic.direction.line'].sudo().search([('id', '=', self.id)]) 
                student_advisor= self.env['op.student'].search([('id', '=', recId.student_id.id)])
                student_advisor.write({'advisor':None })
        res = super(HUEAcademicDirectionLine, self).write(values)
        
class HUEAcademicDirection(models.Model):
    _name = 'hue.academic.direction'
    _description = 'hue.academic.direction'
    
    college_id = fields.Many2one('hue.faculties', 'College', required=False)
    faculty_id = fields.Many2one('op.faculty', 'Faculty', required=True)
    student_ids = fields.One2many('hue.academic.direction.line', 'acad_dir_id', 'Students')
    attachment_ids = fields.Many2many('ir.attachment', 'class_ir_attachments_rel', 'class_id', 'attachment_id', 'Attachments')

    _sql_constraints = [
        ('faculty_id_unique', 'unique(faculty_id)', 'Faculty already exists!')
    ]

    def readXls(self, att):
        xml = base64.b64decode(att.datas)
        xml_filename = att.datas_fname
        wb = open_workbook(file_contents=xml)

        for s in wb.sheets():
            all_data = []
            for row in range(s.nrows):
                data_row = []
                for col in range(s.ncols):
                    value = (s.cell(row, col).value)
                    data_row.append(value)
                all_data.append(data_row)
        return all_data

    def importXls(self):
        print("dddddddddddddddddddddddddd")
        print("dddddddddddddddddddddddddd")
        print("dddddddddddddddddddddddddd")
        print("dddddddddddddddddddddddddd")
        for att in self.attachment_ids:
            data = self.readXls(att)
            # print(data)
            i = 0
            for row in data:
                i+=1
                print(row)
                fid = int(row[4])
                scode = int(row[2])
                fdate = row[3]
                college = int(row[5])
                if isinstance(fdate, str):
                    fdate_arr = fdate.split('/')
                    if len(fdate_arr)<2:
                        stdate = fdate
                        # raise ValidationError(_('Date error '+fdate+' in line '+str(i)))
                    else:
                        stdate = fdate_arr[2] + '-' + fdate_arr[1] + '-' + fdate_arr[0]
                else:
                    stdate = str(int(row[7]))+'-'+str(int(row[6]))+'-'+str(int(row[5]))
                # stdate = datetime.datetime.fromtimestamp(int(row[3]))
                # print(fid)
                # print(scode)
                # print(fdate)
                faculty = self.env['op.faculty'].sudo().search([('id_number', '=', fid)], limit=1)
                if faculty:
                    academic_direction = self.env['hue.academic.direction'].sudo().search([('faculty_id', '=', faculty.id)], limit=1)
                    if not academic_direction:
                        academic_direction = self.env['hue.academic.direction'].sudo().create({'faculty_id': faculty.id, 'college_id': college})
                    student = self.env['op.student'].sudo().search([('student_code', '=', scode)], limit=1)
                    if student:
                        academic_direction_line = academic_direction.student_ids.sudo().search([('acad_dir_id', '=', academic_direction.id), ('student_id', '=', student.id), ('from_date', '=', stdate)], limit=1)
                        if not academic_direction_line:
                            academic_direction_line = self.env['hue.academic.direction.line'].sudo().create({'acad_dir_id': academic_direction.id, 'student_id': student.id, 'from_date': stdate, 'college_id': college})


