"""JUnit XML report generator for PyOsmo test execution."""

import xml.etree.ElementTree as ET
from xml.dom import minidom

from pyosmo.reporting import Reporter


class JUnitReporter(Reporter):
    """Generate JUnit XML report for CI/CD integration.

    The JUnit XML format is widely supported by CI/CD systems
    (Jenkins, GitLab CI, GitHub Actions, etc.) for test result visualization.
    """

    def generate(self) -> str:
        """Generate JUnit XML report.

        Returns:
            JUnit XML-formatted report as a string
        """
        # Create root test suites element
        testsuites = ET.Element("testsuites")
        testsuites.set("name", self.config.title)
        testsuites.set("tests", str(self.history.test_case_count))
        testsuites.set("failures", str(self.history.error_count))
        testsuites.set("errors", "0")
        testsuites.set("time", str(self.history.duration.total_seconds()))

        # Create a test suite for all test cases
        testsuite = ET.SubElement(testsuites, "testsuite")
        testsuite.set("name", "PyOsmo Test Suite")
        testsuite.set("tests", str(self.history.test_case_count))
        testsuite.set("failures", str(self.history.error_count))
        testsuite.set("errors", "0")
        testsuite.set("time", str(self.history.duration.total_seconds()))
        testsuite.set("timestamp", self.history.start_time.isoformat())

        # Add each test case
        for idx, tc in enumerate(self.history.test_cases, start=1):
            testcase = ET.SubElement(testsuite, "testcase")
            testcase.set("classname", "PyOsmo")
            testcase.set("name", f"TestCase_{idx}")
            testcase.set("time", str(tc.duration.total_seconds()))

            # Add step information as system-out
            steps_info = []
            for step_log in tc.steps_log:
                steps_info.append(
                    f"{step_log.timestamp.strftime('%H:%M:%S.%f')[:-3]} - "
                    f"{step_log.name} ({step_log.duration.total_seconds():.3f}s)"
                )

            if steps_info:
                system_out = ET.SubElement(testcase, "system-out")
                system_out.text = "\n".join(steps_info)

            # Add failures if any
            failure_messages = []
            for step_log in tc.steps_log:
                if step_log.error:
                    failure = ET.SubElement(testcase, "failure")
                    failure.set("message", str(step_log.error))
                    failure.set("type", type(step_log.error).__name__)
                    failure.text = f"Step '{step_log.name}' failed: {step_log.error}"
                    failure_messages.append(f"Step '{step_log.name}': {step_log.error}")

            # Add error summary if there were failures
            if failure_messages:
                system_err = ET.SubElement(testcase, "system-err")
                system_err.text = "\n".join(failure_messages)

        # Convert to pretty-printed XML string
        xml_str = ET.tostring(testsuites, encoding="unicode")
        dom = minidom.parseString(xml_str)
        return dom.toprettyxml(indent="  ")
