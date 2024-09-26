from odoo import models, fields, api, _
import urllib.request as urllib2
import ssl
import json


class Certificate(models.Model):
    _name = 'hue.certificates'
    _description = 'The pre university certificate'

    name = fields.Char()
    certificate_active = fields.Boolean(string="Certificate Active")
    enroll_code = fields.Char(string="Enroll Code")
    d_id = fields.Char(string="External ID", readonly=True)
    certtype = fields.Selection([('1','مصرية'),('2','عربية'),('3','أجنبية')], string='Certificate Type')
    
    
    @api.model
    def get_hue_certificates_fun(self):
        hue_cer = self.env['hue.certificates']
        url = "https://sys.mc.edu.eg/WebServiceMCI?index=GetHighSchoolCertificates&userName=myd777myd&password=lo@stmm"
        req = urllib2.Request(url, headers={ 'X-Mashape-Key': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX' })
        gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)  # Only for gangstars
        webURL = urllib2.urlopen(req, context=gcontext)
        data = webURL.read()
        encoding = webURL.info().get_content_charset('utf-8')
        data = json.loads(data.decode(encoding))
        index = 0
        for  val in data['data']:
            d_id = data['data'][index]['ID']
            cer = hue_cer.search([('d_id','=',d_id)],limit=1)
            if not cer:
                hue_cer.create({'name':data['data'][index]['Name'],'d_id':data['data'][index]['ID']})
            index += 1