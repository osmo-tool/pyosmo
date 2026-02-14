# AI Web Agent - PyOsmo Model Generator

Generate PyOsmo model-based tests for any web application using Claude + Playwright.

## How it works

1. **`generate_model.py`** — A Claude agent explores a web page via Playwright MCP, discovers interactive elements, and generates a PyOsmo model with `step_*`/`guard_*` methods.

2. **`refine_model.py`** — Runs the generated model **multiple times** (default: 10), collects multi-run history with flakiness analysis, and sends it to Claude for refinement. The agent fixes errors (especially flaky ones), improves coverage, and adds missing steps.

3. **`prompt_template.py`** — System prompts that teach the agent PyOsmo patterns and how to interpret multi-run results.

## Setup

```bash
# Install dependencies
pip install claude-agent-sdk playwright pyosmo

# Install Playwright browsers
playwright install chromium

# Set your API key
export ANTHROPIC_API_KEY=your-key-here
```

## Usage

### Generate a model

```bash
python generate_model.py https://todomvc.com/examples/react/dist/ -o todo_model.py
```

### Refine a model

```bash
# Single refinement pass (10 runs for flakiness detection)
python refine_model.py todo_model.py --url https://todomvc.com/examples/react/dist/

# Custom number of runs per iteration
python refine_model.py todo_model.py --url https://todomvc.com/examples/react/dist/ --runs 20

# Multiple refinement iterations
python refine_model.py todo_model.py --url https://todomvc.com/examples/react/dist/ --iterations 3 --runs 10
```

### Run the generated model directly

```bash
python todo_model.py
```

## Example output

See `example_output/todo_app_model.py` for a sample of what the agent generates for a TodoMVC application. The example includes DOM and screenshot capture in the `after()` hook.

## Multi-run workflow and flakiness detection

The refinement script uses `generate_and_save()` to run the model multiple times and save results:

```
test_results/
  summary.json           # Cross-run flakiness analysis
  run_0/
    history.json         # Per-run history
    test_0/
      step_000_dom.html  # DOM snapshots (if captured)
      step_000_screenshot.png
    ...
  run_1/
    ...
```

`summary.json` includes:
- **`flaky_steps`** — Steps that failed in some runs but not all (intermittent issues)
- **`step_results`** — Per-step pass/fail counts across all runs
- **`step_frequency`** — How often each step ran across all runs

## How the refinement loop works

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  Generate   │────>│  Run model   │────>│  Collect     │
│  model      │     │  N times     │     │  multi-run   │
└─────────────┘     └──────────────┘     │  history     │
                                         └──────┬───────┘
                    ┌──────────────┐            │
                    │  Write back  │<───────────┘
                    │  refined     │  Claude analyzes
                    │  model       │  flakiness, errors
                    └──────────────┘  & coverage
```

The multi-run history gives the agent everything it needs to diagnose flaky steps, fix consistent errors, and improve coverage.

## Capturing per-step artifacts

Models can capture DOM snapshots, screenshots, or any data per-step using `self.osmo_history`:

```python
def after(self):
    self.osmo_history.attach('dom.html', self.page.content())
    self.osmo_history.attach('screenshot.png', self.page.screenshot())
```

These artifacts are saved to disk by `generate_and_save()` and can be used for visual diffing or debugging.
