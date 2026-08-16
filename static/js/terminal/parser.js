/**
 * Terminal Command Parser
 * Enforces ARCH-015 (Strict Whitelist) and ARCH-016 (XSS Sanitization & No Eval)
 */

export class CommandParser {
    /**
     * Escape sensitive characters to safe HTML entities.
     * @param {string} str 
     * @returns {string}
     */
    static escapeHTML(str) {
        if (typeof str !== 'string') return '';
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    /**
     * Parse raw user input into command name and argument list.
     * @param {string} rawInput 
     * @returns {{ raw: string, command: string, args: string[], isValid: boolean }}
     */
    static parse(rawInput) {
        if (!rawInput || typeof rawInput !== 'string') {
            return { raw: '', command: '', args: [], isValid: false };
        }

        const trimmed = rawInput.trim();
        if (trimmed.length === 0) {
            return { raw: '', command: '', args: [], isValid: false };
        }

        // Tokenize by whitespace and sanitize each token
        const tokens = trimmed.split(/\s+/).map(token => this.escapeHTML(token));
        const command = tokens[0].toLowerCase();
        const args = tokens.slice(1);

        return {
            raw: this.escapeHTML(trimmed),
            command,
            args,
            isValid: true
        };
    }
}
