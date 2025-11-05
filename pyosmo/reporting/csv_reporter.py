"""CSV report generator for PyOsmo test execution."""

import csv
import io

from pyosmo.reporting import Reporter


class CSVReporter(Reporter):
    """Generate CSV report suitable for data analysis.

    The CSV format provides tabular data that can be imported into
    spreadsheets, databases, or analysis tools like pandas, Excel, etc.
    """

    def generate(self) -> str:
        """Generate CSV report.

        Returns:
            CSV-formatted report as a string with step execution data
        """
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            "test_case_id",
            "step_index",
            "step_name",
            "timestamp",
            "duration_seconds",
            "has_error",
            "error_type",
            "error_message",
        ])

        # Write data rows
        for test_idx, tc in enumerate(self.history.test_cases, start=1):
            for step_idx, step_log in enumerate(tc.steps_log, start=1):
                writer.writerow([
                    test_idx,
                    step_idx,
                    step_log.name,
                    step_log.timestamp.isoformat(),
                    step_log.duration.total_seconds(),
                    "Yes" if step_log.error else "No",
                    type(step_log.error).__name__ if step_log.error else "",
                    str(step_log.error) if step_log.error else "",
                ])

        return output.getvalue()


class CSVSummaryReporter(Reporter):
    """Generate CSV summary report with aggregated statistics.

    This reporter provides a summary view with step frequency
    and execution time statistics.
    """

    def generate(self) -> str:
        """Generate CSV summary report.

        Returns:
            CSV-formatted summary report as a string
        """
        stats = self.history.statistics()
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            "step_name",
            "execution_count",
            "avg_duration_seconds",
            "total_duration_seconds",
        ])

        # Calculate total durations
        step_total_times = {}
        for test_case in self.history.test_cases:
            for step_log in test_case.steps_log:
                if step_log.name not in step_total_times:
                    step_total_times[step_log.name] = 0.0
                step_total_times[step_log.name] += step_log.duration.total_seconds()

        # Write data rows sorted by execution count (descending)
        for step_name, count in sorted(
            stats.step_frequency.items(), key=lambda x: x[1], reverse=True
        ):
            avg_time = stats.step_execution_times.get(step_name, 0.0)
            total_time = step_total_times.get(step_name, 0.0)

            writer.writerow([
                step_name,
                count,
                avg_time,
                total_time,
            ])

        return output.getvalue()
