/**
 * Overdue -- Application JavaScript
 * Toast system, HTMX event listeners, gauge re-initialization.
 */

/* ============================================================
   TOAST SYSTEM (with stagger queue)
   ============================================================ */

const toastQueue = [];
let toastProcessing = false;

function queueToast(text, type, iconId) {
    toastQueue.push({ text: text, type: type, iconId: iconId });
    if (!toastProcessing) processToastQueue();
}

function processToastQueue() {
    if (toastQueue.length === 0) {
        toastProcessing = false;
        return;
    }
    toastProcessing = true;
    const item = toastQueue.shift();
    showToast(item.text, item.type, item.iconId);
    setTimeout(processToastQueue, 400);
}

/**
 * Read pre-rendered pixel art icon SVG from hidden <template> elements.
 * Returns a cloned DOM node (not a string), safe from XSS since the content
 * originates from server-rendered templates, never from user input.
 */
function _iconNode(id) {
    const tpl = document.getElementById('icon-' + id);
    if (!tpl) return null;
    return tpl.content.cloneNode(true);
}

function showToast(text, type, iconId) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = 'pixel-card text-center py-3 px-5 min-w-[220px]';
    toast.style.pointerEvents = 'auto';
    const borderColors = { badge: '#b76ef0', rank: '#f0c543', party: '#b76ef0' };
    toast.style.borderColor = borderColors[type] || '#5cdb5c';
    toast.style.animation = 'toast-slide-in 0.3s ease-out';
    if (type === 'party') toast.style.animation += ', party-glow 2s linear infinite';

    const span = document.createElement('span');
    span.className = 'font-pixel text-[10px]';
    if (type === 'xp') {
        span.className += ' text-dewey-pristine';
    } else if (type === 'streak') {
        span.className += ' text-streak';
    } else if (type === 'badge') {
        span.className += ' text-badge-common';
    } else if (type === 'rank') {
        span.className += ' gold-shimmer';
    } else if (type === 'party') {
        span.className += ' gold-shimmer';
    }

    /* Prepend pixel art icon if available, then add text safely */
    const icon = iconId ? _iconNode(iconId) : null;
    if (icon) {
        span.appendChild(icon);
        span.appendChild(document.createTextNode(' '));
    }
    span.appendChild(document.createTextNode(text));
    toast.appendChild(span);

    container.appendChild(toast);

    setTimeout(function() {
        toast.style.animation = 'toast-fade-out 0.5s ease-out forwards';
        setTimeout(function() {
            if (toast.parentNode) toast.parentNode.removeChild(toast);
        }, 500);
    }, 3000);
}

/* ============================================================
   REVIEW CELEBRATION EFFECT
   ============================================================ */

function showReviewCelebration() {
    // Respect prefers-reduced-motion
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    // Pixel particle burst from review section (use pre-swap position if available)
    let rect = window.__reviewSectionRect;
    if (!rect) {
        const target = document.getElementById('review-section');
        if (!target) return;
        rect = target.getBoundingClientRect();
    }
    delete window.__reviewSectionRect;
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    const colors = ['#f0c543', '#5cdb5c', '#b76ef0', '#e8563e', '#7eb5e3', '#ffe9a0', '#a0d468', '#f6bb42'];

    for (let i = 0; i < 8; i++) {
        const particle = document.createElement('div');
        const angle = (i / 8) * 2 * Math.PI;
        const dx = Math.cos(angle) * 80;
        const dy = Math.sin(angle) * 80;
        particle.style.cssText = 'position:fixed;width:6px;height:6px;pointer-events:none;z-index:9999;' +
            'left:' + cx + 'px;top:' + cy + 'px;background:' + colors[i] + ';' +
            'animation:star-burst 0.6s ease-out forwards;' +
            '--dx:' + dx + 'px;--dy:' + dy + 'px;';
        // Use inline transform for each particle direction
        particle.animate([
            { transform: 'translate(0, 0) scale(1)', opacity: 1 },
            { transform: 'translate(' + dx + 'px, ' + dy + 'px) scale(0)', opacity: 0 }
        ], { duration: 600, easing: 'ease-out', fill: 'forwards' });
        document.body.appendChild(particle);
        (function(p) {
            setTimeout(function() { if (p.parentNode) p.parentNode.removeChild(p); }, 700);
        })(particle);
    }
}

/* ============================================================
   UI SOUND EFFECTS
   ============================================================ */

const uiSfxState = {
    context: null
};

function getUiAudioContext() {
    if (uiSfxState.context) return uiSfxState.context;
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (!AudioCtx) return null;
    uiSfxState.context = new AudioCtx();
    return uiSfxState.context;
}

function scheduleUiTone(kind) {
    const context = getUiAudioContext();
    if (!context) return;

    if (context.state === 'suspended' && typeof context.resume === 'function') {
        context.resume().catch(function() {
            // Ignore resume failures (usually permission/autoplay edge cases).
        });
    }

    const now = context.currentTime;
    let firstFreq = 680;
    let secondFreq = 920;
    let wave = 'triangle';

    if (kind === 'review') {
        firstFreq = 520;
        secondFreq = 760;
        wave = 'square';
    } else if (kind === 'back') {
        firstFreq = 620;
        secondFreq = 360;
        wave = 'sawtooth';
    }

    const oscillator = context.createOscillator();
    const gain = context.createGain();

    oscillator.type = wave;
    oscillator.frequency.setValueAtTime(firstFreq, now);
    oscillator.frequency.linearRampToValueAtTime(secondFreq, now + 0.08);

    var baseGain = document.body.classList.contains('party-mode') ? 0.15 : 0.07;
    gain.gain.setValueAtTime(0.0001, now);
    gain.gain.linearRampToValueAtTime(baseGain, now + 0.015);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.13);

    oscillator.connect(gain);
    gain.connect(context.destination);
    oscillator.start(now);
    oscillator.stop(now + 0.14);
}

function shouldPlayUiSoundForClick(evt) {
    if (!evt) return false;
    if (evt.isTrusted === false) return false;
    if (typeof evt.button === 'number' && evt.button !== 0) return false;
    if (evt.metaKey || evt.ctrlKey || evt.shiftKey || evt.altKey) return false;
    return true;
}

function playReviewActionSfx(kind) {
    if (kind !== 'review' && kind !== 'back') {
        kind = 'next';
    }
    scheduleUiTone(kind);
}

function navigateWithUiTransition(href) {
    if (!href) return;
    const target = new URL(href, window.location.origin);
    const targetPath = target.pathname + target.search + target.hash;
    const currentPath = window.location.pathname + window.location.search + window.location.hash;
    if (targetPath === currentPath) return;

    if (window.htmx && typeof window.htmx.ajax === 'function') {
        const src = document.createElement('a');
        src.setAttribute('hx-push-url', 'true');
        window.htmx.ajax('GET', targetPath, { source: src, target: 'body', swap: 'innerHTML' });
    } else {
        window.location.assign(target.toString());
    }
}

window.playReviewActionSfx = playReviewActionSfx;
window.navigateWithUiTransition = navigateWithUiTransition;

function handleUiNavigationClick(evt) {
    if (!shouldPlayUiSoundForClick(evt)) return;

    const reviewBtn = evt.target.closest('.review-btn');
    if (reviewBtn) {
        if (reviewBtn.disabled) return;
        playReviewActionSfx('review');
        return;
    }

    const nextAction = evt.target.closest('.next-vol-link');
    if (nextAction) {
        playReviewActionSfx('next');
        return;
    }

    const backAction = evt.target.closest('.done-btn, .back-shelf-link');
    if (backAction) {
        playReviewActionSfx('back');
    }
}

if (!window.__overdueUiNavigationClickBound) {
    document.addEventListener('click', handleUiNavigationClick, true);
    window.__overdueUiNavigationClickBound = true;
}

/* ============================================================
   GAME EVENT HANDLER
   ============================================================ */

function handleGameEventToast(evt) {
    const data = evt.detail;
    if (!data) return;

    // Trigger celebration effect
    showReviewCelebration();

    const xpBreakdown = Array.isArray(data.xp_breakdown) ? data.xp_breakdown : [];
    let totalXpFromBreakdown = 0;

    xpBreakdown.forEach(function(entry) {
        if (!entry) return;
        const amount = Number(entry.amount || 0);
        if (amount <= 0) return;
        totalXpFromBreakdown += amount;
    });

    const xpToShow = totalXpFromBreakdown > 0 ? totalXpFromBreakdown : Number(data.xp_awarded || 0);
    if (xpToShow > 0) {
        queueToast(xpToShow + ' pages (+' + xpToShow + ' XP)', 'xp', 'star');
    }

    const bonusLabels = [];
    xpBreakdown.forEach(function(entry) {
        if (!entry || typeof entry.reason !== 'string') return;
        if (entry.reason.indexOf('overdue') >= 0) bonusLabels.push('overdue x2');
        if (entry.reason.indexOf('streak bonus') >= 0) bonusLabels.push('streak');
    });
    if (bonusLabels.length > 0) {
        const uniqueBonusLabels = bonusLabels.filter(function(label, index) {
            return bonusLabels.indexOf(label) === index;
        });
        queueToast('Bonus: ' + uniqueBonusLabels.join(' + '), 'streak', 'fire');
    }

    if (data.badges_earned && data.badges_earned.length > 0) {
        data.badges_earned.forEach(function(badge) {
            queueToast(badge + ' earned!', 'badge', 'award');
        });
    }

    if (data.rank_changed && data.new_rank) {
        queueToast('Ranked up to ' + data.new_rank + '!', 'rank', 'crown');
    }
}

if (!window.__overdueGameEventToastBound) {
    document.body.addEventListener('gameEvent', handleGameEventToast);
    window.__overdueGameEventToastBound = true;
}

/* ============================================================
   PARTY MODE (Easter Egg -- click "OVERDUE" 5 times)
   ============================================================ */

(function() {
    if (window.__overduePartyModeInit) return;
    window.__overduePartyModeInit = true;

    const PARTY_MODE_STORAGE_KEY = 'overdue:party-mode';
    const PARTY_AUDIO_TIME_STORAGE_KEY = 'overdue:party-audio-time';
    const CLICKS_NEEDED = 5;
    const CLICK_WINDOW_MS = 3000;
    const SINGLE_CLICK_NAV_DELAY_MS = 500;
    let clicks = [];
    let singleClickTimer = null;
    let resumeOnInteraction = null;
    const audio = getOrCreatePartyAudio();
    restorePersistedPartyMode();

    document.addEventListener('click', function(e) {
        const logo = e.target.closest('#overdue-logo');
        if (!logo) return;
        if ((typeof e.button === 'number' && e.button !== 0) || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) {
            return;
        }

        const logoHref = logo.getAttribute('href') || '/';
        const now = Date.now();
        clicks.push(now);
        clicks = clicks.filter(function(t) { return now - t < CLICK_WINDOW_MS; });

        // Suppress immediate navigation so rapid click sequences can complete.
        e.preventDefault();
        e.stopPropagation();

        if (singleClickTimer) {
            clearTimeout(singleClickTimer);
            singleClickTimer = null;
        }

        // Preserve normal logo navigation for single clicks.
        if (clicks.length === 1 && !isHrefCurrentLocation(logoHref)) {
            singleClickTimer = window.setTimeout(function() {
                singleClickTimer = null;
                clicks = [];
                navigateToLogoHref(logoHref);
            }, SINGLE_CLICK_NAV_DELAY_MS);
        }

        // Visual pulse on each click in the sequence
        if (clicks.length >= 1) {
            logo.style.transform = 'scale(1.25)';
            logo.style.transition = 'transform 0.15s ease';
            setTimeout(function() {
                logo.style.transform = 'scale(1)';
            }, 150);
        }

        if (clicks.length >= CLICKS_NEEDED) {
            clicks = [];
            if (singleClickTimer) {
                clearTimeout(singleClickTimer);
                singleClickTimer = null;
            }
            togglePartyMode();
        }
    }, false);

    function navigateToLogoHref(href) {
        const target = new URL(href, window.location.origin);
        const targetPath = target.pathname + target.search + target.hash;
        const currentPath = window.location.pathname + window.location.search + window.location.hash;
        if (targetPath === currentPath) return;
        window.location.assign(target.toString());
    }

    function isHrefCurrentLocation(href) {
        const target = new URL(href, window.location.origin);
        const targetPath = target.pathname + target.search + target.hash;
        const currentPath = window.location.pathname + window.location.search + window.location.hash;
        return targetPath === currentPath;
    }

    function togglePartyMode() {
        const active = document.body.classList.toggle('party-mode');
        persistPartyMode(active);
        if (active) {
            tryStartPartyAudio(true);
            queueToast('Party Mode Activated', 'party', 'star');
        } else {
            stopPartyAudio();
            queueToast('Party Completed', 'party', 'award');
        }
    }

    window.__overdueTogglePartyMode = togglePartyMode;

    function getOrCreatePartyAudio() {
        if (window.__overduePartyAudio) return window.__overduePartyAudio;
        const persistentAudio = new Audio('/static/audio/party.mp3');
        persistentAudio.loop = true;
        persistentAudio.preload = 'auto';
        if (typeof persistentAudio.load === 'function') {
            try {
                persistentAudio.load();
            } catch (_err) {
                // Ignore media preload failures.
            }
        }
        window.__overduePartyAudio = persistentAudio;
        return persistentAudio;
    }

    function persistPartyAudioPosition() {
        if (!audio || !readPersistedPartyMode()) return;
        if (!Number.isFinite(audio.currentTime) || audio.currentTime <= 0) return;
        try {
            sessionStorage.setItem(PARTY_AUDIO_TIME_STORAGE_KEY, String(audio.currentTime));
        } catch (_err) {
            // Ignore storage availability issues.
        }
    }

    function clearPersistedPartyAudioPosition() {
        try {
            sessionStorage.removeItem(PARTY_AUDIO_TIME_STORAGE_KEY);
        } catch (_err) {
            // Ignore storage availability issues.
        }
    }

    function restorePersistedPartyAudioPosition() {
        if (!audio) return;
        let savedSeconds = null;
        try {
            savedSeconds = Number(sessionStorage.getItem(PARTY_AUDIO_TIME_STORAGE_KEY));
        } catch (_err) {
            savedSeconds = null;
        }
        if (!Number.isFinite(savedSeconds) || savedSeconds <= 0) return;

        const applySavedTime = function() {
            try {
                if (Number.isFinite(audio.duration) && savedSeconds >= audio.duration) return;
                audio.currentTime = savedSeconds;
            } catch (_err) {
                // Some browsers can throw if metadata is not ready yet.
            }
        };

        if (audio.readyState >= 1) {
            applySavedTime();
        } else {
            const onLoadedMetadata = function() {
                audio.removeEventListener('loadedmetadata', onLoadedMetadata);
                applySavedTime();
            };
            audio.addEventListener('loadedmetadata', onLoadedMetadata);
        }
    }

    function tryStartPartyAudio(restart) {
        if (!audio) return;
        if (restart) {
            audio.currentTime = 0;
            clearPersistedPartyAudioPosition();
        } else {
            restorePersistedPartyAudioPosition();
        }
        const playPromise = audio.play();
        if (playPromise && typeof playPromise.catch === 'function') {
            playPromise.catch(function() {
                attachResumeOnInteraction();
            });
        }
    }

    function stopPartyAudio() {
        if (!audio) return;
        persistPartyAudioPosition();
        audio.pause();
        audio.currentTime = 0;
        clearPersistedPartyAudioPosition();
        detachResumeOnInteraction();
    }

    function attachResumeOnInteraction() {
        if (resumeOnInteraction) return;
        resumeOnInteraction = function() {
            detachResumeOnInteraction();
            if (readPersistedPartyMode()) tryStartPartyAudio(false);
        };
        document.addEventListener('pointerdown', resumeOnInteraction, true);
        document.addEventListener('keydown', resumeOnInteraction, true);
    }

    function detachResumeOnInteraction() {
        if (!resumeOnInteraction) return;
        document.removeEventListener('pointerdown', resumeOnInteraction, true);
        document.removeEventListener('keydown', resumeOnInteraction, true);
        resumeOnInteraction = null;
    }

    function persistPartyMode(active) {
        try {
            if (active) {
                localStorage.setItem(PARTY_MODE_STORAGE_KEY, '1');
            } else {
                localStorage.removeItem(PARTY_MODE_STORAGE_KEY);
            }
        } catch (_err) {
            // Ignore storage availability issues.
        }
    }

    function readPersistedPartyMode() {
        try {
            return localStorage.getItem(PARTY_MODE_STORAGE_KEY) === '1';
        } catch (_err) {
            return false;
        }
    }

    function restorePersistedPartyMode() {
        if (!readPersistedPartyMode()) return;
        document.body.classList.add('party-mode');
        tryStartPartyAudio(false);
    }

    function handlePartyModeAfterSwap() {
        if (!readPersistedPartyMode()) return;
        document.body.classList.add('party-mode');
        if (audio && audio.paused) {
            tryStartPartyAudio(false);
        }
    }

    if (!window.__overduePartyModeAfterSwapBound) {
        document.addEventListener('htmx:afterSwap', handlePartyModeAfterSwap);
        window.__overduePartyModeAfterSwapBound = true;
    }

    window.addEventListener('pagehide', function() {
        if (readPersistedPartyMode()) persistPartyAudioPosition();
    });
})();

/* ============================================================
   HTMX PRE-REQUEST HANDLER
   ============================================================ */

function handleHtmxBeforeRequest(evt) {
    const target = evt.detail.target;
    if (target && target.id === 'review-section') {
        // Capture old gauge score for animation
        const gaugeEl = document.querySelector('#dewey-gauge-container .dewey-gauge');
        const container = document.getElementById('dewey-gauge-container');
        if (gaugeEl && container) {
            container.dataset.previousScore = gaugeEl.dataset.score || '0';
        }
        // Capture rect for particles
        window.__reviewSectionRect = target.getBoundingClientRect();
    }
}

if (!window.__overdueHtmxBeforeRequestBound) {
    document.body.addEventListener('htmx:beforeRequest', handleHtmxBeforeRequest);
    window.__overdueHtmxBeforeRequestBound = true;
}

/* ============================================================
   TIERED LOADING INDICATOR
   Tier 1 (0-300ms): nothing -- page-flip transition is enough.
   Tier 2 (300ms+):  thin pixel progress bar at top of viewport.
   Tier 3 (2s+):     full "Consulting the shelves..." overlay.
   ============================================================ */

(function() {
    if (window.__overdueTieredLoadingInit) return;
    window.__overdueTieredLoadingInit = true;

    var TIER2_DELAY = 300;
    var TIER3_DELAY = 2000;
    var COMPLETION_FADE = 300;

    var tier2Timer = null;
    var tier3Timer = null;
    var progressTimer = null;
    var progressStart = 0;

    var progressEl = document.getElementById('nav-progress');
    var progressBar = progressEl ? progressEl.querySelector('.nav-progress-bar') : null;
    var overlayEl = document.getElementById('loading-overlay');

    function isBoostNavigation(evt) {
        if (!evt || !evt.detail) return false;
        var verb = evt.detail.verb;
        if (verb && verb.toUpperCase() !== 'GET') return false;
        var elt = evt.detail.elt;
        if (!elt) return false;
        // Exclude polling requests (hx-trigger="every ...")
        var trigger = elt.getAttribute && elt.getAttribute('hx-trigger');
        if (trigger && trigger.indexOf('every') >= 0) return false;
        // Exclude targeted partial swaps (review section, etc.)
        var target = evt.detail.target;
        if (target && target.id && target.id !== 'main' && target.tagName !== 'BODY') {
            // Allow only full-page boost navigations
            var hxBoost = elt.closest && elt.closest('[hx-boost="true"]');
            if (!hxBoost) return false;
        }
        return true;
    }

    function updateProgressBar() {
        if (!progressBar) return;
        var elapsed = Date.now() - progressStart;
        // Logarithmic curve: fast start, asymptotically approaches 85%
        var pct = 85 * (1 - Math.exp(-elapsed / 2000));
        progressBar.style.width = pct + '%';
        progressTimer = requestAnimationFrame(updateProgressBar);
    }

    function showTier2() {
        if (!progressEl || !progressBar) return;
        progressStart = Date.now();
        progressBar.style.width = '0%';
        progressBar.style.transition = 'none';
        progressEl.classList.add('active');
        progressEl.classList.remove('complete');
        progressTimer = requestAnimationFrame(updateProgressBar);
    }

    function showTier3() {
        if (!overlayEl) return;
        overlayEl.classList.remove('loading-overlay-hidden');
        overlayEl.classList.add('loading-overlay-visible');
    }

    function hideAll() {
        // Clear pending timers
        if (tier2Timer) { clearTimeout(tier2Timer); tier2Timer = null; }
        if (tier3Timer) { clearTimeout(tier3Timer); tier3Timer = null; }
        if (progressTimer) { cancelAnimationFrame(progressTimer); progressTimer = null; }

        // Complete progress bar animation
        if (progressEl && progressEl.classList.contains('active')) {
            if (progressBar) {
                progressBar.style.transition = 'width 0.15s ease-out';
                progressBar.style.width = '100%';
            }
            progressEl.classList.add('complete');
            setTimeout(function() {
                progressEl.classList.remove('active', 'complete');
                if (progressBar) {
                    progressBar.style.transition = 'none';
                    progressBar.style.width = '0%';
                }
            }, COMPLETION_FADE);
        }

        // Hide overlay
        if (overlayEl) {
            overlayEl.classList.remove('loading-overlay-visible');
            overlayEl.classList.add('loading-overlay-hidden');
        }
    }

    document.body.addEventListener('htmx:beforeRequest', function(evt) {
        if (!isBoostNavigation(evt)) return;
        // Start timer chain
        tier2Timer = setTimeout(showTier2, TIER2_DELAY);
        tier3Timer = setTimeout(showTier3, TIER3_DELAY);
    });

    document.body.addEventListener('htmx:afterRequest', function(evt) {
        if (!isBoostNavigation(evt)) return;
        hideAll();
    });

    document.body.addEventListener('htmx:responseError', function() {
        hideAll();
    });

    document.body.addEventListener('htmx:sendError', function() {
        hideAll();
    });
})();

/* ============================================================
   REFERENCE DESK MODAL (Easter Egg -- press ? anywhere)
   ============================================================ */

(function() {
    if (window.__overdueReferenceDeskInit) return;
    window.__overdueReferenceDeskInit = true;

    var backdropEl = null;
    var isOpen = false;

    function createModal() {
        var backdrop = document.createElement('div');
        backdrop.className = 'reference-desk-backdrop loading-overlay-hidden';
        backdrop.style.display = 'none';
        backdrop.style.alignItems = 'center';
        backdrop.style.justifyContent = 'center';

        var card = document.createElement('div');
        card.className = 'pixel-card text-center py-8 px-6';
        card.style.maxWidth = '420px';
        card.style.width = '90vw';
        card.style.position = 'relative';
        card.style.zIndex = '251';

        var icon = document.createElement('img');
        icon.src = '/static/icons/search.svg';
        icon.alt = '';
        icon.width = 28;
        icon.height = 28;
        icon.className = 'pixel-icon';
        icon.style.display = 'inline-block';
        icon.style.marginBottom = '0.75rem';

        var heading = document.createElement('h2');
        heading.className = 'pixel-heading mb-4';
        heading.textContent = 'THE REFERENCE DESK';

        var desc = document.createElement('p');
        desc.className = 'text-parchment-dark text-lg mb-6';
        var descText1 = document.createTextNode('Got a question? Our archivist, ');
        var dosuSpan = document.createElement('span');
        dosuSpan.className = 'text-gold';
        dosuSpan.textContent = 'Dosu';
        var descText2 = document.createTextNode(', is here to help.');
        desc.appendChild(descText1);
        desc.appendChild(dosuSpan);
        desc.appendChild(descText2);

        var btn = document.createElement('a');
        btn.href = 'https://app.dosu.dev/04283041-db40-47f2-9553-9b7452d3ac02/ask';
        btn.target = '_blank';
        btn.rel = 'noopener noreferrer';
        btn.className = 'pixel-btn pixel-btn-gold';
        btn.textContent = 'Ask Dosu';
        btn.style.display = 'inline-block';

        var hint = document.createElement('p');
        hint.className = 'pixel-label text-ink-light mt-4';
        hint.textContent = 'Press ? to close';

        card.appendChild(icon);
        card.appendChild(heading);
        card.appendChild(desc);
        card.appendChild(btn);
        card.appendChild(hint);
        backdrop.appendChild(card);
        document.body.appendChild(backdrop);

        backdrop.addEventListener('click', function(e) {
            if (e.target === backdrop) closeModal();
        });

        return backdrop;
    }

    function openModal() {
        if (!backdropEl) backdropEl = createModal();
        backdropEl.style.display = 'flex';
        backdropEl.classList.remove('loading-overlay-hidden');
        backdropEl.classList.add('loading-overlay-visible');
        isOpen = true;
    }

    function closeModal() {
        if (!backdropEl) return;
        backdropEl.classList.remove('loading-overlay-visible');
        backdropEl.classList.add('loading-overlay-hidden');
        backdropEl.style.display = 'none';
        isOpen = false;
    }

    document.addEventListener('keydown', function(e) {
        var tag = (e.target.tagName || '').toLowerCase();
        if (tag === 'input' || tag === 'textarea' || tag === 'select') return;

        if (e.key === '?') {
            e.preventDefault();
            if (isOpen) {
                closeModal();
            } else {
                openModal();
            }
            return;
        }

        if (e.key === 'Escape' && isOpen) {
            e.stopPropagation();
            e.preventDefault();
            closeModal();
        }
    });

    // Clean up DOM reference on full-page body swap
    document.addEventListener('htmx:beforeSwap', function(evt) {
        if (evt.detail && evt.detail.target === document.body) {
            backdropEl = null;
            isOpen = false;
        }
    });
})();

/* ============================================================
   PARTY TOGGLE (Footer easter egg)
   ============================================================ */

(function() {
    if (window.__overduePartyToggleInit) return;
    window.__overduePartyToggleInit = true;

    function handlePartyToggle(e) {
        if (!e.target.closest('#party-toggle')) return;
        e.preventDefault();
        if (typeof window.__overdueTogglePartyMode === 'function') {
            window.__overdueTogglePartyMode();
        }
    }

    document.addEventListener('click', handlePartyToggle);
    document.addEventListener('keydown', function(e) {
        if (e.key !== 'Enter' && e.key !== ' ') return;
        handlePartyToggle(e);
    });
})();
