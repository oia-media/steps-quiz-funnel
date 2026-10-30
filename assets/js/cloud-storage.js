/**
 * STEPS Specialty Coffee Bar — Cloud Standalone Storage Adapter
 * Enables 100% full-stack functionality on static hosts (GitHub Pages)
 * using high-fidelity in-browser localStorage database with cross-tab live synchronization.
 */
(function() {
    'use strict';

    const isCloudDemo = window.location.hostname.includes('github.io') || 
                        window.location.protocol === 'file:' || 
                        window.location.port === '' ||
                        window.location.hostname.endsWith('.pages.dev');

    // Auto-rewrite absolute root links for GitHub Pages subdirectory paths
    document.addEventListener('DOMContentLoaded', () => {
        if (isCloudDemo) {
            document.querySelectorAll('a[href="/card"], a[href="/card/"]').forEach(a => a.setAttribute('href', 'card.html'));
            document.querySelectorAll('a[href="/quiz"], a[href="/quiz/"]').forEach(a => a.setAttribute('href', 'index.html'));
            document.querySelectorAll('a[href="/admin"], a[href="/admin/"]').forEach(a => a.setAttribute('href', 'admin.html'));
            document.querySelectorAll('a[href="/classic"], a[href="/classic/"]').forEach(a => a.setAttribute('href', 'classic.html'));
        }
    });

    const DEFAULT_BASE_OFFERS = [
        { index: 1, title: 'Free 1st Coffee', desc: 'Signature drink free', icon: '☕' },
        { index: 2, title: '20% Off Pastry', desc: 'Fresh Bakery Item', icon: '🥐' },
        { index: 3, title: 'Free Size Upgrade', desc: 'Coffee or Specialty Drink', icon: '🥛' },
        { index: 4, title: 'Buy 1 Get 1 Free', desc: 'Signature Drinks', icon: '🎁' },
        { index: 5, title: 'Free Drink + VIP Status', desc: 'Grand Loyalty Reward', icon: '🌟' }
    ];

    const INITIAL_DEMO_CARDS = {
        "01015484767": {
            "phone": "01015484767",
            "name": "Omar",
            "passId": "STP-5FAB-26",
            "matchedDrink": "strawberry_matcha",
            "matchedDrinkName": "Strawberry Matcha",
            "matchedDrinkDesc": "Ceremonial Japanese green tea layered over sweet handcrafted strawberry puree.",
            "cardActive": true,
            "stamps": {
                "1": { "title": "Free Strawberry Matcha", "desc": "Your Quiz Signature Match • 100% Free Drink", "icon": "🍵", "status": "redeemed", "unlockedAt": "2026-10-30T03:00:57.617230", "redeemedAt": "2026-10-30T05:29:12.049334" },
                "2": { "title": "20% Off Pastry", "desc": "Fresh Bakery Item", "icon": "🥐", "status": "locked", "unlockedAt": null, "redeemedAt": null },
                "3": { "title": "Free Size Upgrade", "desc": "Coffee or Specialty Drink", "icon": "🥛", "status": "locked", "unlockedAt": null, "redeemedAt": null },
                "4": { "title": "Buy 1 Get 1 Free", "desc": "Signature Drinks", "icon": "🎁", "status": "locked", "unlockedAt": null, "redeemedAt": null },
                "5": { "title": "Free Drink + VIP Status", "desc": "Grand Loyalty Reward", "icon": "🌟", "status": "locked", "unlockedAt": null, "redeemedAt": null }
            },
            "createdAt": "2026-10-30T03:00:57.617230",
            "quizFinishedAt": "2026-10-30T03:00:57.617230",
            "activatedAt": "2026-10-30T05:29:12.047847"
        },
        "01043142342": {
            "phone": "01043142342",
            "name": "omar",
            "passId": "STP-9549-26",
            "matchedDrink": "iced_spanish_latte",
            "matchedDrinkName": "Iced Spanish Latte",
            "matchedDrinkDesc": "Silky espresso combined with sweet condensed milk, served over chilled ice.",
            "cardActive": true,
            "stamps": {
                "1": { "title": "Free Iced Spanish Latte", "desc": "Your Quiz Signature Match • 100% Free Drink", "icon": "☕", "status": "available", "unlockedAt": "2026-10-30T03:07:12.287312", "redeemedAt": null },
                "2": { "title": "20% Off Pastry", "desc": "Fresh Bakery Item", "icon": "🥐", "status": "locked", "unlockedAt": null, "redeemedAt": null },
                "3": { "title": "Free Size Upgrade", "desc": "Coffee or Specialty Drink", "icon": "🥛", "status": "locked", "unlockedAt": null, "redeemedAt": null },
                "4": { "title": "Buy 1 Get 1 Free", "desc": "Signature Drinks", "icon": "🎁", "status": "available", "unlockedAt": "2026-10-30T05:32:00.000000", "redeemedAt": null },
                "5": { "title": "Free Drink + VIP Status", "desc": "Grand Loyalty Reward", "icon": "🌟", "status": "locked", "unlockedAt": null, "redeemedAt": null }
            },
            "createdAt": "2026-10-30T03:07:12.287312",
            "quizFinishedAt": "2026-10-30T03:07:12.287312",
            "activatedAt": "2026-10-30T05:30:15.112340"
        },
        "01098712349": {
            "phone": "01098712349",
            "name": "Youssef",
            "passId": "STP-3B7D-26",
            "matchedDrink": "mocha_frappe",
            "matchedDrinkName": "Mocha Frappe",
            "matchedDrinkDesc": "Rich chocolate blended with double espresso and crushed ice, topped with velvet froth.",
            "cardActive": false,
            "stamps": {
                "1": { "title": "Free Mocha Frappe", "desc": "Your Quiz Signature Match • 100% Free Drink", "icon": "🥤", "status": "available", "unlockedAt": "2026-10-30T04:00:19.883484", "redeemedAt": null },
                "2": { "title": "20% Off Pastry", "desc": "Fresh Bakery Item", "icon": "🥐", "status": "locked", "unlockedAt": null, "redeemedAt": null },
                "3": { "title": "Free Size Upgrade", "desc": "Coffee or Specialty Drink", "icon": "🥛", "status": "locked", "unlockedAt": null, "redeemedAt": null },
                "4": { "title": "Buy 1 Get 1 Free", "desc": "Signature Drinks", "icon": "🎁", "status": "locked", "unlockedAt": null, "redeemedAt": null },
                "5": { "title": "Free Drink + VIP Status", "desc": "Grand Loyalty Reward", "icon": "🌟", "status": "locked", "unlockedAt": null, "redeemedAt": null }
            },
            "createdAt": "2026-10-30T04:00:19.883484",
            "quizFinishedAt": "2026-10-30T04:00:19.883484",
            "activatedAt": null
        }
    };

    const DRINK_METADATA = {
        'iced_spanish_latte': { name: 'Iced Spanish Latte', desc: 'Silky espresso combined with sweet condensed milk, served over chilled ice.', icon: '☕' },
        'strawberry_matcha': { name: 'Strawberry Matcha', desc: 'Ceremonial Japanese green tea layered over sweet handcrafted strawberry puree.', icon: '🍵' },
        'passionfruit_mojito': { name: 'Passionfruit Mojito', desc: 'Zesty passionfruit, crushed mint and sparkling fruit soda with crisp citrus notes.', icon: '🍹' },
        'mocha_frappe': { name: 'Mocha Frappe', desc: 'Rich chocolate blended with double espresso and crushed ice, topped with velvet froth.', icon: '🥤' }
    };

    const normalizePhone = (val) => {
        if (!val) return '';
        let clean = String(val).trim().replace(/[\s\-()._]/g, '');
        if (clean.startsWith('+20')) clean = '0' + clean.slice(3);
        else if (clean.startsWith('0020')) clean = '0' + clean.slice(4);
        else if (clean.startsWith('20') && clean.length === 12) clean = '0' + clean.slice(2);
        else if (/^1[0125][0-9]{8}$/.test(clean)) clean = '0' + clean;
        return clean;
    };

    const getStoredDb = () => {
        try {
            const raw = localStorage.getItem('steps_cards_db');
            if (raw) return JSON.parse(raw);
        } catch (_) {}
        localStorage.setItem('steps_cards_db', JSON.stringify(INITIAL_DEMO_CARDS));
        return { ...INITIAL_DEMO_CARDS };
    };

    const saveStoredDb = (db) => {
        try {
            localStorage.setItem('steps_cards_db', JSON.stringify(db));
            // Trigger storage event for same-window updates
            window.dispatchEvent(new Event('steps_db_updated'));
        } catch (_) {}
    };

    const getStoredOffers = () => {
        try {
            const raw = localStorage.getItem('steps_offers_config');
            if (raw) return JSON.parse(raw);
        } catch (_) {}
        localStorage.setItem('steps_offers_config', JSON.stringify(DEFAULT_BASE_OFFERS));
        return [ ...DEFAULT_BASE_OFFERS ];
    };

    const saveStoredOffers = (offers) => {
        try {
            localStorage.setItem('steps_offers_config', JSON.stringify(offers));
            window.dispatchEvent(new Event('steps_offers_updated'));
        } catch (_) {}
    };

    const getArchivedDb = () => {
        try {
            const raw = localStorage.getItem('steps_archived_cards_db');
            if (raw) return JSON.parse(raw);
        } catch (_) {}
        return {};
    };

    const saveArchivedDb = (db) => {
        try {
            localStorage.setItem('steps_archived_cards_db', JSON.stringify(db));
        } catch (_) {}
    };

    const jsonResponse = (data, status = 200) => {
        return new Response(JSON.stringify(data), {
            status,
            headers: { 'Content-Type': 'application/json' }
        });
    };

    // Client-Side Simulated Server Router
    const handleMockRequest = async (urlStr, options = {}) => {
        const u = new URL(urlStr, window.location.origin);
        const path = u.pathname;
        const method = (options.method || 'GET').toUpperCase();
        let payload = null;

        if (options.body) {
            try {
                payload = typeof options.body === 'string' ? JSON.parse(options.body) : options.body;
            } catch (_) {}
        }

        const nowIso = new Date().toISOString();

        // 1. GET /api/offers & GET /api/admin/offers
        if (path.endsWith('/api/offers') || path.endsWith('/api/admin/offers')) {
            const offers = getStoredOffers();
            return jsonResponse({ success: true, count: offers.length, offers });
        }

        // 2. POST /api/admin/offers
        if (path.endsWith('/api/admin/offers') && method === 'POST') {
            if (!payload || !Array.isArray(payload.offers)) {
                return jsonResponse({ success: false, message: 'Invalid payload' }, 400);
            }
            saveStoredOffers(payload.offers);
            return jsonResponse({ success: true, count: payload.offers.length, message: 'Base offers saved successfully!' });
        }

        // 3. POST /api/submit
        if (path.endsWith('/api/submit') && method === 'POST') {
            const mobile = normalizePhone(payload?.mobile || payload?.phone || '');
            const name = (payload?.name || '').trim();
            const matchedDrink = payload?.matchedDrink || 'iced_spanish_latte';
            const drinkInfo = DRINK_METADATA[matchedDrink] || DRINK_METADATA['iced_spanish_latte'];

            const db = getStoredDb();
            const archived = getArchivedDb();

            // Check if archived -> restore
            if (archived[mobile]) {
                const restoredCard = archived[mobile];
                delete archived[mobile];
                saveArchivedDb(archived);
                restoredCard.restoredAt = nowIso;
                if (name) restoredCard.name = name;
                db[mobile] = restoredCard;
                saveStoredDb(db);
                return jsonResponse({ success: true, restored: true, card: restoredCard });
            }

            // Check if already registered
            if (db[mobile]) {
                return jsonResponse({
                    success: false,
                    alreadyRegistered: true,
                    card: db[mobile],
                    redirect: `card.html?phone=${encodeURIComponent(mobile)}`,
                    message: 'Mobile number already registered.'
                }, 409);
            }

            // Generate new pass
            const hex = Math.floor(Math.random() * 0xFFFF).toString(16).toUpperCase().padStart(4, '0');
            const passId = `STP-${hex}-26`;
            const activeOffers = getStoredOffers();

            const stamps = {};
            activeOffers.forEach(off => {
                const idxStr = String(off.index);
                if (off.index === 1) {
                    stamps[idxStr] = {
                        title: `Free ${drinkInfo.name}`,
                        desc: 'Your Quiz Signature Match • 100% Free Drink',
                        icon: drinkInfo.icon,
                        status: 'available',
                        unlockedAt: nowIso,
                        redeemedAt: null
                    };
                } else {
                    stamps[idxStr] = {
                        title: off.title,
                        desc: off.desc,
                        icon: off.icon,
                        status: 'locked',
                        unlockedAt: null,
                        redeemedAt: null
                    };
                }
            });

            const newCard = {
                phone: mobile,
                name: name || 'Valued Guest',
                passId,
                matchedDrink,
                matchedDrinkName: drinkInfo.name,
                matchedDrinkDesc: drinkInfo.desc,
                cardActive: false,
                isBanned: false,
                stamps,
                createdAt: nowIso,
                quizFinishedAt: nowIso,
                activatedAt: null,
                updatedAt: nowIso
            };

            db[mobile] = newCard;
            saveStoredDb(db);
            return jsonResponse({ success: true, card: newCard });
        }

        // 4. GET /api/card
        if (path.endsWith('/api/card') && method === 'GET') {
            const phone = normalizePhone(u.searchParams.get('phone') || '');
            const db = getStoredDb();
            const card = db[phone];
            if (!card) {
                return jsonResponse({ success: false, message: 'Card not found' }, 404);
            }
            if (card.isBanned) {
                return jsonResponse({ success: false, isBanned: true, message: 'Customer is banned' }, 403);
            }
            return jsonResponse({ success: true, card });
        }

        // 5. POST /api/card/activate
        if (path.endsWith('/api/card/activate') && method === 'POST') {
            const phone = normalizePhone(payload?.phone || '');
            const db = getStoredDb();
            const card = db[phone];
            if (!card) return jsonResponse({ success: false, message: 'Card not found' }, 404);
            card.cardActive = true;
            card.activatedAt = nowIso;
            card.updatedAt = nowIso;
            db[phone] = card;
            saveStoredDb(db);
            return jsonResponse({ success: true, card });
        }

        // 6. GET /api/admin/cards
        if (path.endsWith('/api/admin/cards') && method === 'GET') {
            const db = getStoredDb();
            const q = (u.searchParams.get('q') || '').toLowerCase().trim();
            const fromDate = u.searchParams.get('from_date');
            const toDate = u.searchParams.get('to_date');

            let list = Object.values(db);
            if (q) {
                list = list.filter(c => 
                    (c.phone && c.phone.includes(q)) || 
                    (c.name && c.name.toLowerCase().includes(q)) || 
                    (c.passId && c.passId.toLowerCase().includes(q))
                );
            }
            if (fromDate) {
                list = list.filter(c => (c.quizFinishedAt || c.createdAt) >= fromDate);
            }
            if (toDate) {
                list = list.filter(c => (c.quizFinishedAt || c.createdAt) <= toDate + 'T23:59:59');
            }
            return jsonResponse({ success: true, count: list.length, total: Object.keys(db).length, cards: list });
        }

        // 7. GET /api/admin/search
        if (path.endsWith('/api/admin/search')) {
            const phone = normalizePhone(u.searchParams.get('phone') || u.searchParams.get('q') || '');
            const db = getStoredDb();
            const card = db[phone];
            if (!card) return jsonResponse({ success: false, message: 'Card not found' }, 404);
            return jsonResponse({ success: true, card });
        }

        // 8. POST /api/admin/stamp
        if (path.endsWith('/api/admin/stamp') && method === 'POST') {
            const phone = normalizePhone(payload?.phone || '');
            const stampIndex = String(payload?.stampIndex || '1');
            const action = payload?.action || 'redeem';

            const db = getStoredDb();
            const card = db[phone];
            if (!card) return jsonResponse({ success: false, message: 'Card not found' }, 404);

            if (!card.stamps) card.stamps = {};
            if (!card.stamps[stampIndex]) {
                card.stamps[stampIndex] = { title: `Perk #${stampIndex}`, desc: '', icon: '☕', status: 'locked' };
            }

            const stamp = card.stamps[stampIndex];
            if (action === 'redeem') {
                stamp.status = 'redeemed';
                stamp.redeemedAt = nowIso;
                if (!stamp.unlockedAt) stamp.unlockedAt = nowIso;
            } else if (action === 'unlock') {
                stamp.status = 'available';
                stamp.unlockedAt = nowIso;
                stamp.redeemedAt = null;
            } else if (action === 'reset') {
                stamp.status = 'locked';
                stamp.unlockedAt = null;
                stamp.redeemedAt = null;
            }

            card.updatedAt = nowIso;
            db[phone] = card;
            saveStoredDb(db);
            return jsonResponse({ success: true, card });
        }

        // 9. POST /api/admin/customer/ban
        if (path.endsWith('/api/admin/customer/ban') && method === 'POST') {
            const phone = normalizePhone(payload?.phone || '');
            const db = getStoredDb();
            const card = db[phone];
            if (!card) return jsonResponse({ success: false, message: 'Customer not found' }, 404);
            card.isBanned = Boolean(payload?.ban !== false);
            card.bannedAt = card.isBanned ? nowIso : null;
            db[phone] = card;
            saveStoredDb(db);
            return jsonResponse({ success: true, isBanned: card.isBanned });
        }

        // 10. POST /api/admin/customer/delete
        if (path.endsWith('/api/admin/customer/delete') && method === 'POST') {
            const phone = normalizePhone(payload?.phone || '');
            const db = getStoredDb();
            const card = db[phone];
            if (!card) return jsonResponse({ success: false, message: 'Customer not found' }, 404);
            const archived = getArchivedDb();
            card.deletedAt = nowIso;
            archived[phone] = card;
            saveArchivedDb(archived);
            delete db[phone];
            saveStoredDb(db);
            return jsonResponse({ success: true, message: `Customer ${phone} archived and removed.` });
        }

        // 11. POST /api/admin/customer/update-offers
        if (path.endsWith('/api/admin/customer/update-offers') && method === 'POST') {
            const phone = normalizePhone(payload?.phone || '');
            const phones = Array.isArray(payload?.phones) ? payload.phones.map(normalizePhone) : (phone ? [phone] : []);
            const reason = payload?.reason || 'Campaign upgrade';
            const offers = getStoredOffers();
            const db = getStoredDb();
            let count = 0;

            phones.forEach(p => {
                const card = db[p];
                if (!card) return;
                if (!card.offersHistory) card.offersHistory = [];
                card.offersHistory.push({
                    historyId: `hist_${Date.now()}`,
                    archivedAt: nowIso,
                    reason,
                    offersCount: Object.keys(card.stamps || {}).length,
                    stamps: JSON.parse(JSON.stringify(card.stamps || {}))
                });

                offers.forEach(off => {
                    const idxStr = String(off.index);
                    const isFirst = (off.index === 1);
                    if (!card.stamps[idxStr]) {
                        card.stamps[idxStr] = { status: 'locked', unlockedAt: null, redeemedAt: null };
                    }
                    if (!isFirst) {
                        card.stamps[idxStr].title = off.title;
                        card.stamps[idxStr].desc = off.desc;
                        card.stamps[idxStr].icon = off.icon;
                    }
                });
                card.updatedAt = nowIso;
                count++;
            });

            saveStoredDb(db);
            return jsonResponse({ success: true, updatedCount: count, message: `Upgraded ${count} customer card(s).` });
        }

        // 12. GET /api/admin/customer/history
        if (path.endsWith('/api/admin/customer/history') && method === 'GET') {
            const phone = normalizePhone(u.searchParams.get('phone') || '');
            const db = getStoredDb();
            const card = db[phone];
            if (!card) return jsonResponse({ success: false, message: 'Card not found' }, 404);
            return jsonResponse({ success: true, phone, historyCount: (card.offersHistory || []).length, history: card.offersHistory || [] });
        }

        return jsonResponse({ success: false, message: 'Not found' }, 404);
    };

    // Monkey-patch window.fetch to seamlessly intercept /api requests on GitHub Pages or fallback on failure
    const _originalFetch = window.fetch;
    window.fetch = async function(input, init) {
        const url = typeof input === 'string' ? input : (input && input.url ? input.url : '');

        // Only intercept /api or api/ calls
        if (url && (url.includes('/api/') || url.startsWith('api/'))) {
            if (isCloudDemo) {
                return handleMockRequest(url, init);
            }
            try {
                const res = await _originalFetch.apply(this, arguments);
                if (!res.ok && res.status === 404) {
                    return handleMockRequest(url, init);
                }
                return res;
            } catch (_) {
                return handleMockRequest(url, init);
            }
        }

        return _originalFetch.apply(this, arguments);
    };

})();
