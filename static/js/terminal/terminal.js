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
        this.historyIndex = 0;
        this.tempInput = ''; // Store current input before navigating history

        this._bindEvents();
        this._initBanner();
    }

    _initBanner() {
        this.renderer.renderOutput(
            "ALI.DEV Interactive Terminal [Version 1.0.0]\nType 'help' to see available commands.\n"
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
                this._navigateHistoryUp();
            } else if (e.key === 'ArrowDown') {
                e.preventDefault();
                this._navigateHistoryDown();
            }
        });

        this.container.addEventListener('click', () => {
            this.input.focus();
        });
    }

    _handleEnter() {
        const rawValue = this.input.value;
        this.input.value = '';
        this.tempInput = '';

        if (!rawValue.trim()) return;

        // Store non-duplicate command in history
        if (this.history.length === 0 || this.history[this.history.length - 1] !== rawValue) {
            this.history.push(rawValue);
        }
        this.historyIndex = this.history.length;

        this.renderer.renderCommandLine(rawValue);
        const result = this.registry.execute(rawValue);

        if (result.action === 'clear') {
            this.renderer.clear();
        } else {
            if (result.output) {
                this.renderer.renderOutput(result.output, result.isError);
            }
            if (result.action === 'open_url' && result.url) {
                window.open(result.url, '_blank', 'noopener,noreferrer');
            }
        }

        this.renderer.scrollToBottom();
    }

    _navigateHistoryUp() {
        if (this.history.length === 0) return;

        if (this.historyIndex === this.history.length) {
            this.tempInput = this.input.value;
        }

        if (this.historyIndex > 0) {
            this.historyIndex--;
            this.input.value = this.history[this.historyIndex];
            this._setCursorToEnd();
        }
    }

    _navigateHistoryDown() {
        if (this.historyIndex < this.history.length) {
            this.historyIndex++;
            if (this.historyIndex === this.history.length) {
                this.input.value = this.tempInput;
            } else {
                this.input.value = this.history[this.historyIndex];
            }
            this._setCursorToEnd();
        }
    }

    _setCursorToEnd() {
        const len = this.input.value.length;
        this.input.setSelectionRange(len, len);
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
}
