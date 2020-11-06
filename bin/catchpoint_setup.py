import splunk, splunk.admin as admin, splunk.entity as en
from auth_handler import *
from requests_handler import *
import json,sys
'''
Copyright (C) 2005 - 2010 Splunk Inc. All Rights Reserved.
Description:  This skeleton python script handles the parameters in the configuration page.

      handleList method: lists configurable parameters in the configuration page
      corresponds to handleractions = list in restmap.conf

      handleEdit method: controls the parameters and saves the values
      corresponds to handleractions = edit in restmap.conf

      reference: http://wiki.splunk.com/Create_setup_screen_using_a_custom_endpoint
'''
class ConfigApp(admin.MConfigHandler):

  catchpoint_args = ("url", "access_token", "expires_in", "endpoint_uri", "is_refreshed", "tid_store", "client_secret")
  cp = auth_handler.Catchpoint()
  '''
  Changes argument format from how it is received from the web form to match the expexted creds format from: auth_handler.py _authorize(self, creds)
  '''
  def changeArgsFormat(self, args):
   
    tempArgs = {}
    for arg in self.catchpoint_args:
      if arg is not None:
          if arg == "access_token":
            tempArgs["refresh_token"] = ""
          else:
            tempArgs[arg] = args[arg][0]
    tempArgs['api_URIs'] = [
                {'token_uri': {
                    'hostname_prefix': 'io.',
                    'path_template_arg1': 'ui/',
                    'path_template_arg2': 'token/'
                }},
                {'endpoint_uri': {
                    'hostname_prefix': 'io.',
                    'path_template_arg1': 'ui/',
                    'path_template_arg2': '{0}/performance/raw?tests=' .format('v1')
                }}
                ]
    return tempArgs

  '''
  Get Access_token from form input
  '''
  def requestToken(self, args):
    catchpoint = Catchpoint()
    response = {}

    creds = self.changeArgsFormat(args)
    catchpoint._develop_URIs(creds)
    catchpoint._authorize(creds)
    response["access_token"] = catchpoint._token
    response["expires_in"] = catchpoint.expires_in
    response["endpoint_uri"] = catchpoint.endpoint_uri
    response["is_refreshed"] = "NO"
    return response  #  catchpoint._token

  '''
  Set up supported arguments
  '''
  def setup(self):
    if self.requestedAction == admin.ACTION_EDIT:
      for arg in self.catchpoint_args:
        self.supportedArgs.addOptArg(arg)

  '''
  Read the initial values of the parameters from the custom file
      myappsetup.conf, and write them to the setup screen.

  If the app has never been set up,
      uses .../<appname>/default/myappsetup.conf.

  If app has been set up, looks at
      .../local/myappsetup.conf first, then looks at
  .../default/myappsetup.conf only if there is no value for a field in
      .../local/myappsetup.conf

  For boolean fields, may need to switch the true/false setting.

  For text fields, if the conf file says None, set to the empty string.
  '''

  def handleList(self, confInfo):
    confDict = self.readConf("catchpoint")
    if None != confDict:
      for stanza, settings in confDict.items():
        for key, val in settings.items():
          if key in self.catchpoint_args:
            if val is None:
              val = ''
            confInfo[stanza].append(key, val)


  '''
  After user clicks Save on setup screen, take updated parameters,
  normalize them, and save them somewhere
  '''
  def handleEdit(self, confInfo):

    name = self.callerArgs.id
    args = self.callerArgs.data
    client_identifier = args["client_secret"]
    args['access_token'][0] = ' '
    ''' String type expected. Will throw error if None type is found '''
    for arg in self.catchpoint_args:
      if args.get(arg, None) and args[arg][0] is None:
        args[arg][0] = ' '

    response = None #self.requestToken(args)
    returnedToken = None #response["access_token"]

    if returnedToken:
      args["access_token"][0] = returnedToken
      args["expires_in"][0] = auth_handler.Catchpoint()._prepare_expire()
      args["endpoint_uri"][0] = response["endpoint_uri"]
      #args["is_refreshed"][0] = "NO"
      args["tid_store"][0] = ","

    '''
    Since we are using a conf file to store parameters,
    write them to the [setupentity] stanza
    in <appname>/local/myappsetup.conf
    '''

    self.writeConf('catchpoint', client_identifier[0], self.callerArgs.data)

admin.init(ConfigApp, admin.CONTEXT_NONE)