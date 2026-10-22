import { copyFileSync } from 'node:fs';

for (const [source, target] of [
    ['node_modules/htmx.org/dist/htmx.min.js', 'static/js/htmx.min.js'],
    ['node_modules/alpinejs/dist/cdn.min.js', 'static/js/alpine.min.js'],
]) {
    copyFileSync(source, target);
    console.log(`Copied ${target}`);
}
