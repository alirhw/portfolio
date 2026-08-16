import { CommandParser } from './parser.js';
import { ThemeManager, THEMES } from '../theme.js';

export const ALLOWED_COMMANDS = Object.freeze([
    'help',
    'skills',
    'projects',
    'contact',
    'stats',
    'clear',
    'theme',
    'repo',
    'sudo'
]);

export class CommandRegistry {
    constructor(dataContext = {}) {
        this.data = dataContext; // Contains skills, projects, contact, stats parsed from json payload
        this.commands = new Map();
        this._registerBuiltins();
    }

    _registerBuiltins() {
        this.commands.set('help', () => ({
            output: [
                'Available commands:',
                '  help      - Show this help menu',
                '  skills    - List skills grouped by category',
                '  projects  - List featured projects and technologies',
                '  contact   - Show contact channels (email, github, linkedin)',
                '  stats     - View live GitHub activity metrics',
                '  theme     - Toggle or set theme (usage: theme [light|dark])',
                '  repo      - Open repository URL in a new tab',
                '  clear     - Clear the terminal screen',
                '  sudo      - Request superuser permissions'
            ].join('\n')
        }));

        this.commands.set('skills', () => {
            const categories = this.data.skills || [];
            if (categories.length === 0) {
                return { output: 'No skills found in database context.' };
            }

            const lines = ['Technical Competencies:'];
            categories.forEach(cat => {
                const categoryName = cat.category || cat.name || 'General';
                const skillNames = (cat.skills || [])
                    .map(s => (typeof s === 'string' ? s : s.name))
                    .join(', ');
                lines.push(`  [${categoryName}] -> ${skillNames || 'None'}`);
            });
            return { output: lines.join('\n') };
        });

        this.commands.set('projects', () => {
            const projects = this.data.projects || [];
            if (projects.length === 0) {
                return { output: 'No featured projects found.' };
            }

            const lines = ['Featured Projects:'];
            projects.forEach((proj, idx) => {
                const stack = (proj.technologies || []).join(', ');
                lines.push(`  ${idx + 1}. ${proj.title} [${stack}]`);
                if (proj.summary) {
                    lines.push(`     "${proj.summary}"`);
                }
                if (proj.url) {
                    lines.push(`     Link: ${proj.url}`);
                }
            });
            return { output: lines.join('\n') };
        });

        this.commands.set('contact', () => {
            const contact = this.data.contact || {};
            const lines = ['Contact & Links:'];
            if (contact.name) lines.push(`  Name:     ${contact.name}`);
            if (contact.email) lines.push(`  Email:    ${contact.email}`);
            if (contact.github) lines.push(`  GitHub:   ${contact.github}`);
            if (contact.linkedin) lines.push(`  LinkedIn: ${contact.linkedin}`);
            return { output: lines.join('\n') };
        });

        this.commands.set('stats', () => {
            const stats = this.data.stats || {};
            return {
                output: [
                    'GitHub Metrics:',
                    `  Contributions (1y): ${stats.contributions ?? 0}`,
                    `  Public Repos:       ${stats.repos ?? 0}`,
                    `  Stars Earned:       ${stats.stars ?? 0}`,
                    `  Current Streak:     ${stats.streak ?? 0} days`
                ].join('\n')
            };
        });

        this.commands.set('theme', (args) => {
            const target = args[0] ? args[0].toLowerCase() : null;

            if (target === 'dark') {
                ThemeManager.setTheme(THEMES.DARK);
                return { output: 'Theme switched to dark mode.' };
            }

            if (target === 'light') {
                ThemeManager.setTheme(THEMES.LIGHT);
                return { output: 'Theme switched to light mode.' };
            }

            if (!target || target === 'toggle') {
                const newTheme = ThemeManager.toggleTheme();
                return { output: `Theme toggled to ${newTheme} mode.` };
            }

            return {
                output: `Invalid theme argument: '${target}'. Usage: theme [light|dark]`,
                isError: true
            };
        });

        this.commands.set('repo', () => ({
            output: 'Opening GitHub repository...',
            action: 'open_url',
            url: this.data.contact?.github || 'https://github.com'
        }));

        this.commands.set('clear', () => ({
            action: 'clear',
            output: null
        }));

        this.commands.set('sudo', () => ({
            output: 'Permission denied: User is not in the sudoers file. This incident will be reported.',
            isError: true
        }));
    }

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
        return handler(parsed.args, this.data);
    }
}
