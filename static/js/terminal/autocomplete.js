import { ALLOWED_COMMANDS } from './commands.js';

export class TerminalAutocomplete {
    /**
     * Autocomplete input based on allowed commands whitelist.
     * @param {string} currentInput 
     * @returns {{ match: string|null, suggestions: string[] }}
     */
    static complete(currentInput) {
        const trimmed = currentInput.trim().toLowerCase();
        if (!trimmed) {
            return { match: null, suggestions: [...ALLOWED_COMMANDS] };
        }

        const matches = ALLOWED_COMMANDS.filter(cmd => cmd.startsWith(trimmed));

        if (matches.length === 1) {
            return { match: matches[0], suggestions: [] };
        }

        return {
            match: null,
            suggestions: matches
        };
    }
}
