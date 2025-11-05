"""JSON report generator for PyOsmo test execution."""

import json
from typing import Any, Dict, List

from pyosmo.reporting import Reporter


class JSONReporter(Reporter):
    """Generate JSON report with complete test execution data.

    The JSON format provides programmatic access to all test data
    and is suitable for integration with external analysis tools.
    """

    def generate(self) -> str:
        """Generate JSON report.

        Returns:
            JSON-formatted report as a string
        """
        data = self.to_dict()
        return json.dumps(data, indent=2, default=str)

    def to_dict(self) -> Dict[str, Any]:
        """Convert history to dictionary for JSON serialization.

        Returns:
            Dictionary representation of test execution history
        """
        # Get statistics
        stats = self.history.statistics()

        # Build test case data
        test_cases = []
        for idx, tc in enumerate(self.history.test_cases, start=1):
            test_case_data = {
                "id": idx,
                "duration_seconds": tc.duration.total_seconds(),
                "step_count": len(tc.steps_log),
                "error_count": tc.error_count,
                "steps": [],
            }

            for step_log in tc.steps_log:
                step_data = {
                    "name": step_log.name,
                    "timestamp": step_log.timestamp.isoformat(),
                    "duration_seconds": step_log.duration.total_seconds(),
                    "has_error": step_log.error is not None,
                }
                if step_log.error:
                    step_data["error_message"] = str(step_log.error)
                    step_data["error_type"] = type(step_log.error).__name__

                test_case_data["steps"].append(step_data)

            test_cases.append(test_case_data)

        # Build step pairs data
        step_pairs_list = [
            {"from_step": pair[0], "to_step": pair[1], "count": count}
            for pair, count in self.history.step_pairs().items()
        ]

        # Build coverage timeline
        coverage_timeline = [
            {"step_index": idx, "unique_steps_covered": count}
            for idx, count in self.history.coverage_timeline()
        ]

        # Assemble complete report
        return {
            "config": {
                "title": self.config.title,
            },
            "summary": {
                "total_tests": stats.total_tests,
                "total_steps": stats.total_steps,
                "unique_steps": stats.unique_steps,
                "duration_seconds": stats.duration.total_seconds(),
                "error_count": stats.error_count,
                "average_steps_per_test": stats.average_steps_per_test,
                "start_time": self.history.start_time.isoformat(),
                "stop_time": self.history.stop_time.isoformat() if self.history.stop_time else None,
            },
            "statistics": {
                "most_executed_step": stats.most_executed_step,
                "least_executed_step": stats.least_executed_step,
                "step_frequency": stats.step_frequency,
                "step_execution_times": stats.step_execution_times,
            },
            "coverage": {
                "step_pairs": step_pairs_list,
                "timeline": coverage_timeline,
            },
            "test_cases": test_cases,
        }
