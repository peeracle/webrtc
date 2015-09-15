"""
    Copyright 2013 Appurify, Inc
    All rights reserved

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
    License for the specific language governing permissions and limitations
    under the License.
"""
from .utils import get, post

####################
## Access Token API
####################


def access_token_generate(api_key, api_secret, team=None, access_token_tag=None):
    """Generate an access token, given an api key and secret"""
    data = {'key': api_key, 'secret': api_secret}
    if type(access_token_tag) == list:
        data['tags'] = access_token_tag
    if team:
        data['team'] = team
    return post('access_token/generate', data)


def access_token_list(api_key, api_secret, page_no=1, page_size=10):
    """Retrieve a list of access tokens for a particular key/secret pair"""
    return get('access_token/list', {'key': api_key, 'secret': api_secret, 'page_no': page_no, 'page_size': page_size})


def access_token_usage(api_key, api_secret, access_token, page_no=1, page_size=10):
    """ DEPRECATED. Will be removed in future versions.
    Get details on device time used for a particular key/secret pair
    """
    return get('access_token/usage', {'key': api_key, 'secret': api_secret, 'access_token': access_token, 'page_no': page_no, 'page_size': page_size})


def access_token_validate(access_token):
    """Verify that an access token is valid and retrieve the remaining ttl for that token"""
    return post('access_token/validate', {'access_token': access_token})


def access_token_revoke(access_token):
    """Revoke access token."""
    return post('access_token/revoke', {'access_token': access_token})

##############
## Device API
##############


def devices_list(access_token):
    """Get list of devices"""
    return get('devices/list', {'access_token': access_token})


def devices_config_list(access_token):
    """Get available configuration option for devices"""
    return get('devices/config/list', {'access_token': access_token})


# TODO: access configuration parameters and pass it on
def devices_config(access_token, device_id):
    """Fetch configuration of specific device id"""
    return post('devices/config', {'access_token': access_token, 'device_id': device_id})


def devices_config_networks_list(access_token):
    return get('devices/config/networks/list', {'access_token': access_token})

###########
## App API
###########


def apps_list(access_token):
    return get('apps/list', {'access_token': access_token})


def apps_upload(access_token, source, source_type, type=None, name=None, webapp_url=None):
    files = None if source_type == 'url' else {'source': source}
    data = {'access_token': access_token, 'source_type': source_type}

    if source_type == 'url':
        data['source'] = source
    if type:
        data['app_test_type'] = type
    if name:
        data['name'] = name
    if webapp_url:
        data['url'] = webapp_url

    return post('apps/upload', data, files)

############
## Test API
############


def tests_list(access_token):
    return get('tests/list', {'access_token': access_token})


def tests_upload(access_token, test_source, test_source_type, test_type, app_id=None):
    files = None if test_source_type == 'url' else {'source': test_source}
    data = {'access_token': access_token, 'source_type': test_source_type, 'test_type': test_type}
    if app_id:
        data['app_id'] = app_id
    if test_source_type == 'url':
        data['source'] = test_source
    return post('tests/upload', data, files)


def tests_run(access_token, device_type_id, app_id, test_id, device_id=None):
    return post('tests/run', {'access_token': access_token, 'device_type_id': device_type_id, 'app_id': app_id, 'test_id': test_id, 'device_id': device_id, 'async': '1'})


def tests_check_result(access_token, test_run_id):
    return get('tests/check', {'access_token': access_token, 'test_run_id': test_run_id})


def tests_abort(access_token, test_run_id, reason='Not specified.'):
    return post('tests/abort', {'access_token': access_token, 'test_run_id': test_run_id, 'reason': reason})


###################
## Config file API
###################

def config_upload(access_token, config_src, test_id):
    """Upload a configuration file to associate with a test."""
    data, files = {'access_token': access_token, 'test_id': test_id}, {'source': config_src}
    return post('tests/config/upload', data, files)
