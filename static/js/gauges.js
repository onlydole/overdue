/**
 * Dewey Score gauge rendering -- pixel art style.
 * Draws segmented progress bars and circular gauges for Dewey Scores.
 * Supports animated transitions on OOB re-renders after reviews.
 */

/* ============================================================
   SCORE -> COLOR / LABEL HELPERS
   ============================================================ */

function _gaugeColor(score) {
    if (score >= 75) return '#5cdb5c';
    if (score >= 50) return '#a0d468';
    if (score >= 25) return '#f6bb42';
    return '#e8563e';
}

function _gaugeLabel(score) {
    if (score >= 75) return 'PRISTINE';
    if (score >= 50) return 'GOOD';
    if (score >= 25) return 'DUSTY';
    return 'OVERDUE';
}

/* ============================================================
   RENDER A GAUGE AT A SPECIFIC SCORE
   ============================================================ */

function renderGaugeAtScore(gauge, score) {
    var color = _gaugeColor(score);
    var label = _gaugeLabel(score);
    var pct = Math.min(score / 100, 1);

    // Segmented bar style
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
        // Circular gauge with conic gradient
        gauge.style.borderColor = color;
        gauge.style.background = 'conic-gradient(' + color + ' ' + (pct * 360) + 'deg, #2e2e4a ' + (pct * 360) + 'deg)';
        gauge.style.borderRadius = '50%';

        // Build or update inner label
        var inner = gauge.querySelector('.gauge-inner');
        if (!inner) {
            inner = document.createElement('div');
            inner.className = 'gauge-inner flex flex-col items-center justify-center rounded-full';
            inner.style.background = '#232342';
            inner.style.width = '75%';
            inner.style.height = '75%';
            inner.style.position = 'absolute';

            var num = document.createElement('span');
            num.className = 'gauge-num';
            num.style.fontFamily = '"Press Start 2P", cursive';
            num.style.fontSize = '0.55rem';
            num.style.color = color;
            num.textContent = Math.round(score);
            inner.appendChild(num);

            var lbl = document.createElement('span');
            lbl.className = 'gauge-label';
            lbl.style.fontFamily = '"VT323", monospace';
            lbl.style.fontSize = '0.6rem';
            lbl.style.color = '#8b8b9e';
            lbl.style.marginTop = '2px';
            lbl.textContent = label;
            inner.appendChild(lbl);

            gauge.appendChild(inner);
        } else {
            var numEl = inner.querySelector('.gauge-num');
            var lblEl = inner.querySelector('.gauge-label');
            if (numEl) {
                numEl.textContent = Math.round(score);
                numEl.style.color = color;
            }
            if (lblEl) {
                lblEl.textContent = label;
            }
        }
    }
}

/* ============================================================
   ANIMATED GAUGE TRANSITION
   ============================================================ */

function animateGauge(gauge, fromScore, toScore, duration) {
    // Respect prefers-reduced-motion
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        renderGaugeAtScore(gauge, toScore);
        return;
    }

    var start = null;

    function step(timestamp) {
        if (!start) start = timestamp;
        var elapsed = timestamp - start;
        var progress = Math.min(elapsed / duration, 1);

        // Ease-out cubic
        var eased = 1 - Math.pow(1 - progress, 3);
        var currentScore = fromScore + (toScore - fromScore) * eased;

        renderGaugeAtScore(gauge, currentScore);

        if (progress < 1) {
            requestAnimationFrame(step);
        }
    }

    requestAnimationFrame(step);
}

/* ============================================================
   INIT GAUGES (called on load and after HTMX swaps)
   ============================================================ */

function initGauges() {
    var gauges = document.querySelectorAll('.dewey-gauge');

    gauges.forEach(function(gauge) {
        // Skip already-rendered gauges unless forced
        if (gauge.dataset.rendered) return;

        var score = parseFloat(gauge.dataset.score) || 0;

        // Check if parent container has a previous score for animation
        var container = gauge.closest('#dewey-gauge-container');
        var previousScore = container ? container.dataset.previousScore : null;

        if (previousScore !== null && previousScore !== undefined) {
            var from = parseFloat(previousScore);
            delete container.dataset.previousScore;
            animateGauge(gauge, from, score, 600);
        } else {
            renderGaugeAtScore(gauge, score);
        }

        gauge.dataset.rendered = 'true';
    });
}

/* ============================================================
   EVENT LISTENERS
   ============================================================ */

// Initialize on page load
document.addEventListener('DOMContentLoaded', initGauges);

// Re-initialize after HTMX content swaps
document.body.addEventListener('htmx:afterSwap', initGauges);

// Debounced resize handler for gauge re-render
var resizeTimer;
window.addEventListener('resize', function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function() {
        document.querySelectorAll('.dewey-gauge').forEach(function(g) {
            delete g.dataset.rendered;
            while (g.firstChild) g.removeChild(g.firstChild);
        });
        initGauges();
    }, 250);
});
