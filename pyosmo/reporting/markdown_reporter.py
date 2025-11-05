"""Markdown report generator for PyOsmo test execution."""

from pyosmo.reporting import Reporter


class MarkdownReporter(Reporter):
    """Generate Markdown report suitable for documentation.

    The Markdown format is human-readable and can be included
    in documentation systems, README files, or version control.
    """

    def generate(self) -> str:
        """Generate Markdown report.

        Returns:
            Markdown-formatted report as a string
        """
        stats = self.history.statistics()
        lines = []

        # Title
        lines.append(f"# {self.config.title}\n")

        # Summary Section
        lines.append("## Summary\n")
        lines.append(f"- **Total Tests**: {stats.total_tests}")
        lines.append(f"- **Total Steps**: {stats.total_steps}")
        lines.append(f"- **Unique Steps**: {stats.unique_steps}")
        lines.append(f"- **Duration**: {stats.duration}")
        lines.append(f"- **Errors**: {stats.error_count}")
        lines.append(f"- **Average Steps per Test**: {stats.average_steps_per_test:.2f}\n")

        if self.config.include_statistics:
            # Step Frequency Table
            lines.append("## Step Execution Frequency\n")
            lines.append("| Step Name | Execution Count | Avg Duration (s) |")
            lines.append("|-----------|-----------------|------------------|")

            for step_name, count in sorted(
                stats.step_frequency.items(), key=lambda x: x[1], reverse=True
            ):
                avg_time = stats.step_execution_times.get(step_name, 0.0)
                lines.append(f"| {step_name} | {count} | {avg_time:.4f} |")
            lines.append("")

            # Most/Least Executed
            lines.append("## Step Statistics\n")
            if stats.most_executed_step:
                lines.append(
                    f"- **Most Executed**: {stats.most_executed_step} "
                    f"({stats.step_frequency[stats.most_executed_step]} times)"
                )
            if stats.least_executed_step:
                lines.append(
                    f"- **Least Executed**: {stats.least_executed_step} "
                    f"({stats.step_frequency[stats.least_executed_step]} times)"
                )
            lines.append("")

        # Test Cases Section
        if self.config.include_timeline:
            lines.append("## Test Cases\n")
            for idx, tc in enumerate(self.history.test_cases, start=1):
                status = "❌ FAILED" if tc.error_count > 0 else "✅ PASSED"
                lines.append(
                    f"### Test Case {idx} {status}\n"
                )
                lines.append(f"- **Duration**: {tc.duration}")
                lines.append(f"- **Steps**: {len(tc.steps_log)}")
                lines.append(f"- **Errors**: {tc.error_count}\n")

                if tc.error_count > 0:
                    lines.append("**Error Details:**\n")
                    for step_log in tc.steps_log:
                        if step_log.error:
                            lines.append(f"- Step `{step_log.name}`: {step_log.error}\n")

        # Step Pairs (Transitions)
        step_pairs = self.history.step_pairs()
        if step_pairs and self.config.include_statistics:
            lines.append("## Step Transitions\n")
            lines.append("| From Step | To Step | Count |")
            lines.append("|-----------|---------|-------|")

            for (from_step, to_step), count in sorted(
                step_pairs.items(), key=lambda x: x[1], reverse=True
            )[:20]:  # Top 20 transitions
                lines.append(f"| {from_step} | {to_step} | {count} |")
            lines.append("")

        # Failed Tests
        failed_tests = self.history.failed_tests()
        if failed_tests:
            lines.append("## Failed Tests\n")
            for idx, tc in enumerate(failed_tests, start=1):
                test_idx = self.history.test_cases.index(tc) + 1
                lines.append(f"### Failed Test {test_idx}\n")
                lines.append(f"- **Duration**: {tc.duration}")
                lines.append(f"- **Error Count**: {tc.error_count}\n")

                lines.append("**Steps with Errors:**\n")
                for step_log in tc.steps_log:
                    if step_log.error:
                        lines.append(f"- `{step_log.name}` at {step_log.timestamp}")
                        lines.append(f"  - Error: {step_log.error}")
                lines.append("")

        # Metadata footer
        lines.append("---\n")
        lines.append(f"*Report generated from {self.history.start_time.strftime('%Y-%m-%d %H:%M:%S')}*")
        if self.history.stop_time:
            lines.append(f"*to {self.history.stop_time.strftime('%Y-%m-%d %H:%M:%S')}*")

        return "\n".join(lines)
