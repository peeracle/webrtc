"""
Copyright 2013 Appurify, Inc
All rights reserved
    
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.

To run tests:
from parent directory of tests:
python -m unittest tests.test_client
"""
import unittest
import json
import mock
import os
from appurify.client import AppurifyClient, AppurifyClientError
from appurify.constants import EXIT_CODE_APP_INSTALL_FAILED, EXIT_CODE_CLIENT_EXCEPTION, EXIT_CODE_OTHER_EXCEPTION
class TestObject(object):
    pass

def mockRequestObj(response_obj, status_code=200):
    r = TestObject()
    r.headers = {'x-api-server-hostname': 'django-01'}
    r.text = json.dumps(response_obj)
    r.status_code = status_code
    r.json = lambda: response_obj
    return r

def mockRequestPost(url, data, files=None, verify=False, headers={'User-Agent': 'MockAgent'}):
    if 'access_token/generate' in url:
        return mockRequestObj({"meta": {"code": 200}, "response": {"access_token": "test_access_token", "ttl": 86400}})
    if 'apps/upload' in url:
        name = data.get('name', None)
        return mockRequestObj({"meta": {"code": 200}, 
                               "response": {"_id_": None, 
                                            "uploaded_on": "2013-09-09T21:25:24Z", 
                                            "name": name, 
                                            "app_group_id": None, 
                                            "test_type": "test_test_type", 
                                            "size": None, 
                                            "app_group": "None", 
                                            "id": 12345, 
                                            "app_id": "test_app_id"}})
    if 'tests/upload' in url:
        return mockRequestObj({"meta": {"code": 200}, 
                               "response": {"uploaded_on": "2013-09-09T22:30:51Z", 
                                            "name": "use_bdd_tests.zip", "ttl": 86400,
                                             "config": None, 
                                             "test_type": "uiautomation",
                                             "test_id": "test_test_id", 
                                              "expired": False, 
                                              "id": 3456, 
                                              "size": 1326}})
    if 'config/upload/' in url:
        return mockRequestObj({"meta": {"code": 200}, 
                               "response": {"test_id": "test_test_id", 
                                            "config_id": 23456, 
                                            "conf_file": "appurify.conf"}})
    if 'tests/run' in url:
        return mockRequestObj({
                                "meta": {
                                    "code": 200
                                },
                                "response": {
                                    "id": 16282,
                                    "test_type": "uiautomation",
                                    "device_type": {
                                        "device_type_id": 58,
                                        "name": "5_NR",
                                        "battery": False,
                                        "brand": "iPhone",
                                        "os_name": "iOS",
                                        "os_version": "6.1.2",
                                        "has_available_device": None,
                                        "carrier": None,
                                        "available_devices_count": None,
                                        "busy_devices_count": None,
                                        "all_devices_count": None,
                                        "is_rooted": False,
                                        "is_api": True,
                                        "is_manual": False
                                    },
                                    "request_time": "2013-09-11T22:35:18.724Z",
                                    "start_time": None,
                                    "end_time": None,
                                    "all_pass": False,
                                    "run_id": "test_test_run_id",
                                    "nbr_pass": None,
                                    "nbr_fail": None,
                                    "queued": True,
                                    "app": 17967,
                                    "version": {
                                        "id": 17967,
                                        "app": 7735,
                                        "uploaded_on": "2013-09-11T22:35:18Z",
                                        "description": None,
                                        "size": 197072,
                                        "icon_url": "/api/app/icon/?app_id=c5f361ebed16488dbf6b69be54f03e2c",
                                        "app_id": "c5f361ebed16488dbf6b69be54f03e2c",
                                        "app_type": "ios",
                                        "web_app_url": None
                                    },
                                    "app_name": "use-bdd",
                                    "device": "58 - iPhone 5_NR / iOS 6.1.2",
                                    "source": 16177,
                                    "config": {
                                        "id": 1963,
                                        "device": {
                                            "id": 123,
                                            "profiler": True,
                                            "videocapture": True,
                                            "import_photos": False,
                                            "import_contacts": False,
                                            "latitude": "37.777363",
                                            "longitude": "-122.395894",
                                            "packet_capture": True,
                                            "free_memory": None,
                                            "orientation": None,
                                            "network": None
                                        },
                                        "framework": "{\"uiautomation\": {\"template\": \"Memory_Profiling_Template\"}}",
                                        "test_timeout": 240,
                                        "debug": False,
                                        "keep_vm": False,
                                        "device_types": [],
                                        "vm_size": "small"
                                    },
                                    "status": "queueing",
                                    "test_id": "test_test_id",
                                    "app_id": "test_app_id",
                                    "test_run_id": "test_test_run_id",
                                    "queue_timeout_limit": 2
                                }
                            })

def mockRequestPostMulti(url, data, files=None, verify=False, headers={'User-Agent': 'MockAgent'}):
    if 'tests/run' in url:
        return mockRequestObj({
            "meta": {
                "code": 200
            },
            "response": {
                "test_run_id": "test_test_run_id1,test_test_run_id2",
                "test_id": "test_test_id",
                "test_runs": [
                    {
                        "id": 16290,
                        "test_type": "uiautomation",
                        "device_type": {
                            "device_type_id": 58,
                            "name": "5_NR",
                            "battery": False,
                            "brand": "iPhone",
                            "os_name": "iOS",
                            "os_version": "6.1.2",
                            "has_available_device": None,
                            "carrier": None,
                            "available_devices_count": None,
                            "busy_devices_count": None,
                            "all_devices_count": None,
                            "is_rooted": False,
                            "is_api": True,
                            "is_manual": False
                        },
                        "request_time": "2013-09-12T22:01:48.594Z",
                        "start_time": None,
                        "end_time": None,
                        "all_pass": False,
                        "run_id": "test_test_run_id1",
                        "nbr_pass": None,
                        "nbr_fail": None,
                        "queued": True,
                        "app": 17975,
                        "version": {
                            "id": 17975,
                            "app": 7735,
                            "uploaded_on": "2013-09-12T21:59:07Z",
                            "description": None,
                            "size": 197072,
                            "icon_url": "/api/app/icon/?app_id=4858befdd9304984a171837c612746eb",
                            "app_id": "test_app_id",
                            "app_type": "ios",
                            "web_app_url": None
                        },
                        "app_name": "use-bdd",
                        "device": "58 - iPhone 5_NR / iOS 6.1.2",
                        "source": 16185,
                        "config": {
                            "id": 1971,
                            "device": {
                                "id": 123,
                                "profiler": True,
                                "videocapture": True,
                                "import_photos": False,
                                "import_contacts": False,
                                "latitude": "37.777363",
                                "longitude": "-122.395894",
                                "packet_capture": True,
                                "free_memory": None,
                                "orientation": None,
                                "network": None
                            },
                            "framework": "{\"uiautomation\": {\"template\": \"Memory_Profiling_Template\"}}",
                            "test_timeout": 240,
                            "debug": False,
                            "keep_vm": False,
                            "device_types": [],
                            "vm_size": "small",
                            "raw": "[uiautomation]\ntemplate=Memory_Profiling_Template\n\n[appurify]\nprofiler=1\npcap=1\nlatlng=37.777363,-122.395894\n\n"
                        },
                        "status": "queueing",
                        "test_id": "test_test_id",
                        "app_id": "test_app_id",
                        "test_run_id": "test_test_run_id1",
                        "device_type_id": 58,
                        "queue_timeout_limit": 2,
                    },
                    {
                        "id": 16291,
                        "test_type": "uiautomation",
                        "device_type": {
                            "device_type_id": 61,
                            "name": "5_NR",
                            "battery": False,
                            "brand": "iPhone",
                            "os_name": "iOS",
                            "os_version": "6.0.2",
                            "has_available_device": None,
                            "carrier": None,
                            "available_devices_count": None,
                            "busy_devices_count": None,
                            "all_devices_count": None,
                            "is_rooted": False,
                            "is_api": True,
                            "is_manual": False
                        },
                        "request_time": "2013-09-12T22:01:48.614Z",
                        "start_time": None,
                        "end_time": None,
                        "all_pass": False,
                        "run_id": "test_test_run_id2",
                        "nbr_pass": None,
                        "nbr_fail": None,
                        "queued": True,
                        "app": 17975,
                        "version": {
                            "id": 17975,
                            "app": 7735,
                            "uploaded_on": "2013-09-12T21:59:07Z",
                            "description": None,
                            "size": 197072,
                            "icon_url": "/api/app/icon/?app_id=4858befdd9304984a171837c612746eb",
                            "app_id": "test_app_id",
                            "app_type": "ios",
                            "web_app_url": None
                        },
                        "app_name": "use-bdd",
                        "device": "61 - iPhone 5_NR / iOS 6.0.2",
                        "source": 16185,
                        "config": {
                            "id": 1971,
                            "device": {
                                "id": 234,
                                "profiler": True,
                                "videocapture": True,
                                "import_photos": False,
                                "import_contacts": False,
                                "latitude": "37.777363",
                                "longitude": "-122.395894",
                                "packet_capture": True,
                                "free_memory": None,
                                "orientation": None,
                                "network": None
                            },
                            "framework": "{\"uiautomation\": {\"template\": \"Memory_Profiling_Template\"}}",
                            "test_timeout": 240,
                            "debug": False,
                            "keep_vm": False,
                            "device_types": [],
                            "vm_size": "small",
                            "raw": "[uiautomation]\ntemplate=Memory_Profiling_Template\n\n[appurify]\nprofiler=1\npcap=1\nlatlng=37.777363,-122.395894\n\n"
                        },
                        "status": "queueing",
                        "test_id": "test_test_id",
                        "app_id": "test_app_id",
                        "test_run_id": "test_test_run_id2",
                        "device_type_id": 61,
                        "queue_timeout_limit": 2,
                    }
                ],
                "app_id": "test_app_id",
            }
        })
    else:
        raise Exception("Unrecognized url")

def mockRequestGet(url, params, verify=False, headers={'User-Agent': 'MockUserAgent'}):
    if 'tests/check' in url:
        if mockRequestGet.count <= 0:
            mockRequestGet.count = mockRequestGet.count + 1
            return mockRequestObj({"meta": {"code": 200}, 
                                   "response": {"status": "in-progress", 
                                                "test_run_id": "test_test_run_id", 
                                                "test_config": "[uiautomation]\n\n[appurify]\nprofiler=1\npcap=1\n", 
                                                "device_type": "58 - iPhone 5_NR / iOS 6.1.2", 
                                                "device_type_id": 58}})
        elif mockRequestGet.exception:
            mockRequestGet.count = mockRequestGet.count + 1
            return mockRequestObj({"meta": {"code": 200}, 
                                   "response": {"status": "complete", 
                                                "detailed_status": "exception", 
                                                "results": {"exception": "-9999: Other exception", 
                                                            "errors": None, 
                                                            "url": "http://localhost/resource/tests/result/?run_id=dummy_test_run_id", 
                                                            "number_passes": mockRequestGet.passes, 
                                                            "number_fails": mockRequestGet.fails, 
                                                            "pass": mockRequestGet.pass_val, 
                                                            "output": ""}, 
                                                "test_run_id": "test_test_run_id", 
                                                "device_type": "58 - iPhone 5_NR / iOS 6.1.2",
                                                "device_type_id": 58}})
        else:
            mockRequestGet.count = mockRequestGet.count + 1
            return mockRequestObj({"meta": {"code": 200}, 
                                   "response": {"status": "complete", 
                                                "test_config": "[test_type]\nconfig", 
                                                "results": {"exception": None, 
                                                            "errors": "", 
                                                            "url": "http://localhost/resource/tests/result/?run_id=dummy_test_run_id", 
                                                            "number_passes": mockRequestGet.passes,
                                                            "number_fails": mockRequestGet.fails,
                                                            "pass": mockRequestGet.pass_val, 
                                                            "output": "test_run_output"}, 
                                                "test_run_id": "test_test_run_id", 
                                                "device_type": "58 - iPhone 5_NR / iOS 6.1.2", 
                                                "device_type_id": 58}})
    elif 'devices/list' in url:
        return mockRequestObj({"meta": {"code": 200},
                                "response": [{"device_type_id": 137, "name": "5", "battery":False, "brand": "iPhone", "os_name": "iOS", "os_version": "7.0.4", "has_available_device":True, "available_devices_count": 1, "busy_devices_count": 0, "all_devices_count": 1, "is_rooted":False, "is_api":True, "is_manual":False, "device_family": "ios"}, 
                                             {"device_type_id": 223, "name": "G Flex", "battery":False, "brand": "LG", "os_name": "Android", "os_version": "4.2.2", "has_available_device":True, "available_devices_count": 1, "busy_devices_count": 0, "all_devices_count": 1, "is_rooted":False, "is_api":True, "is_manual":False, "device_family": "android"}]})
mockRequestGet.count = 0
mockRequestGet.passes = 1
mockRequestGet.fails = 1
mockRequestGet.exception = 0
mockRequestGet.pass_val = False

def mockRequestGetPrimaryException(url, params, verify=False, headers={'User-Agent': 'MockUserAgent'}):
    raise Exception("Mock Syntax Error")

class TestAuth(unittest.TestCase):
    def setUp(self):
        self.client = AppurifyClient(api_key="test_key", api_secret="test_secret")

    @mock.patch("requests.post", mockRequestPost)
    def testGetAccessToken(self):
        client = AppurifyClient(api_key="test_key", api_secret="test_secret")
        client.refreshAccessToken()
        access_token = client.access_token
        self.assertEqual(access_token, "test_access_token", "Should return proper access token on post")

    def testGetAccessTokenPrePop(self):
        client = AppurifyClient(access_token="Already_Set")
        client.refreshAccessToken()
        access_token = client.access_token
        self.assertEqual(access_token, "Already_Set", "Should return access token when one is provided")

    def testNoAuth(self):
        client = AppurifyClient()
        with self.assertRaises(AppurifyClientError):
            """ Should error out on no auth data """
            client.refreshAccessToken()

class TestUpload(unittest.TestCase):

    @mock.patch("requests.post", mockRequestPost)
    def testUploadAppNoSource(self):
        client = AppurifyClient(access_token="authenticated", test_type='ios_webrobot')
        app_id = client.uploadApp()
        self.assertEqual(app_id, "test_app_id", "Should properly fetch web robot for app id")

    @mock.patch("requests.post", mockRequestPost)
    @mock.patch("requests.get", mockRequestGet)
    def testUploadAppSource(self):
        client = AppurifyClient(access_token="authenticated", app_src=__file__, app_src_type='raw', test_type='calabash', name="test_name", device_type_id="137")
        app_id = client.uploadApp()
        self.assertEqual(app_id, "test_app_id", "Should properly fetch web robot for app id")

    @mock.patch("requests.post", mockRequestPost)
    def testUploadAppNoSourceError(self):
        client = AppurifyClient(access_token="authenticated", app_src_type='raw', test_type='calabash')
        with self.assertRaises(AppurifyClientError):
            client.uploadApp()

    @mock.patch("requests.post", mockRequestPost)
    def testUploadTestNoSource(self):
        client = AppurifyClient(access_token="authenticated", test_type='ios_webrobot')
        app_id = client.uploadTest('test_app_id')
        self.assertEqual(app_id, "test_test_id", "Should properly fetch web robot for app id")

    @mock.patch("requests.post", mockRequestPost)
    def testUploadTest(self):
        client = AppurifyClient(access_token="authenticated", test_src=__file__, test_type="uiautomation", test_src_type='raw')
        test_id = client.uploadTest('test_app_id')
        self.assertEqual(test_id, "test_test_id", "Should properly fetch web robot for app id")

    @mock.patch("requests.post", mockRequestPost)
    def testUploadTestNoSourceError(self):
        client = AppurifyClient(access_token="authenticated", test_type='uiautomation')
        with self.assertRaises(AppurifyClientError):
            app_id = client.uploadTest('test_app_id')

    @mock.patch("requests.post", mockRequestPost)
    def testUploadConfig(self):
        client = AppurifyClient(access_token="authenticated", test_type="ios_webrobot")
        config_id = client.uploadConfig("test_id", config_src=__file__)
        self.assertEqual(config_id, 23456, "Should properly fetch uploaded config id")

    def testPrintConfig(self):
        client = AppurifyClient(access_token="authenticated", test_type="ios_webrobot")
        config = [{
                                        "id": 1963,
                                        "device": {
                                            "id": 123,
                                            "profiler": True,
                                            "videocapture": True,
                                        },
                                        "framework": "{\"uiautomation\": {\"template\": \"Memory_Profiling_Template\"}}",
                                        "test_timeout": 240,
                                        "debug": False,
                                        "keep_vm": False,
                                        "device_types": [],
                                        "vm_size": "small"
                    }]
        client.printConfigs(config)

class TestRun(unittest.TestCase):

    @mock.patch("requests.post", mockRequestPost)
    def testRunTestSingle(self):
        client = AppurifyClient(access_token="authenticated")
        test_run_id, queue_timeout_limit, configs = client.runTest("app_id", "test_test_id")
        self.assertEqual(test_run_id, "test_test_run_id", "Should get test_run_id when executing run")
        self.assertEqual(len(configs), 1, "Should get config back for test run")
        self.assertEqual(configs[0]['device']['id'], 123, "Sanity check parameters")

    @mock.patch("requests.post", mockRequestPostMulti)
    def testRunTestMulti(self):
        client = AppurifyClient(access_token="authenticated")
        test_run_id, queue_timeout_limit, configs = client.runTest("app_id", "test_test_id")
        self.assertEqual(test_run_id, "test_test_run_id1,test_test_run_id2", "Should get test_run_ids when executing run")
        self.assertEqual(len(configs), 2, "Should get config back for test run")
        self.assertEqual(configs[0]['device']['id'], 123, "Sanity check parameters")

    @mock.patch("requests.get", mockRequestGet)
    def testPollTestResult(self):
        mockRequestGet.count = 0
        client = AppurifyClient(access_token="authenticated", timeout_sec=2, poll_every=0.1)
        test_status_response = client.pollTestResult("test_test_run_id", 2)
        self.assertEqual(test_status_response['status'], "complete", "Should poll until complete")

    @mock.patch("requests.post", mockRequestPost)
    @mock.patch("requests.get", mockRequestGet)
    def testMainServerException(self):
        mockRequestGet.count = 0
        mockRequestGet.passes = 0
        mockRequestGet.fails = 0
        mockRequestGet.exception = 1
        mockRequestGet.pass_val = False
        client = AppurifyClient(api_key="test_key", api_secret="test_secret", test_type="uiautomation", 
                                app_src=__file__, app_src_type='raw', 
                                test_src=__file__, test_src_type='raw',
                                timeout_sec=2, poll_every=0.1, device_type_id="137")
        result_code = client.main()
        self.assertEqual(result_code, EXIT_CODE_OTHER_EXCEPTION, "Main should execute and return exception code")

    @mock.patch("requests.post", mockRequestPost)
    @mock.patch("requests.get", mockRequestGet)
    def testMainFail(self):
        mockRequestGet.count = 0
        mockRequestGet.passes = 1
        mockRequestGet.fails = 1
        mockRequestGet.exception = 0
        mockRequestGet.pass_val = False
        client = AppurifyClient(api_key="test_key", api_secret="test_secret", test_type="uiautomation", 
                                app_src=__file__, app_src_type='raw', 
                                test_src=__file__, test_src_type='raw',
                                timeout_sec=2, poll_every=0.1, device_type_id="137")
        result_code = client.main()
        self.assertEqual(result_code, 1, "Main should execute and return fail code")

    @mock.patch("requests.post", mockRequestPost)
    @mock.patch("requests.get", mockRequestGet)
    def testMainPass(self):
        mockRequestGet.count = 0
        mockRequestGet.passes = 2
        mockRequestGet.fails = 0
        mockRequestGet.exception = 0
        mockRequestGet.pass_val = True
        client = AppurifyClient(api_key="test_key", api_secret="test_secret", test_type="uiautomation", 
                                app_src=__file__, app_src_type='raw', 
                                test_src=__file__, test_src_type='raw',
                                timeout_sec=2, poll_every=0.1, device_type_id="137")
        result_code = client.main()
        self.assertEqual(result_code, 0, "Main should execute and return pass code")

    @mock.patch("requests.post", mockRequestPost)
    @mock.patch("requests.get", mockRequestGet)
    def testMainPassUrl(self):
        mockRequestGet.count = 0
        mockRequestGet.passes = 2
        mockRequestGet.fails = 0
        mockRequestGet.exception = 0
        mockRequestGet.pass_val = True
        client = AppurifyClient(api_key="test_key", api_secret="test_secret", test_type="ios_webrobot", 
                                app_src=None, 
                                test_src=None,
                                url="www.yahoo.com",
                                timeout_sec=2, poll_every=0.1, device_type_id="137")
        result_code = client.main()
        self.assertEqual(result_code, 0, "Main should execute and return pass code")

    @mock.patch("requests.get", mockRequestGet)
    def testDefaultPollTimeout(self):
        old_env = os.environ.get('APPURIFY_API_TIMEOUT', None)
        try:
            os.environ['APPURIFY_API_TIMEOUT'] = '0.2'
            mockRequestGet.count = -20
            client = AppurifyClient(access_token="authenticated",  poll_every=0.1)
            with self.assertRaises(AppurifyClientError):
                client.pollTestResult("test_test_run_id", 0.2)
        finally:
            if old_env:
                os.environ['APPURIFY_API_TIMEOUT'] = str(old_env)

    @mock.patch("requests.post", mockRequestPost)
    @mock.patch("requests.get", mockRequestGet)
    def testDefaultPollTimeoutCode(self):
        old_env = os.environ.get('APPURIFY_API_TIMEOUT', None)
        try:
            os.environ['APPURIFY_API_TIMEOUT'] = '0.2'
            mockRequestGet.count = -20
            client = AppurifyClient(api_key="test_key", api_secret="test_secret", test_type="ios_webrobot", 
                            app_src=None, 
                            test_src=None,
                            url="www.yahoo.com",
                            poll_every=0.1,
                            device_type_id="137")
            result_code = client.main()
            self.assertEqual(result_code, 3, "Main should execute and return error code with default timeout")
        finally:
            if old_env:
                os.environ['APPURIFY_API_TIMEOUT'] = str(old_env)

    @mock.patch("requests.get", mockRequestGet)
    def testPollTimeout(self):
        mockRequestGet.count = -20
        client = AppurifyClient(access_token="authenticated", timeout_sec=0.2, poll_every=0.1, device_type_id="137")
        with self.assertRaises(AppurifyClientError):
            client.pollTestResult("test_test_run_id", 0.2)

    @mock.patch("requests.post", mockRequestPost)
    @mock.patch("requests.get", mockRequestGet)
    def testPollTimeoutCode(self):
        mockRequestGet.count = -20
        client = AppurifyClient(api_key="test_key", api_secret="test_secret", test_type="ios_webrobot", 
            app_src=None, 
            test_src=None,
            url="www.yahoo.com",
            timeout_sec=0.2,
            poll_every=0.1,
            device_type_id="137")
        result_code = client.main()
        self.assertEqual(result_code, 3, "Main should execute and return error code")

    @mock.patch("requests.post", mockRequestPost)
    @mock.patch("requests.get", mockRequestGet)
    def testGetExceptionExitCode(self):
        mockRequestGet.count = -20
        
        client = AppurifyClient(access_token="authenticated", timeout_sec=0.2, poll_every=0.1, device_type_id="137")
        self.assertEqual(client.getExceptionExitCode([{"exception": "4007: Error installing the app: file does not contain AndroidManifest.xml\n (1)"}]), EXIT_CODE_APP_INSTALL_FAILED, "Should return correct exit code for matching exception")
        self.assertEqual(client.getExceptionExitCode([{"exception": "-9999: no match anything"}]), EXIT_CODE_OTHER_EXCEPTION, "Should return correct exit code for no exception")