
from __future__ import print_function
import httplib2
import os
import re
import csv
import json

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_id.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'


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
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-quickstart.json')

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

def clean_data(person):
    try:
        name = person[0:person.find('<')].encode('utf8').replace('\"','')
    except AttributeError, e:
        print('error getting name', e)
        name = None

    try:
        email = re.search('<(.*?)>', person).group(0)
    except AttributeError, e:
        email = person[person.find('<'):person.find('>')].encode('utf8').replace('\"','')
    except Exception, e:
        print('error getting email', e)
        email = None

    return (name,email)

def main():
    """Shows basic usage of the Gmail API.

    Creates a Gmail API service object and outputs a list of message names
    of the user's Gmail account.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    messageIds = []
    i = 0
    nextPageToken = None
    while (i <= 15):
        try:
            response = service.users().messages().list(userId='me', q='after:2016/09/01', maxResults=10000, pageToken=nextPageToken).execute()
            messages = response.get('messages')
            nextPageToken = response['nextPageToken']

            for m in messages:
                messageIds.append(m['id'])

            i+=1            
        except KeyError:
            break

    senders = []
    counter = 0
    for i in messageIds:
        data = service.users().messages().get(userId='me', id=i).execute()
        for d in data['payload']['headers']:
            if d['name'] == 'Received':
                print(d['value'][d['value'].find('; ')+1:d['value'].find('(PST)')])
            if d['name'] == 'From' and 'bounce' not in d['value']:
                senders.append(d['value'])
                print(counter, ' ', d['value'])
                counter += 1
                break

    emails = []
    with open('out.csv', 'wb') as f:
        writer = csv.writer(f, delimiter=',')
        for person in set(senders):
            cleaned = clean_data(person)
            name = cleaned[0]
            email = cleaned[1]
            if email not in emails:
                emails.append(email)
                if name != None and email != None:
                    writer.writerow([name, email])

if __name__ == '__main__':
    main()