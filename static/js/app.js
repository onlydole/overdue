/**
 * Overdue -- Application JavaScript
 * Toast system, HTMX event listeners, gauge re-initialization.
 */

/* ============================================================
   TOAST SYSTEM (with stagger queue)
   ============================================================ */

var toastQueue = [];
var toastProcessing = false;

function queueToast(text, type) {
    toastQueue.push({ text: text, type: type });
    if (!toastProcessing) processToastQueue();
}

function processToastQueue() {
    if (toastQueue.length === 0) {
        toastProcessing = false;
        return;
    }
    toastProcessing = true;
    var item = toastQueue.shift();
    showToast(item.text, item.type);
    setTimeout(processToastQueue, 400);
}

function showToast(text, type) {
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
    span.textContent = text;
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

    // Gold screen flash overlay
    var flash = document.createElement('div');
    flash.className = 'review-flash-overlay';
    flash.style.cssText = 'position:fixed;inset:0;background:rgba(240,197,67,0.25);pointer-events:none;z-index:9999;animation:review-flash 0.4s ease-out forwards;';
    document.body.appendChild(flash);
    setTimeout(function() { if (flash.parentNode) flash.parentNode.removeChild(flash); }, 500);

    // Pixel particle burst from review section
    var target = document.getElementById('review-section');
    if (!target) return;
    var rect = target.getBoundingClientRect();
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
        queueToast('\u2605 +' + data.xp_awarded + ' XP', 'xp');
    }

    if (data.streak_bonus_awarded) {
        queueToast('\uD83D\uDD25 Streak Bonus!', 'streak');
    }

    if (data.badges_earned && data.badges_earned.length > 0) {
        data.badges_earned.forEach(function(badge) {
            queueToast('\uD83C\uDFC6 ' + badge + ' earned!', 'badge');
        });
    }

    if (data.rank_changed && data.new_rank) {
        queueToast('\uD83D\uDC51 Ranked up to ' + data.new_rank + '!', 'rank');
    }
});

/* ============================================================
   GAUGE RE-INITIALIZATION
   ============================================================ */

function initGauges() {
    var gauges = document.querySelectorAll('.dewey-gauge');
    gauges.forEach(function(gauge) {
        // Skip already-rendered gauges
        if (gauge.dataset.rendered) return;

        var score = parseFloat(gauge.dataset.score) || 0;
        var color, label;
        if (score >= 75) { color = '#5cdb5c'; label = 'PRISTINE'; }
        else if (score >= 50) { color = '#a0d468'; label = 'GOOD'; }
        else if (score >= 25) { color = '#f6bb42'; label = 'DUSTY'; }
        else { color = '#e8563e'; label = 'OVERDUE'; }

        var pct = Math.min(score / 100, 1);

        if (gauge.classList.contains('dewey-gauge-bar')) {
            var segments = 10;
            var filledSegments = Math.round(pct * segments);
            while (gauge.firstChild) { gauge.removeChild(gauge.firstChild); }
            var bar = document.createElement('div');
            bar.className = 'flex gap-[2px] w-full h-full items-end p-1';
            for (var i = 0; i < segments; i++) {
                var seg = document.createElement('div');
                seg.className = 'flex-1';
                seg.style.height = (20 + (i * 8)) + '%';
                seg.style.background = i < filledSegments ? color : '#2e2e4a';
                bar.appendChild(seg);
            }
            gauge.appendChild(bar);
        } else {
            gauge.style.borderColor = color;
            gauge.style.background = 'conic-gradient(' + color + ' ' + (pct * 360) + 'deg, #2e2e4a ' + (pct * 360) + 'deg)';
            gauge.style.borderRadius = '50%';
            if (!gauge.children.length) {
                var inner = document.createElement('div');
                inner.className = 'flex flex-col items-center justify-center rounded-full';
                inner.style.background = '#232342';
                inner.style.width = '75%';
                inner.style.height = '75%';
                inner.style.position = 'absolute';
                var num = document.createElement('span');
                num.style.fontFamily = '"Press Start 2P", cursive';
                num.style.fontSize = '0.55rem';
                num.style.color = color;
                num.textContent = Math.round(score);
                inner.appendChild(num);
                var lbl = document.createElement('span');
                lbl.style.fontFamily = '"VT323", monospace';
                lbl.style.fontSize = '0.6rem';
                lbl.style.color = '#8b8b9e';
                lbl.style.marginTop = '2px';
                lbl.textContent = label;
                inner.appendChild(lbl);
                gauge.appendChild(inner);
            }
        }
        gauge.dataset.rendered = 'true';
    });
}

// Re-init gauges after HTMX swaps
document.body.addEventListener('htmx:afterSwap', function() {
    initGauges();
});

// Debounced resize handler for gauge re-render
var resizeTimer;
window.addEventListener('resize', function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function() {
        // Reset rendered state and re-init
        document.querySelectorAll('.dewey-gauge').forEach(function(g) {
            delete g.dataset.rendered;
            while (g.firstChild) g.removeChild(g.firstChild);
        });
        initGauges();
    }, 250);
});
