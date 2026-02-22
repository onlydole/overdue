/**
 * Overdue -- Application JavaScript
 * Toast system, HTMX event listeners, gauge re-initialization.
 */

/* ============================================================
   TOAST SYSTEM (with stagger queue)
   ============================================================ */

var toastQueue = [];
var toastProcessing = false;

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
    var item = toastQueue.shift();
    showToast(item.text, item.type, item.iconId);
    setTimeout(processToastQueue, 400);
}

/**
 * Read pre-rendered pixel art icon SVG from hidden <template> elements.
 * Returns a cloned DOM node (not a string), safe from XSS since the content
 * originates from server-rendered templates, never from user input.
 */
function _iconNode(id) {
    var tpl = document.getElementById('icon-' + id);
    if (!tpl) return null;
    return tpl.content.cloneNode(true);
}

function showToast(text, type, iconId) {
    var container = document.getElementById('toast-container');
    if (!container) return;

    var toast = document.createElement('div');
    toast.className = 'pixel-card text-center py-3 px-5 min-w-[220px]';
    toast.style.pointerEvents = 'auto';
    toast.style.borderColor = type === 'badge' ? '#b76ef0' : type === 'rank' ? '#f0c543' : '#5cdb5c';
    toast.style.animation = 'toast-slide-in 0.3s ease-out';

    var span = document.createElement('span');
    span.className = 'font-pixel text-[10px]';
    if (type === 'xp') {
        span.className += ' text-dewey-pristine';
    } else if (type === 'streak') {
        span.className += ' text-streak';
    } else if (type === 'badge') {
        span.className += ' text-badge-common';
    } else if (type === 'rank') {
        span.className += ' gold-shimmer';
    }

    /* Prepend pixel art icon if available, then add text safely */
    var icon = iconId ? _iconNode(iconId) : null;
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
    var rect = window.__reviewSectionRect;
    if (!rect) {
        var target = document.getElementById('review-section');
        if (!target) return;
        rect = target.getBoundingClientRect();
    }
    delete window.__reviewSectionRect;
    var cx = rect.left + rect.width / 2;
    var cy = rect.top + rect.height / 2;
    var colors = ['#f0c543', '#5cdb5c', '#b76ef0', '#e8563e', '#7eb5e3', '#ffe9a0', '#a0d468', '#f6bb42'];

    for (var i = 0; i < 8; i++) {
        var particle = document.createElement('div');
        var angle = (i / 8) * 2 * Math.PI;
        var dx = Math.cos(angle) * 80;
        var dy = Math.sin(angle) * 80;
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
   GAME EVENT HANDLER
   ============================================================ */

document.body.addEventListener('gameEvent', function(evt) {
    var data = evt.detail;
    if (!data) return;

    // Trigger celebration effect
    showReviewCelebration();

    if (data.xp_awarded > 0) {
        queueToast('+' + data.xp_awarded + ' XP', 'xp', 'star');
    }

    if (data.streak_bonus_awarded) {
        queueToast('Streak Bonus!', 'streak', 'fire');
    }

    if (data.badges_earned && data.badges_earned.length > 0) {
        data.badges_earned.forEach(function(badge) {
            queueToast(badge + ' earned!', 'badge', 'trophy');
        });
    }

    if (data.rank_changed && data.new_rank) {
        queueToast('Ranked up to ' + data.new_rank + '!', 'rank', 'crown');
    }
});

/* ============================================================
   HTMX PRE-REQUEST HANDLER
   ============================================================ */

document.body.addEventListener('htmx:beforeRequest', function(evt) {
    var target = evt.detail.target;
    if (target && target.id === 'review-section') {
        // Capture old gauge score for animation
        var gaugeEl = document.querySelector('#dewey-gauge-container .dewey-gauge');
        var container = document.getElementById('dewey-gauge-container');
        if (gaugeEl && container) {
            container.dataset.previousScore = gaugeEl.dataset.score || '0';
        }
        // Capture rect for particles
        window.__reviewSectionRect = target.getBoundingClientRect();
    }
});
