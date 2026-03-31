import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:5173" 
API_URL = "http://localhost:3000"

def test_health_check(page: Page):
    
    response = page.request.get(f"{API_URL}/health/")

    if not response.ok:
        response = page.request.get(f"{API_URL}/api/health/")
        
    assert response.ok, f"Health check failed with status {response.status}"
    data = response.json()
    assert data.get("status") == "healthy" or data.get("message") == "OK" or response.status == 200

def test_home_page_loads_and_has_products(page: Page):
    
    page.goto(BASE_URL)
 
    page.wait_for_load_state("networkidle")

    try:
        page.wait_for_selector(".card", timeout=5000)
    except Exception:
        pass

    cards = page.query_selector_all(".card")
    assert len(cards) >= 3, f"Expected at least 3 products on home page, found {len(cards)}"

    heading_locator = page.get_by_role("heading", name="Premium Wireless Headphones")
    expect(heading_locator).to_be_visible(timeout=5000)

    button_locator = page.get_by_role("button", name="View Details")
    expect(button_locator.first).to_be_visible(timeout=5000)

    print("✅ Base Public Test Passed: Products and buttons verified.")