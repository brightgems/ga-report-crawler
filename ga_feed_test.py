#-*- coding:utf8 -*-

"""Hello Analytics Reporting API V4."""

import argparse

from apiclient.discovery import build
import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools
import os

os.environ.setdefault('http_proxy','http://localhost:1080')
SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
DISCOVERY_URI = ('https://analyticsreporting.googleapis.com/$discovery/rest')
CLIENT_SECRETS_PATH = os.path.join(os.path.dirname(__file__), 'client_secrets.json') # Path to client_secrets.json file.




def initialize_analyticsreporting():
    """Initializes the analyticsreporting service object.
    
    Returns:
      analytics an authorized analyticsreporting service object.
    """
    # Parse command-line arguments.
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[tools.argparser])
    flags = parser.parse_args([])
    
    # Set up a Flow object to be used if we need to authenticate.
    flow = client.flow_from_clientsecrets(
        CLIENT_SECRETS_PATH, scope=SCOPES,
        message=tools.message_if_missing(CLIENT_SECRETS_PATH))
    
    # Prepare credentials, and authorize HTTP object with them.
    # If the credentials don't exist or are invalid run through the native client
    # flow. The Storage object will ensure that if successful the good
    # credentials will get written back to a file.
# CREDENTIAL_STORE_FILE =  os.path.join(os.path.dirname(__file__),
#                                 API_NAME + '.dat')
    
    storage = file.Storage(os.path.join(os.path.dirname(__file__),'analyticsreporting.dat'))
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(flow, storage, flags)
    http = credentials.authorize(http=httplib2.Http())
    
    # Build the service object.
    analytics = build('analytics', 'v3', http=http, discoveryServiceUrl=DISCOVERY_URI,cache_discovery=False)
    
    return analytics

def get_report(analytics,view_id):
    # Use the Analytics Service Object to query the Analytics Reporting API V4.
    return analytics.reports().batchGet(
        body={
          'reportRequests': [
          {
            'viewId': view_id,
            'dateRanges': [{'startDate': '7daysAgo', 'endDate': 'today'}],
            'dimensions':[{'name':'ga:campaign'}
                          ,{'name':'ga:source'}
                          ,{'name':'ga:sourceMedium'}
                          ,{'name':'ga:medium'}
                          ,{'name':'ga:date'}
                          ,{'name':'ga:week'}  
                          ,{'name':'ga:landingPagePath'}                                                 
                          ],
            'metrics': [{'expression': 'ga:sessions'}
                        ,{'expression':'ga:percentNewSessions'}
                        ,{'expression':'ga:pageviews'}
                        ,{'expression':'ga:uniquePageviews'}
                        ,{'expression':'ga:bounceRate'}
                        ,{'expression':'ga:avgTimeOnPage'}]
          }]
        }
    ).execute()


def print_response(response,view_id):
    """Parses and prints the Analytics Reporting API V4 response"""
    
    for report in response.get('reports', []):
        columnHeader = report.get('columnHeader', {})
        dimensionHeaders = columnHeader.get('dimensions', [])
        metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])
        rows = report.get('data', {}).get('rows', [])
    #根据行数循环
    ls=[]
    for row in rows:
        dimensions = row.get('dimensions', [])
        dateRangeValues = row.get('metrics', [])
        
        # metrics : value
        dim_col = {}
        dim_t = []
        for header, dimension in zip(dimensionHeaders, dimensions):
            dim_col[header] = dimension 
            print header + ': ' + dimension
        print dim_col
        
        
        metrc_col = {}   
        for i, values in enumerate(dateRangeValues):
            print 'Date range (' + str(i) + ')'
            for metricHeader, value in zip(metricHeaders, values.get('values')):
                metrc_col[metricHeader.get('name')] = value
                print metricHeader.get('name') + ': ' + value
        p_record = dict(dim_col,**metrc_col)
        p_record['ga:view_id'] = view_id
        ls.append(p_record)
    return ls

def get_response(view_id):

    analytics = initialize_analyticsreporting()
    response = get_report(analytics,view_id)
    return print_response(response,view_id)
    
def main():
    view_id = '142583166'
    ls = get_response(view_id)
    print(ls)
    
if __name__ == '__main__':
    main()