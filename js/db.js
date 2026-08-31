/* ==========================================================================
   Smart Civic Connect - Database & Data Access Layer
   CRUD across Sanitation, Food Safety, and Smart Electricity Departments
   ========================================================================== */

import { INITIAL_DATA } from './config.js';
import { auth } from './auth.js';

const STORAGE_ISSUES_KEY = 'clean_safe_issues';
const STORAGE_VENDORS_KEY = 'clean_safe_vendors';
const STORAGE_REWARDS_KEY = 'clean_safe_rewards';
const STORAGE_CCTV_KEY = 'clean_safe_cctv';
const STORAGE_SUPPORT_KEY = 'clean_safe_support';
const STORAGE_POWER_KEY = 'clean_safe_power';

class DatabaseManager {
  constructor() {
    this.issues = this.loadFromStorage(STORAGE_ISSUES_KEY, INITIAL_DATA.issues);
    this.vendors = this.loadFromStorage(STORAGE_VENDORS_KEY, INITIAL_DATA.certifiedVendors);
    this.rewards = this.loadFromStorage(STORAGE_REWARDS_KEY, INITIAL_DATA.rewardsHistory);
    this.cctvIncidents = this.loadFromStorage(STORAGE_CCTV_KEY, INITIAL_DATA.cctvIncidents);
    this.supportTickets = this.loadFromStorage(STORAGE_SUPPORT_KEY, INITIAL_DATA.supportTickets);
    this.powerGridStatus = this.loadFromStorage(STORAGE_POWER_KEY, INITIAL_DATA.powerGridStatus);
    this.listeners = [];

    this.updateSLAStatuses();
  }

  loadFromStorage(key, fallback) {
    try {
      const data = localStorage.getItem(key);
      if (data) return JSON.parse(data);
    } catch (e) {
      console.warn(`Storage load error for ${key}:`, e);
    }
    return JSON.parse(JSON.stringify(fallback));
  }

  saveToStorage(key, data) {
    try {
      localStorage.setItem(key, JSON.stringify(data));
    } catch (e) {
      console.warn(`Storage save error for ${key}:`, e);
    }
    this.notify();
  }

  subscribe(callback) {
    this.listeners.push(callback);
    callback(this.getAllIssues());
  }

  notify() {
    const all = this.getAllIssues();
    this.listeners.forEach(cb => cb(all));
  }

  // --- Issues / Complaints CRUD ---
  getAllIssues() {
    return [...this.issues];
  }

  getIssueById(id) {
    return this.issues.find(iss => iss.id === id);
  }

  getIssuesByDepartment(department) {
    return this.issues.filter(i => i.department === department);
  }

  // Resource Allocation
  getResourceForCategory(department, category, severity) {
    if (department === 'electricity') {
      if (category === 'transformer_damage' || severity === 'bulk') {
        return { resource: "Emergency Lineman Squad & Boom Lift Truck", icon: "⚡" };
      }
      return { resource: "Street Light Maintenance Lineman", icon: "💡" };
    }

    if (department === 'food_safety') {
      return { resource: "Food Safety Inspection Officer", icon: "🔍" };
    }

    // Sanitation Department
    switch (severity) {
      case 'low':
        return { resource: "Sanitation Worker with Pushcart", icon: "🛒" };
      case 'medium':
        return { resource: "Garbage Collection Vehicle", icon: "🚛" };
      case 'bulk':
      default:
        return { resource: "Road Repair & Heavy Compactor Machine", icon: "🚜" };
    }
  }

  // Create Issue Report
  createIssue(issueData) {
    const user = auth.getUser();
    const issueCount = this.issues.length + 128;
    const newId = `ISS-2026-${String(issueCount).padStart(5, '0')}`;
    
    const resourceAlloc = this.getResourceForCategory(issueData.department, issueData.category, issueData.severity);

    const newIssue = {
      id: newId,
      department: issueData.department || "sanitation",
      deptName: issueData.deptName || "Sanitation & Waste Management",
      deptIcon: issueData.deptIcon || "🏢",
      title: issueData.title,
      category: issueData.category || "garbage",
      categoryName: issueData.categoryName || "Urban Civic Issue",
      categoryIcon: issueData.categoryIcon || "📌",
      severity: issueData.severity || "medium",
      severityLabel: issueData.severityLabel || "Medium Severity",
      recommendedResource: resourceAlloc.resource,
      resourceIcon: resourceAlloc.icon,
      description: issueData.description,
      location: issueData.location || "Ward 12 Central, Main Street",
      lat: issueData.lat || 17.0010,
      lng: issueData.lng || 81.8045,
      reportedBy: issueData.anonymous ? "Anonymous Citizen" : user.name,
      userId: user.id,
      timestamp: new Date().toISOString(),
      slaHoursLeft: 48,
      status: "pending",
      assignedWorker: issueData.department === 'electricity' ? "Suresh Babu (Lineman #LN-402)" : issueData.department === 'food_safety' ? "Dr. Lakshmi Prasad (FSO)" : "Ramesh Kumar (Sanitation Lead)",
      imageBefore: issueData.imageBefore || "https://images.unsplash.com/photo-1605600659908-0ef719419d41?w=800&auto=format&fit=crop&q=80",
      imageAfter: null,
      upvotes: 1,
      upvotedBy: [user.id],
      rewardIssued: false,
      rewardPoints: 50,
      rewardAmount: 30,
      fineAmount: issueData.severity === 'bulk' ? 500 : 150,
      fineIssued: false,
      comments: [
        { author: "AI Auto-Classifier", text: `✅ Routed to ${issueData.deptName || 'Department'}. Allocated: ${resourceAlloc.resource}. 48-Hour SLA active.`, time: "Just now" }
      ]
    };

    this.issues.unshift(newIssue);
    this.saveToStorage(STORAGE_ISSUES_KEY, this.issues);
    return newIssue;
  }

  // Upvote
  toggleUpvote(issueId) {
    const user = auth.getUser();
    const issue = this.getIssueById(issueId);
    if (!issue) return null;

    if (!issue.upvotedBy) issue.upvotedBy = [];
    const idx = issue.upvotedBy.indexOf(user.id);
    
    if (idx === -1) {
      issue.upvotedBy.push(user.id);
      issue.upvotes = (issue.upvotes || 0) + 1;
    } else {
      issue.upvotedBy.splice(idx, 1);
      issue.upvotes = Math.max(0, (issue.upvotes || 1) - 1);
    }

    this.saveToStorage(STORAGE_ISSUES_KEY, this.issues);
    return issue;
  }

  // Add Comment
  addComment(issueId, text) {
    const user = auth.getUser();
    const issue = this.getIssueById(issueId);
    if (!issue) return null;

    if (!issue.comments) issue.comments = [];
    issue.comments.push({
      author: user.name,
      text: text,
      time: "Just now"
    });

    this.saveToStorage(STORAGE_ISSUES_KEY, this.issues);
    return issue;
  }

  // Resolve Issue with Before/After Verification
  resolveIssue(issueId, resolutionNotes, imageAfter) {
    const issue = this.getIssueById(issueId);
    if (!issue) return null;

    issue.status = "resolved";
    issue.resolutionNotes = resolutionNotes || "Issue resolved and field verified.";
    issue.imageAfter = imageAfter || "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=800&auto=format&fit=crop&q=80";
    issue.resolvedAt = new Date().toISOString();

    // Reward the citizen reporter with +50 points and ₹30
    if (!issue.rewardIssued) {
      issue.rewardIssued = true;
      auth.addReward(30, 50);

      this.rewards.unshift({
        id: `TX-${Date.now().toString().slice(-4)}`,
        type: "reward",
        title: `Valid Report Resolved (#${issue.id})`,
        amount: 30,
        points: 50,
        date: "Today",
        status: "Credited to Wallet"
      });
      this.saveToStorage(STORAGE_REWARDS_KEY, this.rewards);
    }

    this.saveToStorage(STORAGE_ISSUES_KEY, this.issues);
    return issue;
  }

  // Assign Progress
  assignProgress(issueId, officerNotes) {
    const issue = this.getIssueById(issueId);
    if (!issue) return null;

    issue.status = "in_progress";
    if (officerNotes) {
      this.addComment(issueId, `Field Update: ${officerNotes}`);
    }
    this.saveToStorage(STORAGE_ISSUES_KEY, this.issues);
    return issue;
  }

  // Fine
  imposeFine(issueId, fineAmount = 500, violatorEntity = "Responsible Violator") {
    const issue = this.getIssueById(issueId);
    if (!issue) return null;

    issue.fineIssued = true;
    issue.fineAmount = fineAmount;
    this.addComment(issueId, `⚖️ Penalty Notice: Fine of ₹${fineAmount} imposed on ${violatorEntity}.`);
    
    this.saveToStorage(STORAGE_ISSUES_KEY, this.issues);
    return issue;
  }

  // SLA Watchdog
  updateSLAStatuses() {
    const now = Date.now();
    let updated = false;

    this.issues.forEach(iss => {
      if (iss.status === 'resolved') return;
      const reportedTime = new Date(iss.timestamp).getTime();
      const elapsedHours = (now - reportedTime) / (3600 * 1000);
      const remaining = Math.round(48 - elapsedHours);
      iss.slaHoursLeft = remaining;

      if (remaining <= 0 && iss.status !== 'escalated') {
        iss.status = 'escalated';
        iss.assignedWorker = "Zonal Senior Department Officer";
        updated = true;
      }
    });

    if (updated) {
      this.saveToStorage(STORAGE_ISSUES_KEY, this.issues);
    }
  }

  // Vendors
  getAllVendors() {
    return [...this.vendors];
  }

  // Power Grid
  getPowerGridStatus() {
    return this.powerGridStatus;
  }

  // Support
  getSupportTickets() {
    return [...this.supportTickets];
  }

  createSupportTicket(ticketData) {
    const newTicket = {
      id: `TECH-${Date.now().toString().slice(-4)}`,
      issueType: ticketData.issueType,
      desc: ticketData.desc,
      status: "Under Review",
      date: "Just now"
    };
    this.supportTickets.unshift(newTicket);
    this.saveToStorage(STORAGE_SUPPORT_KEY, this.supportTickets);
    return newTicket;
  }

  // Metrics
  getMetrics() {
    const total = this.issues.length;
    const resolved = this.issues.filter(i => i.status === 'resolved').length;
    const inProgress = this.issues.filter(i => i.status === 'in_progress').length;
    const pending = this.issues.filter(i => i.status === 'pending').length;
    const escalated = this.issues.filter(i => i.status === 'escalated').length;

    const sanitationCount = this.issues.filter(i => i.department === 'sanitation').length;
    const foodCount = this.issues.filter(i => i.department === 'food_safety').length;
    const electricityCount = this.issues.filter(i => i.department === 'electricity').length;

    const totalRewardsPaid = this.rewards.reduce((sum, r) => sum + (r.amount || 0), 0);
    const totalFinesCollected = this.issues.filter(i => i.fineIssued).reduce((sum, i) => sum + (i.fineAmount || 0), 0);

    return {
      total,
      resolved,
      inProgress,
      pending,
      escalated,
      sanitationCount,
      foodCount,
      electricityCount,
      resolutionRate: total > 0 ? Math.round((resolved / total) * 100) : 0,
      totalRewardsPaid,
      totalFinesCollected
    };
  }
}

export const db = new DatabaseManager();
