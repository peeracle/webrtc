# Appurify Python Client

The official Python client for the [Appurify](http://www.appurify.com) API.

### Installation

```
pip install appurify-0.5.1.tar.gz
```

This will install any missing dependencies and add two executable scripts to your bin folder:

```
$ appurify-client.py -h
$ appurify-tunnel.py -h
```

### Running Tests

```
appurify-client.py --api-key $API_KEY --api-secret $API_SECRET --team $TEAM \
--app-src $APP-SRC --app-test-type $TEST_TYPE --test-src $TEST_SRC --test-type $TEST_TYPE \
--device-type-id $DEVICE_TYPE_IDS --result-dir $RESULT_DIR
```

### Jenkins Integration

In Jenkins create a new Execute Shell build step and upload your app using the Python wrapper as pictured below.

![Jenkins Integration](https://raw.github.com/appurify/appurify-python/master/jenkins.png)

### Exit codes

To facilitate error reporting, the client will report one of the following error codes on exit:

|Code| Meaning |
|----|---------|
| 0  | Test completed with no exceptions or errors |
| 1  | Test completed normally but reported test failures |
| 2  | Test was aborted by the user or system |
| 3  | Test was aborted by the system because of timeout |
| 4  | Test could not be completed because the device could not be activated or reserved |
| 5  | Test could not execute because there was an error in the configuration or uploaded files |
| 6  | Test could not execute because the server rejected the provided credentials|
| 7  | Test could not execute because of other server/remote exception |
| 8  | Test could not execute because of an unexpected error in the client |
| 9  | Test got a connection error attempting to reach the server  |
| 10  | The app could not be installed on the device (possibly due to incorrect build) |
| 11  | Test could not execute because device type is not found in user pool  |
| 12  | Test could not execute because app is not built for device type |
| 13  |  Device doesn't exist in users device pool |
| 14  |  App is not compabtible with device specified. |
| 15  |  Test reached timeout for grid session |

### Contribution

Found a bug or want to add a much needed feature? Go for it and send us the Pull Request!

## Release Notes

### 1.0.0
- Moved tunnel into its own separate repository

### 0.5.1
- Support for teams, using the ```--team``` flag.

### 0.5.0
- Loosen dependency requirements so that future versions of required modules are supported

### 0.4.9
- User-abort now handled smoothly if run has not been uploaded to server and runID not generated.

### 0.4.8
- An app or test source of size 0 will not be allowed nor uploaded to server.

### 0.4.5
- Bug fix of multiple devices trying when downloading results flag passed would fail.

### 0.4.3
- Client will not allow upload of .ipa to android devices
- Client will not allow upload of .apk to iOS devices
- If device type is not in user pool, client will no allow run to upload to server

## 0#.4
- Better handling around client/server connection errors (including SSL cert errors)

### 0.3.4
- Add exit codes

### 0.2.9
- Handle case where test results may not immediately be ready for download after a test completes.

### 0.2.8
- Added ```--version``` flag to print version and exit


### 0.2.6
- Users will receive a warning when attempting to upload a web test without specifying the url parameter.
- Support for both ```--timeout``` parameter to specify the desired timeout at runtime, or using the os environment variable ```APPURIFY_API_TIMEOUT```. Specify desired timeout in seconds.

### 0.2.2

- Added ```ios_sencharobot``` test type

### 0.2.1

- ```network_headers``` test type no longer requires app source
- Fixed an issue where test results were not properly downloaded despite setting the ```result-dir``` parameter.
- Test source is now optional for ```kif``` test type
- Improved test status information when polling a running test
- Configuration values are now printed when running a test
- Fixed a bug where ``name``` parameter was not respected for web apps
