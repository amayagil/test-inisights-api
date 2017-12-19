import json
import sys


try:
    import requests
except ImportError:
    print("Please install the python-requests module.")
    sys.exit(-1)

# URL to Insights
URL = "https://access.redhat.com/r/insights"
# URL for the API to your deployed insights account
ACCOUNT_API = "%s/v1/account/" % URL
SYS_API = "%s/v1/groups" % URL
# Default credentials to login to your Insights Account, please change
USERNAME = "changeme"
PASSWORD = "changeme"
SSL_VERIFY = True
POST_HEADERS = {'content-type': 'application/json'}

class InsightsRequest:

    def __init__(self, location, data=None):
        """
        Class constructor
        :param location:
        :param data:
        """
        self.location = location
        self.data = data

    def get_insights(self):
        """
        Performs a GET using the passed URL location
        """
        r = requests.get(
            self.location,
            auth=(USERNAME, PASSWORD),
            verify=SSL_VERIFY,
            params=self.data)

        if self._check_http_response(r):
            return r.json()
        else:
            return None

    def post_insights(self):
        """
        Performs a POST and passes the data to the URL location
        """
        r = requests.post(
            self.location,
            data=self.data,
            auth=(USERNAME, PASSWORD),
            verify=SSL_VERIFY,
            headers=POST_HEADERS)

        return self._check_http_response(r)

    def delete_insights(self):
        """
            Performs a DELETE and cleans all empty groups
        """
        r = requests.delete(
            self.location,
            auth=(USERNAME, PASSWORD),
            verify=SSL_VERIFY)

        return self._check_http_response(r)

    def _check_http_response(self, result):
        if not result.ok:
            print('HTTP Error found!!! \n' + ' CODE: ' + str(result.status_code) + '\n REASON: ' + result.reason)
        return result.ok

def cute_output(insights_request):
    """
    Prints desired values of the object in a nicer form
    :param insights_request:
    :return:
    """
    json_report = insights_request.get_insights()

    if not json_report:
        print('Error ocurred, unable to print!!!')
    else:
        for groups in json_report:
            print('GROUP: ' + groups['display_name'])
            for systems in groups['systems']:
                print('\n\t\t Host name: ' + systems['hostname'])
                print('\n\t\t Product: ' + systems['product'])
                print('\n\t\t Type: ' + systems['type'])
                print('\n\t\t Registered at Insights: ' + systems['created_at'])
                print('\n\t\t Last checked at Insights: ' + systems['last_check_in'] + '\n\n')

def clean_empty_group(id):
    """
        Performs a DELETE and cleans all empty groups
    """
    location = SYS_API + '/' + str(id)
    insights_request = InsightsRequest(location)

    if not insights_request.delete_insights():
        print('Unable to clean group ' + str(id))

def create_maint_plan(host_name):
    """
        Performs a POST and creates a maintenance plan for a given host
    """
    location = URL + '/v2/reports'
    #location = URL + '/v1/maintenance'
    payload = {'expand': 'system'}
    insights_request = InsightsRequest(location,payload)
    plan = {'name' : 'my_plan'}

    json_data = insights_request.get_insights()
    if json_data is not None:
        for report in json_data['resources']:
            if host_name == report['system']['hostname']:
                plan['reports'].append(report['id'])
                plan['add'].append(report['rule_id'])
        insights_request.location = URL + '/v1/maintenance'
        insights_request.data = json.dumps(plan)
        result = insights_request.post_insights()
        if not result:
            print('Error occurred while create maintenance plan, for host ' + host_name)
        return result
    return False

def main():
    """
    Main routine that creates or re-uses an organization and
    life cycle environments. If life cycle environments already
    exist, exit out.
    """

    payload = {'include': 'systems'}
    insights_request = InsightsRequest(SYS_API, payload)
    cute_output(insights_request)

    groups = insights_request.get_insights()
    found = False

    for elem in groups:
        if not elem['systems']:
            found = True
            print('Deleting empty group ' + elem['display_name'])
            clean_empty_group(elem['id'])
    if not found:
        print('No empty groups found, nothing to delete!!!')

    payload = {'expand': 'system'}
    insights_request = InsightsRequest(URL + '/v2/reports', payload)
    reports = create_maint_plan(insights_request)
    """
    print(reports)

    result = get_json(URL + '/v2/reports', payload)
    print(result)
    for elem in result['resources']:
        print('Report: ' + str(elem['id']) + ' Rule id: ' + str(elem['rule_id']) + '\tSystem: ' + str(elem['system']['hostname']))
    """
    #create_maint_plan('gherkin')
if __name__ == "__main__":
    main()