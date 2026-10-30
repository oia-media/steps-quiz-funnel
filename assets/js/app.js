/**
 * STEPS Specialty Coffee Bar - Sales Funnel & Loyalty Card Engine
 * Includes 3-Question Funnel, 250ms Auto-Advance, 1-1-1 Tie-Breaker,
 * and Interactive Digital Loyalty Card Activation with Reward Unlocking.
 */
(() => {
    'use strict';

    const app = document.querySelector('#quiz-app');
    if (!app) return;

    if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
    window.scrollTo(0, 0);

    const config = window.STEPS_QUIZ || {
        submitUrl: 'api/submit.php',
        totalQuestions: 3
    };

    // Drink Profiles
    const DRINKS = {
        iced_spanish_latte: {
            name: 'Iced Spanish Latte',
            desc: 'Silky espresso combined with sweet condensed milk, served over chilled ice.',
            base: 'Iced Espresso Coffee'
        },
        strawberry_matcha: {
            name: 'Strawberry Matcha',
            desc: 'Ceremonial Japanese green tea layered over sweet handcrafted strawberry puree.',
            base: 'Japanese Green Tea'
        },
        passionfruit_mojito: {
            name: 'Passionfruit Mojito',
            desc: 'Zesty passionfruit, crushed mint and sparkling fruit soda with crisp citrus notes.',
            base: 'Fizzy Fruit Soda'
        },
        mocha_frappe: {
            name: 'Mocha Frappe',
            desc: 'Blended ice, rich espresso, and decadent dark chocolate topped with cold velvet cream.',
            base: 'Blended Ice & Coffee'
        }
    };

    // Subsequent Loyalty Rewards (Revealed upon Activation)
    const REVEALED_STAMPS = {
        2: { icon: '🥐', title: '20% Off Pastry', desc: 'Fresh Bakery Item', tag: 'Unlocked' },
        3: { icon: '☕', title: 'Free Upgrade', desc: 'Size Upgrade', tag: 'Unlocked' },
        4: { icon: '🎁', title: 'Buy 1 Get 1', desc: 'Signature Drinks', tag: 'Unlocked' },
        5: { icon: '🌟', title: 'Free Drink + VIP', desc: 'Any Signature Drink', tag: 'VIP Reward' }
    };

    const screens = [...app.querySelectorAll('[data-screen]')];
    const questionScreens = [...app.querySelectorAll('.question-screen')];
    const headerProgress = app.querySelector('#header-progress');
    const progressFill = app.querySelector('#progress-fill');
    const progressCount = app.querySelector('#progress-count');
    const status = app.querySelector('#sr-status');
    const claimForm = app.querySelector('#claim-form');
    const formMessage = app.querySelector('#form-message');
    const confettiCanvas = document.querySelector('#confetti-canvas');

    const answers = {};
    let currentStep = 0;
    let autoAdvanceTimer = null;
    let activeResult = null;
    let memberData = { name: '', mobile: '', passId: '' };

    // Screen Navigation
    const showScreen = (name, step = currentStep) => {
        screens.forEach((screen) => {
            const matches = screen.dataset.screen === name
                && (name !== 'question' || Number(screen.dataset.step) === step);
            screen.hidden = !matches;
            screen.classList.toggle('is-active', matches);
        });

        const isQuestion = name === 'question';
        headerProgress.hidden = !isQuestion;

        if (isQuestion) {
            const percent = (step / config.totalQuestions) * 100;
            progressFill.style.width = `${percent}%`;
            progressCount.textContent = `${String(step).padStart(2, '0')} / ${String(config.totalQuestions).padStart(2, '0')}`;
        }

        requestAnimationFrame(() => {
            const active = screens.find((screen) => !screen.hidden);
            const heading = active?.querySelector('h1, h2');
            if (heading) {
                heading.setAttribute('tabindex', '-1');
                heading.focus({ preventScroll: true });
            }
            window.scrollTo({ top: 0, behavior: 'auto' });
        });
    };

    // Calculate Winning Drink with 1-1-1 Anchor Tie-Breaker
    const calculateWinner = (answers) => {
        const scores = {
            iced_spanish_latte: 0,
            strawberry_matcha: 0,
            passionfruit_mojito: 0,
            mocha_frappe: 0
        };

        ['q1', 'q2', 'q3'].forEach((q) => {
            const selected = answers[q];
            if (selected && scores[selected] !== undefined) {
                scores[selected] += 1;
            }
        });

        // 1. Majority Rule: Check if any drink has 2 or 3 votes
        for (const [key, score] of Object.entries(scores)) {
            if (score >= 2) {
                return DRINKS[key] ? { key, ...DRINKS[key] } : { key, ...DRINKS.iced_spanish_latte };
            }
        }

        // 2. 1-1-1 Tie Rule (Telegraph Brief Specification):
        // In any 1-1-1 tie, Question 1 (The Base) is the Anchor Decider.
        const q1Key = answers.q1;
        if (q1Key && DRINKS[q1Key]) {
            return { key: q1Key, ...DRINKS[q1Key] };
        }

        return { key: 'iced_spanish_latte', ...DRINKS.iced_spanish_latte };
    };

    // Start Quiz -> Directly opens Question 1
    const startQuiz = () => {
        currentStep = 1;
        showScreen('question', currentStep);
        status.textContent = 'Question 1 of 3';
    };

    // Reset Quiz
    const resetQuiz = () => {
        clearTimeout(autoAdvanceTimer);
        Object.keys(answers).forEach((k) => delete answers[k]);
        questionScreens.forEach((screen) => {
            screen.querySelector('form').reset();
            const btn = screen.querySelector('.next-button');
            if (btn) btn.disabled = true;
        });
        if (claimForm) claimForm.reset();
        if (formMessage) formMessage.textContent = '';
        currentStep = 0;
        activeResult = null;
        resetLoyaltyCardUI();
        showScreen('landing');
    };

    // Reset Loyalty Card UI to Initial State
    const resetLoyaltyCardUI = () => {
        const card = app.querySelector('#loyalty-card');
        const statusPill = app.querySelector('#card-status-pill');
        const statusText = app.querySelector('#card-status-text');
        const activationBox = app.querySelector('#card-activation-box');
        const barcodeBox = app.querySelector('#card-barcode-box');
        const stampsLabel = app.querySelector('#stamps-count-label');

        if (!card) return;
        card.classList.remove('is-activated');
        if (statusPill) statusPill.classList.remove('active');
        if (statusText) statusText.textContent = 'Pending Activation';
        if (activationBox) activationBox.hidden = false;
        if (barcodeBox) barcodeBox.hidden = true;
        if (stampsLabel) stampsLabel.textContent = 'Stamp 1 of 5 Ready';

        // Reset locked stamps
        [2, 3, 4, 5].forEach((num) => {
            const slot = app.querySelector(`.stamp-slot[data-stamp="${num}"]`);
            if (slot) {
                slot.classList.add('is-locked');
                slot.classList.remove('is-revealed');
                const badge = slot.querySelector('.stamp-badge');
                if (badge) badge.innerHTML = `<span class="stamp-icon">🔒</span><span class="stamp-number">${num}</span>`;
                const tag = slot.querySelector('.stamp-status-tag');
                if (tag) tag.textContent = num === 5 ? 'Grand Prize' : 'Locked';
            }
        });
    };

    // Generate Member Pass ID
    const generatePassId = () => {
        const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
        let code = '';
        for (let i = 0; i < 4; i++) {
            code += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        return `STP-${code}-26`;
    };

    // Advance to Next Step or Complete Quiz
    const proceedToNextStep = () => {
        if (currentStep < config.totalQuestions) {
            currentStep += 1;
            showScreen('question', currentStep);
            status.textContent = `Question ${currentStep} of ${config.totalQuestions}`;
        } else {
            // All 3 questions answered -> Show calculating interstitial briefly
            showScreen('calculating');
            status.textContent = 'Analyzing your taste profile...';

            activeResult = calculateWinner(answers);

            setTimeout(() => {
                showScreen('claim');
                status.textContent = 'Claim your matched drink and loyalty card.';
                const nameInput = app.querySelector('#full-name');
                if (nameInput) nameInput.focus();
            }, 850);
        }
    };

    // Auto-Advance UX: 250ms after user taps an option
    app.addEventListener('change', (event) => {
        const input = event.target.closest('.question-form input[type="radio"]');
        if (!input) return;

        const form = input.closest('.question-form');
        const qKey = form.dataset.question;
        answers[qKey] = input.value;

        const nextBtn = form.querySelector('.next-button');
        if (nextBtn) nextBtn.disabled = false;

        // Visual feedback animation
        const card = input.closest('.option-card');
        if (card) {
            card.style.transform = 'scale(0.98)';
            setTimeout(() => { card.style.transform = ''; }, 120);
        }

        // 250ms auto advance as specified in Telegraph Brief
        clearTimeout(autoAdvanceTimer);
        autoAdvanceTimer = setTimeout(() => {
            proceedToNextStep();
        }, 250);
    });

    // Form Submit (Keyboard enter / manual next click)
    questionScreens.forEach((screen) => {
        const form = screen.querySelector('.question-form');
        form.addEventListener('submit', (event) => {
            event.preventDefault();
            clearTimeout(autoAdvanceTimer);
            const selected = form.querySelector('input:checked');
            if (!selected) return;
            answers[form.dataset.question] = selected.value;
            proceedToNextStep();
        });
    });

    // Global Click Handler
    app.addEventListener('click', (event) => {
        const control = event.target.closest('[data-action]');
        if (!control) return;

        switch (control.dataset.action) {
            case 'start':
                startQuiz();
                break;
            case 'back': {
                clearTimeout(autoAdvanceTimer);
                const active = screens.find((screen) => !screen.hidden);
                if (active?.dataset.screen === 'claim') {
                    currentStep = config.totalQuestions;
                    showScreen('question', currentStep);
                } else if (currentStep > 1) {
                    currentStep -= 1;
                    showScreen('question', currentStep);
                } else {
                    resetQuiz();
                }
                break;
            }
            case 'reset':
            case 'done':
                if (memberData && memberData.mobile) {
                    window.location.href = `card.html?phone=${encodeURIComponent(memberData.mobile)}`;
                } else {
                    resetQuiz();
                }
                break;
        }
    });

    // Claim Form Submission
    claimForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const submitButton = claimForm.querySelector('[type="submit"]');
        const nameInput = claimForm.elements.name;
        const mobileInput = claimForm.elements.mobile;
        const name = nameInput.value.trim().replace(/\s+/g, ' ');
        const mobile = mobileInput.value.trim();

        nameInput.removeAttribute('aria-invalid');
        mobileInput.removeAttribute('aria-invalid');
        formMessage.textContent = '';

        if (name.length < 2 || name.length > 120) {
            nameInput.setAttribute('aria-invalid', 'true');
            formMessage.textContent = 'Please enter your full name.';
            nameInput.focus();
            return;
        }

        // Helper to normalize and clean Egyptian mobile number
        const cleanEgyptMobile = (val) => {
            let clean = val.trim().replace(/[\s\-()._]/g, '');
            if (clean.startsWith('+20')) {
                clean = '0' + clean.slice(3);
            } else if (clean.startsWith('0020')) {
                clean = '0' + clean.slice(4);
            } else if (clean.startsWith('20') && clean.length === 12) {
                clean = '0' + clean.slice(2);
            } else if (/^1[0125][0-9]{8}$/.test(clean)) {
                clean = '0' + clean;
            }
            return clean;
        };

        const checkFakeEgyptMobile = (num) => {
            if (!/^01[0125][0-9]{8}$/.test(num)) {
                return { isFake: true, message: 'Please enter a valid Egyptian mobile number (11 digits starting with 010, 011, 012, or 015).' };
            }

            const suffix = num.slice(3);

            // 1. Repeated identical digits
            if (/(\d)\1{4,}/.test(suffix)) {
                return { isFake: true, message: 'This number contains unrealistic repeated digits. Please enter an active Egyptian mobile.' };
            }

            // 2. Sequential ascending or descending patterns (e.g. 34567890, 12345678)
            const seqs = [
                '01234567', '12345678', '23456789', '34567890', '45678901', '56789012', '67890123',
                '98765432', '87654321', '76543210', '65432109', '54321098', '43210987'
            ];
            for (const s of seqs) {
                if (suffix.includes(s)) {
                    return { isFake: true, message: `"${num}" is an invalid sequential test number. Please enter a genuine Egyptian mobile.` };
                }
            }

            // 3. Arithmetic progressions (e.g. 34567890)
            const diff = Number(suffix[1]) - Number(suffix[0]);
            if (diff !== 0) {
                let isAp = true;
                for (let i = 2; i < suffix.length; i++) {
                    if ((Number(suffix[i]) - Number(suffix[i-1])) !== diff) {
                        isAp = false;
                        break;
                    }
                }
                if (isAp) {
                    return { isFake: true, message: 'Sequential arithmetic pattern detected. Please enter a genuine Egyptian mobile.' };
                }
            }

            // 4. Repeated 2-digit, 3-digit, 4-digit chunks
            if (/^(\d{2})\1{3}$/.test(suffix) || /^(\d{4})\1$/.test(suffix)) {
                return { isFake: true, message: 'Repetitive pattern detected. Please enter a genuine Egyptian mobile number.' };
            }

            // 5. Low entropy: at least 4 unique digits
            const uniqueDigits = new Set(suffix.split(''));
            if (uniqueDigits.size < 4) {
                return { isFake: true, message: 'Number lacks realistic digit variation. Please enter a real phone number.' };
            }

            // 6. Blacklisted known dummy numbers
            const knownFakes = [
                '01034567890', '01134567890', '01234567890', '01534567890',
                '01012345678', '01112345678', '01212345678', '01512345678'
            ];
            if (knownFakes.includes(num)) {
                return { isFake: true, message: 'This test number is blacklisted. Please enter a real Egyptian mobile number.' };
            }

            return { isFake: false };
        };

        const cleanedMobile = cleanEgyptMobile(mobile);
        const fakeCheck = checkFakeEgyptMobile(cleanedMobile);

        if (fakeCheck.isFake) {
            mobileInput.setAttribute('aria-invalid', 'true');
            formMessage.textContent = fakeCheck.message;
            mobileInput.focus();
            return;
        }

        submitButton.disabled = true;
        const originalBtnText = submitButton.innerHTML;
        submitButton.innerHTML = 'Activating Card...';

        if (!activeResult) {
            activeResult = calculateWinner(answers);
        }

        const passId = generatePassId();
        memberData = { name, mobile: cleanedMobile, passId };

        // Attempt server submission with graceful local fallback
        try {
            const payload = {
                name,
                mobile: cleanedMobile,
                passId,
                answers,
                matchedDrink: activeResult.key
            };

            const res = await fetch(config.submitUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();

            // Save phone to localStorage
            try {
                localStorage.setItem('steps_saved_phone', cleanedMobile);
            } catch (_) {}

            if (data.alreadyRegistered) {
                // Show pop-up modal with highlighted title and 3-second direct
                const modal = document.querySelector('#already-registered-modal');
                const targetUrl = `card.html?phone=${encodeURIComponent(cleanedMobile)}`;
                if (modal) {
                    modal.hidden = false;
                    const countdownEl = document.querySelector('#modal-countdown');
                    const progressFill = document.querySelector('#modal-progress-fill');
                    const openBtn = document.querySelector('#btn-modal-open-now');

                    let countdownTimer = null;
                    const directToCard = () => {
                        if (countdownTimer) clearInterval(countdownTimer);
                        window.location.href = targetUrl;
                    };

                    if (openBtn) {
                        openBtn.onclick = directToCard;
                    }

                    let elapsedMs = 0;
                    const totalMs = 3000;
                    const intervalMs = 50;

                    countdownTimer = setInterval(() => {
                        elapsedMs += intervalMs;
                        const progressPct = Math.min(100, (elapsedMs / totalMs) * 100);
                        if (progressFill) progressFill.style.width = progressPct + '%';

                        const remainingSec = Math.max(1, Math.ceil((totalMs - elapsedMs) / 1000));
                        if (countdownEl) countdownEl.textContent = remainingSec;

                        if (elapsedMs >= totalMs) {
                            directToCard();
                        }
                    }, intervalMs);
                } else {
                    window.location.href = targetUrl;
                }
                return;
            }

            if (!res.ok && !data.success) {
                formMessage.style.color = 'var(--error)';
                formMessage.textContent = data.message || 'Please check your mobile number.';
                submitButton.disabled = false;
                submitButton.innerHTML = originalBtnText;
                return;
            }

            // Normal new registration -> Direct straight to dedicated /card pass!
            submitButton.innerHTML = 'Pass Ready! Opening...';
            setTimeout(() => {
                window.location.href = `card.html?phone=${encodeURIComponent(cleanedMobile)}`;
            }, 600);
            return;
        } catch (error) {
            // Local file:// or offline fallback
            try {
                localStorage.setItem('steps_saved_phone', cleanedMobile);
            } catch (_) {}
            renderThankYouScreen(activeResult, memberData);
            showScreen('thanks');
        } finally {
            submitButton.disabled = false;
            submitButton.innerHTML = originalBtnText;
        }
    });

    // Real-time validation for Egyptian Mobile Number input
    const mobileInputEl = claimForm ? claimForm.elements.mobile : null;
    const nameInputEl = claimForm ? claimForm.elements.name : null;

    if (mobileInputEl) {
        mobileInputEl.addEventListener('input', () => {
            const val = mobileInputEl.value.trim().replace(/[\s\-()._]/g, '');
            if (!val) {
                mobileInputEl.removeAttribute('aria-invalid');
                formMessage.textContent = '';
                return;
            }

            // Immediately catch invalid prefixes like 013, 014, 016, 017, etc.
            if (val.startsWith('01') && val.length >= 3) {
                const thirdDigit = val.charAt(2);
                if (!['0', '1', '2', '5'].includes(thirdDigit)) {
                    mobileInputEl.setAttribute('aria-invalid', 'true');
                    formMessage.textContent = 'Invalid Egyptian network. Number must start with 010 (Vodafone), 011 (Etisalat), 012 (Orange), or 015 (WE).';
                    return;
                }
            }

            // Check if length exceeds 11 digits (or full normalized format)
            if (val.length > 11 && !val.startsWith('+20') && !val.startsWith('0020')) {
                mobileInputEl.setAttribute('aria-invalid', 'true');
                formMessage.textContent = 'Egyptian mobile numbers must be exactly 11 digits (e.g. 01012345678).';
                return;
            }

            // If 11 digits entered, check anti-fake heuristics live
            const normalized = cleanEgyptMobile(val);
            if (normalized.length === 11) {
                const fake = checkFakeEgyptMobile(normalized);
                if (fake.isFake) {
                    mobileInputEl.setAttribute('aria-invalid', 'true');
                    formMessage.textContent = fake.message;
                    return;
                }
            }

            // Clear error if looking valid
            mobileInputEl.removeAttribute('aria-invalid');
            formMessage.textContent = '';
        });
    }

    if (nameInputEl) {
        nameInputEl.addEventListener('input', () => {
            if (nameInputEl.value.trim().length >= 2) {
                nameInputEl.removeAttribute('aria-invalid');
                if (formMessage.textContent.includes('name')) {
                    formMessage.textContent = '';
                }
            }
        });
    }

    // Populate Thank You & Loyalty Card Screen
    const renderThankYouScreen = (result, member) => {
        // Matched Drink
        const drinkTitle = app.querySelector('#thanks-drink');
        const drinkDesc = app.querySelector('#thanks-drink-desc');
        if (drinkTitle) drinkTitle.textContent = result.name;
        if (drinkDesc) drinkDesc.textContent = result.desc;

        // Cardholder details
        const cardName = app.querySelector('#card-holder-name');
        const cardPass = app.querySelector('#card-pass-id');
        const barcodeDisplay = app.querySelector('#barcode-display');
        const openCardBtn = app.querySelector('#btn-open-dedicated-card');

        if (cardName) cardName.textContent = member.name || 'Valued Member';
        if (cardPass) cardPass.textContent = member.passId;
        if (barcodeDisplay) barcodeDisplay.textContent = member.passId;

        if (openCardBtn && member.mobile) {
            openCardBtn.href = `card.html?phone=${encodeURIComponent(member.mobile)}`;
            try {
                localStorage.setItem('steps_saved_phone', member.mobile);
            } catch (_) {}
        }
    };

    // Loyalty Card Activation Handler
    const activateButton = app.querySelector('#btn-activate-card');
    if (activateButton) {
        activateButton.addEventListener('click', () => {
            activateLoyaltyCard();
        });
    }

    const activateLoyaltyCard = () => {
        const card = app.querySelector('#loyalty-card');
        const statusPill = app.querySelector('#card-status-pill');
        const statusText = app.querySelector('#card-status-text');
        const activationBox = app.querySelector('#card-activation-box');
        const barcodeBox = app.querySelector('#card-barcode-box');
        const stampsLabel = app.querySelector('#stamps-count-label');

        if (!card) return;

        card.classList.add('is-activated');
        if (statusPill) statusPill.classList.add('active');
        if (statusText) statusText.textContent = 'Active VIP Member';
        if (activationBox) activationBox.hidden = true;
        if (barcodeBox) barcodeBox.hidden = false;
        if (stampsLabel) stampsLabel.textContent = 'All 5 Stamps Unlocked!';

        // Trigger Confetti Burst
        triggerConfetti();

        // Staggered reveal of locked stamps 2 through 5
        [2, 3, 4, 5].forEach((num, index) => {
            setTimeout(() => {
                const slot = app.querySelector(`.stamp-slot[data-stamp="${num}"]`);
                const reward = REVEALED_STAMPS[num];
                if (slot && reward) {
                    slot.classList.remove('is-locked');
                    slot.classList.add('is-revealed');

                    const badge = slot.querySelector('.stamp-badge');
                    if (badge) {
                        badge.innerHTML = `<span class="stamp-icon">${reward.icon}</span><span class="stamp-number">${num}</span>`;
                    }

                    const strong = slot.querySelector('.stamp-title') || slot.querySelector('.stamp-meta strong');
                    const small = slot.querySelector('.stamp-desc') || slot.querySelector('.stamp-meta small');
                    const tag = slot.querySelector('.stamp-status-tag');

                    if (strong) strong.textContent = reward.title;
                    if (small) small.textContent = reward.desc;
                    if (tag) tag.textContent = reward.tag;
                }
            }, 250 + (index * 160));
        });

        status.textContent = 'Digital Loyalty Card activated! All rewards are now revealed.';
    };

    // Save Pass / Wallet Action
    const savePassBtn = app.querySelector('#btn-save-pass');
    if (savePassBtn) {
        savePassBtn.addEventListener('click', () => {
            const passDetails = `STEPS SPECIALTY COFFEE BAR - DIGITAL LOYALTY PASS\n`
                + `Member: ${memberData.name}\n`
                + `Pass ID: ${memberData.passId}\n`
                + `First Order: Free Coffee (${activeResult?.name || 'Signature Drink'})\n`
                + `Status: Active VIP Member\n`
                + `Present this pass at STEPS counter to redeem.`;

            const blob = new Blob([passDetails], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `STEPS-Loyalty-Card-${memberData.passId}.txt`;
            a.click();
            URL.revokeObjectURL(url);

            savePassBtn.innerHTML = `✓ Pass Saved!`;
            setTimeout(() => {
                savePassBtn.innerHTML = `<svg viewBox="0 0 24 24" width="18" height="18"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg> Save Pass to Device`;
            }, 2500);
        });
    }

    // Share Pass Action
    const sharePassBtn = app.querySelector('#btn-share-pass');
    if (sharePassBtn) {
        sharePassBtn.addEventListener('click', async () => {
            const shareText = `I just took the STEPS Quiz and got a Digital Loyalty Card with my first coffee free! Check it out: ${window.location.href}`;
            if (navigator.share) {
                try {
                    await navigator.share({
                        title: 'STEPS Coffee Digital Loyalty Card',
                        text: shareText,
                        url: window.location.href
                    });
                } catch (_) {}
            } else if (navigator.clipboard) {
                await navigator.clipboard.writeText(shareText);
                sharePassBtn.textContent = '✓ Link Copied!';
                setTimeout(() => {
                    sharePassBtn.innerHTML = `<svg viewBox="0 0 24 24" width="18" height="18"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg> Share Card`;
                }, 2000);
            }
        });
    }

    // Lightweight Confetti Particle Engine
    const triggerConfetti = () => {
        if (!confettiCanvas) return;
        const ctx = confettiCanvas.getContext('2d');
        confettiCanvas.width = window.innerWidth;
        confettiCanvas.height = window.innerHeight;

        const colors = ['#dfba73', '#c5a059', '#2e2019', '#f7e7c4', '#ffffff', '#e6a23c'];
        const particles = [];
        const count = 90;

        for (let i = 0; i < count; i++) {
            particles.push({
                x: window.innerWidth * (0.35 + Math.random() * 0.3),
                y: window.innerHeight * 0.5,
                w: 6 + Math.random() * 8,
                h: 4 + Math.random() * 6,
                color: colors[Math.floor(Math.random() * colors.length)],
                vx: (Math.random() - 0.5) * 14,
                vy: -(Math.random() * 12 + 6),
                gravity: 0.35 + Math.random() * 0.2,
                rotation: Math.random() * 360,
                vRot: (Math.random() - 0.5) * 10,
                opacity: 1
            });
        }

        let animId;
        const render = () => {
            ctx.clearRect(0, 0, confettiCanvas.width, confettiCanvas.height);
            let activeParticles = 0;

            particles.forEach((p) => {
                p.x += p.vx;
                p.y += p.vy;
                p.vy += p.gravity;
                p.rotation += p.vRot;
                p.vx *= 0.98;
                p.opacity -= 0.009;

                if (p.opacity > 0 && p.y < confettiCanvas.height) {
                    activeParticles++;
                    ctx.save();
                    ctx.translate(p.x, p.y);
                    ctx.rotate((p.rotation * Math.PI) / 180);
                    ctx.fillStyle = p.color;
                    ctx.globalAlpha = Math.max(0, p.opacity);
                    ctx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h);
                    ctx.restore();
                }
            });

            if (activeParticles > 0) {
                animId = requestAnimationFrame(render);
            } else {
                ctx.clearRect(0, 0, confettiCanvas.width, confettiCanvas.height);
                cancelAnimationFrame(animId);
            }
        };

        render();
    };

    // Window resize handler for canvas
    window.addEventListener('resize', () => {
        if (confettiCanvas) {
            confettiCanvas.width = window.innerWidth;
            confettiCanvas.height = window.innerHeight;
        }
    });

})();
