'use strict';

// ── Clock ────────────────────────────────────────────────────────────────────
(function startClock() {
  const el = document.getElementById('clock');
  if (!el) return;
  const tick = () => {
    const now = new Date();
    el.textContent = now.toLocaleString('hu-HU', {
      year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit', second: '2-digit'
    });
  };
  tick();
  setInterval(tick, 1000);
})();

// ── WebSocket ─────────────────────────────────────────────────────────────────
(function connectWS() {
  const wsUrl = `ws://${location.host}/ws`;
  let ws, reconnectTimer;

  const dot   = document.getElementById('ws-dot');
  const label = document.getElementById('ws-label');

  function setStatus(online) {
    if (!dot || !label) return;
    dot.className   = `dot ${online ? 'dot-online' : 'dot-offline'}`;
    label.textContent = online ? 'Kapcsolódva' : 'Lecsatlakozva';
  }

  function connect() {
    ws = new WebSocket(wsUrl);

    ws.onopen  = () => setStatus(true);
    ws.onclose = () => {
      setStatus(false);
      reconnectTimer = setTimeout(connect, 5000);
    };
    ws.onerror = () => ws.close();

    ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        if (data.type === 'rfid_event' && typeof window.onRFIDEvent === 'function') {
          window.onRFIDEvent(data);
        }
      } catch {}
    };
  }

  connect();
})();

// ── Toast helper ──────────────────────────────────────────────────────────────
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const id = `toast-${Date.now()}`;
  const iconMap = { success: 'check-circle-fill', danger: 'x-circle-fill',
                    warning: 'exclamation-triangle-fill', info: 'info-circle-fill' };
  const icon = iconMap[type] || 'info-circle-fill';
  const html = `
    <div id="${id}" class="toast align-items-center text-bg-${type} border-0" role="alert" aria-live="polite">
      <div class="d-flex">
        <div class="toast-body d-flex align-items-center gap-2">
          <i class="bi bi-${icon}"></i>${message}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
      </div>
    </div>`;
  container.insertAdjacentHTML('beforeend', html);
  const el = document.getElementById(id);
  const toast = new bootstrap.Toast(el, { delay: 4000 });
  toast.show();
  el.addEventListener('hidden.bs.toast', () => el.remove());
}
