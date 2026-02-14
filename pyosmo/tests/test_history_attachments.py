"""Tests for history attachments and multi-run flakiness analysis."""

import json

from pyosmo import Osmo
from pyosmo.end_conditions import Length
from pyosmo.error_strategy import AlwaysIgnore
from pyosmo.history.history import OsmoHistory
from pyosmo.history.test_step_log import TestStepLog
from pyosmo.model import TestStep


class SimpleModel:
    def __init__(self):
        self.count = 0

    def step_one(self):
        self.count += 1

    def step_two(self):
        self.count += 1


class AttachingModel:
    """Model that attaches data via osmo_history."""

    def __init__(self):
        self.count = 0
        self.osmo_history: OsmoHistory = None  # injected by Osmo

    def step_action(self):
        self.count += 1

    def after(self):
        self.osmo_history.attach('note', f'after step {self.count}')


class FlakyModel:
    """Model that fails intermittently based on a counter."""

    def __init__(self):
        self.call_count = 0

    def before_test(self):
        self.call_count = 0

    def step_flaky(self):
        self.call_count += 1
        if self.call_count == 2:
            raise AssertionError('flaky failure')

    def step_stable(self):
        pass


# --- TestStepLog attachment tests ---


def test_attach_text_to_step():
    step = TestStep('step_action', lambda: None)
    log = TestStepLog(step, duration=__import__('datetime').timedelta(seconds=0.1))
    log.attach('dom', '<html>hello</html>')
    assert 'dom' in log.attachments
    assert log.attachments['dom'] == '<html>hello</html>'


def test_attach_binary_to_step():
    step = TestStep('step_action', lambda: None)
    log = TestStepLog(step, duration=__import__('datetime').timedelta(seconds=0.1))
    png_data = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
    log.attach('screenshot.png', png_data)
    assert 'screenshot.png' in log.attachments
    assert isinstance(log.attachments['screenshot.png'], bytes)
    assert len(log.attachments['screenshot.png']) == 108


# --- OsmoHistory attachment tests ---


def test_history_attach():
    history = OsmoHistory()
    history.start_new_test()
    step = TestStep('step_action', lambda: None)
    history.add_step(step, __import__('datetime').timedelta(seconds=0.1))
    history.attach('dom', '<div>test</div>')
    tc = history.current_test_case
    assert tc is not None
    assert tc.steps_log[-1].attachments['dom'] == '<div>test</div>'


def test_to_dict_with_attachments():
    history = OsmoHistory()
    history.start_new_test()
    step = TestStep('step_action', lambda: None)
    history.add_step(step, __import__('datetime').timedelta(seconds=0.1))
    history.attach('screenshot.png', b'\x89PNG' + b'\x00' * 10)
    history.attach('dom.html', '<html></html>')
    history.stop()

    d = history.to_dict()
    step_entry = d['test_cases'][0]['steps'][0]
    # Should be a dict with attachments metadata
    assert isinstance(step_entry, dict)
    assert step_entry['name'] == 'action'
    assert len(step_entry['attachments']) == 2

    att_names = {a['name'] for a in step_entry['attachments']}
    assert att_names == {'screenshot.png', 'dom.html'}

    # Check types
    for att in step_entry['attachments']:
        if att['name'] == 'screenshot.png':
            assert att['type'] == 'bytes'
            assert att['size'] == 14
        elif att['name'] == 'dom.html':
            assert att['type'] == 'str'
            assert att['size'] == 13


def test_to_dict_without_attachments():
    """Steps without attachments should remain as plain strings."""
    history = OsmoHistory()
    history.start_new_test()
    step = TestStep('step_action', lambda: None)
    history.add_step(step, __import__('datetime').timedelta(seconds=0.1))
    history.stop()

    d = history.to_dict()
    # No attachments → step entry is just the name string
    assert d['test_cases'][0]['steps'][0] == 'action'


def test_to_json_no_binary():
    """to_json() should not embed raw bytes — only metadata."""
    history = OsmoHistory()
    history.start_new_test()
    step = TestStep('step_action', lambda: None)
    history.add_step(step, __import__('datetime').timedelta(seconds=0.1))
    history.attach('screenshot.png', b'\x89PNG\r\n')
    history.stop()

    json_str = history.to_json()
    # Should parse cleanly as JSON (no bytes)
    parsed = json.loads(json_str)
    assert parsed is not None
    # Should not contain the raw PNG bytes
    assert '\\x89' not in json_str
    assert 'PNG' not in json_str or 'screenshot.png' in json_str


def test_save_directory_structure(tmp_path):
    history = OsmoHistory()
    history.start_new_test()
    step = TestStep('step_action', lambda: None)
    history.add_step(step, __import__('datetime').timedelta(seconds=0.1))
    history.attach('screenshot.png', b'\x89PNG\r\n')
    history.attach('dom.html', '<html>test</html>')
    history.stop()

    history.save(tmp_path / 'output')

    assert (tmp_path / 'output' / 'history.json').exists()
    assert (tmp_path / 'output' / 'test_0' / 'step_000_screenshot.png').exists()
    assert (tmp_path / 'output' / 'test_0' / 'step_000_dom.html').exists()

    # Verify binary file content
    png_content = (tmp_path / 'output' / 'test_0' / 'step_000_screenshot.png').read_bytes()
    assert png_content == b'\x89PNG\r\n'

    # Verify text file content
    html_content = (tmp_path / 'output' / 'test_0' / 'step_000_dom.html').read_text()
    assert html_content == '<html>test</html>'


# --- Osmo integration tests ---


def test_capture_after_step_callback():
    model = SimpleModel()
    osmo = Osmo(model)
    osmo.test_end_condition = Length(3)
    osmo.test_suite_end_condition = Length(1)

    captured = []

    def capture():
        captured.append(model.count)
        return {'count': str(model.count)}

    osmo.capture_after_step(capture)
    osmo.generate()

    assert len(captured) == 3
    # All steps should have the "count" attachment
    for tc in osmo.history.test_cases:
        for step_log in tc.steps_log:
            assert 'count' in step_log.attachments


def test_osmo_history_injection():
    """Verify that osmo_history is injected into models."""
    model = AttachingModel()
    osmo = Osmo(model)
    osmo.test_end_condition = Length(3)
    osmo.test_suite_end_condition = Length(1)
    osmo.generate()

    # The after() hook should have attached notes via osmo_history
    for tc in osmo.history.test_cases:
        for step_log in tc.steps_log:
            assert 'note' in step_log.attachments
            note = step_log.attachments['note']
            assert isinstance(note, str)
            assert note.startswith('after step')


def test_multi_run_accumulation():
    model = SimpleModel()
    osmo = Osmo(model)
    osmo.test_end_condition = Length(2)
    osmo.test_suite_end_condition = Length(1)

    osmo.generate()
    osmo.generate()
    osmo.generate()

    assert len(osmo.runs) == 3
    # Each run should have its own history
    for run in osmo.runs:
        assert run.test_case_count == 1
        assert run.total_amount_of_steps == 2


def test_generate_and_save(tmp_path):
    model = SimpleModel()
    osmo = Osmo(model)
    osmo.test_end_condition = Length(2)
    osmo.test_suite_end_condition = Length(1)

    output_dir = tmp_path / 'results'
    osmo.generate_and_save(output_dir, runs=3)

    assert len(osmo.runs) == 3
    assert (output_dir / 'summary.json').exists()
    assert (output_dir / 'run_0' / 'history.json').exists()
    assert (output_dir / 'run_1' / 'history.json').exists()
    assert (output_dir / 'run_2' / 'history.json').exists()

    summary = json.loads((output_dir / 'summary.json').read_text())
    assert summary['total_runs'] == 3
    assert 'step_results' in summary
    assert 'step_frequency' in summary
    assert 'flaky_steps' in summary


def test_summary_flaky_detection(tmp_path):
    model = FlakyModel()
    osmo = Osmo(model)
    osmo.seed = 42
    osmo.test_end_condition = Length(5)
    osmo.test_suite_end_condition = Length(1)
    osmo.on_error(AlwaysIgnore())

    output_dir = tmp_path / 'flaky_results'
    osmo.generate_and_save(output_dir, runs=20)

    summary = json.loads((output_dir / 'summary.json').read_text())

    # step_flaky appears as "flaky" (step_ prefix stripped by TestStep.name)
    assert 'flaky' in summary['step_results']
    flaky_results = summary['step_results']['flaky']
    assert flaky_results['fail'] > 0
    assert flaky_results['pass'] > 0
    assert 'flaky' in summary['flaky_steps']

    # step_stable appears as "stable" — should never fail
    if 'stable' in summary['step_results']:
        assert summary['step_results']['stable']['fail'] == 0
        assert 'stable' not in summary['flaky_steps']
