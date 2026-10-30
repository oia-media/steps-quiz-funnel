#!/usr/bin/env python3
"""
Automated Test Suite for STEPS Coffee Bar Quiz & Loyalty Card Application
Tests all backend API endpoints, validations, edge cases, and workflows.
"""

import sys
import json
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime

BASE_URL = "http://localhost:8000"

test_results = []

def run_test(test_id, category, name, fn):
    print(f"Running [{test_id}] {category}: {name}...", end=" ", flush=True)
    try:
        res = fn()
        if res.get("passed", False):
            print("✅ PASS")
            test_results.append({
                "id": test_id,
                "category": category,
                "name": name,
                "status": "PASS",
                "details": res.get("details", "")
            })
        else:
            print(f"❌ FAIL - {res.get('details', '')}")
            test_results.append({
                "id": test_id,
                "category": category,
                "name": name,
                "status": "FAIL",
                "details": res.get("details", ""),
                "expected": res.get("expected", ""),
                "actual": res.get("actual", "")
            })
    except Exception as e:
        print(f"💥 ERROR - {str(e)}")
        test_results.append({
            "id": test_id,
            "category": category,
            "name": name,
            "status": "ERROR",
            "details": str(e)
        })

def make_request(path, method="GET", data=None, headers=None, raw_body=None):
    url = f"{BASE_URL}{path}"
    h = headers or {}
    req_data = None
    if raw_body is not None:
        req_data = raw_body.encode("utf-8") if isinstance(raw_body, str) else raw_body
    elif data is not None:
        req_data = json.dumps(data).encode("utf-8")
        h.setdefault("Content-Type", "application/json")
    
    req = urllib.request.Request(url, data=req_data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode("utf-8")
            status = resp.status
            content_type = resp.headers.get("Content-Type", "")
            try:
                json_data = json.loads(body)
            except Exception:
                json_data = None
            return status, body, json_data, content_type
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            json_data = json.loads(body)
        except Exception:
            json_data = None
        return e.code, body, json_data, e.headers.get("Content-Type", "")
    except Exception as e:
        raise e

# =========================================================================
# 1. Page Routing & Static Endpoints
# =========================================================================

def test_get_root():
    code, body, _, ct = make_request("/")
    if code == 200 and "Find Your Perfect Drink" in body and "text/html" in ct:
        return {"passed": True, "details": "Served quiz.html with 200 OK"}
    return {"passed": False, "details": f"Expected 200 text/html quiz, got {code} {ct}"}

def test_get_quiz():
    code, body, _, ct = make_request("/quiz")
    if code == 200 and "Find Your Perfect Drink" in body:
        return {"passed": True, "details": "Served /quiz.html with 200 OK"}
    return {"passed": False, "details": f"Expected 200 OK, got {code}"}

def test_get_card():
    code, body, _, ct = make_request("/card")
    if code == 200 and "Digital Loyalty Card" in body:
        return {"passed": True, "details": "Served /card.html with 200 OK"}
    return {"passed": False, "details": f"Expected 200 OK, got {code}"}

def test_get_admin():
    code, body, _, ct = make_request("/admin")
    if code == 200 and "Barista POS" in body:
        return {"passed": True, "details": "Served /admin.html with 200 OK"}
    return {"passed": False, "details": f"Expected 200 OK, got {code}"}

def test_get_classic():
    code, body, _, ct = make_request("/classic")
    if code == 200 and "GOOD COFFEE" in body:
        return {"passed": True, "details": "Served /index.html with 200 OK"}
    return {"passed": False, "details": f"Expected 200 OK, got {code}"}

def test_head_routes():
    for p in ["/", "/quiz", "/card", "/admin", "/classic"]:
        code, _, _, _ = make_request(p, method="HEAD")
        if code != 200:
            return {"passed": False, "details": f"HEAD {p} returned {code}"}
    return {"passed": True, "details": "All HEAD requests returned 200 OK"}

# =========================================================================
# 2. Offers Configuration API
# =========================================================================

def test_get_offers():
    code, _, data, _ = make_request("/api/offers")
    if code == 200 and data and data.get("success") and isinstance(data.get("offers"), list):
        return {"passed": True, "details": f"Retrieved {len(data['offers'])} base offers"}
    return {"passed": False, "details": f"Expected 200 with offers list, got {code} {data}"}

def test_get_admin_offers():
    code, _, data, _ = make_request("/api/admin/offers")
    if code == 200 and data and data.get("success") and isinstance(data.get("offers"), list):
        return {"passed": True, "details": f"Retrieved {len(data['offers'])} admin offers"}
    return {"passed": False, "details": f"Expected 200 with offers list, got {code} {data}"}

def test_post_admin_offers_update():
    new_offers = [
        {"index": 1, "title": "Free Specialty Espresso", "desc": "1st Order Perk", "icon": "☕"},
        {"index": 2, "title": "25% Off Croissant", "desc": "Bakery Delight", "icon": "🥐"},
        {"index": 3, "title": "Free Milk Alternative", "desc": "Oat or Almond", "icon": "🥛"},
        {"index": 4, "title": "Buy 1 Get 1 Special", "desc": "Cold Brew", "icon": "🎁"},
        {"index": 5, "title": "Free Beverage + VIP Pin", "desc": "VIP Milestone", "icon": "🌟"}
    ]
    code, _, data, _ = make_request("/api/admin/offers", method="POST", data={"offers": new_offers, "updateExistingCards": False})
    if code == 200 and data and data.get("success") and data.get("count") == 5:
        # Verify persistence via GET /api/offers
        c2, _, d2, _ = make_request("/api/offers")
        if c2 == 200 and len(d2.get("offers", [])) == 5 and d2["offers"][0]["title"] == "Free Specialty Espresso":
            return {"passed": True, "details": "Updated 5 offers and verified persistence"}
    return {"passed": False, "details": f"Failed to update offers. Status: {code}, data: {data}"}

def test_post_admin_offers_add_slot():
    six_offers = [
        {"index": 1, "title": "Free 1st Coffee", "desc": "Signature drink free", "icon": "☕"},
        {"index": 2, "title": "20% Off Pastry", "desc": "Fresh Bakery Item", "icon": "🥐"},
        {"index": 3, "title": "Free Size Upgrade", "desc": "Coffee or Specialty Drink", "icon": "🥛"},
        {"index": 4, "title": "Buy 1 Get 1 Free", "desc": "Signature Drinks", "icon": "🎁"},
        {"index": 5, "title": "Free Dessert Slice", "desc": "Chef Specialty Cake", "icon": "🍰"},
        {"index": 6, "title": "Free Drink + VIP Status", "desc": "Grand Loyalty Reward", "icon": "🌟"}
    ]
    code, _, data, _ = make_request("/api/admin/offers", method="POST", data={"offers": six_offers, "updateExistingCards": False})
    if code == 200 and data.get("count") == 6:
        return {"passed": True, "details": "Added 6th offer slot successfully"}
    return {"passed": False, "details": f"Expected count 6, got {code} {data}"}

def test_post_admin_offers_delete_slot():
    three_offers = [
        {"index": 1, "title": "Welcome Coffee", "desc": "1st visit", "icon": "☕"},
        {"index": 2, "title": "Pastry Perk", "desc": "2nd visit", "icon": "🥐"},
        {"index": 3, "title": "Grand Prize", "desc": "3rd visit", "icon": "🌟"}
    ]
    code, _, data, _ = make_request("/api/admin/offers", method="POST", data={"offers": three_offers, "updateExistingCards": False})
    if code == 200 and data.get("count") == 3:
        return {"passed": True, "details": "Deleted slots down to 3 offers successfully"}
    return {"passed": False, "details": f"Expected count 3, got {code} {data}"}

def test_post_admin_offers_empty():
    code, _, data, _ = make_request("/api/admin/offers", method="POST", data={"offers": []})
    if code == 422:
        return {"passed": True, "details": "Rejected empty offers list with 422"}
    return {"passed": False, "details": f"Expected 422 Unprocessable Entity, got {code} {data}"}

def test_post_admin_offers_invalid_type():
    code, _, data, _ = make_request("/api/admin/offers", method="POST", data={"offers": "not-a-list"})
    if code == 422:
        return {"passed": True, "details": "Rejected non-list offers with 422"}
    return {"passed": False, "details": f"Expected 422, got {code} {data}"}

def test_post_admin_offers_preserves_existing_cards():
    """Verify that updating base offers ONLY affects new customers, preserving old customers' offers."""
    # First record existing card's stamp #2 title
    c_code, _, c_data, _ = make_request("/api/admin/cards")
    initial_title = None
    if c_code == 200 and c_data.get("cards"):
        initial_title = c_data["cards"][0].get("stamps", {}).get("2", {}).get("title")

    # Set new base offers with distinct title
    new_campaign = [
        {"index": 1, "title": "New Welcome Perk", "desc": "Welcome", "icon": "☕"},
        {"index": 2, "title": "Brand New 50% Off Perk", "desc": "Special", "icon": "🥐"},
        {"index": 3, "title": "Brand New VIP Gift", "desc": "VIP", "icon": "🌟"}
    ]
    code, _, data, _ = make_request("/api/admin/offers", method="POST", data={"offers": new_campaign})
    if code == 200 and data.get("success"):
        # Check that existing cards in DB DID NOT change to "Brand New 50% Off Perk"
        c_code2, _, c_data2, _ = make_request("/api/admin/cards")
        if c_code2 == 200 and c_data2.get("cards"):
            sample = c_data2["cards"][0]
            stamps = sample.get("stamps", {})
            current_title = stamps.get("2", {}).get("title")
            if current_title != "Brand New 50% Off Perk":
                return {"passed": True, "details": f"Existing card kept original offer '{current_title}', not overwritten by base offers change"}
            return {"passed": False, "details": f"Existing card was unexpectedly overwritten: {stamps}"}
        return {"passed": True, "details": "Base offers updated without altering existing customer records"}
    return {"passed": False, "details": f"Failed to update base offers: {code} {data}"}

# =========================================================================
# 3. Lead Registration & Phone Validation
# =========================================================================

def test_submit_valid_vodafone():
    payload = {
        "name": "QA Vodafone Tester",
        "mobile": "01092837461",
        "matchedDrink": "iced_spanish_latte",
        "answers": {"q1": "iced_spanish_latte", "q2": "iced_spanish_latte", "q3": "iced_spanish_latte"}
    }
    code, _, data, _ = make_request("/api/submit", method="POST", data=payload)
    if code == 200 and data.get("success") and data.get("card", {}).get("phone") == "01092837461":
        return {"passed": True, "details": f"Registered Vodafone 010. Pass ID: {data['card']['passId']}"}
    return {"passed": False, "details": f"Expected 200, got {code} {data}"}

def test_submit_valid_orange():
    payload = {
        "name": "QA Orange Tester",
        "mobile": "01283746192",
        "matchedDrink": "strawberry_matcha",
        "answers": {"q1": "strawberry_matcha", "q2": "strawberry_matcha", "q3": "strawberry_matcha"}
    }
    code, _, data, _ = make_request("/api/submit", method="POST", data=payload)
    if code == 200 and data.get("success") and data.get("card", {}).get("phone") == "01283746192":
        return {"passed": True, "details": f"Registered Orange 012. Pass ID: {data['card']['passId']}"}
    return {"passed": False, "details": f"Expected 200, got {code} {data}"}

def test_submit_valid_etisalat():
    payload = {
        "name": "QA Etisalat Tester",
        "mobile": "01183746291",
        "matchedDrink": "passionfruit_mojito",
        "answers": {"q1": "passionfruit_mojito", "q2": "passionfruit_mojito", "q3": "passionfruit_mojito"}
    }
    code, _, data, _ = make_request("/api/submit", method="POST", data=payload)
    if code == 200 and data.get("success") and data.get("card", {}).get("phone") == "01183746291":
        return {"passed": True, "details": f"Registered Etisalat 011. Pass ID: {data['card']['passId']}"}
    return {"passed": False, "details": f"Expected 200, got {code} {data}"}

def test_submit_valid_we():
    payload = {
        "name": "QA WE Tester",
        "mobile": "01583746291",
        "matchedDrink": "mocha_frappe",
        "answers": {"q1": "mocha_frappe", "q2": "mocha_frappe", "q3": "mocha_frappe"}
    }
    code, _, data, _ = make_request("/api/submit", method="POST", data=payload)
    if code == 200 and data.get("success") and data.get("card", {}).get("phone") == "01583746291":
        return {"passed": True, "details": f"Registered WE 015. Pass ID: {data['card']['passId']}"}
    return {"passed": False, "details": f"Expected 200, got {code} {data}"}

def test_submit_international_plus20():
    payload = {
        "name": "QA International +20",
        "mobile": "+20 10 9384 7561",
        "matchedDrink": "iced_spanish_latte",
        "answers": {}
    }
    code, _, data, _ = make_request("/api/submit", method="POST", data=payload)
    if code == 200 and data.get("success") and data.get("card", {}).get("phone") == "01093847561":
        return {"passed": True, "details": "Cleaned +20 prefix to 01093847561"}
    return {"passed": False, "details": f"Expected 200 normalized, got {code} {data}"}

def test_submit_international_0020():
    payload = {
        "name": "QA International 0020",
        "mobile": "00201093847562",
        "matchedDrink": "iced_spanish_latte",
        "answers": {}
    }
    code, _, data, _ = make_request("/api/submit", method="POST", data=payload)
    if code == 200 and data.get("success") and data.get("card", {}).get("phone") == "01093847562":
        return {"passed": True, "details": "Cleaned 0020 prefix to 01093847562"}
    return {"passed": False, "details": f"Expected 200 normalized, got {code} {data}"}

def test_submit_10digits_missing_leading_zero():
    payload = {
        "name": "QA 10 Digits Missing Zero",
        "mobile": "1093847563",
        "matchedDrink": "iced_spanish_latte",
        "answers": {}
    }
    code, _, data, _ = make_request("/api/submit", method="POST", data=payload)
    if code == 200 and data.get("success") and data.get("card", {}).get("phone") == "01093847563":
        return {"passed": True, "details": "Prepended 0 to 1093847563 -> 01093847563"}
    return {"passed": False, "details": f"Expected 200 normalized, got {code} {data}"}

def test_submit_dynamic_stamps_milestones():
    # Verify card created matches active base offers
    payload = {
        "name": "QA Stamp Milestone Verification",
        "mobile": "01093847564",
        "matchedDrink": "iced_spanish_latte",
        "answers": {}
    }
    code, _, data, _ = make_request("/api/submit", method="POST", data=payload)
    if code != 200:
        return {"passed": False, "details": f"Registration failed with {code}"}
    
    card = data.get("card", {})
    stamps = card.get("stamps", {})
    
    # Fetch current base offers
    _, _, off_data, _ = make_request("/api/offers")
    expected_count = len(off_data.get("offers", []))
    
    if len(stamps) != expected_count:
        return {"passed": False, "details": f"Expected {expected_count} stamps, got {len(stamps)}"}
    
    s1 = stamps.get("1", {})
    if s1.get("status") != "available" or not s1.get("unlockedAt"):
        return {"passed": False, "details": f"Stamp 1 not 'available' or unlockedAt missing: {s1}"}
    
    for idx in range(2, expected_count + 1):
        s_idx = stamps.get(str(idx), {})
        if s_idx.get("status") != "locked" or s_idx.get("unlockedAt") is not None:
            return {"passed": False, "details": f"Stamp {idx} not locked or unlockedAt not null: {s_idx}"}
    
    if card.get("cardActive") is not False:
        return {"passed": False, "details": f"Expected initial cardActive=False, got {card.get('cardActive')}"}
    
    return {"passed": True, "details": f"Card created with {expected_count} stamps matching active offers, stamp 1 unlocked, cardActive=False"}

def test_submit_first_deal_matches_quiz_drink():
    # Test Passionfruit Mojito (as in user screenshot)
    payload_mojito = {
        "name": "Quiz Mojito Tester",
        "mobile": "01077182934",
        "matchedDrink": "passionfruit_mojito"
    }
    code, _, data, _ = make_request("/api/submit", method="POST", data=payload_mojito)
    if code != 200:
        return {"passed": False, "details": f"Mojito registration failed with code {code}"}
    
    card = data.get("card", {})
    s1 = card.get("stamps", {}).get("1", {})
    if s1.get("title") != "Free Passionfruit Mojito":
        return {"passed": False, "details": f"Expected stamp 1 title 'Free Passionfruit Mojito', got '{s1.get('title')}'"}
    if s1.get("desc") != "Your Quiz Signature Match • 100% Free Drink":
        return {"passed": False, "details": f"Expected stamp 1 desc 'Your Quiz Signature Match • 100% Free Drink', got '{s1.get('desc')}'"}
    if s1.get("icon") != "🍹":
        return {"passed": False, "details": f"Expected stamp 1 icon '🍹', got '{s1.get('icon')}'"}

    # Also test Strawberry Matcha
    payload_matcha = {
        "name": "Quiz Matcha Tester",
        "mobile": "01077182935",
        "matchedDrink": "strawberry_matcha"
    }
    code2, _, data2, _ = make_request("/api/submit", method="POST", data=payload_matcha)
    if code2 != 200:
        return {"passed": False, "details": f"Matcha registration failed with code {code2}"}
    
    s1_matcha = data2.get("card", {}).get("stamps", {}).get("1", {})
    if s1_matcha.get("title") != "Free Strawberry Matcha" or s1_matcha.get("icon") != "🍵":
        return {"passed": False, "details": f"Matcha stamp 1 mismatch: {s1_matcha}"}

    return {"passed": True, "details": "Deal 1 in card is dynamically set to 'Free [Drink]' with match subtitle and matching drink icon"}

# --- Invalid Formats & Edge Cases ---

def test_submit_invalid_length_10_digits():
    payload = {"name": "Short Mobile", "mobile": "0101928374", "matchedDrink": "iced_spanish_latte"}
    code, _, data, _ = make_request("/api/submit", method="POST", data=payload)
    if code == 422:
        return {"passed": True, "details": "10-digit number rejected with 422"}
    return {"passed": False, "details": f"Expected 422, got {code} {data}"}

def test_submit_invalid_length_12_digits():
    payload = {"name": "Long Mobile", "mobile": "010192837465", "matchedDrink": "iced_spanish_latte"}
    code, _, data, _ = make_request("/api/submit", method="POST", data=payload)
    if code == 422:
        return {"passed": True, "details": "12-digit number rejected with 422"}
    return {"passed": False, "details": f"Expected 422, got {code} {data}"}

def test_submit_invalid_prefix_013():
    payload = {"name": "Bad Network 013", "mobile": "01392837461", "matchedDrink": "iced_spanish_latte"}
    code, _, data, _ = make_request("/api/submit", method="POST", data=payload)
    if code == 422:
        return {"passed": True, "details": "Prefix 013 rejected with 422"}
    return {"passed": False, "details": f"Expected 422, got {code} {data}"}

def test_submit_invalid_prefix_014():
    payload = {"name": "Bad Network 014", "mobile": "01492837461", "matchedDrink": "iced_spanish_latte"}
    code, _, data, _ = make_request("/api/submit", method="POST", data=payload)
    if code == 422:
        return {"passed": True, "details": "Prefix 014 rejected with 422"}
    return {"passed": False, "details": f"Expected 422, got {code} {data}"}

def test_submit_invalid_prefix_016():
    payload = {"name": "Bad Network 016", "mobile": "01692837461", "matchedDrink": "iced_spanish_latte"}
    code, _, data, _ = make_request("/api/submit", method="POST", data=payload)
    if code == 422:
        return {"passed": True, "details": "Prefix 016 rejected with 422"}
    return {"passed": False, "details": f"Expected 422, got {code} {data}"}

def test_submit_invalid_chars():
    payload = {"name": "Alpha Mobile", "mobile": "010abcd3746", "matchedDrink": "iced_spanish_latte"}
    code, _, data, _ = make_request("/api/submit", method="POST", data=payload)
    if code == 422:
        return {"passed": True, "details": "Alphanumeric mobile rejected with 422"}
    return {"passed": False, "details": f"Expected 422, got {code} {data}"}

# --- Anti-Fraud & Fake Number Detection ---

def test_submit_fake_repetitive_zeros():
    payload = {"name": "Repetitive Zeros", "mobile": "01000000000", "matchedDrink": "iced_spanish_latte"}
    code, _, data, _ = make_request("/api/submit", method="POST", data=payload)
    if code == 422:
        return {"passed": True, "details": "01000000000 blocked with 422"}
    return {"passed": False, "details": f"Expected 422, got {code} {data}"}

def test_submit_fake_repetitive_ones():
    payload = {"name": "Repetitive Ones", "mobile": "01111111111", "matchedDrink": "iced_spanish_latte"}
    code, _, data, _ = make_request("/api/submit", method="POST", data=payload)
    if code == 422:
        return {"passed": True, "details": "01111111111 blocked with 422"}
    return {"passed": False, "details": f"Expected 422, got {code} {data}"}

def test_submit_fake_sequential_ascending_1():
    payload = {"name": "Sequential 1", "mobile": "01012345678", "matchedDrink": "iced_spanish_latte"}
    code, _, data, _ = make_request("/api/submit", method="POST", data=payload)
    if code == 422:
        return {"passed": True, "details": "01012345678 blocked with 422"}
    return {"passed": False, "details": f"Expected 422, got {code} {data}"}

def test_submit_fake_sequential_ascending_2():
    payload = {"name": "Sequential 2", "mobile": "01123456789", "matchedDrink": "iced_spanish_latte"}
    code, _, data, _ = make_request("/api/submit", method="POST", data=payload)
    if code == 422:
        return {"passed": True, "details": "01123456789 blocked with 422"}
    return {"passed": False, "details": f"Expected 422, got {code} {data}"}

def test_submit_fake_sequential_ascending_3():
    payload = {"name": "Sequential 3", "mobile": "01234567890", "matchedDrink": "iced_spanish_latte"}
    code, _, data, _ = make_request("/api/submit", method="POST", data=payload)
    if code == 422:
        return {"passed": True, "details": "01234567890 blocked with 422"}
    return {"passed": False, "details": f"Expected 422, got {code} {data}"}

def test_submit_fake_sequential_descending():
    payload = {"name": "Sequential Desc", "mobile": "01087654321", "matchedDrink": "iced_spanish_latte"}
    code, _, data, _ = make_request("/api/submit", method="POST", data=payload)
    if code == 422:
        return {"passed": True, "details": "01087654321 blocked with 422"}
    return {"passed": False, "details": f"Expected 422, got {code} {data}"}

def test_submit_fake_repetitive_chunks():
    payload = {"name": "Repeated Chunks", "mobile": "01012121212", "matchedDrink": "iced_spanish_latte"}
    code, _, data, _ = make_request("/api/submit", method="POST", data=payload)
    if code == 422:
        return {"passed": True, "details": "01012121212 blocked with 422"}
    return {"passed": False, "details": f"Expected 422, got {code} {data}"}

def test_submit_fake_low_entropy():
    payload = {"name": "Low Entropy", "mobile": "01012122112", "matchedDrink": "iced_spanish_latte"}
    code, _, data, _ = make_request("/api/submit", method="POST", data=payload)
    if code == 422:
        return {"passed": True, "details": "01012122112 (<4 unique digits) blocked with 422"}
    return {"passed": False, "details": f"Expected 422, got {code} {data}"}

def test_submit_fake_blacklisted_number():
    payload = {"name": "Blacklisted", "mobile": "01512345678", "matchedDrink": "iced_spanish_latte"}
    code, _, data, _ = make_request("/api/submit", method="POST", data=payload)
    if code == 422:
        return {"passed": True, "details": "01512345678 blocked with 422"}
    return {"passed": False, "details": f"Expected 422, got {code} {data}"}

def test_submit_short_name():
    payload = {"name": "A", "mobile": "01093847599", "matchedDrink": "iced_spanish_latte"}
    code, _, data, _ = make_request("/api/submit", method="POST", data=payload)
    if code == 422:
        return {"passed": True, "details": "Short name (<2 chars) rejected with 422"}
    return {"passed": False, "details": f"Expected 422, got {code} {data}"}

def test_submit_duplicate_registration_status():
    """
    User Prompt Requirement:
    - Duplicate submission response: verifying 409 conflict & redirect payload
    """
    phone = "01092837461" # Registered earlier in test_submit_valid_vodafone
    payload = {
        "name": "Duplicate Submitter",
        "mobile": phone,
        "matchedDrink": "mocha_frappe",
        "answers": {}
    }
    code, _, data, _ = make_request("/api/submit", method="POST", data=payload)
    has_already_registered = (data and data.get("alreadyRegistered") is True)
    has_card = (data and "card" in data)
    
    # Prompt asks for 409 Conflict verification
    if code == 409 and has_already_registered and has_card:
        return {"passed": True, "details": "Returned 409 Conflict with alreadyRegistered: true and card payload"}
    elif code == 200 and has_already_registered and has_card:
        return {
            "passed": False,
            "details": f"Server returned 200 OK instead of 409 Conflict for duplicate registration. alreadyRegistered={has_already_registered}",
            "expected": "HTTP 409 Conflict",
            "actual": f"HTTP {code} OK"
        }
    return {
        "passed": False,
        "details": f"Unexpected response for duplicate registration: HTTP {code}, payload: {data}"
    }

# =========================================================================
# 4. Card Pass Operations
# =========================================================================

def test_card_get_valid():
    phone = "01092837461"
    code, _, data, _ = make_request(f"/api/card?phone={phone}")
    if code == 200 and data.get("success") and data.get("card", {}).get("phone") == phone:
        return {"passed": True, "details": f"Found card for {phone}"}
    return {"passed": False, "details": f"Expected 200 with card, got {code} {data}"}

def test_card_get_normalized_plus20():
    phone_clean = "01092837461"
    raw_param = urllib.parse.quote("+20 109 283-7461")
    code, _, data, _ = make_request(f"/api/card?phone={raw_param}")
    if code == 200 and data.get("success") and data.get("card", {}).get("phone") == phone_clean:
        return {"passed": True, "details": "Normalized raw international phone parameter"}
    return {"passed": False, "details": f"Expected 200 with normalized phone, got {code} {data}"}

def test_card_get_nonexistent():
    code, _, data, _ = make_request("/api/card?phone=01099999999")
    if code == 404 and data.get("success") is False:
        return {"passed": True, "details": "Returned 404 for nonexistent card"}
    return {"passed": False, "details": f"Expected 404, got {code} {data}"}

def test_card_get_missing_phone():
    code, _, data, _ = make_request("/api/card")
    if code == 404 and data.get("success") is False:
        return {"passed": True, "details": "Returned 404 for missing phone parameter"}
    return {"passed": False, "details": f"Expected 404, got {code} {data}"}

def test_card_activate_valid():
    phone = "01092837461"
    code, _, data, _ = make_request("/api/card/activate", method="POST", data={"phone": phone})
    if code == 200 and data.get("success") and data.get("card", {}).get("cardActive") is True:
        return {"passed": True, "details": f"Activated card for {phone}, cardActive=True"}
    return {"passed": False, "details": f"Expected 200 cardActive=True, got {code} {data}"}

def test_card_activate_nonexistent():
    code, _, data, _ = make_request("/api/card/activate", method="POST", data={"phone": "01099999999"})
    if code == 404:
        return {"passed": True, "details": "Returned 404 for activating nonexistent card"}
    return {"passed": False, "details": f"Expected 404, got {code} {data}"}

# =========================================================================
# 5. POS Admin Operations
# =========================================================================

def test_admin_cards_list():
    code, _, data, _ = make_request("/api/admin/cards")
    if code == 200 and data.get("success") and isinstance(data.get("cards"), list):
        return {"passed": True, "details": f"Returned {data.get('count')} member cards"}
    return {"passed": False, "details": f"Expected 200 with cards list, got {code} {data}"}

def test_admin_cards_search_by_phone():
    phone = "01092837461"
    code, _, data, _ = make_request(f"/api/admin/cards?q={phone}")
    if code == 200 and data.get("success") and any(c.get("phone") == phone for c in data.get("cards", [])):
        return {"passed": True, "details": f"Found member matching phone {phone}"}
    return {"passed": False, "details": f"Expected cards matching {phone}, got {code} {data}"}

def test_admin_cards_search_by_name():
    code, _, data, _ = make_request("/api/admin/cards?q=Vodafone")
    if code == 200 and data.get("success") and len(data.get("cards", [])) > 0:
        return {"passed": True, "details": "Found member matching name 'Vodafone'"}
    return {"passed": False, "details": f"Expected cards matching 'Vodafone', got {code} {data}"}

def test_admin_search_endpoint():
    """
    User Prompt Requirement:
    - POS Admin operations: GET /api/admin/search?phone=...
    """
    phone = "01092837461"
    code, _, data, _ = make_request(f"/api/admin/search?phone={phone}")
    if code == 200 and data and (data.get("success") or "card" in data or "cards" in data):
        return {"passed": True, "details": f"Endpoint GET /api/admin/search returned 200"}
    return {
        "passed": False,
        "details": f"Endpoint GET /api/admin/search returned HTTP {code} (endpoint missing in server.py)",
        "expected": "HTTP 200 OK",
        "actual": f"HTTP {code}"
    }

def test_admin_stamp_redeem():
    phone = "01092837461"
    payload = {"phone": phone, "stampIndex": "1", "action": "redeem"}
    code, _, data, _ = make_request("/api/admin/stamp", method="POST", data=payload)
    if code == 200 and data.get("success"):
        stamps = data.get("card", {}).get("stamps", {})
        s1 = stamps.get("1", {})
        if s1.get("status") == "redeemed" and s1.get("redeemedAt"):
            return {"passed": True, "details": f"Stamp 1 status updated to 'redeemed' with timestamp {s1['redeemedAt']}"}
        return {"passed": False, "details": f"Stamp 1 not redeemed: {s1}"}
    return {"passed": False, "details": f"Expected 200, got {code} {data}"}

def test_admin_stamp_unlock():
    phone = "01092837461"
    payload = {"phone": phone, "stampIndex": "2", "action": "unlock"}
    code, _, data, _ = make_request("/api/admin/stamp", method="POST", data=payload)
    if code == 200 and data.get("success"):
        stamps = data.get("card", {}).get("stamps", {})
        s2 = stamps.get("2", {})
        if s2.get("status") == "available" and s2.get("unlockedAt"):
            return {"passed": True, "details": f"Stamp 2 status updated to 'available' with timestamp {s2['unlockedAt']}"}
        return {"passed": False, "details": f"Stamp 2 not unlocked: {s2}"}
    return {"passed": False, "details": f"Expected 200, got {code} {data}"}

def test_admin_stamp_reset():
    phone = "01092837461"
    payload = {"phone": phone, "stampIndex": "2", "action": "reset"}
    code, _, data, _ = make_request("/api/admin/stamp", method="POST", data=payload)
    if code == 200 and data.get("success"):
        stamps = data.get("card", {}).get("stamps", {})
        s2 = stamps.get("2", {})
        if s2.get("status") == "locked" and s2.get("unlockedAt") is None and s2.get("redeemedAt") is None:
            return {"passed": True, "details": "Stamp 2 reset back to 'locked' with null timestamps"}
        return {"passed": False, "details": f"Stamp 2 not reset: {s2}"}
    return {"passed": False, "details": f"Expected 200, got {code} {data}"}

def test_admin_stamp_out_of_range():
    phone = "01092837461"
    payload = {"phone": phone, "stampIndex": "99", "action": "redeem"}
    code, _, data, _ = make_request("/api/admin/stamp", method="POST", data=payload)
    if code == 400 and data.get("success") is False:
        return {"passed": True, "details": "Out-of-range stamp index 99 returned 400 Bad Request"}
    return {"passed": False, "details": f"Expected 400, got {code} {data}"}

def test_admin_stamp_invalid_action():
    phone = "01092837461"
    payload = {"phone": phone, "stampIndex": "1", "action": "destroy_stamp"}
    code, _, data, _ = make_request("/api/admin/stamp", method="POST", data=payload)
    # Server should reject invalid actions with 400 or 422
    if code in [400, 422] and data.get("success") is False:
        return {"passed": True, "details": f"Invalid action rejected with {code}"}
    return {
        "passed": False,
        "details": f"Server silently accepted invalid action 'destroy_stamp' with HTTP {code} {data}",
        "expected": "HTTP 400 or 422 error",
        "actual": f"HTTP {code}"
    }

def test_admin_stamp_nonexistent_phone():
    payload = {"phone": "01000000001", "stampIndex": "1", "action": "redeem"}
    code, _, data, _ = make_request("/api/admin/stamp", method="POST", data=payload)
    if code == 404:
        return {"passed": True, "details": "Nonexistent phone returned 404"}
    return {"passed": False, "details": f"Expected 404, got {code} {data}"}

# =========================================================================
# 5B. Customer Lifecycle: Ban, Unban, Delete & Date Filters
# =========================================================================

def test_admin_ban_customer():
    phone = "01092837461"
    code, _, data, _ = make_request("/api/admin/customer/ban", method="POST", data={"phone": phone, "action": "ban"})
    if code == 200 and data.get("success") and data.get("isBanned") is True:
        return {"passed": True, "details": "Customer successfully banned via /api/admin/customer/ban"}
    return {"passed": False, "details": f"Expected 200 isBanned=True, got {code} {data}"}

def test_banned_customer_blocked_on_submit():
    phone = "01092837461"
    payload = {"name": "Blocked Person", "mobile": phone, "matchedDrink": "iced_spanish_latte"}
    code, _, data, _ = make_request("/api/submit", method="POST", data=payload)
    if code == 403 and data.get("isBanned") is True:
        return {"passed": True, "details": "Banned customer successfully rejected on /api/submit with HTTP 403 Forbidden"}
    return {"passed": False, "details": f"Expected 403 Forbidden, got {code} {data}"}

def test_banned_customer_blocked_on_card():
    phone = "01092837461"
    code, _, data, _ = make_request(f"/api/card?phone={phone}")
    if code == 403 and data.get("isBanned") is True:
        return {"passed": True, "details": "Banned customer access blocked on /api/card with HTTP 403 Forbidden"}
    return {"passed": False, "details": f"Expected 403, got {code} {data}"}

def test_admin_unban_customer():
    phone = "01092837461"
    code, _, data, _ = make_request("/api/admin/customer/ban", method="POST", data={"phone": phone, "action": "unban"})
    if code == 200 and data.get("success") and data.get("isBanned") is False:
        return {"passed": True, "details": "Customer successfully unbanned via /api/admin/customer/ban"}
    return {"passed": False, "details": f"Expected 200 isBanned=False, got {code} {data}"}

def test_admin_delete_customer():
    phone = "01077182998"
    reg_payload = {"name": "Delete Tester", "mobile": phone, "matchedDrink": "passionfruit_mojito"}
    make_request("/api/submit", method="POST", data=reg_payload)

    del_payload = {"phone": phone}
    code, _, data, _ = make_request("/api/admin/customer/delete", method="POST", data=del_payload)
    if code == 200 and data.get("success"):
        c_code, _, _, _ = make_request(f"/api/card?phone={phone}")
        if c_code == 404:
            return {"passed": True, "details": "Customer deleted from cards DB; subsequent card lookup returns 404"}
        return {"passed": False, "details": f"Card still returned {c_code} after deletion"}
    return {"passed": False, "details": f"Delete request failed with {code} {data}"}

def test_deleted_customer_can_re_register():
    phone = "01077182998"
    reg_payload = {"name": "Re-registered User", "mobile": phone, "matchedDrink": "mocha_frappe"}
    code, _, data, _ = make_request("/api/submit", method="POST", data=reg_payload)
    if code == 200 and data.get("success"):
        card = data.get("card", {})
        if card.get("phone") == phone and card.get("name") == "Re-registered User":
            # Clean up after test
            make_request("/api/admin/customer/delete", method="POST", data={"phone": phone})
            return {"passed": True, "details": "Deleted customer successfully allowed to re-enter number and generate new card"}
    return {"passed": False, "details": f"Re-registration failed: expected 200, got {code} {data}"}

def test_deleted_customer_restores_old_data():
    phone = "01088776655"
    # 1. Register customer
    code, _, data, _ = make_request("/api/submit", method="POST", data={"name": "Loyal Returning Guest", "mobile": phone, "matchedDrink": "iced_spanish_latte"})
    orig_pass_id = data.get("card", {}).get("passId")

    # 2. Redeem stamp 1 and unlock stamp 2
    make_request("/api/admin/stamp", method="POST", data={"phone": phone, "stampIndex": "1", "action": "redeem"})
    make_request("/api/admin/stamp", method="POST", data={"phone": phone, "stampIndex": "2", "action": "unlock"})

    # 3. Delete customer
    del_code, _, del_data, _ = make_request("/api/admin/customer/delete", method="POST", data={"phone": phone})
    assert del_code == 200, "Delete failed"

    # Lookup returns 404 while deleted
    c_code, _, _, _ = make_request(f"/api/card?phone={phone}")
    assert c_code == 404, "Card still returned 200 while deleted"

    # 4. Customer returns and submits quiz again
    ret_code, _, ret_data, _ = make_request("/api/submit", method="POST", data={"name": "Loyal Returning Guest", "mobile": phone, "matchedDrink": "iced_spanish_latte"})
    if ret_code == 200 and ret_data.get("success"):
        card = ret_data.get("card", {})
        # Verify old data is preserved:
        is_same_pass = (card.get("passId") == orig_pass_id)
        is_stamp1_redeemed = (card.get("stamps", {}).get("1", {}).get("status") == "redeemed")
        is_stamp2_unlocked = (card.get("stamps", {}).get("2", {}).get("status") == "available")

        # Cleanup
        make_request("/api/admin/customer/delete", method="POST", data={"phone": phone})

        if is_same_pass and is_stamp1_redeemed and is_stamp2_unlocked:
            return {"passed": True, "details": "Returning customer successfully restored with previous pass ID, redeemed stamp 1, and unlocked stamp 2!"}
        return {"passed": False, "details": f"Old data not restored: same_pass={is_same_pass}, stamp1_redeemed={is_stamp1_redeemed}, stamp2_unlocked={is_stamp2_unlocked}"}
    return {"passed": False, "details": f"Return submission failed with code {ret_code}: {ret_data}"}

def test_admin_cards_date_filtering():
    code, _, data, _ = make_request("/api/admin/cards?from_date=2026-01-01&to_date=2026-12-31")
    if code == 200 and data.get("success") and "cards" in data:
        return {"passed": True, "details": f"Date filtering returned {data.get('count')} cards out of {data.get('total')}"}
    return {"passed": False, "details": f"Expected 200 with cards array, got {code} {data}"}

# =========================================================================
# 5C. Selective Customer Offer Upgrades & Offers History Audit Trail
# =========================================================================

def test_admin_update_customer_offers_single():
    phone = "01092837461"
    test_offers = [
        {"index": 1, "title": "Free 1st Coffee", "desc": "Signature drink free", "icon": "☕"},
        {"index": 2, "title": "25% Off Artisan Pastry", "desc": "Fresh bakery treat", "icon": "🥐"},
        {"index": 3, "title": "Free Size Upgrade", "desc": "Coffee or Specialty Drink", "icon": "🥛"},
        {"index": 4, "title": "Buy 1 Get 1 Free", "desc": "Signature Drinks", "icon": "🎁"},
        {"index": 5, "title": "Free Drink + VIP Status", "desc": "Grand Loyalty Reward", "icon": "🌟"}
    ]
    make_request("/api/admin/offers", method="POST", data={"offers": test_offers})

    code, _, data, _ = make_request("/api/admin/customer/update-offers", method="POST", data={"phone": phone, "reason": "Test single customer upgrade"})
    if code == 200 and data.get("success") and data.get("updatedCount") == 1:
        c_code, _, card_data, _ = make_request(f"/api/card?phone={phone}")
        if c_code == 200:
            card = card_data.get("card", {})
            stamps = card.get("stamps", {})
            history = card.get("offersHistory", [])
            if len(stamps) == 5 and stamps.get("2", {}).get("title") == "25% Off Artisan Pastry":
                if len(history) >= 1 and history[-1].get("reason") == "Test single customer upgrade":
                    return {"passed": True, "details": "Customer successfully upgraded to active offers; previous snapshot archived in offersHistory"}
                return {"passed": False, "details": f"Stamps updated but offersHistory missing or empty: {history}"}
            return {"passed": False, "details": f"Stamps did not update to new campaign: {stamps}"}
    return {"passed": False, "details": f"Expected 200 updatedCount=1, got {code} {data}"}

def test_admin_update_customer_offers_batch():
    phones = ["01283746192", "01183746291"]
    code, _, data, _ = make_request("/api/admin/customer/update-offers", method="POST", data={"phones": phones, "reason": "Batch upgrade test"})
    if code == 200 and data.get("success") and data.get("updatedCount") == 2:
        return {"passed": True, "details": "Successfully batch upgraded 2 customers and recorded history for each"}
    return {"passed": False, "details": f"Expected 200 updatedCount=2, got {code} {data}"}

def test_admin_customer_history_endpoint():
    phone = "01092837461"
    code, _, data, _ = make_request(f"/api/admin/customer/history?phone={phone}")
    if code == 200 and data.get("success") and data.get("historyCount", 0) >= 1:
        history = data.get("history", [])
        last_snap = history[-1]
        if "stamps" in last_snap and "archivedAt" in last_snap:
            return {"passed": True, "details": f"History endpoint returned {len(history)} archived version(s) with timestamps and stamp states"}
    return {"passed": False, "details": f"Expected 200 with history array, got {code} {data}"}

def test_admin_customer_multiple_upgrades_accumulate_history():
    phone = "01092837461"
    five_offers = [
        {"index": 1, "title": "Free 1st Coffee", "desc": "Signature drink free", "icon": "☕"},
        {"index": 2, "title": "20% Off Pastry", "desc": "Fresh Bakery Item", "icon": "🥐"},
        {"index": 3, "title": "Free Size Upgrade", "desc": "Coffee or Specialty Drink", "icon": "🥛"},
        {"index": 4, "title": "Buy 1 Get 1 Free", "desc": "Signature Drinks", "icon": "🎁"},
        {"index": 5, "title": "Free Drink + VIP Status", "desc": "Grand Loyalty Reward", "icon": "🌟"}
    ]
    make_request("/api/admin/offers", method="POST", data={"offers": five_offers})
    code, _, data, _ = make_request("/api/admin/customer/update-offers", method="POST", data={"phone": phone, "reason": "Second upgrade milestone"})
    if code == 200 and data.get("success"):
        c_code, _, hist_data, _ = make_request(f"/api/admin/customer/history?phone={phone}")
        if c_code == 200 and hist_data.get("historyCount", 0) >= 2:
            return {"passed": True, "details": f"Customer accumulated {hist_data.get('historyCount')} historical snapshots across multiple upgrades"}
        return {"passed": False, "details": f"Expected >=2 history entries, got {hist_data}"}
    return {"passed": False, "details": f"Second upgrade failed: {code} {data}"}

# =========================================================================
# 6. Malformed Payloads & Edge Cases
# =========================================================================

def test_malformed_json_submit():
    code, _, data, _ = make_request("/api/submit", method="POST", raw_body="{invalid-json", headers={"Content-Type": "application/json"})
    if code == 400:
        return {"passed": True, "details": "Malformed JSON returned 400 Bad Request"}
    return {"passed": False, "details": f"Expected 400, got {code} {data}"}

def test_json_array_payload_submit():
    """Testing server robustness when client sends JSON array instead of dict."""
    try:
        code, _, data, _ = make_request("/api/submit", method="POST", raw_body="[1, 2, 3]", headers={"Content-Type": "application/json"})
        if code in [400, 422]:
            return {"passed": True, "details": f"JSON array payload safely rejected with {code}"}
        return {
            "passed": False,
            "details": f"Expected 400 or 422 for non-dict JSON array, got {code} {data}",
            "expected": "HTTP 400 or 422",
            "actual": f"HTTP {code}"
        }
    except urllib.error.HTTPError as e:
        if e.code == 500:
            return {
                "passed": False,
                "details": "Server crashed with HTTP 500 (AttributeError: 'list' object has no attribute 'get')",
                "expected": "HTTP 400 or 422",
                "actual": "HTTP 500 Internal Server Error"
            }
        return {"passed": False, "details": f"HTTPError {e.code}"}

def test_unknown_endpoint_get():
    code, _, _, _ = make_request("/api/unknown_endpoint")
    if code == 404:
        return {"passed": True, "details": "Unknown GET endpoint returned 404"}
    return {"passed": False, "details": f"Expected 404, got {code}"}

def test_unknown_endpoint_post():
    code, _, _, _ = make_request("/api/unknown_endpoint", method="POST", data={"foo": "bar"})
    if code == 404:
        return {"passed": True, "details": "Unknown POST endpoint returned 404"}
    return {"passed": False, "details": f"Expected 404, got {code}"}

def test_card_activation_records_activated_at():
    phone = "01099887766"
    payload = {
        "name": "Activation Timestamp Tester",
        "mobile": phone,
        "matchedDrink": "iced_spanish_latte",
        "answers": {"q1": "iced_spanish_latte"}
    }
    c1, _, d1, _ = make_request("/api/submit", method="POST", data=payload)
    if c1 != 200:
        return {"passed": False, "details": f"Submit failed: {c1} {d1}"}

    card1 = d1.get("card", {})
    if card1.get("activatedAt") is not None:
        return {"passed": False, "details": f"activatedAt should initially be None, got: {card1.get('activatedAt')}"}

    # Activate the card
    c2, _, d2, _ = make_request("/api/card/activate", method="POST", data={"phone": phone})
    if c2 != 200:
        return {"passed": False, "details": f"Activate failed: {c2} {d2}"}

    card2 = d2.get("card", {})
    activated_at = card2.get("activatedAt")
    if not activated_at:
        return {"passed": False, "details": "activatedAt missing after activation"}

    # Verify persistence via GET /api/card
    c3, _, d3, _ = make_request(f"/api/card?phone={phone}")
    if c3 == 200 and d3.get("card", {}).get("activatedAt") == activated_at:
        return {"passed": True, "details": f"Card activation timestamp successfully recorded and persisted: {activated_at}"}
    return {"passed": False, "details": f"GET /api/card failed or activatedAt mismatch: {c3} {d3}"}

def test_quiz_finished_at_timestamp():
    phone = "01099887767"
    payload = {
        "name": "Quiz Finished Timestamp Tester",
        "mobile": phone,
        "matchedDrink": "mocha_frappe",
        "answers": {"q1": "mocha_frappe"}
    }
    c, _, d, _ = make_request("/api/submit", method="POST", data=payload)
    if c != 200:
        return {"passed": False, "details": f"Submit failed: {c} {d}"}

    card = d.get("card", {})
    quiz_finished_at = card.get("quizFinishedAt")
    if not quiz_finished_at:
        return {"passed": False, "details": "quizFinishedAt missing in card returned by /api/submit"}

    # Verify ISO timestamp format
    try:
        from datetime import datetime
        _ = datetime.fromisoformat(quiz_finished_at)
        return {"passed": True, "details": f"quizFinishedAt recorded correctly: {quiz_finished_at}"}
    except Exception as e:
        return {"passed": False, "details": f"Invalid ISO format for quizFinishedAt: {quiz_finished_at} ({e})"}

def test_stamp_timestamps_persisted():
    phone = "01099887768"
    payload = {
        "name": "Stamp Timestamps Tester",
        "mobile": phone,
        "matchedDrink": "strawberry_matcha",
        "answers": {"q1": "strawberry_matcha"}
    }
    c1, _, d1, _ = make_request("/api/submit", method="POST", data=payload)
    if c1 != 200:
        return {"passed": False, "details": f"Submit failed: {c1}"}

    card1 = d1.get("card", {})
    s1 = card1.get("stamps", {}).get("1", {})
    if not s1.get("unlockedAt"):
        return {"passed": False, "details": "Stamp #1 unlockedAt timestamp should be set upon submit"}

    # Redeem Stamp #1
    c2, _, d2, _ = make_request("/api/admin/stamp", method="POST", data={"phone": phone, "stampIndex": "1", "action": "redeem"})
    if c2 != 200:
        return {"passed": False, "details": f"Redeem stamp #1 failed: {c2} {d2}"}

    card2 = d2.get("card", {})
    s1_after = card2.get("stamps", {}).get("1", {})
    redeemed_at = s1_after.get("redeemedAt")
    if not redeemed_at:
        return {"passed": False, "details": "Stamp #1 redeemedAt missing after redeem action"}

    # Unlock Stamp #2
    c3, _, d3, _ = make_request("/api/admin/stamp", method="POST", data={"phone": phone, "stampIndex": "2", "action": "unlock"})
    if c3 != 200:
        return {"passed": False, "details": f"Unlock stamp #2 failed: {c3} {d3}"}

    card3 = d3.get("card", {})
    s2_after = card3.get("stamps", {}).get("2", {})
    if not s2_after.get("unlockedAt"):
        return {"passed": False, "details": "Stamp #2 unlockedAt missing after unlock action"}

    return {"passed": True, "details": f"Stamp timestamps verified: unlockedAt and redeemedAt ({redeemed_at}) persisted"}

def test_admin_cards_timestamps_and_date_filtering():
    phone = "01099887769"
    payload = {
        "name": "Admin Timestamps & Date Filter Tester",
        "mobile": phone,
        "matchedDrink": "passionfruit_mojito",
        "answers": {"q1": "passionfruit_mojito"}
    }
    c1, _, d1, _ = make_request("/api/submit", method="POST", data=payload)
    if c1 != 200:
        return {"passed": False, "details": f"Submit failed: {c1}"}

    # Query admin cards
    c2, _, d2, _ = make_request(f"/api/admin/cards?q={phone}")
    if c2 != 200 or not d2.get("cards"):
        return {"passed": False, "details": f"Admin search failed: {c2} {d2}"}

    card = d2["cards"][0]
    if "quizFinishedAt" not in card:
        return {"passed": False, "details": "quizFinishedAt missing from admin cards endpoint"}

    # Verify date filtering with today
    from datetime import datetime
    today_str = datetime.now().strftime("%Y-%m-%d")
    c3, _, d3, _ = make_request(f"/api/admin/cards?q={phone}&from_date={today_str}&to_date={today_str}")
    if c3 == 200 and len(d3.get("cards", [])) >= 1:
        return {"passed": True, "details": f"Admin endpoint verified timestamps & date range filter with {today_str}"}
    return {"passed": False, "details": f"Admin date range query failed: {c3} {d3}"}


def main():
    print("=" * 70)
    print(" ☕ STEPS COFFEE BAR QA TEST SUITE - EXECUTION START")
    print("=" * 70)

    # Clean up any residual test numbers from previous runs for idempotent execution
    test_phones = {
        "01092837461",
        "01283746192",
        "01183746291",
        "01583746291",
        "01093847561",
        "01093847562",
        "01093847563",
        "01093847564",
        "01077182934",
        "01077182935",
        "01077182998",
        "01099887766",
        "01099887767",
        "01099887768",
        "01099887769",
    }
    try:
        import os
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cards_db.json")
        if os.path.exists(db_path):
            with open(db_path, "r", encoding="utf-8") as f:
                db = json.load(f)
            modified = False
            for p in test_phones:
                if p in db:
                    del db[p]
                    modified = True
            if modified:
                with open(db_path, "w", encoding="utf-8") as f:
                    json.dump(db, f, indent=2)
        banned_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "banned_phones.json")
        if os.path.exists(banned_path):
            with open(banned_path, "r", encoding="utf-8") as f:
                banned = json.load(f)
            banned = [p for p in banned if p not in test_phones]
            with open(banned_path, "w", encoding="utf-8") as f:
                json.dump(banned, f, indent=2)
    except Exception:
        pass

    tests = [
        # 1. Routing
        ("TC-01", "Page Routing", "GET / (Root Quiz Funnel)", test_get_root),
        ("TC-02", "Page Routing", "GET /quiz", test_get_quiz),
        ("TC-03", "Page Routing", "GET /card", test_get_card),
        ("TC-04", "Page Routing", "GET /admin", test_get_admin),
        ("TC-05", "Page Routing", "GET /classic", test_get_classic),
        ("TC-06", "Page Routing", "HEAD requests on all page routes", test_head_routes),

        # 2. Offers Config API
        ("TC-07", "Offers API", "GET /api/offers", test_get_offers),
        ("TC-08", "Offers API", "GET /api/admin/offers", test_get_admin_offers),
        ("TC-09", "Offers API", "POST /api/admin/offers (Update standard offers)", test_post_admin_offers_update),
        ("TC-10", "Offers API", "POST /api/admin/offers (Add 6th offer slot)", test_post_admin_offers_add_slot),
        ("TC-11", "Offers API", "POST /api/admin/offers (Delete slots down to 3)", test_post_admin_offers_delete_slot),
        ("TC-12", "Offers API", "POST /api/admin/offers (Reject empty offers)", test_post_admin_offers_empty),
        ("TC-13", "Offers API", "POST /api/admin/offers (Reject non-list offers)", test_post_admin_offers_invalid_type),
        ("TC-14", "Offers API", "POST /api/admin/offers (Preserves existing cards in DB)", test_post_admin_offers_preserves_existing_cards),

        # 3. Lead Registration & Phone Validation
        ("TC-15", "Lead Registration", "Valid Vodafone 010 (11 digits)", test_submit_valid_vodafone),
        ("TC-16", "Lead Registration", "Valid Orange 012 (11 digits)", test_submit_valid_orange),
        ("TC-17", "Lead Registration", "Valid Etisalat 011 (11 digits)", test_submit_valid_etisalat),
        ("TC-18", "Lead Registration", "Valid WE 015 (11 digits)", test_submit_valid_we),
        ("TC-19", "Lead Registration", "Normalize +20 international format", test_submit_international_plus20),
        ("TC-20", "Lead Registration", "Normalize 0020 international format", test_submit_international_0020),
        ("TC-21", "Lead Registration", "Normalize 10-digit number without leading 0", test_submit_10digits_missing_leading_zero),
        ("TC-22", "Lead Registration", "Card dynamic stamp milestone initialization", test_submit_dynamic_stamps_milestones),
        ("TC-22B", "Lead Registration", "First deal in card features quiz matched drink", test_submit_first_deal_matches_quiz_drink),
        ("TC-23", "Lead Registration", "Invalid length: 10 digits", test_submit_invalid_length_10_digits),
        ("TC-24", "Lead Registration", "Invalid length: 12 digits", test_submit_invalid_length_12_digits),
        ("TC-25", "Lead Registration", "Invalid network prefix: 013", test_submit_invalid_prefix_013),
        ("TC-26", "Lead Registration", "Invalid network prefix: 014", test_submit_invalid_prefix_014),
        ("TC-27", "Lead Registration", "Invalid network prefix: 016", test_submit_invalid_prefix_016),
        ("TC-28", "Lead Registration", "Invalid characters (letters)", test_submit_invalid_chars),
        ("TC-29", "Anti-Fraud Phone", "Block repeated zeros: 01000000000", test_submit_fake_repetitive_zeros),
        ("TC-30", "Anti-Fraud Phone", "Block repeated ones: 01111111111", test_submit_fake_repetitive_ones),
        ("TC-31", "Anti-Fraud Phone", "Block sequential ascending: 01012345678", test_submit_fake_sequential_ascending_1),
        ("TC-32", "Anti-Fraud Phone", "Block sequential ascending: 01123456789", test_submit_fake_sequential_ascending_2),
        ("TC-33", "Anti-Fraud Phone", "Block sequential ascending: 01234567890", test_submit_fake_sequential_ascending_3),
        ("TC-34", "Anti-Fraud Phone", "Block sequential descending: 01087654321", test_submit_fake_sequential_descending),
        ("TC-35", "Anti-Fraud Phone", "Block repetitive pattern: 01012121212", test_submit_fake_repetitive_chunks),
        ("TC-36", "Anti-Fraud Phone", "Block low entropy: 01012122112", test_submit_fake_low_entropy),
        ("TC-37", "Anti-Fraud Phone", "Block blacklisted test number: 01512345678", test_submit_fake_blacklisted_number),
        ("TC-38", "Lead Registration", "Reject short name (<2 chars)", test_submit_short_name),
        ("TC-39", "Lead Registration", "Duplicate registration: HTTP 409 & redirect payload", test_submit_duplicate_registration_status),

        # 4. Card Pass Operations
        ("TC-40", "Card Operations", "GET /api/card?phone=<valid>", test_card_get_valid),
        ("TC-41", "Card Operations", "GET /api/card?phone=<international raw>", test_card_get_normalized_plus20),
        ("TC-42", "Card Operations", "GET /api/card?phone=<nonexistent>", test_card_get_nonexistent),
        ("TC-43", "Card Operations", "GET /api/card (missing phone)", test_card_get_missing_phone),
        ("TC-44", "Card Operations", "POST /api/card/activate (valid)", test_card_activate_valid),
        ("TC-45", "Card Operations", "POST /api/card/activate (nonexistent phone)", test_card_activate_nonexistent),

        # 5. POS Admin Operations
        ("TC-46", "Admin Operations", "GET /api/admin/cards (List members)", test_admin_cards_list),
        ("TC-47", "Admin Operations", "GET /api/admin/cards?q=<phone> (Search phone)", test_admin_cards_search_by_phone),
        ("TC-48", "Admin Operations", "GET /api/admin/cards?q=<name> (Search name)", test_admin_cards_search_by_name),
        ("TC-49", "Admin Operations", "GET /api/admin/search?phone=... (Direct POS Search)", test_admin_search_endpoint),
        ("TC-50", "Admin Operations", "POST /api/admin/stamp (action: redeem)", test_admin_stamp_redeem),
        ("TC-51", "Admin Operations", "POST /api/admin/stamp (action: unlock)", test_admin_stamp_unlock),
        ("TC-52", "Admin Operations", "POST /api/admin/stamp (action: reset)", test_admin_stamp_reset),
        ("TC-53", "Admin Operations", "POST /api/admin/stamp (out-of-range stamp index)", test_admin_stamp_out_of_range),
        ("TC-54", "Admin Operations", "POST /api/admin/stamp (invalid action validation)", test_admin_stamp_invalid_action),
        ("TC-55", "Admin Operations", "POST /api/admin/stamp (nonexistent phone)", test_admin_stamp_nonexistent_phone),

        # 5B. Customer Lifecycle: Ban, Unban, Delete & Date Filters
        ("TC-56", "Customer Lifecycle", "POST /api/admin/customer/ban (Ban customer)", test_admin_ban_customer),
        ("TC-57", "Customer Lifecycle", "POST /api/submit rejected for banned customer (HTTP 403)", test_banned_customer_blocked_on_submit),
        ("TC-58", "Customer Lifecycle", "GET /api/card rejected for banned customer (HTTP 403)", test_banned_customer_blocked_on_card),
        ("TC-59", "Customer Lifecycle", "POST /api/admin/customer/ban (Unban customer)", test_admin_unban_customer),
        ("TC-60", "Customer Lifecycle", "POST /api/admin/customer/delete (Delete customer)", test_admin_delete_customer),
        ("TC-61", "Customer Lifecycle", "Deleted customer can re-register via /api/submit", test_deleted_customer_can_re_register),
        ("TC-61B", "Customer Lifecycle", "Returning deleted customer restores previous stamps & pass ID", test_deleted_customer_restores_old_data),
        ("TC-62", "Customer Lifecycle", "GET /api/admin/cards date range filtering", test_admin_cards_date_filtering),

        # 5C. Customer Offers Upgrades & History Audit Trail
        ("TC-63", "Customer Offers & History", "POST /api/admin/customer/update-offers (Single customer)", test_admin_update_customer_offers_single),
        ("TC-64", "Customer Offers & History", "POST /api/admin/customer/update-offers (Batch customers)", test_admin_update_customer_offers_batch),
        ("TC-65", "Customer Offers & History", "GET /api/admin/customer/history (History audit endpoint)", test_admin_customer_history_endpoint),
        ("TC-66", "Customer Offers & History", "Multiple upgrades accumulate sequential history versions", test_admin_customer_multiple_upgrades_accumulate_history),

        # 6. Malformed & Edge Cases
        ("TC-67", "Robustness", "Malformed JSON on POST /api/submit", test_malformed_json_submit),
        ("TC-68", "Robustness", "JSON array payload on POST /api/submit", test_json_array_payload_submit),
        ("TC-69", "Robustness", "GET unknown API endpoint", test_unknown_endpoint_get),
        ("TC-70", "Robustness", "POST unknown API endpoint", test_unknown_endpoint_post),

        # 7. Customer Timestamps & Audit Trail
        ("TC-71", "Timestamps & Audit", "POST /api/card/activate records activatedAt ISO timestamp", test_card_activation_records_activated_at),
        ("TC-72", "Timestamps & Audit", "POST /api/submit records quizFinishedAt ISO timestamp", test_quiz_finished_at_timestamp),
        ("TC-73", "Timestamps & Audit", "POST /api/admin/stamp records unlockedAt & redeemedAt timestamps", test_stamp_timestamps_persisted),
        ("TC-74", "Timestamps & Audit", "GET /api/admin/cards returns timestamps and filters by date range", test_admin_cards_timestamps_and_date_filtering),
    ]

    for tid, cat, name, fn in tests:
        run_test(tid, cat, name, fn)

    passed = [t for t in test_results if t["status"] == "PASS"]
    failed = [t for t in test_results if t["status"] == "FAIL"]
    errors = [t for t in test_results if t["status"] == "ERROR"]

    print("=" * 70)
    print(f" TOTAL TESTS: {len(test_results)} | PASSED: {len(passed)} | FAILED: {len(failed)} | ERRORS: {len(errors)}")
    print("=" * 70)

    # Save results as JSON
    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump(test_results, f, indent=2)

    # Teardown: Restore clean production base offers so test mocks never pollute live database
    clean_offers = [
        {"index": 1, "title": "Free 1st Coffee", "desc": "Signature drink free", "icon": "☕"},
        {"index": 2, "title": "20% Off Pastry", "desc": "Fresh Bakery Item", "icon": "🥐"},
        {"index": 3, "title": "Free Size Upgrade", "desc": "Coffee or Specialty Drink", "icon": "🥛"},
        {"index": 4, "title": "Buy 1 Get 1 Free", "desc": "Signature Drinks", "icon": "🎁"},
        {"index": 5, "title": "Free Drink + VIP Status", "desc": "Grand Loyalty Reward", "icon": "🌟"}
    ]
    make_request("/api/admin/offers", method="POST", data={"offers": clean_offers})

if __name__ == "__main__":
    main()
