# pylint: disable=bare-except,broad-except,too-many-instance-attributes
import logging
from datetime import datetime, timedelta
from random import Random
from typing import Optional, Union, List

from pyosmo.config import OsmoConfig
from pyosmo.history.history import OsmoHistory
from pyosmo.model import OsmoModelCollector, TestStep
from pyosmo.reporting import Format, ReportConfig

logger = logging.getLogger("osmo")


class Osmo(OsmoConfig):
    """
    Osmo tester core - Model-Based Testing framework.

    This class provides the main interface for configuring and running
    model-based tests. It manages test execution, model collection,
    and test history tracking.
    """

    def __init__(self, model: Optional[Union[object, List[object]]] = None) -> None:
        """
        Initialize Osmo with an optional model.

        Args:
            model: Optional model instance or list of model instances containing test steps and guards
        """
        super().__init__()
        self.model = OsmoModelCollector()
        if model:
            if isinstance(model, list):
                for m in model:
                    self.add_model(m)
            else:
                self.add_model(model)
        self.history = OsmoHistory()

    @property
    def seed(self) -> int:
        return self._seed

    @seed.setter
    def seed(self, value: int) -> None:
        """Set random seed for test generation"""
        logger.debug(f"Set seed: {value}")
        if not isinstance(value, int):
            raise AttributeError("Seed value must be an integer.")
        self._seed = value
        self._random = Random(self._seed)
        # update osmo_random in all models
        for model in self.model.sub_models:
            model.osmo_random = self._random  # type: ignore[attr-defined]

    @staticmethod
    def _check_model(model: object) -> None:
        """Check that model is valid"""
        if not hasattr(model, "__class__"):
            raise Exception("Osmo model need to be instance of model, not just class")

    def add_model(self, model: object) -> None:
        """Add model for osmo"""
        logger.debug(f"Add model:{model}")
        self._check_model(model)
        # Set osmo_random
        model.osmo_random = self._random  # type: ignore[attr-defined]
        self.model.add_model(model)

    def _run_step(self, step: TestStep) -> None:
        """
        Run step and save it to the history
        :param step: Test step
        :return:
        """
        logger.debug(f"Run step: {step}")
        start_time = datetime.now()
        try:
            step.execute()
            self.history.add_step(step, datetime.now() - start_time)
        except Exception as error:
            self.history.add_step(step, datetime.now() - start_time, error)
            raise error

    def run(self) -> None:
        """Same as generate but in online usage this sounds more natural"""
        self.generate()

    def generate(self) -> None:
        """Generate / run tests"""
        self.history = OsmoHistory()  # Restart the history
        logger.debug("Start generation..")
        logger.info(f"Using seed: {self.seed}")
        # Initialize algorithm
        self.algorithm.initialize(self.random, self.model)

        self.model.execute_optional("before_suite")
        if not self.model.all_steps:
            raise Exception("Empty model!")

        while True:
            try:
                self.history.start_new_test()
                self.model.execute_optional("before_test")
                while True:
                    # Use algorithm to select the step
                    self.model.execute_optional("before")
                    step = self.algorithm.choose(self.history, self.model.available_steps)
                    self.model.execute_optional(f"pre_{step}")
                    try:
                        self._run_step(step)
                    except BaseException as error:
                        self.test_error_strategy.failure_in_test(self.history, self.model, error)
                    self.model.execute_optional(f"post_{step.name}")
                    # General after step which is run after each step
                    self.model.execute_optional("after")

                    if self.test_end_condition.end_test(self.history, self.model):
                        break
                self.model.execute_optional("after_test")
            except BaseException as error:
                self.test_suite_error_strategy.failure_in_suite(self.history, self.model, error)
            if self.test_suite_end_condition.end_suite(self.history, self.model):
                break
        self.model.execute_optional("after_suite")
        self.history.stop()

    def save_report(
        self,
        path: str,
        format: Format = Format.HTML,
        config: Optional[ReportConfig] = None
    ) -> None:
        """Save test execution report to a file.

        Args:
            path: File path where report should be saved
            format: Report format (HTML, JSON, JUNIT, MARKDOWN, or CSV)
            config: Optional configuration for report generation

        Example:
            >>> osmo = Osmo(model)
            >>> osmo.run()
            >>> osmo.save_report("report.html", format=Format.HTML)
            >>> osmo.save_report("results.json", format=Format.JSON)
        """
        from pyosmo.reporting import (
            HTMLReporter,
            JSONReporter,
            JUnitReporter,
            MarkdownReporter,
            CSVReporter,
        )

        # Select appropriate reporter based on format
        reporter_map = {
            Format.HTML: HTMLReporter,
            Format.JSON: JSONReporter,
            Format.JUNIT: JUnitReporter,
            Format.MARKDOWN: MarkdownReporter,
            Format.CSV: CSVReporter,
        }

        reporter_class = reporter_map.get(format)
        if reporter_class is None:
            raise ValueError(f"Unsupported format: {format}")

        reporter = reporter_class(self.history, config)
        reporter.save(path)
        logger.info(f"Report saved to {path} in {format.value} format")

    def save_reports(
        self,
        base_path: str,
        formats: Optional[List[Format]] = None,
        config: Optional[ReportConfig] = None
    ) -> None:
        """Save test execution reports in multiple formats.

        Args:
            base_path: Base file path (without extension) for reports
            formats: List of formats to generate (defaults to all formats)
            config: Optional configuration for report generation

        Example:
            >>> osmo = Osmo(model)
            >>> osmo.run()
            >>> osmo.save_reports(
            ...     "reports/test_run",
            ...     formats=[Format.HTML, Format.JSON, Format.JUNIT]
            ... )
            # Creates: test_run.html, test_run.json, test_run.xml
        """
        if formats is None:
            formats = [Format.HTML, Format.JSON, Format.JUNIT, Format.MARKDOWN, Format.CSV]

        # Extension mapping for different formats
        extensions = {
            Format.HTML: ".html",
            Format.JSON: ".json",
            Format.JUNIT: ".xml",
            Format.MARKDOWN: ".md",
            Format.CSV: ".csv",
        }

        for format_type in formats:
            extension = extensions.get(format_type, f".{format_type.value}")
            path = f"{base_path}{extension}"
            self.save_report(path, format_type, config)

        logger.info(f"Generated {len(formats)} reports at {base_path}.*")
