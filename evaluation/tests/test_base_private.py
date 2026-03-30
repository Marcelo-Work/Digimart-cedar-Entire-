import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:5173" 

def test_health_check(page: Page):
    """Verify the backend health endpoint returns 200."""
    response = page.request.get("http://localhost:3000/api/health/")
    assert response.ok, "Health check failed"
    data = response.json()
    assert data.get("status") == "healthy"

def test_home_page_loads_and_has_products(page: Page):
    """
    Enhanced Base Test:
    1. Verify home page loads.
    2. Verify product cards exist (Boss Requirement).
    3. Verify specific seeded product titles exist.
    """
    
    page.goto(BASE_URL)
    
   
    expect(page).to_have_title("DigiMart")
    
   
    try:
        page.wait_for_selector(".card", timeout=5000)
    except Exception:
        pass

    cards = page.query_selector_all(".card")
    assert len(cards) >= 3, f"Expected at least 3 products on home page, found {len(cards)}"
   
    expect(page.locator("text=Premium Wireless Headphones")).to_be_visible()
    expect(page.locator("text=Mechanical Gaming Keyboard")).to_be_visible()
    
    buttons = page.query_selector_all("button:has-text('View Details')")
    assert len(buttons) >= 3, "View Details buttons missing or not aligned"

    print("✅ Base Public Test Passed: Products and buttons verified.")