"""
    Copyright 2013 Appurify, Inc
    All rights reserved

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
    License for the specific language governing permissions and limitations
    under the License.
"""
import argparse
import json
import os
import sys
import time
import pprint
import inspect
import requests

from . import constants

from .utils import log, wget
from .api import *


class AppurifyClientError(Exception):
    def __init__(self, message, exit_code=constants.EXIT_CODE_CLIENT_EXCEPTION):
        super(AppurifyClientError, self).__init__(message)
        self.exit_code = exit_code


class AppurifyClient(object):

    def __init__(self, *args, **kwargs):
        self.args = kwargs

        self.access_token = self.args.get('access_token', None)
        self.timeout = self.args.get('timeout_sec', None) or os.environ.get('APPURIFY_API_TIMEOUT', None)
        if self.timeout is not None:
            self.timeout = float(self.timeout)

        self.poll_every = self.args.get('poll_every', None) or os.environ.get('APPURIFY_API_POLL_DELAY', constants.API_POLL_SEC)

        self.test_type = self.args.get('test_type' or None)
        self.device_type_id = self.args.get('device_type_id', None)
        self.device_id = self.args.get('device_id', None)
        disable_ssl_check = self.args.get('disable_ssl_check', False)
        if disable_ssl_check:
            self.verify_ssl = False
        else:
            self.verify_ssl = True

    def refreshAccessToken(self):
        if self.access_token is None:
            api_key = self.args.get('api_key', None)
            api_secret = self.args.get('api_secret', None)
            if api_key is None or api_secret is None:
                raise AppurifyClientError("Either access_token or api_key and api_secret are required parameters", exit_code=constants.EXIT_CODE_BAD_TEST)
            log('generating access token...')
            team = self.args.get('team')
            r = access_token_generate(api_key, api_secret, team=team)
            if r.status_code == 200:
                access_token = r.json()['response']['access_token']
                log('access_token_generate success, access_token:%s' % access_token)
                self.access_token = access_token
            else:
                raise AppurifyClientError('access_token_generate failed with response %s' % r.text, exit_code=constants.EXIT_CODE_AUTH_FAILURE)
        return self.access_token

    def checkDevice(self):
        response_device_list = devices_list(self.access_token)
        data_device_list = json.loads(response_device_list.text.replace("'", "\""))
        device_id_list = []

        for device in data_device_list["response"]:
            device_id_list.append(device["device_type_id"])

        if response_device_list.status_code == 200 and self.device_type_id:
            listOfDevices = self.device_type_id.split(',')
            for d in listOfDevices:
                if int(d) not in device_id_list:
                    raise AppurifyClientError("Current device list does not include device type: %s" % d, exit_code=constants.EXIT_CODE_DEVICE_NOT_FOUND)

    def checkAppCompatibility(self, app_src):
        response_device_list = devices_list(self.access_token)
        data_device_list = json.loads(response_device_list.text.replace("'", "\""))

        reservingDevice = -1

        for device in data_device_list["response"]:
            paramListDevices = self.device_type_id.split(',')
            for d in paramListDevices:
                if int(d) == device["device_type_id"]:
                    reservingDevice = device

                #verify app type works with OS type of device
                if reservingDevice != -1 and int(response_device_list.status_code) == 200:
                    devicePlatform = reservingDevice["os_name"].lower()
                    appType = app_src[-3:]
                    if (appType == "ipa" and devicePlatform == "android") or (appType == "apk" and devicePlatform == "ios"):
                        raise AppurifyClientError("Must install .ipa on iOS device or .apk on android device.  Mismatch: %s installing onto an %s device: %s" % (appType, devicePlatform, d), exit_code=constants.EXIT_CODE_APP_INCOMPATIBLE)

    def uploadApp(self):
        log('uploading app file...')
        app_src_type = self.args.get('app_src_type', None)
        app_src = self.args.get('app_src', None)
        app_name = self.args.get('name', None)
        webapp_url = self.args.get('url', None)
        if app_src is None and self.test_type in constants.NO_APP_SOURCE:
            if webapp_url is None and app_name is None:
                log('WARNING: url for this webapp was not passed (using --url parameter). The results for this app will appear under unclassified_app_group in the UI.')
                log('    To avoid this issue, please pass the url of the website under test using the --url parameter')
            r = apps_upload(self.access_token, None, 'url', self.test_type, name=app_name, webapp_url=webapp_url)
        else:
            if app_src is None:
                raise AppurifyClientError("app src is required for test type %s" % self.test_type, exit_code=constants.EXIT_CODE_BAD_TEST)
            app_size = os.path.getsize(app_src)
            if app_size < 1:
                raise AppurifyClientError("A valid app must contain some data.  The uploaded app is empty.", exit_code=constants.EXIT_CODE_BAD_TEST)
            if app_src_type != 'url':
                self.checkAppCompatibility(app_src)
                with open(app_src, 'rb') as app_file_source:
                    r = apps_upload(self.access_token, app_file_source, app_src_type, app_src_type, app_name)
            else:
                r = apps_upload(self.access_token, app_src, app_src_type, app_src_type, app_name)
        if r.status_code == 200:
            app_id = r.json()['response']['app_id']
            log('apps_upload success, app_id:%s' % app_id)
            return app_id
        else:
            raise AppurifyClientError('apps_upload failed with response %s' % r.text, exit_code=constants.EXIT_CODE_BAD_TEST)

    def uploadTest(self, app_id):
        log('uploading test file...')
        test_src_type = self.args.get('test_src_type', None)
        test_src = self.args.get('test_src', None)
        if not test_src and self.test_type not in constants.NO_TEST_SOURCE:
            raise AppurifyClientError('test_type %s requires a test source' % self.test_type, exit_code=constants.EXIT_CODE_BAD_TEST)
        if test_src:
            test_size = os.path.getsize(test_src)
            if test_size < 1:
                raise AppurifyClientError("Test requires something to exist inside test source.  The uploaded source is empty.", exit_code=constants.EXIT_CODE_BAD_TEST)
            if test_src_type != 'url':
                with open(test_src, 'rb') as test_file_source:
                    r = tests_upload(self.access_token, test_file_source, test_src_type, self.test_type, app_id=app_id)
            else:
                r = tests_upload(self.access_token, test_src, test_src_type, self.test_type, app_id=app_id)
        elif self.test_type in constants.NO_TEST_SOURCE:
            r = tests_upload(self.access_token, None, 'url', self.test_type, app_id=app_id)
        if r.status_code == 200:
            test_id = r.json()['response']['test_id']
            log('tests_upload success, test_id:%s' % test_id)
            return test_id
        else:
            raise AppurifyClientError('tests_upload failed with response %s' % r.text, exit_code=constants.EXIT_CODE_OTHER_EXCEPTION)

    def uploadConfig(self, test_id, config_src):
        log('uploading config file...')
        with open(config_src, 'rb') as config_src_file:
            r = config_upload(self.access_token, config_src_file, test_id)
            if r.status_code == 200:
                log('config file upload success, test_id:%s' % test_id)
                config_id = r.json()['response']['config_id']
                return config_id
            else:
                raise AppurifyClientError('config file upload  failed with response %s' % r.text, exit_code=constants.EXIT_CODE_BAD_TEST)

    def runTest(self, app_id, test_id):
        r = tests_run(self.access_token, self.device_type_id, app_id, test_id, self.device_id)
        if r.status_code == 200:
            test_response = r.json()['response']
            test_run_id = test_response['test_run_id']
            log('tests_run success scheduling test test_run_id:%s' % test_run_id)

            try:
                configs = [test_response['config']]
            except:
                try:
                    configs = map(lambda x: x['config'], test_response['test_runs'])
                except:
                    configs = []

            return (test_run_id, test_response['queue_timeout_limit'] if 'queue_timeout_limit' in test_response else constants.DEFAULT_TIMEOUT, configs)
        else:
            raise AppurifyClientError('runTest failed scheduling test with response %s' % r.text, exit_code=constants.EXIT_CODE_OTHER_EXCEPTION)

    def abortTest(self, test_run_id, reason):
        r = tests_abort(self.access_token, test_run_id, reason)
        if r.status_code == 200:
            response = r.json()['response']
            if response['status'] == 'aborting':
                log("aborting test run id %s" % test_run_id)
            elif response['status'] == 'complete':
                log("test run id %s is complete" % test_run_id)
            return True
        else:
            False

    def printConfigs(self, configs):
        if configs:
            found_config = False
            print "== Test will run with the following device configurations =="
            for config in configs:
                if config:
                    found_config = True
                    print json.dumps(config, sort_keys=True, indent=4, separators=(',', ': '))
            if not found_config:
                print "Default"
            print "== End device configurations =="

    def pollTestResult(self, test_run_id, timeout_limit):
        test_status = None
        runtime = 0

        while test_status != 'complete' and runtime < timeout_limit:
            time.sleep(self.poll_every)
            r = tests_check_result(self.access_token, test_run_id)
            test_status_response = r.json()['response']
            test_status = test_status_response['status']
            if test_status == 'complete':
                test_response = test_status_response['results']
                log("**** COMPLETE - JSON SUMMARY FOLLOWS ****")
                log(json.dumps(test_response))
                log("**** COMPLETE - JSON SUMMARY ENDS ****")
                return test_status_response
            else:
                log("%s sec elapsed (timeout in %s)" % (runtime, (timeout_limit - runtime)))
                if 'message' in test_status_response:
                    log(test_status_response['message'])
                log("Test progress: {}".format(test_status_response.get('detailed_status', 'status-unavailable')))
            runtime = runtime + self.poll_every

        raise AppurifyClientError("Test result poll timed out after %s seconds" % timeout_limit, exit_code=constants.EXIT_CODE_TEST_TIMEOUT)

    @staticmethod
    def download_test_response(results_url, result_dir, verify=True):
        if not os.path.exists(result_dir):
            log("Attempting to create directory %s" % result_dir)
            os.makedirs(result_dir)
        if result_dir:
            result_path = result_dir + '/' + 'results.zip'
            log("Saving results to %s" % result_path)
            try_count = 1
            status_code = 0
            while try_count <= constants.MAX_DOWNLOAD_RETRIES and status_code != 200:
                time.sleep(try_count)
                status_code = wget(results_url, result_path, verify)
                try_count = try_count + 1
            if try_count > constants.MAX_DOWNLOAD_RETRIES:
                log("Error downloading url %s, failed after 5 retries" % results_url)

    def reportTestResult(self, test_status_response):
        log("== reportTestResult ==")
        log(json.dumps(test_status_response))

        exit_code = constants.EXIT_CODE_ALL_PASS
        test_response = test_status_response['results']
        result_dir = self.args.get('result_dir', None)

        if 'complete_count' in test_status_response:
            response_pass = AppurifyClient.print_multi_test_responses(test_response)
            if result_dir:
                AppurifyClient.download_multi_test_response(test_response, result_dir, self.verify_ssl)
        else:
            response_pass = AppurifyClient.print_single_test_response(test_response)
            # make sure test response has the same format in both cases
            test_response = [test_response]

            if result_dir:
                result_url = test_response[0]['url']
                AppurifyClient.download_test_response(result_url, result_dir, self.verify_ssl)

        detailed_status = test_status_response.get('detailed_status')
        if detailed_status == "exception":
            exit_code = self.getExceptionExitCode(test_response)
        elif detailed_status == "timeout":
            exit_code = constants.EXIT_CODE_TEST_TIMEOUT
        else:
            if not response_pass:
                exit_code = constants.EXIT_CODE_TEST_FAILURE

        return exit_code

    def getExceptionExitCode(self, test_response):
        exit_code = constants.EXIT_CODE_CLIENT_EXCEPTION
        try:
            for response in test_response:
                exception = response.get("exception", False)
                if exception:
                    exception_code = exception.split(":")[0]
                    for key in constants.EXIT_CODE_EXCEPTION_MAP:
                        try:
                            exception_code = int(exception_code)
                        except Exception:
                            #if exception code cannot parse into int, means server didn't send correctly.
                            return constants.EXIT_CODE_OTHER_EXCEPTION
                        if exception_code in constants.EXIT_CODE_EXCEPTION_MAP[key]:
                            return key
                    return constants.EXIT_CODE_OTHER_EXCEPTION
        except:
            return constants.EXIT_CODE_OTHER_EXCEPTION
        return exit_code

    @staticmethod
    def print_single_test_response(test_response):
        try:
            for response_type in ['output', 'errors', 'exception', 'number_passes', 'number_fails']:
                response_text = test_response[response_type] or None
                response_text = None if type(response_text) in ('unicode', 'str') and response_text.strip() == '' else response_text
                log("Test %s: %s" % (response_type, response_text))

            response_pass = test_response['pass']
            if response_pass:
                log("All tests passed!")
            else:
                log("There were test failures")

            results_url = test_response['url']
            log("Detailed results url: %s" % results_url)
            return response_pass
        except Exception as e:
            log("Error printing test results: %r" % e)

    @staticmethod
    def print_multi_test_responses(test_response):
        response_pass = True
        for result in test_response:
            log("Device Type %s result:" % result['device_type'])
            AppurifyClient.print_single_test_response(result["results"])
            log("\n")
        return response_pass

    @staticmethod
    def download_multi_test_response(test_response, result_dir, verify=True):
        for result in test_response:
            try:
                result_url = result['results']['url']
                device_type_id = result['device_type_id']
                device_result_path = result_dir + "/device_type_%s" % device_type_id
                AppurifyClient.download_test_response(result_url, device_result_path, verify)
            except Exception as e:
                log("Error downloading test response: %s" % e)

    def main(self):
        """
        See constants for return codes
        """
        exit_code = 0

        try:
            self.refreshAccessToken()

            if self.test_type is None:
                raise AppurifyClientError("test_type is required")

            self.checkDevice()

            # upload app/test of use passed id's
            app_id = self.args.get('app_id', None) or self.uploadApp()
            test_id = self.args.get('test_id', None) or self.uploadTest(app_id)

            config_src = self.args.get('config_src', False)
            if config_src:
                self.uploadConfig(test_id, config_src)

            # start test run
            test_run_id, queue_timeout_limit, configs = self.runTest(app_id, test_id)
            self.printConfigs(configs)

            self.timeout = self.timeout or queue_timeout_limit
            # poll for results and print report
            test_status_response = self.pollTestResult(test_run_id, self.timeout)
            exit_code = self.reportTestResult(test_status_response)

        except AppurifyClientError, e:
            log(str(e))
            exit_code = e.exit_code
        except KeyboardInterrupt, e:
            try:
                self.abortTest(test_run_id, repr(e))
            except UnboundLocalError, e:
                log("Test stopped before session created on server. No run_id found.")
            log(str(e))
            exit_code = constants.EXIT_CODE_TEST_ABORT
        except requests.exceptions.RequestException, e:
            log(str(e))
            exit_code = constants.EXIT_CODE_CONNECTION_ERROR
        except Exception, e:
            log("%s : %s" % (sys.exc_traceback.tb_lineno, str(e)))
            exit_code = constants.EXIT_CODE_CLIENT_EXCEPTION

        log('done with exit code %s' % exit_code)
        return exit_code

    @staticmethod
    def execute(action, kwargs, required):
        """Execute a particular action and prints received response."""
        #disable retries
        os.environ['APPURIFY_API_RETRY_ON_FAILURE'] = '0'
        pp = pprint.PrettyPrinter(indent=4)
        r = globals()[action](**{k: v for k, v in kwargs.iteritems() if k in required})
        pp.pprint(r.json())
        return 0 if r.status_code == 200 else 1

    @staticmethod
    def cli():
        parser = argparse.ArgumentParser(
            description='Appurify developer REST API client v%s' % constants.__version__,
            epilog='Having difficulty using %s? Report at: %s/issues/new or email us at %s' % (constants.__description__, constants.__repourl__, constants.__contact__)
        )

        parser.add_argument('--api-key', help='Appurify developer key')
        parser.add_argument('--api-secret', help='Appurify developer secret')
        parser.add_argument('--team', help="Act on behalf of a team")
        parser.add_argument('--access-token-tag', action='append', help='colon separated key:value tag for access_token to be generated')
        parser.add_argument('--access-token', help='Use an existing access token instead of generating a new one')

        parser.add_argument('--app-src', help='Path or Url of app file to upload')
        parser.add_argument('--app-id', help='Specify to use previously uploaded app file')

        parser.add_argument('--test-src', help='Path or Url of test file to upload')
        parser.add_argument('--test-type', help='Type of test being uploaded')
        parser.add_argument('--test-id', help='Specify to use previously uploaded test file')
        parser.add_argument('--test-run-id', help='Specify test run id (required only while running tests_check_result action)')

        parser.add_argument('--device-type-id', help='Device type to reserve and run tests upon (you may run tests on multiple devices by using a comma separated list of device IDs)')
        parser.add_argument('--device-id', help='Specify to use a particular device')

        parser.add_argument('--config-src', help='Path of additional configuration to add to test')
        parser.add_argument('--result-dir', help='Path to save downloaded results to')
        parser.add_argument('--action', help='Specific API to call (default: main)')

        parser.add_argument('--name', help='Optional, the name of the app to display')
        parser.add_argument('--url', help='If the app being tested is a web application, url of the web application')

        parser.add_argument('--disable-ssl-check', help="Optional, if set, don't verify SSL certificates (e.g. if you're using self-signed certificates)", action="store_true")
        parser.add_argument('--timeout', help='Optional, timeout in seconds before the client assumes the test has failed. Defaults to server side timeout value (~ 6 hours)')
        parser.add_argument('--version', help='Print client version and exit', action='store_true')

        kwargs = {}
        args = parser.parse_args()

        if args.version:
            print(constants.__version__)
            sys.exit(0)

        # (optional) when 'main' is the requested action
        # (required) when 'devices_config' is the requested action
        kwargs['device_id'] = args.device_id

        # (required) access_token || api_key && api_secret
        # (optional) access_token_tag
        if args.access_token is None and (args.api_key is None or args.api_secret is None):
            parser.error('--access-token OR --api-key and --api-secret is required')

        kwargs['test_run_id'] = args.test_run_id
        kwargs['api_key'] = args.api_key
        kwargs['api_secret'] = args.api_secret
        kwargs['team'] = args.team
        kwargs['access_token'] = args.access_token
        kwargs['access_token_tag'] = args.access_token_tag
        kwargs['disable_ssl_check'] = args.disable_ssl_check

        # (optional)
        if args.action:
            if args.action in constants.ENABLED_ACTIONS:
                argspec = inspect.getargspec(globals()[args.action])
                required = argspec[0] if not argspec[3] else argspec[0][: -1 * len(argspec[3])]
                for k in required:
                    if not k in kwargs or not kwargs[k]:
                        parser.error('"%s" action requires following parameters: %s. "%s" not found.' % (args.action, ", ".join(required), k))
                sys.exit(AppurifyClient.execute(args.action, kwargs, required))
            else:
                parser.error('"%s" action is not supported. Available options are: %s' % (args.action, ", ".join(constants.ENABLED_ACTIONS)))

        # (required) app_id || app_src
        # (optional) app_test_type
        # (calculated) app_src_type
        if args.app_id is None and args.app_src is None and args.test_type not in constants.NO_APP_SOURCE:
            parser.error('--app-id OR --app-src is required')

        kwargs['app_id'] = args.app_id
        kwargs['app_src'] = args.app_src

        if args.app_src:
            if args.app_src[0:4] == 'http':
                kwargs['app_src_type'] = 'url'
            else:
                try:
                    with open(args.app_src) as _:
                        pass
                    kwargs['app_src_type'] = 'raw'
                except:
                    parser.error('--app-src %s could not be found' % args.app_src)

        # (required) test_id || test_src && test_type
        if args.test_id is None and (args.test_src is None or args.test_type is None) and args.test_type not in constants.NO_TEST_SOURCE:
            parser.error('--test-id OR --test-src and --test-type is required')

        kwargs['test_id'] = args.test_id
        kwargs['test_type'] = args.test_type
        kwargs['test_src'] = args.test_src
        if args.test_type not in constants.SUPPORTED_TEST_TYPES:
            parser.error('--test-type must be one of the following: %s' % ', '.join(constants.SUPPORTED_TEST_TYPES))

        # (calculated) test_src_type
        if args.test_src:
            if args.test_src[0:4] == 'http':
                kwargs['test_src_type'] = 'url'
            else:
                try:
                    with open(args.test_src) as _:
                        pass
                    kwargs['test_src_type'] = 'raw'
                except:
                    parser.error('--test-src %s could not be found' % args.test_src)

        # (optional) config_src
        if args.config_src is not None:
            kwargs['config_src'] = args.config_src

        # (required) device_type_id
        kwargs['device_type_id'] = args.device_type_id

        # (optional) result_dir
        kwargs['result_dir'] = args.result_dir

        # (optional) app name
        kwargs['name'] = args.name

        kwargs['url'] = args.url

        # (optional) timeout
        try:
            kwargs['timeout_sec'] = int(args.timeout)
        except:
            pass

        client = AppurifyClient(**kwargs)
        sys.exit(client.main())


def init():
    AppurifyClient.cli()

if __name__ == '__main__':
    init()
