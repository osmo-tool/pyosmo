"""
Model updater - Updates existing PyOsmo models with new discoveries.
"""

import ast
import re
from typing import Dict, List, Set, Optional
from pathlib import Path

from .crawler import Page
from .generator import ModelGenerator


class ModelUpdater:
    """
    Updates existing PyOsmo models with newly discovered actions and states.
    """

    def __init__(self, model_path: Path):
        """
        Initialize the model updater.

        Args:
            model_path: Path to the existing model file
        """
        self.model_path = Path(model_path)
        self.existing_code = ''
        self.tree: Optional[ast.Module] = None
        self.existing_methods: Set[str] = set()
        self.existing_guards: Set[str] = set()
        self.class_name: Optional[str] = None

        if self.model_path.exists():
            self._parse_existing_model()

    def _parse_existing_model(self):
        """Parse the existing model file."""
        with open(self.model_path, 'r') as f:
            self.existing_code = f.read()

        try:
            self.tree = ast.parse(self.existing_code)
        except SyntaxError as e:
            raise ValueError(f'Failed to parse model file: {e}')

        # Find the model class and extract method names
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                self.class_name = node.name

                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_name = item.name
                        if method_name.startswith('step_'):
                            self.existing_methods.add(method_name[5:])  # Remove 'step_' prefix
                        elif method_name.startswith('guard_'):
                            self.existing_guards.add(method_name[6:])  # Remove 'guard_' prefix

    def update_model(self, pages: Dict[str, Page], base_url: str, preserve_existing: bool = True) -> str:
        """
        Update the model with new discoveries.

        Args:
            pages: Newly crawled pages
            base_url: Base URL of the website
            preserve_existing: Whether to preserve existing code

        Returns:
            Updated model code
        """
        # Generate new model
        generator = ModelGenerator(pages, base_url)
        new_code = generator.generate_model_class(self.class_name or 'WebsiteModel')

        if not preserve_existing or not self.existing_code:
            return new_code

        # Parse new model to find new methods
        new_tree = ast.parse(new_code)
        new_methods: Set[str] = set()

        for node in ast.walk(new_tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        if item.name.startswith('step_'):
                            new_methods.add(item.name[5:])

        # Find truly new methods (not in existing model)
        added_methods = new_methods - self.existing_methods

        if not added_methods:
            print('No new methods to add.')
            return self.existing_code

        # Extract new method code
        updated_code = self._merge_models(new_code, added_methods)

        return updated_code

    def _merge_models(self, new_code: str, added_methods: Set[str]) -> str:
        """
        Merge new methods into existing model.

        Args:
            new_code: Newly generated model code
            added_methods: Set of method names to add

        Returns:
            Merged model code
        """
        # Parse new code to extract method definitions
        new_tree = ast.parse(new_code)
        methods_to_add: List[str] = []

        for node in ast.walk(new_tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_name = item.name
                        action_name = method_name.replace('step_', '').replace('guard_', '')

                        if action_name in added_methods:
                            # Extract method source code
                            method_code = ast.get_source_segment(new_code, item)
                            if method_code:
                                methods_to_add.append(method_code)

        if not methods_to_add:
            return self.existing_code

        # Find insertion point (before last method or at end of class)
        lines = self.existing_code.split('\n')
        insertion_line = len(lines)

        # Find the last method in the class
        for i in range(len(lines) - 1, -1, -1):
            if re.match(r'^\s+def ', lines[i]):
                # Find the end of this method
                indent = len(lines[i]) - len(lines[i].lstrip())
                for j in range(i + 1, len(lines)):
                    if lines[j].strip() and not lines[j].startswith(' ' * (indent + 1)):
                        insertion_line = j
                        break
                break

        # Insert new methods
        new_lines = lines[:insertion_line]
        new_lines.append('')
        new_lines.append('    # --- Auto-generated methods below ---')
        new_lines.append('')

        for method_code in methods_to_add:
            # Add proper indentation
            method_lines = method_code.split('\n')
            new_lines.extend(method_lines)
            new_lines.append('')

        new_lines.extend(lines[insertion_line:])

        return '\n'.join(new_lines)

    def save_updated_model(self, pages: Dict[str, Page], base_url: str, backup: bool = True):
        """
        Update and save the model.

        Args:
            pages: Newly crawled pages
            base_url: Base URL of the website
            backup: Whether to create a backup of the existing model
        """
        if backup and self.model_path.exists():
            backup_path = self.model_path.with_suffix('.py.bak')
            backup_path.write_text(self.existing_code)
            print(f'Backup saved to: {backup_path}')

        updated_code = self.update_model(pages, base_url)

        with open(self.model_path, 'w') as f:
            f.write(updated_code)

        print(f'Model updated: {self.model_path}')

    def get_update_summary(self, pages: Dict[str, Page], base_url: str) -> Dict:
        """
        Get a summary of what would be updated.

        Args:
            pages: Newly crawled pages
            base_url: Base URL of the website

        Returns:
            Dictionary with update statistics
        """
        generator = ModelGenerator(pages, base_url)
        generator.analyze_forms()
        generator.analyze_links()

        new_actions = {action['name'] for action in generator.actions}
        added_actions = new_actions - self.existing_methods
        removed_actions = self.existing_methods - new_actions

        return {
            'existing_methods': len(self.existing_methods),
            'new_methods': len(new_actions),
            'added_methods': len(added_actions),
            'removed_methods': len(removed_actions),
            'added_method_names': list(added_actions),
            'removed_method_names': list(removed_actions),
        }
