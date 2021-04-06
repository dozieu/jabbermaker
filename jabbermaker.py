from lxml import etree
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client, Settings, Plugin
from zeep.transports import Transport
#from zeep.cache import SqliteCache
from zeep.exceptions import Fault
import sys
import urllib3
import getpass
import pyinputplus as pyip


print('#' * 42)
print(('#' * 3) + '    -- Jabber Profile Creator --    ' + ('#' * 3))
print(('#' * 42) + '\n')


CUCM_ADDRESS = input('Enter Server Address: ')
USERNAME = input('usersname: ')
PASSWORD = getpass.getpass()


DEFAULT_PT = 'Default_PT'


INTERNAL_CSS = 'Internal-CSS'
EXTERNAL_CSS = 'International-CSS'

# add to dictionary if more sites
devicepools = {'site_a':'devicepool_a', 
               'site_b':'devicepool_b'}

searchspace = {'site_a': 'css_a', 
                'site_b': 'css_b'}


model = {'SEP': 'Cisco 8811', 
         'BOT' : 'Cisco Dual Mode for Android', 
         'TCT':'Cisco Dual Mode for iPhone',
         'TAB':'Cisco Jabber for Tablet',
         'CSF': 'Cisco Unified Client Services Framework'}

sec_profiles = {'TAB':'Cisco Jabber for Tablet - Standard SIP Non-Secure Profile',
                'SEP':'Universal Device Template - Model-independent Security Profile',
                'BOT':'Cisco Dual Mode for Android - Standard SIP Non-Secure Profile',
                'CSF':'Cisco Unified Client Services Framework - Standard SIP Non-Secure Profile',
                'TCT': 'Cisco Dual Mode for iPhone - Standard SIP Non-Secure Profile'}


def get_pt(defaultpt):
	dn_pt = input(f'Leave blank for default: "{defaultpt}" or Enter Partition: ')
	if dn_pt == '':
		dn_pt = defaultpt
	return dn_pt


def make_devicename(dname, devicetype='CSF'):
    #Generates device name from dname and phone type    
    for i in dname:
        if i.isalnum() == False:
            dname = dname.replace(i, '')
    dev_name = (devicetype + ((dname.upper())))[:15]
    return (dev_name)


# Change to true to enable output of request/response headers and XML
DEBUG = False

# The WSDL is a local file in the working directory, see README
WSDL_FILE = 'schema/AXLAPI.wsdl'

# This class lets you view the incoming and outgoing http headers and XML

class MyLoggingPlugin( Plugin ):

    def egress( self, envelope, http_headers, operation, binding_options ):

        # Format the request body as pretty printed XML
        xml = etree.tostring( envelope, pretty_print = True, encoding = 'unicode')

        print( f'\nRequest\n-------\nHeaders:\n{http_headers}\n\nBody:\n{xml}' )

    def ingress( self, envelope, http_headers, operation ):

        # Format the response body as pretty printed XML
        xml = etree.tostring( envelope, pretty_print = True, encoding = 'unicode')

        print( f'\nResponse\n-------\nHeaders:\n{http_headers}\n\nBody:\n{xml}' )

# The first step is to create a SOAP client session
session = Session()

# We avoid certificate verification by default
# And disable insecure request warnings to keep the output clear
session.verify = False
urllib3.disable_warnings( urllib3.exceptions.InsecureRequestWarning )

# To enabled SSL cert checking (recommended for production)
# place the CUCM Tomcat cert .pem file in the root of the project
# and uncomment the line below

# session.verify = 'changeme.pem'

# Add Basic Auth credentials
session.auth = HTTPBasicAuth( USERNAME, PASSWORD )

# Create a Zeep transport and set a reasonable timeout value
transport = Transport( session = session, timeout = 10 )

# strict=False is not always necessary, but it allows zeep to parse imperfect XML
settings = Settings( strict = False, xml_huge_tree = True )

# If debug output is requested, add the MyLoggingPlugin callback
plugin = [ MyLoggingPlugin() ] if DEBUG else [ ]

# Create the Zeep client with the specified settings
client = Client( WSDL_FILE, settings = settings, transport = transport,
        plugins = plugin )

# Create the Zeep service binding to AXL at the specified CUCM
service = client.create_service( '{http://www.cisco.com/AXLAPIService/}AXLAPIBinding',
                                f'https://{CUCM_ADDRESS}:8443/axl/' )


# ------------------------------------------------------------------------------------------------


while True:

	#Getting line and user information
	proceed = input('Press "Enter" to continue or Press "3" to Quit: ')
	if proceed == '3':
		break

	print(('=' * 42) + '\n')
	addDN = pyip.inputYesNo('Do want to add a new DN? [Y or N]:')

	

	if addDN == 'yes':
	    dn_pattern = input('Enter new Directory Number: ')
	    dn_partition = get_pt(DEFAULT_PT)
	    print(f'Using Partition {dn_partition}')
	    dn_description = input ('Enter Description: ')
	if addDN == 'no':
	    dn_pattern = input('Enter existing Directory Number: ')
	    dn_partition = get_pt(DEFAULT_PT)
	    print(f'Using Partition {dn_partition}')
	    dn_description = ''

	userid = input('Enter phone owner UserID: ')
	devicename = input('\nEnter device name, (leave blank to use UserID): ')
	if devicename == '':
		devicename = userid


	print(('=' * 42) + '\n')
	displayname = input('Enter line Display name: ')
	linelabel = input('Enter line label: ')    
	alertingname = input('Enter line Alerting name: ')

	print(('=' * 42) + '\n')
	location =  pyip.inputMenu(['For Site_A','For Site_B'], numbered=True)
	phonemodel = pyip.inputMenu(['CSF', 'Iphone', 'Android','Tablet'], numbered=True)

	print('Creating '+ phonemodel + ' Jabber for location ' + location +'\n')

	# Setting device pool, css and location
	# add another 'if' block if you more sites
	if location == 'For Site_A':        
	    ph_css = searchspace['site_a']
	    ph_devicepool = devicepools['site_a']
	if location == 'For Site_B':        
	    ph_css = searchspace['site_b']
	    ph_devicepool = devicepools['site_b']


	# Setting model and security profile
	if phonemodel == 'CSF':
	    ph_model = model['CSF']
	    ph_sec_profile = sec_profiles['CSF']
	    ph_type = 'CSF'
	if phonemodel == 'Iphone':
	    ph_model = model['TCT']
	    ph_sec_profile = sec_profiles['TCT']
	    ph_type = 'TCT'
	if phonemodel == 'Android':
	    ph_model = model['BOT']
	    ph_sec_profile = sec_profiles['BOT']
	    ph_type = 'BOT'
	if phonemodel == 'Tablet':
	    ph_model = model['TAB']
	    ph_sec_profile = sec_profiles['TAB']
	    ph_type = 'TAB'


	print ('The following will be configured..')
	print ('DN = ',dn_pattern, ' PT = ', dn_partition, ' UserID = ', userid)

	proceed = pyip.inputMenu(['Submit','Restart', 'End'], numbered=True)


	# Create data to setup Line
	line_data = {
	    'pattern': dn_pattern,
	    'description': dn_description,
	    'usage': 'Device',
	    'routePartitionName': dn_partition,
	    'autoAnswer': 'Auto Answer Off',
	    'alertingName': alertingname,
	    'asciiAlertingName': alertingname,
	    'presenceGroupName': 'Standard Presence group',
	    'shareLineAppearanceCssName': EXTERNAL_CSS,  #--chg
	    'voiceMailProfileName': 'Default',
	    'networkHoldMohAudioSourceId': '2',
	    'userHoldMohAudioSourceId': '2',
	    
	    'callForwardAll': {'forwardToVoiceMail': 'false',
	                'callingSearchSpaceName': INTERNAL_CSS,
	                'secondaryCallingSearchSpaceName': INTERNAL_CSS},                                
	    
	    'callForwardBusy': {'forwardToVoiceMail': 'true',
	                        'callingSearchSpaceName': INTERNAL_CSS},
	    
	    'callForwardBusyInt': {'forwardToVoiceMail': 'true',
	                        'callingSearchSpaceName': INTERNAL_CSS},

	    'callForwardNoAnswer': {'forwardToVoiceMail': 'true',
	                        'callingSearchSpaceName': INTERNAL_CSS,
	                        'duration': 16},

	    'callForwardNoAnswerInt': {'forwardToVoiceMail': 'true',
	                        'callingSearchSpaceName': INTERNAL_CSS},

	    'callForwardNoCoverage': {'forwardToVoiceMail': 'true',
	                        'callingSearchSpaceName': INTERNAL_CSS},
	    
	    'callForwardNoCoverageInt': {'forwardToVoiceMail': 'true',
	                        'callingSearchSpaceName': INTERNAL_CSS},

	    'callForwardOnFailure': {'forwardToVoiceMail': 'true',
	                        'callingSearchSpaceName': INTERNAL_CSS},

	    'callForwardNotRegistered': {'forwardToVoiceMail': 'true',
	                        'callingSearchSpaceName': INTERNAL_CSS},

	    'callForwardNotRegisteredInt': {'forwardToVoiceMail': 'true',
	                        'callingSearchSpaceName': INTERNAL_CSS}

	        }

	# Create data to setup phone
	phonename = make_devicename(devicename,ph_type)
	phone = {
	    'name': phonename,
	    'product': ph_model,
	    'model': ph_model,
	    'class': 'Phone',
	    'protocol': 'SIP',
	    'protocolSide': 'User',
	    'callingSearchSpaceName': ph_css,
	    'description': displayname + ' Jabber',
	    'devicePoolName': ph_devicepool,
	    'commonPhoneConfigName': 'Standard Common Phone Profile',
	    #'networkHoldMohAudioSourceId': '2',
	    #'userHoldMohAudioSourceId': '2',
	    'locationName': 'Hub_None',  
	    'securityProfileName': ph_sec_profile,
	    'useTrustedRelayPoint': 'Default',
	    'builtInBridgeStatus': 'Default',
	    'sipProfileName': 'Standard SIP Profile',
	    'packetCaptureMode': 'None',
	    'certificateOperation': 'No Pending Operation',
	    'deviceMobilityMode': 'Default',
	    'ownerUserName': userid,
	    'userLocale': 'English United States',

	    'lines': {
	        'line': [
	            {
	                'index': 1,
	                'label': alertingname,
	                'display': displayname,
	                'displayAscii': displayname,
	                'dirn': {
	                    'pattern': dn_pattern,
	                    'routePartitionName': dn_partition
	                },
	                'associatedEndusers': {
	                            'enduser': [
	                                {
	                                    'userId': userid
	                                }
	                            ]
	                        },
	                
	            }
	        ]
	    }
	}


	if proceed == 'Submit':
	    if addDN == 'yes':
	        # Execute the addLine request
	        try:
	            resp = service.addLine( line_data )

	        except Fault as err:
	            print( f'Zeep error: addLine: { err }' )
	            sys.exit( 1 )

	        print( '\nadd Line.. OK:' )
	        
	    # Execute the addPhone request
	    try:
	        resp = service.addPhone( phone )

	    except Fault as err:
	        print( f'Zeep error: addPhone: { err }' )
	        sys.exit( 1 )

	    print( '\nadd Phone.. OK:' )
	    
	    # Update devices for End User
	    end_user = {'userid': userid}
	    try:
	        resp = service.getUser( **end_user )
	        #Check if user already owns devices
	        if (resp['return']['user']['associatedDevices']):
	            resp_devices =  list(resp['return']['user']['associatedDevices']['device'])
	            resp_devices.append(phonename)
	            end_user = {'userid': userid,
	                        'associatedDevices': {'device':resp_devices }}
	            resp = service.updateUser( **end_user )
	        else:
	            # Create an associated devices object
	            devices = {'device': []}
	            devices[ 'device' ].append( phonename )
	            end_user = {'userid': userid,
	                        'associatedDevices': devices}
	            resp = service.updateUser( **end_user )

	    except Fault as err:
	        print( f'Zeep error: updateUser: { err }' )
	        sys.exit( 1 )

	    print( '\nupdate User.. OK:' )
	    
	if proceed == 'End':
	    print('Ending!')
	    break
	input('Hit Enter to close.') 
	print ('Done')

