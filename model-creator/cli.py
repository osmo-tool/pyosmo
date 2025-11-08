"""
CLI interface for the PyOsmo Model Creator.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from .crawler import WebsiteCrawler
from .generator import ModelGenerator
from .updater import ModelUpdater


def create_model(args):
    """Create a new model from a website."""
    print(f"Crawling website: {args.url}")
    print(f"Max pages: {args.max_pages}")
    print(f"Output: {args.output}")
    print("-" * 60)

    # Initialize crawler
    auth = None
    if args.username and args.password:
        auth = (args.username, args.password)

    crawler = WebsiteCrawler(
        base_url=args.url,
        max_pages=args.max_pages,
        delay=args.delay,
        follow_external=args.follow_external,
        auth=auth,
    )

    # Crawl the website
    pages = crawler.crawl()

    if not pages:
        print("Error: No pages were crawled. Check the URL and try again.")
        return 1

    # Display crawl statistics
    stats = crawler.get_statistics()
    print("\nCrawl Statistics:")
    print(f"  Pages discovered: {stats['total_pages']}")
    print(f"  Forms found: {stats['total_forms']}")
    print(f"  Links found: {stats['total_links']}")
    print(f"  Pages with forms: {stats['pages_with_forms']}")
    print(f"  Pages with login: {stats['pages_with_login']}")
    print(f"  Pages with logout: {stats['pages_with_logout']}")
    print()

    # Save crawl data if requested
    if args.save_crawl:
        crawl_data = {
            url: {
                "title": page.title,
                "forms": len(page.forms),
                "links": len(page.links),
                "has_login": page.has_login,
                "has_logout": page.has_logout,
            }
            for url, page in pages.items()
        }

        crawl_path = Path(args.output).with_suffix(".crawl.json")
        with open(crawl_path, "w") as f:
            json.dump(crawl_data, f, indent=2)
        print(f"Crawl data saved to: {crawl_path}")

    # Generate model
    print("Generating model...")
    generator = ModelGenerator(pages, args.url)
    generator.save_model(args.output, args.class_name)

    # Display generation statistics
    gen_stats = generator.get_statistics()
    print("\nModel Generation Statistics:")
    print(f"  Total actions: {gen_stats['total_actions']}")
    print(f"  Form actions: {gen_stats['form_actions']}")
    print(f"  Navigation actions: {gen_stats['navigation_actions']}")
    print(f"  State variables: {gen_stats['state_variables']}")
    print(f"  Login actions: {gen_stats['login_actions']}")
    print(f"  Logout actions: {gen_stats['logout_actions']}")
    print()

    print(f"✓ Model created successfully: {args.output}")
    print("\nTo test the model, run:")
    print(f"  python -m osmo.explorer -m {args.output}:{args.class_name}")

    return 0


def update_model(args):
    """Update an existing model."""
    model_path = Path(args.model)

    if not model_path.exists():
        print(f"Error: Model file not found: {model_path}")
        return 1

    print(f"Updating model: {model_path}")
    print(f"Crawling website: {args.url}")
    print("-" * 60)

    # Initialize crawler
    auth = None
    if args.username and args.password:
        auth = (args.username, args.password)

    crawler = WebsiteCrawler(
        base_url=args.url,
        max_pages=args.max_pages,
        delay=args.delay,
        follow_external=args.follow_external,
        auth=auth,
    )

    # Crawl the website
    pages = crawler.crawl()

    if not pages:
        print("Error: No pages were crawled. Check the URL and try again.")
        return 1

    # Display crawl statistics
    stats = crawler.get_statistics()
    print("\nCrawl Statistics:")
    print(f"  Pages discovered: {stats['total_pages']}")
    print(f"  Forms found: {stats['total_forms']}")
    print()

    # Update model
    print("Analyzing model updates...")
    updater = ModelUpdater(model_path)

    # Get update summary
    summary = updater.get_update_summary(pages, args.url)
    print("\nUpdate Summary:")
    print(f"  Existing methods: {summary['existing_methods']}")
    print(f"  New methods discovered: {summary['new_methods']}")
    print(f"  Methods to add: {summary['added_methods']}")

    if summary['added_method_names']:
        print("\n  New methods:")
        for method in summary['added_method_names']:
            print(f"    - {method}")

    if summary['removed_method_names']:
        print(f"\n  Methods no longer found: {summary['removed_methods']}")
        for method in summary['removed_method_names']:
            print(f"    - {method}")

    if summary['added_methods'] == 0:
        print("\n✓ Model is up to date. No changes needed.")
        return 0

    # Confirm update
    if not args.yes:
        response = input("\nProceed with update? [y/N]: ")
        if response.lower() not in ["y", "yes"]:
            print("Update cancelled.")
            return 0

    # Perform update
    updater.save_updated_model(pages, args.url, backup=not args.no_backup)

    print(f"\n✓ Model updated successfully: {model_path}")

    return 0


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="PyOsmo Model Creator - Generate models from websites",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a new model
  python -m model-creator create https://example.com -o models/example_model.py

  # Create with login
  python -m model-creator create https://example.com -o models/example.py \\
      --username user --password pass

  # Update existing model
  python -m model-creator update models/example_model.py https://example.com

  # Crawl more pages
  python -m model-creator create https://example.com -o models/example.py \\
      --max-pages 100
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new model")
    create_parser.add_argument("url", help="Base URL of the website to model")
    create_parser.add_argument(
        "-o", "--output",
        required=True,
        help="Output path for the generated model"
    )
    create_parser.add_argument(
        "-c", "--class-name",
        default="WebsiteModel",
        help="Name of the model class (default: WebsiteModel)"
    )
    create_parser.add_argument(
        "-m", "--max-pages",
        type=int,
        default=50,
        help="Maximum number of pages to crawl (default: 50)"
    )
    create_parser.add_argument(
        "-d", "--delay",
        type=float,
        default=0.5,
        help="Delay between requests in seconds (default: 0.5)"
    )
    create_parser.add_argument(
        "--follow-external",
        action="store_true",
        help="Follow external links"
    )
    create_parser.add_argument(
        "--username",
        help="Username for basic authentication"
    )
    create_parser.add_argument(
        "--password",
        help="Password for basic authentication"
    )
    create_parser.add_argument(
        "--save-crawl",
        action="store_true",
        help="Save crawl data to JSON file"
    )

    # Update command
    update_parser = subparsers.add_parser("update", help="Update an existing model")
    update_parser.add_argument("model", help="Path to the existing model file")
    update_parser.add_argument("url", help="Base URL of the website")
    update_parser.add_argument(
        "-m", "--max-pages",
        type=int,
        default=50,
        help="Maximum number of pages to crawl (default: 50)"
    )
    update_parser.add_argument(
        "-d", "--delay",
        type=float,
        default=0.5,
        help="Delay between requests in seconds (default: 0.5)"
    )
    update_parser.add_argument(
        "--follow-external",
        action="store_true",
        help="Follow external links"
    )
    update_parser.add_argument(
        "--username",
        help="Username for basic authentication"
    )
    update_parser.add_argument(
        "--password",
        help="Password for basic authentication"
    )
    update_parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help="Skip confirmation prompt"
    )
    update_parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Don't create backup of existing model"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        if args.command == "create":
            return create_model(args)
        elif args.command == "update":
            return update_model(args)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        return 1
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
