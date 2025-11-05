"""
Example demonstrating PyOsmo's reporting capabilities.

This example shows how to generate test reports in multiple formats
(HTML, JSON, JUnit XML, Markdown, and CSV) with custom configuration.
"""

from pathlib import Path

from pyosmo import Osmo
from pyosmo.decorators import guard, step
from pyosmo.end_conditions import Length
from pyosmo.reporting import Format, ReportConfig


class ShoppingCartModel:
    """Simple e-commerce shopping cart model for testing."""

    def __init__(self):
        self.cart = []
        self.logged_in = False
        self.items_browsed = 0

    @step
    def step_login(self):
        """User logs into the system."""
        print("  → Login")
        self.logged_in = True

    @step
    def step_logout(self):
        """User logs out."""
        print("  → Logout")
        self.logged_in = False
        self.cart = []

    @guard("step_logout")
    def guard_logout(self):
        return self.logged_in

    @step
    def step_browse_products(self):
        """User browses products."""
        print("  → Browse products")
        self.items_browsed += 1

    @step
    def step_add_to_cart(self):
        """User adds item to cart."""
        print("  → Add to cart")
        self.cart.append(f"item_{len(self.cart) + 1}")

    @guard("step_add_to_cart")
    def guard_add_to_cart(self):
        return self.logged_in and self.items_browsed > 0

    @step
    def step_remove_from_cart(self):
        """User removes item from cart."""
        print("  → Remove from cart")
        if self.cart:
            self.cart.pop()

    @guard("step_remove_from_cart")
    def guard_remove_from_cart(self):
        return len(self.cart) > 0

    @step
    def step_checkout(self):
        """User proceeds to checkout."""
        print("  → Checkout")

    @guard("step_checkout")
    def guard_checkout(self):
        return self.logged_in and len(self.cart) > 0


def main():
    """Run the example and generate reports."""
    print("=" * 60)
    print("PyOsmo Reporting Example")
    print("=" * 60)
    print()

    # Create the model
    model = ShoppingCartModel()

    # Configure Osmo
    osmo = Osmo(model)
    osmo.seed = 42  # For reproducibility
    osmo.test_end_condition = Length(30)  # 30 steps per test
    osmo.test_suite_end_condition = Length(3)  # 3 test cases

    # Run the tests
    print("Running tests...\n")
    osmo.run()

    # Print summary
    print("\n" + "=" * 60)
    print("Test Execution Complete!")
    print("=" * 60)
    osmo.history.print_summary()

    # Create reports directory
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)

    print("\nGenerating reports...")
    print("-" * 60)

    # Example 1: Generate individual reports with basic configuration
    print("\n1. Generating individual reports with basic config:")
    osmo.save_report(str(reports_dir / "report.html"), format=Format.HTML)
    print("   ✓ HTML report saved to reports/report.html")

    osmo.save_report(str(reports_dir / "report.json"), format=Format.JSON)
    print("   ✓ JSON report saved to reports/report.json")

    osmo.save_report(str(reports_dir / "junit-results.xml"), format=Format.JUNIT)
    print("   ✓ JUnit XML saved to reports/junit-results.xml")

    osmo.save_report(str(reports_dir / "report.md"), format=Format.MARKDOWN)
    print("   ✓ Markdown report saved to reports/report.md")

    osmo.save_report(str(reports_dir / "report.csv"), format=Format.CSV)
    print("   ✓ CSV report saved to reports/report.csv")

    # Example 2: Generate multiple reports at once
    print("\n2. Generating multiple reports at once:")
    osmo.save_reports(
        str(reports_dir / "shopping_cart"),
        formats=[Format.HTML, Format.JSON, Format.JUNIT],
    )
    print("   ✓ Generated shopping_cart.html, shopping_cart.json, shopping_cart.xml")

    # Example 3: Generate with custom configuration
    print("\n3. Generating reports with custom configuration:")

    # Light theme configuration
    light_config = ReportConfig(
        title="Shopping Cart Test Suite - Light Theme",
        include_charts=True,
        include_timeline=True,
        include_statistics=True,
        theme="light",
    )
    osmo.save_report(
        str(reports_dir / "report_light.html"), format=Format.HTML, config=light_config
    )
    print("   ✓ Light theme HTML report saved to reports/report_light.html")

    # Dark theme configuration
    dark_config = ReportConfig(
        title="Shopping Cart Test Suite - Dark Theme",
        include_charts=True,
        include_timeline=True,
        include_statistics=True,
        theme="dark",
    )
    osmo.save_report(
        str(reports_dir / "report_dark.html"), format=Format.HTML, config=dark_config
    )
    print("   ✓ Dark theme HTML report saved to reports/report_dark.html")

    # Example 4: Minimal configuration (no charts, just data)
    print("\n4. Generating minimal report (no charts):")
    minimal_config = ReportConfig(
        title="Shopping Cart Test Suite - Minimal",
        include_charts=False,
        include_timeline=True,
        include_statistics=True,
    )
    osmo.save_report(
        str(reports_dir / "report_minimal.html"),
        format=Format.HTML,
        config=minimal_config,
    )
    print("   ✓ Minimal HTML report saved to reports/report_minimal.html")

    # Example 5: Programmatic access to test data
    print("\n5. Programmatic access to test data:")
    stats = osmo.history.statistics()
    print(f"   • Total tests: {stats.total_tests}")
    print(f"   • Total steps: {stats.total_steps}")
    print(f"   • Unique steps: {stats.unique_steps}")
    print(f"   • Duration: {stats.duration}")
    print(f"   • Most executed step: {stats.most_executed_step}")
    print(f"   • Errors: {stats.error_count}")

    # Step frequency
    print("\n   Step Execution Frequency:")
    for step_name, count in sorted(
        stats.step_frequency.items(), key=lambda x: x[1], reverse=True
    ):
        avg_time_ms = stats.step_execution_times[step_name] * 1000
        print(f"     - {step_name}: {count} times (avg {avg_time_ms:.2f}ms)")

    print("\n" + "=" * 60)
    print("Reports generated successfully!")
    print("=" * 60)
    print("\nOpen the HTML reports in your browser to see interactive visualizations.")
    print("Check out the other formats for different use cases:")
    print("  • JSON: For data analysis with pandas or custom tools")
    print("  • JUnit XML: For CI/CD integration")
    print("  • Markdown: For documentation")
    print("  • CSV: For spreadsheet analysis")
    print()


if __name__ == "__main__":
    main()
