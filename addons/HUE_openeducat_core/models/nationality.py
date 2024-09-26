from odoo import models, fields, fields, api, _
import urllib.request as urllib2
import ssl
import json


class Nationality(models.Model):
    _name = 'hue.nationalities'
    _description = 'students nationalities'
    
    name = fields.Char()
    en_name = fields.Char(string='English Name')
    d_id = fields.Char(string="External ID",readonly=True)
    foreign_nationality = fields.Boolean(string="Foreign Nationality",default=True)


    @api.model
    def get_nationalities_fun(self):
        hue_nat = self.env['hue.nationalities']
        url = "https://sys.mc.edu.eg/WebServiceMCI?index=GetNationalities&userName=myd777myd&password=lo@stmm"
        req = urllib2.Request(url, headers={ 'X-Mashape-Key': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX' })
        gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)  # Only for gangstars
        webURL = urllib2.urlopen(req, context=gcontext)
        data = webURL.read()
        encoding = webURL.info().get_content_charset('utf-8')
        print("encoding", encoding)
        data = json.loads(data.decode(encoding))
        index = 0
        for  val in data['data']:
            d_id = data['data'][index]['ID']
            nat = hue_nat.search([('d_id','=',d_id)],limit=1)
            if not nat:
                hue_nat.create({'name':data['data'][index]['Name'],'d_id':data['data'][index]['ID']})
            index += 1