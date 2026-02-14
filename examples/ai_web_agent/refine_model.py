#!/usr/bin/env python3
"""Refine an existing PyOsmo model based on test execution results.

Usage:
    python refine_model.py <model_file> [--url URL] [--steps 20] [--iterations 3]

This script:
1. Runs the existing model with PyOsmo
2. Collects history as JSON
3. Sends the model + history to Claude for analysis and refinement
4. Writes the updated model back

Requires:
    pip install claude-agent-sdk playwright pyosmo
"""

import argparse
import asyncio
import importlib.util
import sys
from pathlib import Path


def run_model_and_get_history(model_path: str, url: str, steps: int) -> tuple[str, str]:
    """Run a PyOsmo model and return (model_source, history_json)."""
    from playwright.sync_api import sync_playwright

    from pyosmo import Osmo
    from pyosmo.end_conditions import Length
    from pyosmo.error_strategy import AlwaysIgnore

    source = Path(model_path).read_text()

    # Dynamically load the model module
    spec = importlib.util.spec_from_file_location('generated_model', model_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Find the model class (first class with step_* methods)
    model_class = None
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if isinstance(attr, type) and any(m.startswith('step_') for m in dir(attr)):
            model_class = attr
            break

    if model_class is None:
        print('Error: No PyOsmo model class found in the file')
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        model = model_class(page=page, url=url)

        osmo = Osmo(model)
        osmo.test_end_condition = Length(steps)
        osmo.on_error(AlwaysIgnore())

        osmo.generate()

        history_json = osmo.history.to_json()
        browser.close()

    return source, history_json


async def refine_model(model_path: str, url: str, steps: int) -> None:
    try:
        from claude_agent_sdk import Agent, AgentConfig
    except ImportError:
        print('Error: claude-agent-sdk is required. Install with: pip install claude-agent-sdk')
        sys.exit(1)

    from prompt_template import REFINEMENT_PROMPT

    print(f'Running model {model_path}...')
    source, history_json = run_model_and_get_history(model_path, url, steps)

    print('Analyzing results and refining model...')

    agent = Agent(
        model='claude-sonnet-4-5-20250929',
        config=AgentConfig(system_prompt=REFINEMENT_PROMPT),
    )

    user_prompt = f"""\
Here is the current PyOsmo model:

```python
{source}
```

Here are the test execution results (JSON):

```json
{history_json}
```

Analyze the results and output an improved version of the model.
Fix any errors, improve coverage, and add missing steps if needed.
Output ONLY the complete updated Python file.
"""

    result = await agent.run(user_prompt)

    # Write refined model back
    Path(model_path).write_text(result)
    print(f'Refined model written to {model_path}')


def main() -> None:
    parser = argparse.ArgumentParser(description='Refine a PyOsmo model based on test results')
    parser.add_argument('model_file', help='Path to the PyOsmo model file')
    parser.add_argument('--url', required=True, help='URL of the web application')
    parser.add_argument('--steps', type=int, default=20, help='Steps per test (default: 20)')
    parser.add_argument('--iterations', type=int, default=1, help='Refinement iterations (default: 1)')
    args = parser.parse_args()

    for i in range(args.iterations):
        if args.iterations > 1:
            print(f'\n--- Refinement iteration {i + 1}/{args.iterations} ---')
        asyncio.run(refine_model(args.model_file, args.url, args.steps))


if __name__ == '__main__':
    main()
