/**
 * Dewey Score gauge rendering -- pixel art style.
 * Draws segmented progress bars for Dewey Scores.
 */

function initGauges() {
    var gauges = document.querySelectorAll('.dewey-gauge');

    gauges.forEach(function(gauge) {
        // Skip already-rendered gauges unless forced
        if (gauge.dataset.rendered) return;

        var score = parseFloat(gauge.dataset.score) || 0;

        // Determine color based on score thresholds
        var color, label;
        if (score >= 75) { color = '#5cdb5c'; label = 'PRISTINE'; }
        else if (score >= 50) { color = '#a0d468'; label = 'GOOD'; }
        else if (score >= 25) { color = '#f6bb42'; label = 'DUSTY'; }
        else { color = '#e8563e'; label = 'OVERDUE'; }

        var pct = Math.min(score / 100, 1);

        // Segmented bar style
        if (gauge.classList.contains('dewey-gauge-bar')) {
            var segments = 10;
            var filledSegments = Math.round(pct * segments);

            // Clear existing children
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

// Initialize on page load
document.addEventListener('DOMContentLoaded', initGauges);

// Re-initialize after HTMX content swaps
document.body.addEventListener('htmx:afterSwap', initGauges);
