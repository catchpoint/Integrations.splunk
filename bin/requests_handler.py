import auth_handler, parse
import token_handler
class Request(object):

    def __init__(
            self
    ):
        self.credentials = None

    def retrieve_rd_wrapper(self, consumer_key, consumer_secret, test_id):

        creds_original = {
            'client_id': consumer_key,
            'client_secret': consumer_secret,
            'refresh_token': 'None',
            'api_URIs': [
                {'token_uri': {
                    'hostname_prefix': 'io.',
                    'path_template_arg1': 'ui/',
                    'path_template_arg2': 'token'
                }},
                {'endpoint_uri': {
                    'path_template_arg2': '{0}/performance/raw?tests={1}' .format('v1', test_id)
                }}
            ]
        }

        creds = creds_original

        # force URIs developed to have the same beginning path
        creds['api_URIs'][1]['endpoint_uri']['hostname_prefix'] = creds['api_URIs'][0]['token_uri']['hostname_prefix']
        creds['api_URIs'][1]['endpoint_uri']['path_template_arg1'] = creds['api_URIs'][0]['token_uri']['path_template_arg1']
        raw_data = auth_handler.Catchpoint()._get_raw_performance_data(creds)
        mapped = parse.search(raw_data)
        return mapped
    
    # Handles parsing Catchpoint API data. 
    def make_verified_requests_with(self, token, uri):
        the_catchpoint_object = auth_handler.Catchpoint()
        the_catchpoint_object._token = token
        raw_data  = the_catchpoint_object._make_request(uri)
        auth_handler.Catchpoint()._debug(str(raw_data))
        mapped = parse.search(auth_handler.Catchpoint().normalize_json(raw_data))
        return mapped

    # Intiates API request to pull performamce/alerts data. 
    def refresh_token(self, test_id, consumer_key, consumer_secret, setup_input, data_retrieval_type, client_identifier, service):
        return token_handler.get_refresh_token(test_id, consumer_key, consumer_secret, setup_input, data_retrieval_type, client_identifier, service, self)
