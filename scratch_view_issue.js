window.viewIssueDetail = function(issueId) {
    const issue = db.getIssueById(issueId);
    if (!issue) return;
    activeIssueIdForModal = issueId;

    const modal = document.getElementById('issueDetailModal');
    const content = document.getElementById('issueDetailContent');
    if (!modal || !content) return;

    const isResolved = issue.status === 'resolved';
    const isEscalated = issue.status === 'escalated' || issue.isSlaBreached;
    const reportedTimeStr = formatReportDateTime(issue.timestamp);
    const resolvedTs = isResolved ? getRealisticResolvedTimestamp(issue) : null;
    const resolvedTimeStr = isResolved ? formatReportDateTime(resolvedTs) : null;
    const turnaroundStr = isResolved ? calculateSlaTurnaround(issue.timestamp, resolvedTs, issue) : null;

    const verifiedOfficer = issue.verifiedByOfficer || 'Consultant Officer K. Mukundha (GOV-MUNC-SEC-012)';
    const verifiedTimeStr = formatReportDateTime(issue.verifiedTimestamp || (issue.timestamp + 18 * 60 * 1000));
    const assignedWorker = issue.assignedWorker || 'Municipal Rapid Squad';
    const assignedTimeStr = formatReportDateTime(issue.assignedTimestamp || (issue.timestamp + 45 * 60 * 1000));
    const workerStatus = issue.workerStatus || (isResolved ? 'Completed & Verified On-Site' : isEscalated ? 'Delayed (>48h) — Auto-Forwarded' : 'Active On-Site Cleaning & Hazard Removal');

    content.innerHTML = `
      <div>
        <!-- Top Status & SLA Banner -->
        <div class="tracker-header-card">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 0.75rem;">
            <div>
              <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.35rem;">
                <span class="cat-badge">${issue.deptIcon} ${issue.deptName}</span>
                <span class="badge badge-${issue.status}">${issue.status.replace('_', ' ').toUpperCase()}</span>
                <span class="badge sev-${issue.severity}">${issue.severity.toUpperCase()}</span>
              </div>
              <h2 style="font-size: 1.35rem; color: white; margin: 0.2rem 0 0.4rem;">${issue.title}</h2>
              <div style="font-size: 0.85rem; color: #94a3b8; display: flex; align-items: center; gap: 0.4rem;">
                <span>📍</span> <span>${issue.location}</span>
              </div>
            </div>
            <div style="text-align: right;">
              <div style="font-family: var(--font-mono); font-size: 1.05rem; color: #38bdf8; font-weight: 800;">${issue.id}</div>
              <div style="margin-top: 0.5rem;">
                ${isResolved ? `
                  <div class="sla-live-badge sla-resolved">
                    <span>✅</span> RESOLVED WITHIN 48H SLA (${turnaroundStr})
                  </div>
                ` : isEscalated ? `
                  <div class="sla-live-badge sla-breached">
                    <span>🚨</span> 48H SLA BREACHED — FORWARDED TO MUNICIPAL COMMISSIONER
                  </div>
                ` : `
                  <div class="sla-live-badge sla-active">
                    <span class="gps-pulse-dot" style="background: #38bdf8; box-shadow: 0 0 8px #38bdf8;"></span>
                    <span class="sla-live-ticker" data-deadline="${issue.slaDeadline || (issue.timestamp + 48 * 3600 * 1000)}">⏱️ 48H SLA ACTIVE: ${issue.slaHoursLeft}H LEFT (Due ${deadlineTimeStr})</span>
                  </div>
                `}
              </div>
            </div>
          </div>

          <!-- Metadata Grid with Exact Timestamps -->
          <div class="tracker-meta-grid">
            <div class="tracker-meta-item">
              📅 Reported Date & Time:
              <strong>${reportedTimeStr}</strong>
            </div>
            <div class="tracker-meta-item">
              ⏳ 48-Hour Resolution Deadline:
              <strong>${deadlineTimeStr}</strong>
            </div>
            <div class="tracker-meta-item">
              ${isResolved ? '✅ Verified Resolution Date & Time:' : '⏱️ Status Countdown:'}
              <strong style="color: ${isResolved ? '#34d399' : isEscalated ? '#f87171' : '#38bdf8'};">
                ${isResolved ? `${resolvedTimeStr} (${turnaroundStr})` : isEscalated ? '🚨 Auto-Escalated to Commissioner' : `${issue.slaHoursLeft} Hours Remaining`}
              </strong>
            </div>
            <div class="tracker-meta-item">
              🪙 Civic Incentive Standing:
              <strong style="color: #facc15;">+50 Civic Credits (Gold Streak)</strong>
            </div>
          </div>
        </div>

        <!-- Before & After Photographic Evidence -->
        <div style="margin-bottom: 1.5rem;">
          <div style="font-size: 0.85rem; font-weight: 800; color: #38bdf8; margin-bottom: 0.6rem; display: flex; align-items: center; gap: 0.4rem;">
            <span>📸</span> GEOTAGGED PHOTOGRAPHIC AUDIT RECORD
          </div>
          <div style="display: grid; grid-template-columns: ${isResolved ? 'repeat(2, 1fr)' : '1fr'}; gap: 1rem;">
            <div style="border-radius: var(--radius-lg); overflow: hidden; max-height: 230px; border: 1px solid var(--border); position: relative;">
              <img src="${issue.imageBefore}" style="width: 100%; height: 100%; object-fit: cover;" alt="Before">
              <span style="position: absolute; bottom: 8px; left: 8px; background: rgba(0,0,0,0.85); color: #f43f5e; font-weight: 800; font-size: 0.72rem; padding: 3px 8px; border-radius: 4px; border: 1px solid rgba(244, 63, 94, 0.4);">
                1. REPORTED HAZARD (PROOF ATTACHED • ${reportedTimeStr})
              </span>
            </div>
            ${isResolved ? `
              <div style="border-radius: var(--radius-lg); overflow: hidden; max-height: 230px; border: 1px solid #10b981; position: relative;">
                <img src="${issue.imageAfter || 'https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=800&auto=format&fit=crop&q=80'}" style="width: 100%; height: 100%; object-fit: cover;" alt="After">
                <span style="position: absolute; bottom: 8px; left: 8px; background: rgba(0,0,0,0.85); color: #34d399; font-weight: 800; font-size: 0.72rem; padding: 3px 8px; border-radius: 4px; border: 1px solid rgba(16, 185, 129, 0.4);">
                  2. CLEANED & RESOLVED (VERIFIED ON ${resolvedTimeStr})
                </span>
              </div>
            ` : ''}
          </div>
        </div>

        <!-- 5-Stage Live Order-Style Tracking Stepper -->
        <div>
          <div style="font-size: 0.95rem; font-weight: 800; color: white; margin-bottom: 1rem; display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
              <span>📦</span> <span>Live 48-Hour SLA Grievance Tracking Timeline</span>
            </div>
            <div style="font-size: 0.75rem; color: #94a3b8;">Standard 48-Hour SLA Window</div>
          </div>

          <div class="order-tracking-timeline">
            <!-- Stage 1: Grievance Initiated -->
            <div class="timeline-step completed">
              <div class="timeline-node">📝</div>
              <div class="timeline-content">
                <div class="step-header-row">
                  <div class="step-title">Stage 1: Grievance Initiated by Citizen</div>
                  <div class="step-time-pill">${reportedTimeStr}</div>
                </div>
                <div class="step-desc">
                  Complaint logged by <strong>${issue.reportedBy || 'KRISH'}</strong> with GPS geotagged coordinates (<code>${issue.lat || 17.0010}° N, ${issue.lng || 81.8045}° E</code>) and initial photographic evidence.
                </div>
                <div class="step-sub-meta">
                  <span>📍 ${issue.location}</span>
                  <span>👤 Reporter ID: ${issue.userId || 'user-101'}</span>
                  <span>📷 Photo Evidence: Verified</span>
                </div>
              </div>
            </div>

            <!-- Stage 2: Consultant Officer Verification & SLA Start -->
            <div class="timeline-step completed">
              <div class="timeline-node">🔍</div>
              <div class="timeline-content">
                <div class="step-header-row">
                  <div class="step-title">Stage 2: Verification by Consultant Officer & SLA Activation</div>
                  <div class="step-time-pill">${verifiedTimeStr}</div>
                </div>
                <div class="step-desc">
                  Grievance inspected and validated by <strong>${verifiedOfficer}</strong>. Severity level classified as <strong>${issue.severity.toUpperCase()}</strong>. Official <strong>48-Hour SLA Countdown Clock</strong> activated.
                </div>
                <div class="step-sub-meta">
                  <span>🛡️ Verified By: ${verifiedOfficer}</span>
                  <span>⏱️ 48h SLA Deadline: ${deadlineTimeStr}</span>
                  <span>📂 Division: ${issue.deptName}</span>
                </div>
              </div>
            </div>

            <!-- Stage 3: Squad & Vehicle Allocation -->
            <div class="timeline-step ${isResolved || issue.status === 'in_progress' ? 'completed' : 'active'}">
              <div class="timeline-node">🚛</div>
              <div class="timeline-content">
                <div class="step-header-row">
                  <div class="step-title">Stage 3: Rapid Response Squad & Fleet Allocation</div>
                  <div class="step-time-pill">${assignedTimeStr}</div>
                </div>
                <div class="step-desc">
                  Work order assigned to <strong>${assignedWorker}</strong>. Automated vehicle dispatch allocated <strong>${issue.recommendedResource}</strong> with digital routing.
                </div>
                <div class="step-sub-meta">
                  <span>👷 Assigned Squad: ${assignedWorker}</span>
                  <span>🚚 Resource: ${issue.recommendedResource}</span>
                  <span>📡 Telemetry: GPS Connected</span>
                </div>
              </div>
            </div>

            <!-- Stage 4: On-Site Work Execution -->
            <div class="timeline-step ${isResolved ? 'completed' : isEscalated ? 'breached' : 'active'}">
              <div class="timeline-node">🛠️</div>
              <div class="timeline-content">
                <div class="step-header-row">
                  <div class="step-title">Stage 4: On-Site Field Remediation & Worker Status</div>
                  <div class="step-time-pill">${isResolved ? (issue.resolvedTimestamp ? formatReportDateTime(issue.resolvedTimestamp - 1800000) : formatReportDateTime(issue.timestamp + 3600000 * 20)) : formatReportDateTime(Date.now() - 1800000)}</div>
                </div>
                <div class="step-desc">
                  Rapid field crew deployed on ground conducting cleaning, electrical repairs, or food safety audit.
                </div>
                <div style="margin: 0.5rem 0;">
                  <span style="font-size: 0.78rem; font-weight: 800; padding: 3px 10px; border-radius: 4px; ${isResolved ? 'background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4);' : isEscalated ? 'background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4);' : 'background: rgba(2, 132, 199, 0.2); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4);'}">
                    ${isResolved ? '✅ Field Execution Completed' : isEscalated ? '🚨 SLA Delay: Auto-Forwarded to Commissioner' : `🟢 Worker Live Status: ${workerStatus}`}
                  </span>
                </div>
                <div class="step-sub-meta">
                  <span>👷 Field Lead: ${assignedWorker}</span>
                  <span>📋 Protocol: Swachh Bharat & SCADA Quality Standards</span>
                </div>
              </div>
            </div>

            <!-- Stage 5: Final Resolution OR SLA Auto-Forwarded to Commissioner -->
            ${isResolved ? `
              <div class="timeline-step completed">
                <div class="timeline-node">🎉</div>
                <div class="timeline-content">
                  <div class="step-header-row">
                    <div class="step-title" style="color: #34d399;">Stage 5: Verified Resolution & Civic Reward Issued</div>
                    <div class="step-time-pill" style="color: #34d399; border-color: rgba(16, 185, 129, 0.4); background: rgba(16, 185, 129, 0.1);">${resolvedTimeStr}</div>
                  </div>
                  <div class="step-desc">
                    Field resolution certified and approved! Before/After photographic inspection verified. Turnaround time: <strong>${turnaroundStr}</strong> (Resolved well within 48-Hour SLA).
                  </div>
                  <div class="step-sub-meta">
                    <span style="color: #facc15; font-weight: 700;">🪙 +50 Civic Credits Credited to ${issue.reportedBy || 'Citizen'}</span>
                    <span style="color: #34d399;">📜 Participation Certificate Updated</span>
                    <span>✅ Status: CLOSED & ARCHIVED</span>
                  </div>
                </div>
              </div>
            ` : isEscalated ? `
              <div class="timeline-step breached">
                <div class="timeline-node">🚨</div>
                <div class="timeline-content">
                  <div class="step-header-row">
                    <div class="step-title" style="color: #f87171;">Stage 5: 🚨 SLA Breached (>48h) — Forwarded to Municipal Commissioner</div>
                    <div class="step-time-pill" style="color: #f87171; border-color: rgba(239, 68, 68, 0.4); background: rgba(239, 68, 68, 0.1);">${deadlineTimeStr}</div>
                  </div>
                  <div class="step-desc" style="color: #fecdd3;">
                    <strong>AUTOMATIC SLA ESCALATION:</strong> Field resolution was not completed within the mandatory 48-Hour SLA period. The ticket has been automatically forwarded to the <strong>Zonal Municipal Commissioner (Dr. Mahesh Babu) & Department Heads</strong> with Critical Red Priority for immediate direct intervention.
                  </div>
                  <div class="step-sub-meta">
                    <span style="color: #f87171; font-weight: 700;">🚨 Forwarded To: Municipal Commissioner Red Desk</span>
                    <span style="color: #facc15;">⚡ Priority: CRITICAL LEVEL 1</span>
                    <span>⚠️ Escalation Reason: SLA Timer Expired</span>
                  </div>
                </div>
              </div>
            ` : `
              <div class="timeline-step">
                <div class="timeline-node">⏳</div>
                <div class="timeline-content">
                  <div class="step-header-row">
                    <div class="step-title" style="color: #94a3b8;">Stage 5: Final Resolution & Reward (+50 Civic Credits)</div>
                    <div class="step-time-pill">Expected by ${deadlineTimeStr}</div>
                  </div>
                  <div class="step-desc">
                    In progress within the guaranteed 48-Hour SLA window. If not resolved before the SLA deadline, the grievance will be automatically forwarded to the Zonal Municipal Commissioner.
                  </div>
                  <div class="step-sub-meta">
                    <span>🪙 Reward: +50 Civic Credits upon completion</span>
                    <span>⏱️ Window: 48h Resolution Guarantee</span>
                  </div>
                </div>
              </div>
            `}
          </div>

          <!-- Community Comments & Live Citizen Discussion -->
          <div style="margin-top: 1.5rem; background: rgba(255, 255, 255, 0.02); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 1.1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.85rem;">
              <h4 style="color: white; font-size: 1.05rem; margin: 0; display: flex; align-items: center; gap: 0.5rem;">
                <span>💬</span> Community Discussion & Officer Remarks (${(issue.comments || []).length})
              </h4>
            </div>

            <!-- Existing Comments List -->
            <div class="comments-list" style="display: flex; flex-direction: column; gap: 0.65rem; max-height: 240px; overflow-y: auto; margin-bottom: 1rem; padding-right: 4px;">
              ${(issue.comments && issue.comments.length > 0) ? issue.comments.map(c => `
                <div style="background: rgba(255, 255, 255, 0.04); border-left: 3px solid #38bdf8; border-radius: 6px; padding: 0.6rem 0.85rem; font-size: 0.82rem;">
                  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
                    <strong style="color: #38bdf8;">${c.author || 'Civic Guardian'}</strong>
                    <span style="font-size: 0.72rem; color: #94a3b8;">${c.time || 'Recently'}</span>
                  </div>
                  <div style="color: #e2e8f0; line-height: 1.45;">${c.text}</div>
                </div>
              `).join('') : `
                <div style="text-align: center; color: #64748b; font-size: 0.82rem; padding: 1rem;">No remarks yet. Be the first citizen to leave a comment!</div>
              `}
            </div>

            <!-- Add Comment Input Box -->
            <div style="display: flex; gap: 0.5rem; align-items: center;">
              <input type="text" id="issueCommentInput" class="form-input" placeholder="Add an official remark, update, or question..." style="flex: 1; font-size: 0.85rem; padding: 0.6rem 0.85rem;" onkeydown="if(event.key === 'Enter'){ window.submitComment('${issue.id}'); }">
              <button type="button" class="btn btn-sm btn-primary" onclick="window.submitComment('${issue.id}')" style="white-space: nowrap; padding: 0.6rem 1rem;">
                <span>🚀</span> Post
              </button>
            </div>
          </div>
        </div>
      </div>
    `;

    window.openModal('issueDetailModal');
  };

  