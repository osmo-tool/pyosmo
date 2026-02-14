import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING

from pyosmo.history.test_case import OsmoTestCaseRecord
from pyosmo.history.test_step_log import TestStepLog
from pyosmo.model import TestStep

if TYPE_CHECKING:
    from pyosmo.history.statistics import OsmoStatistics


class OsmoHistory:
    def __init__(self) -> None:
        self.test_cases: list[OsmoTestCaseRecord] = []
        self.stop_time: datetime | None = None
        self.start_time: datetime = datetime.now()
        # Incremental step counter — avoids O(tc*s) history walks
        self._step_counts: dict[str, int] = {}

    def start_new_test(self) -> None:
        # Stop test case timer
        if self.current_test_case and self.current_test_case.is_running():
            self.current_test_case.stop()
        # Start a new test case
        self.test_cases.append(OsmoTestCaseRecord())

    def stop(self) -> None:
        if self.stop_time:
            return
        if self.current_test_case:
            self.current_test_case.stop()
        self.stop_time = datetime.now()

    def add_step(self, step: TestStep, duration: timedelta, error: Exception | None = None) -> None:
        """Add a step to the history"""
        if self.current_test_case is None:
            raise Exception('There is no active test case!!')
        self.current_test_case.add_step(TestStepLog(step, duration, error))
        self._step_counts[step.name] = self._step_counts.get(step.name, 0) + 1

    def attach(self, name: str, data: str | bytes) -> None:
        """Attach data to the last step of the current test case."""
        if self.current_test_case is None or not self.current_test_case.steps_log:
            raise Exception('No step to attach to!')
        self.current_test_case.steps_log[-1].attach(name, data)

    @property
    def error_count(self) -> int:
        """Total count of errors in all tests cases"""
        return sum(x.error_count for x in self.test_cases)

    @property
    def current_test_case(self) -> OsmoTestCaseRecord | None:
        """The test case which is running or generating at the moment"""
        return self.test_cases[-1] if self.test_cases else None

    @property
    def duration(self) -> timedelta:
        if self.stop_time is None:
            # Test is still running
            return datetime.now() - self.start_time
        return self.stop_time - self.start_time

    @property
    def test_case_count(self) -> int:
        return len(self.test_cases)

    @property
    def total_amount_of_steps(self) -> int:
        return sum(len(tc.steps_log) for tc in self.test_cases)

    def is_used(self, step: TestStep) -> bool:
        """is used at least once"""
        return any(tc.is_used(step) for tc in self.test_cases)

    def get_step_count(self, step: TestStep) -> int:
        """Counts how many times the step is really called during whole history"""
        return self._step_counts.get(step.name, 0)

    @property
    def step_stats(self) -> str:
        stats: dict[str, int] = {}
        ret = ''
        for test_case in self.test_cases:
            for step in test_case.steps_log:
                if step.name in stats:
                    stats[step.name] = stats[step.name] + 1
                else:
                    stats[step.name] = 1
        for key, value in stats.items():
            ret += f'{key}:{value}\n'
        return ret

    def print_summary(self) -> None:
        if self.stop_time is None:
            raise Exception('Cannot get summary of ongoing test')
        ret = '\n'
        ret += 'Osmo run summary:\n'
        ret += f'Test cases: {self.test_case_count}\n'
        ret += f'Test steps: {self.total_amount_of_steps}\n'
        ret += f'Duration: {self.duration}\n'
        print(ret)

    def statistics(self) -> 'OsmoStatistics':
        """Get structured statistics from test execution.

        Returns:
            Structured statistics object with programmatic access
        """
        from pyosmo.history.statistics import OsmoStatistics

        return OsmoStatistics.from_history(self)

    def failed_tests(self) -> list[OsmoTestCaseRecord]:
        """Get list of test cases that had errors.

        Returns:
            List of test case records with errors
        """
        return [tc for tc in self.test_cases if tc.error_count > 0]

    def step_frequency(self) -> dict[str, int]:
        """Get execution frequency of each step.

        Returns:
            Dictionary mapping step name to execution count
        """
        frequency: dict[str, int] = {}
        for test_case in self.test_cases:
            for step in test_case.steps_log:
                frequency[step.name] = frequency.get(step.name, 0) + 1
        return frequency

    def step_pairs(self) -> dict[tuple[str, str], int]:
        """Get execution frequency of step pairs (transitions).

        Returns:
            Dictionary mapping (step_a, step_b) tuples to execution count
        """
        pairs: dict[tuple[str, str], int] = {}
        for test_case in self.test_cases:
            steps = [s.name for s in test_case.steps_log]
            for i in range(len(steps) - 1):
                pair = (steps[i], steps[i + 1])
                pairs[pair] = pairs.get(pair, 0) + 1
        return pairs

    def coverage_timeline(self) -> list[tuple[int, int]]:
        """Get step coverage progression over time.

        Returns:
            List of (step_index, unique_steps_covered) tuples
        """
        seen_steps = set()
        timeline = []
        step_index = 0

        for test_case in self.test_cases:
            for step_log in test_case.steps_log:
                seen_steps.add(step_log.name)
                timeline.append((step_index, len(seen_steps)))
                step_index += 1

        return timeline

    def to_dict(self) -> dict:
        """Serialize history to a dictionary for JSON export.

        Returns:
            Dictionary with statistics, step frequency, step pairs, and per-test details.
        """
        return {
            'statistics': self.statistics().to_dict(),
            'step_frequency': self.step_frequency(),
            'step_pairs': {f'{a} -> {b}': count for (a, b), count in self.step_pairs().items()},
            'test_cases': [
                {
                    'steps': [
                        {
                            'name': step_log.name,
                            'attachments': [
                                {
                                    'name': att_name,
                                    'type': 'bytes' if isinstance(att_data, bytes) else 'str',
                                    'size': len(att_data),
                                }
                                for att_name, att_data in step_log.attachments.items()
                            ],
                        }
                        if step_log.attachments
                        else step_log.name
                        for step_log in tc.steps_log
                    ],
                    'duration_seconds': tc.duration.total_seconds(),
                    'error_count': tc.error_count,
                    'errors': [
                        {'step': step_log.name, 'error': str(step_log.error)}
                        for step_log in tc.steps_log
                        if step_log.error is not None
                    ],
                }
                for tc in self.test_cases
            ],
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize history to a JSON string.

        Args:
            indent: JSON indentation level (default: 2)

        Returns:
            JSON string representation of history
        """
        return json.dumps(self.to_dict(), indent=indent)

    def save_json(self, path: str | Path) -> None:
        """Save history as JSON to a file.

        Args:
            path: File path to write JSON to
        """
        Path(path).write_text(self.to_json())

    def save(self, directory: str | Path) -> None:
        """Save history with attachments to a directory.

        Creates a directory structure with history.json and per-test attachment files:
            directory/
                history.json
                test_0/
                    step_000_screenshot.png
                    step_000_dom.html
                test_1/
                    ...
        """
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)

        for tc_index, tc in enumerate(self.test_cases):
            for step_index, step_log in enumerate(tc.steps_log):
                if not step_log.attachments:
                    continue
                test_dir = directory / f'test_{tc_index}'
                test_dir.mkdir(exist_ok=True)
                for att_name, att_data in step_log.attachments.items():
                    file_path = test_dir / f'step_{step_index:03d}_{att_name}'
                    if isinstance(att_data, bytes):
                        file_path.write_bytes(att_data)
                    else:
                        file_path.write_text(att_data)

        (directory / 'history.json').write_text(self.to_json())

    def __str__(self) -> str:
        ret = ''
        for tc_index, test_case in enumerate(self.test_cases, start=1):
            ret += f'{tc_index}. test case {test_case.duration:.2f}s\n'
            for step in test_case.steps_log:
                ret += f'{step.timestamp} {step.duration:.2f}s {step.name}\n'
            ret += '\n'
        return ret
