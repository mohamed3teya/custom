from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from ldap3 import Server, Connection, ALL, NTLM, ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES, AUTO_BIND_NO_TLS, SUBTREE

##### Ldap Directory MG 
class LDAPDirectory(models.Model):
    _name = "ldap.directory"
    _description = "LDAP Directory"
    
    name = fields.Char('G/O Name',help="Group or Organizational Unit Directory.")
    dn = fields.Char('LDAP DN')
    obj_id = fields.Char('Object ID')
    parent_id = fields.Many2one('ldap.directory', string='Parent Directory', index=True)

    ##### Get Ldap Sub tree  MG 
    def _get_ldap_child_data(self,conn,ldap_base,parent_id):
        conn.search(format(ldap_base),search_filter='(|(objectClass=group)(objectclass=organizationalUnit))',search_scope=1,attributes=['cn','name','distinguishedName','objectGUID'])
        for entry in sorted(conn.entries):
            print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            print(entry.name)
            obj_id = self.env['ldap.directory'].search([('obj_id','=',entry.objectGUID)])
            if not obj_id:
                obj_id = self.env['ldap.directory'].create({'name': entry.name,'parent_id':parent_id,'dn': entry.distinguishedName,'obj_id': entry.objectGUID})
            else:
                print("else")
                print(obj_id)
                obj_id.write({'name': entry.name,'dn': entry.distinguishedName,'parent_id':parent_id})
            self._get_ldap_child_data(conn,entry.distinguishedName,obj_id.id)
        conn.bind()
        

    ##### LDAP Connect  MG
    def _ldap_connect(self):    
        get_param = self.env['ir.config_parameter'].sudo().get_param
        ldap_server = get_param('ldap_server')
        ldap_server_port = get_param('ldap_server_port', default='389')
        user_name = get_param('ldap_binddn')
        password = get_param('ldap_password')
        ldap_base = get_param('ldap_base') #'OU=MC  Schools,DC=mc,DC=edu,DC=eg'#get_param('ldap_base')
        server = Server(ldap_server, port=int(ldap_server_port),get_info=ALL)
        conn = Connection(server, user='{}\\{}'.format(ldap_base, user_name), password=password, authentication=NTLM,
                          auto_bind=True)
        return [conn,ldap_base]
    
    ##### Get Ldap OU tree  MG     
    @api.model
    def _sync_ldap(self):
        ldap_conn = self._ldap_connect()
        conn = ldap_conn[0]
        ldap_base = ldap_conn[1]
        conn.search(format(ldap_base),search_filter='(|(objectClass=group)(objectclass=organizationalUnit))',search_scope=1,attributes=['cn','name','distinguishedName','objectGUID'])
        for entry in sorted(conn.entries):
            print("#######################")
            print(entry.name)
            obj_id = self.env['ldap.directory'].search([('obj_id','=',entry.objectGUID)])
            if not obj_id:
                obj_id = self.env['ldap.directory'].create({'name': entry.name,'dn': entry.distinguishedName,'obj_id': entry.objectGUID})
            else:
                obj_id.write({'name': entry.name,'dn': entry.distinguishedName})
            self._get_ldap_child_data(conn,entry.distinguishedName,obj_id.id)
        conn.bind()
    
    @api.model
    def _sync_ldap_department(self):
        print('21111111111222222222223333333333')
        ldap_conn = self.env["ldap.directory"]._ldap_connect()
        conn = ldap_conn[0]
        ldap_base = ldap_conn[1]
        employees = self.env['hr.employee'].search([])
        for rec in employees:
            try:
                if rec.user_id.oauth_uid:
                    username = (rec.user_id.oauth_uid.split('@'))[0]
                    print(username)
                else:
                    username = 'False'
                search_dn = conn.search(format(ldap_base),search_filter= "(sAMAccountName="+username+")", search_scope=SUBTREE, attributes=['distinguishedName'])
                if search_dn:
                    userdn = str(conn.response[0]['dn'])
                    conn.modify(userdn, {'department': [('MODIFY_REPLACE', rec.department_id.name)]})
            except KeyError:
                pass
            
class StudentIdapDir(models.Model):
    _name = 'student.ldap.directory'
    _description = 'student ldap directory'

    dn = fields.Char(string='LDAP DN')
    name = fields.Char(string="G/O Name")
    obj_id = fields.Char(string='Object ID')
    parent_id = fields.Many2one('student.ldap.directory', string='Parent Directory')