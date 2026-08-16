import { CommandRegistry } from './commands.js';
import { TerminalRenderer } from './renderer.js';
import { TerminalAutocomplete } from './autocomplete.js';

export class InteractiveTerminal {
    constructor({ containerId, inputId, outputId, dataContext }) {
        this.container = document.getElementById(containerId);
        this.input = document.getElementById(inputId);
        this.output = document.getElementById(outputId);

        if (!this.container || !this.input || !this.output) return;

        this.renderer = new TerminalRenderer(this.output);
        this.registry = new CommandRegistry(dataContext);
        
        this.history = [];
        this.historyIndex = -1;

        this._bindEvents();
        this._initBanner();
    }

    _initBanner() {
        this.renderer.renderOutput(
            "ALI.DEV Interactive Terminal [Version 1.0.0]\nType 'help' to see list of available commands.\n"
        );
    }

    _bindEvents() {
        this.input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this._handleEnter();
            } else if (e.key === 'Tab') {
                e.preventDefault();
                this._handleTab();
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                this._navigateHistory(1);
            } else if (e.key === 'ArrowDown') {
                e.preventDefault();
                this._navigateHistory(-1);
            }
        });

        // Refocus on input when clicking anywhere on the terminal body
        this.container.addEventListener('click', () => {
            this.input.focus();
        });
    }

    _handleEnter() {
        const rawValue = this.input.value;
        this.input.value = '';

        if (!rawValue.trim()) return;

        this.history.push(rawValue);
        this.historyIndex = this.history.length;

        this.renderer.renderCommandLine(rawValue);

        const result = this.registry.execute(rawValue);

        if (result.action === 'clear') {
            this.renderer.clear();
        } else {
            if (result.output) {
                this.renderer.renderOutput(result.output, result.isError);
            }

            if (result.action === 'theme') {
                this._applyThemeAction(result.themeTarget);
            } else if (result.action === 'open_url' && result.url) {
                window.open(result.url, '_blank', 'noopener,noreferrer');
            }
        }

        this.renderer.scrollToBottom();
    }

    _handleTab() {
        const currentVal = this.input.value;
        const result = TerminalAutocomplete.complete(currentVal);

        if (result.match) {
            this.input.value = result.match + ' ';
        } else if (result.suggestions.length > 1) {
            this.renderer.renderCommandLine(currentVal);
            this.renderer.renderOutput(result.suggestions.join('  '));
            this.renderer.scrollToBottom();
        }
    }

    _navigateHistory(direction) {
        if (this.history.length === 0) return;

        this.historyIndex -= direction;
        if (this.historyIndex < 0) this.historyIndex = 0;
        if (this.historyIndex > this.history.length) this.historyIndex = this.history.length;

        if (this.historyIndex === this.history.length) {
            this.input.value = '';
        } else {
            this.input.value = this.history[this.historyIndex];
        }
    }

    _applyThemeAction(target) {
        const root = document.documentElement;
        let nextTheme = target;

        if (!['light', 'dark'].includes(target)) {
            const current = root.getAttribute('data-theme') || 'light';
            nextTheme = current === 'light' ? 'dark' : 'light';
        }

        root.setAttribute('data-theme', nextTheme);
        localStorage.setItem('theme', nextTheme);
    }
}
