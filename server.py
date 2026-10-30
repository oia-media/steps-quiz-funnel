#!/usr/bin/env python3
"""
STEPS Specialty Coffee Bar - Full Sales Funnel & Loyalty Card Server
Features:
- / -> Sales Funnel Quiz (index.html)
- /card -> Dedicated Customer Digital Loyalty Pass (card.html)
- /admin -> Barista & Store Manager Admin Portal (admin.html)
- /api/submit -> Register Quiz Lead (1 Card per Phone Number)
- /api/card -> Real-time Card Lookup by Phone
- /api/card/activate -> Customer Card Activation
- /api/admin/cards -> List all members for store staff
- /api/admin/stamp -> Barista Action: Unlock or Redeem Stamps 1-5
"""

import os
import sys
import json
import csv
import re
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, HTTPServer
import urllib.parse
import copy

PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(DIRECTORY, 'cards_db.json')
CSV_FILE = os.path.join(DIRECTORY, 'leads.csv')
BANNED_FILE = os.path.join(DIRECTORY, 'banned_phones.json')

def load_banned_phones():
    if os.path.exists(BANNED_FILE):
        try:
            with open(BANNED_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception as e:
            print(f"[BANNED LOAD ERROR] {e}")
    return {}

def save_banned_phones(data):
    with open(BANNED_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

ARCHIVED_DB_FILE = os.path.join(DIRECTORY, 'archived_cards_db.json')

def load_archived_db():
    if os.path.exists(ARCHIVED_DB_FILE):
        try:
            with open(ARCHIVED_DB_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception as e:
            print(f"[ARCHIVED DB LOAD ERROR] {e}")
    return {}

def save_archived_db(data):
    with open(ARCHIVED_DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Drink Profiles
DRINK_PROFILES = {
    'iced_spanish_latte': {
        'name': 'Iced Spanish Latte',
        'desc': 'Silky espresso combined with sweet condensed milk, served over chilled ice.',
        'base': 'Iced Espresso Coffee'
    },
    'strawberry_matcha': {
        'name': 'Strawberry Matcha',
        'desc': 'Ceremonial Japanese green tea layered over sweet handcrafted strawberry puree.',
        'base': 'Japanese Green Tea'
    },
    'passionfruit_mojito': {
        'name': 'Passionfruit Mojito',
        'desc': 'Zesty passionfruit, crushed mint and sparkling fruit soda with crisp citrus notes.',
        'base': 'Fizzy Fruit Soda'
    },
    'mocha_frappe': {
        'name': 'Mocha Frappe',
        'desc': 'Blended ice, rich espresso, and decadent dark chocolate topped with cold velvet cream.',
        'base': 'Blended Ice & Coffee'
    }
}

OFFERS_FILE = os.path.join(DIRECTORY, 'offers_config.json')

DEFAULT_OFFERS = [
    {"index": 1, "title": "Free 1st Coffee", "desc": "Signature drink free", "icon": "☕"},
    {"index": 2, "title": "20% Off Pastry", "desc": "Fresh Bakery Item", "icon": "🥐"},
    {"index": 3, "title": "Free Size Upgrade", "desc": "Coffee or Specialty Drink", "icon": "🥛"},
    {"index": 4, "title": "Buy 1 Get 1 Free", "desc": "Signature Drinks", "icon": "🎁"},
    {"index": 5, "title": "Free Drink + VIP Status", "desc": "Grand Loyalty Reward", "icon": "🌟"}
]

def load_offers():
    if os.path.exists(OFFERS_FILE):
        try:
            with open(OFFERS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    return data
        except Exception as e:
            print(f"[OFFERS LOAD ERROR] {e}")
    return DEFAULT_OFFERS

def save_offers(offers):
    with open(OFFERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(offers, f, indent=2, ensure_ascii=False)

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def update_card_offers_with_history(card, new_offers, reason="Admin manual upgrade to active campaign"):
    """
    Archives current card stamps into offersHistory and updates stamps to match new_offers.
    Preserves customer's quiz signature drink match for Stamp 1.
    Preserves existing redeemed status if stamp was redeemed.
    """
    now_iso = datetime.now().isoformat()
    current_stamps = card.get('stamps', {})

    history_entry = {
        'historyId': f"hist_{int(datetime.now().timestamp() * 1000)}",
        'archivedAt': now_iso,
        'reason': reason,
        'offersCount': len(current_stamps),
        'stamps': copy.deepcopy(current_stamps),
        'summary': [f"#{k}: {v.get('title', '')} [{v.get('status', '')}]" for k, v in sorted(current_stamps.items(), key=lambda x: int(x[0])) if isinstance(v, dict)]
    }

    if 'offersHistory' not in card or not isinstance(card['offersHistory'], list):
        card['offersHistory'] = []
    card['offersHistory'].append(history_entry)

    drink_icons = {
        'iced_spanish_latte': '☕',
        'strawberry_matcha': '🍵',
        'passionfruit_mojito': '🍹',
        'mocha_frappe': '🥤'
    }

    new_stamps = {}
    for off in new_offers:
        idx_str = str(off['index'])
        prev = current_stamps.get(idx_str, {})
        is_first = (off['index'] == 1)

        if is_first and card.get('matchedDrinkName'):
            drink_k = card.get('matchedDrink', '')
            drink_n = card.get('matchedDrinkName', '')
            d_icon = drink_icons.get(drink_k, off.get('icon', '☕'))
            new_stamps[idx_str] = {
                'title': f"Free {drink_n}",
                'desc': "Your Quiz Signature Match • 100% Free Drink",
                'icon': d_icon,
                'status': prev.get('status', 'available'),
                'unlockedAt': prev.get('unlockedAt', now_iso),
                'redeemedAt': prev.get('redeemedAt', None)
            }
        else:
            prev_status = prev.get('status', 'locked')
            new_stamps[idx_str] = {
                'title': off['title'],
                'desc': off['desc'],
                'icon': off['icon'],
                'status': prev_status if prev_status in ['redeemed', 'available'] else ('available' if is_first else 'locked'),
                'unlockedAt': prev.get('unlockedAt', now_iso if is_first else None),
                'redeemedAt': prev.get('redeemedAt', None)
            }

    card['stamps'] = new_stamps
    card['updatedAt'] = now_iso
    return card

def normalize_egypt_mobile(mobile_raw):
    clean = re.sub(r'[\s\-()._]', '', mobile_raw.strip())
    if clean.startswith('+20'):
        clean = '0' + clean[3:]
    elif clean.startswith('0020'):
        clean = '0' + clean[4:]
    elif clean.startswith('20') and len(clean) == 12:
        clean = '0' + clean[2:]
    elif re.match(r'^1[0125][0-9]{8}$', clean):
        clean = '0' + clean
    return clean

def is_valid_egypt_mobile(clean):
    return bool(re.match(r'^01[0125][0-9]{8}$', clean))

def check_fake_egypt_mobile(num):
    if not is_valid_egypt_mobile(num):
        return True, "Number must be exactly 11 digits starting with 010, 011, 012, or 015."

    suffix = num[3:]

    # 1. Repeated identical digits (e.g. 00000000, 11111111 or 5+ same digit)
    if re.search(r"(\d)\1{4,}", suffix):
        return True, "This number contains unrealistic repeated digits. Please enter an active Egyptian mobile."

    # 2. Sequential ascending or descending patterns (e.g. 34567890, 12345678, 87654321)
    seqs = [
        "01234567", "12345678", "23456789", "34567890", "45678901", "56789012", "67890123",
        "98765432", "87654321", "76543210", "65432109", "54321098", "43210987"
    ]
    for s in seqs:
        if s in suffix:
            return True, f"Sequential test pattern ({s}) is not permitted. Please enter a genuine mobile number."

    # 3. Arithmetic progressions (e.g. 34567890, 87654321)
    diff = int(suffix[1]) - int(suffix[0])
    if diff != 0:
        is_ap = True
        for i in range(2, len(suffix)):
            if (int(suffix[i]) - int(suffix[i-1])) != diff:
                is_ap = False
                break
        if is_ap:
            return True, "Sequential arithmetic numbers are not permitted. Please enter a genuine mobile number."

    # 4. Repeated 2-digit, 3-digit, 4-digit chunks (e.g. 12121212, 12341234)
    if re.match(r"^(\d{2})\1{3}$", suffix) or re.match(r"^(\d{4})\1$", suffix):
        return True, "Repetitive pattern numbers are not permitted."

    # 5. Low entropy: at least 4 unique digits
    if len(set(suffix)) < 4:
        return True, "Number lacks realistic digit variation. Please enter a real phone number."

    # 6. Known test dummy list
    known_fakes = {
        "01034567890", "01134567890", "01234567890", "01534567890",
        "01012345678", "01112345678", "01212345678", "01512345678"
    }
    if num in known_fakes:
        return True, "This test number is blacklisted. Please enter a real Egyptian mobile number."

    return False, "Valid"

class StepsHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_HEAD(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path in ['/quiz', '/quiz/', '/', '/index.html']:
            self.path = '/quiz.html'
        elif path in ['/card', '/card/']:
            self.path = '/card.html'
        elif path in ['/admin', '/admin/']:
            self.path = '/admin.html'
        elif path in ['/classic', '/classic/']:
            self.path = '/index.html'
        return super().do_HEAD()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # Route /quiz or /quiz/ -> quiz.html (New Luxury UI)
        if path in ['/quiz', '/quiz/']:
            self.path = '/quiz.html'
            return super().do_GET()

        # Route /card or /card/ -> card.html
        if path in ['/card', '/card/']:
            self.path = '/card.html'
            return super().do_GET()

        # Route /admin or /admin/ -> admin.html
        if path in ['/admin', '/admin/']:
            self.path = '/admin.html'
            return super().do_GET()

        # Route root / or /index.html -> default to new quiz UI quiz.html
        if path in ['/', '/index.html']:
            self.path = '/quiz.html'
            return super().do_GET()

        # Optional route /classic -> original marketscene replica index.html
        if path in ['/classic', '/classic/']:
            self.path = '/index.html'
            return super().do_GET()

        # API: Lookup Card by Phone -> GET /api/card?phone=010...
        if path == '/api/card':
            phone_raw = query.get('phone', [''])[0]
            clean_phone = normalize_egypt_mobile(phone_raw)

            db = load_db()
            if clean_phone in db:
                card = db[clean_phone]
                if card.get('isBanned'):
                    self.send_json_response(403, {
                        'success': False,
                        'isBanned': True,
                        'message': 'This loyalty pass has been suspended. Please contact store management.',
                        'card': card
                    })
                    return
                self.send_json_response(200, {
                    'success': True,
                    'card': card
                })
            else:
                self.send_json_response(404, {
                    'success': False,
                    'message': 'No loyalty card found for this mobile number.'
                })
            return

        # API: Admin List Cards -> GET /api/admin/cards?q=...&from_date=...&to_date=...&status=...
        if path == '/api/admin/cards':
            search_query = query.get('q', [''])[0].strip().lower()
            from_date = query.get('from_date', [''])[0].strip()
            to_date = query.get('to_date', [''])[0].strip()
            status_filter = query.get('status', [''])[0].strip().lower()

            db = load_db()
            cards_list = list(db.values())

            # Ensure backward compatibility for timestamps
            for c in cards_list:
                if 'quizFinishedAt' not in c:
                    c['quizFinishedAt'] = c.get('createdAt', '')
                if c.get('cardActive') and not c.get('activatedAt'):
                    c['activatedAt'] = c.get('updatedAt') or c.get('createdAt', '')

            # Sort newest first
            cards_list.sort(key=lambda c: c.get('createdAt', c.get('updatedAt', '')), reverse=True)

            filtered = []
            for c in cards_list:
                # Text Search Filter
                if search_query:
                    match_phone = search_query in c.get('phone', '').lower()
                    match_name = search_query in c.get('name', '').lower()
                    match_pass = search_query in c.get('passId', '').lower()
                    if not (match_phone or match_name or match_pass):
                        continue

                # Date Range Filter on createdAt (format: YYYY-MM-DD...)
                created_iso = c.get('createdAt', '')
                created_date = created_iso[:10] if len(created_iso) >= 10 else ''
                if from_date and created_date and created_date < from_date:
                    continue
                if to_date and created_date and created_date > to_date:
                    continue

                # Status Filter
                is_banned = bool(c.get('isBanned', False))
                is_active = bool(c.get('cardActive', False))
                s1_ready = c.get('stamps', {}).get('1', {}).get('status') == 'available'

                if status_filter == 'banned' and not is_banned:
                    continue
                elif status_filter == 'active' and (not is_active or is_banned):
                    continue
                elif status_filter == 'pending' and (is_active or is_banned):
                    continue
                elif status_filter == 'ready' and (not s1_ready or is_banned):
                    continue

                filtered.append(c)

            self.send_json_response(200, {
                'success': True,
                'count': len(filtered),
                'total': len(db),
                'cards': filtered
            })
            return

        # API: POS Admin Search -> GET /api/admin/search?phone=... or ?q=...
        if path == '/api/admin/search':
            search_param = query.get('phone', [''])[0] or query.get('q', [''])[0]
            clean_phone = normalize_egypt_mobile(search_param)
            db = load_db()
            card = None
            if clean_phone in db:
                card = db[clean_phone]
            else:
                search_lower = search_param.strip().lower()
                for c in db.values():
                    if search_lower and (c.get('passId', '').lower() == search_lower or c.get('name', '').lower() == search_lower or search_lower in c.get('phone', '')):
                        card = c
                        break

            if card:
                self.send_json_response(200, {
                    'success': True,
                    'card': card
                })
            else:
                self.send_json_response(404, {
                    'success': False,
                    'message': 'No loyalty card found for this search.'
                })
            return

        # API: Customer Offers History -> GET /api/admin/customer/history?phone=...
        if path == '/api/admin/customer/history':
            phone_param = query.get('phone', [''])[0].strip()
            if not phone_param:
                self.send_json_response(400, {'success': False, 'message': 'Phone number is required'})
                return
            clean_phone = normalize_egypt_mobile(phone_param)
            db = load_db()
            if clean_phone not in db:
                self.send_json_response(404, {'success': False, 'message': f'Customer {clean_phone} not found'})
                return
            card = db[clean_phone]
            history = card.get('offersHistory', [])
            self.send_json_response(200, {
                'success': True,
                'phone': clean_phone,
                'name': card.get('name', ''),
                'passId': card.get('passId', ''),
                'createdAt': card.get('createdAt', ''),
                'currentStamps': card.get('stamps', {}),
                'historyCount': len(history),
                'history': history
            })
            return

        # API: Get Base Offers -> GET /api/offers or /api/admin/offers
        if path in ['/api/offers', '/api/admin/offers']:
            offers = load_offers()
            self.send_json_response(200, {
                'success': True,
                'count': len(offers),
                'offers': offers
            })
            return

        # Serve static files as standard
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)

        try:
            payload = json.loads(post_data.decode('utf-8')) if post_data else {}
        except Exception:
            self.send_json_response(400, {'success': False, 'message': 'Invalid JSON payload'})
            return

        if not isinstance(payload, dict):
            self.send_json_response(400, {'success': False, 'message': 'Payload must be a JSON object'})
            return

        # ------------------------------------------------------------------
        # 1. API: Submit Quiz Lead / Create or Update Card (1 per Phone)
        # ------------------------------------------------------------------
        if path in ['/api/submit', '/api/submit.php']:
            name = payload.get('name', '').strip()
            mobile_raw = payload.get('mobile', '').strip()
            matched_drink = payload.get('matchedDrink', 'iced_spanish_latte')
            answers = payload.get('answers', {})

            if len(name) < 2:
                self.send_json_response(422, {'success': False, 'message': 'Please provide a valid full name.'})
                return

            clean_phone = normalize_egypt_mobile(mobile_raw)
            is_fake, fake_reason = check_fake_egypt_mobile(clean_phone)
            if is_fake:
                self.send_json_response(422, {
                    'success': False,
                    'message': fake_reason
                })
                return

            db = load_db()
            now_iso = datetime.now().isoformat()
            drink_info = DRINK_PROFILES.get(matched_drink, DRINK_PROFILES['iced_spanish_latte'])

            # Check if mobile number is banned / suspended
            banned_phones = load_banned_phones()
            if clean_phone in banned_phones or (clean_phone in db and db[clean_phone].get('isBanned')):
                print(f"[BANNED ATTEMPT] ⛔ Suspended phone {clean_phone} attempted registration.")
                self.send_json_response(403, {
                    'success': False,
                    'isBanned': True,
                    'message': 'This mobile number has been suspended from the STEPS Loyalty Program. Please speak with store management.'
                })
                return

            if clean_phone in db:
                # Phone already did the quiz -> Cant do it again! Direct to card page.
                card = db[clean_phone]
                print(f"[ALREADY REGISTERED] 🚫 {card['name']} ({clean_phone}) attempted quiz again -> Directing to /card")
                self.send_json_response(409, {
                    'success': True,
                    'alreadyRegistered': True,
                    'message': 'You have already completed the quiz! Directing you to your loyalty card...',
                    'card': card
                })
                return

            # Check if this customer was previously deleted and is returning
            # "if i deleted a customer and he come back agian, he must come back with the old data he had not a new one"
            archived_db = load_archived_db()
            if clean_phone in archived_db:
                old_card = archived_db[clean_phone]
                del archived_db[clean_phone]
                save_archived_db(archived_db)

                # Keep previous passId, stamps, activation status, timestamps, and history
                if name:
                    old_card['name'] = name
                old_card['isBanned'] = False
                old_card['bannedAt'] = None
                old_card['updatedAt'] = now_iso
                old_card['restoredAt'] = now_iso
                db[clean_phone] = old_card
                save_db(db)

                print(f"[RETURNING DELETED CUSTOMER RESTORED] ♻️ {old_card.get('name')} ({clean_phone}) restored with previous loyalty card data!")
                self.send_json_response(200, {
                    'success': True,
                    'restored': True,
                    'message': f"Welcome back, {old_card.get('name')}! Your loyalty card and previous stamps have been restored.",
                    'card': old_card
                })
                return

            # Brand new member registration
            pass_id = f"STP-{os.urandom(2).hex().upper()}-26"
            configured_offers = load_offers()
            drink_icons = {
                'iced_spanish_latte': '☕',
                'strawberry_matcha': '🍵',
                'passionfruit_mojito': '🍹',
                'mocha_frappe': '🥤'
            }
            matched_icon = drink_icons.get(matched_drink, '☕')

            card_stamps = {}
            for off in configured_offers:
                idx_str = str(off.get('index', 1))
                is_first = (off.get('index', 1) == 1)
                if is_first:
                    card_stamps[idx_str] = {
                        'title': f"Free {drink_info['name']}",
                        'desc': "Your Quiz Signature Match • 100% Free Drink",
                        'icon': matched_icon,
                        'status': 'available',
                        'unlockedAt': now_iso,
                        'redeemedAt': None
                    }
                else:
                    card_stamps[idx_str] = {
                        'title': off.get('title', f"Reward #{idx_str}"),
                        'desc': off.get('desc', ''),
                        'icon': off.get('icon', '☕'),
                        'status': 'locked',
                        'unlockedAt': None,
                        'redeemedAt': None
                    }

            card = {
                'phone': clean_phone,
                'name': name,
                'passId': pass_id,
                'matchedDrink': matched_drink,
                'matchedDrinkName': drink_info['name'],
                'matchedDrinkDesc': drink_info['desc'],
                'cardActive': False, # Must press Activate Card button on pass page
                'isBanned': False,
                'bannedAt': None,
                'stamps': card_stamps,
                'createdAt': now_iso,
                'quizFinishedAt': now_iso,
                'activatedAt': None,
                'updatedAt': now_iso,
                'ip': self.client_address[0]
            }
            db[clean_phone] = card
            print(f"[NEW CARD ISSUED] 🎉 {name} ({clean_phone}) | Pass: {pass_id} | Drink: {drink_info['name']}")

            save_db(db)

            # Append to leads.csv for marketing
            csv_exists = os.path.exists(CSV_FILE)
            with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if not csv_exists:
                    writer.writerow(['Timestamp', 'Name', 'Phone', 'Pass ID', 'Matched Drink', 'IP'])
                writer.writerow([now_iso, card['name'], card['phone'], card['passId'], card['matchedDrinkName'], self.client_address[0]])

            self.send_json_response(200, {
                'success': True,
                'message': 'Digital loyalty card ready',
                'card': card
            })
            return

        # ------------------------------------------------------------------
        # 2. API: Activate Digital Card
        # ------------------------------------------------------------------
        if path == '/api/card/activate':
            phone_raw = payload.get('phone', '').strip()
            clean_phone = normalize_egypt_mobile(phone_raw)

            db = load_db()
            if clean_phone not in db:
                self.send_json_response(404, {'success': False, 'message': 'Card not found'})
                return

            card = db[clean_phone]
            card['cardActive'] = True
            now_iso = datetime.now().isoformat()
            if not card.get('activatedAt'):
                card['activatedAt'] = now_iso
            card['updatedAt'] = now_iso
            save_db(db)

            print(f"[CARD ACTIVATED] ⚡ {card['name']} ({clean_phone}) at {card['activatedAt']}")
            self.send_json_response(200, {'success': True, 'card': card})
            return

        # ------------------------------------------------------------------
        # 3. API: Admin Barista Stamp Actions
        # ------------------------------------------------------------------
        if path == '/api/admin/stamp':
            phone_raw = payload.get('phone', '').strip()
            stamp_index = str(payload.get('stampIndex', '1'))
            action = payload.get('action', 'redeem') # 'redeem', 'unlock', 'reset'

            if action not in ['redeem', 'unlock', 'reset']:
                self.send_json_response(422, {
                    'success': False,
                    'message': f"Invalid action: '{action}'"
                })
                return

            clean_phone = normalize_egypt_mobile(phone_raw)
            db = load_db()

            if clean_phone not in db:
                self.send_json_response(404, {'success': False, 'message': 'Member card not found'})
                return

            card = db[clean_phone]
            if stamp_index not in card.get('stamps', {}):
                self.send_json_response(400, {'success': False, 'message': 'Invalid stamp index'})
                return

            now_iso = datetime.now().isoformat()
            stamp = card['stamps'][stamp_index]

            if action == 'redeem':
                stamp['status'] = 'redeemed'
                stamp['redeemedAt'] = now_iso
                if not stamp.get('unlockedAt'):
                    stamp['unlockedAt'] = card.get('quizFinishedAt') or card.get('createdAt') or now_iso
            elif action == 'unlock':
                stamp['status'] = 'available'
                stamp['unlockedAt'] = now_iso
                stamp['redeemedAt'] = None
            elif action == 'reset':
                stamp['status'] = 'locked'
                stamp['unlockedAt'] = None
                stamp['redeemedAt'] = None

            card['updatedAt'] = now_iso
            save_db(db)

            print(f"[ADMIN STAMP UPDATED] ☕ Member: {card['name']} | Stamp #{stamp_index} -> {action.upper()} ({stamp['status']})")
            self.send_json_response(200, {
                'success': True,
                'message': f"Stamp {stamp_index} updated to {stamp['status']}",
                'card': card
            })
            return

        # ------------------------------------------------------------------
        # 4. API: Update Base Offers (Number of offers, titles, icons)
        # ------------------------------------------------------------------
        if path == '/api/admin/offers':
            raw_offers = payload.get('offers', [])

            if not isinstance(raw_offers, list) or len(raw_offers) == 0:
                self.send_json_response(422, {'success': False, 'message': 'At least one offer is required.'})
                return

            sanitized_offers = []
            for i, off in enumerate(raw_offers, start=1):
                title = str(off.get('title', '')).strip()
                desc = str(off.get('desc', '')).strip()
                icon = str(off.get('icon', '☕')).strip() or '☕'

                if not title:
                    title = f"Reward #{i}"

                sanitized_offers.append({
                    'index': i,
                    'title': title,
                    'desc': desc,
                    'icon': icon
                })

            save_offers(sanitized_offers)
            print(f"[BASE OFFERS UPDATED] ⚙️ {len(sanitized_offers)} offers configured for new customers: {[o['title'] for o in sanitized_offers]}")

            self.send_json_response(200, {
                'success': True,
                'message': f'Base offers updated successfully for new customers ({len(sanitized_offers)} offers)',
                'count': len(sanitized_offers),
                'offers': sanitized_offers
            })
            return

        # ------------------------------------------------------------------
        # 5. API: Admin Ban / Unban Customer
        # ------------------------------------------------------------------
        if path == '/api/admin/customer/ban':
            phone_raw = payload.get('phone', '').strip()
            action = str(payload.get('action', 'ban')).lower().strip() # 'ban' or 'unban'
            reason = str(payload.get('reason', 'Administrative decision')).strip()

            if action not in ['ban', 'unban']:
                self.send_json_response(422, {'success': False, 'message': "Action must be 'ban' or 'unban'"})
                return

            clean_phone = normalize_egypt_mobile(phone_raw)
            if not is_valid_egypt_mobile(clean_phone):
                self.send_json_response(422, {'success': False, 'message': 'Invalid Egyptian mobile number'})
                return

            banned_phones = load_banned_phones()
            db = load_db()
            now_iso = datetime.now().isoformat()

            if action == 'ban':
                banned_phones[clean_phone] = {
                    'bannedAt': now_iso,
                    'reason': reason,
                    'name': db.get(clean_phone, {}).get('name', '')
                }
                save_banned_phones(banned_phones)
                if clean_phone in db:
                    db[clean_phone]['isBanned'] = True
                    db[clean_phone]['bannedAt'] = now_iso
                    db[clean_phone]['updatedAt'] = now_iso
                    save_db(db)
                print(f"[CUSTOMER BANNED] ⛔ {clean_phone} has been suspended from the program.")
                self.send_json_response(200, {
                    'success': True,
                    'message': f"Customer {clean_phone} has been banned.",
                    'isBanned': True,
                    'card': db.get(clean_phone)
                })
                return
            else: # unban
                if clean_phone in banned_phones:
                    del banned_phones[clean_phone]
                    save_banned_phones(banned_phones)
                if clean_phone in db:
                    db[clean_phone]['isBanned'] = False
                    db[clean_phone]['bannedAt'] = None
                    db[clean_phone]['updatedAt'] = now_iso
                    save_db(db)
                print(f"[CUSTOMER UNBANNED] ✅ {clean_phone} has been reinstated.")
                self.send_json_response(200, {
                    'success': True,
                    'message': f"Customer {clean_phone} has been unbanned.",
                    'isBanned': False,
                    'card': db.get(clean_phone)
                })
                return

        # ------------------------------------------------------------------
        # 6. API: Admin Delete Customer (Archives card so if they return, old data is restored)
        # ------------------------------------------------------------------
        if path == '/api/admin/customer/delete':
            phone_raw = payload.get('phone', '').strip()
            clean_phone = normalize_egypt_mobile(phone_raw)

            db = load_db()
            banned_phones = load_banned_phones()
            archived_db = load_archived_db()

            deleted = False
            if clean_phone in db:
                card = db[clean_phone]
                card['deletedAt'] = datetime.now().isoformat()
                archived_db[clean_phone] = copy.deepcopy(card)
                save_archived_db(archived_db)

                del db[clean_phone]
                save_db(db)
                deleted = True

            # Also lift ban if deleted so they can return
            if clean_phone in banned_phones:
                del banned_phones[clean_phone]
                save_banned_phones(banned_phones)

            if deleted:
                print(f"[CUSTOMER DELETED & ARCHIVED] 🗑️ {clean_phone} archived from active database.")
                self.send_json_response(200, {
                    'success': True,
                    'message': f"Customer {clean_phone} deleted successfully. If they return, their previous card data will be restored."
                })
            else:
                self.send_json_response(404, {
                    'success': False,
                    'message': f"Customer {clean_phone} not found in database."
                })
            return

        # ------------------------------------------------------------------
        # 7. API: Admin Update Customer Offers & Archive History
        # ------------------------------------------------------------------
        if path == '/api/admin/customer/update-offers':
            phones_input = payload.get('phones')
            if phones_input is None:
                single_phone = payload.get('phone', '').strip()
                phones = [single_phone] if single_phone else []
            elif isinstance(phones_input, list):
                phones = [str(p).strip() for p in phones_input if str(p).strip()]
            else:
                phones = []

            if not phones:
                self.send_json_response(422, {'success': False, 'message': 'No customer phone provided'})
                return

            db = load_db()
            active_offers = load_offers()
            updated_cards = []
            not_found = []
            reason = payload.get('reason', 'Admin manual upgrade to active campaign')

            for p_raw in phones:
                clean_phone = normalize_egypt_mobile(p_raw)
                if clean_phone not in db:
                    not_found.append(p_raw)
                    continue
                card = db[clean_phone]
                update_card_offers_with_history(card, active_offers, reason=reason)
                updated_cards.append(card)

            if updated_cards:
                save_db(db)

            print(f"[CUSTOMER OFFERS UPDATED] 🔄 {len(updated_cards)} customer(s) upgraded to current campaign.")
            self.send_json_response(200, {
                'success': True,
                'message': f"Successfully updated {len(updated_cards)} customer(s) to current campaign offers.",
                'updatedCount': len(updated_cards),
                'notFound': not_found,
                'cards': updated_cards
            })
            return

        self.send_json_response(404, {'success': False, 'message': 'Endpoint not found'})

    def do_DELETE(self):
        # Support HTTP DELETE requests delegating to do_POST routing
        return self.do_POST()

    def send_json_response(self, code, data):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

def run_server():
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, StepsHandler)
    print("=" * 64)
    print(" ☕ STEPS Specialty Coffee Bar - Digital Loyalty Ecosystem")
    print(f" 🎯 Quiz Funnel:      http://localhost:{PORT}/quiz")
    print(f" 🌐 Landing / Home:   http://localhost:{PORT}/")
    print(f" 💳 Digital Card:     http://localhost:{PORT}/card")
    print(f" 👨‍🍳 Barista Admin:    http://localhost:{PORT}/admin")
    print(f" 📂 Data Store:       cards_db.json & leads.csv")
    print("=" * 64)
    print(" Running... Press Ctrl+C to stop.\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        sys.exit(0)

if __name__ == '__main__':
    run_server()
