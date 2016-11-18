###############################################################################
#
# These are global variables that you probably don't need to modify
#
# Please check environment_config.py for variables that you should change
#
###############################################################################

global couchdb_port
global couchdb_baseurl

couchdb_port=':5984'
couchdb_baseurl='http://localhost' + couchdb_port
couchdb_headers='{"content-type": "application/json"}'

wxadvisory_domain='https://wxadvisory.com'
wxoutside_domain='http://beta.wxoutside.tools'

wxoutside_email_server='mail.wxoutside.tools'
wxoutside_email_port=587