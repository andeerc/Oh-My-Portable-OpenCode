const fs = require('fs');
const path = require('path');
const os = require('os');

const home = os.homedir();
const opencodeConfigDir = path.join(home, '.config', 'opencode');
const targetAgentDir = path.join(opencodeConfigDir, 'agent');
const targetCommandDir = path.join(opencodeConfigDir, 'command');

const sourcePromptsDir = path.join(__dirname, '..', 'dist', 'prompts');
const sourceAgentFile = path.join(sourcePromptsDir, 'agent', 'conductor.md');
const sourceCommandsDir = path.join(sourcePromptsDir, 'commands');

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

try {
  ensureDir(targetAgentDir);
  ensureDir(targetCommandDir);

  if (fs.existsSync(sourceAgentFile)) {
    fs.copyFileSync(sourceAgentFile, path.join(targetAgentDir, 'conductor.md'));
    console.log('[Conductor] Installed agent definition.');
  }

  if (fs.existsSync(sourceCommandsDir)) {
    const commands = fs.readdirSync(sourceCommandsDir);
    for (const cmdFile of commands) {
      fs.copyFileSync(path.join(sourceCommandsDir, cmdFile), path.join(targetCommandDir, cmdFile));
    }
    console.log('[Conductor] Installed slash commands.');
  }
} catch (err) {
  console.error('[Conductor] Setup failed:', err.message);
}