"""Example PyOsmo model for a Todo application.

This is a sample of what the AI agent generates. It models a typical
TodoMVC-style application with add, complete, delete, and filter actions.
"""

from playwright.sync_api import Page

from pyosmo import Osmo
from pyosmo.end_conditions import Length


class TodoAppModel:
    """Model-based test for a Todo web application."""

    def __init__(self, page: Page, url: str):
        self.page = page
        self.url = url
        self.todo_count = 0
        self.completed_count = 0

    def before_test(self):
        """Navigate to app and reset state."""
        self.page.goto(self.url)
        self.page.wait_for_selector('.new-todo')
        self.todo_count = 0
        self.completed_count = 0

    # --- Add a todo item ---

    def step_add_todo(self):
        input_field = self.page.locator('.new-todo')
        input_field.fill(f'Task {self.todo_count + 1}')
        input_field.press('Enter')
        self.todo_count += 1

    def guard_add_todo(self):
        return self.todo_count < 10

    def weight_add_todo(self):
        return 5  # Adding items is the most common action

    # --- Toggle a todo as complete ---

    def step_toggle_todo(self):
        items = self.page.locator('.todo-list li:not(.completed) .toggle')
        items.first.click()
        self.completed_count += 1

    def guard_toggle_todo(self):
        active_count = self.todo_count - self.completed_count
        return active_count > 0

    # --- Delete a todo item ---

    def step_delete_todo(self):
        item = self.page.locator('.todo-list li').first
        item.hover()
        item.locator('.destroy').click()
        self.todo_count -= 1

    def guard_delete_todo(self):
        return self.todo_count > 0

    # --- Filter: show all ---

    def step_filter_all(self):
        self.page.click('a[href="#/"]')

    def guard_filter_all(self):
        return self.todo_count > 0

    # --- Filter: show active ---

    def step_filter_active(self):
        self.page.click('a[href="#/active"]')

    def guard_filter_active(self):
        return self.todo_count > 0

    # --- Filter: show completed ---

    def step_filter_completed(self):
        self.page.click('a[href="#/completed"]')

    def guard_filter_completed(self):
        return self.completed_count > 0

    # --- Assertions and capture (run after every step) ---

    def after(self):
        """Verify todo count display and capture DOM snapshot."""
        active_count = self.todo_count - self.completed_count
        if active_count > 0:
            count_text = self.page.locator('.todo-count').text_content()
            assert str(active_count) in count_text

        # Attach DOM snapshot and screenshot for analysis
        self.osmo_history.attach('dom.html', self.page.content())
        self.osmo_history.attach('screenshot.png', self.page.screenshot())


if __name__ == '__main__':
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        model = TodoAppModel(page=page, url='https://todomvc.com/examples/react/dist/')

        osmo = Osmo(model)
        osmo.test_end_condition = Length(30)
        osmo.generate()

        print(osmo.history.to_json())
        browser.close()
