
from __future__ import print_function
import httplib2
import os
from datetime import datetime, timedelta

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# This is based on https://developers.google.com/sheets/api/quickstart/python

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'vendors/google_client_secret.json'
CLIENT_CREDTS_FILE = 'sheets.googleapis.com-python-finecast.json'
APPLICATION_NAME = 'Finecast API'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, CLIENT_CREDTS_FILE)

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def get_sheets_service():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4')

    return discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)

def get_drive_service():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())

    return discovery.build('drive', 'v3', http=http)

def sheettime(xldate, delta=0):
    # datemode: 0 for 1900-based, 1462 * 1 for 1904-based
    return (
        datetime(1899, 12, 30)
        + timedelta(days=xldate + delta)
    )
