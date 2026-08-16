import { InteractiveTerminal } from './terminal.js';

document.addEventListener('DOMContentLoaded', () => {
    const dataSourceElem = document.getElementById('terminal-data-source');
    const terminalSection = document.getElementById('terminal-section');

    if (!dataSourceElem || !terminalSection) {
        return;
    }

    try {
        const terminalData = JSON.parse(dataSourceElem.textContent);

        // Enable and display terminal on page (Progressive Enhancement)
        terminalSection.classList.add('is-initialized');

        new InteractiveTerminal({
            containerId: 'portfolio-terminal',
            inputId: 'terminal-input',
            outputId: 'terminal-output',
            dataContext: terminalData
        });
    } catch (err) {
        console.warn('Terminal initialization aborted due to data parsing error:', err);
    }
});
