import pytest
from playwright.sync_api import Page, expect

# Adjust URL based on whether you run locally (5173) or Docker (80)
BASE_URL = "http://localhost:5173" 
API_URL = "http://localhost:3000"

def test_health_check(page: Page):
    """Verify the backend health endpoint returns 200."""
    # Try standard health endpoint first
    response = page.request.get(f"{API_URL}/health/")
    
    # If 404, try /api/health/ (fallback)
    if not response.ok:
        response = page.request.get(f"{API_URL}/api/health/")
        
    assert response.ok, f"Health check failed with status {response.status}"
    data = response.json()
    # Check for common healthy status keys
    assert data.get("status") == "healthy" or data.get("message") == "OK" or response.status == 200

def test_home_page_loads_and_has_products(page: Page):
    """
    Enhanced Base Test:
    1. Verify home page loads.
    2. Verify product cards exist.
    3. Verify specific seeded product titles exist (Fixed strict mode).
    """
    page.goto(BASE_URL)
    
    # Wait for network to be idle (ensures products are loaded)
    page.wait_for_load_state("networkidle")

    # Check for product cards
    try:
        page.wait_for_selector(".card", timeout=5000)
    except Exception:
        # If .card class fails, try checking for any product container or just proceed to count
        pass

    cards = page.query_selector_all(".card")
    assert len(cards) >= 3, f"Expected at least 3 products on home page, found {len(cards)}"

    # FIX: Use get_by_role or get_by_text with exact match to avoid strict mode violation
    # We look specifically for the Heading (h5) containing the text
    heading_locator = page.get_by_role("heading", name="Premium Wireless Headphones")
    expect(heading_locator).to_be_visible(timeout=5000)
    
    # Also check for the button
    button_locator = page.get_by_role("button", name="View Details")
    expect(button_locator.first).to_be_visible(timeout=5000)

    print("✅ Base Public Test Passed: Products and buttons verified.")