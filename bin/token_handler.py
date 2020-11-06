import auth_handler
import json
import splunk.clilib.cli_common as cli_common
import logger
logger = logger.setup_logger("app_catchpoint.log")

# Pulls performance/alerts data from Catchpoint, updates token if expired and retries the performance/alerts data pull with the new token.
def get_refresh_token(test_id, consumer_key, consumer_secret, setup_input, data_retrieval_type, client_identifier, service, requests_handler_object):
    the_catchpoint_object = auth_handler.Catchpoint()
    credential = build_credential_dictionary(consumer_key, consumer_secret,  test_id, data_retrieval_type)
    the_catchpoint_object._develop_URIs(credential)

    try:
        data = requests_handler_object.make_verified_requests_with(setup_input['access_token'], the_catchpoint_object.endpoint_uri)
        if data:
            return data

    except Exception as e:
        """overview: token is no longer valid, reauthortize."""
        the_catchpoint_object._authorize(credential)

        expires = the_catchpoint_object._prepare_expire()
        setup_input = cli_common.getConfStanza("catchpoint", "catchpoint_account")
        catchpoint_conf = service.confs.__getitem__('catchpoint').__getitem__(client_identifier)
        catchpoint_conf.update(**{'access_token' : '{0}'.format(the_catchpoint_object._token) })
        catchpoint_conf.refresh()
        catchpoint_conf.update(**{'expires_in' : '{0}'.format(expires) })
        catchpoint_conf.refresh()
        data = requests_handler_object.make_verified_requests_with(the_catchpoint_object._token, the_catchpoint_object.endpoint_uri)

        if data:
            setup_input = cli_common.getConfStanza("catchpoint", client_identifier)
            setup_input['access_token'] = the_catchpoint_object._token
            return data
        else:
            logger.exception("ERROR! Unable to obtain an access_token. Failing Silently...")

# Constructs dictionary required to make request to Catchpoint API. 
def build_credential_dictionary(consumer_key, consumer_secret, test_id, data_retrieval_type):
    creds = {
        'client_id': consumer_key,
        'client_secret': consumer_secret,
        'refresh_token': 'None',
        'api_URIs': [
            {'token_uri': {
                'hostname_prefix': 'io.',
                'path_template_arg1': 'ui/',
                'path_template_arg2': 'token'
            }}
        ]
    }
    if data_retrieval_type == 'alerts':
        creds['api_URIs'].append( {'endpoint_uri':{ 'path_template_arg2' : '{0}/alerts' .format('v1')}} ) 
    else:
        creds['api_URIs'].append( {'endpoint_uri':{ 'path_template_arg2' : '{0}/performance/raw?tests={1}' .format('v1', test_id)}} ) 
    # force URIs developed to have the same beginning path
    creds['api_URIs'][1]['endpoint_uri'].update( { 'hostname_prefix' : creds['api_URIs'][0]['token_uri']['hostname_prefix'] } )  
    creds['api_URIs'][1]['endpoint_uri'].update( { 'path_template_arg1' : creds['api_URIs'][0]['token_uri']['path_template_arg1'] } )  
    return creds