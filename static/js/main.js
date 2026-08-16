document.addEventListener("DOMContentLoaded", () => {
    const themeToggleBtn = document.getElementById("theme-toggle");
    const rootHtml = document.documentElement;

    // بازیابی تم ذخیره‌شده یا ترجیح سیستم‌عامل
    const savedTheme = localStorage.getItem("theme");
    const systemPrefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const initialTheme = savedTheme || (systemPrefersDark ? "dark" : "light");

    const applyTheme = (theme) => {
        rootHtml.setAttribute("data-theme", theme);
        localStorage.setItem("theme", theme);

        if (themeToggleBtn) {
            const isDark = theme === "dark";
            themeToggleBtn.setAttribute(
                "aria-label",
                isDark ? "Switch to light theme" : "Switch to dark theme"
            );
        }
    };

    applyTheme(initialTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener("click", () => {
            const currentTheme = rootHtml.getAttribute("data-theme") || "light";
            const nextTheme = currentTheme === "light" ? "dark" : "light";
            applyTheme(nextTheme);
        });
    }
});
