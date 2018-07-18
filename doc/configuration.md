# Configuring test generation
Test generation can be configured using an OsmoConfig object that is
available in [config.py](pyosmo/config.py). This object is initialized
as a part of the Osmo object under attribute config. If you want to
configure test generation, you cana either access
the configuration through this object, create your own and replace
the config object or use the api:s available in the Osmo object.

## Available configuration
The OsmoConfig object contains the following configuration values:

### stop_on_fail
Boolean. If set to True (default), test suite generation will stop after
a test that had a failed step has finished. Set to False to continue
test generation until the end of the test suite has been reached.

### stop_test_on_exception
Boolean. If set to True (default), a test will stop if a step
raises an exception. If set to False, other steps in the test will
still be run if a step raises an exception.

### algorithm
The algorithm used for test generation. Default is RandomAlgorithm.

### tests_in_a_suite
Integer. Set how many tests will be generated/run in a suite.

### steps_in_a_test
Integer. Set how many steps will be generated into a single test.

## APIs in Osmo
The Osmo object contains the following apis to access the configuration
object directly:

### config
Gets the OsmoConfig object. If set to a new OsmoConfig object, linking
stop_on_fail, stop_test_on_exception, tests_in_a_suite
and steps_in_a_test is done automatically in the setter.

### stop_on_fail
Set the stop_on_fail configuration value.

### stop_test_on_exception
Set the stop_test_on_exception configuration value.

### set_algorithm
Attribute that points to the algorithm object in the configuration

### tests_in_a_suite
Integer. Set how many tests will be generated/run in a suite.

### steps_in_a_test
Integer. Set how many steps will be generated into a single test.
