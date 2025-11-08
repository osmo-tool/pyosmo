"""Structured statistics for OSMO test execution"""

from dataclasses import dataclass
from datetime import timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyosmo.history.history import OsmoHistory


@dataclass
class OsmoStatistics:
    """Structured statistics from test execution.

    Provides programmatic access to test statistics instead of formatted strings.
    """

    total_steps: int
    """Total number of steps executed across all tests"""

    unique_steps: int
    """Number of unique steps executed"""

    total_tests: int
    """Total number of test cases executed"""

    duration: timedelta
    """Total duration of test execution"""

    error_count: int
    """Total number of errors encountered"""

    most_executed_step: str | None
    """Name of the most frequently executed step"""

    least_executed_step: str | None
    """Name of the least frequently executed step"""

    average_steps_per_test: float
    """Average number of steps per test case"""

    step_frequency: dict[str, int]
    """Execution frequency of each step"""

    step_execution_times: dict[str, float]
    """Average execution time for each step (in seconds)"""

    @classmethod
    def from_history(cls, history: 'OsmoHistory') -> 'OsmoStatistics':
        """Create statistics from history.

        Args:
            history: Test execution history

        Returns:
            Structured statistics
        """
        from collections import defaultdict

        # Collect step frequency and execution times
        step_frequency: dict[str, int] = defaultdict(int)
        step_times: dict[str, list[float]] = defaultdict(list)

        for test_case in history.test_cases:
            for step_log in test_case.steps_log:
                step_frequency[step_log.name] += 1
                step_times[step_log.name].append(step_log.duration.total_seconds())

        # Calculate average execution times
        step_execution_times = {step_name: sum(times) / len(times) for step_name, times in step_times.items()}

        # Find most and least executed steps
        most_executed = max(step_frequency.items(), key=lambda x: x[1])[0] if step_frequency else None
        least_executed = min(step_frequency.items(), key=lambda x: x[1])[0] if step_frequency else None

        return cls(
            total_steps=history.total_amount_of_steps,
            unique_steps=len(step_frequency),
            total_tests=history.test_case_count,
            duration=history.duration,
            error_count=history.error_count,
            most_executed_step=most_executed,
            least_executed_step=least_executed,
            average_steps_per_test=history.total_amount_of_steps / history.test_case_count
            if history.test_case_count > 0
            else 0.0,
            step_frequency=dict(step_frequency),
            step_execution_times=step_execution_times,
        )

    def to_dict(self) -> dict[str, object]:
        """Convert statistics to dictionary for serialization.

        Returns:
            Dictionary representation of statistics
        """
        return {
            'total_steps': self.total_steps,
            'unique_steps': self.unique_steps,
            'total_tests': self.total_tests,
            'duration_seconds': self.duration.total_seconds(),
            'error_count': self.error_count,
            'most_executed_step': self.most_executed_step,
            'least_executed_step': self.least_executed_step,
            'average_steps_per_test': self.average_steps_per_test,
            'step_frequency': self.step_frequency,
            'step_execution_times': self.step_execution_times,
        }

    def __str__(self) -> str:
        """Formatted string representation of statistics."""
        lines = [
            'Test Execution Statistics:',
            f'  Total Tests: {self.total_tests}',
            f'  Total Steps: {self.total_steps}',
            f'  Unique Steps: {self.unique_steps}',
            f'  Duration: {self.duration}',
            f'  Errors: {self.error_count}',
            f'  Avg Steps/Test: {self.average_steps_per_test:.2f}',
        ]

        if self.most_executed_step:
            lines.append(
                f'  Most Executed: {self.most_executed_step} ({self.step_frequency[self.most_executed_step]} times)'
            )

        if self.least_executed_step:
            lines.append(
                f'  Least Executed: {self.least_executed_step} ({self.step_frequency[self.least_executed_step]} times)'
            )

        return '\n'.join(lines)
