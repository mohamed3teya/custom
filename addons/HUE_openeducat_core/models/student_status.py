from odoo import models, fields, api, _
import urllib.request as urllib2
import ssl
import json


class StudentDatatStatus(models.Model):
    _name = 'hue.std.data.status'
    _description = 'Registered students status'
    
    name = fields.Char()
    en_name = fields.Char(string='English Name')
    d_id = fields.Char(string='External ID')
    active_invoice = fields.Boolean(string="Active Invoice")
    
    
    @api.model
    def get_hue_student_status_fun(self):
        stu_status = self.env['hue.std.data.status']
        url = "https://sys.mc.edu.eg/WebServiceMCI?index=GetStudentStatuses&userName=myd777myd&password=lo@stmm"
        req = urllib2.Request(url, headers={ 'X-Mashape-Key': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX' })
        gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)  # Only for gangstars
        webURL = urllib2.urlopen(req, context=gcontext)
        data = webURL.read()
        encoding = webURL.info().get_content_charset('utf-8')
        data = json.loads(data.decode(encoding))
        index = 0
        for  val in data['data']:
            d_id = data['data'][index]['ID']
            status = stu_status.search([('d_id','=',d_id)],limit=1)
            if not status:
                stu_status.create({'name':data['data'][index]['Name'],'d_id':data['data'][index]['ID']})
            index += 1
    

class StudentStatus(models.Model):
    _name = 'hue.student.status'
    _description = 'hue.student.status'
    
    academic_id = fields.Many2one('op.academic.term', string='Academic Year')
    academic_term_id = fields.Many2one('op.academic.term', string='Term')
    assigned = fields.Boolean()
    invoice_id = fields.Integer(string="Invoice")
    one_time = fields.Boolean(string="One Time")
    paid = fields.Boolean()
    student_id = fields.Many2one('op.student', string='Student')
    
    def action_open_related_document(self):
        self.ensure_one()
        print(self.invoice_id)
        return {
            'type': 'ir.actions.act_window',
            'name': 'ddd',
            'res_model': 'account.move',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [[False, 'form']],
            'res_id': self.id,
        }