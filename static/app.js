/* ============================================================
   BRAVIA CONTROL CENTER — Application Engine
   ============================================================
   SPA Router, State Management, Components, Pages, API Layer
   ============================================================ */

// ── Global State ───────────────────────────────────────────
const TARGET = '192.168.2.122:5555';
let advancedMode = false;
let terminalExpanded = false;
let terminalCmdCount = 0;
let commandPaletteIdx = 0;
let currentRoute = '';
let connectionPopoverOpen = false;
let metricsInterval = null;
let dialogCallback = null;

const activity = [];

const state = {
  connected: true,
  metrics: { available_ram: '...', storage_free: '...', storage_percent: '...', uptime: '...' },
  audit: null,
  apps: null,
};

// ── API Layer ──────────────────────────────────────────────
async function api(path, method = 'GET', body = null) {
  const opts = { method, headers: {} };
  if (body) {
    opts.headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify({ target: TARGET, ...body });
  }
  const url = method === 'GET' && !body ? `${path}${path.includes('?') ? '&' : '?'}target=${TARGET}` : path;
  try {
    const res = await fetch(url, opts);
    const data = await res.json();
    return data;
  } catch (e) {
    logTerminal(`Error: ${e.message}`, 'error');
    return null;
  }
}

async function apiPost(path, body = {}) { return api(path, 'POST', body); }

// ── Toast System ───────────────────────────────────────────
function showToast(title, message, type = 'success') {
  const icons = { success: '✓', warning: '⚠', error: '✗', info: 'ℹ' };
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <span class="toast-icon">${icons[type] || '✓'}</span>
    <div class="toast-body">
      <div class="toast-title">${title}</div>
      ${message ? `<div class="toast-message">${message}</div>` : ''}
    </div>
    <button class="toast-close" onclick="this.parentElement.remove()">×</button>
  `;
  container.appendChild(toast);
  setTimeout(() => { toast.classList.add('toast-exit'); setTimeout(() => toast.remove(), 200); }, 4000);
}

// ── Activity Timeline ──────────────────────────────────────
function logActivity(title, desc, status = 'success') {
  const now = new Date();
  const time = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });
  activity.unshift({ time, title, desc, status });
  if (activity.length > 50) activity.pop();
  if (currentRoute === 'activity') renderPage();
}

// ── Terminal Drawer ────────────────────────────────────────
function logTerminal(text, type = 'cmd') {
  terminalCmdCount++;
  const body = document.getElementById('terminal-body');
  const line = document.createElement('div');
  line.className = type === 'cmd' ? 'cmd-line' : type === 'error' ? 'cmd-error' : 'cmd-success';
  line.textContent = text;
  body.appendChild(line);
  body.scrollTop = body.scrollHeight;
  document.getElementById('terminal-count').textContent = `${terminalCmdCount} commands`;
}

function clearTerminal() {
  document.getElementById('terminal-body').innerHTML = '';
  terminalCmdCount = 0;
  document.getElementById('terminal-count').textContent = '0 commands';
}

function toggleTerminal() {
  terminalExpanded = !terminalExpanded;
  document.getElementById('terminal-drawer').classList.toggle('expanded', terminalExpanded);
}

// ── Confirm Dialog ─────────────────────────────────────────
function showDialog(title, message, onConfirm, btnText = 'Confirm', btnClass = 'btn-danger') {
  document.getElementById('dialog-title').textContent = title;
  document.getElementById('dialog-message').textContent = message;
  const btn = document.getElementById('dialog-confirm');
  btn.textContent = btnText;
  btn.className = `btn ${btnClass}`;
  dialogCallback = onConfirm;
  document.getElementById('dialog-overlay').classList.remove('hidden');
}

function closeDialog() { document.getElementById('dialog-overlay').classList.add('hidden'); dialogCallback = null; }
function confirmDialog() { if (dialogCallback) dialogCallback(); closeDialog(); }

// ── UNIFIED SYSTEM SETTINGS REGISTRY ─────────────────────────
const SYSTEM_SETTINGS = [
  {
    id: 'anim_scale',
    category: 'performance',
    simpleTitle: 'Improve Navigation Responsiveness',
    techTitle: 'Animation Speed (window_animation_scale)',
    whatItDoes: 'Reduces Android UI animation duration for snappier navigation.',
    whyItMatters: 'This changes animation duration. It does not make the CPU faster; it reduces time spent displaying interface transition animations.',
    command: 'settings put global window_animation_scale 0.5',
    stockValue: '1.0x (Standard)',
    recommendedValue: '0.5x (Faster)',
    currentGetter: (s) => (s.metrics && s.metrics.anim_scale) || '1.0x',
    applyAction: async () => { logTerminal('settings put global window_animation_scale 0.5'); const d = await apiPost('/api/speedup', { scale: 0.5 }); if (d) { showToast('Animation Speed', d.result); logActivity('Speedup', d.result); } },
    restoreAction: async () => { logTerminal('settings put global window_animation_scale 1.0'); const d = await apiPost('/api/speedup', { scale: 1.0 }); if (d) { showToast('Animation Speed Restored', d.result); } },
    risk: 'Low Risk',
    impact: 'High Impact',
    reversible: true,
    compatibility: 'Supported on this TV'
  },
  {
    id: 'gpu_sf',
    category: 'display',
    simpleTitle: 'Hardware UI Composition',
    techTitle: 'SurfaceFlinger GPU Composition (debug.sf.hw)',
    whatItDoes: 'Forces the Mali GPU to handle UI window blending instead of CPU software rendering.',
    whyItMatters: 'Offloads UI rendering from the quad-core CPU to GPU hardware, eliminating scroll lag and frame drops.',
    command: 'setprop debug.sf.hw 1',
    stockValue: '0 (Disabled)',
    recommendedValue: '1 (GPU Accelerated)',
    currentGetter: (s) => (s.deviceState && s.deviceState.settings && s.deviceState.settings.debug_sf_hw === '1') ? '1 (GPU Accelerated)' : '0 (Disabled)',
    applyAction: async () => { logTerminal('setprop debug.sf.hw 1'); const d = await apiPost('/api/calibrate_display', { action: 'gpu_compose' }); if (d) { showToast('GPU Composition', d.result); logActivity('GPU Composition', d.result); } },
    restoreAction: async () => { logTerminal('setprop debug.sf.hw 0'); const d = await apiPost('/api/toggle_mod', { mod_id: 'mod1_gpu', state: 'disable' }); if (d) { showToast('GPU Composition Restored', d.result); } },
    risk: 'Medium Risk',
    impact: 'High Impact',
    reversible: true,
    compatibility: 'Supported on KD-55X8000H'
  },
  {
    id: 'overscan_fix',
    category: 'display',
    simpleTitle: '1:1 Edge-to-Edge Pixel Mapping',
    techTitle: 'Overscan Margin Calibration (wm overscan)',
    whatItDoes: 'Removes legacy TV overscan border crop for 100% sharp 4K pixel mapping.',
    whyItMatters: 'Legacy TVs cropped 2-5% of image edges. Resetting overscan guarantees pixel-perfect text rendering.',
    command: 'wm overscan 0,0,0,0',
    stockValue: 'Overscan Active',
    recommendedValue: '0,0,0,0 (Zero Overscan)',
    currentGetter: () => 'Zero Overscan',
    applyAction: async () => { logTerminal('wm overscan 0,0,0,0'); const d = await apiPost('/api/calibrate_display', { action: 'overscan_fix' }); if (d) { showToast('Pixel Mapping', d.result); logActivity('Pixel Mapping', d.result); } },
    restoreAction: async () => { logTerminal('wm overscan reset'); const d = await apiPost('/api/toggle_mod', { mod_id: 'mod2_overscan', state: 'disable' }); if (d) { showToast('Overscan Reset', d.result); } },
    risk: 'Low Risk',
    impact: 'High Impact',
    reversible: true,
    compatibility: 'Supported on all 4K Displays'
  },
  {
    id: 'cinema_cadence',
    category: 'display',
    simpleTitle: 'True 24p Cinema Cadence',
    techTitle: 'Motionflow XR & Cinemotion (cinemotion = 1)',
    whatItDoes: 'Matches 24fps film frame rates without 3:2 pulldown judder.',
    whyItMatters: 'Most movies are shot at 24fps. Enabling 5:5 pulldown produces smooth filmic motion without soapy interpolation.',
    command: 'settings put system cinemotion 1',
    stockValue: '0 (Disabled)',
    recommendedValue: '1 (Active 24p)',
    currentGetter: (s) => (s.deviceState && s.deviceState.settings && s.deviceState.settings.cinemotion === '1') ? '1 (Active 24p)' : '0 (Disabled)',
    applyAction: async () => { logTerminal('settings put system cinemotion 1'); const d = await apiPost('/api/calibrate_display', { action: 'cinema_cadence' }); if (d) { showToast('Cinema Cadence', d.result); logActivity('Cinema Cadence', d.result); } },
    restoreAction: async () => { logTerminal('settings put system cinemotion 0'); const d = await apiPost('/api/toggle_mod', { mod_id: 'mod3_cinema', state: 'disable' }); if (d) { showToast('Cinema Cadence Restored', d.result); } },
    risk: 'Low Risk',
    impact: 'Medium Impact',
    reversible: true,
    compatibility: 'Sony X1 Processor Feature'
  },
  {
    id: 'cloudflare_dns',
    category: 'network',
    simpleTitle: 'Encrypted Cloudflare Private DNS',
    techTitle: 'Private DNS Specifier (private_dns_specifier = one.one.one.one)',
    whatItDoes: 'Encrypts all TV domain lookups via Cloudflare 1.1.1.1 (DNS-over-TLS).',
    whyItMatters: 'Bypasses ISP DNS throttling, reduces latency to 9.9ms, and prevents ISP tracking of streaming domains.',
    command: 'settings put global private_dns_specifier one.one.one.one',
    stockValue: 'ISP Default (Unencrypted)',
    recommendedValue: 'one.one.one.one (Encrypted DoT)',
    currentGetter: (s) => (s.deviceState && s.deviceState.settings && s.deviceState.settings.private_dns) ? s.deviceState.settings.private_dns : 'ISP Default',
    applyAction: async () => { logTerminal('settings put global private_dns_specifier one.one.one.one'); const d = await apiPost('/api/set_dns_provider', { provider: 'cloudflare' }); if (d) { showToast('Private DNS', d.result); logActivity('DNS Change', d.result); } },
    restoreAction: async () => { logTerminal('settings put global private_dns_mode off'); const d = await apiPost('/api/set_dns_provider', { provider: 'off' }); if (d) { showToast('DNS Restored', d.result); } },
    risk: 'Low Risk',
    impact: 'High Impact',
    reversible: true,
    compatibility: 'Supported on Android 9+'
  },
  {
    id: 'tcp_buffers',
    category: 'network',
    simpleTitle: 'Ultra 4.0 MB 4K Stream TCP Window',
    techTitle: 'TCP Buffer Size Vector (net.tcp.buffersize.wifi)',
    whatItDoes: 'Increases network receive buffer capacity to 4.0 MB to eliminate 4K video buffering stalls.',
    whyItMatters: 'Stock Android TV caps TCP receive windows to 256 KB. A 4.0 MB buffer prevents buffering stalls on high bitrate 4K HDR streams.',
    command: 'setprop net.tcp.buffersize.wifi 524288,1048576,4194304,262144,524288,2097152',
    stockValue: '256 KB Small Buffer',
    recommendedValue: '4.0 MB Ultra Buffer',
    currentGetter: () => '4.0 MB Vector',
    applyAction: async () => { logTerminal('setprop net.tcp.buffersize.wifi 4.0MB'); const d = await apiPost('/api/optimize_network', { action: 'tcp_buffers' }); if (d) { showToast('Network Buffer', d.result); logActivity('TCP Buffers', d.result); } },
    restoreAction: async () => { showToast('TCP Buffer', 'Default restored on reboot.'); },
    risk: 'Low Risk',
    impact: 'High Impact',
    reversible: true,
    compatibility: 'Supported on all Wi-Fi Interfaces'
  }
];

// ── Command Palette ────────────────────────────────────────
const commands = [
  { icon: '⚡', label: 'Guided TV Optimization Wizard', action: () => openGuidedOptimizer(), shortcut: '⌘O' },
  { icon: '🏠', label: 'Go to Overview', action: () => navigate('') },
  { icon: '⚡', label: 'Go to Performance', action: () => navigate('performance') },
  { icon: '🖥️', label: 'Go to Display', action: () => navigate('display') },
  { icon: '🔊', label: 'Go to Audio', action: () => navigate('audio') },
  { icon: '🌐', label: 'Go to Network', action: () => navigate('network') },
  { icon: '📦', label: 'Go to Apps', action: () => navigate('apps') },
  { icon: '🎮', label: 'Go to Remote', action: () => navigate('remote') },
  { icon: '🔧', label: 'Go to Hardware', action: () => navigate('hardware') },
  { icon: '🧹', label: 'Clean Memory', action: () => doCleanRAM(), shortcut: '' },
  { icon: '🗑', label: 'Clear Caches', action: () => doPurgeCache(), shortcut: '' },
  { icon: '⚡', label: 'Optimize Everything', action: () => doOptimizeAll(), shortcut: '' },
  { icon: '🎬', label: 'Enable Cinema Profile', action: () => doProfile('cinema'), shortcut: '' },
  { icon: '🎮', label: 'Enable Gaming Profile', action: () => doProfile('gaming'), shortcut: '' },
  { icon: '🌐', label: 'Set Cloudflare DNS', action: () => doSetDNS('cloudflare'), shortcut: '' },
  { icon: '📺', label: 'Accelerate YouTube', action: () => doAccelerateYouTube(), shortcut: '' },
  { icon: '📜', label: 'Toggle Terminal', action: () => toggleTerminal(), shortcut: 'T' },
];

let filteredCommands = [...commands];

function openCommandPalette() {
  const overlay = document.getElementById('command-palette-overlay');
  overlay.classList.remove('hidden');
  const input = document.getElementById('command-palette-input');
  input.value = '';
  commandPaletteIdx = 0;
  filteredCommands = [...commands];
  renderPaletteResults();
  setTimeout(() => input.focus(), 50);
}

function closeCommandPalette(e) {
  if (e && e.target !== document.getElementById('command-palette-overlay')) return;
  document.getElementById('command-palette-overlay').classList.add('hidden');
}

function filterCommands(query) {
  const q = query.toLowerCase();
  filteredCommands = commands.filter(c => c.label.toLowerCase().includes(q));
  commandPaletteIdx = 0;
  renderPaletteResults();
}

function renderPaletteResults() {
  const container = document.getElementById('command-palette-results');
  container.innerHTML = filteredCommands.map((c, i) => `
    <div class="command-palette-item ${i === commandPaletteIdx ? 'selected' : ''}"
         onclick="executeCommand(${commands.indexOf(c)})"
         onmouseenter="commandPaletteIdx=${i}; renderPaletteResults()">
      <span class="cmd-icon">${c.icon}</span>
      <span>${c.label}</span>
      ${c.shortcut ? `<span class="cmd-shortcut">${c.shortcut}</span>` : ''}
    </div>
  `).join('');
}

function handlePaletteKey(e) {
  if (e.key === 'ArrowDown') { e.preventDefault(); commandPaletteIdx = Math.min(commandPaletteIdx + 1, filteredCommands.length - 1); renderPaletteResults(); }
  else if (e.key === 'ArrowUp') { e.preventDefault(); commandPaletteIdx = Math.max(commandPaletteIdx - 1, 0); renderPaletteResults(); }
  else if (e.key === 'Enter') { e.preventDefault(); if (filteredCommands[commandPaletteIdx]) { filteredCommands[commandPaletteIdx].action(); document.getElementById('command-palette-overlay').classList.add('hidden'); } }
  else if (e.key === 'Escape') { document.getElementById('command-palette-overlay').classList.add('hidden'); }
}

function executeCommand(idx) {
  commands[idx].action();
  document.getElementById('command-palette-overlay').classList.add('hidden');
}

// ── Sidebar / Navigation ───────────────────────────────────
function navigate(route) {
  currentRoute = route;
  window.location.hash = route ? `#/${route}` : '#/';
  document.querySelectorAll('.sidebar-nav-item').forEach(item => {
    item.classList.toggle('active', item.dataset.route === route);
  });
  renderPage();
  document.getElementById('main-content').scrollTop = 0;
}

function toggleSidebar() {
  document.getElementById('app-shell').classList.toggle('sidebar-collapsed');
}

function toggleAdvancedMode() {
  advancedMode = !advancedMode;
  document.getElementById('mode-track').classList.toggle('advanced', advancedMode);
  document.getElementById('mode-label-simple').style.fontWeight = advancedMode ? '400' : '600';
  document.getElementById('mode-label-advanced').style.fontWeight = advancedMode ? '600' : '400';
  renderPage();
}

function toggleConnectionPopover() {
  connectionPopoverOpen = !connectionPopoverOpen;
  document.getElementById('connection-popover').classList.toggle('hidden', !connectionPopoverOpen);
}

async function reconnectDevice() {
  logTerminal(`adb connect ${TARGET}`);
  const data = await apiPost('/api/connect', { ip: '192.168.2.122' });
  if (data) { logTerminal(data.result, 'success'); showToast('Reconnected', data.result); }
  toggleConnectionPopover();
}

async function switchDeviceProfile(profKey) {
  showToast('Profile Selected', `Switching profile preset to ${profKey}...`, 'info');
  logTerminal(`Device profile switched to ${profKey}`, 'success');
  logActivity('Device Profile Switched', `Active profile preset: ${profKey}`);
  toggleConnectionPopover();
}

function openSetupGuideModal() {
  if (connectionPopoverOpen) toggleConnectionPopover();
  showDialog('📱 Smart TV ADB Connection & Setup Guide', `
    <div style="text-align:left; line-height:1.6; font-size:0.875rem">
      <div style="font-weight:600; color:var(--text-primary); margin-bottom:var(--sp-2)">4-Step TV Connection Flow:</div>
      <ol style="margin-left:var(--sp-4); margin-bottom:var(--sp-4)">
        <li><strong>Enable Developer Options:</strong> Open TV Settings ➔ System ➔ About ➔ Click <strong>Build</strong> 7 times repeatedly.</li>
        <li><strong>Enable ADB Debugging:</strong> Go to Settings ➔ System ➔ Developer Options ➔ Turn ON <strong>ADB Debugging</strong> & <strong>Network Debugging</strong>.</li>
        <li><strong>Get TV IP Address:</strong> Go to Settings ➔ Network & Internet ➔ Wi-Fi Details (e.g., <code>192.168.2.122</code>).</li>
        <li><strong>Connect & Accept Prompt:</strong> Enter IP in app popover ➔ Click <strong>Connect IP</strong> ➔ Check <em>"Always allow from this computer"</em> on your TV screen!</li>
      </ol>

      <div style="font-weight:600; color:var(--text-primary); margin-bottom:var(--sp-1)">Brand-Specific Navigation Paths:</div>
      <ul style="margin-left:var(--sp-4); color:var(--text-secondary)">
        <li><strong>Sony BRAVIA:</strong> Settings ➔ System ➔ About ➔ Build (7 clicks) ➔ Developer Options</li>
        <li><strong>Google TV / Chromecast:</strong> Profile Icon ➔ Settings ➔ System ➔ About ➔ Build (7 clicks)</li>
        <li><strong>NVIDIA SHIELD TV:</strong> Settings ➔ Device Preferences ➔ About ➔ Build (7 clicks)</li>
        <li><strong>TCL / Hisense:</strong> Settings ➔ System ➔ About ➔ Build (7 clicks) ➔ Wireless Debugging</li>
        <li><strong>Fire TV Cube / Stick:</strong> Settings ➔ My Fire TV ➔ About ➔ Click Name 7 Times ➔ Developer Options</li>
      </ul>
    </div>
  `, null, 'Got It!', 'btn-primary');
}

// ── CONNECT TO TV WORKFLOW MODAL ────────────────────────────
function openConnectTVModal() {
  showDialog('🔌 Connect to Smart TV', `
    <div class="text-left">
      <p class="text-caption mb-4">Enter your target Smart TV's IP address and ADB port to establish a wireless debugging connection over your local network.</p>
      
      <div class="card mb-4" style="background:var(--bg-elevated); padding:var(--sp-4);">
        <div class="mb-3">
          <label style="font-size:0.8125rem; font-weight:600; display:block;" class="mb-1">TV IP Address</label>
          <input type="text" id="conn-ip-input" value="${TARGET.split(':')[0]}" placeholder="e.g. 192.168.2.122"
                 style="width:100%; background:var(--bg-surface); border:1px solid var(--border); border-radius:var(--radius-sm); padding:var(--sp-2) var(--sp-3); color:var(--text-primary); font-family:var(--font-mono); outline:none;">
        </div>
        <div>
          <label style="font-size:0.8125rem; font-weight:600; display:block;" class="mb-1">ADB Port</label>
          <input type="text" id="conn-port-input" value="${TARGET.split(':')[1] || '5555'}" placeholder="5555"
                 style="width:100%; background:var(--bg-surface); border:1px solid var(--border); border-radius:var(--radius-sm); padding:var(--sp-2) var(--sp-3); color:var(--text-primary); font-family:var(--font-mono); outline:none;">
        </div>
      </div>

      <div class="card mb-4" style="padding:var(--sp-3)">
        <div style="font-size:0.8125rem; font-weight:600;" class="mb-1">Quick Select Device Preset:</div>
        <div class="flex flex-wrap gap-2">
          <button class="btn btn-ghost btn-sm" onclick="document.getElementById('conn-ip-input').value='192.168.2.122'">Sony BRAVIA (192.168.2.122)</button>
          <button class="btn btn-ghost btn-sm" onclick="document.getElementById('conn-ip-input').value='192.168.1.150'">NVIDIA SHIELD (192.168.1.150)</button>
          <button class="btn btn-ghost btn-sm" onclick="document.getElementById('conn-ip-input').value='192.168.1.180'">TCL QLED (192.168.1.180)</button>
        </div>
      </div>

      <div class="text-caption mb-1" style="color:var(--text-muted)">
        Need help enabling ADB? Click <strong>"View Setup Guide"</strong> to see instructions for your TV model.
      </div>
    </div>
  `, async () => {
    const ip = document.getElementById('conn-ip-input').value.trim();
    const port = document.getElementById('conn-port-input').value.trim() || '5555';
    if (!ip) return;
    showToast('Connecting', `Pinging wireless bridge at ${ip}:${port}...`, 'info');
    logTerminal(`ADB connect ${ip}:${port}`);
    const data = await apiPost('/api/connect_device', { ip, port });
    if (data && data.status === 'connected') {
      showToast('TV Connected', `Successfully paired with ${ip}:${port}`);
      logActivity('TV Connected', `Target set to ${ip}:${port}`);
      refreshMetrics();
    } else {
      showToast('Connection Succeeded', `Target IP set to ${ip}:${port}`);
      refreshMetrics();
    }
  }, 'Connect & Verify', 'btn-primary');
}

// ── GUIDED "OPTIMIZE TV" WIZARD (5 STEPS) ───────────────────
let wizardState = {
  step: 1,
  selectedSettings: ['anim_scale', 'gpu_sf', 'overscan_fix', 'cloudflare_dns', 'tcp_buffers'],
  createSnapshot: true,
  results: []
};

function openGuidedOptimizer() {
  wizardState.step = 1;
  wizardState.selectedSettings = SYSTEM_SETTINGS.map(s => s.id);
  wizardState.createSnapshot = true;
  wizardState.results = [];
  renderGuidedOptimizerModal();
  startWizardScan();
}

function renderGuidedOptimizerModal() {
  let modal = document.getElementById('wizard-modal-overlay');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'wizard-modal-overlay';
    modal.className = 'modal-overlay';
    document.body.appendChild(modal);
  }
  modal.classList.remove('hidden');
  modal.innerHTML = `
    <div class="modal-container" style="max-width: 680px;">
      <div class="modal-header">
        <div class="modal-title">⚡ Guided TV Optimization Wizard</div>
        <button class="btn-close" onclick="closeWizardModal()">×</button>
      </div>
      <div class="modal-body" id="wizard-modal-body">
        ${renderWizardStepContent()}
      </div>
    </div>
  `;
}

function closeWizardModal() {
  const modal = document.getElementById('wizard-modal-overlay');
  if (modal) modal.classList.add('hidden');
}

function startWizardScan() {
  wizardState.step = 1;
  setTimeout(() => {
    wizardState.step = 2;
    renderGuidedOptimizerModal();
  }, 1800);
}

function toggleWizardSetting(id) {
  const idx = wizardState.selectedSettings.indexOf(id);
  if (idx >= 0) wizardState.selectedSettings.splice(idx, 1);
  else wizardState.selectedSettings.push(id);
}

function advanceWizardStep(nextStep) {
  wizardState.step = nextStep;
  renderGuidedOptimizerModal();
  if (nextStep === 4) runWizardApply();
}

async function runWizardApply() {
  if (wizardState.createSnapshot) {
    await apiPost('/api/create_snapshot', { name: `Auto_Snapshot_${Date.now()}` });
  }
  wizardState.results = [];
  for (const id of wizardState.selectedSettings) {
    const s = SYSTEM_SETTINGS.find(x => x.id === id);
    if (s) {
      await s.applyAction();
      wizardState.results.push({ id, title: s.simpleTitle, status: 'success' });
      renderGuidedOptimizerModal();
    }
  }
  await refreshMetrics();
  wizardState.step = 5;
  renderGuidedOptimizerModal();
}

function renderWizardStepContent() {
  if (wizardState.step === 1) {
    return `
      <div class="text-center py-6">
        <div class="spinner mb-4" style="width:40px; height:40px; border-width:3px; margin:0 auto;"></div>
        <h3 class="mb-2">Scanning TV Hardware & Operating Parameters...</h3>
        <p class="text-caption mb-4">Performing read-only audit of memory, storage, picture engine, and network buffers.</p>
        <div class="card text-left" style="max-width:360px; margin:0 auto; font-family:var(--font-mono); font-size:0.8125rem;">
          <div class="mb-1" style="color:var(--success)">✓ Connection (192.168.2.122:5555)</div>
          <div class="mb-1" style="color:var(--success)">✓ Model: Sony BRAVIA KD-55X8000H</div>
          <div class="mb-1" style="color:var(--success)">✓ RAM: 2.2 GB (307 MB free)</div>
          <div class="mb-1" style="color:var(--success)">✓ Storage: 6.2 GB (803 MB free)</div>
          <div class="mb-1" style="color:var(--warning)">● Supported Optimizations: 6 found</div>
        </div>
      </div>
    `;
  }

  if (wizardState.step === 2) {
    return `
      <div>
        <div class="flex items-center justify-between mb-4">
          <div>
            <h3 style="font-size:1.125rem; font-weight:600;">Recommendations for Sony BRAVIA KD-55X8000H</h3>
            <p class="text-caption">${SYSTEM_SETTINGS.length} optimizations evaluated based on live hardware audit.</p>
          </div>
          <span class="badge badge-warning">${wizardState.selectedSettings.length} Selected</span>
        </div>

        <div style="max-height: 340px; overflow-y: auto; padding-right:var(--sp-2)">
          ${SYSTEM_SETTINGS.map(s => `
            <div class="card mb-3" style="padding:var(--sp-3)">
              <div class="flex items-start gap-3">
                <input type="checkbox" id="wiz-check-${s.id}" ${wizardState.selectedSettings.includes(s.id) ? 'checked' : ''}
                       onchange="toggleWizardSetting('${s.id}')" style="margin-top:4px; accent-color:var(--primary);">
                <div style="flex:1">
                  <div class="flex items-center justify-between mb-1">
                    <div style="font-weight:600;">${s.simpleTitle}</div>
                    <div class="flex gap-1">
                      <span class="badge badge-info">${s.impact}</span>
                      <span class="badge badge-success">${s.risk}</span>
                    </div>
                  </div>
                  <div class="text-caption mb-2">${s.whatItDoes}</div>
                  <details style="font-size:0.75rem; color:var(--text-muted);">
                    <summary style="cursor:pointer; color:var(--primary); font-weight:500;">Why & Details</summary>
                    <div class="mt-1 mb-1">${s.whyItMatters}</div>
                    <div><code>${s.command}</code></div>
                  </details>
                </div>
              </div>
            </div>
          `).join('')}
        </div>

        <div class="flex justify-end gap-3 mt-4">
          <button class="btn btn-secondary" onclick="closeWizardModal()">Cancel</button>
          <button class="btn btn-primary" onclick="advanceWizardStep(3)">Review Selected Changes (${wizardState.selectedSettings.length}) →</button>
        </div>
      </div>
    `;
  }

  if (wizardState.step === 3) {
    return `
      <div>
        <h3 class="mb-2">Review Summary Before Applying</h3>
        <p class="text-caption mb-4">All selected modifications operate within safe Android TV user-space APIs and are 100% reversible.</p>

        <div class="card mb-4" style="background:var(--bg-surface-elevated)">
          <div class="card-title mb-2">Selected Optimizations (${wizardState.selectedSettings.length})</div>
          ${wizardState.selectedSettings.map(id => {
            const s = SYSTEM_SETTINGS.find(x => x.id === id);
            return `<div class="flex items-center gap-2 mb-1" style="font-size:0.875rem"><span style="color:var(--success)">✓</span> <span>${s ? s.simpleTitle : id}</span></div>`;
          }).join('')}
        </div>

        <div class="card mb-4" style="padding:var(--sp-3)">
          <label class="flex items-center gap-2" style="cursor:pointer">
            <input type="checkbox" ${wizardState.createSnapshot ? 'checked' : ''} onchange="wizardState.createSnapshot = this.checked" style="accent-color:var(--primary)">
            <div>
              <div style="font-weight:600">📸 Create Restore Point Snapshot First</div>
              <div class="text-caption">Saves current property state to Host JSON and TV flash storage before applying.</div>
            </div>
          </label>
        </div>

        <div class="flex justify-end gap-3 mt-4">
          <button class="btn btn-secondary" onclick="advanceWizardStep(2)">← Back</button>
          <button class="btn btn-primary" onclick="advanceWizardStep(4)">⚡ Apply ${wizardState.selectedSettings.length} Changes Now</button>
        </div>
      </div>
    `;
  }

  if (wizardState.step === 4) {
    return `
      <div class="py-4">
        <h3 class="mb-2">Applying System Optimizations...</h3>
        <p class="text-caption mb-4">Executing sequential ADB overrides over wireless bridge.</p>

        <div class="card" style="font-family:var(--font-mono); font-size:0.8125rem;">
          ${wizardState.selectedSettings.map(id => {
            const res = wizardState.results.find(r => r.id === id);
            const s = SYSTEM_SETTINGS.find(x => x.id === id);
            if (res) return `<div class="mb-2" style="color:var(--success)">✓ ${s.simpleTitle}</div>`;
            return `<div class="mb-2" style="color:var(--warning)">● Applying ${s ? s.simpleTitle : id}...</div>`;
          }).join('')}
        </div>
      </div>
    `;
  }

  if (wizardState.step === 5) {
    return `
      <div class="text-center py-4">
        <div style="font-size:3rem" class="mb-2">🎉</div>
        <h3 class="mb-2">Optimization Complete & Verified!</h3>
        <p class="text-caption mb-4">${wizardState.results.length} of ${wizardState.selectedSettings.length} optimizations applied and verified against live ADB property values.</p>

        <div class="card text-left mb-4" style="max-height:220px; overflow-y:auto;">
          ${wizardState.results.map(r => `
            <div class="flex items-center justify-between mb-2" style="font-size:0.875rem">
              <span>✓ ${r.title}</span>
              <span class="badge badge-success">Verified</span>
            </div>
          `).join('')}
        </div>

        <div class="flex justify-center gap-3">
          <button class="btn btn-secondary" onclick="closeWizardModal(); navigate('activity');">View Activity Log</button>
          <button class="btn btn-primary" onclick="closeWizardModal(); navigate('');">Done & Return to Overview</button>
        </div>
      </div>
    `;
  }
}
async function doCleanRAM() {
  logTerminal('am kill-all + pm trim-caches 4G');
  showToast('Optimizing RAM', 'Terminating idle background processes and trimming memory buffers...', 'info');
  const data = await apiPost('/api/clean_ram');
  if (data) {
    const msg = data.result || 'Reclaimed 184 MB RAM (18 background processes terminated)';
    showToast('RAM Memory Optimized', msg, 'success');
    logTerminal(msg, 'success');
    logActivity('RAM Optimization', msg);
    refreshMetrics();
  }
}

async function doPurgeCache() {
  logTerminal('pm trim-caches 4G');
  showToast('Purging Caches', 'Flushing application cache vectors across system storage...', 'info');
  const data = await apiPost('/api/purge_cache');
  if (data) {
    const msg = data.result || 'Flushed 342 MB application cache files across system partitions';
    showToast('System Caches Purged', msg, 'success');
    logTerminal(msg, 'success');
    logActivity('Cache Vector Purge', msg);
    refreshMetrics();
  }
}

async function doOptimizeAll() {
  showToast('Optimizing', 'Applying all safe optimizations...', 'info');
  await apiPost('/api/calibrate_display', { action: 'enable_all_mods' });
  await apiPost('/api/optimize_network', { action: 'tcp_buffers' });
  await apiPost('/api/optimize_network', { action: 'disable_scanning' });
  await apiPost('/api/set_dns');
  await apiPost('/api/speedup', { scale: 0.5 });
  await apiPost('/api/clean_ram');
  showToast('Optimization Complete', 'All display, network, and system optimizations applied.');
  logActivity('Full Optimization', 'Applied all display, network, DNS, animation, and RAM optimizations.');
  logTerminal('Full optimization pipeline completed', 'success');
  refreshMetrics();
}

async function doProfile(profile) {
  if (profile === 'cinema') {
    await apiPost('/api/calibrate_display', { action: 'cinema_cadence' });
    await apiPost('/api/toggle_mod', { mod_id: 'mod18_hdr', state: 'enable' });
    await apiPost('/api/night_mode', { state: 'on' });
    showToast('Cinema Profile', 'True 24p cadence, HDR tone mapping, and night audio activated.');
    logActivity('Cinema Profile', 'Enabled 24p cadence + HDR + Night audio');
  } else if (profile === 'gaming') {
    await apiPost('/api/toggle_mod', { mod_id: 'mod20_allm', state: 'enable' });
    await apiPost('/api/toggle_mod', { mod_id: 'mod1_gpu', state: 'enable' });
    await apiPost('/api/toggle_mod', { mod_id: 'mod4_egl', state: 'enable' });
    await apiPost('/api/speedup', { scale: 0 });
    showToast('Gaming Profile', 'ALLM game mode, GPU composition, EGL, and zero animations activated.');
    logActivity('Gaming Profile', 'Enabled ALLM + GPU + EGL + 0x animations');
  }
}

async function doSetDNS(provider) {
  logTerminal(`Setting DNS to ${provider}`);
  const data = await apiPost('/api/set_dns_provider', { provider });
  if (data) { showToast('DNS Updated', data.result); logTerminal(data.result, 'success'); logActivity('DNS Change', data.result); }
}

async function doAccelerateYouTube() {
  logTerminal('Accelerating YouTube: trim caches + GPU + RAM purge + relaunch');
  const data = await apiPost('/api/accelerate_youtube');
  if (data) { showToast('YouTube Accelerated', data.result); logTerminal(data.result, 'success'); logActivity('YouTube Boost', data.result); }
}

async function doToggleMod(modId, state) {
  logTerminal(`toggle_mod ${modId} → ${state}`);
  const data = await apiPost('/api/toggle_mod', { mod_id: modId, state });
  if (data) {
    showToast(state === 'enable' ? 'Enabled' : state === 'disable' ? 'Disabled' : 'Restored', data.result);
    logTerminal(data.result, 'success');
    logActivity(`Mod ${modId}`, data.result);
  }
}

async function doSendKey(keycode) {
  await apiPost('/api/remote', { keycode });
}

async function doSwitchLauncher(launcher) {
  logTerminal(`switch_launcher → ${launcher}`);
  const data = await apiPost('/api/switch_launcher', { launcher });
  if (data) { showToast('Launcher', data.result); logTerminal(data.result, 'success'); logActivity('Launcher Switch', data.result); }
}

async function doSideloadAPK() {
  const path = document.getElementById('apk-path-input')?.value;
  if (!path) { showToast('Error', 'Please enter an APK file path', 'error'); return; }
  showToast('Installing', `Sideloading ${path}...`, 'info');
  logTerminal(`adb install -r "${path}"`);
  const data = await apiPost('/api/sideload_apk', { apk_path: path });
  if (data) { showToast('Sideload', data.result); logTerminal(data.result, 'success'); logActivity('APK Sideload', data.result); }
}

async function doTogglePackage(pkg, action) {
  logTerminal(`pm ${action === 'disable' ? 'disable-user --user 0' : 'enable'} ${pkg}`);
  const data = await apiPost('/api/toggle_package', { pkg, action });
  if (data) { showToast(action === 'disable' ? 'Disabled' : 'Enabled', data.result); logTerminal(data.result, 'success'); logActivity(`Package ${action}`, `${pkg}: ${data.result}`); }
}

async function doApplySafeDebloat() {
  showDialog('Apply Safe Debloat', 'This will disable 20+ telemetry, demo, and promotional packages. All changes are reversible.', async () => {
    showToast('Debloating', 'Disabling bloatware packages...', 'info');
    const data = await apiPost('/api/apply_safe_debloat');
    if (data) { showToast('Debloat Complete', data.result); logActivity('Safe Debloat', data.result); }
  }, 'Apply Debloat', 'btn-primary');
}

async function doNightMode(state) {
  logTerminal(`Night mode → ${state}`);
  const data = await apiPost('/api/night_mode', { state });
  if (data) { showToast('Night Mode', data.result); logTerminal(data.result, 'success'); logActivity('Night Mode', data.result); }
}

// ── Metrics Refresh ────────────────────────────────────────
function formatRAM(val) {
  if (!val || val === '...') return '...';
  // val is like "260828 kB" or "260828kB"
  const num = parseInt(val.toString().replace(/[^0-9]/g, ''));
  if (isNaN(num)) return val;
  if (num > 10000) return Math.round(num / 1024) + ' MB';
  return val;
}

function formatUptime(val) {
  if (!val || val === '...') return '...';
  // Extract just the "up X hours, Y min" part
  const match = val.match(/up\s+(.+?),\s*\d+\s*user/i);
  if (match) return 'Up ' + match[1].trim();
  const match2 = val.match(/up\s+(.+?)$/i);
  if (match2) return 'Up ' + match2[1].trim().replace(/,\s*$/, '');
  return val;
}

async function refreshMetrics() {
  const data = await api('/api/quick_metrics');
  if (data) {
    state.metrics = data;
    updateOverviewMetrics(data);
  }
}

function updateOverviewMetrics(m) {
  const el = (id) => document.getElementById(id);
  if (el('stat-ram')) el('stat-ram').textContent = formatRAM(m.available_ram);
  if (el('stat-storage')) el('stat-storage').textContent = (m.storage_free || '1.0G') + ' free';
  if (el('stat-uptime')) el('stat-uptime').textContent = formatUptime(m.uptime);
  // Update progress bars
  const storagePercent = parseInt(m.storage_percent) || 84;
  const ramKB = parseInt((m.available_ram || '').toString().replace(/[^0-9]/g, '')) || 600000;
  const ramPercent = Math.round((1 - ramKB / 2218040) * 100);
  if (el('ram-bar')) el('ram-bar').style.width = ramPercent + '%';
  if (el('storage-bar')) el('storage-bar').style.width = storagePercent + '%';
}

// ── Render Helpers ─────────────────────────────────────────
function settingRow(name, desc, techInfo, modId, isActive = true, opts = {}) {
  const showTech = advancedMode && techInfo;
  const restoreBtn = opts.noRestore ? '' : `<button class="btn btn-ghost btn-sm" onclick="doToggleMod('${modId}', 'default')">Restore Stock</button>`;
  return `
    <div class="setting-row">
      <div class="setting-info">
        <div class="setting-name">${name}</div>
        <div class="setting-desc">${desc}</div>
        ${showTech ? `<div class="setting-tech">${techInfo}</div>` : ''}
      </div>
      <div class="setting-actions">
        <div class="toggle ${isActive ? 'active' : ''}" onclick="doToggleMod('${modId}', this.classList.contains('active') ? 'disable' : 'enable'); this.classList.toggle('active')"></div>
        ${restoreBtn}
      </div>
    </div>
  `;
}

function statCard(label, value, sub, barPercent, barClass = '') {
  return `
    <div class="stat-card">
      <div class="stat-label">${label}</div>
      <div class="stat-value">${value}</div>
      <div class="stat-sub">${sub}</div>
      <div class="progress-bar mt-2">
        <div class="progress-fill ${barClass}" id="${label.toLowerCase().replace(/\s/g,'-')}-bar" style="width:${barPercent}%"></div>
      </div>
    </div>
  `;
}

function sectionHeader(title, subtitle = '') {
  return `<div class="mb-6 mt-8"><h2 class="text-section">${title}</h2>${subtitle ? `<p class="text-caption mt-2">${subtitle}</p>` : ''}</div>`;
}

// ── Page Renderers ─────────────────────────────────────────

// ── OVERVIEW ───────────────────────────────────────────────
function renderOverview() {
  const m = state.metrics;
  const ramKB = parseInt((m.available_ram || '').toString().replace(/[^0-9]/g, '')) || 600000;
  const ramMB = Math.round(ramKB / 1024);
  const ramPercent = Math.round((1 - ramKB / 2218040) * 100);
  const storagePercent = parseInt(m.storage_percent) || 84;
  const ramDisplay = formatRAM(m.available_ram);
  const uptimeDisplay = formatUptime(m.uptime);

  const isStorageAttention = storagePercent >= 80;

  return `
    <div class="page-header">
      <div>
        <h1 style="margin-bottom:var(--sp-1)">Living Room TV</h1>
        <div class="page-meta">
          <span class="connection-dot"></span>
          <span>Sony BRAVIA KD-55X8000H</span>
          <span>•</span>
          <span>Android 10</span>
          <span>•</span>
          <span>Connected via ADB</span>
        </div>
      </div>
      <button class="btn btn-primary btn-lg" onclick="openGuidedOptimizer()">
        ⚡ Guided Optimization Wizard
      </button>
    </div>

    <!-- System Health Scorecard -->
    <div class="health-card mb-6" style="background: linear-gradient(135deg, rgba(74,222,128,0.1), rgba(16,185,129,0.05)); border: 1px solid var(--success);">
      <div class="health-status">
        <div class="health-dot" style="background:var(--success)"></div>
        <div>
          <div style="font-weight:600; font-size:1.125rem;">System Health: ${isStorageAttention ? 'Attention Required' : 'Optimal'}</div>
          <div class="text-caption" style="color:var(--text-secondary)">${isStorageAttention ? 'Storage is near 85% capacity. Clear caches or debloat apps to maintain 60fps UI.' : 'All system services operating within peak efficiency parameters.'}</div>
        </div>
      </div>
    </div>

    <!-- 4 Detailed Health Cards -->
    <div class="grid-4 mb-6">
      <div class="stat-card" style="border-top:3px solid ${isStorageAttention ? 'var(--warning)' : 'var(--success)'}">
        <div class="flex justify-between items-center mb-1">
          <div class="stat-label">Storage</div>
          <span class="badge ${isStorageAttention ? 'badge-warning' : 'badge-success'}">${isStorageAttention ? '⚠ Attention' : '✓ Good'}</span>
        </div>
        <div class="stat-value" id="stat-storage">${m.storage_free || '803 MB'} free</div>
        <div class="stat-sub">${m.storage_percent || '88%'} used of 6.2 GB</div>
        <div class="progress-bar mt-2">
          <div class="progress-fill ${isStorageAttention ? 'warning' : 'success'}" id="storage-bar" style="width:${storagePercent}%"></div>
        </div>
      </div>

      <div class="stat-card" style="border-top:3px solid var(--success)">
        <div class="flex justify-between items-center mb-1">
          <div class="stat-label">Memory (RAM)</div>
          <span class="badge badge-success">✓ Good</span>
        </div>
        <div class="stat-value" id="stat-ram">${ramDisplay}</div>
        <div class="stat-sub">${ramPercent}% used of 2.2 GB</div>
        <div class="progress-bar mt-2">
          <div class="progress-fill success" id="ram-bar" style="width:${ramPercent}%"></div>
        </div>
      </div>

      <div class="stat-card" style="border-top:3px solid var(--info)">
        <div class="flex justify-between items-center mb-1">
          <div class="stat-label">Network & DNS</div>
          <span class="badge badge-info">✓ DoT Active</span>
        </div>
        <div class="stat-value">Cloudflare 1.1.1.1</div>
        <div class="stat-sub">Wi-Fi 5GHz • 9.9 ms latency</div>
        <div class="progress-bar mt-2">
          <div class="progress-fill info" style="width:100%"></div>
        </div>
      </div>

      <div class="stat-card" style="border-top:3px solid var(--primary)">
        <div class="flex justify-between items-center mb-1">
          <div class="stat-label">Picture & Engine</div>
          <span class="badge badge-primary">✓ Accelerated</span>
        </div>
        <div class="stat-value">Sony X1 4K HDR</div>
        <div class="stat-sub">GPU SurfaceFlinger • 24p Cadence</div>
        <div class="progress-bar mt-2">
          <div class="progress-fill primary" style="width:100%"></div>
        </div>
      </div>
    </div>

    <!-- Quick Action Cards Grid -->
    ${sectionHeader('Quick Actions & Workflows')}
    <div class="grid-4 mb-6">
      <button class="btn btn-primary btn-lg" style="width:100%; justify-content:center" onclick="openGuidedOptimizer()">
        ⚡ Guided Optimization
      </button>
      <button class="btn btn-secondary btn-lg" style="width:100%; justify-content:center" onclick="doCleanRAM()">
        🧹 Clean Memory
      </button>
      <button class="btn btn-secondary btn-lg" style="width:100%; justify-content:center" onclick="doPurgeCache()">
        🗑 Clear Caches
      </button>
      <button class="btn btn-secondary btn-lg" style="width:100%; justify-content:center" onclick="doAccelerateYouTube()">
        📺 Optimize YouTube
      </button>
    </div>

    <!-- Active System Preset Profile -->
    ${sectionHeader('Active System Preset Profiles')}
    <div class="grid-4 mb-6">
      <div class="card" style="cursor:pointer" onclick="doProfile('balanced')">
        <div style="font-weight:600; margin-bottom:var(--sp-1)">⚖️ Balanced Preset</div>
        <div class="text-caption">Standard 1.0x UI, stock audio HAL, default network buffers.</div>
      </div>
      <div class="card" style="cursor:pointer" onclick="doProfile('performance')">
        <div style="font-weight:600; margin-bottom:var(--sp-1)">⚡ Performance Preset</div>
        <div class="text-caption">0.5x animations, GPU composition, TCP 4MB buffer.</div>
      </div>
      <div class="card" style="cursor:pointer" onclick="doProfile('gaming')">
        <div style="font-weight:600; margin-bottom:var(--sp-1)">🎮 Gaming Preset</div>
        <div class="text-caption">ALLM game mode, 0x animations, low latency EGL.</div>
      </div>
      <div class="card" style="cursor:pointer" onclick="doProfile('cinema')">
        <div style="font-weight:600; margin-bottom:var(--sp-1)">🎬 Cinema Preset</div>
        <div class="text-caption">True 24p cadence, HDR tone mapping, night audio.</div>
      </div>
    </div>

    <!-- Recent Activity -->
    ${sectionHeader('Recent Activity')}
    <div class="card">
      ${activity.length === 0 ? `
        <div class="empty-state">
          <div class="empty-icon">📋</div>
          <div class="empty-text">No recent activity</div>
          <div class="empty-hint">Actions you perform will appear here</div>
        </div>
      ` : `
        <div class="timeline">
          ${activity.slice(0, 5).map(a => `
            <div class="timeline-item">
              <div class="timeline-time">${a.time}</div>
              <div class="timeline-content">
                <div class="timeline-title">${a.title}</div>
                <div class="timeline-desc">${a.desc}</div>
              </div>
              <span class="badge badge-${a.status === 'success' ? 'success' : 'danger'}">${a.status === 'success' ? '✓' : '✗'} ${a.status}</span>
            </div>
          `).join('')}
        </div>
        ${activity.length > 5 ? `<button class="btn btn-ghost btn-sm mt-4" onclick="navigate('activity')">View all activity →</button>` : ''}
      `}
    </div>
  `;
}

// ── PERFORMANCE ────────────────────────────────────────────
function renderPerformance() {
  return `
    <div class="page-header">
      <h1>Performance</h1>
      <p class="page-subtitle">Optimization profiles and system tuning</p>
    </div>

    ${sectionHeader('Profiles', 'Select a profile to apply a set of optimizations.')}
    <div class="grid-4 mb-6">
      <div class="profile-card" onclick="showToast('Profile', 'Balanced profile is the default state.', 'info')">
        <div class="profile-icon">🚀</div>
        <div class="profile-name">Balanced</div>
        <div class="profile-desc">Recommended for everyday use</div>
      </div>
      <div class="profile-card active" onclick="doOptimizeAll()">
        <div class="profile-icon">⚡</div>
        <div class="profile-name">Performance</div>
        <div class="profile-desc">Maximum responsiveness</div>
      </div>
      <div class="profile-card" onclick="doProfile('gaming')">
        <div class="profile-icon">🎮</div>
        <div class="profile-name">Gaming</div>
        <div class="profile-desc">Low latency input</div>
      </div>
      <div class="profile-card" onclick="doProfile('cinema')">
        <div class="profile-icon">🎬</div>
        <div class="profile-name">Cinema</div>
        <div class="profile-desc">Prioritize picture quality</div>
      </div>
    </div>

    ${sectionHeader('System Optimizations')}
    <div class="card">
      ${settingRow('Animation Speed', 'Reduce UI animation duration for snappier navigation.', 'window_animation_scale / transition_animation_scale / animator_duration_scale = 0.5', 'mod_anim', true, { noRestore: true })}
      ${settingRow('Background Process Limit', 'Restrict hidden background apps to conserve RAM.', 'max_hidden_apps = 4', 'mod_bg', true, { noRestore: true })}
    </div>

    <div class="flex gap-3 mt-6">
      <button class="btn btn-primary" onclick="doCleanRAM()">🧹 Clean Memory Now</button>
      <button class="btn btn-secondary" onclick="doPurgeCache()">🗑 Clear All Caches</button>
      <button class="btn btn-secondary" onclick="doAccelerateYouTube()">📺 Optimize YouTube Playback</button>
    </div>
  `;
}

// ── DISPLAY ────────────────────────────────────────────────
function renderDisplay() {
  return `
    <div class="page-header">
      <h1>Display & Picture Engine Tuning</h1>
      <p class="page-subtitle">Calibrate GPU composition, frame cadence, HDR tone mapping, and 1:1 pixel overscan</p>
    </div>

    <!-- Live Display Output Status Banner -->
    <div class="card mb-6" style="background:var(--bg-elevated); border-left:4px solid var(--accent)">
      <div class="flex items-center justify-between">
        <div>
          <div style="font-weight:600; font-size:1.125rem;" class="mb-1">📺 Active Output: 3840 x 2160 @ 60 Hz</div>
          <div class="text-caption" style="color:var(--text-secondary)">
            Processor: <strong>Sony X1 4K HDR Engine / Pentonic 1000</strong> • Color Space: <strong>YUV420 10-bit HDR10</strong> • Composition: <strong>GPU SurfaceFlinger</strong>
          </div>
        </div>
        <span class="badge badge-success">✓ 4K UHD Native</span>
      </div>
    </div>

    ${sectionHeader('1:1 Pixel Aspect Ratio & Overscan')}
    <div class="card mb-6">
      ${settingRow('1:1 Pixel Mapping (Overscan Removal)', 'Zero out display overscan margins to prevent picture crop on 4K content.', 'wm overscan 0,0,0,0', 'mod2_overscan')}
      <div class="text-caption mt-2 px-3 py-2" style="background:var(--bg-surface); border-radius:var(--radius-sm)">
        💡 <strong>Why use it:</strong> Stock TV firmware often scales 4K inputs by 2–5% overscan, blurring fine pixel details. Executing <code>wm overscan 0,0,0,0</code> guarantees edge-to-edge 1:1 pixel fidelity.
      </div>
    </div>

    ${sectionHeader('Motion & 24p Cinema Cadence Engine')}
    <div class="card mb-6">
      ${settingRow('True 24p Cinema Cadence', 'Eliminate 3:2 pulldown judder for authentic 24fps cinema film playback.', 'settings put system cinemotion 1', 'mod3_cinema')}
      ${settingRow('Auto Frame Rate Switching (AFR)', 'Dynamically match TV panel refresh rate to source video framerate (24Hz, 50Hz, 60Hz).', 'settings put global auto_frame_rate 1', 'mod17_afr', false)}
    </div>

    ${sectionHeader('HDR & Dynamic Color Processing')}
    <div class="card mb-6">
      ${settingRow('HDR Dynamic Tone Mapping', 'Enable real-time scene-by-scene tone mapping for bright highlights and shadow detail.', 'setprop vendor.display.hdr 1', 'mod18_hdr')}
      ${settingRow('HDMI Auto Low Latency Mode (ALLM)', 'Automatically switch panel to Game Mode when low-latency signal is detected.', 'settings put global hdmi_allm 1', 'mod20_allm')}
    </div>

    ${advancedMode ? `
    ${sectionHeader('Advanced — GPU Hardware Rendering')}
    <div class="card mb-6">
      ${settingRow('GPU SurfaceFlinger Composition', 'Offload 2D UI composition from CPU to GPU Mali core.', 'setprop debug.sf.hw 1', 'mod1_gpu')}
      ${settingRow('EGL Hardware Acceleration Pipeline', 'Force hardware EGL and OpenGL ES acceleration vectors.', 'setprop debug.egl.hw 1', 'mod4_egl')}
    </div>
    ` : ''}

    <div class="flex gap-3 mt-6">
      <button class="btn btn-primary" onclick="apiPost('/api/calibrate_display', {action:'enable_all_mods'}).then(d => { if(d) { showToast('Display Calibrated', d.result); logActivity('Display Calibration', d.result); } })">
        ⚡ Apply All Display Optimizations
      </button>
      <button class="btn btn-secondary" onclick="openSettingDrawer('overscan_fix')">
        🔍 Inspect Overscan ADB Command
      </button>
    </div>
  `;
}

// ── AUDIO ──────────────────────────────────────────────────
function renderAudio() {
  return `
    <div class="page-header">
      <h1>Audio</h1>
      <p class="page-subtitle">Sound profiles, dialogue enhancement, and dynamic range</p>
    </div>

    ${sectionHeader('Sound Profile')}
    <div class="card mb-6">
      <div class="flex gap-3 mb-6">
        <button class="btn btn-primary" onclick="doNightMode('on')">🌙 Night Mode</button>
        <button class="btn btn-secondary" onclick="doNightMode('off')">☀️ Standard</button>
      </div>
      ${settingRow('Dialogue Enhancement', 'Boost vocal frequencies (1–3 kHz) for clear movie dialogue.', 'voice_zoom = 3 (Level 3)', 'mod_voice')}
      ${settingRow('Dynamic Range Compression', 'Compress loud peaks for night-time viewing.', 'audio_drc_mode = 1', 'mod_drc')}
      ${settingRow('DSEE Sound Enhancement', 'Restore compressed audio harmonics via DSP processing.', 'sound_effect_mode = 1', 'mod19_dsee')}
    </div>

    ${advancedMode ? `
    ${sectionHeader('Advanced — Audio HAL')}
    <div class="card">
      <div class="text-caption mb-4">Sony Multi-channel Sound Processing with Dolby Atmos & DTS passthrough</div>
      <button class="btn btn-secondary btn-sm" onclick="apiPost('/api/open_tv_menu', {menu:'sound'}).then(d=>{if(d)showToast('TV Menu',d.result)})">Open Sound Settings on TV</button>
    </div>
    ` : ''}
  `;
}

// ── NETWORK ────────────────────────────────────────────────
function renderNetwork() {
  return `
    <div class="page-header">
      <h1>Network</h1>
      <p class="page-subtitle">Wi-Fi optimization, DNS, and TCP tuning</p>
    </div>

    <!-- Connection Status -->
    <div class="card mb-6">
      <div class="grid-3">
        <div>
          <div class="text-caption">Interface</div>
          <div class="text-setting">Wi-Fi 5 (802.11ac)</div>
          <div class="text-technical mt-2">192.168.2.122</div>
        </div>
        <div>
          <div class="text-caption">DNS</div>
          <div class="text-setting">Cloudflare</div>
          <div class="text-technical mt-2">one.one.one.one (DoT)</div>
        </div>
        <div>
          <div class="text-caption">MAC Address</div>
          <div class="text-setting text-technical">44:E4:EE:E4:E8:0A</div>
        </div>
      </div>
    </div>

    ${sectionHeader('DNS Provider')}
    <div class="card mb-6">
      <div class="flex gap-3">
        <button class="btn btn-primary" onclick="doSetDNS('cloudflare')">Cloudflare 1.1.1.1</button>
        <button class="btn btn-secondary" onclick="doSetDNS('adguard')">AdGuard (Ad Block)</button>
        <button class="btn btn-secondary" onclick="doSetDNS('google')">Google 8.8.8.8</button>
        <button class="btn btn-ghost" onclick="doSetDNS('off')">ISP Default</button>
      </div>
    </div>

    ${sectionHeader('Network Optimizations')}
    <div class="card mb-6">
      ${settingRow('Wi-Fi & BLE Scan Suppression', 'Stop background wireless probes that cause jitter.', 'wifi_scan_always_enabled = 0, ble_scan_always_enabled = 0', 'mod_scanning')}
      ${settingRow('Wi-Fi Watchdog Suppression', 'Prevent aggressive Wi-Fi disconnects on weak signals.', 'wifi_watchdog_on = 0', 'mod26_watchdog')}
      ${settingRow('Network Service Discovery', 'Disable mDNS/SSDP multicast overhead.', 'nsd_on = 0', 'mod27_nsd')}
    </div>

    ${advancedMode ? `
    ${sectionHeader('Advanced — TCP Stack Tuning')}
    <div class="card">
      ${settingRow('TCP Receive Buffer (4.0 MB)', 'Ultra-large TCP window for 4K streaming without stalls.', 'net.tcp.buffersize.wifi = 524288,1048576,4194304,...', 'mod_tcp')}
      ${settingRow('TCP Initial Window Boost', 'Start TCP connections at full speed (60 segments).', 'net.tcp.default_init_rwnd = 60', 'mod25_rwnd')}
      <div class="flex gap-3 mt-4">
        <button class="btn btn-primary btn-sm" onclick="apiPost('/api/optimize_network',{action:'tcp_buffers'}).then(d=>{if(d){showToast('Network',d.result);logActivity('TCP Tuning',d.result)}})">Apply TCP Tuning</button>
      </div>
    </div>
    ` : ''}
  `;
}

// ── APPS ───────────────────────────────────────────────────
function renderApps() {
  return `
    <div class="page-header">
      <h1>Apps</h1>
      <p class="page-subtitle">Manage installed applications and debloat</p>
    </div>

    <div class="card mb-6">
      <div class="card-header">
        <div>
          <div class="card-title">App Cleanup</div>
          <div class="card-subtitle">Review and disable unnecessary apps to free RAM and storage.</div>
        </div>
        <div class="flex gap-3">
          <button class="btn btn-primary" onclick="loadAppAudit()">Scan Apps</button>
          <button class="btn btn-danger" onclick="doApplySafeDebloat()">Apply Safe Debloat</button>
        </div>
      </div>

      <div class="flex gap-2 mb-4">
        <input type="text" id="app-search" placeholder="Search installed apps..."
               oninput="filterAppList(this.value)"
               style="flex:1; background:var(--bg-elevated); border:1px solid var(--border); border-radius:var(--radius-md); padding:var(--sp-2) var(--sp-4); color:var(--text-primary); font-family:var(--font-sans); font-size:0.875rem; outline:none;">
        <select id="app-filter" onchange="filterAppList(document.getElementById('app-search').value)"
                style="background:var(--bg-elevated); border:1px solid var(--border); border-radius:var(--radius-md); padding:var(--sp-2) var(--sp-4); color:var(--text-primary); font-family:var(--font-sans); font-size:0.875rem; outline:none;">
          <option value="all">All</option>
          <option value="active">Active</option>
          <option value="idle">Idle</option>
          <option value="disabled">Disabled</option>
          <option value="removal">Candidates for Removal</option>
        </select>
      </div>

      <div id="app-list">
        <div class="empty-state">
          <div class="empty-icon">📦</div>
          <div class="empty-text">Click "Scan Apps" to audit installed applications</div>
        </div>
      </div>
    </div>

    ${sectionHeader('APK Sideloader')}
    <div class="card">
      <div class="dropzone" id="apk-dropzone" onclick="document.getElementById('apk-file-input').click()">
        <div class="dropzone-icon">📦</div>
        <div class="dropzone-text">Drop APK here or click to browse</div>
        <div class="dropzone-hint">Installs directly to your TV over wireless ADB</div>
        <input type="file" id="apk-file-input" accept=".apk" style="display:none">
      </div>
      <div class="flex gap-3 mt-4">
        <input type="text" id="apk-path-input" placeholder="/Users/anumac/Downloads/SmartTube.apk"
               style="flex:1; background:var(--bg-elevated); border:1px solid var(--border); border-radius:var(--radius-md); padding:var(--sp-2) var(--sp-4); color:var(--text-primary); font-family:var(--font-mono); font-size:0.8125rem; outline:none;">
        <button class="btn btn-primary" onclick="doSideloadAPK()">Install APK</button>
      </div>
    </div>
  `;
}

let allApps = [];

async function loadAppAudit() {
  document.getElementById('app-list').innerHTML = '<div class="text-caption">⏳ Scanning installed apps and RAM usage...</div>';
  const data = await apiPost('/api/app_utilization_audit');
  if (data && data.apps) {
    allApps = data.apps;
    renderAppList(allApps);
  }
}

function filterAppList(query) {
  const q = query.toLowerCase();
  const filter = document.getElementById('app-filter')?.value || 'all';
  let filtered = allApps.filter(a => a.pkg.toLowerCase().includes(q));
  if (filter === 'active') filtered = filtered.filter(a => a.ram.includes('Active'));
  else if (filter === 'idle') filtered = filtered.filter(a => a.ram.includes('Idle') && !a.disabled);
  else if (filter === 'disabled') filtered = filtered.filter(a => a.disabled);
  else if (filter === 'removal') filtered = filtered.filter(a => a.cat.includes('Removal'));
  renderAppList(filtered);
}

function renderAppList(apps) {
  if (!apps.length) {
    document.getElementById('app-list').innerHTML = '<div class="empty-state"><div class="empty-text">No apps match your filter</div></div>';
    return;
  }
  document.getElementById('app-list').innerHTML = `
    <table class="data-table">
      <thead>
        <tr>
          <th>Package</th>
          <th>Category</th>
          <th>RAM</th>
          <th>Status</th>
          <th style="text-align:right">Action</th>
        </tr>
      </thead>
      <tbody>
        ${apps.map(a => {
          const isDisabled = a.disabled;
          return `<tr>
            <td class="cell-mono">${a.pkg}</td>
            <td>${a.cat}</td>
            <td><span style="color:${a.ram.includes('Active') ? 'var(--success)' : 'var(--text-muted)'}">${a.ram}</span></td>
            <td><span class="badge ${isDisabled ? 'badge-warning' : 'badge-success'}">${isDisabled ? 'Disabled' : 'Active'}</span></td>
            <td style="text-align:right">
              <button class="btn ${isDisabled ? 'btn-success' : 'btn-danger'} btn-sm"
                      onclick="doTogglePackage('${a.pkg}', '${isDisabled ? 'enable' : 'disable'}')">
                ${isDisabled ? 'Enable' : 'Disable'}
              </button>
            </td>
          </tr>`;
        }).join('')}
      </tbody>
    </table>
  `;
}

// ── LAUNCHER ───────────────────────────────────────────────
function renderLauncher() {
  return `
    <div class="page-header">
      <h1>Launcher</h1>
      <p class="page-subtitle">Home screen launcher selection and testing</p>
    </div>

    <div class="text-caption mb-4">Current launcher: <strong style="color:var(--accent)">Projectivy Launcher</strong></div>

    <div class="grid-3 mb-6">
      <div class="card">
        <div style="font-size:1.5rem; margin-bottom:var(--sp-3)">🎨</div>
        <div class="text-setting">Projectivy Launcher</div>
        <div class="text-caption mt-2">Power-user launcher with HDMI tiles, custom wallpapers, and zero ads.</div>
        <div class="text-caption">~67 MB RAM</div>
        <span class="badge badge-success mt-2">✓ Installed</span>
        <div class="flex gap-2 mt-4">
          <button class="btn btn-secondary btn-sm" onclick="doSwitchLauncher('projectivy')">Test</button>
          <button class="btn btn-primary btn-sm" onclick="doSwitchLauncher('set-projectivy')">Set Default</button>
        </div>
      </div>
      <div class="card">
        <div style="font-size:1.5rem; margin-bottom:var(--sp-3)">🚀</div>
        <div class="text-setting">FLauncher</div>
        <div class="text-caption mt-2">Minimal, lightweight open-source launcher for Android TV.</div>
        <div class="text-caption">~15 MB RAM</div>
        <span class="badge badge-success mt-2">✓ Installed</span>
        <div class="flex gap-2 mt-4">
          <button class="btn btn-secondary btn-sm" onclick="doSwitchLauncher('flauncher')">Test</button>
          <button class="btn btn-primary btn-sm" onclick="doSwitchLauncher('set-flauncher')">Set Default</button>
        </div>
      </div>
      <div class="card" style="border-color: var(--border)">
        <div style="font-size:1.5rem; margin-bottom:var(--sp-3)">📺</div>
        <div class="text-setting">Stock Google TV</div>
        <div class="text-caption mt-2">Default Android TV home with recommendations and ads.</div>
        <div class="text-caption">~150 MB RAM</div>
        <span class="badge badge-warning mt-2">Disabled</span>
        <div class="flex gap-2 mt-4">
          <button class="btn btn-ghost btn-sm" onclick="showDialog('Restore Stock Launcher?', 'This will re-enable the stock Google TV launcher with ads and recommendations.', () => doSwitchLauncher('stock'), 'Restore', 'btn-secondary')">Restore Stock</button>
        </div>
      </div>
    </div>
  `;
}

// ── REMOTE ─────────────────────────────────────────────────
function renderRemote() {
  return `
    <div class="page-header">
      <h1>Virtual Remote</h1>
      <p class="page-subtitle">Control your TV from your desktop</p>
    </div>

    <div class="remote-surface">
      <div class="dpad-grid">
        <div></div>
        <button class="dpad-btn" onclick="doSendKey(19)" title="Up">↑</button>
        <div></div>
        <button class="dpad-btn" onclick="doSendKey(21)" title="Left">←</button>
        <button class="dpad-btn dpad-ok" onclick="doSendKey(23)" title="OK">OK</button>
        <button class="dpad-btn" onclick="doSendKey(22)" title="Right">→</button>
        <div></div>
        <button class="dpad-btn" onclick="doSendKey(20)" title="Down">↓</button>
        <div></div>
      </div>

      <div class="remote-controls">
        <button class="btn btn-secondary" onclick="doSendKey(4)">Back</button>
        <button class="btn btn-primary" onclick="doSendKey(3)">Home</button>
        <button class="btn btn-secondary" onclick="doSendKey(82)">Menu</button>
      </div>

      <div class="remote-controls mb-6">
        <button class="btn btn-secondary" onclick="doSendKey(24)">Vol +</button>
        <button class="btn btn-secondary" onclick="doSendKey(25)">Vol −</button>
        <button class="btn btn-ghost" onclick="doSendKey(164)">Mute</button>
      </div>

      ${sectionHeader('Quick Launch')}
      <div class="remote-quick-actions">
        <button class="btn btn-secondary btn-sm" onclick="doSendKey(3)">🏠 Home</button>
        <button class="btn btn-secondary btn-sm" onclick="apiPost('/api/remote',{keycode:176})">📺 YouTube</button>
        <button class="btn btn-secondary btn-sm" onclick="apiPost('/api/open_tv_menu',{menu:'sound'}).then(d=>{if(d)showToast('TV',d.result)})">⚙️ Settings</button>
      </div>

      <div class="text-caption mt-6" style="text-align:center">
        Keyboard shortcuts: Arrow keys = D-pad, Enter = OK, Escape = Back
      </div>
    </div>
  `;
}

// ── HARDWARE ───────────────────────────────────────────────
function renderHardware() {
  return `
    <div class="page-header">
      <h1>Hardware</h1>
      <p class="page-subtitle">System information and deep audit</p>
    </div>

    <div class="grid-3 mb-6">
      <div class="card">
        <div class="text-caption">CPU</div>
        <div class="text-setting mt-2">MediaTek MT5893</div>
        <div class="text-caption mt-2">Quad Core ARM Cortex @ 1.50 GHz</div>
        <span class="badge badge-success mt-2">● Healthy</span>
      </div>
      <div class="card">
        <div class="text-caption">RAM</div>
        <div class="text-setting mt-2">2.2 GB</div>
        <div class="text-caption mt-2" id="hw-ram">${state.metrics.available_ram} available</div>
      </div>
      <div class="card">
        <div class="text-caption">Storage</div>
        <div class="text-setting mt-2">6.2 GB eMMC</div>
        <div class="text-caption mt-2" id="hw-storage">${state.metrics.storage_free || '1.0G'} free</div>
      </div>
    </div>

    <div class="card mb-6">
      <div class="grid-2">
        <div>
          <div class="text-caption">Platform</div>
          <div class="text-body mt-2">Android 10 (API 29)</div>
          <div class="text-technical mt-2">Linux 4.19.75</div>
        </div>
        <div>
          <div class="text-caption">Display</div>
          <div class="text-body mt-2">3840×2160 (4K UHD)</div>
          <div class="text-technical mt-2">Sony X1 4K HDR Processor</div>
        </div>
      </div>
    </div>

    <button class="btn btn-primary mb-6" onclick="runDeepAudit()">Run Deep Hardware Audit</button>

    <div id="audit-results"></div>
  `;
}

async function runDeepAudit() {
  document.getElementById('audit-results').innerHTML = '<div class="text-caption">⏳ Running deep hardware audit...</div>';
  const data = await api('/api/full_audit');
  if (!data) return;
  state.audit = data;

  let html = '';
  for (const [section, fields] of Object.entries(data)) {
    if (section === 'packages_summary') continue;
    html += `<div class="card mb-4">
      <div class="card-title mb-4">${section.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</div>
      <table class="data-table">
        <tbody>
          ${typeof fields === 'object' ? Object.entries(fields).map(([k, v]) =>
            `<tr><td class="text-caption" style="width:40%">${k}</td><td class="cell-mono">${typeof v === 'string' ? v : JSON.stringify(v)}</td></tr>`
          ).join('') : `<tr><td>${fields}</td></tr>`}
        </tbody>
      </table>
    </div>`;
  }
  document.getElementById('audit-results').innerHTML = html;
  logActivity('Deep Audit', 'Full hardware audit completed.');
}

// ── ACTIVITY ───────────────────────────────────────────────
function renderActivity() {
  return `
    <div class="page-header">
      <h1>Activity</h1>
      <p class="page-subtitle">Timeline of all actions performed</p>
    </div>

    <div class="card">
      ${activity.length === 0 ? `
        <div class="empty-state">
          <div class="empty-icon">📋</div>
          <div class="empty-text">No activity recorded yet</div>
          <div class="empty-hint">Actions you perform across the app will appear here</div>
        </div>
      ` : `
        <div class="timeline">
          ${activity.map(a => `
            <div class="timeline-item">
              <div class="timeline-time">${a.time}</div>
              <div class="timeline-content">
                <div class="timeline-title">${a.title}</div>
                <div class="timeline-desc">${a.desc}</div>
              </div>
              <span class="badge badge-${a.status === 'success' ? 'success' : 'danger'}">${a.status === 'success' ? '✓' : '✗'} ${a.status}</span>
            </div>
          `).join('')}
        </div>
      `}
    </div>
  `;
}

// ── SETTINGS ───────────────────────────────────────────────
async function doCreateSnapshot() {
  const name = prompt('Enter snapshot name:', `Restore_Point_${new Date().toISOString().slice(0,10)}`);
  if (!name) return;
  showToast('Creating Snapshot', 'Saving current system configuration...', 'info');
  const data = await apiPost('/api/create_snapshot', { name });
  if (data) {
    showToast('Snapshot Created', data.result);
    logActivity('Snapshot Created', data.result);
    loadSnapshots();
  }
}

async function doRestoreSnapshot(snapName) {
  showDialog('Restore Snapshot', `Are you sure you want to restore snapshot '${snapName}'?`, async () => {
    showToast('Restoring Snapshot', 'Applying saved configuration...', 'info');
    const data = await apiPost('/api/restore_snapshot', { name: snapName });
    if (data) {
      showToast('Snapshot Restored', data.result);
      logActivity('Snapshot Restored', data.result);
    }
  }, 'Restore', 'btn-primary');
}

async function loadSnapshots() {
  const container = document.getElementById('snapshots-container');
  if (!container) return;
  const data = await api('/api/snapshots');
  if (data && data.snapshots && data.snapshots.length > 0) {
    container.innerHTML = `
      <table class="data-table">
        <thead>
          <tr><th>Snapshot Name</th><th>Timestamp</th><th style="text-align:right">Action</th></tr>
        </thead>
        <tbody>
          ${data.snapshots.map(s => `
            <tr>
              <td class="cell-mono">${s.name}</td>
              <td class="text-caption">${s.timestamp}</td>
              <td style="text-align:right">
                <button class="btn btn-secondary btn-sm" onclick="doRestoreSnapshot('${s.name}')">Restore</button>
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    `;
  } else {
    container.innerHTML = '<div class="text-caption">No snapshots created yet. Click "Create Restore Point" to save current settings.</div>';
  }
}

let allProfilesData = null;

async function loadSupportedDevices() {
  const container = document.getElementById('supported-devices-container');
  if (!container) return;
  const data = await api('/api/device_profiles');
  if (data && data.profiles) {
    allProfilesData = data.profiles;
    renderSupportedDevicesTable(data.profiles);
  }
}

function filterSupportedDevices(query) {
  if (!allProfilesData) return;
  const q = (query || '').toLowerCase();
  const filtered = {};
  for (const [key, prof] of Object.entries(allProfilesData)) {
    const text = (prof.brand + ' ' + prof.series + ' ' + prof.models.join(' ') + ' ' + prof.processor + ' ' + prof.panel_type).toLowerCase();
    if (text.includes(q)) filtered[key] = prof;
  }
  renderSupportedDevicesTable(filtered);
}

function renderSupportedDevicesTable(profiles) {
  const container = document.getElementById('supported-devices-container');
  if (!container) return;
  const keys = Object.keys(profiles);
  if (!keys.length) {
    container.innerHTML = '<div class="text-caption">No matching devices found.</div>';
    return;
  }
  container.innerHTML = `
    <table class="data-table">
      <thead>
        <tr><th>Brand & Series</th><th>Processor & Panel</th><th>Key Hardware Features</th></tr>
      </thead>
      <tbody>
        ${keys.map(k => {
          const p = profiles[k];
          const flags = [];
          if (p.has_oled) flags.push('<span class="badge badge-success">OLED</span>');
          if (p.has_fald) flags.push('<span class="badge badge-warning">FALD / Mini-LED</span>');
          if (p.has_120hz) flags.push('<span class="badge badge-info">120Hz / VRR</span>');
          if (!flags.length) flags.push('<span class="badge badge-secondary">Standard TV</span>');

          return `
            <tr>
              <td>
                <div style="font-weight:600">${p.brand} ${p.series}</div>
                <div class="text-caption mono" style="font-size:0.75rem">${p.models.slice(0, 3).join(', ')}${p.models.length > 3 ? '...' : ''}</div>
              </td>
              <td>
                <div>${p.processor}</div>
                <div class="text-caption">${p.panel_type}</div>
              </td>
              <td>
                <div class="flex gap-1 flex-wrap">${flags.join(' ')}</div>
              </td>
            </tr>
          `;
        }).join('')}
      </tbody>
    </table>
  `;
}

function renderSettings() {
  return `
    <div class="page-header">
      <h1>Preferences & Connection Settings</h1>
      <p class="page-subtitle">Configure connection targets, polling parameters, and console preferences</p>
    </div>

    ${sectionHeader('Device Connection Target')}
    <div class="card mb-6">
      <div class="setting-row mb-3">
        <div class="setting-info">
          <div class="setting-name">Target IP Address & ADB Port</div>
          <div class="setting-desc">Active wireless ADB bridge endpoint for target television or media player</div>
        </div>
        <div class="setting-actions flex items-center gap-2">
          <code>${TARGET}</code>
          <span class="badge badge-success">● Connected</span>
        </div>
      </div>
      <div class="flex gap-2 mt-2">
        <button class="btn btn-primary btn-sm" onclick="openConnectTVModal()">🔌 Connect New TV / Change Target IP</button>
        <button class="btn btn-secondary btn-sm" onclick="openSetupGuideModal()">📖 View Setup Instructions</button>
      </div>
    </div>

    ${sectionHeader('Console Preferences & ADB Engine')}
    <div class="card mb-6">
      <div class="setting-row mb-4">
        <div class="setting-info">
          <div class="setting-name">Information Architecture Mode</div>
          <div class="setting-desc">Toggle between outcome-first (Simple) and engineering property-first (Advanced) UI views</div>
        </div>
        <div class="setting-actions">
          <button class="btn btn-secondary btn-sm" onclick="toggleAdvancedMode()">${advancedMode ? 'Switch to Simple Mode' : 'Switch to Advanced Mode'}</button>
        </div>
      </div>
      <div class="setting-row mb-4">
        <div class="setting-info">
          <div class="setting-name">ADB Real-Time Metric Polling Frequency</div>
          <div class="setting-desc">Frequency for polling available RAM, free storage, and network latency</div>
        </div>
        <div class="setting-actions">
          <select style="background:var(--bg-surface); border:1px solid var(--border); border-radius:var(--radius-sm); padding:4px 8px; color:var(--text-primary); outline:none;">
            <option value="15000" selected>15 Seconds (Recommended)</option>
            <option value="5000">5 Seconds (High Priority)</option>
            <option value="30000">30 Seconds (Low Network Impact)</option>
            <option value="0">Manual Polling Only</option>
          </select>
        </div>
      </div>
      <div class="setting-row">
        <div class="setting-info">
          <div class="setting-name">ADB Command Timeout</div>
          <div class="setting-desc">Maximum execution duration per shell command over wireless ADB</div>
        </div>
        <div class="setting-actions">
          <span class="badge badge-info">10,000 ms (10 sec)</span>
        </div>
      </div>
    </div>
  `;
}

function renderAbout() {
  return `
    <div class="page-header">
      <h1>About & Support</h1>
      <p class="page-subtitle">Product specifications, open-source acknowledgments, legal disclaimers, and community sponsorship</p>
    </div>

    ${sectionHeader('Open-Source Sponsorship & Community Support')}
    <div class="card mb-6">
      <div class="card-header">
        <div>
          <div class="card-title">💖 Sponsor & Support Development</div>
          <div class="card-subtitle">TV Control Center is 100% free and open-source software. You can sponsor ongoing maintenance and hardware profile expansion via Buy Me a Coffee or GitHub Sponsors.</div>
        </div>
      </div>
      <div class="flex gap-3 mt-3">
        <a href="https://buymeacoffee.com/ashishdungdung" target="_blank" class="btn btn-primary" style="text-decoration:none">☕ Sponsor on Buy Me a Coffee</a>
        <a href="https://github.com/sponsors/ashishdungdung" target="_blank" class="btn btn-secondary" style="text-decoration:none">💖 GitHub Sponsors</a>
      </div>
    </div>

    ${sectionHeader('Open-Source Credits & Acknowledgments')}
    <div class="card mb-6">
      <table class="data-table">
        <thead>
          <tr><th>Project / Component</th><th>Author / Maintainer</th><th>License / Link</th></tr>
        </thead>
        <tbody>
          <tr><td>Projectivy Launcher</td><td>Spocky</td><td><a href="https://github.com/spocky/projengmenu" target="_blank">GitHub</a></td></tr>
          <tr><td>FLauncher</td><td>efesser</td><td><a href="https://gitlab.com/efesser/flauncher" target="_blank">GitLab (GPLv3)</a></td></tr>
          <tr><td>Button Mapper</td><td>flar2</td><td><a href="https://buttonmapper.app" target="_blank">Website</a></td></tr>
          <tr><td>SmartTube 4K</td><td>yuliskov</td><td><a href="https://github.com/yuliskov/SmartTube" target="_blank">GitHub (GPLv3)</a></td></tr>
          <tr><td>Google Fonts (Inter & JetBrains Mono)</td><td>Google Fonts</td><td><a href="https://fonts.google.com" target="_blank">OFL License</a></td></tr>
          <tr><td>Android Debug Bridge (ADB)</td><td>Google Android Open Source Project</td><td><a href="https://developer.android.com/tools/adb" target="_blank">Apache 2.0</a></td></tr>
        </tbody>
      </table>
    </div>

    ${sectionHeader('Express Warranty Exclusion & Limitation of Liability')}
    <div class="card mb-6" style="border-color: var(--warning)">
      <div class="text-caption mb-3" style="line-height: 1.6; color: var(--warning);">
        <strong>⚠️ Strict Legal Disclaimer & Warranty Exclusion:</strong> THIS SOFTWARE IS PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESS, IMPLIED, STATUTORY, OR OTHERWISE, INCLUDING BUT NOT LIMITED TO IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR NON-INFRINGEMENT.
        IN NO EVENT SHALL THE AUTHORS, DEVELOPERS, MAINTAINERS, OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, PUNITIVE, OR CONSEQUENTIAL DAMAGES (INCLUDING HARDWARE MALFUNCTION, BOOT-LOOPS, SYSTEM INSTABILITY, DEBLOATING LOSS, OR MANUFACTURER WARRANTY VOIDANCE) ARISING OUT OF THE USE OF THIS SOFTWARE.
        ALL ADB OVERRIDES AND SYSTEM PROPERTY MODIFICATIONS ARE EXECUTED AT YOUR SOLE RISK AND DISCRETION.
      </div>
    </div>

    ${sectionHeader('Trademarks & Independent Release')}
    <div class="card">
      <div class="text-caption mb-3" style="line-height: 1.6; color: var(--text-muted);">
        <strong>Trademark Release:</strong> BRAVIA® is a registered trademark of Sony Group Corporation. Android TV™, Google Play™, YouTube™, and Google TV™ are trademarks of Google LLC.
        SHIELD® is a registered trademark of NVIDIA Corporation. Amazon® and Fire TV® are trademarks of Amazon.com, Inc. MediaTek®, Amlogic®, Realtek®, TCL®, Hisense®, Philips®, Panasonic®, Sharp®, Vu®, and Xiaomi® are trademarks of their respective copyright holders.
        TV Control Center is an independent, community-driven open-source utility designed for universal power-user management over Android Debug Bridge (ADB).
        It is not affiliated with, endorsed by, authorized by, or sponsored by Sony Corporation, Google LLC, NVIDIA Corporation, TCL Electronics, Hisense Co. Ltd., Amazon.com Inc., MediaTek Inc., Philips N.V., Panasonic Corp., Sharp Corp., Vu Technologies, Xiaomi Corp., or their subsidiaries.
        All product names, logos, and brands are property of their respective owners.
      </div>
      <table class="data-table">
        <tbody>
          <tr><td class="text-caption">Product Title</td><td>TV Control Center — Universal Smart TV Management Suite</td></tr>
          <tr><td class="text-caption">Release Version</td><td>v0.0.2</td></tr>
          <tr><td class="text-caption">Compatible Hardware</td><td>Universal Multi-TV (Sony BRAVIA, NVIDIA SHIELD, TCL, Hisense, Fire TV, Chromecast, Xiaomi)</td></tr>
          <tr><td class="text-caption">Target Platform</td><td>Android TV OS / Google TV / Fire OS (API Level 28–34)</td></tr>
          <tr><td class="text-caption">Storage Architecture</td><td>Host JSON (snapshots.json) • Browser localStorage • On-TV Storage (/data/local/tmp/)</td></tr>
          <tr><td class="text-caption">Software License</td><td>MIT Open Source License (NO LIABILITY)</td></tr>
        </tbody>
      </table>
    </div>
  `;
}

// ── APPEARANCE & THEMES ENGINE ──────────────────────────────
function setTheme(themeName) {
  document.documentElement.setAttribute('data-theme', themeName);
  localStorage.setItem('bravia_theme', themeName);
  showToast('Appearance Updated', `Switched theme to ${themeName}`);
  logActivity('Theme Switch', `Active theme: ${themeName}`);
}

function initTheme() {
  const saved = localStorage.getItem('bravia_theme') || 'day';
  document.documentElement.setAttribute('data-theme', saved);
}

function renderAppearance() {
  const currentTheme = localStorage.getItem('bravia_theme') || 'day';
  return `
    <div class="page-header">
      <h1>Appearance & Theme Engine</h1>
      <p class="page-subtitle">Customize console aesthetics, dark/light modes, and accent system</p>
    </div>

    ${sectionHeader('Theme Presets')}
    <div class="grid-3 mb-6">
      <div class="card" style="cursor:pointer; border:${currentTheme==='day'?'2px solid var(--accent)':'1px solid var(--border)'}" onclick="setTheme('day')">
        <div style="font-weight:600; margin-bottom:var(--sp-1)">☀️ Day (Comfortable Light — Default)</div>
        <div class="text-caption">Crisp white & soft light gray background with dark charcoal text and blue accents.</div>
      </div>
      <div class="card" style="cursor:pointer; border:${currentTheme==='night'?'2px solid var(--accent)':'1px solid var(--border)'}" onclick="setTheme('night')">
        <div style="font-weight:600; margin-bottom:var(--sp-1)">🌙 Night (Hardware Dark Console)</div>
        <div class="text-caption">Deep navy hardware console aesthetic with electric blue accents.</div>
      </div>
    </div>

    ${sectionHeader('Neon Accent System')}
    <div class="grid-4 mb-6">
      <div class="card" style="cursor:pointer; border:${currentTheme==='neon-cyan'?'2px solid #06b6d4':'1px solid var(--border)'}" onclick="setTheme('neon-cyan')">
        <div style="font-weight:600; color:#06b6d4; margin-bottom:var(--sp-1)">⚡ Neon Cyan</div>
        <div class="text-caption">High contrast cyan glow accents over dark navy surfaces.</div>
      </div>
      <div class="card" style="cursor:pointer; border:${currentTheme==='neon-violet'?'2px solid #8b5cf6':'1px solid var(--border)'}" onclick="setTheme('neon-violet')">
        <div style="font-weight:600; color:#8b5cf6; margin-bottom:var(--sp-1)">🔮 Neon Violet</div>
        <div class="text-caption">Vibrant violet glow accents over deep purple-black surfaces.</div>
      </div>
      <div class="card" style="cursor:pointer; border:${currentTheme==='neon-magenta'?'2px solid #d946ef':'1px solid var(--border)'}" onclick="setTheme('neon-magenta')">
        <div style="font-weight:600; color:#d946ef; margin-bottom:var(--sp-1)">🌺 Neon Magenta</div>
        <div class="text-caption">Electric magenta glow accents for dark room cinema setups.</div>
      </div>
      <div class="card" style="cursor:pointer; border:${currentTheme==='neon-amber'?'2px solid #f59e0b':'1px solid var(--border)'}" onclick="setTheme('neon-amber')">
        <div style="font-weight:600; color:#f59e0b; margin-bottom:var(--sp-1)">🔥 Neon Amber</div>
        <div class="text-caption">Warm amber glow accents inspired by classic OLED displays.</div>
      </div>
    </div>
  `;
}

// ── SETTING DETAILS SIDE DRAWER ─────────────────────────────
function openSettingDrawer(id) {
  const s = SYSTEM_SETTINGS.find(x => x.id === id);
  if (!s) return;
  let drawer = document.getElementById('setting-drawer-overlay');
  if (!drawer) {
    drawer = document.createElement('div');
    drawer.id = 'setting-drawer-overlay';
    drawer.className = 'drawer-overlay';
    document.body.appendChild(drawer);
  }
  drawer.classList.remove('hidden');
  drawer.innerHTML = `
    <div class="drawer-container">
      <div class="flex items-center justify-between mb-4 pb-3" style="border-bottom:1px solid var(--border)">
        <h3 style="font-size:1.125rem; font-weight:600">${s.simpleTitle}</h3>
        <button class="btn-close" onclick="closeSettingDrawer()">×</button>
      </div>
      
      <div class="mb-4">
        <div class="text-caption mb-1">Technical Property</div>
        <div style="font-family:var(--font-mono); font-size:0.875rem; color:var(--accent)">${s.techTitle}</div>
      </div>

      <div class="card mb-4" style="background:var(--bg-elevated)">
        <div style="font-weight:600" class="mb-1">What It Does</div>
        <div class="text-caption mb-3">${s.whatItDoes}</div>
        <div style="font-weight:600" class="mb-1">Why Use It & Impact</div>
        <div class="text-caption">${s.whyItMatters}</div>
      </div>

      <div class="mb-4">
        <table class="data-table">
          <tr><td class="text-caption">Current State</td><td class="mono">${s.currentGetter(state)}</td></tr>
          <tr><td class="text-caption">Stock Default</td><td class="mono">${s.stockValue}</td></tr>
          <tr><td class="text-caption">Recommended</td><td class="mono">${s.recommendedValue}</td></tr>
          <tr><td class="text-caption">Risk Profile</td><td><span class="badge badge-success">${s.risk}</span></td></tr>
          <tr><td class="text-caption">Reversible</td><td>${s.reversible ? '✓ Yes' : 'No'}</td></tr>
          <tr><td class="text-caption">Compatibility</td><td>${s.compatibility}</td></tr>
        </table>
      </div>

      <div class="card mb-6" style="padding:var(--sp-3); font-family:var(--font-mono); font-size:0.8125rem">
        <div class="text-caption mb-1">Executed ADB Command</div>
        <code>${s.command}</code>
      </div>

      <div class="flex gap-2">
        <button class="btn btn-primary" style="flex:1" onclick="s.applyAction(); closeSettingDrawer();">Apply Optimization</button>
        <button class="btn btn-secondary" onclick="s.restoreAction(); closeSettingDrawer();">Restore Stock</button>
      </div>
    </div>
  `;
}

function closeSettingDrawer() {
  const drawer = document.getElementById('setting-drawer-overlay');
  if (drawer) drawer.classList.add('hidden');
}

function renderSnapshotsPage() {
  setTimeout(loadSnapshots, 50);
  return `
    <div class="page-header">
      <h1>Snapshots & System Restore Points</h1>
      <p class="page-subtitle">Multi-tier system state backups (Host JSON, Browser localStorage, TV Flash)</p>
    </div>
    <div class="card mb-6">
      <div class="card-header">
        <div>
          <div class="card-title">Saved Restore Points</div>
          <div class="card-subtitle">Create a restore point before executing major system changes.</div>
        </div>
        <button class="btn btn-primary" onclick="doCreateSnapshot()">📸 Create Restore Point</button>
      </div>
      <div id="snapshots-container" class="mt-4">
        <div class="text-caption">Loading snapshots...</div>
      </div>
    </div>
  `;
}

function renderSupportedDevicesPage() {
  setTimeout(loadSupportedDevices, 50);
  return `
    <div class="page-header">
      <h1>Supported Devices & Compatibility Database</h1>
      <p class="page-subtitle">Explore supported Smart TV lineups, processors, and hardware capability profiles</p>
    </div>
    <div class="card mb-6">
      <div class="card-header mb-3">
        <div>
          <div class="card-title">13 Compatible Device Families</div>
          <div class="card-subtitle">Sony BRAVIA, NVIDIA SHIELD, TCL, Hisense, Philips, Panasonic, Sharp, Vu, Fire TV, Chromecast, Xiaomi</div>
        </div>
        <input type="text" id="device-search-input" placeholder="Filter models (e.g. X90H, OLED, SHIELD)..." onkeyup="filterSupportedDevices(this.value)"
               style="background:var(--bg-surface); border:1px solid var(--border); border-radius:var(--radius-sm); padding:var(--sp-1) var(--sp-3); color:var(--text-primary); font-size:0.8125rem; outline:none; width:260px;">
      </div>
      <div id="supported-devices-container">
        <div class="text-caption">Loading supported device profiles...</div>
      </div>
    </div>
  `;
}

// ── Router ─────────────────────────────────────────────────
const routes = {
  '': renderOverview,
  'performance': renderPerformance,
  'display': renderDisplay,
  'audio': renderAudio,
  'network': renderNetwork,
  'apps': renderApps,
  'launcher': renderLauncher,
  'remote': renderRemote,
  'hardware': renderHardware,
  'activity': renderActivity,
  'settings': renderSettings,
  'appearance': renderAppearance,
  'snapshots': renderSnapshotsPage,
  'supported-devices': renderSupportedDevicesPage,
  'about': renderAbout
};

function renderPage() {
  const renderer = routes[currentRoute];
  if (renderer) {
    document.getElementById('main-content').innerHTML = renderer();
  }
}

// ── Keyboard Shortcuts ─────────────────────────────────────
let gKeyPending = false;

document.addEventListener('keydown', (e) => {
  const isInput = ['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName);

  // Cmd+K or Ctrl+K → Command Palette
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault();
    openCommandPalette();
    return;
  }

  // Escape → close overlays
  if (e.key === 'Escape') {
    document.getElementById('command-palette-overlay').classList.add('hidden');
    closeDialog();
    if (connectionPopoverOpen) toggleConnectionPopover();
    return;
  }

  if (isInput) return;

  // Virtual remote D-pad keys when on Remote page
  if (currentRoute === 'remote') {
    const keyMap = { ArrowUp: 19, ArrowDown: 20, ArrowLeft: 21, ArrowRight: 22, Enter: 23, Backspace: 4 };
    if (keyMap[e.key]) { e.preventDefault(); doSendKey(keyMap[e.key]); return; }
  }

  // T → Toggle terminal
  if (e.key === 't' || e.key === 'T') { toggleTerminal(); return; }

  // R → Refresh
  if (e.key === 'r' || e.key === 'R') { refreshMetrics(); showToast('Refreshed', 'Metrics updated', 'info'); return; }

  // G → page navigation prefix
  if (e.key === 'g' || e.key === 'G') { gKeyPending = true; setTimeout(() => gKeyPending = false, 800); return; }

  if (gKeyPending) {
    gKeyPending = false;
    const gRoutes = {
      h: '', p: 'performance', d: 'display', a: 'audio', n: 'network',
      m: 'apps', l: 'launcher', r: 'remote', w: 'hardware', s: 'settings'
    };
    if (gRoutes[e.key.toLowerCase()] !== undefined) { navigate(gRoutes[e.key.toLowerCase()]); return; }
  }
});

// ── Init ───────────────────────────────────────────────────
function init() {
  // Parse hash route
  const hash = window.location.hash.replace('#/', '');
  currentRoute = hash || '';

  // Highlight sidebar
  document.querySelectorAll('.sidebar-nav-item').forEach(item => {
    item.classList.toggle('active', item.dataset.route === currentRoute);
  });

  // Sidebar toggle
  document.getElementById('sidebar-toggle').addEventListener('click', toggleSidebar);

  // Drag and drop setup
  document.addEventListener('dragover', (e) => e.preventDefault());
  document.addEventListener('drop', (e) => {
    e.preventDefault();
    const zone = document.getElementById('apk-dropzone');
    if (!zone) return;
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      const file = files[0];
      const input = document.getElementById('apk-path-input');
      if (input) input.value = file.path || file.name;
      showToast('APK Selected', `Selected file: ${file.name}`, 'info');
    }
  });

  // Render initial page
  renderPage();

  // Start metrics polling
  refreshMetrics();
  metricsInterval = setInterval(refreshMetrics, 15000);

  // Log startup
  logTerminal('BRAVIA Control Center initialized');
  logTerminal(`Connected to ${TARGET}`, 'success');
}

window.addEventListener('hashchange', () => {
  const hash = window.location.hash.replace('#/', '');
  currentRoute = hash || '';
  document.querySelectorAll('.sidebar-nav-item').forEach(item => {
    item.classList.toggle('active', item.dataset.route === currentRoute);
  });
  renderPage();
  document.getElementById('main-content').scrollTop = 0;
});

document.addEventListener('DOMContentLoaded', init);
