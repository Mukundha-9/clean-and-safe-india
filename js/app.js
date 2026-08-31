/* ==========================================================================
   Smart Civic Connect - Master Application Coordinator & Security Router
   ========================================================================== */

import { auth, SYSTEM_ACCOUNTS } from './auth.js';
import { db } from './db.js';
import { storage } from './storage.js';
import { mapManager } from './map.js';
import { iotSimulator } from './iot-simulator.js';
import { chatbot } from './chatbot.js';
import { ui } from './ui.js';

// State
let activeAuthDept = 'citizen';
let selectedDepartment = 'sanitation';
let selectedDeptName = 'Sanitation & Waste Management';
let selectedDeptIcon = '🏢';
let selectedCategory = 'garbage';
let selectedCategoryName = 'Urban Garbage Overflow';
let selectedCategoryIcon = '🗑️';

let reportPhotoBase64 = null;
let resolvePhotoBase64 = null;
let selectedLat = 17.0005;
let selectedLng = 81.8040;
let activeIssueIdForModal = null;

// =========================================================================
// AUTHENTICATION & PORTAL GATEWAY CONTROLLER
// =========================================================================
export function checkAuthAndRoute() {
  const isAuth = auth.isAuthenticated();
  const sessionDept = auth.getDepartment();

  const allViews = document.querySelectorAll('.master-dashboard-view');
  allViews.forEach(v => v.classList.remove('active'));

  const chatbotBtn = document.getElementById('chatbotTrigger');
  const chatbotWin = document.getElementById('chatbotWindow');

  if (!isAuth) {
    const authView = document.getElementById('authGatewayView');
    if (authView) authView.classList.add('active');
    if (chatbotBtn) chatbotBtn.style.display = 'none';
    if (chatbotWin) chatbotWin.classList.remove('active');
    window.scrollTo(0, 0);
    return;
  }

  // Show chatbot only when logged in
  if (chatbotBtn) chatbotBtn.style.display = 'flex';

  // Route strictly to authorized dashboard
  if (sessionDept === 'citizen') {
    const citizenView = document.getElementById('citizenMasterView');
    if (citizenView) citizenView.classList.add('active');
    ui.renderCitizenDashboard();
  } else if (sessionDept === 'municipal') {
    const munView = document.getElementById('municipalMasterView');
    if (munView) munView.classList.add('active');
    ui.renderMunicipalDashboard();
    setTimeout(() => {
      mapManager.initMainMap('gisMapContainer', db.getAllIssues());
    }, 150);
  } else if (sessionDept === 'food') {
    const foodView = document.getElementById('foodSafetyMasterView');
    if (foodView) foodView.classList.add('active');
    ui.renderFoodSafetyDashboard();
  } else {
    const authView = document.getElementById('authGatewayView');
    if (authView) authView.classList.add('active');
  }

  window.scrollTo(0, 0);
}

window.handleLogout = function() {
  auth.logout();
  checkAuthAndRoute();
  ui.showToast("Logged out securely. Session ended.", "info", "🔒");
};

// Switch Department Tab in Login Card
window.switchAuthDeptTab = function(dept) {
  activeAuthDept = dept;
  document.querySelectorAll('.auth-tab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.dept === dept);
  });

  const headerTitle = document.getElementById('authCardHeaderTitle');
  const headerDesc = document.getElementById('authCardHeaderDesc');
  const submitBtn = document.getElementById('authSubmitBtn');
  const demoEmailEl = document.getElementById('demoCredsEmail');
  const demoPassEl = document.getElementById('demoCredsPass');

  const deptAcc = SYSTEM_ACCOUNTS[dept];

  if (dept === 'citizen') {
    if (headerTitle) headerTitle.textContent = "Citizen Portal Login";
    if (headerDesc) headerDesc.textContent = "Report civic issues, track 48h SLA & earn citizen rewards";
    if (submitBtn) {
      submitBtn.className = "auth-btn-submit btn-dept-citizen";
      submitBtn.innerHTML = "<span>🚀</span> Login to Citizen Portal";
    }
  } else if (dept === 'municipal') {
    if (headerTitle) headerTitle.textContent = "Municipal & Electricity Official Login";
    if (headerDesc) headerDesc.textContent = "Administrative triage, vehicle dispatch & power SCADA control";
    if (submitBtn) {
      submitBtn.className = "auth-btn-submit btn-dept-municipal";
      submitBtn.innerHTML = "<span>🛡️</span> Access Municipal Command";
    }
  } else if (dept === 'food') {
    if (headerTitle) headerTitle.textContent = "Food Safety Authority (FSO) Login";
    if (headerDesc) headerDesc.textContent = "Official food hygiene inspections & digital QR certification";
    if (submitBtn) {
      submitBtn.className = "auth-btn-submit btn-dept-food";
      submitBtn.innerHTML = "<span>🍲</span> Access Food Safety Portal";
    }
  }

  if (demoEmailEl) demoEmailEl.textContent = deptAcc.email;
  if (demoPassEl) demoPassEl.textContent = deptAcc.password;
};

// 1-Click Helper to fill demo credentials
window.fillDemoCredentials = function() {
  const deptAcc = SYSTEM_ACCOUNTS[activeAuthDept];
  const emailInput = document.getElementById('authEmailInput');
  const passInput = document.getElementById('authPasswordInput');
  if (emailInput && passInput) {
    emailInput.value = deptAcc.email;
    passInput.value = deptAcc.password;
    ui.showToast(`Loaded official credentials for ${deptAcc.deptTitle}`, "info", "🔑");
  }
};

// =========================================================================
// SUB-TAB SWITCHERS
// =========================================================================

// Phase 1: Citizen Sub-tabs
window.switchCitizenSubTab = function(tabName) {
  document.querySelectorAll('.citizen-subview').forEach(v => v.style.display = 'none');
  document.querySelectorAll('.citizen-nav-btn').forEach(b => b.classList.remove('active'));

  const targetView = document.getElementById(`citizenTab_${tabName}`);
  const targetBtn = document.querySelector(`.citizen-nav-btn[data-tab="${tabName}"]`);

  if (targetView) targetView.style.display = 'block';
  if (targetBtn) targetBtn.classList.add('active');

  ui.renderCitizenDashboard();
};

// Phase 2: Municipal Sub-tabs
window.switchMunicipalSubTab = function(tabName) {
  document.querySelectorAll('.municipal-subview').forEach(v => v.style.display = 'none');
  document.querySelectorAll('.municipal-nav-btn').forEach(b => b.classList.remove('active'));

  const targetView = document.getElementById(`munTab_${tabName}`);
  const targetBtn = document.querySelector(`.municipal-nav-btn[data-tab="${tabName}"]`);

  if (targetView) targetView.style.display = 'block';
  if (targetBtn) targetBtn.classList.add('active');

  if (tabName === 'heatmap') {
    setTimeout(() => {
      mapManager.initMainMap('gisMapContainer', db.getAllIssues());
    }, 150);
  }

  ui.renderMunicipalDashboard();
};

// Phase 3: Food Safety Sub-tabs
window.switchFoodSubTab = function(tabName) {
  document.querySelectorAll('.food-subview').forEach(v => v.style.display = 'none');
  document.querySelectorAll('.food-nav-btn').forEach(b => b.classList.remove('active'));

  const targetView = document.getElementById(`foodTab_${tabName}`);
  const targetBtn = document.querySelector(`.food-nav-btn[data-tab="${tabName}"]`);

  if (targetView) targetView.style.display = 'block';
  if (targetBtn) targetBtn.classList.add('active');

  ui.renderFoodSafetyDashboard();
};

// =========================================================================
// MODALS & ISSUE REPORTING
// =========================================================================
window.openReportModal = function(preselectedDept = null) {
  if (preselectedDept) {
    selectedDepartment = preselectedDept;
    if (preselectedDept === 'electricity') {
      selectedDeptName = "Smart Electricity Department";
      selectedDeptIcon = "⚡";
    } else if (preselectedDept === 'food_safety') {
      selectedDeptName = "Food Safety Department";
      selectedDeptIcon = "🍲";
    } else {
      selectedDeptName = "Sanitation & Waste Management";
      selectedDeptIcon = "🏢";
    }
  }

  const deptSelect = document.getElementById('reportDeptSelect');
  if (deptSelect) {
    deptSelect.value = selectedDepartment;
    updateCategoryPickerForDept(selectedDepartment);
  }

  const modal = document.getElementById('reportIssueModal');
  if (modal) modal.classList.add('active');
  
  setTimeout(() => {
    mapManager.initPickerMap('locationPickerMap', [selectedLat, selectedLng], (lat, lng, address) => {
      selectedLat = lat;
      selectedLng = lng;
      const addrInput = document.getElementById('reportLocationInput');
      if (addrInput) addrInput.value = address;
    });
  }, 200);
};

function updateCategoryPickerForDept(dept) {
  const container = document.getElementById('reportCategoryPickerContainer');
  if (!container) return;

  let categories = [];
  if (dept === 'electricity') {
    categories = [
      { id: 'transformer_damage', name: 'Damaged Transformer / Sparking', icon: '⚡', severity: 'bulk' },
      { id: 'broken_pole', name: 'Broken Pole / Fallen Wire', icon: '🗼', severity: 'bulk' },
      { id: 'street_light', name: 'Street Light Failure (Dark Zone)', icon: '💡', severity: 'low' },
      { id: 'power_outage', name: 'Unexpected Local Power Outage', icon: '🔌', severity: 'medium' }
    ];
  } else if (dept === 'food_safety') {
    categories = [
      { id: 'food_hygiene', name: 'Unhygienic Food Stall / Prep', icon: '🍲', severity: 'bulk' },
      { id: 'food_spoilage', name: 'Rotten Food / Spoilage Odor', icon: '🥩', severity: 'bulk' },
      { id: 'open_drain', name: 'Open Sewage Drain near Stall', icon: '🚰', severity: 'medium' }
    ];
  } else {
    categories = [
      { id: 'garbage', name: 'Urban Garbage Accumulation', icon: '🗑️', severity: 'medium' },
      { id: 'pothole', name: 'Damaged Road / Pothole', icon: '🕳️', severity: 'bulk' },
      { id: 'water_leakage', name: 'Water Pipe Leakage / Drainage', icon: '🚰', severity: 'medium' },
      { id: 'littering', name: 'Roadside Littering', icon: '🧹', severity: 'low' }
    ];
  }

  selectedCategory = categories[0].id;
  selectedCategoryName = categories[0].name;
  selectedCategoryIcon = categories[0].icon;

  container.innerHTML = categories.map((c, idx) => `
    <div class="category-option-card ${idx === 0 ? 'selected' : ''}" data-category="${c.id}" data-name="${c.name}" data-icon="${c.icon}" data-severity="${c.severity}">
      <span class="cat-icon">${c.icon}</span>
      <span class="cat-name">${c.name}</span>
    </div>
  `).join('');

  container.querySelectorAll('.category-option-card').forEach(card => {
    card.addEventListener('click', () => {
      container.querySelectorAll('.category-option-card').forEach(x => x.classList.remove('selected'));
      card.classList.add('selected');
      selectedCategory = card.dataset.category;
      selectedCategoryName = card.dataset.name;
      selectedCategoryIcon = card.dataset.icon;
      
      const sevSelect = document.getElementById('reportSeveritySelect');
      if (sevSelect && card.dataset.severity) {
        sevSelect.value = card.dataset.severity;
      }
    });
  });
}

window.closeModal = function(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.remove('active');
};

window.viewIssueDetail = function(issueId) {
  const issue = db.getIssueById(issueId);
  if (!issue) return;
  activeIssueIdForModal = issueId;

  const modal = document.getElementById('issueDetailModal');
  const content = document.getElementById('issueDetailContent');
  if (!modal || !content) return;

  const isResolved = issue.status === 'resolved';
  const currentUser = auth.getUser() || { role: 'citizen' };

  content.innerHTML = `
    <div>
      <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
        <div>
          <span class="badge badge-${issue.status}">${issue.status.replace('_', ' ')}</span>
          <span class="cat-badge" style="margin-left: 0.4rem;">${issue.deptIcon} ${issue.deptName}</span>
          <span class="badge sev-${issue.severity}" style="margin-left: 0.4rem;">${issue.severity.toUpperCase()}</span>
        </div>
        <div style="font-family: var(--font-mono); font-size: 0.85rem; color: #38bdf8; font-weight: 700;">
          ${issue.id}
        </div>
      </div>

      <h2 style="font-size: 1.35rem; margin-bottom: 0.5rem;">${issue.title}</h2>
      <p style="font-size: 0.92rem; color: var(--text-muted); margin-bottom: 1.25rem;">${issue.description}</p>

      ${isResolved && issue.imageAfter ? `
        <div style="margin-bottom: 1.5rem;">
          <div style="font-weight: 700; font-size: 0.85rem; text-transform: uppercase; color: #059669; margin-bottom: 0.5rem;">
            📸 Resolution Proof: Before vs After Verification
          </div>
          <div class="compare-container" id="detailCompareSlider">
            <img src="${issue.imageAfter}" class="compare-img" alt="After resolution">
            <div class="compare-overlay" id="compareOverlay">
              <img src="${issue.imageBefore}" class="compare-img" alt="Before resolution">
            </div>
            <div class="compare-handle" id="compareHandle">↔</div>
            <span class="compare-badge-before">BEFORE</span>
            <span class="compare-badge-after">RESOLVED</span>
          </div>
        </div>
      ` : `
        <div style="margin-bottom: 1.5rem; border-radius: var(--radius-lg); overflow: hidden; max-height: 280px;">
          <img src="${issue.imageBefore}" style="width: 100%; height: 100%; object-fit: cover;" alt="${issue.title}">
        </div>
      `}

      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 0.75rem; background: var(--bg-card-subtle); padding: 1rem; border-radius: var(--radius-md); margin-bottom: 1.25rem; font-size: 0.82rem;">
        <div>📍 <strong>Location:</strong> ${issue.location}</div>
        <div>👤 <strong>Reported By:</strong> ${issue.reportedBy}</div>
        <div>⏱️ <strong>SLA Status:</strong> ${isResolved ? 'Resolved' : `${issue.slaHoursLeft}h remaining (48h Window)`}</div>
        <div>🚛 <strong>Allocated Unit:</strong> ${issue.recommendedResource}</div>
        <div>👷 <strong>Assigned Field Staff:</strong> ${issue.assignedWorker}</div>
        <div>🪙 <strong>Citizen Reward:</strong> ${issue.rewardIssued ? `✅ ₹30 (+50 Pts) Credited` : '₹30 (+50 Pts) upon resolution'}</div>
      </div>

      ${currentUser.role !== 'citizen' && !isResolved ? `
        <div style="background: #1e293b; color: white; padding: 1rem; border-radius: var(--radius-md); margin-bottom: 1.25rem;">
          <div style="font-weight: 700; font-size: 0.88rem; margin-bottom: 0.6rem; color: #38bdf8;">
            🛡️ Officer / Worker Actions (${currentUser.roleTitle || currentUser.role})
          </div>
          <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
            <button class="btn btn-sm btn-primary" onclick="window.closeModal('issueDetailModal'); window.openResolveModal('${issue.id}')">
              ✅ Upload Before/After Proof & Mark Cleaned
            </button>
            <button class="btn btn-sm btn-saffron" onclick="window.promptAssignProgress('${issue.id}')">
              🚛 Update Dispatch Status
            </button>
            <button class="btn btn-sm btn-danger" onclick="window.promptFine('${issue.id}')">
              ⚖️ Issue Violator Fine (₹150-₹500)
            </button>
          </div>
        </div>
      ` : ''}

      <div>
        <h4 style="margin-bottom: 0.6rem; font-size: 0.95rem;">Work Order Timeline & Updates</h4>
        <div style="display: flex; flex-direction: column; gap: 0.4rem; margin-bottom: 0.75rem;">
          ${(issue.comments || []).map(c => `
            <div style="background: white; border: 1px solid var(--border); padding: 0.5rem 0.75rem; border-radius: var(--radius-md); font-size: 0.82rem;">
              <div style="display: flex; justify-content: space-between; font-weight: 700; color: var(--text-main); margin-bottom: 2px;">
                <span>${c.author}</span>
                <span style="font-size: 0.72rem; color: var(--text-muted); font-weight: 400;">${c.time}</span>
              </div>
              <p style="margin: 0; color: var(--text-muted);">${c.text}</p>
            </div>
          `).join('')}
        </div>

        <div style="display: flex; gap: 0.5rem;">
          <input type="text" id="detailCommentInput" class="form-input" placeholder="Add an official update..." style="flex: 1; font-size: 0.85rem; padding: 0.5rem 0.75rem;">
          <button class="btn btn-secondary btn-sm" onclick="window.submitComment('${issue.id}')">Post Update</button>
        </div>
      </div>
    </div>
  `;

  modal.classList.add('active');

  setTimeout(() => {
    setupComparisonSlider();
  }, 100);
};

function setupComparisonSlider() {
  const container = document.getElementById('detailCompareSlider');
  const overlay = document.getElementById('compareOverlay');
  const handle = document.getElementById('compareHandle');
  if (!container || !overlay || !handle) return;

  let isDragging = false;
  const move = (clientX) => {
    const rect = container.getBoundingClientRect();
    let x = clientX - rect.left;
    x = Math.max(0, Math.min(x, rect.width));
    const percent = (x / rect.width) * 100;
    overlay.style.width = `${percent}%`;
    handle.style.left = `${percent}%`;
  };

  handle.addEventListener('mousedown', () => isDragging = true);
  window.addEventListener('mouseup', () => isDragging = false);
  window.addEventListener('mousemove', (e) => {
    if (isDragging) move(e.clientX);
  });

  handle.addEventListener('touchstart', () => isDragging = true);
  window.addEventListener('touchend', () => isDragging = false);
  window.addEventListener('touchmove', (e) => {
    if (isDragging && e.touches[0]) move(e.touches[0].clientX);
  });
}

window.openResolveModal = function(issueId) {
  activeIssueIdForModal = issueId;
  const issue = db.getIssueById(issueId);
  if (!issue) return;

  const titleEl = document.getElementById('resolveModalIssueTitle');
  if (titleEl) titleEl.textContent = `Resolving: #${issue.id} - ${issue.title} (${issue.deptName})`;

  const modal = document.getElementById('resolveIssueModal');
  if (modal) modal.classList.add('active');
};

window.toggleUpvote = function(issueId) {
  const updated = db.toggleUpvote(issueId);
  if (updated) {
    ui.renderCitizenDashboard();
    ui.renderMunicipalDashboard();
    ui.renderFoodSafetyDashboard();
    ui.showToast(`Updated upvote for #${updated.id}`, 'info', '👍');
  }
};

window.submitComment = function(issueId) {
  const input = document.getElementById('detailCommentInput');
  if (!input || !input.value.trim()) return;

  db.addComment(issueId, input.value.trim());
  input.value = '';
  window.viewIssueDetail(issueId);
  ui.showToast("Update logged successfully!", 'info', '💬');
};

window.promptAssignProgress = function(issueId) {
  const note = prompt("Enter field team dispatch details:", "Field crew dispatched with repair vehicle.");
  if (note) {
    db.assignProgress(issueId, note);
    window.viewIssueDetail(issueId);
    ui.renderMunicipalDashboard();
    ui.showToast("Dispatch status updated!", 'info', '🚛');
  }
};

window.promptFine = function(issueId) {
  const amount = prompt("Enter violator penalty fine (₹):", "500");
  if (amount && !isNaN(amount)) {
    db.imposeFine(issueId, parseInt(amount, 10));
    window.viewIssueDetail(issueId);
    ui.renderMunicipalDashboard();
    ui.showToast(`Penalty fine of ₹${amount} issued!`, 'error', '⚖️');
  }
};

window.viewDigitalCertificate = function(vendorId) {
  const vendors = db.getAllVendors();
  const vendor = vendors.find(v => v.id === vendorId);
  if (!vendor) return;

  const modal = document.getElementById('certificateModal');
  const card = document.getElementById('certificateCardContent');
  if (!modal || !card) return;

  card.innerHTML = `
    <div class="vendor-cert-card">
      <div class="cert-header">
        <div style="display: flex; align-items: center; gap: 0.75rem;">
          <div style="width: 50px; height: 50px; border-radius: 10px; background: #10b981; color: white; display: flex; align-items: center; justify-content: center; font-size: 1.8rem;">
            🍲
          </div>
          <div>
            <h3 style="font-size: 1.3rem; color: #0f172a; margin-bottom: 2px;">${vendor.name}</h3>
            <p style="font-size: 0.85rem; color: #059669; font-weight: 700;">DIGITAL FOOD HYGIENE & SAFETY CERTIFICATE</p>
          </div>
        </div>
        <div class="cert-stamp">
          <div class="cert-grade">${vendor.hygieneGrade}</div>
          <div>VERIFIED</div>
        </div>
      </div>

      <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; font-size: 0.9rem; margin-bottom: 1.5rem;">
        <div>👤 <strong>Proprietor:</strong> ${vendor.owner}</div>
        <div>📍 <strong>Location:</strong> ${vendor.location}</div>
        <div>📊 <strong>Hygiene Audit Score:</strong> ${vendor.score}</div>
        <div>📅 <strong>Certificate Validity:</strong> ${vendor.validTill}</div>
        <div>🔍 <strong>Certified By:</strong> ${vendor.inspectedBy}</div>
        <div>🆔 <strong>Digital Registration ID:</strong> ${vendor.id}</div>
      </div>

      <div style="background: #f0fdf4; border: 1px dashed #10b981; border-radius: var(--radius-md); padding: 1rem; display: flex; align-items: center; justify-content: space-between;">
        <div style="font-size: 0.82rem; color: #065f46;">
          🔒 <strong>QR Security Verification:</strong> Verified against Food Safety & Hygiene Standards.
        </div>
        <div style="background: white; padding: 6px; border-radius: 6px; box-shadow: var(--shadow-sm); font-family: monospace; font-size: 0.75rem; text-align: center; border: 1px solid var(--border);">
          [QR: ${vendor.id}]<br>SCAN TO VERIFY
        </div>
      </div>
    </div>
  `;

  modal.classList.add('active');
};

// =========================================================================
// INITIALIZATION
// =========================================================================
document.addEventListener('DOMContentLoaded', () => {
  iotSimulator.start();

  // Initial Auth Check & Routing
  checkAuthAndRoute();

  // Login Form Submission
  const authForm = document.getElementById('authLoginForm');
  if (authForm) {
    authForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const email = document.getElementById('authEmailInput').value;
      const pass = document.getElementById('authPasswordInput').value;

      try {
        const session = auth.login(activeAuthDept, email, pass);
        ui.showToast(`Welcome, ${session.user.name}! Access granted.`, 'reward', '🛡️');
        checkAuthAndRoute();
      } catch (err) {
        ui.showToast(err.message, 'error', '⚠️');
      }
    });
  }

  // DB Subscribe
  db.subscribe(() => {
    const sessionDept = auth.getDepartment();
    if (sessionDept === 'citizen') ui.renderCitizenDashboard();
    else if (sessionDept === 'municipal') ui.renderMunicipalDashboard();
    else if (sessionDept === 'food') ui.renderFoodSafetyDashboard();
  });

  ui.renderIoTView();
  ui.renderChatbot();

  // Citizen Filter Chips
  document.querySelectorAll('.citizen-filter-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      document.querySelectorAll('.citizen-filter-chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      ui.citizenFilter = chip.dataset.filter;
      ui.renderCitizenDashboard();
    });
  });

  // Citizen Search
  const searchInput = document.getElementById('citizenSearchInput');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      ui.searchQuery = e.target.value;
      ui.renderCitizenDashboard();
    });
  }

  // Department Select in Report Modal
  const deptSelect = document.getElementById('reportDeptSelect');
  if (deptSelect) {
    deptSelect.addEventListener('change', (e) => {
      selectedDepartment = e.target.value;
      if (selectedDepartment === 'electricity') {
        selectedDeptName = "Smart Electricity Department";
        selectedDeptIcon = "⚡";
      } else if (selectedDepartment === 'food_safety') {
        selectedDeptName = "Food Safety Department";
        selectedDeptIcon = "🍲";
      } else {
        selectedDeptName = "Sanitation & Waste Management";
        selectedDeptIcon = "🏢";
      }
      updateCategoryPickerForDept(selectedDepartment);
    });
  }

  // Photo Upload Handler for Report
  const fileInput = document.getElementById('reportPhotoInput');
  const uploadZone = document.getElementById('reportUploadZone');
  const previewBox = document.getElementById('reportPhotoPreview');
  const previewImg = document.getElementById('reportPreviewImg');
  const removePhotoBtn = document.getElementById('removePhotoBtn');

  if (fileInput && uploadZone) {
    uploadZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', async (e) => {
      if (e.target.files && e.target.files[0]) {
        try {
          reportPhotoBase64 = await storage.processImage(e.target.files[0]);
          if (previewImg && previewBox) {
            previewImg.src = reportPhotoBase64;
            previewBox.style.display = 'block';
            uploadZone.style.display = 'none';
          }
        } catch (err) {
          ui.showToast("Failed to process image: " + err.message, 'error', '⚠️');
        }
      }
    });
  }

  if (removePhotoBtn) {
    removePhotoBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      reportPhotoBase64 = null;
      if (fileInput) fileInput.value = '';
      if (previewBox) previewBox.style.display = 'none';
      if (uploadZone) uploadZone.style.display = 'block';
    });
  }

  // After Photo Upload for Resolve Modal
  const resolveFileInput = document.getElementById('resolvePhotoInput');
  const resolveUploadZone = document.getElementById('resolveUploadZone');
  const resolvePreviewBox = document.getElementById('resolvePhotoPreview');
  const resolvePreviewImg = document.getElementById('resolvePreviewImg');

  if (resolveFileInput && resolveUploadZone) {
    resolveUploadZone.addEventListener('click', () => resolveFileInput.click());
    resolveFileInput.addEventListener('change', async (e) => {
      if (e.target.files && e.target.files[0]) {
        try {
          resolvePhotoBase64 = await storage.processImage(e.target.files[0]);
          if (resolvePreviewImg && resolvePreviewBox) {
            resolvePreviewImg.src = resolvePhotoBase64;
            resolvePreviewBox.style.display = 'block';
            resolveUploadZone.style.display = 'none';
          }
        } catch (err) {
          ui.showToast("Failed to process image: " + err.message, 'error', '⚠️');
        }
      }
    });
  }

  // GPS Auto-detect button
  const gpsBtn = document.getElementById('btnDetectGps');
  if (gpsBtn) {
    gpsBtn.addEventListener('click', () => {
      gpsBtn.textContent = '⏳ Detecting...';
      mapManager.detectCurrentGPS((lat, lng, address) => {
        selectedLat = lat;
        selectedLng = lng;
        gpsBtn.textContent = '📍 GPS Detected';
        const addrInput = document.getElementById('reportLocationInput');
        if (addrInput) addrInput.value = address;
        ui.showToast("GPS Coordinates Locked & Tagged!", 'info', '🛰️');
      });
    });
  }

  // Report Form Submission
  const reportForm = document.getElementById('reportIssueForm');
  if (reportForm) {
    reportForm.addEventListener('submit', (e) => {
      e.preventDefault();

      const title = document.getElementById('reportTitleInput').value.trim();
      const desc = document.getElementById('reportDescInput').value.trim();
      const location = document.getElementById('reportLocationInput').value.trim();
      const severity = document.getElementById('reportSeveritySelect').value;
      const anonymous = document.getElementById('reportAnonymousCheck').checked;

      if (!title || !desc) {
        ui.showToast("Please provide both title and description.", 'error', '⚠️');
        return;
      }

      const newIssue = db.createIssue({
        department: selectedDepartment,
        deptName: selectedDeptName,
        deptIcon: selectedDeptIcon,
        title,
        description: desc,
        location: location || "Ward 12 Central Market Junction",
        category: selectedCategory,
        categoryName: selectedCategoryName,
        categoryIcon: selectedCategoryIcon,
        severity: severity,
        severityLabel: severity.toUpperCase(),
        lat: selectedLat,
        lng: selectedLng,
        anonymous: anonymous,
        imageBefore: reportPhotoBase64 || storage.getDefaultImageForCategory(selectedCategory)
      });

      reportForm.reset();
      reportPhotoBase64 = null;
      if (previewBox) previewBox.style.display = 'none';
      if (uploadZone) uploadZone.style.display = 'block';
      window.closeModal('reportIssueModal');

      ui.showToast(`Complaint #${newIssue.id} registered! 48h SLA activated.`, 'reward', '🎉');
      
      const sessionDept = auth.getDepartment();
      if (sessionDept === 'citizen') ui.renderCitizenDashboard();
      else if (sessionDept === 'municipal') ui.renderMunicipalDashboard();
      else if (sessionDept === 'food') ui.renderFoodSafetyDashboard();
    });
  }

  // Resolve Form Submission
  const resolveForm = document.getElementById('resolveIssueForm');
  if (resolveForm) {
    resolveForm.addEventListener('submit', (e) => {
      e.preventDefault();
      if (!activeIssueIdForModal) return;

      const notes = document.getElementById('resolveNotesInput').value.trim();
      const resolved = db.resolveIssue(
        activeIssueIdForModal,
        notes,
        resolvePhotoBase64 || "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=800&auto=format&fit=crop&q=80"
      );

      resolveForm.reset();
      resolvePhotoBase64 = null;
      if (resolvePreviewBox) resolvePreviewBox.style.display = 'none';
      if (resolveUploadZone) resolveUploadZone.style.display = 'block';
      window.closeModal('resolveIssueModal');

      ui.showToast(`Issue #${resolved.id} resolved! ₹30 reward & 50 points issued.`, 'reward', '💰');
      
      const sessionDept = auth.getDepartment();
      if (sessionDept === 'citizen') ui.renderCitizenDashboard();
      else if (sessionDept === 'municipal') ui.renderMunicipalDashboard();
      else if (sessionDept === 'food') ui.renderFoodSafetyDashboard();
    });
  }

  // Chatbot Toggle
  const chatTrigger = document.getElementById('chatbotTrigger');
  const chatWindow = document.getElementById('chatbotWindow');
  const chatClose = document.getElementById('chatbotClose');
  const chatInput = document.getElementById('chatbotInput');
  const chatSendBtn = document.getElementById('chatbotSendBtn');

  if (chatTrigger && chatWindow) {
    chatTrigger.addEventListener('click', () => {
      chatWindow.classList.toggle('active');
      if (chatWindow.classList.contains('active')) {
        ui.renderChatbot();
        if (chatInput) chatInput.focus();
      }
    });
  }

  if (chatClose && chatWindow) {
    chatClose.addEventListener('click', () => {
      chatWindow.classList.remove('active');
    });
  }

  const handleChatSend = () => {
    if (!chatInput || !chatInput.value.trim()) return;
    const userMsg = chatInput.value.trim();
    chatInput.value = '';
    chatbot.processUserMessage(userMsg);
    ui.renderChatbot();
  };

  if (chatSendBtn) chatSendBtn.addEventListener('click', handleChatSend);
  if (chatInput) {
    chatInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') handleChatSend();
    });
  }

  document.querySelectorAll('.quick-reply-pill').forEach(pill => {
    pill.addEventListener('click', () => {
      const q = pill.dataset.query;
      if (q) {
        chatbot.processUserMessage(q);
        ui.renderChatbot();
      }
    });
  });

  // IoT Sliders
  const gasSlider = document.getElementById('iotGasSlider');
  if (gasSlider) {
    gasSlider.addEventListener('input', (e) => {
      iotSimulator.setGasPpm(parseInt(e.target.value, 10));
    });
  }
});
