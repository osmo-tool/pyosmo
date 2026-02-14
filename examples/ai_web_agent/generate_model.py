#!/usr/bin/env python3
"""Generate a PyOsmo model for a web application using Claude + Playwright.

Usage:
    python generate_model.py <URL> [--output model.py]

Requires:
    pip install claude-agent-sdk
    npx @anthropic-ai/claude-code mcp add playwright -- npx @playwright/mcp@latest
"""

import argparse
import asyncio
import sys

from prompt_template import PYOSMO_MODEL_REFERENCE


async def generate_model(url: str, output_path: str) -> None:
    try:
        from claude_agent_sdk import Agent, AgentConfig, MCPServer
    except ImportError:
        print('Error: claude-agent-sdk is required. Install with: pip install claude-agent-sdk')
        sys.exit(1)

    playwright_mcp = MCPServer(
        name='playwright',
        command='npx',
        args=['@playwright/mcp@latest'],
    )

    agent = Agent(
        model='claude-sonnet-4-5-20250929',
        config=AgentConfig(
            system_prompt=PYOSMO_MODEL_REFERENCE,
            mcp_servers=[playwright_mcp],
        ),
    )

    user_prompt = f"""\
Explore the web application at {url} and generate a PyOsmo model for it.

Steps:
1. Navigate to {url} and observe the page structure
2. Click around to discover interactive elements, forms, navigation, and states
3. Generate a PyOsmo model class with step_*/guard_* methods using Playwright selectors
4. Include state tracking and assertions where appropriate
5. Output ONLY the complete Python file content, no extra explanation

Save the model to: {output_path}
"""

    print(f'Exploring {url} and generating model...')
    result = await agent.run(user_prompt)
    print(f'Agent completed. Model saved to {output_path}')
    print(f'Result: {result}')


def main() -> None:
    parser = argparse.ArgumentParser(description='Generate a PyOsmo model from a web application')
    parser.add_argument('url', help='URL of the web application to model')
    parser.add_argument(
        '--output', '-o', default='generated_model.py', help='Output file path (default: generated_model.py)'
    )
    args = parser.parse_args()

    asyncio.run(generate_model(args.url, args.output))


if __name__ == '__main__':
    main()
