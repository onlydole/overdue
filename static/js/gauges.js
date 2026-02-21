/**
 * Dewey Score gauge rendering.
 * Draws circular progress indicators for Dewey Scores.
 */
document.addEventListener('DOMContentLoaded', function() {
    const gauges = document.querySelectorAll('.dewey-gauge');

    gauges.forEach(function(gauge) {
        const score = parseFloat(gauge.dataset.score) || 0;
        const size = gauge.offsetWidth || 48;

        // Determine color based on score
        let color;
        if (score >= 75) color = '#2D5A3D';
        else if (score >= 50) color = '#D4A574';
        else if (score >= 25) color = '#C45D3E';
        else color = '#8B2500';

        // Set border color to reflect score
        const pct = score / 100;
        gauge.style.borderColor = color;
        gauge.style.borderWidth = '3px';
        gauge.style.background = `conic-gradient(${color} ${pct * 360}deg, #e5e7eb ${pct * 360}deg)`;
        gauge.style.borderRadius = '50%';

        // If no inner content, add score text
        if (!gauge.children.length) {
            const text = document.createElement('span');
            text.className = 'text-xs font-bold bg-white rounded-full w-3/4 h-3/4 flex items-center justify-center';
            text.style.color = color;
            text.textContent = Math.round(score);
            gauge.appendChild(text);
        }
    });
});
