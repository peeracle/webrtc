"""
    Copyright 2013 Appurify, Inc
    All rights reserved

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
    License for the specific language governing permissions and limitations
    under the License.
"""
# Current development version
# Increment this during development as and when desired
# setup.py will use this version to generate new releases
VERSION = (1, 0, 0)
__version__ = '.'.join(map(str, VERSION[0:3])) + ''.join(VERSION[3:])

# Last tagged stable version
# Bump this to match VERSION when dev version is stable for new release
# and also have passed Sencha architect tool integration tests
# This variable is only used by REST API (/client/version/)
STABLE_VERSION = (0, 4, 9)
__stable_version__ = '.'.join(map(str, STABLE_VERSION[0:3])) + ''.join(STABLE_VERSION[3:])

__homepage__ = 'http://appurify.com'
__license__ = 'Commercial'
__description__ = 'Appurify Developer Python Client'
__contact__ = "support@appurify.com"
__repourl__ = 'http://github.com/appurify/appurify-python'

API_PROTO = "https"             # override using APPURIFY_API_PROTO environment variable
API_HOST = "live.appurify.com"  # APPURIFY_API_HOST
API_PORT = 443                  # APPURIFY_API_PORT

API_POLL_SEC = 15               # test result polled every poll seconds (APPURIFY_API_POLL_DELAY)

API_RETRY_ON_FAILURE = 1        # should client retry API calls in case of non-200 response (APPURIFY_API_RETRY_ON_FAILURE)
API_RETRY_DELAY = 1             # (in seconds) if retry on failure is enabled, interval between each retry (APPURIFY_API_RETRY_DELAY)
API_MAX_RETRY = 3               # if retry on failure is enabled, how many times should client retry (APPURIFY_API_MAX_RETRY)

API_STATUS_UP = 1               # aws status page code for service up and running
API_STATUS_DOWN = 2             # service is down
API_WAIT_FOR_SERVICE = 1        # should client wait for service to come back live by polling aws status page?
API_STATUS_BASE_URL = 'https://s3-us-west-1.amazonaws.com/appurify-api-status'

MAX_DOWNLOAD_RETRIES = 10           # Number of times client should try to download the test results before giving up

DEFAULT_TIMEOUT = 3600              # default timeout if one cant be obtained from platform

# Exit codes
EXIT_CODE_ALL_PASS = 0              # Test completed with no exceptions or errors
EXIT_CODE_TEST_FAILURE = 1          # Test completed normally but reported test failures
EXIT_CODE_TEST_ABORT = 2            # Test was aborted by the user or system
EXIT_CODE_TEST_TIMEOUT = 3          # Test was aborted by the system because of timeout
EXIT_CODE_DEVICE_FAILURE = 4        # Test could not be completed because the device could not be activated or reserved
EXIT_CODE_BAD_TEST = 5              # Test could not execute because there was an error in the configuration or uploaded files
EXIT_CODE_AUTH_FAILURE = 6          # Test could not execute because the server rejected the provided credentials (key/secret)
EXIT_CODE_OTHER_EXCEPTION = 7       # Test could not execute because of other server/remote exception
EXIT_CODE_CLIENT_EXCEPTION = 8      # Test could not execute because of an unexpected error in the client
EXIT_CODE_CONNECTION_ERROR = 9      # Test got a connection error attempting to reach the server
EXIT_CODE_APP_INSTALL_FAILED = 10   # The app could not be installed on the device (possibly due to incorrect build)
EXIT_CODE_INVALID_PROVISION = 11    # Test could not execute because device type is not found in user pool
EXIT_CODE_INVALID_DEVICE = 12       # Test could not execute because app is not built for device type
EXIT_CODE_DEVICE_NOT_FOUND = 13     # Device doesn't exist in users device pool
EXIT_CODE_APP_INCOMPATIBLE = 14     # Device doesn't exist in users device pool
EXIT_CODE_GRID_TIMEOUT = 15         # Test reached timeout for grid session

# TODO: Probably should be fetching these from the server at some point
EXIT_CODE_EXCEPTION_MAP = {EXIT_CODE_TEST_ABORT : [4000, 5000],
                          EXIT_CODE_APP_INSTALL_FAILED : [4007],
                          EXIT_CODE_GRID_TIMEOUT : [7003, 7005, 7007],
                          EXIT_CODE_INVALID_PROVISION : [4008, 4005],
                          EXIT_CODE_INVALID_DEVICE : [4006, 4009],
                          EXIT_CODE_TEST_TIMEOUT : [4001, 4002, 4003, 1010],
                          EXIT_CODE_DEVICE_FAILURE: [1000, 1001, 1002, 1005, 1008, 1009, 1011, 1012, 1013, 1014],
                          EXIT_CODE_BAD_TEST: [1003, 1006, 1007, 1008, 3000, 3001, 3003, 3004]}


SUPPORTED_TEST_TYPES = [
    'calabash',
    'ocunit',
    'uiautomation',
    'robotium',
    'ios_robot',
    'android_uiautomator',
    'kiwi',
    'cedar',
    'kif',
    'android_calabash',
    'ios_selenium',
    'android_selenium',
    'ios_webrobot',
    'appium',
    'browser_test',
    'appurify_recording',
    'network_headers',
    'ios_sencharobot',
    'android_monkey',
    'calabash_refresh_app',
    'ios_webviewrobot',
    'ios_wpt',
    'touch_test',
    'ios_monkeytalk',
    'android_robot',
    'android_monkeytalk',
    'espresso',
    'android_spoon'
]

NO_TEST_SOURCE = [
    'ios_robot',
    'ios_webrobot',
    'browser_test',
    'kif',
    'kif:google',
    'network_headers',
    'ios_sencharobot',
    'ios_webviewrobot',
    'ios_wpt',
    'touch_test',
    'android_robot',
]

NO_APP_SOURCE = [
    'ios_selenium',
    'android_selenium',
    'ios_webrobot',
    'browser_test',
    'network_headers',
    'ios_webviewrobot',
    'ios_wpt',
    'appium',
    'android_spoon',
]

ENABLED_ACTIONS = [
    'access_token_generate',
    'access_token_list',
    'access_token_usage',
    'access_token_validate',
    'devices_list',
    'devices_config',
    'devices_config_list',
    'devices_config_networks_list',
    'tests_list',
    'tests_check_result',
]
