/* ==========================================================================
   Smart Civic Connect - UI Rendering Engine & State Controllers
   ========================================================================== */

import { auth, SYSTEM_ACCOUNTS } from './auth.js';
import { db } from './db.js';
import { mapManager } from './map.js';
import { iotSimulator } from './iot-simulator.js';
import { chatbot } from './chatbot.js';

class UIManager {
  constructor() {
    this.citizenFilter = 'all';
    this.searchQuery = '';
  }

  showToast(message, type = 'info', icon = '🔔') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type === 'reward' ? 'toast-reward' : type === 'error' ? 'toast-error' : ''}`;
    toast.innerHTML = `
      <div style="display: flex; align-items: center; gap: 0.75rem;">
        <span style="font-size: 1.25rem;">${icon}</span>
        <div>
          <div style="font-weight: 700; font-size: 0.9rem; color: #0f172a;">${message}</div>
        </div>
      </div>
      <button style="background: none; border: none; font-size: 1.1rem; cursor: pointer; color: #94a3b8;" onclick="this.parentElement.remove()">✕</button>
    `;

    container.appendChild(toast);
    setTimeout(() => {
      if (toast.parentElement) toast.remove();
    }, 4500);
  }

  // Create issue card HTML
  createCardHTML(issue) {
    const currentUser = auth.getUser();
    const isUpvoted = currentUser && (issue.upvotedBy || []).includes(currentUser.id || 'user-101');
    const isResolved = issue.status === 'resolved';
    const isEscalated = issue.status === 'escalated';
    
    let slaText = isResolved ? `✅ Resolved` : isEscalated ? `🚨 Escalated (>48h)` : `⏱️ ${issue.slaHoursLeft}h SLA left`;

    return `
      <div class="issue-card" onclick="window.viewIssueDetail('${issue.id}')">
        <div class="issue-card-media">
          <img src="${issue.imageBefore}" class="issue-card-img" alt="${issue.title}" loading="lazy">
          <div class="issue-floating-badges">
            <span class="badge badge-${issue.status}">
              ${issue.status.replace('_', ' ')}
            </span>
            <span class="issue-sla-pill">${slaText}</span>
          </div>
        </div>
        <div class="issue-card-body">
          <div class="issue-meta-row">
            <span class="cat-badge">${issue.deptIcon} ${issue.deptName}</span>
            <span class="badge sev-${issue.severity}">${issue.severity.toUpperCase()}</span>
          </div>
          <h3 class="issue-title">${issue.title}</h3>
          <p class="issue-desc">${issue.description}</p>
          <div class="issue-location-row">
            <span>📍</span>
            <span>${issue.location}</span>
          </div>
          <div class="issue-card-footer" onclick="event.stopPropagation()">
            <button class="upvote-btn ${isUpvoted ? 'upvoted' : ''}" onclick="window.toggleUpvote('${issue.id}')">
              <span>👍</span>
              <span>${issue.upvotes || 0}</span>
              <span>Me Too</span>
            </button>
            <div style="font-size: 0.8rem; color: var(--text-muted); display: flex; align-items: center; gap: 0.3rem;">
              <span>💬</span>
              <span>${(issue.comments || []).length} Updates</span>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  // =========================================================================
  // PHASE 1: CITIZEN DASHBOARD RENDERING
  // =========================================================================
  renderCitizenDashboard() {
    const user = auth.getUser();
    if (!user) return;
    const allIssues = db.getAllIssues();

    // Topbar Details
    const walletBalanceEl = document.getElementById('citizenNavWallet');
    if (walletBalanceEl) {
      walletBalanceEl.textContent = `₹${user.walletBalance || 0} (${user.rewardPoints || 0} Pts)`;
    }

    const userNameEl = document.getElementById('citizenTopName');
    const userAvatarEl = document.getElementById('citizenTopAvatar');
    if (userNameEl) userNameEl.textContent = user.name;
    if (userAvatarEl) userAvatarEl.textContent = user.avatar || "SR";

    // Filter Issues Feed
    const feedGrid = document.getElementById('citizenIssuesFeedGrid');
    if (feedGrid) {
      let filtered = allIssues;
      if (this.citizenFilter === 'sanitation') {
        filtered = filtered.filter(i => i.department === 'sanitation');
      } else if (this.citizenFilter === 'food') {
        filtered = filtered.filter(i => i.department === 'food_safety');
      } else if (this.citizenFilter === 'electricity') {
        filtered = filtered.filter(i => i.department === 'electricity');
      } else if (this.citizenFilter === 'my_reports') {
        filtered = filtered.filter(i => i.userId === user.id || i.reportedBy === user.name);
      } else if (this.citizenFilter === 'resolved') {
        filtered = filtered.filter(i => i.status === 'resolved');
      }

      if (this.searchQuery) {
        const q = this.searchQuery.toLowerCase();
        filtered = filtered.filter(i => 
          i.title.toLowerCase().includes(q) || 
          i.description.toLowerCase().includes(q) || 
          i.location.toLowerCase().includes(q) ||
          i.id.toLowerCase().includes(q)
        );
      }

      feedGrid.innerHTML = filtered.length ? filtered.map(i => this.createCardHTML(i)).join('') : '<p style="grid-column: 1/-1; text-align: center; padding: 2rem; background: white; border-radius: var(--radius-lg);">No matching reports found.</p>';
    }

    // Wallet
    const balEl = document.getElementById('citizenWalletBalance');
    const ptsEl = document.getElementById('citizenWalletPoints');
    if (balEl) balEl.textContent = `₹${user.walletBalance || 0}`;
    if (ptsEl) ptsEl.textContent = `${user.rewardPoints || 0} Pts`;

    const ledgerList = document.getElementById('citizenWalletLedger');
    if (ledgerList) {
      const history = db.loadFromStorage('clean_safe_rewards', []);
      ledgerList.innerHTML = history.map(tx => `
        <div style="display: flex; align-items: center; justify-content: space-between; padding: 0.85rem 0; border-bottom: 1px solid var(--border);">
          <div style="display: flex; align-items: center; gap: 0.75rem;">
            <div style="width: 36px; height: 36px; border-radius: 50%; background: #d1fae5; color: #047857; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; font-weight: 800;">
              🪙
            </div>
            <div>
              <div style="font-weight: 700; font-size: 0.9rem; color: var(--text-main);">${tx.title}</div>
              <div style="font-size: 0.78rem; color: var(--text-muted);">${tx.date} • ${tx.status}</div>
            </div>
          </div>
          <div style="font-size: 1.1rem; font-weight: 800; color: #10b981;">
            +₹${tx.amount} (+${tx.points || 50} pts)
          </div>
        </div>
      `).join('');
    }
  }

  // =========================================================================
  // PHASE 2: MUNICIPAL & ELECTRICITY COMMAND DASHBOARD RENDERING
  // =========================================================================
  renderMunicipalDashboard() {
    const user = auth.getUser();
    if (!user) return;
    const issues = db.getAllIssues();
    const metrics = db.getMetrics();
    const powerData = db.getPowerGridStatus();

    // Topbar
    const adminNameEl = document.getElementById('munTopAdminName');
    const adminBadgeEl = document.getElementById('munTopAdminBadge');
    if (adminNameEl) adminNameEl.textContent = user.name;
    if (adminBadgeEl) adminBadgeEl.textContent = user.officialId || "GOV-MUNC-SEC-012";

    // Summary Metrics
    const totalEl = document.getElementById('munTotalReports');
    const resolvedEl = document.getElementById('munResolvedReports');
    const rateEl = document.getElementById('munResolutionRate');
    const rewardsEl = document.getElementById('munRewardsPaid');
    const finesEl = document.getElementById('munFinesCollected');

    if (totalEl) totalEl.textContent = metrics.total;
    if (resolvedEl) resolvedEl.textContent = metrics.resolved;
    if (rateEl) rateEl.textContent = `${metrics.resolutionRate}%`;
    if (rewardsEl) rewardsEl.textContent = `₹${metrics.totalRewardsPaid}`;
    if (finesEl) finesEl.textContent = `₹${metrics.totalFinesCollected}`;

    // 48h SLA Queue Table
    const tableBody = document.getElementById('munIncidentTableBody');
    if (tableBody) {
      tableBody.innerHTML = issues.map(issue => {
        const isResolved = issue.status === 'resolved';
        const isEscalated = issue.status === 'escalated';
        const slaPercent = Math.max(0, Math.min(100, Math.round((issue.slaHoursLeft / 48) * 100)));
        const slaClass = isResolved ? 'sla-safe' : isEscalated || issue.slaHoursLeft < 10 ? 'sla-danger' : issue.slaHoursLeft < 24 ? 'sla-warning' : 'sla-safe';

        return `
          <tr>
            <td>
              <div style="font-family: var(--font-mono); font-weight: 700; color: #38bdf8;">${issue.id}</div>
              <div style="font-size: 0.72rem; color: var(--command-text-muted);">${new Date(issue.timestamp).toLocaleDateString()}</div>
            </td>
            <td>
              <div style="font-weight: 700; color: white;">${issue.title}</div>
              <div style="font-size: 0.75rem; color: var(--command-text-muted);">📍 ${issue.location}</div>
            </td>
            <td>
              <span class="cat-badge">${issue.deptIcon} ${issue.deptName}</span>
            </td>
            <td>
              <span class="badge sev-${issue.severity}">${issue.severity.toUpperCase()}</span>
            </td>
            <td>
              <div class="sla-progress-container" style="min-width: 100px;">
                <div class="sla-progress-bar">
                  <div class="sla-progress-fill ${slaClass}" style="width: ${isResolved ? 100 : slaPercent}%;"></div>
                </div>
                <span class="sla-text ${slaClass === 'sla-danger' ? 'text-danger' : ''}">
                  ${isResolved ? '✅ Resolved' : isEscalated ? '🚨 Escalated' : `${issue.slaHoursLeft}h left`}
                </span>
              </div>
            </td>
            <td>
              <div style="font-size: 0.8rem; color: #cbd5e1;">${issue.recommendedResource}</div>
            </td>
            <td>
              <div style="display: flex; gap: 0.4rem;">
                <button class="btn btn-sm btn-outline" style="color: white; border-color: var(--command-border);" onclick="window.viewIssueDetail('${issue.id}')">
                  Review
                </button>
                ${!isResolved ? `
                  <button class="btn btn-sm btn-primary" onclick="window.openResolveModal('${issue.id}')">
                    Resolve
                  </button>
                ` : `
                  <span style="font-size: 0.8rem; color: #10b981; font-weight: 700;">Resolved</span>
                `}
              </div>
            </td>
          </tr>
        `;
      }).join('');
    }

    // Power Outage Board
    const outageGrid = document.getElementById('munPowerOutageGrid');
    if (outageGrid) {
      outageGrid.innerHTML = (powerData.activeOutages || []).map(o => `
        <div class="outage-card ${o.status === 'UNSCHEDULED_OUTAGE' ? 'active-outage' : ''}">
          <div>
            <div class="outage-header">
              <span class="power-status-pill ${o.status === 'UNSCHEDULED_OUTAGE' ? 'power-status-outage' : 'power-status-online'}">
                ${o.status === 'UNSCHEDULED_OUTAGE' ? '⚡ OUTAGE ACTIVE' : '🔧 SCHEDULED WORK'}
              </span>
              <span class="outage-eta">${o.estimatedRestoration}</span>
            </div>
            <h3 style="font-size: 1.1rem; margin-bottom: 0.35rem;">${o.feeder}</h3>
            <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.5rem;"><strong>Area:</strong> ${o.ward} • <strong>Affected:</strong> ~${o.affectedConsumers} Consumers</p>
            <div style="background: #f8fafc; padding: 0.6rem; border-radius: var(--radius-sm); font-size: 0.82rem; margin-bottom: 0.75rem; border: 1px dashed var(--border);">
              <div>⚠️ <strong>Cause:</strong> ${o.reason}</div>
              <div>👷 <strong>Status:</strong> ${o.repairStage}</div>
            </div>
          </div>
          <div style="font-size: 0.8rem; color: var(--text-muted); display: flex; align-items: center; gap: 0.4rem;">
            <span>👮</span> <span>Lineman: <strong>${o.assignedLineman}</strong></span>
          </div>
        </div>
      `).join('');
    }

    // Worker Tasks
    const workerGrid = document.getElementById('munWorkerTasksGrid');
    if (workerGrid) {
      const pending = issues.filter(i => i.status !== 'resolved');
      workerGrid.innerHTML = pending.map(task => `
        <div class="lineman-ticket-card ${task.severity === 'bulk' ? 'lineman-high-risk' : ''}">
          <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
              <span class="badge badge-${task.status}">${task.status.toUpperCase()}</span>
              <span class="cat-badge" style="margin-left: 0.4rem;">${task.deptIcon} ${task.deptName}</span>
            </div>
            <div style="font-family: var(--font-mono); font-size: 0.82rem; font-weight: 700; color: #6366f1;">
              ${task.id}
            </div>
          </div>
          <h3 style="font-size: 1.15rem; color: var(--text-main);">${task.title}</h3>
          <p style="font-size: 0.85rem; color: var(--text-muted);">${task.description}</p>
          <div style="background: var(--bg-card-subtle); padding: 0.75rem; border-radius: var(--radius-md); font-size: 0.82rem;">
            <div>📍 <strong>Location:</strong> ${task.location}</div>
            <div>⏱️ <strong>SLA Remaining:</strong> ${task.slaHoursLeft} Hours</div>
            <div>🚛 <strong>Required Kit/Vehicle:</strong> ${task.recommendedResource}</div>
          </div>
          <div style="display: flex; gap: 0.5rem; margin-top: 0.5rem;">
            <button class="btn btn-sm btn-outline" style="flex: 1;" onclick="window.viewIssueDetail('${task.id}')">Review</button>
            <button class="btn btn-sm btn-primary" style="flex: 1;" onclick="window.openResolveModal('${task.id}')">Upload Proof & Resolve</button>
          </div>
        </div>
      `).join('');
    }
  }

  // =========================================================================
  // PHASE 3: FOOD SAFETY DEPARTMENT DASHBOARD RENDERING
  // =========================================================================
  renderFoodSafetyDashboard() {
    const user = auth.getUser();
    if (!user) return;

    // Topbar
    const fsoNameEl = document.getElementById('foodTopOfficerName');
    const fsoBadgeEl = document.getElementById('foodTopBadge');
    if (fsoNameEl) fsoNameEl.textContent = user.name;
    if (fsoBadgeEl) fsoBadgeEl.textContent = user.officialId || "FSSAI-INSP-2026-44";

    // Food Safety Issues
    const foodGrid = document.getElementById('foodDeptIssuesGrid');
    if (foodGrid) {
      const items = db.getIssuesByDepartment('food_safety');
      foodGrid.innerHTML = items.length ? items.map(i => this.createCardHTML(i)).join('') : '<p style="grid-column: 1/-1; text-align: center; padding: 2rem; background: white; border-radius: var(--radius-lg);">No active food safety violations reported.</p>';
    }

    // Certified Vendors Directory
    const vendorGrid = document.getElementById('foodDeptVendorsGrid');
    if (vendorGrid) {
      const vendors = db.getAllVendors();
      vendorGrid.innerHTML = vendors.map(vendor => `
        <div class="card" style="display: flex; flex-direction: column; justify-content: space-between;">
          <div>
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
              <div>
                <span class="badge ${vendor.hygieneGrade.includes('A') ? 'badge-resolved' : 'badge-pending'}">
                  ${vendor.status}
                </span>
                <h3 style="margin-top: 0.4rem; font-size: 1.15rem;">${vendor.name}</h3>
                <p style="font-size: 0.85rem; color: var(--text-muted);">Proprietor: ${vendor.owner} • 📍 ${vendor.location}</p>
              </div>
              <div style="text-align: center; background: #ecfdf5; border: 2px solid #10b981; border-radius: var(--radius-md); padding: 4px 10px;">
                <div style="font-size: 1.25rem; font-weight: 900; color: #047857;">${vendor.hygieneGrade}</div>
                <div style="font-size: 0.65rem; font-weight: 700; color: #065f46;">HYGIENE</div>
              </div>
            </div>
            <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1rem;">
              <div>• Audit Score: <strong>${vendor.score}</strong></div>
              <div>• Certificate Validity: <strong>${vendor.validTill}</strong></div>
              <div>• Inspected by: ${vendor.inspectedBy}</div>
            </div>
          </div>
          <button class="btn btn-outline btn-sm" style="width: 100%;" onclick="window.viewDigitalCertificate('${vendor.id}')">
            <span>📜</span> View & Print Digital Certificate
          </button>
        </div>
      `).join('');
    }
  }

  // IoT Sensor Telemetry Stream
  renderIoTView() {
    iotSimulator.subscribe((telemetry) => {
      const gasValEls = document.querySelectorAll('.iotGasValue');
      const gasStatusEls = document.querySelectorAll('.iotGasStatus');
      const gasLedEls = document.querySelectorAll('.iotGasLed');

      gasValEls.forEach(el => el.textContent = `${telemetry.mq135GasSensor.valuePpm} PPM`);
      gasStatusEls.forEach(el => el.textContent = telemetry.mq135GasSensor.spoilageRisk);
      gasLedEls.forEach(el => {
        el.className = `iot-status-led ${telemetry.mq135GasSensor.status === 'CRITICAL_SPOILAGE' ? 'led-red' : telemetry.mq135GasSensor.status === 'ELEVATED' ? 'led-amber' : 'led-green'}`;
      });

      const binValEls = document.querySelectorAll('.iotBinValue');
      const binStatusEls = document.querySelectorAll('.iotBinStatus');
      const binProgressEls = document.querySelectorAll('.iotBinProgress');

      binValEls.forEach(el => el.textContent = `${telemetry.ultrasonicBinLevel.fillPercentage}%`);
      binStatusEls.forEach(el => el.textContent = telemetry.ultrasonicBinLevel.alert);
      binProgressEls.forEach(el => el.style.width = `${telemetry.ultrasonicBinLevel.fillPercentage}%`);

      const weightValEls = document.querySelectorAll('.iotWeightValue');
      weightValEls.forEach(el => el.textContent = `${telemetry.loadCellWeight.weightKg} kg`);
    });
  }

  // Chatbot
  renderChatbot() {
    const msgContainer = document.getElementById('chatbotMessages');
    if (!msgContainer) return;

    const messages = chatbot.getMessages();
    msgContainer.innerHTML = messages.map(m => `
      <div class="chat-bubble ${m.sender}">
        ${m.text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>')}
      </div>
    `).join('');

    msgContainer.scrollTop = msgContainer.scrollHeight;
  }
}

export const ui = new UIManager();
