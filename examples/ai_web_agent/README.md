# AI Web Agent - PyOsmo Model Generator

Generate PyOsmo model-based tests for any web application using Claude + Playwright.

## How it works

1. **`generate_model.py`** — A Claude agent explores a web page via Playwright MCP, discovers interactive elements, and generates a PyOsmo model with `step_*`/`guard_*` methods.

2. **`refine_model.py`** — Runs the generated model, collects test history as JSON, and sends it to Claude for analysis. The agent fixes errors, improves coverage, and adds missing steps.

3. **`prompt_template.py`** — System prompts that teach the agent PyOsmo patterns.

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
# Single refinement pass
python refine_model.py todo_model.py --url https://todomvc.com/examples/react/dist/

# Multiple iterations
python refine_model.py todo_model.py --url https://todomvc.com/examples/react/dist/ --iterations 3
```

### Run the generated model directly

```bash
python todo_model.py
```

## Example output

See `example_output/todo_app_model.py` for a sample of what the agent generates for a TodoMVC application.

## How the refinement loop works

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  Generate   │────>│  Run model   │────>│  Collect     │
│  model      │     │  with PyOsmo │     │  history JSON│
└─────────────┘     └──────────────┘     └──────┬───────┘
                                                │
                    ┌──────────────┐            │
                    │  Write back  │<───────────┘
                    │  refined     │  Claude analyzes
                    │  model       │  errors & coverage
                    └──────────────┘
```

The history JSON includes statistics, step frequencies, transition pairs, and per-test error details — giving the agent everything it needs to diagnose and fix issues.
