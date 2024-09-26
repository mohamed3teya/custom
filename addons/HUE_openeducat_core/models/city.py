from odoo import models, fields, api, _
import urllib.request as urllib2
import ssl
import json


class City(models.Model):
    _name = 'hue.cities'
    _description = 'list of cities arabic and english names'
    
    name = fields.Char()
    d_id = fields.Char(string="External ID", readonly=False)
    

    @api.model
    def get_hue_cities_fun(self):
        hue_city = self.env['hue.cities']
        url = "https://sys.mc.edu.eg/WebServiceMCI?index=GetCities&userName=myd777myd&password=lo@stmm"
        req = urllib2.Request(url, headers={ 'X-Mashape-Key': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX' })
        gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)  # Only for gangstars
        webURL = urllib2.urlopen(req, context=gcontext)
        data = webURL.read()
        encoding = webURL.info().get_content_charset('utf-8')
        data = json.loads(data.decode(encoding))
        index = 0
        for  val in data['data']:
            d_id = data['data'][index]['ID']
            city = hue_city.search([('d_id','=',d_id)],limit=1)
            if not city:
                hue_city.create({'name':data['data'][index]['Name'],'d_id':data['data'][index]['ID']})
            index += 1