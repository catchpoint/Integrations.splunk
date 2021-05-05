import os
import splunk.clilib.cli_common as cli_common, splunk, json
import splunk.entity as entity
from auth_handler import *
from requests_handler import *
from datetime import *
import logger
logger = logger.setup_logger("app_catchpoint.log")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from splunklib.modularinput import *
from splunklib import six

class Splunk_Integration_ModInput(Script):
    """All modular inputs should inherit from the abstract base class Script
    from splunklib.modularinput.script.
    They must override the get_scheme and stream_events functions, and,
    if the scheme returned by get_scheme has Scheme.use_external_validation
    set to True, we should also override the validate_input function.
    """
    
    def get_scheme(self):
        scheme = Scheme("Catchpoint Modular Input")
        scheme.description = "Stream specified test metrics into Splunk from Catchpoint"
        scheme.use_external_validation = True
        scheme.use_single_instance = False
        
        # Add client_identifier variable to the scheme using the Argument class and its properties.
        client_identifier = Argument(
            name = "client_identifier",
            description = "Client Secret from Catchpoint Portal for a particular division or client.",
            data_type = Argument.data_type_string,
            required_on_edit = False,
            required_on_create = True
        )

        # Add test_arg variable to the scheme using the Argument class and its properties.
        test_arg = Argument(
            name = "test_id",
            description = "The test ID(s).",
            data_type = Argument.data_type_string,
            required_on_edit = False,
            required_on_create = False
        )

        # Add data_type_arg variable to the scheme using the Argument class and its properties.
        data_type_arg = Argument(
            name = "data_retrieval",
            description = "The type of data to be ingested.",
            data_type = Argument.data_type_string,
            required_on_edit = True,
            required_on_create = True
        )

        scheme.add_argument(test_arg)
        scheme.add_argument(data_type_arg)
        scheme.add_argument(client_identifier)
        return scheme

    def validate_input(self, validation_definition):
        """We are using external validation to verify data_retrieval and client_identifier option is selected
        by the user from data input. If validate_input function does not raise an Exception, 
        the input is assumed to be valid. Otherwise it prints the exception as an error message
        when telling splunkd that the configuration is invalid.
        """
        data_retrieval = validation_definition.parameters["data_retrieval"]
        client_identifier = validation_definition.parameters["client_identifier"]

        if not data_retrieval:
            raise ValueError("All fields must have a value")
        if not client_identifier:
            raise ValueError("All fields must have a value")

    def interval_handler(self, input_name, setup_input, test_id, end, start, data_retrieval, client_identifier):
        """Update configuration in local/catchpoint.conf.
        """
        interval = str(Catchpoint()._get_interval(end, start)) if data_retrieval != 'alerts' else '1200'
        try:
            stanza_lname = str(input_name.split('://')[1])
            if stanza_lname not in setup_input['tid_store']:
                import splunklib.client as client, ssl

                ssl._create_default_https_context = ssl._create_unverified_context
                service = self.service
                catchpoint_conf = service.confs.__getitem__('catchpoint').__getitem__(client_identifier)
                catchpoint_conf.update(**{'tid_store' : '{0},{1}'.format(stanza_lname, catchpoint_conf.content['tid_store'] )})
                item = service.inputs.__getitem__(stanza_lname)
                item.post(**{'data_retrieval': data_retrieval, 'test_id': test_id, 'interval': interval, 'client_identifier': client_identifier})
                item.refresh()
        except Exception as e:
            logger.exception('Exception in interval_handler')
            logger.exception(e)

    def write_event_handler(self, content, event_data, test_id, setup_input, ew, data_retrieval, client_identifier):
        head = next(content)
        self.interval_handler(event_data.stanza, setup_input, test_id, str(head['end']), str(head['start']), data_retrieval, client_identifier)
        
        import itertools       
        for event in itertools.chain([head], content):
            event_data.data = json.dumps(event, sort_keys=True)
            ew.write_event(event_data)
        ew.close()

    def stream_events(self, inputs, ew):
        """Splunk calls this method to process events
        By default (no arguments), uses stdin and stdout
        :param inputs: an InputDefinition object
        :param ew: an EventWriter object
        """
        try:  
            # Go through each input for this modular input, extract test_id, data_retrieval_type and client_identifier from local/inputs.conf file
            event_data = Event()
            for input_name, input_item in six.iteritems(inputs.inputs):
                logger.info("name: {0}, \nitem: {1}\n\n\n".format(input_name, input_item))
                data_retrieval_type = input_item['data_retrieval']
                event_data = Event()
                event_data.index = input_item['index']
                logger.info("event_data.index = = "+str(event_data.index))
                test_id = input_item['test_id'] if data_retrieval_type != 'alerts' else 'n/a'
                client_identifier = input_item['client_identifier']
                event_data.stanza = input_name
                service = self.service
                myapp = cli_common.getConfStanza("app", "package")['id']

                # List all credentials that are stored in this Splunk app.
                entities = entity.getEntities(['admin', 'passwords'], namespace=myapp, owner='nobody', sessionKey=service.token)
                credentials = []

            # Extract all client secrets and client keys for the pull API authorization.
            for i, c in entities.items():
                if(c['eai:acl']['app']=="search_cp" and c['username']==client_identifier):
                    credentials.append((c['username'], c['clear_password']))

            consumer_secret, consumer_key = credentials.pop()
            # Opening catchpoint.conf to update details.
            setup_input = cli_common.getConfStanza("catchpoint", client_identifier)    
            content = Request().refresh_token(test_id, consumer_key, consumer_secret, setup_input, data_retrieval_type, client_identifier, service)
            self.write_event_handler(content, event_data, test_id, setup_input, ew, data_retrieval_type, client_identifier)
            ew.write_event(event_data)
        except Exception as e:
            logger.exception('stream_events err: ')
            logger.exception(e)


if __name__ == "__main__":
    sys.exit(Splunk_Integration_ModInput().run(sys.argv))
