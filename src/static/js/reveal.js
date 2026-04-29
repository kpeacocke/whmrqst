(() => {
    const groups = document.querySelectorAll('.reveal-sequence');
    for (const group of groups) {
        const items = [...group.querySelectorAll('.reveal-item')]
            .sort((a, b) => Number(a.dataset.revealOrder || 0) - Number(b.dataset.revealOrder || 0));

        for (const item of items) {
            item.classList.remove('is-visible');
        }

        items.forEach((item, index) => {
            const delay = 120 + index * 140;
            globalThis.setTimeout(() => {
                item.classList.add('is-visible');
            }, delay);
        });
    }
})();
