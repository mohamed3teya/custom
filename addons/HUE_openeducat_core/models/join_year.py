from odoo import models, fields, api, _
import urllib.request as urllib2
import ssl
import json
   
   
class HueJoiningYears(models.Model):
	_name = 'hue.joining.years'
	_description = 'Join year'
	
	name = fields.Char()
	active = fields.Boolean(string="Active")	
	d_id = fields.Char(string="External ID")
	

	@api.model
	def get_hue_Join_year_fun(self):
		hue_joinyear = self.env['hue.joining.years']
		url = "https://sys.mc.edu.eg/WebServiceMCI?index=GetJoinYears&userName=myd777myd&password=lo@stmm"
		req = urllib2.Request(url, headers={ 'X-Mashape-Key': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX' })
		gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)  # Only for gangstars
		webURL = urllib2.urlopen(req, context=gcontext)
		data = webURL.read()
		encoding = webURL.info().get_content_charset('utf-8')
		data = json.loads(data.decode(encoding))
		
		index = 0
		for  val in data['data']:
			d_id = data['data'][index]['YearID']
			joinyear = hue_joinyear.search([('d_id','=',d_id)],limit=1)
			if not joinyear:
				hue_joinyear.create({'name':data['data'][index]['YearName'],'d_id':data['data'][index]['YearID']})
			index += 1