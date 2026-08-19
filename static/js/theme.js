/**
 * Unified Theme Manager
 * Supports UI toggle and Terminal command synchronization with localStorage persistence.
 */

export const THEME_KEY = 'portfolio_theme';
export const THEMES = Object.freeze({
    LIGHT: 'light',
    DARK: 'dark'
});

export class ThemeManager {
    static getSystemPreference() {
        return window.matchMedia('(prefers-color-scheme: dark)').matches
            ? THEMES.DARK
            : THEMES.LIGHT;
    }

    static getCurrentTheme() {
        const stored = localStorage.getItem(THEME_KEY);
        if (stored === THEMES.LIGHT || stored === THEMES.DARK) {
            return stored;
        }
        const docTheme = document.documentElement.getAttribute('data-theme');
        if (docTheme === THEMES.LIGHT || docTheme === THEMES.DARK) {
            return docTheme;
        }
        return this.getSystemPreference();
    }

    /**
     * Apply target theme and dispatch custom themechange event for cross-component sync.
     * @param {'light' | 'dark'} theme 
     */
    static setTheme(theme) {
        const targetTheme = (theme === THEMES.DARK) ? THEMES.DARK : THEMES.LIGHT;
        document.documentElement.setAttribute('data-theme', targetTheme);

        if (targetTheme === THEMES.DARK) {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }

        try {
            localStorage.setItem(THEME_KEY, targetTheme);
        } catch (e) {}

        // Update ARIA label and icon on header button
        const toggleBtn = document.getElementById('theme-toggle');
        if (toggleBtn) {
            const nextTheme = targetTheme === THEMES.LIGHT ? THEMES.DARK : THEMES.LIGHT;
            toggleBtn.setAttribute('aria-label', `Switch to ${nextTheme} theme`);
            const label = toggleBtn.querySelector('.theme-toggle__label');
            if (label) {
                label.textContent = targetTheme === THEMES.DARK ? 'Dark' : 'Light';
            }
            const icon = toggleBtn.querySelector('i');
            if (icon) {
                if (targetTheme === THEMES.DARK) {
                    icon.className = 'fa-solid fa-moon text-sm text-indigo-400';
                } else {
                    icon.className = 'fa-solid fa-sun text-sm text-amber-500';
                }
            }
        }

        // Dispatch global theme change event
        window.dispatchEvent(new CustomEvent('themechange', { detail: { theme: targetTheme } }));
        return targetTheme;
    }

    /**
     * Switch between light and dark themes.
     */
    static toggleTheme() {
        const current = this.getCurrentTheme();
        const next = current === THEMES.DARK ? THEMES.LIGHT : THEMES.DARK;
        return this.setTheme(next);
    }

    /**
     * Initialize theme settings on page load.
     */
    static init() {
        const initial = this.getCurrentTheme();
        this.setTheme(initial);

        const toggleBtn = document.getElementById('theme-toggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleTheme();
            });
        }

        // Listen for OS system theme changes if not manually overridden
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem(THEME_KEY)) {
                this.setTheme(e.matches ? THEMES.DARK : THEMES.LIGHT);
            }
        });
    }
}
