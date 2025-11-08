"""
Example: Counter model demonstrating pytest-pyosmo discovery

To run:
1. Install: pip install pytest pyosmo
2. Copy pytest_pyosmo_plugin.py to your project (or conftest.py)
3. Run: pytest test_models_example.py -v
4. Run quick: pytest test_models_example.py -m quick -v
"""

import pytest

# ============================================================================
# Model 1: Simple Counter
# ============================================================================


@pytest.model
class CounterModel:
    """
    A simple counter that can increment, decrement, and reset.

    Tests with default configuration (50 steps, 5 tests).
    """

    def __init__(self):
        self.value = 0

    def before_test(self):
        """Reset before each generated test"""
        self.value = 0
        print('  [Counter Reset] Starting new test sequence')

    # Increment action
    def guard_increment(self):
        """Can always increment"""
        return True

    def step_increment(self):
        """Increment and verify"""
        old_value = self.value
        self.value += 1
        assert self.value == old_value + 1, f'Expected {old_value + 1}, got {self.value}'
        print(f'  [+] Counter: {old_value} → {self.value}')

    # Decrement action
    def guard_decrement(self):
        """Can only decrement if value > 0"""
        return self.value > 0

    def step_decrement(self):
        """Decrement and verify"""
        old_value = self.value
        self.value -= 1
        assert self.value == old_value - 1, f'Expected {old_value - 1}, got {self.value}'
        assert self.value >= 0, 'Counter went negative!'
        print(f'  [-] Counter: {old_value} → {self.value}')

    # Reset action
    def guard_reset(self):
        """Can always reset"""
        return True

    def step_reset(self):
        """Reset to zero"""
        self.value = 0
        assert self.value == 0, 'Reset failed'
        print('  [↻] Counter: reset to 0')


# ============================================================================
# Model 2: Quick Counter (smoke test)
# ============================================================================


@pytest.mark.quick
@pytest.model
class QuickCounterModel(CounterModel):
    """
    Same counter but runs quick test (20 steps, 2 tests).

    Useful for:
    - Fast feedback in CI
    - Local development
    - Before committing

    Run with: pytest -m quick
    """

    pass


# ============================================================================
# Model 3: Comprehensive Counter
# ============================================================================


@pytest.mark.comprehensive
@pytest.model
class ComprehensiveCounterModel(CounterModel):
    """
    Same counter but comprehensive testing (100 steps, 100% transition coverage).

    Useful for:
    - Before release
    - Nightly CI
    - Stress testing

    Run with: pytest -m comprehensive
    """

    pass


# ============================================================================
# Model 4: Authentication Flow
# ============================================================================


@pytest.model
class AuthenticationModel:
    """
    Test an authentication state machine.

    States: logged_out → logged_in, with transition rules
    Guards prevent invalid sequences like:
    - Logging in twice without logout
    - Accessing protected resources when logged out
    """

    def __init__(self):
        self.logged_in = False
        self.user = None
        self.session_token = None

    def before_test(self):
        """Clean state before each test"""
        self.logged_in = False
        self.user = None
        self.session_token = None

    # Login
    def guard_login(self):
        """Can only login when logged out"""
        return not self.logged_in

    def step_login(self):
        """Simulate login"""
        # This would call your actual API/code
        self.logged_in = True
        self.user = 'testuser'
        self.session_token = 'token_12345'
        print(f"  [→] Login: user='{self.user}'")

    # Logout
    def guard_logout(self):
        """Can only logout when logged in"""
        return self.logged_in

    def step_logout(self):
        """Simulate logout"""
        self.logged_in = False
        self.user = None
        self.session_token = None
        print('  [←] Logout')

    # Protected operation (only when logged in)
    def guard_access_profile(self):
        """Can only access profile when logged in"""
        return self.logged_in

    def step_access_profile(self):
        """Access user profile"""
        assert self.logged_in, 'Not logged in'
        print(f'  [→] Access profile for {self.user}')

    # Session refresh
    def guard_refresh_session(self):
        """Can refresh session when logged in"""
        return self.logged_in

    def step_refresh_session(self):
        """Refresh session token"""
        old_token = self.session_token
        self.session_token = f'token_{hash(old_token)}'
        print('  [↻] Refresh session token')


# ============================================================================
# Model 5: Shopping Cart
# ============================================================================


@pytest.mark.quick
@pytest.model
class ShoppingCartModel:
    """
    Test shopping cart state machine.

    Guards ensure:
    - Can't checkout with empty cart
    - Can't add items after purchase
    - etc.
    """

    def __init__(self):
        self.items = []
        self.total = 0.0

    def before_test(self):
        self.items = []
        self.total = 0.0

    def guard_add_item(self):
        """Can always add items"""
        return True

    def step_add_item(self):
        """Add item to cart"""
        price = 10.0 + len(self.items)
        self.items.append({'id': len(self.items), 'price': price})
        self.total += price
        print(f'  [+] Add item: ${price:.2f}, total: ${self.total:.2f}')

    def guard_remove_item(self):
        """Can only remove if items exist"""
        return len(self.items) > 0

    def step_remove_item(self):
        """Remove last item from cart"""
        if self.items:
            item = self.items.pop()
            self.total -= item['price']
            print(f'  [-] Remove item: ${item["price"]:.2f}, total: ${self.total:.2f}')

    def guard_checkout(self):
        """Can only checkout with items"""
        return len(self.items) > 0

    def step_checkout(self):
        """Checkout and verify"""
        assert len(self.items) > 0, 'Cannot checkout empty cart'
        order_total = self.total
        print(f'  [→] Checkout: {len(self.items)} items, total: ${order_total:.2f}')
        self.items = []
        self.total = 0.0


# ============================================================================
# Additional Tests (regular pytest tests can coexist)
# ============================================================================


def test_counter_manual():
    """Regular pytest test alongside model tests"""
    counter = 0
    counter += 1
    assert counter == 1


class TestRegularClass:
    """Regular pytest test class still works"""

    def test_something(self):
        assert 1 + 1 == 2

    def test_another(self):
        assert len([1, 2, 3]) == 3


# ============================================================================
# Documentation
# ============================================================================

"""
RUNNING THE EXAMPLES:

1. All tests:
   pytest test_models_example.py -v

2. Quick tests only (smoke test):
   pytest test_models_example.py -m quick -v

3. Comprehensive tests only:
   pytest test_models_example.py -m comprehensive -v

4. Just count how many tests will be generated:
   pytest test_models_example.py --collect-only -q

5. Run one specific model:
   pytest test_models_example.py::CounterModel -v

6. Run with verbose output:
   pytest test_models_example.py -v -s

7. Stop on first failure:
   pytest test_models_example.py -x

8. Run in parallel (requires pytest-xdist):
   pip install pytest-xdist
   pytest test_models_example.py -n auto

EXPECTED OUTPUT:

The plugin discovers the @pytest.model classes and generates test sequences
automatically. You should see:

- CounterModel: generates 5 tests with random sequences
- QuickCounterModel: generates 2 quick tests
- ComprehensiveCounterModel: generates 10 tests until coverage is 100%
- AuthenticationModel: generates sequences testing login/logout/profile access
- ShoppingCartModel: quick smoke tests of shopping cart

Each sequence tests a different combination of allowed actions.
"""
