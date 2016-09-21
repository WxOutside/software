
global couchdb_port
global couchdb_baseurl

couchdb_port=':5984'
couchdb_baseurl='http://localhost' + couchdb_port

couchdb_headers='{"content-type": "application/json"}'

wxadvisory_domain='https://wxadvisory.com'

wxoutside_email_server='mail.wxoutside.tools'
wxoutside_email_port=587

#### Customise the values in the next 3 lines ####
wxoutside_sensor_name=[sensor_name]
wxoutside_sensor_email=[email_address_goes_here]
wxoutside_sensor_password=[email password]
