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
POST_HEADERS = {'content-type': 'application/json'}
# Default credentials to login to Insights Account
USERNAME = "amaya.gil"
PASSWORD = "ba58o35s"
SSL_VERIFY = True


def get_json(location, payload=None):
    """
    Performs a GET using the passed URL location
    """
    r = requests.get(
        location,
        auth=(USERNAME, PASSWORD),
        verify=SSL_VERIFY,
        params=payload)

    return r.json()


def post_json(location, json_data):
    """
    Performs a POST and passes the data to the URL location
    """

    result = requests.post(
        location,
        data=json_data,
        auth=(USERNAME, PASSWORD),
        verify=SSL_VERIFY,
        headers=POST_HEADERS)

    print(result.status_code)
    print(result.reason)

def clean_empty_groups(id):
    """
        Performs a DELETE and cleans all empty groups
    """
    location = SYS_API + '/' + str(id)
    d = requests.delete(
        location,
        auth=(USERNAME, PASSWORD),
        verify=SSL_VERIFY)

    if not d.ok:
        print('Error group not found!!! \t' + str(d.status_code) + ' ' + d.reason)

def create_maint_plan(host_name):
    """
        Performs a POST and creates a maintenance plan for a give host
    """
    payload = {'expand': 'system'}
    result = get_json(URL + '/v2/reports', payload)
    plan = {'name' : 'mi_plan'}

   # for elem in result['resources']:
    #    if host_name == elem['system']['hostname']:
            #plan['reports'].append(elem['id'])
            #plan['add'].append(elem['rule_id'])

    location = URL + '/v1/maintenance'
    print(location)
    print(plan)
    post_json(location, json.dumps(plan))
    #print(p.json)

def main():
    """
    Main routine that creates or re-uses an organization and
    life cycle environments. If life cycle environments already
    exist, exit out.
    """

    payload = {'include': 'systems'}
    result = get_json(SYS_API, payload)
    """print(result)
    print ("Grupos: ")
    for groups in result:
        print('\t' + groups['display_name'])
        if not groups['systems']:
            print('ELIMINANDO GRUPO: ' + groups['display_name'])
            clean_empty_groups(groups['id'])
        for sistemas in groups['systems']:
            print('\t\t' + sistemas['hostname'])
            print('\t' + sistemas['product'])
            print('\t' + sistemas['type'])
            print('\t' + sistemas['last_check_in'])
    payload = {'expand': 'system'}
    result = get_json(URL + '/v2/reports', payload)
    print(result)
    for elem in result['resources']:
        print('Report: ' + str(elem['id']) + ' Rule id: ' + str(elem['rule_id']) + '\tSystem: ' + str(elem['system']['hostname']))
"""
    create_maint_plan('gherkin')
if __name__ == "__main__":
    main()