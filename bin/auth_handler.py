import sys, base64, json, requests, time, datetime
import logger
logger=logger.setup_logger("app_catchpoint.log")
class CatchpointError(Exception):
    pass


class Catchpoint(object):
    def __init__(
            self

    ):
        """
        Basic init method.

        """
        self.verbose = False 
        self.token_uri = None
        self.endpoint_uri = None
        self.host=None
        self.content_type = "application/json"
        self._auth = False
        self._token = None
        self.expires_in = None

    def _console_logger(self, msg, describe):
        """
        :param msg: "logs description and prim./user-defined objects (as json) to console"
        :return: void
        """
        if describe is "":
            relay = "default: ".ljust(35)
        else:
            relay = describe.ljust(35)

    def _debug(self, msg):
        """
        Debug output. Set self.verbose to True to enable.
        """
        if self.verbose:
            logger.info(str(msg))

    def _connection_error(self, e):
        msg = "Unable to reach {0}: {1}".format(self.host, e)
        sys.exit(msg)

    def _authorize(self, creds):
        """
        Request an auth token.

        - creds: dict with client_id and client_secret
        """

        uri = self.token_uri

        payload = {
            'refresh_token': creds['refresh_token'],
            'grant_type': 'client_credentials',
            'client_id': creds['client_id'],
            'client_secret': creds['client_secret']
        }

        try:
            r = requests.post(uri, data=payload,verify=False)
        except requests.exceptions.ConnectionError as e:
            self._connection_error(e)

        data = r.json()

        self._token = data['access_token']
        self.expires_in = data['expires_in']
        self._auth = True

    def _make_request(self, uri, params=None, data=None):
        """
        Make a request with an auth token.

        - uri: URI for the new Request object.
        - params: (optional) dict or bytes to be sent in the query string for the Request.
        - data: (optional) dict, bytes, or file-like object to send in the body of the Request.
        """
        headers = {
            'Accept': self.content_type,
            'Authorization': "Bearer " + base64.b64encode(

                self._token.encode('ascii')

            ).decode("utf-8")
        }

        try:
            r = requests.get(uri, headers=headers, params=params, data=data,verify=False)
            if r.status_code != 200:
                self._debug("The response is "+str(r.content))	
                self._debug("there was some error"+str(r))
        except requests.ConnectionError as e:
            self._debug(str(e))
            self._connection_error(e)

        try:
            r_data = r.json()
        except TypeError as e:
            return e
        return r_data

    def _expired_token_check(self, data):
        """
        Determine whether the token is expired. While this check could
        technically be performed before each request, it's easier to offload
        retry logic onto the script using this class to avoid too many
        req/min.

        - data: The json data returned from the API call.
        """
        if "Message" in data:
            if data['Message'].find("Expired token") != -1:
                self._debug("Token was expired and has been cleared, try again...")
                self._token = None
                self._auth = False

    def _prepare_expire(self):
        timestamp = datetime.datetime.now()
        valid_until = timestamp + datetime.timedelta(minutes = 30)

        datastore = '{0},{1},{2},{3},{4},{5},{6}'.format( valid_until.year, \
        valid_until.month, \
        valid_until.day, \
        valid_until.hour, \
        valid_until.minute, \
        valid_until.second, \
        valid_until.microsecond)
        return datastore

    def _get_interval(self, initE, initS):
        format = '%Y-%m-%dT%H:%M:%S.%fZ'
        end = initE
        start = initS

        end = end[0:len(end) - 3]+"{0}".format("Z")
        start = start[0:len(start) - 3]+"{0}".format("Z")

        b = time.strptime(end, format)
        a = time.strptime(start, format)
        b = time.mktime(b)
        a = time.mktime(a)

        return int((b - a))

    def _develop_URIs(self, creds):
        """
            overview: provides an abstraction layer over uri construction.
            constructs URLs from the endpoint fragments in the correct format
            for the underlying calls to the REST API.
            structure: https://{0}catchpoint.com/{1}api/{ [options: select an endpoint] }
            @args:
            {0} = hostname_prefix

            path_template = "{1}api/{options}"
            {1} =  insert a valid string BEFORE 'api/' to access valid endpoint | empty string
            [options] = insert a valid string AFTER 'api/' to access valid endpoint | CANNOT be the empty string.
        """
        """ overview: build token uri: path construction: {0}api/{1} """
        path_template = "{0}api/{1}"
        path_arg1 = creds['api_URIs'][0]['token_uri']['path_template_arg1']
        path_arg2 = creds['api_URIs'][0]['token_uri']['path_template_arg2']
        token_path = path_template.format(path_arg1, path_arg2)

        hostname_prefix = creds['api_URIs'][0]['token_uri']['hostname_prefix']
        host = "https://{0}catchpoint.com/".format(hostname_prefix)
        self.token_uri = "{0}{1}".format(host, token_path)

        """ overview: build api endpoint uri: path construction too. """
        path_arg1 = creds['api_URIs'][1]['endpoint_uri']['path_template_arg1']
        path_arg2 = creds['api_URIs'][1]['endpoint_uri']['path_template_arg2']
        api_endpoint_path = path_template.format(path_arg1, path_arg2)
        self.endpoint_uri = "{0}{1}".format(host, api_endpoint_path)

    def _get_raw_performance_data(self, creds):
        """
        Retrieve raw performance chart data.
        """
        self._develop_URIs(creds)
        if not self._auth:
            self._authorize(creds)

        result = self._make_request(self.endpoint_uri)
        return self.normalize_json(result)

    def normalize_json(self,data):
        parsed = data
        items_array=[]
        if("alerts" not in data.keys()):
            for i in parsed["detail"]["items"]:
                temp={}
                for fields in i:
                    if(fields == "breakdown_1"):
                        temp["test_id"]=i[fields]["id"]
                        temp["test_name"]=i[fields]["name"]
                    elif(fields == "breakdown_2"):
                        temp["node_id"]=i[fields]["id"]
                        temp["node_name"]=i[fields]["name"]
                    elif(fields == "timezone"):
                        temp["timezone_id"]=i[fields]["id"]
                        temp["timezone_name"]=i[fields]["name"]
                    else:   
                        temp[fields] = i[fields]        

                items_array.append(temp)

            data["detail"]["items"]=items_array
        return data
