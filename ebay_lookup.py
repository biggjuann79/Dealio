
import random

# MOCKED SANDBOX VERSION
# Replace with real eBay API when switching to production

def lookup_ebay_price(query: str):
    """
    Simulates an eBay completed listing average price lookup.
    In sandbox, this returns a random average price for demo purposes.
    """
    # Simulate a lookup failure rate
    if random.random() < 0.2:
        return None

    # Simulated average price range
    return round(random.uniform(80.0, 1200.0), 2)

def calculate_deal_score(craigslist_price, ebay_price):
    if not ebay_price or ebay_price == 0:
        return None, None, None

    savings_amount = max(0, ebay_price - craigslist_price)
    savings_percentage = (savings_amount / ebay_price) * 100
    score = min(100.0, savings_percentage * 1.5)

    return round(savings_amount, 2), round(savings_percentage, 2), round(score, 2)
