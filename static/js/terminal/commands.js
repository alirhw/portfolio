import { CommandParser } from './parser.js';

export const ALLOWED_COMMANDS = Object.freeze([
    'help',
    'skills',
    'projects',
    'contact',
    'clear',
    'theme',
    'repo',
    'sudo'
]);

export class CommandRegistry {
    constructor(dataContext = {}) {
        this.data = dataContext;
        this.commands = new Map();
        this._registerBuiltins();
    }

    _registerBuiltins() {
        this.commands.set('help', () => ({
            output: [
                'Available commands:',
                '  help      - Show this list of available commands',
                '  skills    - List core technical stack & competencies',
                '  projects  - Display featured open-source & client projects',
                '  contact   - Show available communication channels',
                '  theme     - Switch between light and dark themes (usage: theme [light|dark])',
                '  repo      - Open repository for this portfolio',
                '  clear     - Clear the terminal screen',
                '  sudo      - Administrative privileges request'
            ].join('\n')
        }));

        this.commands.set('clear', () => ({
            action: 'clear',
            output: null
        }));

        this.commands.set('sudo', () => ({
            output: 'Permission denied: User is not in the sudoers file. This incident will be reported.'
        }));

        this.commands.set('repo', () => ({
            output: 'Opening repository...',
            action: 'open_url',
            url: this.data.githubUrl || 'https://github.com/example/portfolio'
        }));
    }

    /**
     * Safely execute command matching whitelist.
     * @param {string} rawInput 
     * @returns {{ output: string|null, action?: string, url?: string, isError?: boolean }}
     */
    execute(rawInput) {
        const parsed = CommandParser.parse(rawInput);
        if (!parsed.isValid) {
            return { output: null };
        }

        if (!ALLOWED_COMMANDS.includes(parsed.command)) {
            return {
                output: `command not found: ${parsed.command}. Type 'help' for available commands.`,
                isError: true
            };
        }

        const handler = this.commands.get(parsed.command);
        if (!handler) {
            return {
                output: `Command '${parsed.command}' is registered but has no handler attached.`,
                isError: true
            };
        }

        return handler(parsed.args, this.data);
    }
}
