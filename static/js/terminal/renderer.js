/**
 * Safe DOM Terminal Renderer (ARCH-016: Zero innerHTML injection)
 */
export class TerminalRenderer {
    constructor(outputContainer) {
        this.container = outputContainer;
    }

    /**
     * Render user command input line.
     * @param {string} commandText 
     */
    renderCommandLine(commandText) {
        const line = document.createElement('div');
        line.className = 'terminal-line terminal-line--command';

        const prompt = document.createElement('span');
        prompt.className = 'terminal-prompt';
        prompt.appendChild(document.createTextNode('ali@portfolio:~$ '));

        const cmd = document.createElement('span');
        cmd.className = 'terminal-cmd-text';
        cmd.appendChild(document.createTextNode(commandText));

        line.appendChild(prompt);
        line.appendChild(cmd);
        this.container.appendChild(line);
    }

    /**
     * Render processed command output block.
     * @param {string} outputText 
     * @param {boolean} isError 
     */
    renderOutput(outputText, isError = false) {
        if (!outputText) return;

        const block = document.createElement('pre');
        block.className = isError 
            ? 'terminal-output terminal-output--error' 
            : 'terminal-output';
        
        block.appendChild(document.createTextNode(outputText));
        this.container.appendChild(block);
    }

    /**
     * Completely clear the terminal output.
     */
    clear() {
        while (this.container.firstChild) {
            this.container.removeChild(this.container.firstChild);
        }
    }

    /**
     * Automatically scroll to the bottom of the terminal output.
     */
    scrollToBottom() {
        this.container.scrollTop = this.container.scrollHeight;
    }
}
