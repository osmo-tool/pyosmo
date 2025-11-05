"""HTML report generator for PyOsmo test execution."""

import json
from typing import Any, Dict

from pyosmo.reporting import Reporter


class HTMLReporter(Reporter):
    """Generate interactive HTML report with visualizations.

    The HTML format provides a rich, interactive view of test results
    with charts, tables, and visual feedback suitable for sharing
    with stakeholders.
    """

    def generate(self) -> str:
        """Generate HTML report.

        Returns:
            HTML-formatted report as a string
        """
        stats = self.history.statistics()

        # Prepare data for charts
        chart_data = self._prepare_chart_data() if self.config.include_charts else None

        # Build HTML
        html = self._html_template(stats, chart_data)
        return html

    def _prepare_chart_data(self) -> Dict[str, Any]:
        """Prepare data for JavaScript charts."""
        stats = self.history.statistics()

        # Step frequency data
        step_names = list(stats.step_frequency.keys())
        step_counts = list(stats.step_frequency.values())

        # Coverage timeline data
        timeline = self.history.coverage_timeline()
        timeline_steps = [t[0] for t in timeline]
        timeline_coverage = [t[1] for t in timeline]

        # Step execution times
        time_names = list(stats.step_execution_times.keys())
        time_values = [stats.step_execution_times[name] * 1000 for name in time_names]  # Convert to ms

        return {
            "step_frequency": {
                "labels": step_names,
                "data": step_counts,
            },
            "coverage_timeline": {
                "labels": timeline_steps,
                "data": timeline_coverage,
            },
            "execution_times": {
                "labels": time_names,
                "data": time_values,
            },
        }

    def _html_template(self, stats: Any, chart_data: Dict[str, Any] | None) -> str:
        """Generate complete HTML report."""
        theme_colors = self._get_theme_colors()

        # Build test case rows
        test_case_rows = []
        for idx, tc in enumerate(self.history.test_cases, start=1):
            status_class = "failed" if tc.error_count > 0 else "passed"
            status_text = "❌ FAILED" if tc.error_count > 0 else "✅ PASSED"

            test_case_rows.append(f"""
                <tr class="{status_class}">
                    <td>{idx}</td>
                    <td>{len(tc.steps_log)}</td>
                    <td>{tc.duration.total_seconds():.3f}s</td>
                    <td>{tc.error_count}</td>
                    <td><span class="status-badge {status_class}">{status_text}</span></td>
                </tr>
            """)

        test_case_table = "".join(test_case_rows)

        # Build step frequency rows
        step_freq_rows = []
        for step_name, count in sorted(stats.step_frequency.items(), key=lambda x: x[1], reverse=True):
            avg_time = stats.step_execution_times.get(step_name, 0.0)
            step_freq_rows.append(f"""
                <tr>
                    <td><code>{step_name}</code></td>
                    <td>{count}</td>
                    <td>{avg_time * 1000:.2f}ms</td>
                </tr>
            """)

        step_freq_table = "".join(step_freq_rows)

        # Chart scripts
        chart_scripts = ""
        if chart_data:
            chart_scripts = self._generate_chart_scripts(chart_data)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.config.title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: {theme_colors['text']};
            background: {theme_colors['background']};
            padding: 2rem;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        h1 {{
            color: {theme_colors['primary']};
            margin-bottom: 0.5rem;
            font-size: 2.5rem;
        }}

        h2 {{
            color: {theme_colors['secondary']};
            margin: 2rem 0 1rem;
            font-size: 1.8rem;
            border-bottom: 2px solid {theme_colors['border']};
            padding-bottom: 0.5rem;
        }}

        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }}

        .summary-card {{
            background: {theme_colors['card']};
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid {theme_colors['primary']};
        }}

        .summary-card h3 {{
            color: {theme_colors['muted']};
            font-size: 0.9rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.5rem;
        }}

        .summary-card .value {{
            font-size: 2rem;
            font-weight: bold;
            color: {theme_colors['primary']};
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            background: {theme_colors['card']};
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 1rem 0;
        }}

        th {{
            background: {theme_colors['primary']};
            color: white;
            padding: 1rem;
            text-align: left;
            font-weight: 600;
        }}

        td {{
            padding: 0.75rem 1rem;
            border-bottom: 1px solid {theme_colors['border']};
        }}

        tr:hover {{
            background: {theme_colors['hover']};
        }}

        tr.passed {{
            background: {theme_colors['success-bg']};
        }}

        tr.failed {{
            background: {theme_colors['error-bg']};
        }}

        .status-badge {{
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.85rem;
            font-weight: 600;
        }}

        .status-badge.passed {{
            background: {theme_colors['success']};
            color: white;
        }}

        .status-badge.failed {{
            background: {theme_colors['error']};
            color: white;
        }}

        .chart-container {{
            background: {theme_colors['card']};
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 2rem 0;
        }}

        canvas {{
            max-height: 400px;
        }}

        code {{
            background: {theme_colors['code-bg']};
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}

        .timestamp {{
            color: {theme_colors['muted']};
            font-size: 0.9rem;
            margin-top: 2rem;
            text-align: center;
        }}
    </style>
    {"<script src='https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js'></script>" if self.config.include_charts else ""}
</head>
<body>
    <div class="container">
        <h1>{self.config.title}</h1>

        <div class="summary">
            <div class="summary-card">
                <h3>Total Tests</h3>
                <div class="value">{stats.total_tests}</div>
            </div>
            <div class="summary-card">
                <h3>Total Steps</h3>
                <div class="value">{stats.total_steps}</div>
            </div>
            <div class="summary-card">
                <h3>Unique Steps</h3>
                <div class="value">{stats.unique_steps}</div>
            </div>
            <div class="summary-card">
                <h3>Duration</h3>
                <div class="value">{stats.duration.total_seconds():.2f}s</div>
            </div>
            <div class="summary-card">
                <h3>Errors</h3>
                <div class="value" style="color: {'#dc3545' if stats.error_count > 0 else '#28a745'};">{stats.error_count}</div>
            </div>
            <div class="summary-card">
                <h3>Avg Steps/Test</h3>
                <div class="value">{stats.average_steps_per_test:.1f}</div>
            </div>
        </div>

        {self._generate_charts_html(chart_data) if self.config.include_charts and chart_data else ""}

        {self._generate_test_cases_section(test_case_table) if self.config.include_timeline else ""}

        {self._generate_statistics_section(step_freq_table, stats) if self.config.include_statistics else ""}

        <div class="timestamp">
            Report generated: {self.history.start_time.strftime('%Y-%m-%d %H:%M:%S')} -
            {self.history.stop_time.strftime('%Y-%m-%d %H:%M:%S') if self.history.stop_time else 'In Progress'}
        </div>
    </div>

    {chart_scripts}
</body>
</html>"""

    def _get_theme_colors(self) -> Dict[str, str]:
        """Get color scheme based on theme."""
        if self.config.theme == "dark":
            return {
                "background": "#1a1a1a",
                "text": "#e0e0e0",
                "card": "#2d2d2d",
                "primary": "#4a9eff",
                "secondary": "#6c757d",
                "border": "#404040",
                "hover": "#3a3a3a",
                "muted": "#a0a0a0",
                "success": "#28a745",
                "error": "#dc3545",
                "success-bg": "#1e3a2e",
                "error-bg": "#3a1e1e",
                "code-bg": "#1a1a1a",
            }
        else:  # light theme
            return {
                "background": "#f5f5f5",
                "text": "#333333",
                "card": "#ffffff",
                "primary": "#007bff",
                "secondary": "#6c757d",
                "border": "#e0e0e0",
                "hover": "#f8f9fa",
                "muted": "#6c757d",
                "success": "#28a745",
                "error": "#dc3545",
                "success-bg": "#d4edda",
                "error-bg": "#f8d7da",
                "code-bg": "#f4f4f4",
            }

    def _generate_charts_html(self, chart_data: Dict[str, Any]) -> str:
        """Generate HTML for charts section."""
        return f"""
        <h2>Visualizations</h2>

        <div class="chart-container">
            <h3>Step Execution Frequency</h3>
            <canvas id="stepFrequencyChart"></canvas>
        </div>

        <div class="chart-container">
            <h3>Coverage Timeline</h3>
            <canvas id="coverageTimelineChart"></canvas>
        </div>

        <div class="chart-container">
            <h3>Average Step Execution Times</h3>
            <canvas id="executionTimesChart"></canvas>
        </div>
        """

    def _generate_test_cases_section(self, test_case_table: str) -> str:
        """Generate HTML for test cases section."""
        return f"""
        <h2>Test Cases</h2>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Steps</th>
                    <th>Duration</th>
                    <th>Errors</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {test_case_table}
            </tbody>
        </table>
        """

    def _generate_statistics_section(self, step_freq_table: str, stats: Any) -> str:
        """Generate HTML for statistics section."""
        return f"""
        <h2>Step Statistics</h2>
        <table>
            <thead>
                <tr>
                    <th>Step Name</th>
                    <th>Count</th>
                    <th>Avg Duration</th>
                </tr>
            </thead>
            <tbody>
                {step_freq_table}
            </tbody>
        </table>

        <div style="margin-top: 1rem;">
            <p><strong>Most Executed:</strong> <code>{stats.most_executed_step or 'N/A'}</code>
               ({stats.step_frequency.get(stats.most_executed_step, 0) if stats.most_executed_step else 0} times)</p>
            <p><strong>Least Executed:</strong> <code>{stats.least_executed_step or 'N/A'}</code>
               ({stats.step_frequency.get(stats.least_executed_step, 0) if stats.least_executed_step else 0} times)</p>
        </div>
        """

    def _generate_chart_scripts(self, chart_data: Dict[str, Any]) -> str:
        """Generate JavaScript for rendering charts."""
        return f"""
    <script>
        // Chart.js configuration
        Chart.defaults.font.family = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif";

        // Step Frequency Chart
        new Chart(document.getElementById('stepFrequencyChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(chart_data['step_frequency']['labels'])},
                datasets: [{{
                    label: 'Executions',
                    data: {json.dumps(chart_data['step_frequency']['data'])},
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            precision: 0
                        }}
                    }}
                }}
            }}
        }});

        // Coverage Timeline Chart
        new Chart(document.getElementById('coverageTimelineChart'), {{
            type: 'line',
            data: {{
                labels: {json.dumps(chart_data['coverage_timeline']['labels'])},
                datasets: [{{
                    label: 'Unique Steps Covered',
                    data: {json.dumps(chart_data['coverage_timeline']['data'])},
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            precision: 0
                        }}
                    }},
                    x: {{
                        display: false
                    }}
                }}
            }}
        }});

        // Execution Times Chart
        new Chart(document.getElementById('executionTimesChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(chart_data['execution_times']['labels'])},
                datasets: [{{
                    label: 'Avg Duration (ms)',
                    data: {json.dumps(chart_data['execution_times']['data'])},
                    backgroundColor: 'rgba(255, 159, 64, 0.5)',
                    borderColor: 'rgba(255, 159, 64, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
    </script>
        """
