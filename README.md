# STEPS Specialty Coffee Bar — Sales Funnel & Digital Loyalty Ecosystem

A high-converting sales funnel and interactive digital loyalty card ecosystem modeled after [steps.the-marketscene.com](https://steps.the-marketscene.com/) and upgraded with the streamlined 3-question logic from the [Telegraph Brief](https://telegra.ph/STEPS-Quiz---Complete-Final-Brief-10-21).

---

## 🌟 Architecture & Endpoints

| Endpoint | Target Audience | Description |
| :--- | :--- | :--- |
| **`http://localhost:8000/quiz`** | Customer | **New Luxury 3-Question Quiz UI (`quiz.html`)**. Elevated dark-luxury aesthetics with ambient lighting, glassmorphic cards, step tracker, and instant pass issuance. |
| **`http://localhost:8000/`** | Customer | **Main Landing / Quiz Funnel**. Defaults to the new elevated quiz experience. |
| **`http://localhost:8000/card`** | Customer | **Dedicated Digital Loyalty Pass (`card.html`)**. Customers access their card anytime via their phone number. Features live 3-second auto-sync with barista actions. |
| **`http://localhost:8000/admin`** | Barista / Staff | **Store POS & Barista Admin (`admin.html`)**. Search members by phone or pass ID, redeem Free Coffee, unlock stamps 2–5, and add visit stamps. |
| **`http://localhost:8000/classic`** | Customer | **Classic 1-to-1 Funnel Replica (`index.html`)**. Original landing replica. |

---

## ☕ Key Features

1. **Brand-New Elevated Quiz UI (`/quiz`)**:
   - Modern dark-luxury specialty coffee house aesthetic with warm radial lighting and glassmorphism cards.
   - Interactive step tracker (`[1. Base] — [2. Flavor] — [3. Vibe]`).
   - 250ms smooth auto-advance upon selecting options.
   - Coffee brewing taste lab animation.
   - **Repeat Quiz Prevention**: If an Egyptian phone number has already completed the quiz, the system blocks retaking and directly navigates them to their existing card at `/card?phone=...`.
2. **Dedicated `/card` Endpoint**:
   - Customers don't have to retake the quiz to see their loyalty card.
   - Access anytime at `/card` with their mobile number.
   - High-end Apple Wallet metallic dark pass design with live barcode, QR code, and customer pass ID.
   - **Real-Time Live Polling**: When a barista unlocks or redeems an offer in `/admin`, the customer's `/card` screen updates instantly without refreshing!
2. **1 Loyalty Card Per Phone Number**:
   - Phone number is strictly enforced as a unique key in `cards_db.json`.
   - Re-taking the quiz updates the customer's drink preference without resetting any earned stamps or redeemed rewards.
3. **Barista Admin Portal (`/admin`)**:
   - Search by Phone (e.g. `010...`), Customer Name, or Pass ID.
   - One-click stamp actions:
     - `☕ Redeem Free Coffee` (Stamp 1)
     - `🥐 Unlock / Redeem 20% Off Pastry` (Stamp 2)
     - `🥛 Unlock / Redeem Free Upgrade` (Stamp 3)
     - `🎁 Unlock / Redeem Buy 1 Get 1 Free` (Stamp 4)
     - `🌟 Unlock / Redeem Grand VIP Drink` (Stamp 5)
     - `+ Add Visit Stamp` (Automatically unlocks the next available tier)
4. **Strict Egyptian Mobile Validation**:
   - Strictly validates 11-digit numbers starting with `010` (Vodafone), `011` (Etisalat), `012` (Orange), or `015` (WE).
   - Rejects fake prefixes (e.g. `013...`) with instant real-time live input guidance.
5. **1-1-1 Anchor Tie-Breaker**:
   - In any 3-way tie, Question 1 (The Base) automatically wins as the Anchor Decider.

---

## 📁 File Structure

```
steps-quiz-funnel/
├── index.html              # Main Sales Funnel (/)
├── card.html               # Dedicated Customer Pass Endpoint (/card)
├── admin.html              # Barista & Store POS Admin (/admin)
├── assets/
│   ├── css/
│   │   └── app.css         # STEPS branding, responsive styling & loyalty card UI
│   ├── js/
│   │   └── app.js          # Funnel state machine, tie logic, confetti, card activation
│   └── images/             # Official brand images (desktop & mobile banners, logo)
├── api/
│   └── submit.php          # PHP endpoint for production Apache/Nginx hosting
├── server.py               # Built-in multi-endpoint local Python server
├── cards_db.json           # Live Loyalty Card Database (Unique phone key)
├── leads.csv               # Exportable CSV leads database
└── README.md               # Documentation
```

---

## 🚀 How to Run

Run the bundled server from your terminal:

```bash
cd ~/Downloads/steps-quiz-funnel
python3 server.py
```

Open your browser to:
- **Sales Funnel**: [http://localhost:8000/](http://localhost:8000/)
- **Customer Card**: [http://localhost:8000/card](http://localhost:8000/card)
- **Barista Admin**: [http://localhost:8000/admin](http://localhost:8000/admin)
