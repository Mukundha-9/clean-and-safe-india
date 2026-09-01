/* ==========================================================================
   Smart Civic Connect - Master Bundled Engine (Cyber-Dark Theme Edition)
   4-Tier Geospatial Division, Civic Credits & Streak Recognition, GIS & Voice AI,
   Live In-App Interactive WhatsApp Web Client,
   Food Safety Inspection, Rectification & Certified/Violated Registry
   ========================================================================== */

(function() {
  'use strict';

  // =========================================================================
  // 1. NATIONAL 4-TIER GEOSPATIAL JURISDICTION HIERARCHY (6 KEY STATES)
  // =========================================================================
  const GEOSPATIAL_DIRECTORY = {
    "Andhra Pradesh": {
      "Surampalem": {
        coords: [17.0010, 81.8045],
        wards: {
          "Ward 12 (Market Zone)": ["Gandhi Statue Main Road", "Market Gate Cross", "Commercial Complex Lane"],
          "Ward 11 (Lake View Zone)": ["Lake View Road", "North Bund Promenade", "Fishermen Colony Road"],
          "Ward 14 (Campus Zone)": ["College Road Food Court", "University Gate 2 Road", "Aditya Tech Park Lane"]
        }
      },
      "Kakinada": {
        coords: [16.9891, 82.2475],
        wards: {
          "Smart City Zone 1": ["Main Port Road", "Bhanugudi Junction", "Collectorate Road"],
          "Smart City Zone 2": ["Cinema Road", "Jagannaickpur Bridge Lane", "Indrapalayam Road"]
        }
      },
      "Visakhapatnam": {
        coords: [17.6868, 83.2185],
        wards: {
          "Zone 3 (Beach Area)": ["RK Beach Promenade", "Siripuram Junction", "MVP Colony Main Road"]
        }
      }
    },
    "Telangana": {
      "Hyderabad": {
        coords: [17.3850, 78.4867],
        wards: {
          "Charminar Zone": ["Laad Bazaar Road", "Madina Junction", "Nayapul Bridge Lane"],
          "HITEC City Zone": ["Cyber Towers Main Road", "Madhapur 100ft Road", "Mindspace Junction"]
        }
      }
    },
    "Maharashtra": {
      "Pune": {
        coords: [18.5204, 73.8567],
        wards: {
          "Shivajinagar Zone": ["FC Road", "JM Road", "University Circle Lane"]
        }
      },
      "Mumbai": {
        coords: [19.0760, 72.8777],
        wards: {
          "Bandra West Zone": ["Hill Road", "Carter Road Promenade", "Linking Road"],
          "Andheri East Zone": ["Chakala Metro Station Lane", "MIDC Central Road"]
        }
      }
    },
    "Karnataka": {
      "Bengaluru": {
        coords: [12.9716, 77.5946],
        wards: {
          "Indiranagar Zone": ["100 Feet Road", "12th Main Junction", "CMH Road"],
          "Whitefield Zone": ["ITPL Main Road", "Hope Farm Junction"]
        }
      }
    },
    "Tamil Nadu": {
      "Chennai": {
        coords: [13.0827, 80.2707],
        wards: {
          "T. Nagar Zone": ["Ranganathan Street", "Usman Road Flyover", "Panagal Park Lane"],
          "Marina Beach Zone": ["Kamarajar Salai", "Santhome High Road"]
        }
      }
    },
    "Delhi NCR": {
      "New Delhi": {
        coords: [28.6139, 77.2090],
        wards: {
          "Central Zone": ["Connaught Place Outer Circle", "Janpath Road", "Barakhamba Lane"],
          "Karol Bagh Zone": ["Ajmal Khan Road", "Pusa Road Junction"]
        }
      }
    }
  };

  // =========================================================================
  // 2. AUTHENTICATION & DEMO ACCOUNTS
  // =========================================================================
  const STORAGE_SESSION_KEY = 'smart_civic_auth_session_v9';

  const SYSTEM_ACCOUNTS = {
    citizen: {
      department: 'citizen',
      deptTitle: 'Citizen Portal',
      email: 'citizen@civictech.in',
      password: 'password123',
      name: 'KRISH',
      ward: 'Ward 12 (Market Zone), Surampalem',
      role: 'citizen',
      roleTitle: 'Verified Citizen Reporter',
      officialId: 'CIT-IND-2026-8941',
      avatar: 'KR',
      civicCredits: 20,
      activeStreakWeeks: 1,
      guardianLevel: 'Level 1: Bronze Civic Guardian'
    },
    municipal: {
      department: 'municipal',
      deptTitle: 'Municipal & Electricity Command',
      email: 'admin@municipality.gov.in',
      password: 'password123',
      name: 'K. Mukundha (Zonal Administrator)',
      ward: 'Central Municipal Command & SCADA Grid Room',
      role: 'government_admin',
      roleTitle: 'Designated Municipal & Electricity Administrator',
      officialId: 'GOV-MUNC-SEC-012',
      avatar: 'KM',
      civicCredits: 0,
      activeStreakWeeks: 0
    },
    food: {
      department: 'food',
      deptTitle: 'Food Safety & Standards Authority',
      email: 'fso.officer@foodsafety.gov.in',
      password: 'password123',
      name: 'Dr. Lakshmi Prasad (FSO)',
      ward: 'District Food Safety & Inspection Cell',
      role: 'food_officer',
      roleTitle: 'Designated Food Safety Officer (FSO)',
      officialId: 'FSSAI-INSP-2026-44',
      avatar: 'LP',
      civicCredits: 0,
      activeStreakWeeks: 0
    }
  };

  class AuthManager {
    constructor() {
      this.session = this.loadSession();
      this.listeners = [];
    }

    loadSession() {
      try {
        // Clean legacy persistent session so cold opens always start at the Login page
        localStorage.removeItem(STORAGE_SESSION_KEY);
        const stored = sessionStorage.getItem(STORAGE_SESSION_KEY);
        if (stored) return JSON.parse(stored);
      } catch (e) {
        console.warn("Auth session parse error:", e);
      }
      return null;
    }

    saveSession(sessionData) {
      this.session = sessionData;
      try {
        if (sessionData) {
          sessionStorage.setItem(STORAGE_SESSION_KEY, JSON.stringify(sessionData));
          if (sessionData.user && sessionData.user.email) {
            localStorage.setItem('CIVIC_LAST_EMAIL', sessionData.user.email);
          }
        } else {
          sessionStorage.removeItem(STORAGE_SESSION_KEY);
        }
        localStorage.removeItem(STORAGE_SESSION_KEY);
      } catch (e) {
        console.warn("Auth session write error:", e);
      }
      this.notify();
    }

    isAuthenticated() {
      return this.session !== null;
    }

    getUser() {
      return this.session ? this.session.user : null;
    }

    getDepartment() {
      return this.session ? this.session.department : null;
    }

    async login(department, email, password) {
      const cleanEmail = (email || '').trim().toLowerCase();
      const cleanPass = (password || '').trim();

      if (!cleanEmail || cleanEmail.length < 3) {
        throw new Error("Please enter a valid email address.");
      }
      if (!cleanPass) {
        throw new Error("Please enter your password.");
      }

      let data = null;
      let networkError = null;

      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000);

        const res = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: cleanEmail, password: cleanPass, department: department }),
          signal: controller.signal
        });
        clearTimeout(timeoutId);

        data = await res.json();
        if (!res.ok || !data.success) {
          throw new Error(data.error || 'Authentication failed. Incorrect email or password.');
        }
      } catch (err) {
        // If it's a genuine 401 credential rejection from server, re-throw it!
        if (err.message && (err.message.includes('Incorrect') || err.message.includes('password') || err.message.includes('unregistered'))) {
          throw err;
        }
        networkError = err;
      }

      // If backend responded with success
      if (data && data.success && data.user) {
        const sessionData = {
          token: data.token || ('CIVIC_JWT_' + Date.now()),
          department: department,
          user: data.user,
          loginTime: new Date().toISOString()
        };
        this.saveSession(sessionData);
        return sessionData;
      }

      // Resilient Fallback (for mobile APKs, waking cloud containers, or temporary offline)
      console.warn("Using resilient authentication fallback:", networkError);
      
      let fallbackUser = null;
      if (cleanEmail === 'admin@municipality.gov.in') {
        if (cleanPass !== 'password123') throw new Error('Incorrect password for Municipal Admin.');
        fallbackUser = {
          id: 'user-102',
          name: 'K.H. Sameer Reddy (Zonal Administrator)',
          email: cleanEmail,
          department: 'municipal',
          roleTitle: 'Designated Municipal Authority',
          officialId: 'GOV-MUNC-SEC-012',
          avatar: 'SR',
          civicCredits: 20
        };
      } else if (cleanEmail === 'food.officer@fssai.gov.in') {
        if (cleanPass !== 'fssai2026') throw new Error('Incorrect password for Food Safety Officer.');
        fallbackUser = {
          id: 'user-104',
          name: 'Food Safety Officer Sharma',
          email: cleanEmail,
          department: 'food',
          roleTitle: 'Chief Food Safety Inspector',
          officialId: 'FSSAI-INSP-2026-44',
          avatar: 'FS',
          civicCredits: 20
        };
      } else if (cleanEmail === 'lineman.suresh@apepdcl.gov.in') {
        if (cleanPass !== 'scada123') throw new Error('Incorrect password for SCADA Lineman.');
        fallbackUser = {
          id: 'user-105',
          name: 'Lineman Suresh Kumar',
          email: cleanEmail,
          department: 'electricity',
          roleTitle: 'Senior Field Lineman (APEPDCL)',
          officialId: 'DISCOM-LINE-8841',
          avatar: 'SK',
          civicCredits: 20
        };
      } else {
        // Citizen login fallback
        const namePart = cleanEmail.split('@')[0].replace('.', ' ');
        const formattedName = namePart.charAt(0).toUpperCase() + namePart.slice(1);
        fallbackUser = {
          id: 'user-' + Date.now().toString().slice(-4),
          name: formattedName || 'Citizen User',
          email: cleanEmail,
          department: 'citizen',
          roleTitle: 'Verified Civic Citizen',
          officialId: 'CITIZEN-AP-' + Math.floor(1000 + Math.random() * 9000),
          avatar: formattedName.slice(0, 2).toUpperCase() || 'CU',
          civicCredits: 20
        };
      }

      const sessionData = {
        token: 'CIVIC_JWT_' + Date.now(),
        department: department,
        user: fallbackUser,
        loginTime: new Date().toISOString()
      };

      this.saveSession(sessionData);
      return sessionData;
    }

    logout() {
      this.saveSession(null);
    }

    subscribe(cb) {
      this.listeners.push(cb);
    }

    notify() {
      this.listeners.forEach(cb => cb(this.session));
    }
  }

  const auth = new AuthManager();

  // =========================================================================
  // DATE & TIME FORMATTING & SLA TURNAROUND HELPERS
  // =========================================================================
  function formatReportDateTime(ts) {
    if (!ts) return 'Pending';
    const d = new Date(ts);
    return d.toLocaleString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });
  }

  function formatReportDate(ts) {
    if (!ts) return 'Pending';
    const d = new Date(ts);
    return d.toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  }

  function formatReportTime(ts) {
    if (!ts) return '';
    const d = new Date(ts);
    return d.toLocaleTimeString('en-IN', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });
  }

  function getRealisticResolvedTimestamp(issue) {
    if (!issue || !issue.timestamp) return Date.now();
    if (!issue.resolvedTimestamp) {
      const deptHours = issue.department === 'electricity' ? 1.5 : (issue.department === 'food_safety' ? 4.2 : 3.5);
      return issue.timestamp + (deptHours * 3600 * 1000);
    }
    const diffMs = issue.resolvedTimestamp - issue.timestamp;
    // If resolved in same minute during quick test, calculate realistic civic squad resolution time
    if (diffMs < 15 * 60 * 1000) {
      const deptHours = issue.department === 'electricity' ? 1.5 : (issue.department === 'food_safety' ? 4.2 : 3.5);
      return issue.timestamp + (deptHours * 3600 * 1000);
    }
    return issue.resolvedTimestamp;
  }

  function calculateSlaTurnaround(startTs, endTs, issue = {}) {
    if (!startTs) return 'N/A';
    let end = endTs || getRealisticResolvedTimestamp(issue);
    let diffMs = end - startTs;
    if (diffMs < 15 * 60 * 1000) {
      const deptHours = issue.department === 'electricity' ? 1.5 : (issue.department === 'food_safety' ? 4.2 : 3.5);
      diffMs = deptHours * 3600 * 1000;
    }
    const hours = Math.floor(diffMs / (3600 * 1000));
    const mins = Math.floor((diffMs % (3600 * 1000)) / (60 * 1000));
    return `${hours > 0 ? hours + 'h ' : ''}${mins}m Turnaround`;
  }

  // =========================================================================
  // 3. MOCK DATABASE WITH 100% UNIQUE HIGH-QUALITY INCIDENT IMAGES
  // =========================================================================
  const INITIAL_ISSUES = [
    // --- ANDHRA PRADESH ---
    {
      id: 'ISS-2026-00123',
      state: 'Andhra Pradesh',
      city: 'Surampalem',
      ward: 'Ward 12 (Market Zone)',
      street: 'Gandhi Statue Main Road',
      department: 'sanitation',
      deptName: 'Sanitation & Waste Management',
      deptIcon: '🏢',
      title: 'Severe Garbage Overflow at Market Gate',
      description: 'Overfilled municipal waste bin spilling onto pedestrian footpath. High stench and public hygiene risk.',
      location: 'Ward 12 (Market Zone), Gandhi Statue Main Road, Surampalem',
      category: 'garbage',
      categoryName: 'Urban Garbage Overflow',
      categoryIcon: '🗑️',
      severity: 'bulk',
      severityLabel: 'BULK HAZARD',
      status: 'pending',
      timestamp: Date.now() - 3600000 * 8,
      slaDeadline: Date.now() + 3600000 * 40,
      resolvedTimestamp: null,
      slaHoursLeft: 40,
      verifiedByOfficer: 'Consultant Officer K. Mukundha (GOV-MUNC-SEC-012)',
      verifiedTimestamp: Date.now() - 3600000 * 7.5,
      assignedWorker: 'Sanitation Squad 4 (Lead: Ramesh K.)',
      assignedTimestamp: Date.now() - 3600000 * 7,
      workerStatus: 'Dispatched & On-Site Waste Clearing',
      isSlaBreached: false,
      lat: 17.0005,
      lng: 81.8040,
      reportedBy: 'KRISH',
      userId: 'user-101',
      upvotes: 24,
      upvotedBy: ['user-101'],
      imageBefore: 'https://images.unsplash.com/photo-1605600659908-0ef719419d41?w=800&auto=format&fit=crop&q=80',
      imageAfter: null,
      recommendedResource: 'Tractor / Bulk Compactor',
      rewardIssued: false,
      fineLevied: 0,
      comments: [
        { author: 'System Watchdog', text: '48h SLA timer initiated. Automated vehicle allocated.', time: '8h ago' },
        { author: 'Consultant Officer K. Mukundha', text: 'Grievance verified. Squad 4 dispatched.', time: '7h ago' }
      ]
    },
    {
      id: 'ISS-2026-00124',
      state: 'Andhra Pradesh',
      city: 'Surampalem',
      ward: 'Ward 12 (Market Zone)',
      street: 'Commercial Complex Lane',
      department: 'electricity',
      deptName: 'Smart Electricity Department',
      deptIcon: '⚡',
      title: 'Sparks from 11KV Distribution Transformer',
      description: 'Frequent flashover sparks during peak evening load. Fire hazard to adjacent retail shops.',
      location: 'Ward 12 (Market Zone), Commercial Complex Lane, Surampalem',
      category: 'transformer_damage',
      categoryName: 'Damaged Transformer / Sparking',
      categoryIcon: '⚡',
      severity: 'bulk',
      severityLabel: 'HIGH CRITICAL',
      status: 'in_progress',
      timestamp: Date.now() - 3600000 * 18,
      slaDeadline: Date.now() + 3600000 * 30,
      resolvedTimestamp: null,
      slaHoursLeft: 30,
      verifiedByOfficer: 'Consultant Officer K. Mukundha (GOV-MUNC-SEC-012)',
      verifiedTimestamp: Date.now() - 3600000 * 17.5,
      assignedWorker: 'Lineman Squad B (Suresh & Team)',
      assignedTimestamp: Date.now() - 3600000 * 16,
      workerStatus: 'Feeder Isolated & Jumper Splicing In Progress',
      isSlaBreached: false,
      lat: 17.0022,
      lng: 81.8065,
      reportedBy: 'K. Mukundha',
      userId: 'user-102',
      upvotes: 42,
      upvotedBy: ['user-101', 'user-102'],
      imageBefore: 'https://images.unsplash.com/photo-1544724569-5f546fd6f2b5?w=800&auto=format&fit=crop&q=80',
      imageAfter: null,
      recommendedResource: 'Hydraulic Bucket Truck (AP-05-EB)',
      rewardIssued: false,
      fineLevied: 0,
      comments: [
        { author: 'Lineman Dispatch', text: 'Feeder isolated. Replacement bushing in transit.', time: '2h ago' }
      ]
    },
    {
      id: 'ISS-2026-00128',
      state: 'Andhra Pradesh',
      city: 'Surampalem',
      ward: 'Ward 12 (Market Zone)',
      street: 'Gandhi Statue Main Road',
      department: 'sanitation',
      deptName: 'Sanitation & Waste Management',
      deptIcon: '🏢',
      title: '🚨 SLA Breached: Massive Solid Waste & Garbage Dump Overflow',
      description: 'Over 3 tons of rotten municipal garbage overflowing onto main pedestrian road. Exceeded mandatory 48-Hour SLA period without field clearance. Automatically escalated to Municipal Commissioner Dr. Mahesh Babu & Zonal Health Directorate.',
      location: 'Ward 12 (Market Zone), Gandhi Statue Main Road, Surampalem',
      category: 'garbage',
      categoryName: 'Uncollected Municipal Solid Waste & Garbage Dump',
      categoryIcon: '🗑️',
      severity: 'bulk',
      severityLabel: 'SLA BREACHED (>48H)',
      status: 'escalated',
      timestamp: Date.now() - 3600000 * 62,
      slaDeadline: Date.now() - 3600000 * 14,
      resolvedTimestamp: null,
      slaHoursLeft: 0,
      isSlaBreached: true,
      escalatedTo: 'Zonal Municipal Commissioner (Dr. Mahesh Babu) & Higher Health Directorate',
      verifiedByOfficer: 'Consultant Officer K. Mukundha (GOV-MUNC-SEC-012)',
      verifiedTimestamp: Date.now() - 3600000 * 61.5,
      assignedWorker: 'Sanitation Rapid Fleet 3 (Lead: P. Ramesh)',
      assignedTimestamp: Date.now() - 3600000 * 60,
      workerStatus: 'Delayed (>48h) — Auto-Forwarded to Municipal Commissioner Red Desk for Urgent Action',
      lat: 17.0012,
      lng: 81.8048,
      reportedBy: 'KRISH',
      userId: 'user-101',
      upvotes: 84,
      upvotedBy: ['user-101'],
      imageBefore: 'https://images.unsplash.com/photo-1605600659908-0ef719419d41?w=800&auto=format&fit=crop&q=80',
      imageAfter: null,
      recommendedResource: 'Heavy Hydraulic Compactor & 10-Ton Tipper Fleet',
      rewardIssued: false,
      fineLevied: 0,
      comments: [
        { author: 'System SLA Monitor', text: '⏱️ 48-Hour SLA Breached! Grievance unaddressed after 48h limit.', time: '14h ago' },
        { author: 'Auto-Escalation Gateway', text: '🚨 Escalated to Higher Authority: Zonal Municipal Commissioner (Dr. Mahesh Babu) & Urban Health Directorate.', time: '14h ago' },
        { author: 'Municipal Commissioner Red Desk', text: 'Ticket received with Critical Priority 1. Direct disciplinary summons and immediate heavy squad deployed.', time: '12h ago' },
        { author: 'KRISH (Citizen)', text: 'Garbage dump is emitting toxic odor and blocking school children. Thank you for forwarding to the Commissioner.', time: '4h ago' }
      ]
    },
    {
      id: 'ISS-2026-00127',
      state: 'Andhra Pradesh',
      city: 'Surampalem',
      ward: 'Ward 12 (Market Zone)',
      street: 'Old Bus Stand Cross',
      department: 'sanitation',
      deptName: 'Sanitation & Waste Management',
      deptIcon: '🏢',
      title: 'Overflowing Sewage Drain near Old Bus Stand',
      description: 'Blocked underground storm drain overflowing with foul sludge. Exceeded 48h resolution SLA.',
      location: 'Ward 12 (Market Zone), Old Bus Stand Cross, Surampalem',
      category: 'garbage',
      categoryName: 'Sewage Overflow Hazard',
      categoryIcon: '🚯',
      severity: 'bulk',
      severityLabel: 'SLA BREACHED (>48H)',
      status: 'escalated',
      timestamp: Date.now() - 3600000 * 54,
      slaDeadline: Date.now() - 3600000 * 6,
      resolvedTimestamp: null,
      slaHoursLeft: 0,
      isSlaBreached: true,
      escalatedTo: 'Zonal Municipal Commissioner (Dr. Mahesh Babu) & Urban Health Director',
      verifiedByOfficer: 'Consultant Officer K. Mukundha (GOV-MUNC-SEC-012)',
      verifiedTimestamp: Date.now() - 3600000 * 53.5,
      assignedWorker: 'Special Drain Heavy Squad (Lead: B. Satyanarayana)',
      assignedTimestamp: Date.now() - 3600000 * 52,
      workerStatus: 'Delayed (>48h) — Auto-Forwarded to Municipal Commissioner Red Queue',
      lat: 17.0018,
      lng: 81.8052,
      reportedBy: 'KRISH',
      userId: 'user-101',
      upvotes: 63,
      upvotedBy: ['user-101'],
      imageBefore: 'https://images.unsplash.com/photo-1544724569-5f546fd6f2b5?w=800&auto=format&fit=crop&q=80',
      imageAfter: null,
      recommendedResource: 'Hydraulic Suction & Jetting Tanker',
      rewardIssued: false,
      fineLevied: 0,
      comments: [
        { author: 'System Watchdog', text: '48-Hour SLA countdown expired without field sign-off.', time: '6h ago' },
        { author: 'Auto-Escalation Engine', text: 'Grievance automatically forwarded to Zonal Municipal Commissioner Red Priority Queue.', time: '6h ago' }
      ]
    },
    {
      id: 'ISS-2026-00125',
      state: 'Andhra Pradesh',
      city: 'Surampalem',
      ward: 'Ward 14 (Campus Zone)',
      street: 'College Road Food Court',
      department: 'food_safety',
      deptName: 'Food Safety Department',
      deptIcon: '🍲',
      title: 'Uncovered Stale Food & Open Drain Violation',
      description: 'Campus Night Shawarma & Grills: Preparing food next to open drain channel without hairnets or sneeze covers.',
      location: 'Ward 14 (Campus Zone), College Road Food Court, Surampalem',
      category: 'food_hygiene',
      categoryName: 'Unhygienic Food Stall / Prep',
      categoryIcon: '🍲',
      severity: 'medium',
      severityLabel: 'MEDIUM RISK',
      status: 'pending',
      timestamp: Date.now() - 3600000 * 4,
      slaDeadline: Date.now() + 3600000 * 44,
      resolvedTimestamp: null,
      slaHoursLeft: 44,
      verifiedByOfficer: 'Dr. Lakshmi Prasad (Senior FSO)',
      verifiedTimestamp: Date.now() - 3600000 * 3.8,
      assignedWorker: 'Food Safety Officer (Dr. Lakshmi Prasad)',
      assignedTimestamp: Date.now() - 3600000 * 3.5,
      workerStatus: 'Improvement Notice Issued — 7-Day Rectification Window',
      isSlaBreached: false,
      lat: 16.9980,
      lng: 81.8020,
      reportedBy: 'Dr. Lakshmi Prasad (FSO)',
      userId: 'food-01',
      vendorId: 'FSSAI-AP-2026-V02',
      vendorName: 'Campus Night Shawarma & Grills',
      mq135GasPpm: 340,
      upvotes: 18,
      upvotedBy: [],
      imageBefore: 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800&auto=format&fit=crop&q=80',
      imageAfter: null,
      recommendedResource: 'Food Safety Inspector Unit',
      rewardIssued: false,
      fineLevied: 500,
      comments: [
        { author: 'Dr. Lakshmi Prasad (FSO)', text: 'Statutory 7-Day Improvement Notice issued with ₹500 fine.', time: '4h ago' }
      ]
    },
    {
      id: 'ISS-2026-00128',
      state: 'Andhra Pradesh',
      city: 'Surampalem',
      ward: 'Ward 12 (Market Zone)',
      street: 'Market Gate Cross',
      department: 'food_safety',
      deptName: 'Food Safety Department',
      deptIcon: '🍲',
      title: 'Stale Burnt Cooking Oil & Toxic Fumes Violation',
      description: 'Sri Krishna Seafood Point: Reusing black rancid cooking oil across multiple frying cycles (TPM 34%).',
      location: 'Ward 12 (Market Zone), Market Gate Cross, Surampalem',
      category: 'food_hygiene',
      categoryName: 'Toxic Oil Reuse Violation',
      categoryIcon: '🍳',
      severity: 'bulk',
      severityLabel: 'CRITICAL VIOLATION',
      status: 'pending',
      timestamp: Date.now() - 3600000 * 10,
      slaDeadline: Date.now() + 3600000 * 38,
      resolvedTimestamp: null,
      slaHoursLeft: 38,
      verifiedByOfficer: 'Dr. Lakshmi Prasad (Senior FSO)',
      verifiedTimestamp: Date.now() - 3600000 * 9.5,
      assignedWorker: 'Food Safety Officer (Dr. Lakshmi Prasad)',
      assignedTimestamp: Date.now() - 3600000 * 9,
      workerStatus: 'Adulteration Sampling & Notice Levied',
      isSlaBreached: false,
      lat: 17.0012,
      lng: 81.8038,
      reportedBy: 'Dr. Lakshmi Prasad (FSO)',
      userId: 'food-01',
      vendorId: 'FSSAI-AP-2026-V01',
      vendorName: 'Sri Krishna Seafood & Fast Food Point',
      mq135GasPpm: 370,
      upvotes: 45,
      upvotedBy: [],
      imageBefore: 'https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=800&auto=format&fit=crop&q=80',
      imageAfter: null,
      recommendedResource: 'Food Safety Adulteration Cell',
      rewardIssued: false,
      fineLevied: 2000,
      comments: [
        { author: 'Dr. Lakshmi Prasad (FSO)', text: 'Critical Violation notice issued under Section 56. ₹2,000 fine levied.', time: '10h ago' }
      ]
    },
    {
      id: 'ISS-2026-00120',
      state: 'Andhra Pradesh',
      city: 'Surampalem',
      ward: 'Ward 11 (Lake View Zone)',
      street: 'Lake View Road',
      department: 'sanitation',
      deptName: 'Sanitation & Waste Management',
      deptIcon: '🏢',
      title: 'Commercial Debris Cleared at Lake Road',
      description: 'Illegally dumped construction debris cleaned and surface sanitized.',
      location: 'Ward 11 (Lake View Zone), Lake View Road, Surampalem',
      category: 'garbage',
      categoryName: 'Urban Garbage Overflow',
      categoryIcon: '🗑️',
      severity: 'bulk',
      severityLabel: 'RESOLVED',
      status: 'resolved',
      timestamp: Date.now() - 3600000 * 36,
      slaDeadline: Date.now() + 3600000 * 12,
      resolvedTimestamp: Date.now() - 3600000 * 8,
      slaHoursLeft: 0,
      verifiedByOfficer: 'Consultant Officer K. Mukundha (GOV-MUNC-SEC-012)',
      verifiedTimestamp: Date.now() - 3600000 * 35.5,
      assignedWorker: 'Sanitation Squad 1 (Lead: Officer Ramesh)',
      assignedTimestamp: Date.now() - 3600000 * 34,
      workerStatus: 'Field Execution Completed & Cleaned Proof Uploaded',
      isSlaBreached: false,
      lat: 17.0050,
      lng: 81.8010,
      reportedBy: 'KRISH',
      userId: 'user-101',
      upvotes: 56,
      upvotedBy: ['user-101'],
      imageBefore: 'https://images.unsplash.com/photo-1611284446314-60a58ac0deb9?w=800&auto=format&fit=crop&q=80',
      imageAfter: 'https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=800&auto=format&fit=crop&q=80',
      recommendedResource: 'Tractor / Bulk Compactor',
      rewardIssued: true,
      fineLevied: 500,
      comments: [
        { author: 'Officer Ramesh', text: 'Cleaned, sanitized, and ₹500 fine levied on offender.', time: '12h ago' }
      ]
    },
    {
      id: 'ISS-2026-00130',
      state: 'Andhra Pradesh',
      city: 'Kakinada',
      ward: 'Smart City Zone 1',
      street: 'Bhanugudi Junction',
      department: 'sanitation',
      deptName: 'Sanitation & Waste Management',
      deptIcon: '🏢',
      title: 'Water Pipeline Leak & Road Flooding',
      description: 'Underground pipeline burst causing road flooding and hazard for two-wheelers at Bhanugudi.',
      location: 'Smart City Zone 1, Bhanugudi Junction, Kakinada',
      category: 'pipeline_leak',
      categoryName: 'Road & Pipeline Hazard',
      categoryIcon: '🚰',
      severity: 'medium',
      severityLabel: 'MEDIUM RISK',
      status: 'pending',
      timestamp: Date.now() - 3600000 * 5,
      slaHoursLeft: 43,
      lat: 16.9891,
      lng: 82.2475,
      reportedBy: 'Kakinada Citizen Group',
      userId: 'user-104',
      upvotes: 31,
      upvotedBy: [],
      imageBefore: 'https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?w=800&auto=format&fit=crop&q=80',
      imageAfter: null,
      recommendedResource: 'Municipal Water & Sanitation Unit',
      assignedWorker: 'Kakinada Quick Response Squad',
      rewardIssued: false,
      fineLevied: 0,
      comments: [
        { author: 'Smart City Cell', text: 'Emergency valve closure dispatched.', time: '4h ago' }
      ]
    },
    {
      id: 'ISS-2026-00132',
      state: 'Andhra Pradesh',
      city: 'Visakhapatnam',
      ward: 'Zone 3 (Beach Area)',
      street: 'RK Beach Promenade',
      department: 'sanitation',
      deptName: 'Sanitation & Waste Management',
      deptIcon: '🏢',
      title: 'Plastic Waste Accumulation at RK Beach',
      description: 'Tourist plastic bottles and wrappers along coastal walking track needing beach sweeping squad.',
      location: 'Zone 3 (Beach Area), RK Beach Promenade, Visakhapatnam',
      category: 'garbage',
      categoryName: 'Beach Cleanliness',
      categoryIcon: '🏖️',
      severity: 'medium',
      severityLabel: 'MEDIUM RISK',
      status: 'in_progress',
      timestamp: Date.now() - 3600000 * 12,
      slaHoursLeft: 36,
      lat: 17.7126,
      lng: 83.3235,
      reportedBy: 'Vizag Coastal Volunteers',
      userId: 'user-105',
      upvotes: 68,
      upvotedBy: [],
      imageBefore: 'https://images.unsplash.com/photo-1618477461853-cf6ed80faba5?w=800&auto=format&fit=crop&q=80',
      imageAfter: null,
      recommendedResource: 'Beach Sweeping Machine & Team',
      assignedWorker: 'GVMC Coastal Squad',
      rewardIssued: false,
      fineLevied: 0,
      comments: [
        { author: 'GVMC Coastal Officer', text: 'Beach squad deployed on morning shift.', time: '6h ago' }
      ]
    },

    // --- TELANGANA ---
    {
      id: 'ISS-2026-00126',
      state: 'Telangana',
      city: 'Hyderabad',
      ward: 'Charminar Zone',
      street: 'Laad Bazaar Road',
      department: 'sanitation',
      deptName: 'Sanitation & Waste Management',
      deptIcon: '🏢',
      title: 'Night Market Waste at Charminar Lane',
      description: 'Cartons and vegetable waste from night market blocking shop entrances.',
      location: 'Charminar Zone, Laad Bazaar Road, Hyderabad',
      category: 'garbage',
      categoryName: 'Urban Garbage Overflow',
      categoryIcon: '🗑️',
      severity: 'medium',
      severityLabel: 'MEDIUM RISK',
      status: 'pending',
      timestamp: Date.now() - 3600000 * 2,
      slaHoursLeft: 46,
      lat: 17.3616,
      lng: 78.4747,
      reportedBy: 'Hyderabad Civic Watch',
      userId: 'user-201',
      upvotes: 19,
      upvotedBy: [],
      imageBefore: 'https://images.unsplash.com/photo-1530587191325-3db32d826c18?w=800&auto=format&fit=crop&q=80',
      imageAfter: null,
      recommendedResource: 'Collection Truck (AP-05-TX)',
      assignedWorker: 'GHMC South Zone Squad',
      rewardIssued: false,
      fineLevied: 0,
      comments: [
        { author: 'GHMC Portal', text: 'Ticket routed to GHMC South Zone.', time: '1h ago' }
      ]
    },
    {
      id: 'ISS-2026-00134',
      state: 'Telangana',
      city: 'Hyderabad',
      ward: 'HITEC City Zone',
      street: 'Cyber Towers Main Road',
      department: 'electricity',
      deptName: 'Smart Electricity Department',
      deptIcon: '⚡',
      title: 'Exposed Streetlight Wiring & Pole Sparking',
      description: 'Junction box cover dislodged on IT corridor road causing sparking during rain.',
      location: 'HITEC City Zone, Cyber Towers Main Road, Hyderabad',
      category: 'transformer_damage',
      categoryName: 'Exposed Electrical Hazard',
      categoryIcon: '⚡',
      severity: 'bulk',
      severityLabel: 'HIGH CRITICAL',
      status: 'in_progress',
      timestamp: Date.now() - 3600000 * 14,
      slaHoursLeft: 34,
      lat: 17.4504,
      lng: 78.3808,
      reportedBy: 'Cyberabad Commuters',
      userId: 'user-202',
      upvotes: 45,
      upvotedBy: [],
      imageBefore: 'https://images.unsplash.com/photo-1513836279014-a89f7a76ae86?w=800&auto=format&fit=crop&q=80',
      imageAfter: null,
      recommendedResource: 'TSSPDCL Hydraulic Squad',
      assignedWorker: 'Madhapur Electrical Division',
      rewardIssued: false,
      fineLevied: 0,
      comments: [
        { author: 'TSSPDCL', text: 'Junction box insulated; new fuse installed.', time: '2h ago' }
      ]
    },

    // --- MAHARASHTRA ---
    {
      id: 'ISS-2026-00136',
      state: 'Maharashtra',
      city: 'Pune',
      ward: 'Shivajinagar Zone',
      street: 'FC Road',
      department: 'sanitation',
      deptName: 'Sanitation & Waste Management',
      deptIcon: '🏢',
      title: 'Commercial Restaurant Waste on FC Road',
      description: 'Overfilled restaurant dumpsters spilling plastic packaging onto pedestrian walkway.',
      location: 'Shivajinagar Zone, FC Road, Pune',
      category: 'garbage',
      categoryName: 'Commercial Overflow',
      categoryIcon: '🗑️',
      severity: 'bulk',
      severityLabel: 'BULK HAZARD',
      status: 'pending',
      timestamp: Date.now() - 3600000 * 6,
      slaHoursLeft: 42,
      lat: 18.5246,
      lng: 73.8415,
      reportedBy: 'Pune Clean City Forum',
      userId: 'user-301',
      upvotes: 38,
      upvotedBy: [],
      imageBefore: 'https://images.unsplash.com/photo-1532996122724-e3c354a0b15b?w=800&auto=format&fit=crop&q=80',
      imageAfter: null,
      recommendedResource: 'PMC Compactor Unit',
      assignedWorker: 'PMC Ward 5 Squad',
      rewardIssued: false,
      fineLevied: 0,
      comments: [
        { author: 'PMC Control Room', text: 'Collection truck rerouted.', time: '3h ago' }
      ]
    },
    {
      id: 'ISS-2026-00137',
      state: 'Maharashtra',
      city: 'Mumbai',
      ward: 'Bandra West Zone',
      street: 'Linking Road',
      department: 'sanitation',
      deptName: 'Sanitation & Waste Management',
      deptIcon: '🏢',
      title: 'Open Stormwater Gutter at Linking Road',
      description: 'Broken drain slab causing dangerous pedestrian foot trap near shopping stalls.',
      location: 'Bandra West Zone, Linking Road, Mumbai',
      category: 'drain_hazard',
      categoryName: 'Open Manhole Hazard',
      categoryIcon: '⚠️',
      severity: 'bulk',
      severityLabel: 'HIGH CRITICAL',
      status: 'in_progress',
      timestamp: Date.now() - 3600000 * 16,
      slaHoursLeft: 32,
      lat: 19.0607,
      lng: 72.8362,
      reportedBy: 'Bandra Residents Association',
      userId: 'user-302',
      upvotes: 72,
      upvotedBy: [],
      imageBefore: 'https://images.unsplash.com/photo-1584467735815-f778f274e296?w=800&auto=format&fit=crop&q=80',
      imageAfter: null,
      recommendedResource: 'BMC H-West Maintenance Squad',
      assignedWorker: 'BMC Civil Team',
      rewardIssued: false,
      fineLevied: 0,
      comments: [
        { author: 'BMC H-West', text: 'Barricaded. Concrete slab in transit.', time: '5h ago' }
      ]
    },

    // --- KARNATAKA ---
    {
      id: 'ISS-2026-00139',
      state: 'Karnataka',
      city: 'Bengaluru',
      ward: 'Indiranagar Zone',
      street: '100 Feet Road',
      department: 'sanitation',
      deptName: 'Sanitation & Waste Management',
      deptIcon: '🏢',
      title: 'Black Spot Dumping near Metro Station',
      description: 'Illegal debris dumped under flyover pillars on 100 Feet Road.',
      location: 'Indiranagar Zone, 100 Feet Road, Bengaluru',
      category: 'garbage',
      categoryName: 'Black Spot Dumping',
      categoryIcon: '🗑️',
      severity: 'bulk',
      severityLabel: 'BULK HAZARD',
      status: 'pending',
      timestamp: Date.now() - 3600000 * 9,
      slaHoursLeft: 39,
      lat: 12.9784,
      lng: 77.6408,
      reportedBy: 'Bengaluru Civic Action',
      userId: 'user-401',
      upvotes: 54,
      upvotedBy: [],
      imageBefore: 'https://images.unsplash.com/photo-1503596476-1c12a8ba09a9?w=800&auto=format&fit=crop&q=80',
      imageAfter: null,
      recommendedResource: 'BBMP Heavy Tipper Squad',
      assignedWorker: 'BBMP East Zone Team',
      rewardIssued: false,
      fineLevied: 0,
      comments: [
        { author: 'BBMP Portal', text: 'Automated challan inspection assigned.', time: '7h ago' }
      ]
    },
    {
      id: 'ISS-2026-00140',
      state: 'Karnataka',
      city: 'Bengaluru',
      ward: 'Whitefield Zone',
      street: 'ITPL Main Road',
      department: 'electricity',
      deptName: 'Smart Electricity Department',
      deptIcon: '⚡',
      title: 'Underground Cable Trench Flashover',
      description: 'BESCOM power pit exposed with intermittent flashes near bus stop.',
      location: 'Whitefield Zone, ITPL Main Road, Bengaluru',
      category: 'transformer_damage',
      categoryName: 'Cable Flashover',
      categoryIcon: '⚡',
      severity: 'bulk',
      severityLabel: 'HIGH CRITICAL',
      status: 'in_progress',
      timestamp: Date.now() - 3600000 * 20,
      slaHoursLeft: 28,
      lat: 12.9866,
      lng: 77.7337,
      reportedBy: 'Whitefield Tech Corridor Watch',
      userId: 'user-402',
      upvotes: 63,
      upvotedBy: [],
      imageBefore: 'https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?w=800&auto=format&fit=crop&q=80',
      imageAfter: null,
      recommendedResource: 'BESCOM Heavy Rapid Squad',
      assignedWorker: 'BESCOM Whitefield Substation',
      rewardIssued: false,
      fineLevied: 0,
      comments: [
        { author: 'BESCOM Support', text: 'Section bypassed; splicing work underway.', time: '3h ago' }
      ]
    },

    // --- TAMIL NADU ---
    {
      id: 'ISS-2026-00141',
      state: 'Tamil Nadu',
      city: 'Chennai',
      ward: 'T. Nagar Zone',
      street: 'Ranganathan Street',
      department: 'sanitation',
      deptName: 'Sanitation & Waste Management',
      deptIcon: '🏢',
      title: 'Textile Packing Waste at Ranganathan St',
      description: 'Cardboard bales and polythene wrap blocking pedestrian path in shopping lane.',
      location: 'T. Nagar Zone, Ranganathan Street, Chennai',
      category: 'garbage',
      categoryName: 'Commercial Waste',
      categoryIcon: '🗑️',
      severity: 'bulk',
      severityLabel: 'BULK HAZARD',
      status: 'pending',
      timestamp: Date.now() - 3600000 * 7,
      slaHoursLeft: 41,
      lat: 13.0405,
      lng: 80.2337,
      reportedBy: 'Chennai Citizen Alert',
      userId: 'user-501',
      upvotes: 41,
      upvotedBy: [],
      imageBefore: 'https://images.unsplash.com/photo-1528323273322-d81458248d40?w=800&auto=format&fit=crop&q=80',
      imageAfter: null,
      recommendedResource: 'GCC Compactor Unit',
      assignedWorker: 'GCC Zone 10 Team',
      rewardIssued: false,
      fineLevied: 0,
      comments: [
        { author: 'GCC Smart Control', text: 'Night compactor scheduled.', time: '4h ago' }
      ]
    },
    {
      id: 'ISS-2026-00142',
      state: 'Tamil Nadu',
      city: 'Chennai',
      ward: 'Marina Beach Zone',
      street: 'Kamarajar Salai',
      department: 'food_safety',
      deptName: 'Food Safety Department',
      deptIcon: '🍲',
      title: 'Stale Fish & Reheated Oil at Marina Beach Food Stalls',
      description: 'Marina Coastal Fish Fry Stalls: Street seafood stalls operating without refrigeration or oil testing kits.',
      location: 'Marina Beach Zone, Kamarajar Salai, Chennai',
      category: 'food_hygiene',
      categoryName: 'Seafood Safety Violation',
      categoryIcon: '🐟',
      severity: 'bulk',
      severityLabel: 'CRITICAL VIOLATION',
      status: 'pending',
      timestamp: Date.now() - 3600000 * 11,
      slaHoursLeft: 37,
      lat: 13.0500,
      lng: 80.2824,
      reportedBy: 'Dr. Lakshmi Prasad (FSO)',
      userId: 'food-01',
      vendorId: 'FSSAI-TN-2026-V03',
      vendorName: 'Marina Coastal Fish Fry Stalls',
      mq135GasPpm: 520,
      upvotes: 35,
      upvotedBy: [],
      imageBefore: 'https://images.unsplash.com/photo-1534482421-64566f976cfa?w=800&auto=format&fit=crop&q=80',
      imageAfter: null,
      recommendedResource: 'Tamil Nadu FDA Squad',
      assignedWorker: 'Chennai FSO Squad 3',
      rewardIssued: false,
      fineLevied: 5000,
      comments: [
        { author: 'TN FDA Officer', text: 'Critical Seizure Notice issued under Section 59. ₹5,000 fine levied.', time: '5h ago' }
      ]
    },

    // --- DELHI NCR ---
    {
      id: 'ISS-2026-00143',
      state: 'Delhi NCR',
      city: 'New Delhi',
      ward: 'Central Zone',
      street: 'Connaught Place Outer Circle',
      department: 'sanitation',
      deptName: 'Sanitation & Waste Management',
      deptIcon: '🏢',
      title: 'Broken Paver Tiles & Debris at CP Outer Circle',
      description: 'Cracked pedestrian tiles and loose rubble near Metro Gate 4 creating trip hazard.',
      location: 'Central Zone, Connaught Place Outer Circle, New Delhi',
      category: 'road_damage',
      categoryName: 'Pedestrian Safety Hazard',
      categoryIcon: '🚧',
      severity: 'medium',
      severityLabel: 'MEDIUM RISK',
      status: 'pending',
      timestamp: Date.now() - 3600000 * 3,
      slaHoursLeft: 45,
      lat: 28.6315,
      lng: 77.2167,
      reportedBy: 'Delhi Urban Watch',
      userId: 'user-601',
      upvotes: 49,
      upvotedBy: [],
      imageBefore: 'https://images.unsplash.com/photo-1578328819058-b69f3a3b0f6b?w=800&auto=format&fit=crop&q=80',
      imageAfter: null,
      recommendedResource: 'NDMC Civil Repair Unit',
      assignedWorker: 'NDMC Central Division',
      rewardIssued: false,
      fineLevied: 0,
      comments: [
        { author: 'NDMC Smart Portal', text: 'Work order allocated for repaving.', time: '2h ago' }
      ]
    },
    {
      id: 'ISS-2026-00144',
      state: 'Delhi NCR',
      city: 'New Delhi',
      ward: 'Karol Bagh Zone',
      street: 'Ajmal Khan Road',
      department: 'electricity',
      deptName: 'Smart Electricity Department',
      deptIcon: '⚡',
      title: 'Overloaded Commercial Transformer Sparking',
      description: 'High AC load causing loud hum and visible sparking at market sub-station.',
      location: 'Karol Bagh Zone, Ajmal Khan Road, New Delhi',
      category: 'transformer_damage',
      categoryName: 'Commercial Substation Hazard',
      categoryIcon: '⚡',
      severity: 'bulk',
      severityLabel: 'HIGH CRITICAL',
      status: 'in_progress',
      timestamp: Date.now() - 3600000 * 15,
      slaHoursLeft: 33,
      lat: 28.6521,
      lng: 77.1906,
      reportedBy: 'Karol Bagh Traders Guild',
      userId: 'user-602',
      upvotes: 81,
      upvotedBy: [],
      imageBefore: 'https://images.unsplash.com/photo-1509391365360-2e959784a276?w=800&auto=format&fit=crop&q=80',
      imageAfter: null,
      recommendedResource: 'BSES Emergency SCADA Squad',
      assignedWorker: 'BSES Central Squad 4',
      rewardIssued: false,
      fineLevied: 0,
      comments: [
        { author: 'BSES Dispatch', text: 'Load balancing transformer deployed.', time: '4h ago' }
      ]
    }
  ];

  // Full Registry of Both Certified & Violated Establishments
  const INITIAL_VENDORS = [
    // 🟢 Certified Vendors
    {
      id: 'FSSAI-AP-2026-089',
      state: 'Andhra Pradesh',
      city: 'Surampalem',
      ward: 'Ward 12 (Market Zone)',
      name: 'Annapurna Pure Veg Tiffins',
      owner: 'Venkata Rao',
      location: 'Main Road, Surampalem',
      hygieneGrade: 'A+',
      score: '96/100',
      validTill: '31 Dec 2026',
      inspectedBy: 'Dr. Lakshmi Prasad (FSO)',
      status: 'VERIFIED & CERTIFIED',
      isViolated: false
    },
    {
      id: 'FSSAI-AP-2026-112',
      state: 'Andhra Pradesh',
      city: 'Surampalem',
      ward: 'Ward 14 (Campus Zone)',
      name: 'Sai Balaji Fast Food & Juices',
      owner: 'M. Srinivas',
      location: 'College Campus Gate 2, Surampalem',
      hygieneGrade: 'A',
      score: '88/100',
      validTill: '15 Nov 2026',
      inspectedBy: 'Dr. Lakshmi Prasad (FSO)',
      status: 'VERIFIED & CERTIFIED',
      isViolated: false
    },
    // 🔴 Establishments with Official Statutory Violation Notices
    {
      id: 'FSSAI-AP-2026-V01',
      state: 'Andhra Pradesh',
      city: 'Surampalem',
      ward: 'Ward 12 (Market Zone)',
      name: 'Sri Krishna Seafood & Fast Food Point',
      owner: 'K. Durga Prasad',
      location: 'Market Gate Cross, Surampalem',
      hygieneGrade: 'C',
      score: '42/100',
      validTill: 'Action Required (48h SLA)',
      inspectedBy: 'Dr. Lakshmi Prasad (FSO)',
      status: 'VIOLATION NOTICE ISSUED',
      isViolated: true,
      violationClause: 'Section 56: Repeated / Burnt Cooking Oil (TPM 34%)',
      penaltyImposed: '₹2,000.00',
      rectificationDeadline: '27 Aug 2026',
      mq135GasPpm: '370 PPM (High Volatile Fumes)',
      officerDirectives: 'Discard all rancid oil batch immediately. Install TPM digital tester and oil filtration log.'
    },
    {
      id: 'FSSAI-AP-2026-V02',
      state: 'Andhra Pradesh',
      city: 'Surampalem',
      ward: 'Ward 14 (Campus Zone)',
      name: 'Campus Night Shawarma & Grills',
      owner: 'M. Farooq',
      location: 'College Road Food Court, Surampalem',
      hygieneGrade: 'C',
      score: '51/100',
      validTill: 'Action Required (7-Day Notice)',
      inspectedBy: 'Dr. Lakshmi Prasad (FSO)',
      status: 'VIOLATION NOTICE ISSUED',
      isViolated: true,
      violationClause: 'Section 58: Uncovered Food Prep adjacent to Open Drain',
      penaltyImposed: '₹500.00',
      rectificationDeadline: '30 Aug 2026',
      mq135GasPpm: '340 PPM',
      officerDirectives: 'Fit acrylic sneeze shield across display, install drain boundary cover, enforce chef caps and gloves.'
    },
    {
      id: 'FSSAI-TN-2026-V03',
      state: 'Tamil Nadu',
      city: 'Chennai',
      ward: 'Marina Beach Zone',
      name: 'Marina Coastal Fish Fry Stalls',
      owner: 'S. Murugan',
      location: 'Kamarajar Salai, Marina Beach, Chennai',
      hygieneGrade: 'F',
      score: '28/100',
      validTill: 'Immediate Seizure Notice',
      inspectedBy: 'Dr. Lakshmi Prasad (FSO)',
      status: 'CRITICAL SUSPENSION',
      isViolated: true,
      violationClause: 'Section 59: Unpreserved Stale Seafood & Toxic Cooking Oil',
      penaltyImposed: '₹5,000.00',
      rectificationDeadline: 'Immediate Commercial Closure',
      mq135GasPpm: '520 PPM (Severe Spoilage)',
      officerDirectives: 'Immediate confiscation of unchilled seafood stocks. Deep sanitation audit mandatory prior to reopening.'
    },
    {
      id: 'FSSAI-AP-2026-V04',
      state: 'Andhra Pradesh',
      city: 'Surampalem',
      ward: 'Ward 12 (Market Zone)',
      name: 'Aditya Highway Dhaba & Fast Food',
      owner: 'R. Koteswara Rao',
      location: 'Gandhi Statue Main Road, Surampalem',
      hygieneGrade: 'F',
      score: '24/100',
      validTill: 'SEIZED & SUSPENDED',
      inspectedBy: 'Dr. Lakshmi Prasad (FSO)',
      status: 'CRITICAL UNHYGIENIC VIOLATION',
      isViolated: true,
      violationClause: 'Section 59: Rotten Meat Storage, Reheated Stale Oil (TPM >36%) & Drain Adjacent Prep',
      penaltyImposed: '₹5,000.00',
      rectificationDeadline: 'Immediate Suspension & Seizure',
      mq135GasPpm: '580 PPM (Severe Toxic Ammonia Spoilage)',
      officerDirectives: 'Complete commercial closure order served. Kitchen sealed under FSSAI Section 38. Confiscation of contaminated food inventory.'
    },
  ];

  class DatabaseManager {
    constructor() {
      this.issues = this.loadFromStorage('clean_safe_issues_v10', INITIAL_ISSUES);
      this.vendors = this.loadFromStorage('clean_safe_vendors_v10', INITIAL_VENDORS);
      this.finesCollected = this.loadFromStorage('clean_safe_fines_v9', 2500);
      this.listeners = [];
      this.initBackend();
    }

    async initBackend() {
      try {
        const res = await fetch('/api/issues');
        if (res.ok) {
          const data = await res.json();
          if (data.issues && data.issues.length > 0) {
            this.issues = data.issues;
            this.saveToStorage('clean_safe_issues_v10', this.issues);
            this.notify();
          }
        }
      } catch (e) {
        console.log('[Backend] Local fallback active for issues');
      }

      try {
        const vRes = await fetch('/api/vendors');
        if (vRes.ok) {
          const vData = await vRes.json();
          if (vData.vendors && vData.vendors.length > 0) {
            this.vendors = vData.vendors;
            this.saveToStorage('clean_safe_vendors_v10', this.vendors);
            this.notify();
          }
        }
      } catch (e) {
        console.log('[Backend] Local fallback active for vendors');
      }
    }

    loadFromStorage(key, fallback) {
      try {
        const stored = localStorage.getItem(key);
        if (stored) return JSON.parse(stored);
      } catch (e) {
        console.warn('Storage load error:', e);
      }
      return fallback;
    }

    saveToStorage(key, data) {
      try {
        localStorage.setItem(key, JSON.stringify(data));
      } catch (e) {
        console.warn('Storage save error:', e);
      }
    }

    getAllIssues() {
      return [...this.issues];
    }

    getIssueById(id) {
      return this.issues.find(i => i.id === id);
    }

    getDailyReportLimit() {
      return 3;
    }

    getCitizenDailyReportsUsage() {
      const user = auth.getUser();
      const userId = user ? user.id : 'user-101';
      const userName = user ? user.name : 'KRISH';

      const now = new Date();
      const todayDateStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;

      // Count reports submitted today by this citizen across all departments (Food, Electricity, Sanitation/Waste)
      const todayReports = this.issues.filter(issue => {
        const isReporter = (issue.userId === userId) || (issue.reportedBy === userName);
        if (!isReporter) return false;

        const issueDate = new Date(issue.timestamp);
        const issueDateStr = `${issueDate.getFullYear()}-${String(issueDate.getMonth() + 1).padStart(2, '0')}-${String(issueDate.getDate()).padStart(2, '0')}`;
        return issueDateStr === todayDateStr;
      });

      const limit = this.getDailyReportLimit();
      const used = todayReports.length;
      const remaining = Math.max(0, limit - used);
      const isLimitReached = used >= limit;

      return {
        limit,
        used,
        remaining,
        isLimitReached,
        todayDateStr,
        todayReports
      };
    }

    createIssue(issueData) {
      // Enforce 3 Reports Per Day Limit for Citizens across all departments
      const isCitizen = (auth.getDepartment() === 'citizen') || (!auth.isAuthenticated());
      if (isCitizen) {
        const quota = this.getCitizenDailyReportsUsage();
        if (quota.isLimitReached) {
          throw new Error(`Daily Limit Reached: You have already submitted ${quota.used} of ${quota.limit} allowed reports today across all departments (Food, Electricity, Waste). Your daily quota resets at midnight.`);
        }
      }

      const id = 'ISS-2026-' + String(Math.floor(10000 + Math.random() * 90000));
      const now = Date.now();
      const slaDeadline = now + (48 * 3600 * 1000); // 48 Hours = 2 Days SLA Window

      const assignedSquad = issueData.department === 'electricity'
        ? 'Lineman Squad B (Suresh & Team)'
        : issueData.department === 'food_safety'
          ? 'Food Safety Officer (Dr. Lakshmi Prasad)'
          : (issueData.severity === 'bulk' ? 'Sanitation Compactor Squad 4 (Lead: Ramesh K.)' : 'Collection Squad 2 (AP-05-TX)');

      const newIssue = {
        id: id,
        timestamp: now,
        slaDeadline: slaDeadline,
        resolvedTimestamp: null,
        status: 'pending',
        slaHoursLeft: 48,
        upvotes: 1,
        upvotedBy: [auth.getUser() ? auth.getUser().id : 'user-101'],
        reportedBy: auth.getUser() ? auth.getUser().name : 'KRISH',
        userId: auth.getUser() ? auth.getUser().id : 'user-101',
        verifiedByOfficer: 'Consultant Officer K. Mukundha (GOV-MUNC-SEC-012)',
        verifiedTimestamp: now + (15 * 60 * 1000),
        assignedWorker: assignedSquad,
        assignedTimestamp: now + (35 * 60 * 1000),
        workerStatus: 'Dispatched & En Route to Site',
        isSlaBreached: false,
        comments: [
          { author: 'System Watchdog', text: 'Report logged with live GPS geotag. 48h SLA timer activated.', time: 'Just now' },
          { author: 'Consultant Officer K. Mukundha', text: 'Grievance verified. Squad allocated and dispatched.', time: 'Just now' }
        ],
        recommendedResource: issueData.severity === 'bulk' ? 'Tractor / Heavy Squad' : issueData.severity === 'medium' ? 'Collection Truck' : 'Pushcart & Worker',
        rewardIssued: false,
        fineLevied: 0,
        ...issueData
      };

      this.issues.unshift(newIssue);
      this.saveToStorage('clean_safe_issues_v10', this.issues);
      this.notify();
      broadcastRealtimeEvent('ISSUE_CREATED', newIssue);

      // Async persist to SQLite Backend
      fetch('/api/issues', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newIssue)
      }).catch(e => console.log('Backend sync offline:', e));

      return newIssue;
    }

    resolveIssue(issueId, resolutionNotes, photoAfter) {
      const issue = this.getIssueById(issueId);
      if (!issue) return null;

      issue.status = 'resolved';
      issue.resolvedTimestamp = Date.now();
      issue.slaHoursLeft = 0;
      issue.workerStatus = 'Field Execution Completed & Cleaned Proof Uploaded';
      issue.imageAfter = photoAfter || 'https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=800&auto=format&fit=crop&q=80';
      issue.rewardIssued = true;
      issue.comments.push({
        author: auth.getUser() ? auth.getUser().name : 'Field Officer',
        text: 'Issue resolved: ' + resolutionNotes,
        time: 'Just now'
      });

      this.saveToStorage('clean_safe_issues_v10', this.issues);

      // Award +50 Civic Credits and update user session
      const history = this.loadFromStorage('clean_safe_credits_history_v9', []);
      history.unshift({
        id: 'CRD-' + Date.now(),
        title: 'Verified Resolution: ' + issue.title,
        points: 50,
        date: new Date().toLocaleDateString(),
        status: 'Credited to Civic Standing'
      });
      this.saveToStorage('clean_safe_credits_history_v9', history);

      if (auth.isAuthenticated() && auth.getDepartment() === 'citizen') {
        const user = auth.getUser();
        user.civicCredits = (user.civicCredits || 150) + 50;
        auth.saveSession({ ...auth.session, user });
      }

      this.notify();
      broadcastRealtimeEvent('ISSUE_RESOLVED', issue);

      // Async persist resolution to SQLite Backend
      fetch('/api/issues/' + issueId + '/resolve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          notes: resolutionNotes,
          photoAfter: issue.imageAfter,
          officerName: auth.getUser() ? auth.getUser().name : 'Field Officer'
        })
      }).catch(e => console.log('Backend resolve offline:', e));

      return issue;
    }

    rectifyFoodIssue(issueId, notes, gasPpm, score, outcome) {
      const issue = this.getIssueById(issueId);
      if (!issue) return null;

      issue.status = 'resolved';
      issue.imageAfter = 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800&auto=format&fit=crop&q=80';
      issue.comments.push({
        author: 'Dr. Lakshmi Prasad (FSO)',
        text: `Re-inspected & Rectified! Gas Reading: ${gasPpm} PPM | Hygiene Score: ${score}/100. Outcome: ${outcome === 'passed' ? 'Compliant & Cleared (Grade A+ Issued)' : 'Probation Extended'}`,
        time: 'Just now'
      });

      // Update matching vendor in vendor directory
      const vName = issue.vendorName || issue.title;
      const vendor = this.vendors.find(v => (issue.vendorId && v.id === issue.vendorId) || (vName && vName.includes(v.name)));
      if (vendor) {
        if (outcome === 'passed') {
          vendor.isViolated = false;
          vendor.hygieneGrade = 'A+';
          vendor.score = `${score}/100`;
          vendor.status = 'VERIFIED & CERTIFIED';
          vendor.validTill = '31 Dec 2026';
        }
      }

      this.saveToStorage('clean_safe_issues_v10', this.issues);
      this.saveToStorage('clean_safe_vendors_v10', this.vendors);
      this.notify();
      broadcastRealtimeEvent('FOOD_RECTIFIED', issue);

      // Async persist to SQLite Backend
      fetch('/api/food-rectify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ issueId, notes, gasPpm, score, outcome })
      }).catch(e => console.log('Backend food rectify offline:', e));

      return issue;
    }

    addComment(issueId, text, author) {
      const issue = this.getIssueById(issueId);
      if (!issue) return null;
      if (!issue.comments) issue.comments = [];
      const newComment = {
        author: author || (auth.getUser() ? auth.getUser().name : 'Citizen Resident'),
        text: (text || '').trim(),
        time: 'Just now'
      };
      issue.comments.push(newComment);
      this.saveToStorage('clean_safe_issues_v10', this.issues);
      this.notify();
      broadcastRealtimeEvent('COMMENT_ADDED', { issueId, comment: newComment });

      // Async persist comment to backend
      fetch('/api/issues/' + issueId + '/comment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newComment)
      }).catch(e => console.log('Comment offline sync:', e));

      return newComment;
    }

    logFoodViolation(data) {
      const fineAmount = parseInt(data.fineAmount, 10) || 500;
      const vendorId = 'FSSAI-' + (data.state === 'Andhra Pradesh' ? 'AP' : 'IND') + '-2026-V' + Math.floor(10 + Math.random() * 90);

      // Create new vendor entry under violation
      const newVendor = {
        id: vendorId,
        state: data.state,
        city: data.city,
        ward: data.ward,
        name: data.vendorName,
        owner: data.ownerName,
        location: `${data.street}, ${data.ward}, ${data.city}`,
        hygieneGrade: 'C',
        score: '45/100',
        validTill: 'Action Required (Statutory Notice)',
        inspectedBy: 'Dr. Lakshmi Prasad (FSO)',
        status: 'VIOLATION NOTICE ISSUED',
        isViolated: true,
        violationClause: data.violationClause,
        penaltyImposed: `₹${fineAmount.toLocaleString('en-IN')}.00`,
        rectificationDeadline: '7 Days from Notice',
        mq135GasPpm: '360 PPM (High Gas Risk)',
        officerDirectives: data.notes
      };

      this.vendors.unshift(newVendor);
      this.finesCollected = (this.finesCollected || 2500) + fineAmount;

      // Also create an official incident ticket for FSO triage
      const newIssue = this.createIssue({
        state: data.state,
        city: data.city,
        ward: data.ward,
        street: data.street,
        department: 'food_safety',
        deptName: 'Food Safety Department',
        deptIcon: '🍲',
        title: `Food Hygiene Violation: ${data.vendorName}`,
        description: `Official FSSAI Notice: ${data.violationClause}. ${data.notes}`,
        location: `${data.ward}, ${data.street}, ${data.city}`,
        category: 'food_hygiene',
        categoryName: 'Food Hygiene Violation',
        categoryIcon: '🍲',
        severity: fineAmount > 1000 ? 'bulk' : 'medium',
        severityLabel: 'VIOLATION ON NOTICE',
        vendorId: vendorId,
        vendorName: data.vendorName,
        mq135GasPpm: 360,
        imageBefore: 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800&auto=format&fit=crop&q=80',
        assignedWorker: 'Food Safety Officer (Dr. Lakshmi Prasad)',
        fineLevied: fineAmount
      });

      this.saveToStorage('clean_safe_vendors_v10', this.vendors);
      this.saveToStorage('clean_safe_fines_v9', this.finesCollected);
      this.notify();
      broadcastRealtimeEvent('FOOD_VIOLATION_LOGGED', { issue: newIssue, vendor: newVendor });

      // Async persist to SQLite Backend
      fetch('/api/food-violations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      }).catch(e => console.log('Backend food violation offline:', e));

      return { issue: newIssue, vendor: newVendor };
    }

    addFine(amount) {
      this.finesCollected = (this.finesCollected || 2500) + amount;
      this.saveToStorage('clean_safe_fines_v9', this.finesCollected);
      this.notify();
    }

    toggleUpvote(issueId) {
      const issue = this.getIssueById(issueId);
      if (!issue) return null;

      const userId = auth.getUser() ? auth.getUser().id : 'user-101';
      issue.upvotedBy = issue.upvotedBy || [];

      if (issue.upvotedBy.includes(userId)) {
        issue.upvotedBy = issue.upvotedBy.filter(id => id !== userId);
        issue.upvotes = Math.max(0, (issue.upvotes || 1) - 1);
      } else {
        issue.upvotedBy.push(userId);
        issue.upvotes = (issue.upvotes || 0) + 1;
      }

      this.saveToStorage('clean_safe_issues_v10', this.issues);
      this.notify();
      broadcastRealtimeEvent('ISSUE_UPVOTED', issue);
      return issue;
    }

    getAllVendors() {
      return [...this.vendors];
    }

    getMetrics() {
      const total = this.issues.length;
      const resolved = this.issues.filter(i => i.status === 'resolved').length;
      return {
        total,
        resolved,
        resolutionRate: total ? Math.round((resolved / total) * 100) : 0,
        totalRewardsPaid: resolved * 50 + ' Pts',
        totalFinesCollected: this.finesCollected || 2500
      };
    }

    subscribe(cb) {
      this.listeners.push(cb);
    }

    notify() {
      this.listeners.forEach(cb => cb(this.issues));
    }
  }

  const db = new DatabaseManager();

  // =========================================================================
  // 4. GIS MAP MANAGER
  // =========================================================================
  let gisMapInstance = null;

  function initGISMap(targetCoords, zoomLevel) {
    const container = document.getElementById('gisMapContainer');
    if (!container) return;

    if (typeof L === 'undefined') {
      container.innerHTML = `
        <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100%; color:#38bdf8; text-align:center; padding:2rem;">
          <div style="font-size:3rem; margin-bottom:1rem;">🗺️</div>
          <div style="font-weight:800; font-size:1.2rem; color:white;">GIS RED-ZONE HEATMAP READY</div>
          <p style="color:#94a3b8; font-size:0.9rem; max-width:400px; margin-top:0.5rem;">
            Ward 12 Central Market Junction: High-frequency littering & sparking transformer identified as Active Red Zone.
          </p>
        </div>
      `;
      return;
    }

    const center = targetCoords || [17.0010, 81.8045];
    const zoom = zoomLevel || 14;

    try {
      if (gisMapInstance) {
        gisMapInstance.setView(center, zoom);
        setTimeout(() => { if (gisMapInstance) gisMapInstance.invalidateSize(); }, 50);
        return;
      }

      gisMapInstance = L.map('gisMapContainer', {
        zoomControl: true,
        scrollWheelZoom: true
      }).setView(center, zoom);

      // Dark Tiles
      L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap, © CARTO'
      }).addTo(gisMapInstance);

      // Red-Zone Hazard Perimeter
      const redZone = L.circle([17.0005, 81.8040], {
        radius: 350,
        color: '#f43f5e',
        fillColor: '#f43f5e',
        fillOpacity: 0.25,
        weight: 2,
        dashArray: '6, 6'
      }).addTo(gisMapInstance);

      redZone.bindPopup(`
        <div style="color: #0f172a; font-family: sans-serif; padding: 4px;">
          <div style="font-weight: 800; font-size: 1rem; color: #e11d48;">🚨 ACTIVE RED ZONE #12</div>
          <div style="font-size: 0.8rem; color: #475569; margin-top: 2px;">Ward 12 Market Junction</div>
          <div style="font-size: 0.75rem; margin-top: 4px; font-weight: 700; color: #0284c7;">High Priority: Active Complaints</div>
        </div>
      `);

      // Plot All Issues
      const issues = db.getAllIssues();
      issues.forEach(issue => {
        if (issue.lat && issue.lng) {
          const markerColor = issue.department === 'electricity' ? '#0284c7' : issue.department === 'food_safety' ? '#d97706' : '#059669';
          
          const circle = L.circleMarker([issue.lat, issue.lng], {
            radius: issue.severity === 'bulk' ? 14 : 10,
            fillColor: markerColor,
            color: '#ffffff',
            weight: 2.5,
            opacity: 1,
            fillOpacity: 0.9
          }).addTo(gisMapInstance);

          circle.bindPopup(`
            <div style="color: #0f172a; font-family: sans-serif; min-width: 190px;">
              <div style="font-weight: 800; font-size: 0.95rem; margin-bottom: 2px;">${issue.title}</div>
              <div style="font-size: 0.78rem; color: #64748b; margin-bottom: 6px;">📍 ${issue.location}</div>
              <div style="display:flex; justify-content:space-between; align-items:center; font-size: 0.75rem; font-weight: 700; color: ${markerColor};">
                <span>${issue.deptName}</span>
                <span style="background:#f1f5f9; padding:2px 6px; border-radius:4px;">${issue.severity.toUpperCase()}</span>
              </div>
            </div>
          `);
        }
      });

      // Plot Live Moving Fleet with Real-Time Animation
      const fleetData = [
        { name: 'Collection Truck AP-05-TX', type: '🚛', lat: 17.0035, lng: 81.8025, status: 'Moving (24 km/h)' },
        { name: 'Lineman Van AP-05-EB', type: '⚡', lat: 17.0018, lng: 81.8080, status: 'En Route to Feeder 4' },
        { name: 'Compactor Tractor AP-05-CT', type: '🚜', lat: 16.9990, lng: 81.8050, status: 'Compacting at Dump Site' }
      ];

      activeFleetMarkers = [];
      fleetData.forEach((v, idx) => {
        const vehicleMarker = L.circleMarker([v.lat, v.lng], {
          radius: 12,
          fillColor: '#38bdf8',
          color: '#ffffff',
          weight: 3,
          fillOpacity: 1
        }).addTo(gisMapInstance);

        vehicleMarker.bindPopup(`
          <div style="color: #0f172a; font-family: sans-serif;">
            <div style="font-weight: 900; font-size: 0.95rem; color: #0284c7;">${v.type} ${v.name}</div>
            <div style="font-size: 0.8rem; color: #475569; margin-top: 2px;">Status: <strong>${v.status}</strong></div>
            <div style="font-size: 0.72rem; color: #10b981; margin-top: 2px;">📡 Live GPS Geotag Active</div>
          </div>
        `);
        activeFleetMarkers.push({ marker: vehicleMarker, baseLat: v.lat, baseLng: v.lng, idx });
      });

      setTimeout(() => { if (gisMapInstance) gisMapInstance.invalidateSize(); }, 80);
      setTimeout(() => { if (gisMapInstance) gisMapInstance.invalidateSize(); }, 300);
    } catch (err) {
      console.warn("GIS Map error:", err);
    }
  }

  // Real-Time Moving Fleet GPS Loop
  let activeFleetMarkers = [];
  let fleetAnimStep = 0;
  setInterval(() => {
    if (!gisMapInstance || activeFleetMarkers.length === 0) return;
    fleetAnimStep = (fleetAnimStep + 1) % 360;
    activeFleetMarkers.forEach(item => {
      const offsetLat = Math.sin((fleetAnimStep + item.idx * 90) * Math.PI / 180) * 0.0008;
      const offsetLng = Math.cos((fleetAnimStep + item.idx * 90) * Math.PI / 180) * 0.001;
      item.marker.setLatLng([item.baseLat + offsetLat, item.baseLng + offsetLng]);
    });
  }, 2500);

  // =========================================================================
  // 5. GEOSPATIAL 4-TIER CASCADING FILTERS & STATE ENGINE
  // =========================================================================
  let selectedState = 'Andhra Pradesh';
  let selectedCity = 'Surampalem';
  let selectedWard = 'all';
  let selectedStreet = 'all';
  let citizenCategoryFilter = 'all';
  let foodFilter = 'all';
  let vendorFilter = 'all';
  let searchQuery = '';
  let activeIssueIdForModal = null;
  let activeAuthDept = 'citizen';

  function showToast(message, type, icon) {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = 'toast ' + (type === 'reward' ? 'toast-reward' : type === 'error' ? 'toast-error' : '');
    toast.innerHTML = `
      <div style="display: flex; align-items: center; gap: 0.75rem;">
        <span style="font-size: 1.25rem;">${icon || '🔔'}</span>
        <div>
          <div style="font-weight: 700; font-size: 0.9rem; color: #f8fafc;">${message}</div>
        </div>
      </div>
      <button style="background: none; border: none; font-size: 1.1rem; cursor: pointer; color: #94a3b8;" onclick="this.parentElement.remove()">✕</button>
    `;

    container.appendChild(toast);
    setTimeout(() => { if (toast.parentElement) toast.remove(); }, 4500);
  }

  // =========================================================================
  // REAL-TIME BROADCAST SYNCHRONIZATION & AUDIO CHIME ENGINE
  // =========================================================================
  let realtimeSyncChannel = null;
  try {
    if ('BroadcastChannel' in window) {
      realtimeSyncChannel = new BroadcastChannel('clean_safe_india_realtime');
      realtimeSyncChannel.onmessage = (event) => {
        handleRealtimeIncomingEvent(event.data);
      };
    }
  } catch (e) {
    console.warn('BroadcastChannel not supported:', e);
  }

  // Cross-tab storage event listener fallback
  window.addEventListener('storage', (e) => {
    if (e.key === 'csi_realtime_broadcast' && e.newValue) {
      try {
        const data = JSON.parse(e.newValue);
        handleRealtimeIncomingEvent(data);
      } catch (err) {}
    }
  });

  function broadcastRealtimeEvent(type, payload) {
    const packet = {
      type,
      payload,
      timestamp: Date.now(),
      sender: auth.getUser() ? auth.getUser().name : 'System Watchdog'
    };
    if (realtimeSyncChannel) {
      try { realtimeSyncChannel.postMessage(packet); } catch (e) {}
    }
    try {
      localStorage.setItem('csi_realtime_broadcast', JSON.stringify(packet));
    } catch (e) {}
  }

  function playNotificationSound(type = 'chime') {
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx) return;
      const ctx = new AudioCtx();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);

      if (type === 'alert') {
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(440, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.15);
      } else {
        osc.type = 'sine';
        osc.frequency.setValueAtTime(523.25, ctx.currentTime); // C5
        osc.frequency.exponentialRampToValueAtTime(659.25, ctx.currentTime + 0.1); // E5
        osc.frequency.exponentialRampToValueAtTime(783.99, ctx.currentTime + 0.22); // G5
      }

      gain.gain.setValueAtTime(0.12, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.35);
      osc.start();
      osc.stop(ctx.currentTime + 0.35);
    } catch (e) {}
  }

  function handleRealtimeIncomingEvent(packet) {
    if (!packet || !packet.type) return;

    if (packet.type === 'ISSUE_CREATED') {
      const issue = packet.payload;
      const existing = db.issues.find(i => i.id === issue.id);
      if (!existing) {
        db.issues.unshift(issue);
        db.saveToStorage('clean_safe_issues_v10', db.issues);
        db.notify();
      }
      showToast(`🚨 New Complaint #${issue.id} reported in ${issue.ward || 'Ward'}!`, 'info', '📢');
      playNotificationSound('chime');
      renderCitizenDashboard();
      renderMunicipalDashboard();
      renderFoodSafetyDashboard();
    } else if (packet.type === 'ISSUE_RESOLVED') {
      const updated = packet.payload;
      const idx = db.issues.findIndex(i => i.id === updated.id);
      if (idx !== -1) {
        db.issues[idx] = { ...db.issues[idx], ...updated };
      } else {
        db.issues.unshift(updated);
      }
      db.saveToStorage('clean_safe_issues_v10', db.issues);
      db.notify();
      showToast(`✅ Complaint #${updated.id} resolved by field team!`, 'reward', '🎉');
      playNotificationSound('chime');
      renderCitizenDashboard();
      renderMunicipalDashboard();
      renderFoodSafetyDashboard();
    } else if (packet.type === 'FOOD_VIOLATION_LOGGED') {
      if (packet.payload && packet.payload.vendor) {
        const v = packet.payload.vendor;
        const vExisting = db.vendors.find(x => x.id === v.id);
        if (!vExisting) {
          db.vendors.unshift(v);
          db.saveToStorage('clean_safe_vendors_v10', db.vendors);
        }
      }
      db.notify();
      showToast(`⚖️ FSSAI Notice logged for ${packet.payload.vendor ? packet.payload.vendor.name : 'Establishment'}!`, 'error', '🍲');
      playNotificationSound('alert');
      renderFoodSafetyDashboard();
    } else if (packet.type === 'FOOD_RECTIFIED') {
      const rIssue = db.issues.find(i => i.id === packet.payload.issueId);
      if (rIssue) rIssue.status = 'resolved';
      db.notify();
      showToast(`🏆 Grievance rectified & certified Grade A+!`, 'reward', '✅');
      playNotificationSound('chime');
      renderFoodSafetyDashboard();
    } else if (packet.type === 'ISSUE_UPVOTED') {
      const uIssue = db.issues.find(i => i.id === packet.payload.id);
      if (uIssue) uIssue.upvotes = packet.payload.upvotes;
      db.notify();
      renderCitizenDashboard();
    } else if (packet.type === 'FLEET_GPS_STREAM') {
      // Live moving vehicle GPS positions from server
      if (typeof updateFleetGPSMarkers === 'function') {
        updateFleetGPSMarkers(packet.payload);
      }
    }
  }

  // Real-Time Server-Sent Events (SSE) Live Connection to Python Backend
  function initRealtimeSSE() {
    if (!window.EventSource) return;
    try {
      const eventSource = new EventSource('/api/stream');
      eventSource.onopen = function() {
        console.log('⚡ [Real-Time SSE Hub] Connected to live backend stream!');
      };
      eventSource.onmessage = function(e) {
        try {
          const packet = JSON.parse(e.data);
          handleRealtimeIncomingEvent(packet);
        } catch (err) {}
      };
      eventSource.onerror = function() {
        // Automatic reconnection built into browser EventSource
      };
    } catch (e) {
      console.warn('SSE connection skipped:', e);
    }
  }

  // =========================================================================
  // LIVE 1-SECOND SLA COUNTDOWN ENGINE
  // =========================================================================
  function startLiveSLATimerEngine() {
    setInterval(() => {
      const now = Date.now();
      document.querySelectorAll('.sla-live-ticker').forEach(el => {
        const deadline = parseInt(el.dataset.deadline, 10);
        if (!deadline) return;
        const diff = deadline - now;
        if (diff <= 0) {
          el.innerHTML = '<span style="color: #f87171; font-weight: 800;">🚨 48h SLA BREACHED — ESCALATED</span>';
        } else {
          const hours = Math.floor(diff / (1000 * 60 * 60));
          const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
          const secs = Math.floor((diff % (1000 * 60)) / 1000);
          el.textContent = `⏱️ ${hours}h ${mins}m ${secs}s remaining`;
        }
      });
    }, 1000);
  }

  // =========================================================================
  // PWA SERVICE WORKER & 1-TAP INSTALLATION PROMPT
  // =========================================================================
  let deferredPWAInstallPrompt = null;

  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('./sw.js')
        .then(reg => console.log('[PWA] ServiceWorker registered with scope:', reg.scope))
        .catch(err => console.warn('[PWA] ServiceWorker registration failed:', err));
    });
  }

  function isStandaloneApp() {
    return window.matchMedia('(display-mode: standalone)').matches ||
           window.navigator.standalone === true ||
           document.referrer.includes('android-app://');
  }

  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    if (isStandaloneApp()) return;
    deferredPWAInstallPrompt = e;
    document.querySelectorAll('.btn-install-pwa').forEach(btn => {
      btn.style.display = 'inline-flex';
    });
  });

  window.triggerPWAInstall = function() {
    if (isStandaloneApp()) {
      showToast('App is already installed and running in standalone mode!', 'info', '📲');
      return;
    }

    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    if (isIOS) {
      const modal = document.getElementById('iosInstallModal');
      if (modal) modal.classList.add('active');
      return;
    }

    const helpModal = document.getElementById('appInstallHelpModal');
    if (helpModal) {
      helpModal.classList.add('active');
    }
  };

  window.executeDirectPWAInstall = async function() {
    if (deferredPWAInstallPrompt) {
      deferredPWAInstallPrompt.prompt();
      const choice = await deferredPWAInstallPrompt.userChoice;
      if (choice.outcome === 'accepted') {
        showToast('Installing Clean & Safe India App...', 'reward', '📲');
        const helpModal = document.getElementById('appInstallHelpModal');
        if (helpModal) helpModal.classList.remove('active');
      }
      deferredPWAInstallPrompt = null;
    } else {
      showToast('To install directly: Click the Install Icon (⊕) on the right side of your Chrome/Edge address bar, or Menu (⋮) → Install App.', 'info', '💡');
    }
  };

  window.downloadDesktopShortcut = function() {
    const url = window.location.href.split('#')[0].split('?')[0];
    const content = `[InternetShortcut]\nURL=${url}\nIconIndex=0\nIconFile=${url}assets/icon-192.png\n`;
    const blob = new Blob([content], { type: 'application/octet-stream' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'CleanAndSafeIndia.url';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    showToast('Desktop Shortcut (.url) downloaded! Save it on your desktop to launch in 1 click.', 'reward', '💻');
  };

  // Cascading Dropdown Populators
  // Cascading Dropdown Populators for Citizen, Municipal & Food Safety Portals
  function updateAllGeoSelects(type, html, value) {
    const ids = {
      state: ['geoStateSelect', 'geoStateSelect_mun', 'geoStateSelect_food'],
      city: ['geoCitySelect', 'geoCitySelect_mun', 'geoCitySelect_food'],
      ward: ['geoWardSelect', 'geoWardSelect_mun', 'geoWardSelect_food'],
      street: ['geoStreetSelect', 'geoStreetSelect_mun', 'geoStreetSelect_food']
    };

    (ids[type] || []).forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        if (html !== undefined) el.innerHTML = html;
        if (value !== undefined) el.value = value;
      }
    });
  }

  window.handleGeoStateChange = function(state) {
    selectedState = state;
    updateAllGeoSelects('state', undefined, state);

    if (state === 'all') {
      updateAllGeoSelects('city', '<option value="all">All Cities</option>', 'all');
      updateAllGeoSelects('ward', '<option value="all">All Wards / Zones</option>', 'all');
      updateAllGeoSelects('street', '<option value="all">All Streets</option>', 'all');
      selectedCity = 'all';
      selectedWard = 'all';
      selectedStreet = 'all';
    } else {
      const cities = GEOSPATIAL_DIRECTORY[state] || {};
      const cityNames = Object.keys(cities);
      const cityHtml = '<option value="all">All Cities</option>' + cityNames.map(c => `<option value="${c}">${c}</option>`).join('');
      selectedCity = cityNames[0] || 'all';
      updateAllGeoSelects('city', cityHtml, selectedCity);
      window.handleGeoCityChange(selectedCity);
    }

    renderCitizenDashboard();
    renderMunicipalDashboard();
    renderFoodSafetyDashboard();
  };

  window.handleGeoCityChange = function(city) {
    selectedCity = city;
    updateAllGeoSelects('city', undefined, city);

    if (city === 'all' || !GEOSPATIAL_DIRECTORY[selectedState] || !GEOSPATIAL_DIRECTORY[selectedState][city]) {
      updateAllGeoSelects('ward', '<option value="all">All Wards / Zones</option>', 'all');
      updateAllGeoSelects('street', '<option value="all">All Streets</option>', 'all');
      selectedWard = 'all';
      selectedStreet = 'all';
    } else {
      const cityData = GEOSPATIAL_DIRECTORY[selectedState][city];
      const wardNames = Object.keys(cityData.wards || {});
      const wardHtml = '<option value="all">All Wards / Zones</option>' + wardNames.map(w => `<option value="${w}">${w}</option>`).join('');
      selectedWard = wardNames[0] || 'all';
      updateAllGeoSelects('ward', wardHtml, selectedWard);
      window.handleGeoWardChange(selectedWard);

      // Re-center map if open
      if (cityData.coords) {
        initGISMap(cityData.coords, 14);
      }
    }

    renderCitizenDashboard();
    renderMunicipalDashboard();
    renderFoodSafetyDashboard();
  };

  window.handleGeoWardChange = function(ward) {
    selectedWard = ward;
    updateAllGeoSelects('ward', undefined, ward);

    if (ward === 'all' || !GEOSPATIAL_DIRECTORY[selectedState] || !GEOSPATIAL_DIRECTORY[selectedState][selectedCity]) {
      updateAllGeoSelects('street', '<option value="all">All Streets</option>', 'all');
      selectedStreet = 'all';
    } else {
      const streets = GEOSPATIAL_DIRECTORY[selectedState][selectedCity].wards[ward] || [];
      const streetHtml = '<option value="all">All Streets / Landmarks</option>' + streets.map(s => `<option value="${s}">${s}</option>`).join('');
      selectedStreet = 'all';
      updateAllGeoSelects('street', streetHtml, selectedStreet);
    }

    renderCitizenDashboard();
    renderMunicipalDashboard();
    renderFoodSafetyDashboard();
  };

  window.handleGeoStreetChange = function(street) {
    selectedStreet = street;
    updateAllGeoSelects('street', undefined, street);
    renderCitizenDashboard();
    renderMunicipalDashboard();
    renderFoodSafetyDashboard();
  };

  // Modal State / City / Ward change
  window.handleModalStateChange = function(state) {
    const citySelect = document.getElementById('modalReportCity');
    const wardSelect = document.getElementById('modalReportWard');
    if (!citySelect || !wardSelect) return;

    const cities = GEOSPATIAL_DIRECTORY[state] || {};
    const cityNames = Object.keys(cities);
    citySelect.innerHTML = cityNames.map(c => `<option value="${c}">${c}</option>`).join('');
    window.handleModalCityChange(cityNames[0]);
  };

  window.handleModalCityChange = function(city) {
    const state = document.getElementById('modalReportState').value;
    const wardSelect = document.getElementById('modalReportWard');
    if (!wardSelect) return;

    const cityData = (GEOSPATIAL_DIRECTORY[state] || {})[city];
    const wardNames = Object.keys(cityData ? cityData.wards : {});
    wardSelect.innerHTML = wardNames.map(w => `<option value="${w}">${w}</option>`).join('');
  };

  // =========================================================================
  // 6. UI RENDERER & ROUTER
  // =========================================================================
  function renderCardHTML(issue) {
    const isResolved = issue.status === 'resolved';
    const isEscalated = issue.status === 'escalated' || issue.isSlaBreached;
    const reportedTimeStr = formatReportDateTime(issue.timestamp);
    const deadlineTimestamp = issue.slaDeadline || (issue.timestamp + 48 * 3600 * 1000);
    const deadlineTimeStr = formatReportDateTime(deadlineTimestamp);
    const resolvedTs = isResolved ? getRealisticResolvedTimestamp(issue) : null;
    const resolvedTimeStr = isResolved ? formatReportDateTime(resolvedTs) : null;
    const turnaroundStr = isResolved ? calculateSlaTurnaround(issue.timestamp, resolvedTs, issue) : null;

    const slaText = isResolved 
      ? `✅ Resolved (${turnaroundStr})` 
      : isEscalated 
        ? `🚨 SLA Breached (>48h)` 
        : `<span class="sla-live-ticker" data-deadline="${deadlineTimestamp}">⏱️ ${issue.slaHoursLeft}h SLA left</span>`;

    return `
      <div class="issue-card" onclick="window.viewIssueDetail('${issue.id}')">
        <div class="issue-card-media">
          <img src="${issue.imageBefore}" class="issue-card-img" alt="${issue.title}" loading="lazy">
          <div class="issue-floating-badges">
            <span class="badge badge-${issue.status}">${issue.status.replace('_', ' ')}</span>
            <span class="issue-sla-pill ${isEscalated ? 'text-danger' : ''}">${slaText}</span>
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

          <!-- Exact Date & Time Tracking Grid -->
          <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid var(--border); padding: 0.5rem 0.65rem; border-radius: var(--radius-sm); font-size: 0.76rem; color: #cbd5e1; margin-bottom: 0.85rem; line-height: 1.45;">
            <div>📅 <strong>Reported:</strong> ${reportedTimeStr}</div>
            ${isResolved ? `
              <div style="color: #34d399;">✅ <strong>Resolved:</strong> ${resolvedTimeStr} (${turnaroundStr})</div>
            ` : isEscalated ? `
              <div style="color: #f87171; font-weight: 700;">🚨 <strong>SLA Breached:</strong> Forwarded to Zonal Commissioner</div>
            ` : `
              <div style="color: #38bdf8;">⏳ <strong>48h Deadline:</strong> ${deadlineTimeStr}</div>
            `}
          </div>

          <div class="issue-card-footer">
            <button type="button" class="btn-track-issue" onclick="event.stopPropagation(); window.viewIssueDetail('${issue.id}');">
              <span>📦</span>
              <span>Track Live Status</span>
            </button>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
              <button type="button" class="upvote-btn" onclick="event.stopPropagation(); window.toggleUpvote('${issue.id}');" title="Upvote issue priority">
                <span>👍</span>
                <span>${issue.upvotes || 0}</span>
              </button>
              <button type="button" class="comment-btn" onclick="event.stopPropagation(); window.openCommentsModal('${issue.id}');" title="View discussion and remarks" style="background: rgba(255,255,255,0.06); border: 1px solid var(--border); color: #cbd5e1; border-radius: 20px; padding: 4px 10px; cursor: pointer; display: flex; align-items: center; gap: 4px; font-size: 0.78rem; transition: all 0.2s;">
                <span>💬</span>
                <span>${(issue.comments || []).length}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  // Update Citizen Daily Quota Status (3 Reports / Day Rule)
  function updateCitizenDailyQuotaUI() {
    const quota = db.getCitizenDailyReportsUsage();

    // 1. Topbar Daily Quota Pill
    const pill = document.getElementById('citizenDailyQuotaPill');
    const topText = document.getElementById('citizenQuotaTopText');
    const topBtn = document.getElementById('citizenTopReportBtn');

    if (topText) {
      topText.textContent = quota.isLimitReached ? `0/3 Left Today (Full)` : `${quota.remaining}/3 Left Today`;
    }
    if (pill) {
      pill.className = `daily-quota-topbar-pill ${quota.isLimitReached ? 'quota-full' : ''}`;
      pill.title = `Daily Limit: ${quota.used}/${quota.limit} used today. Resets at midnight.`;
    }
    if (topBtn) {
      topBtn.title = quota.isLimitReached ? 'Daily reporting quota reached (3/3 submitted today)' : `Click to report (${quota.remaining}/3 daily reports left)`;
    }

    // 2. Modal Daily Quota Banner & Slot Pills
    const banner = document.getElementById('modalDailyQuotaBanner');
    const quotaText = document.getElementById('modalQuotaText');
    const quotaTitle = document.getElementById('modalQuotaTitle');
    const quotaSub = document.getElementById('modalQuotaSub');
    const submitBtn = document.getElementById('reportSubmitBtn');

    if (quotaText) {
      quotaText.textContent = `${quota.remaining} / ${quota.limit} Remaining`;
      quotaText.style.color = quota.isLimitReached ? '#f87171' : '#38bdf8';
    }

    if (banner) {
      if (quota.isLimitReached) {
        banner.classList.add('quota-exhausted');
        if (quotaTitle) quotaTitle.innerHTML = `<span>🚨</span> Daily Citizen Limit Reached (3/3 Used Today)`;
        if (quotaSub) quotaSub.innerHTML = `You have submitted the maximum allowed <strong>3 reports today</strong> across all departments (Food, Electricity, Sanitation). Quota resets automatically at <strong>12:00 AM Midnight</strong>.`;
      } else {
        banner.classList.remove('quota-exhausted');
        if (quotaTitle) quotaTitle.innerHTML = `<span>⚡</span> Daily Citizen Quota: <span id="modalQuotaText" style="color: #38bdf8; font-family: var(--font-mono); font-weight: 800;">${quota.remaining} / ${quota.limit} Remaining</span>`;
        if (quotaSub) quotaSub.innerHTML = `Max 3 reports allowed per day across all departments (Food, Electricity, Sanitation) to guarantee 48h SLA response.`;
      }
    }

    // Update 3 Slot Indicators
    for (let i = 1; i <= 3; i++) {
      const slot = document.getElementById(`quotaSlot${i}`);
      if (slot) {
        if (i <= quota.used) {
          slot.className = `quota-slot-pill ${quota.isLimitReached ? 'exhausted' : 'used'}`;
          slot.title = `Daily Slot ${i}: Used Today`;
        } else {
          slot.className = 'quota-slot-pill';
          slot.title = `Daily Slot ${i}: Available`;
        }
      }
    }

    // Update Submit Button State
    if (submitBtn) {
      if (quota.isLimitReached) {
        submitBtn.disabled = true;
        submitBtn.className = 'btn btn-primary btn-quota-disabled';
        submitBtn.innerHTML = `<span>⛔</span> Daily Limit Reached (3/3 Used)`;
      } else {
        submitBtn.disabled = false;
        submitBtn.className = 'btn btn-primary';
        submitBtn.innerHTML = `<span>🚀</span> Register Complaint (Start 48h SLA)`;
      }
    }
  }

  function renderCitizenDashboard() {
    const user = auth.getUser();
    if (!user) return;
    const issues = db.getAllIssues();

    // Synchronize Daily Quota UI
    updateCitizenDailyQuotaUI();

    const walletNav = document.getElementById('citizenNavWallet');
    if (walletNav) walletNav.textContent = `${user.civicCredits !== undefined ? user.civicCredits : 20} Civic Credits`;

    const ptsEl = document.getElementById('citizenWalletPoints');
    if (ptsEl) ptsEl.textContent = `${user.civicCredits !== undefined ? user.civicCredits : 20}`;

    const feedGrid = document.getElementById('citizenIssuesFeedGrid');
    if (feedGrid) {
      let filtered = issues;

      // 4-Tier Geospatial Filter
      if (selectedState !== 'all') {
        filtered = filtered.filter(i => (i.state || 'Andhra Pradesh') === selectedState);
      }
      if (selectedCity !== 'all') {
        filtered = filtered.filter(i => (i.city || 'Surampalem') === selectedCity);
      }
      if (selectedWard !== 'all') {
        filtered = filtered.filter(i => (i.ward || '') === selectedWard);
      }
      if (selectedStreet !== 'all') {
        filtered = filtered.filter(i => (i.street || '') === selectedStreet || i.location.includes(selectedStreet));
      }

      // Department / Category Filter
      if (citizenCategoryFilter === 'sanitation') filtered = filtered.filter(i => i.department === 'sanitation');
      else if (citizenCategoryFilter === 'food') filtered = filtered.filter(i => i.department === 'food_safety');
      else if (citizenCategoryFilter === 'electricity') filtered = filtered.filter(i => i.department === 'electricity');
      else if (citizenCategoryFilter === 'my_reports') filtered = filtered.filter(i => i.reportedBy === user.name || i.userId === user.id);
      else if (citizenCategoryFilter === 'resolved') filtered = filtered.filter(i => i.status === 'resolved');

      if (searchQuery) {
        const q = searchQuery.toLowerCase();
        filtered = filtered.filter(i => i.title.toLowerCase().includes(q) || i.location.toLowerCase().includes(q) || i.id.toLowerCase().includes(q));
      }

      feedGrid.innerHTML = filtered.length ? filtered.map(renderCardHTML).join('') : '<p style="grid-column: 1/-1; text-align: center; padding: 2.5rem; background: var(--bg-card); border-radius: var(--radius-lg); color: var(--text-muted); border: 1px dashed var(--border);">No complaints registered in this location division. You can be the first to report!</p>';
    }

    const ledgerList = document.getElementById('citizenWalletLedger');
    if (ledgerList) {
      const history = db.loadFromStorage('clean_safe_credits_history_v9', [
        { id: 'CRD-1', title: 'Weekly Reporting Streak Bonus', points: 50, date: '20 Aug 2026', status: 'Credited' },
        { id: 'CRD-2', title: 'Verified Resolution: Garbage at Lake Road', points: 50, date: '18 Aug 2026', status: 'Credited' },
        { id: 'CRD-3', title: 'Civic Guardian Onboarding Bonus', points: 50, date: '15 Aug 2026', status: 'Credited' }
      ]);
      ledgerList.innerHTML = history.map(tx => `
        <div style="display: flex; align-items: center; justify-content: space-between; padding: 0.85rem 0; border-bottom: 1px solid var(--border);">
          <div style="display: flex; align-items: center; gap: 0.75rem;">
            <div style="width: 36px; height: 36px; border-radius: 50%; background: rgba(16, 185, 129, 0.2); color: #34d399; display: flex; align-items: center; justify-content: center; font-size: 1.1rem;">🎖️</div>
            <div>
              <div style="font-weight: 700; font-size: 0.9rem; color: white;">${tx.title}</div>
              <div style="font-size: 0.78rem; color: var(--text-muted);">${tx.date} • ${tx.status}</div>
            </div>
          </div>
          <div style="font-size: 1.05rem; font-weight: 800; color: #34d399; font-family: var(--font-mono);">+${tx.points} Pts</div>
        </div>
      `).join('');
    }
  }

  function renderMunicipalDashboard() {
    let issues = db.getAllIssues();
    
    // 4-Tier Geospatial Jurisdiction Filter
    if (selectedState !== 'all') {
      issues = issues.filter(i => (i.state || 'Andhra Pradesh') === selectedState);
    }
    if (selectedCity !== 'all') {
      issues = issues.filter(i => (i.city || 'Surampalem') === selectedCity);
    }
    if (selectedWard !== 'all') {
      issues = issues.filter(i => (i.ward || 'Ward 12') === selectedWard || (i.location && i.location.includes(selectedWard.split(' ')[0])));
    }
    if (selectedStreet !== 'all') {
      issues = issues.filter(i => (i.street || '') === selectedStreet || (i.location && i.location.includes(selectedStreet)));
    }

    const totalReports = issues.length;
    const resolvedCount = issues.filter(i => i.status === 'resolved').length;
    const resolutionRate = totalReports > 0 ? Math.round((resolvedCount / totalReports) * 100) : 100;
    const rewardsPaid = resolvedCount * 50;
    const finesCollected = issues.reduce((sum, i) => sum + (i.fineLevied || 0), 0) + (db.finesCollected || 2500);

    const totalEl = document.getElementById('munTotalReports');
    const rateEl = document.getElementById('munResolutionRate');
    const rewardsEl = document.getElementById('munRewardsPaid');
    const finesEl = document.getElementById('munFinesCollected');

    if (totalEl) totalEl.textContent = totalReports;
    if (rateEl) rateEl.textContent = `${resolutionRate}%`;
    if (rewardsEl) rewardsEl.textContent = `${rewardsPaid} Pts`;
    if (finesEl) finesEl.textContent = `₹${finesCollected.toLocaleString('en-IN')}`;

    const tableBody = document.getElementById('munIncidentTableBody');
    if (tableBody) {
      if (issues.length === 0) {
        tableBody.innerHTML = `<tr><td colspan="7" style="text-align: center; padding: 2rem; color: #94a3b8; font-size: 0.85rem;">No civic incidents found in the selected jurisdiction (${selectedState} → ${selectedCity} → ${selectedWard}).</td></tr>`;
      } else {
        tableBody.innerHTML = issues.map(issue => {
          const isResolved = issue.status === 'resolved';
          const isEscalated = issue.status === 'escalated' || issue.isSlaBreached;
          const reportedTimeStr = formatReportDateTime(issue.timestamp);
          const deadlineTimeStr = formatReportDateTime(issue.slaDeadline || (issue.timestamp + 48 * 3600 * 1000));
          const resolvedTimeStr = isResolved ? formatReportDateTime(issue.resolvedTimestamp || (issue.timestamp + 3600000 * 28)) : null;
          const turnaroundStr = isResolved ? calculateSlaTurnaround(issue.timestamp, issue.resolvedTimestamp || (issue.timestamp + 3600000 * 28)) : null;

          return `
            <tr>
              <td>
                <div style="font-family: var(--font-mono); font-weight: 700; color: #38bdf8;">${issue.id}</div>
                <div style="font-size: 0.72rem; color: var(--command-text-muted);">📅 ${reportedTimeStr}</div>
              </td>
              <td>
                <div style="font-weight: 700; color: white;">${issue.title}</div>
                <div style="font-size: 0.75rem; color: var(--command-text-muted);">📍 ${issue.location}</div>
                <div style="font-size: 0.72rem; color: #94a3b8; margin-top: 2px;">👤 ${issue.reportedBy || 'Citizen'} • 👷 ${issue.assignedWorker || 'Squad'}</div>
              </td>
              <td>
                <div style="font-size: 0.78rem; color: #38bdf8; font-weight: 700;">${issue.state || 'Andhra Pradesh'}</div>
                <div style="font-size: 0.72rem; color: var(--command-text-muted);">${issue.city || 'Surampalem'} • ${issue.ward || 'Ward 12'}</div>
              </td>
              <td><span class="cat-badge">${issue.deptIcon} ${issue.deptName}</span></td>
              <td><span class="badge sev-${issue.severity}">${issue.severity.toUpperCase()}</span></td>
              <td>
                <div class="sla-progress-container">
                  <span class="sla-text ${isResolved ? 'text-success' : isEscalated ? 'text-danger' : 'text-warning'}" style="font-weight: 800; font-size: 0.75rem;">
                    ${isResolved ? `✅ Resolved (${turnaroundStr})` : isEscalated ? `🚨 SLA Breached (>48h) — Escalated to Commissioner` : `⏱️ ${issue.slaHoursLeft}h left (Due ${deadlineTimeStr})`}
                  </span>
                </div>
              </td>
              <td>
                <div style="display: flex; gap: 0.4rem;">
                  <button class="btn btn-sm btn-outline" style="color: white; border-color: var(--command-border);" onclick="window.viewIssueDetail('${issue.id}')">📦 Track</button>
                  ${!isResolved ? `<button class="btn btn-sm btn-primary" onclick="window.openResolveModal('${issue.id}')">Resolve</button>` : `<span style="font-size: 0.8rem; color: #10b981; font-weight: 700;">Done</span>`}
                </div>
              </td>
            </tr>
          `;
        }).join('');
      }
    }

    const outageGrid = document.getElementById('munPowerOutageGrid');
    if (outageGrid) {
      outageGrid.innerHTML = `
        <div class="outage-card active-outage">
          <div class="outage-header">
            <span class="power-status-pill power-status-outage">⚡ OUTAGE ACTIVE</span>
            <span class="outage-eta">ETA: 45 Mins</span>
          </div>
          <h3 style="font-size: 1.15rem; color: white; margin-bottom: 0.35rem;">Feeder #4 - Substation Transformer</h3>
          <p style="font-size: 0.85rem; color: var(--text-muted);"><strong>Area:</strong> ${selectedWard !== 'all' ? selectedWard : 'Ward 12 Gandhi Road'} • <strong>Affected:</strong> ~450 Homes</p>
          <div style="background: rgba(255, 255, 255, 0.04); padding: 0.75rem; border-radius: var(--radius-sm); font-size: 0.82rem; margin: 0.6rem 0; border: 1px dashed var(--border);">
            <div>⚠️ <strong>Cause:</strong> Sparking & Flashover</div>
            <div>👷 <strong>Status:</strong> Jumper replacement in progress</div>
          </div>
          <div style="font-size: 0.8rem; color: #38bdf8;">👮 Lineman: <strong>Suresh Kumar</strong></div>
        </div>
      `;
    }

    const workerGrid = document.getElementById('munWorkerTasksGrid');
    if (workerGrid) {
      const pending = issues.filter(i => i.status !== 'resolved');
      if (pending.length === 0) {
        workerGrid.innerHTML = `<p style="grid-column: 1/-1; text-align: center; padding: 2rem; color: #94a3b8; background: var(--bg-card); border-radius: var(--radius-lg); border: 1px dashed var(--border);">All field tasks completed for this jurisdiction!</p>`;
      } else {
        workerGrid.innerHTML = pending.map(task => `
          <div class="lineman-ticket-card">
            <div style="display: flex; justify-content: space-between;">
              <span class="badge badge-${task.status}">${task.status.toUpperCase()}</span>
              <span style="font-family: var(--font-mono); font-weight: 700; color: #38bdf8;">${task.id}</span>
            </div>
            <h3 style="font-size: 1.1rem; color: white; margin: 0.4rem 0;">${task.title}</h3>
            <p style="font-size: 0.82rem; color: var(--text-muted);">${task.description}</p>
            <div style="font-size: 0.75rem; color: #94a3b8; margin: 0.4rem 0;">📍 ${task.location}</div>
            <div style="display: flex; gap: 0.5rem; margin-top: 0.75rem;">
              <button class="btn btn-sm btn-outline" style="flex: 1;" onclick="window.viewIssueDetail('${task.id}')">Review</button>
              <button class="btn btn-sm btn-primary" style="flex: 1;" onclick="window.openResolveModal('${task.id}')">Resolve</button>
            </div>
          </div>
        `).join('');
      }
    }
  }

  function renderFoodSafetyDashboard() {
    const allIssues = db.getAllIssues();
    let foodIssues = allIssues.filter(i => i.department === 'food_safety');
    let vendors = db.getAllVendors();

    // 4-Tier Geospatial Jurisdiction Filter
    if (selectedState !== 'all') {
      foodIssues = foodIssues.filter(i => (i.state || 'Andhra Pradesh') === selectedState);
      vendors = vendors.filter(v => (v.state || 'Andhra Pradesh') === selectedState);
    }
    if (selectedCity !== 'all') {
      foodIssues = foodIssues.filter(i => (i.city || 'Surampalem') === selectedCity);
      vendors = vendors.filter(v => (v.city || 'Surampalem') === selectedCity);
    }
    if (selectedWard !== 'all') {
      foodIssues = foodIssues.filter(i => (i.ward || '') === selectedWard || (i.location && i.location.includes(selectedWard.split(' ')[0])));
      vendors = vendors.filter(v => (v.ward || '') === selectedWard || (v.location && v.location.includes(selectedWard.split(' ')[0])) || (v.address && v.address.includes(selectedWard.split(' ')[0])));
    }
    if (selectedStreet !== 'all') {
      foodIssues = foodIssues.filter(i => (i.street || '') === selectedStreet || (i.location && i.location.includes(selectedStreet)));
      vendors = vendors.filter(v => (v.street || '') === selectedStreet || (v.location && v.location.includes(selectedStreet)) || (v.address && v.address.includes(selectedStreet)));
    }

    // Metric Summary Counters
    const activeAudits = foodIssues.filter(i => i.status !== 'resolved').length;
    const rectifiedOutlets = foodIssues.filter(i => i.status === 'resolved').length;
    const certifiedVendors = vendors.filter(v => !v.isViolated).length;
    const finesLevied = db.finesCollected || 2500;

    const totalAuditsEl = document.getElementById('foodTotalAudits');
    const rectifiedEl = document.getElementById('foodRectifiedOutlets');
    const certifiedEl = document.getElementById('foodCertifiedCount');
    const finesEl = document.getElementById('foodFinesCollected');

    if (totalAuditsEl) totalAuditsEl.textContent = activeAudits;
    if (rectifiedEl) rectifiedEl.textContent = rectifiedOutlets;
    if (certifiedEl) certifiedEl.textContent = certifiedVendors;
    if (finesEl) finesEl.textContent = `₹${finesLevied.toLocaleString('en-IN')}`;

    // 1. Food Complaints & Violations Grid
    const foodGrid = document.getElementById('foodDeptIssuesGrid');
    if (foodGrid) {
      let filteredIssues = foodIssues;
      if (foodFilter === 'pending') filteredIssues = filteredIssues.filter(i => i.status !== 'resolved');
      else if (foodFilter === 'resolved') filteredIssues = filteredIssues.filter(i => i.status === 'resolved');

      if (filteredIssues.length === 0) {
        foodGrid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; padding: 2rem; background: var(--bg-card); border-radius: var(--radius-lg); color: var(--text-muted); border: 1px dashed var(--border);">No food safety violations found in this category.</p>';
      } else {
        foodGrid.innerHTML = filteredIssues.map(issue => {
          const isResolved = issue.status === 'resolved';
          return `
            <div class="card" style="border-top: 3px solid ${isResolved ? '#10b981' : '#f59e0b'};">
              <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
                <span class="badge ${isResolved ? 'badge-resolved' : 'badge-pending'}">${isResolved ? '✅ RECTIFIED & CLEARED' : '⚠️ ACTIVE NOTICE'}</span>
                <span style="font-family: var(--font-mono); font-size: 0.8rem; color: #f59e0b; font-weight: 700;">${issue.id}</span>
              </div>
              <div style="height: 140px; border-radius: 6px; overflow: hidden; margin-bottom: 0.75rem; border: 1px solid var(--border);">
                <img src="${issue.imageBefore}" style="width: 100%; height: 100%; object-fit: cover;" alt="${issue.title}">
              </div>
              <h3 style="color: white; font-size: 1.05rem; margin-bottom: 0.4rem;">${issue.title}</h3>
              <p style="font-size: 0.82rem; color: var(--text-muted); margin-bottom: 0.75rem;">${issue.description}</p>
              
              <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid var(--border); padding: 0.6rem; border-radius: 6px; font-size: 0.78rem; margin-bottom: 0.85rem; color: #cbd5e1;">
                <div>📍 <strong>Location:</strong> ${issue.location}</div>
                <div>🥩 <strong>MQ-135 Gas:</strong> ${issue.mq135GasPpm ? issue.mq135GasPpm + ' PPM' : '340 PPM (Elevated)'}</div>
                ${issue.fineLevied ? `<div style="color:#f87171;">⚖️ <strong>Fine Imposed:</strong> ₹${issue.fineLevied}</div>` : ''}
              </div>

              <div class="food-action-row">
                <button class="btn btn-sm btn-outline" style="flex: 1;" onclick="window.viewIssueDetail('${issue.id}')">
                  🔍 Review Details
                </button>
                ${!isResolved ? `
                  <button class="btn btn-sm btn-rectify" style="flex: 1;" onclick="window.openFoodRectifyModal('${issue.id}')">
                    🛠️ Rectify Problem
                  </button>
                ` : `
                  <span style="font-size: 0.8rem; color: #34d399; font-weight: 800; display: flex; align-items: center; justify-content: center; flex: 1;">
                    ✓ Grade A+ Cleared
                  </span>
                `}
              </div>
            </div>
          `;
        }).join('');
      }
    }

    // 2. Certified & Violated Establishments Grid
    const vendorGrid = document.getElementById('foodDeptVendorsGrid');
    if (vendorGrid) {
      let filteredVendors = vendors;
      if (vendorFilter === 'certified') filteredVendors = filteredVendors.filter(v => !v.isViolated);
      else if (vendorFilter === 'violation') filteredVendors = filteredVendors.filter(v => v.isViolated);

      if (filteredVendors.length === 0) {
        vendorGrid.innerHTML = `
          <div class="card" style="grid-column: 1/-1; text-align: center; padding: 2.5rem; color: #94a3b8; border: 1px dashed var(--border);">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📜</div>
            <h4 style="color: white; margin-bottom: 0.35rem; font-size: 1.1rem;">No Food Establishments Found</h4>
            <p style="font-size: 0.85rem; margin-bottom: 1.25rem;">No vendors currently match the selected ward or category filter.</p>
            <button class="btn btn-sm btn-outline" onclick="window.handleVendorFilter('all', document.querySelector('.vendor-filter-chip[data-filter=all]'))">
              Show All Establishments
            </button>
          </div>
        `;
      } else {
        vendorGrid.innerHTML = filteredVendors.map(vendor => {
          const isViolated = vendor.isViolated;
          return `
            <div class="card" style="border: 1px solid ${isViolated ? '#ef4444' : '#10b981'}; background: ${isViolated ? 'rgba(239, 68, 68, 0.05)' : 'var(--bg-card)'};">
              <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem; gap: 0.5rem;">
                <div>
                  <span class="badge ${isViolated ? 'badge-escalated' : 'badge-resolved'}">
                    ${isViolated ? '🔴 STATUTORY VIOLATION NOTICE' : '🟢 VERIFIED & CERTIFIED'}
                  </span>
                  <h3 style="margin-top: 0.5rem; font-size: 1.15rem; color: white;">${vendor.name}</h3>
                  <p style="font-size: 0.85rem; color: var(--text-muted);">Proprietor: ${vendor.owner} • 📍 ${vendor.location}</p>
                </div>
                <div style="text-align: center; background: ${isViolated ? 'rgba(239, 68, 68, 0.2)' : 'rgba(16, 185, 129, 0.15)'}; border: 2px solid ${isViolated ? '#ef4444' : '#10b981'}; border-radius: var(--radius-md); padding: 4px 10px; min-width: 60px;">
                  <div style="font-size: 1.25rem; font-weight: 900; color: ${isViolated ? '#f87171' : '#34d399'};">${vendor.hygieneGrade || 'A+'}</div>
                  <div style="font-size: 0.65rem; font-weight: 700; color: ${isViolated ? '#ef4444' : '#10b981'};">${isViolated ? 'VIOLATION' : 'HYGIENE'}</div>
                </div>
              </div>

              ${isViolated ? `
                <div style="background: rgba(239, 68, 68, 0.1); border: 1px dashed rgba(239, 68, 68, 0.4); padding: 0.65rem 0.85rem; border-radius: 6px; font-size: 0.82rem; color: #fecdd3; margin-bottom: 0.85rem; line-height: 1.5;">
                  <div>⚖️ <strong>Clause:</strong> ${vendor.violationClause || 'Section 56: Stale Oil Violation'}</div>
                  <div>💳 <strong>Penalty Imposed:</strong> <span style="font-family: var(--font-mono); font-weight: 800; color: #facc15;">${vendor.penaltyImposed || '₹2,000.00'}</span></div>
                  <div>⏳ <strong>Rectification Deadline:</strong> <span style="font-weight: 700; color: white;">${vendor.rectificationDeadline || '48 Hours'}</span></div>
                  <div>🥩 <strong>MQ-135 Gas Risk:</strong> ${vendor.mq135GasPpm || '370 PPM'}</div>
                </div>
              ` : `
                <div style="background: rgba(16, 185, 129, 0.08); border: 1px dashed rgba(16, 185, 129, 0.3); padding: 0.65rem 0.85rem; border-radius: 6px; font-size: 0.82rem; color: #a7f3d0; margin-bottom: 0.85rem; line-height: 1.5;">
                  <div>🏆 <strong>Hygiene Audit Score:</strong> <strong style="color: #34d399;">${vendor.score || '94/100'}</strong></div>
                  <div>📅 <strong>Certificate Validity:</strong> ${vendor.validTill || '31 Dec 2026'}</div>
                  <div>🛡️ <strong>Inspected By:</strong> ${vendor.inspectedBy || 'Dr. Lakshmi Prasad (FSO)'}</div>
                </div>
              `}

              <button class="btn btn-sm ${isViolated ? 'btn-outline' : 'btn-saffron'}" style="width: 100%; border-color: ${isViolated ? '#ef4444' : 'transparent'}; color: ${isViolated ? '#fca5a5' : 'white'};" onclick="window.viewDigitalCertificate('${vendor.id}')">
                ${isViolated ? '⚠️ View Official Statutory Violation Notice' : '📜 View National Hygiene Certificate'}
              </button>
            </div>
          `;
        }).join('');
      }
    }
  }

  // Master Route & Auth Switcher
  function checkAuthAndRoute() {
    const isAuth = auth.isAuthenticated();
    const sessionDept = auth.getDepartment();

    const views = ['authGatewayView', 'citizenMasterView', 'municipalMasterView', 'foodSafetyMasterView'];
    views.forEach(id => {
      const el = document.getElementById(id);
      if (el) el.classList.remove('active');
    });

    const chatbotBtn = document.getElementById('chatbotTrigger');

    if (!isAuth) {
      const authView = document.getElementById('authGatewayView');
      if (authView) authView.classList.add('active');
      if (chatbotBtn) chatbotBtn.style.display = 'none';

      // Prefill last remembered email for user convenience
      const lastEmail = localStorage.getItem('CIVIC_LAST_EMAIL');
      const emailInput = document.getElementById('authEmailInput');
      if (lastEmail && emailInput && !emailInput.value) {
        emailInput.value = lastEmail;
      }

      window.scrollTo(0, 0);
      return;
    }

    if (chatbotBtn) chatbotBtn.style.display = 'flex';

    // Synchronize Dynamic User Avatar, Badge & Profile Elements
    const currentUser = auth.getUser();
    if (currentUser) {
      // 1. Citizen Avatar & Name
      const cAvatar = document.getElementById('citizenTopAvatar');
      if (cAvatar) {
        cAvatar.textContent = currentUser.avatar || 'KR';
        cAvatar.title = `Citizen Profile: ${currentUser.name} (${currentUser.officialId || ''})`;
      }

      // 2. Municipal Admin Badge
      const mBadge = document.getElementById('munTopAdminBadge');
      if (mBadge) {
        mBadge.textContent = currentUser.officialId || 'GOV-MUNC-SEC-012';
        mBadge.parentElement.title = `Officer: ${currentUser.name}`;
      }

      // 3. Food Safety Badge
      const fBadge = document.getElementById('foodTopBadge');
      if (fBadge) {
        fBadge.textContent = currentUser.officialId || 'FSSAI-INSP-2026-44';
        fBadge.parentElement.title = `Inspector: ${currentUser.name}`;
      }
    }

    // Synchronize Department-Specific AI Persona, Header, Greeting & Quick Action Chips
    syncChatbotDepartmentTheme();

    if (sessionDept === 'citizen') {
      const cView = document.getElementById('citizenMasterView');
      if (cView) cView.classList.add('active');
      renderCitizenDashboard();
    } else if (sessionDept === 'municipal') {
      const mView = document.getElementById('municipalMasterView');
      if (mView) mView.classList.add('active');
      renderMunicipalDashboard();
      setTimeout(() => initGISMap([17.0010, 81.8045], 14), 100);
    } else if (sessionDept === 'food') {
      const fView = document.getElementById('foodSafetyMasterView');
      if (fView) fView.classList.add('active');
      renderFoodSafetyDashboard();
    } else {
      const authView = document.getElementById('authGatewayView');
      if (authView) authView.classList.add('active');
    }

    window.scrollTo(0, 0);
  }

  // =========================================================================
  // 7. DEPARTMENT-SPECIFIC AI CHATBOT COPILOT ENGINE
  // =========================================================================
  const DEPARTMENT_CHATBOT_CONFIG = {
    citizen: {
      deptClass: 'dept-citizen',
      icon: '🧑‍💼',
      title: 'Citizen AI Helpdesk',
      subtitle: '24/7 Citizen Support • KRISH',
      placeholder: 'Ask about reporting, 20 Civic Credits, 48h SLA, or Ticket ID...',
      chips: [
        { label: '⚡ Daily Quota (3/day)', prompt: 'What is my daily reporting limit and remaining quota?' },
        { label: '📢 How to Report', prompt: 'How do I report an issue with photo & GPS?' },
        { label: '🪙 My Civic Credits (20 Pts)', prompt: 'Check my civic credits, weekly streak and rewards' },
        { label: '⏱️ Track 48h SLA', prompt: 'What is the 48 hour resolution SLA guarantee?' },
        { label: '📜 View My Certificate', prompt: 'How can I view and download my official participation certificate?' },
        { label: '📱 WhatsApp Bot', prompt: 'How do I use the in-app WhatsApp Grievance Bot?' },
        { label: '🚨 Emergency Helplines', prompt: 'Show 24/7 emergency municipal helplines' }
      ],
      greeting: `👋 Hello <strong>KRISH</strong>! I am your <strong>Citizen AI Helpdesk</strong>.<br>How can I assist you with filing geo-tagged reports (Max 3/day), checking your <strong>20 Welcome Civic Credits</strong>, viewing your <strong>Official Government Certificate</strong>, or tracking our <strong>48h SLA guarantee</strong>?`
    },
    municipal: {
      deptClass: 'dept-municipal',
      icon: '🛡️',
      title: 'Municipal & SCADA Command Copilot',
      subtitle: 'Tactical Ops Assistant • K. Mukundha',
      placeholder: 'Ask about fleet dispatch, 48h SLA risks, SCADA Feeder 4, or e-Challans...',
      chips: [
        { label: '🚨 48h Escalation Watch', prompt: 'Which civic tickets are at risk of 48h SLA breach?' },
        { label: '🚛 Fleet Dispatch Status', prompt: 'Explain the auto-resource allocation rules for collection vehicles' },
        { label: '⚡ SCADA Feeder #4 Outage', prompt: 'Show SCADA electrical grid telemetry and Feeder 4 outage status' },
        { label: '🗺️ GIS Red-Zone Analysis', prompt: 'Give me the GIS Red-Zone hotspot density breakdown for Ward 12' },
        { label: '💳 e-Challan Fund (₹2,500)', prompt: 'Show e-Challan penalty revenue and citizen reward distribution ledger' },
        { label: '👷 Lineman Workload', prompt: 'List active electrical lineman work-orders and substation teams' }
      ],
      greeting: `🛡️ Welcome, <strong>Administrator K. Mukundha</strong>. I am your <strong>Municipal & SCADA Command AI Copilot</strong>.<br>I provide live operational intelligence on 48h SLA escalation countdowns, automated fleet dispatch, GIS Red-Zone hotspot density, and SCADA 33/11KV electrical feeder telemetry.`
    },
    food: {
      deptClass: 'dept-food',
      icon: '🍲',
      title: 'FSSAI Regulatory & Inspection AI Copilot',
      subtitle: 'Enforcement Assistant • Dr. Lakshmi Prasad',
      placeholder: 'Ask about Section 56 stale oil, MQ-135 gas PPM, penalties, or Grade A+ certificates...',
      chips: [
        { label: '⚖️ FSSAI Penalties & Acts', prompt: 'Explain the FSSAI progressive penalty framework and fine tiers' },
        { label: '🥩 MQ-135 Gas Spoilage (>350 PPM)', prompt: 'What are the MQ-135 IoT food spoilage gas thresholds in PPM?' },
        { label: '📜 Issue Grade A+ Certificate', prompt: 'How do I certify a street vendor with a Grade A+ digital QR certificate?' },
        { label: '🍳 Section 56 Stale Oil Notice', prompt: 'What are the legal inspection criteria under Section 56 for rancid cooking oil?' },
        { label: '🛠️ Re-Inspection Protocol', prompt: 'How do I rectify and clear a food stall violation notice?' },
        { label: '🛑 License Seizure Rules', prompt: 'When does a repeated food violation lead to commercial license seizure?' }
      ],
      greeting: `🍲 Greetings, <strong>Food Safety Officer Dr. Lakshmi Prasad</strong>. I am your <strong>FSSAI Regulatory & Inspection AI Copilot</strong>.<br>Ready to assist with logging statutory violation notices under Sections 56, 58 & 59, monitoring MQ-135 volatile gas telemetry, scoring hygiene audits, and verifying establishment rectifications.`
    }
  };

  function syncChatbotDepartmentTheme() {
    const dept = auth.getDepartment() || 'citizen';
    const cfg = DEPARTMENT_CHATBOT_CONFIG[dept] || DEPARTMENT_CHATBOT_CONFIG.citizen;

    const trigIcon = document.getElementById('chatbotTriggerIcon');
    const headerBar = document.getElementById('chatbotHeaderBar');
    const headerIcon = document.getElementById('chatbotHeaderIcon');
    const headerTitle = document.getElementById('chatbotHeaderTitle');
    const headerSubtitle = document.getElementById('chatbotHeaderSubtitle');
    const chipsBar = document.getElementById('chatbotQuickChipsBar');
    const input = document.getElementById('chatbotInput');
    const msgContainer = document.getElementById('chatbotMessages');

    if (trigIcon) trigIcon.textContent = cfg.icon;
    if (headerIcon) headerIcon.textContent = cfg.icon;
    if (headerTitle) headerTitle.textContent = cfg.title;
    if (headerSubtitle) headerSubtitle.textContent = cfg.subtitle;
    if (input) input.placeholder = cfg.placeholder;

    if (headerBar) {
      headerBar.className = `chatbot-header ${cfg.deptClass}`;
    }

    if (chipsBar) {
      chipsBar.innerHTML = cfg.chips.map(chip => `
        <button type="button" class="chat-quick-btn ${dept === 'food' ? 'chip-food' : dept === 'municipal' ? 'chip-mun' : ''}" onclick="window.askChatbot('${chip.prompt.replace(/'/g, "\\'")}')">
          ${chip.label}
        </button>
      `).join('');
    }

    if (msgContainer) {
      msgContainer.innerHTML = `
        <div class="chat-bubble bot">
          ${cfg.greeting}
        </div>
      `;
    }
  }

  async function handleChatbotMessage(forcedText) {
    const input = document.getElementById('chatbotInput');
    const msgContainer = document.getElementById('chatbotMessages');
    if (!msgContainer) return;

    const userText = (typeof forcedText === 'string' ? forcedText : (input ? input.value : '')).trim();
    if (!userText) return;

    // Add User Message Bubble
    const userBubble = document.createElement('div');
    userBubble.className = 'chat-bubble user';
    userBubble.textContent = userText;
    msgContainer.appendChild(userBubble);
    if (input) input.value = '';
    msgContainer.scrollTop = msgContainer.scrollHeight;

    // Show Typing Indicator
    const typingBubble = document.createElement('div');
    typingBubble.className = 'chat-bubble bot';
    typingBubble.innerHTML = '<span style="font-size: 0.8rem; color: #a855f7;">✨ Gemini AI is thinking...</span>';
    msgContainer.appendChild(typingBubble);
    msgContainer.scrollTop = msgContainer.scrollHeight;

    const dept = auth.getDepartment() || 'citizen';
    
    // Check local ticket match first for instant live tracking
    const issues = db.getAllIssues();
    const q = userText.toLowerCase();
    const ticketMatch = issues.find(i => {
      const cleanId = i.id.toLowerCase();
      const numPart = cleanId.split('-').pop();
      return q.includes(cleanId) || (numPart.length >= 3 && q.includes(numPart));
    });

    if (ticketMatch || q.includes('team') || q.includes('who created') || q.includes('developer')) {
      typingBubble.innerHTML = generateDynamicBotReply(userText);
      msgContainer.scrollTop = msgContainer.scrollHeight;
      return;
    }

    try {
      const aiReply = await AiEngine.chat(userText, dept);
      if (aiReply) {
        typingBubble.innerHTML = aiReply.replace(/\n/g, '<br>');
      } else {
        typingBubble.innerHTML = generateDynamicBotReply(userText);
      }
    } catch (e) {
      typingBubble.innerHTML = generateDynamicBotReply(userText);
    }
    msgContainer.scrollTop = msgContainer.scrollHeight;
  }

  function generateDynamicBotReply(rawQuery) {
    const q = rawQuery.toLowerCase();
    const dept = auth.getDepartment() || 'citizen';
    const user = auth.getUser();
    const issues = db.getAllIssues();
    const vendors = db.getAllVendors();
    const userName = user ? user.name : 'User';

    // 1. TICKET LOOKUP BY EXACT OR PARTIAL ID (UNIVERSAL)
    const ticketMatch = issues.find(i => {
      const cleanId = i.id.toLowerCase();
      const numPart = cleanId.split('-').pop();
      return q.includes(cleanId) || (numPart.length >= 3 && q.includes(numPart));
    });

    if (ticketMatch) {
      const isResolved = ticketMatch.status === 'resolved';
      const isEscalated = ticketMatch.status === 'escalated' || ticketMatch.isSlaBreached;
      const reportedTimeStr = formatReportDateTime(ticketMatch.timestamp);
      const deadlineTimeStr = formatReportDateTime(ticketMatch.slaDeadline || (ticketMatch.timestamp + 48 * 3600 * 1000));
      const resolvedTimeStr = isResolved ? formatReportDateTime(ticketMatch.resolvedTimestamp || (ticketMatch.timestamp + 3600000 * 28)) : null;
      const turnaroundStr = isResolved ? calculateSlaTurnaround(ticketMatch.timestamp, ticketMatch.resolvedTimestamp || (ticketMatch.timestamp + 3600000 * 28)) : null;

      return `
        <div style="border-left: 3px solid ${isResolved ? '#10b981' : isEscalated ? '#ef4444' : '#38bdf8'}; padding-left: 10px; line-height: 1.5;">
          <div style="font-size: 0.8rem; color: #38bdf8; font-weight: 800;">📦 ORDER-STYLE LIVE TRACKING: ${ticketMatch.id}</div>
          <div style="font-weight: 800; color: white; margin: 2px 0;">${ticketMatch.title}</div>
          <div style="font-size: 0.8rem; color: #94a3b8;">📍 ${ticketMatch.location}</div>
          
          <div style="background: rgba(255,255,255,0.04); padding: 8px; border-radius: 6px; margin: 6px 0; font-size: 0.8rem;">
            <div>📅 <strong>Reported On:</strong> ${reportedTimeStr} by ${ticketMatch.reportedBy || 'Citizen'}</div>
            <div>🔍 <strong>Verified By:</strong> ${ticketMatch.verifiedByOfficer || 'Consultant Officer K. Mukundha'}</div>
            <div>🚛 <strong>Allocated Squad:</strong> ${ticketMatch.assignedWorker || 'Municipal Squad'} (${ticketMatch.recommendedResource || 'Collection Unit'})</div>
            <div>👷 <strong>Worker Status:</strong> ${ticketMatch.workerStatus || 'In Progress'}</div>
            <div>⏱️ <strong>48h SLA Deadline:</strong> ${deadlineTimeStr}</div>
            ${isResolved ? `
              <div style="color: #34d399; font-weight: 800; margin-top: 4px;">✅ <strong>Resolved On:</strong> ${resolvedTimeStr} (Turnaround: ${turnaroundStr})</div>
            ` : isEscalated ? `
              <div style="color: #f87171; font-weight: 800; margin-top: 4px;">🚨 <strong>SLA Breached (>48h):</strong> Forwarded to Zonal Commissioner</div>
            ` : `
              <div style="color: #38bdf8; font-weight: 800; margin-top: 4px;">⏳ <strong>SLA Remaining:</strong> ${ticketMatch.slaHoursLeft} Hours</div>
            `}
          </div>

          <button class="btn btn-sm btn-outline" style="width: 100%; border-color: #38bdf8; color: #38bdf8; margin-top: 4px;" onclick="window.viewIssueDetail('${ticketMatch.id}')">
            📦 Open Full 5-Stage Live Timeline Stepper
          </button>
        </div>
      `;
    }

    // 2. PROJECT TEAM CREDITS (UNIVERSAL)
    if (q.includes('who created') || q.includes('team') || q.includes('author') || q.includes('developer') || q.includes('college') || q.includes('aditya') || q.includes('mentor')) {
      return `
        🎓 <strong>Smart Civic Connect — Project Credits:</strong><br>
        Innovated by <strong>Team Civic Tech Innovators</strong> (Aditya University, Surampalem):<br>
        • 👨‍💻 <strong>K.H. Sameer Reddy</strong> (Research & Operations Lead)<br>
        • 🛠️ <strong>K. Mukundha</strong> (Lead Developer & System Architect)<br>
        • 📢 <strong>N. Ramya Spoorthi</strong> (Communications & Public Safety)<br>
        • 🎖️ <strong>Mentors:</strong> Dr. Mahesh Babu Kota & Mr. Charan Sanjeev Tadimalla.
      `;
    }

    // =========================================================================
    // A. CITIZEN PORTAL CHATBOT REPLIES (PERSONA: CITIZEN HELPDESK)
    // =========================================================================
    if (dept === 'citizen') {
      const userCredits = user && user.civicCredits !== undefined ? user.civicCredits : 20;
      if (q.match(/\b(hi|hello|hey|greetings|good morning|good afternoon|namaste)\b/)) {
        return `
          👋 Hello <strong>${userName}</strong>! I am your <strong>Citizen AI Helpdesk</strong>.<br><br>
          You currently have <strong>${userCredits} Civic Credits</strong> and an active participation streak.<br>
          How can I help you today?
        `;
      }

      if (q.includes('quota') || q.includes('daily limit') || q.includes('limit') || q.includes('how many report') || q.includes('3 issues') || q.includes('per day')) {
        const quota = db.getCitizenDailyReportsUsage();
        return `
          ⚡ <strong>Daily Citizen Reporting Quota (3 Reports / Day Rule):</strong><br><br>
          • <strong>Rule:</strong> Every verified citizen can report a maximum of <strong>3 issues per day</strong> across all departments (Food Safety, Smart Electricity, Sanitation & Waste).<br>
          • <strong>Your Status Today (${userName}):</strong><br>
            - 📊 <strong>Submitted Today:</strong> <strong>${quota.used} of ${quota.limit} reports used</strong><br>
            - 🟢 <strong>Remaining Quota:</strong> <strong style="color: ${quota.isLimitReached ? '#f87171' : '#34d399'};">${quota.remaining} reports remaining</strong><br>
          • <strong>Why is there a daily limit?</strong> It ensures rapid triage and maintains our guaranteed <strong>48-Hour SLA resolution standard</strong> without overloading rapid response squads.<br>
          • <strong>Reset:</strong> Your quota resets automatically every night at <strong>12:00 AM Midnight</strong>.
        `;
      }

      if (q.includes('how to report') || q.includes('file complaint') || q.includes('submit') || q.includes('photo') || q.includes('gps')) {
        const quota = db.getCitizenDailyReportsUsage();
        return `
          📢 <strong>How to Report an Issue in 3 Simple Steps:</strong><br><br>
          • <em>Daily Quota:</em> You have <strong>${quota.remaining} of 3 reports left today</strong>.<br>
          1. 📍 <strong>Detect GPS / Jurisdiction:</strong> Click <strong>[ + Report Issue ]</strong> and hit <strong>[ 📡 Auto-Detect Live GPS ]</strong> to lock your coordinates.<br>
          2. 📸 <strong>Attach Evidence:</strong> Capture a live camera photo or pick a sample photo with automatic timestamp watermarks.<br>
          3. 🎙️ <strong>Voice Input:</strong> Click the <strong>🎙️ Voice AI Mic</strong> to speak naturally in Telugu/Hindi/English (e.g. <em>"Main road lo chettha ekkuva undi"</em>).<br>
          4. 🚀 <strong>Submit:</strong> Initiates the official <strong>48-Hour SLA Countdown</strong> and awards you <strong>+50 Civic Credits</strong> upon resolution!
        `;
      }

      if (q.includes('credit') || q.includes('point') || q.includes('reward') || q.includes('wallet') || q.includes('streak') || q.includes('standing')) {
        return `
          🪙 <strong>Your Civic Standing & Rewards:</strong><br><br>
          • <strong>Balance:</strong> <strong>${userCredits} Civic Credits</strong><br>
          • <strong>Standing Tier:</strong> 🎖️ <em>Level 1 Bronze Civic Guardian</em> (Initial Welcome Bonus)<br>
          • <strong>Active Streak:</strong> 🔥 <strong>1-Week Streak</strong> (Eligible for Mayor's Green Badge)<br>
          • <strong>Earning Rule:</strong> Receive <strong>+50 Points</strong> for every verified hazard resolved within 48h.<br>
          • <strong>Rebates:</strong> Redeem credits for a <strong>5% Electricity Bill Rebate</strong> or free Metro Smartcard passes!
        `;
      }

      if (q.includes('certificate') || q.includes('award') || q.includes('print') || q.includes('download')) {
        return `
          📜 <strong>Your Official Participation Certificate:</strong><br><br>
          • <strong>Status:</strong> Officially Awarded to <strong>${userName}</strong> by Ministry of Housing & Urban Affairs & Municipal Commissioner Dr. Mahesh Babu.<br>
          • <strong>Certificate ID:</strong> <code>CIT-IND-2026-8941</code> (Verified by National QR Seal)<br>
          • <strong>How to View:</strong> Go to the <strong>🪙 Civic Credits & Streak</strong> sub-tab and click <strong>[ 📜 View Official Certificate ]</strong> to view or print!
        `;
      }

      if (q.includes('sla') || q.includes('48') || q.includes('time limit') || q.includes('deadline') || q.includes('escalat')) {
        return `
          ⏱️ <strong>Guaranteed 48-Hour SLA Framework:</strong><br><br>
          • Every civic complaint receives a strict <strong>48-Hour resolution clock</strong> visible publicly.<br>
          • <strong>Auto-Escalation:</strong> If field teams do not resolve within 48 hours, the ticket turns red and escalates automatically to the Zonal Municipal Director.<br>
          • <strong>Resource Dispatch:</strong> Minor issues receive pushcarts; heavy waste receives compactor tractors automatically.
        `;
      }

      if (q.includes('whatsapp') || q.includes('bot') || q.includes('chat')) {
        return `
          💬 <strong>In-App WhatsApp Grievance Bot:</strong><br><br>
          • Open the <strong>💬 WhatsApp & Support</strong> tab in your dashboard.<br>
          • You can chat directly with our official bot (+91 90000 00000), send camera photos, drop live GPS pins, or record 3-second voice notes.<br>
          • Every WhatsApp grievance creates an official ticket in the municipal database!
        `;
      }

      if (q.includes('emergency') || q.includes('helpline') || q.includes('number') || q.includes('contact')) {
        return `
          🚨 <strong>24/7 Citizen Emergency Helplines:</strong><br><br>
          • 🏢 Sanitation & Open Garbage Dumps: <strong>1800-425-0012</strong><br>
          • ⚡ Electrical Sparking & Outages (SCADA): <strong>1912 / 112</strong><br>
          • 🍲 Food Safety / Adulteration Toll-Free: <strong>1800-112-100</strong>
        `;
      }

      return `
        🧑‍💼 <strong>Citizen AI Helpdesk:</strong> I can help you with:
        <ul style="margin: 6px 0 0 16px; font-size: 0.82rem; color: #cbd5e1;">
          <li>"How to report an issue with camera photo & GPS"</li>
          <li>"Check my <strong>Civic Credits</strong> & weekly streak"</li>
          <li>"View my <strong>National Participation Certificate</strong>"</li>
          <li>"Track ticket <strong>ISS-2026-00123</strong>"</li>
          <li>"Show <strong>emergency helplines</strong>"</li>
        </ul>
      `;
    }

    // =========================================================================
    // B. MUNICIPAL & SCADA COMMAND PORTAL (PERSONA: COMMAND COPILOT)
    // =========================================================================
    if (dept === 'municipal') {
      if (q.match(/\b(hi|hello|hey|greetings|welcome)\b/)) {
        return `
          🛡️ <strong>Municipal Command Copilot:</strong> Online and operational, Administrator <strong>K. Mukundha</strong>.<br><br>
          Current Command Status: <strong>14/16 SCADA Feeders Online</strong> • <strong>3 Pending Grievances</strong> • <strong>₹2,500 Fine Fund</strong>.<br>
          How can I assist tactical triage?
        `;
      }

      if (q.includes('escalat') || q.includes('sla') || q.includes('risk') || q.includes('breach') || q.includes('pending')) {
        const pending = issues.filter(i => i.status !== 'resolved');
        return `
          🚨 <strong>48h SLA Escalation Intelligence:</strong><br><br>
          • <strong>Active Unresolved Queue:</strong> ${pending.length} tickets across Surampalem & regional zones.<br>
          • <strong>Highest Priority:</strong> <code>ISS-2026-00124</code> (11KV Transformer Sparking - 30h SLA left).<br>
          • <strong>Auto-Escalation Rule:</strong> Any ticket reaching &lt;6h triggers automated SMS dispatch to Zonal Field Inspector; tickets exceeding 48h are routed to the Municipal Commissioner's red queue.
        `;
      }

      if (q.includes('fleet') || q.includes('truck') || q.includes('dispatch') || q.includes('resource') || q.includes('allocat')) {
        return `
          🚛 <strong>Automated Resource Allocation Algorithms:</strong><br><br>
          • 🛒 <strong>Low Severity:</strong> Auto-dispatches <em>Sanitation Pushcart & Sanitation Worker</em>.<br>
          • 🚛 <strong>Medium Severity:</strong> Auto-dispatches <em>Standard Collection Truck (AP-05-TX)</em> with GPS tracking.<br>
          • 🚜 <strong>Bulk Hazard:</strong> Auto-dispatches <em>Hydraulic Compactor Tractor (AP-05-CT)</em>.<br>
          • ⚡ <strong>Electrical Hazards:</strong> Auto-dispatches <em>Lineman Bucket Van (AP-05-EB)</em>.
        `;
      }

      if (q.includes('feeder') || q.includes('scada') || q.includes('power') || q.includes('outage') || q.includes('electric') || q.includes('transformer')) {
        return `
          ⚡ <strong>SCADA Substation 33/11KV Telemetry:</strong><br><br>
          • <strong>Surampalem Central Substation:</strong> 14/16 Feeders Operational (87.5% Grid Load).<br>
          • <strong>Active Outage:</strong> <em>Feeder #4 (Ward 12 Gandhi Road)</em> — Tripped due to jumper flashover.<br>
          • <strong>Affected Load:</strong> ~450 Commercial & Residential meters.<br>
          • <strong>Deployment:</strong> Lineman Suresh Kumar & Squad B deployed with replacement bushing. ETA: <strong>35 Minutes</strong>.
        `;
      }

      if (q.includes('red zone') || q.includes('gis') || q.includes('map') || q.includes('hotspot') || q.includes('density')) {
        return `
          🗺️ <strong>GIS Red-Zone Spatial Cluster Analysis:</strong><br><br>
          • <strong>Active Hotspot #12:</strong> <em>Ward 12 Market Junction, Surampalem</em> (Pulsing Red Perimeter on GIS Map).<br>
          • <strong>Incident Density:</strong> 3 overlapping complaints (Commercial dumping + Transformer sparking + Street market waste).<br>
          • <strong>Recommendation:</strong> Station a permanent 3-in-1 CCTV pole with ANPR and deploy a dedicated night tipper squad.
        `;
      }

      if (q.includes('challan') || q.includes('fund') || q.includes('revenue') || q.includes('fine') || q.includes('reward paid')) {
        return `
          💳 <strong>e-Challan Revenue & Self-Sustaining Model:</strong><br><br>
          • <strong>Total Fines Levied:</strong> ₹${db.finesCollected || 2500} (from ANPR vehicle dumping & food notices).<br>
          • <strong>Citizen Rewards Issued:</strong> 150 Pts (+50 Pts / verified resolution).<br>
          • <strong>Financial Equilibrium:</strong> Penalties collected from commercial dumpers (+₹500/violation) directly fund civic credit utility rebates with zero fiscal deficit.
        `;
      }

      if (q.includes('lineman') || q.includes('worker') || q.includes('squad') || q.includes('task')) {
        return `
          👷 <strong>Field Squads & Lineman Workload:</strong><br><br>
          • <strong>Lineman Squad B:</strong> Suresh Kumar & Team assigned to <code>ISS-2026-00124</code> (11KV Transformer).<br>
          • <strong>Sanitation Squad 4:</strong> Lead Ramesh K. assigned to <code>ISS-2026-00123</code> (Market Gate Compactor).<br>
          • <strong>Resolution Verification:</strong> Field teams must upload high-resolution "After" proof photos before closing tickets.
        `;
      }

      return `
        🛡️ <strong>Municipal SCADA & Command Copilot:</strong> Tactical intelligence commands:
        <ul style="margin: 6px 0 0 16px; font-size: 0.82rem; color: #cbd5e1;">
          <li>"Check <strong>48h SLA escalation risks</strong>"</li>
          <li>"Show <strong>SCADA Feeder #4 outage status</strong>"</li>
          <li>"Explain <strong>auto fleet allocation algorithms</strong>"</li>
          <li>"Analyze <strong>GIS Red-Zone hotspots</strong>"</li>
          <li>"Show <strong>e-Challan fine fund balance</strong>"</li>
        </ul>
      `;
    }

    // =========================================================================
    // C. FOOD SAFETY AUTHORITY (FSO) PORTAL (PERSONA: FSSAI REGULATORY COPILOT)
    // =========================================================================
    if (dept === 'food') {
      if (q.match(/\b(hi|hello|hey|greetings|welcome)\b/)) {
        return `
          🍲 <strong>FSSAI Regulatory Copilot:</strong> Ready for inspection duties, Officer <strong>Dr. Lakshmi Prasad</strong>.<br><br>
          Current Registry: <strong>${vendors.length} Establishments Monitored</strong> • <strong>3 Active Notices</strong> • <strong>₹2,500 Penalties Levied</strong>.<br>
          How can I assist your regulatory audits?
        `;
      }

      if (q.includes('penalty') || q.includes('fine') || q.includes('framework') || q.includes('tier') || q.includes('scale') || q.includes('act')) {
        return `
          ⚖️ <strong>FSSAI Progressive Penalty Framework (Act 2006):</strong><br><br>
          • ⚠️ <strong>1st Notice (Minor Hazard):</strong> ₹500 Fine + 7-Day Statutory Improvement Notice.<br>
          • 🚨 <strong>2nd Notice (Critical Violation):</strong> ₹2,000 Heavy Fine + 7-Day Probation (Grade C Notice).<br>
          • 🛑 <strong>3rd Notice (Continuous Violation):</strong> ₹5,000 Fine + Immediate Trade License Revocation & Outlet Sealing.<br>
          • <strong>Statutory Clauses:</strong> Section 56 (Rancid Oil), Section 58 (Open Drains), Section 59 (Expired Food), Section 60 (Water Safety).
        `;
      }

      if (q.includes('gas') || q.includes('mq') || q.includes('135') || q.includes('ppm') || q.includes('spoilage') || q.includes('ammonia')) {
        return `
          🥩 <strong>MQ-135 IoT Food Spoilage Gas Telemetry:</strong><br><br>
          • 🟢 <strong>&lt; 220 PPM:</strong> Normal Food Prep Atmosphere (Hygienic standard).<br>
          • 🟡 <strong>220 – 350 PPM:</strong> Elevated Volatile Organic Compounds (Warning threshold).<br>
          • 🔴 <strong>&gt; 350 PPM:</strong> 🚨 Critical Spoilage Risk (High Ammonia, Methane & Decomposition Gases) $\rightarrow$ Triggers <strong>Automatic FSSAI Inspection Notice</strong>!
        `;
      }

      if (q.includes('certif') || q.includes('grade a') || q.includes('qr') || q.includes('award') || q.includes('clean vendor')) {
        return `
          📜 <strong>Digital QR Food Hygiene Certification:</strong><br><br>
          • <strong>Eligibility:</strong> Minimum hygiene audit score of <strong>85/100</strong> and MQ-135 gas reading <strong>&lt; 220 PPM</strong>.<br>
          • <strong>Seal:</strong> Digital Gold & Emerald Certificate stamped under <em>FSSAI Clean Street Food Hub Guidelines</em> with 1-year validity.<br>
          • <strong>Public QR:</strong> Diners can scan the stall's QR code to verify water test records and oil TPM audit dates!
        `;
      }

      if (q.includes('oil') || q.includes('stale') || q.includes('section 56') || q.includes('tpm') || q.includes('burnt')) {
        return `
          🍳 <strong>Section 56: Stale & Burnt Cooking Oil Violation:</strong><br><br>
          • <strong>Legal Limit:</strong> Total Polar Materials (TPM) must not exceed <strong>25%</strong>.<br>
          • <strong>Enforcement Action:</strong> Discard burnt oil batch immediately; mandate installation of digital TPM tester and daily oil filtration log.<br>
          • <strong>Fine:</strong> ₹2,000 penalty under Section 56 (e.g. <code>ISS-2026-00128</code> at Sri Krishna Seafood).
        `;
      }

      if (q.includes('rectif') || q.includes('re-audit') || q.includes('clear') || q.includes('re-inspect') || q.includes('how to solve')) {
        return `
          🛠️ <strong>Food Safety Rectification & Clearance Protocol:</strong><br><br>
          1. In the <strong>Hygiene Violations</strong> tab, click <strong>[ 🛠️ Rectify Problem ]</strong> on the target notice.<br>
          2. Record re-inspection audit proof (e.g. fresh oil batch tested TPM 12%, sneeze shields installed, water tested).<br>
          3. Input re-tested <strong>MQ-135 Gas PPM (e.g. 145 PPM)</strong> and hygiene score (e.g. <strong>94/100</strong>).<br>
          4. Select <strong>🟢 Compliant & Fully Rectified</strong> $\rightarrow$ This clears the violation and upgrades the establishment to <strong>Grade A+ Certified</strong>!
        `;
      }

      if (q.includes('seizure') || q.includes('cancel') || q.includes('close') || q.includes('seal') || q.includes('suspension')) {
        return `
          🛑 <strong>Emergency Commercial Seizure Protocol:</strong><br><br>
          • <strong>Grounds:</strong> Severe spoilage (MQ-135 &gt; 500 PPM, e.g. Marina Fish Fry Stalls) or continuous failure to rectify after 2 statutory notices.<br>
          • <strong>Enforcement:</strong> Immediate confiscation of adulterated ingredients, physical stall sealing, and filing of formal prosecution under Section 59.
        `;
      }

      return `
        🍲 <strong>FSSAI Regulatory AI Copilot:</strong> Regulatory commands available:
        <ul style="margin: 6px 0 0 16px; font-size: 0.82rem; color: #cbd5e1;">
          <li>"Explain <strong>FSSAI penalties & fine scale</strong>"</li>
          <li>"Show <strong>MQ-135 food spoilage gas thresholds</strong>"</li>
          <li>"How to <strong>rectify and clear a food violation</strong>"</li>
          <li>"Explain <strong>Section 56 stale cooking oil rules</strong>"</li>
          <li>"How to <strong>issue a Grade A+ certificate</strong>"</li>
        </ul>
      `;
    }

    // Dynamic Fallback
    return `
      🤖 I'm here to help with <strong>Smart Civic Connect</strong>! Ask about your department tasks, ticket tracking, or rules.
    `;
  }

    window.toggleChatbot = function(forceOpen) {
    const cWindow = document.getElementById('chatbotWindow');
    if (!cWindow) return;
    if (forceOpen === true) {
      cWindow.classList.add('active');
    } else if (forceOpen === false) {
      cWindow.classList.remove('active');
    } else {
      cWindow.classList.toggle('active');
    }
  };

  window.askChatbot = function(promptText) {
    handleChatbotMessage(promptText);
  };


  // =========================================================================
  // 8. MULTILINGUAL VOICE AI ENGINE (GENUINE BROWSER-NATIVE WEB SPEECH API)
  // =========================================================================
  let activeSpeechRecognition = null;

  window.toggleVoiceRecording = function() {
    const btn = document.getElementById('voiceAiBtn');
    const label = document.getElementById('voiceBtnLabel');
    const statusText = document.getElementById('voiceStatusText');
    const wave = document.getElementById('voiceWaveform');
    const descInput = document.getElementById('reportDescInput');
    const titleInput = document.getElementById('reportTitleInput');

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      showToast('Speech Recognition not supported on this browser. Please use Chrome, Edge, or Android Chrome.', 'error', '🎙️');
      return;
    }

    if (activeSpeechRecognition) {
      try {
        activeSpeechRecognition.stop();
      } catch (e) {}
      activeSpeechRecognition = null;
      if (btn) btn.classList.remove('recording');
      if (label) label.textContent = 'Record Voice';
      if (statusText) statusText.textContent = '🎙️ Voice recording stopped.';
      if (wave) wave.style.display = 'none';
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-IN'; // Indian English, catches mixed Hindi/Telugu terms

      recognition.onstart = function() {
        activeSpeechRecognition = recognition;
        if (btn) btn.classList.add('recording');
        if (label) label.textContent = '🔴 Listening to your voice... Speak now!';
        if (statusText) statusText.innerHTML = '<span style="color:#10b981; font-weight:700;">🎙️ Microphone Live:</span> Speak your complaint now...';
        if (wave) wave.style.display = 'flex';
        playNotificationSound('chime');
        showToast('Microphone active! Speak your complaint now...', 'info', '🎙️');
      };

      recognition.onresult = function(event) {
        let fullTranscript = '';
        for (let i = 0; i < event.results.length; ++i) {
          fullTranscript += event.results[i][0].transcript + ' ';
        }

        const spokenText = fullTranscript.trim();
        if (spokenText) {
          if (descInput) {
            descInput.value = spokenText;
          }
          if (titleInput && (!titleInput.value || titleInput.value.length < 5)) {
            titleInput.value = spokenText.slice(0, 45) + (spokenText.length > 45 ? '...' : '');
          }
          if (statusText) {
            statusText.innerHTML = `🗣️ <em>"${spokenText}"</em>`;
          }
        }
      };

      recognition.onerror = function(event) {
        console.warn('Speech recognition error:', event.error);
        if (event.error === 'not-allowed') {
          showToast('Microphone permission denied. Please allow microphone in browser.', 'error', '⚠️');
        } else if (event.error !== 'no-speech') {
          showToast(`Speech recognition: ${event.error}`, 'error', '🎙️');
        }
        if (btn) btn.classList.remove('recording');
        if (label) label.textContent = 'Record Voice';
        if (statusText) statusText.textContent = 'Click mic to speak your complaint';
        if (wave) wave.style.display = 'none';
        activeSpeechRecognition = null;
      };

      recognition.onend = function() {
        if (btn) btn.classList.remove('recording');
        if (label) label.textContent = 'Record Voice';
        if (wave) wave.style.display = 'none';
        activeSpeechRecognition = null;
        if (descInput && descInput.value) {
          if (statusText) statusText.textContent = '✅ Voice transcribed live into complaint box!';
          showToast('Voice transcribed successfully!', 'reward', '🎙️');
        }
      };

      recognition.start();
    } catch (err) {
      showToast('Could not access microphone: ' + err.message, 'error', '⚠️');
    }
  };

  // =========================================================================
  // 8.1 LIVE GPS GEOLOCATION & IMAGE EVIDENCE SUBMISSION ENGINE
  // =========================================================================
  let currentDetectedGpsCoords = { lat: 17.0010, lng: 81.8045, accuracy: 4 };
  let selectedReportImageBase64 = null;

  window.detectLiveGPSLocation = function() {
    const btn = document.getElementById('modalGpsDetectBtn');
    const label = document.getElementById('modalGpsBtnLabel');
    const statusText = document.getElementById('modalGpsStatusText');
    const streetInput = document.getElementById('reportLocationInput');
    const watermarkGps = document.getElementById('previewGpsWatermark');

    if (btn) btn.classList.add('locating');
    if (label) label.textContent = 'Locking Satellites...';
    if (statusText) {
      statusText.innerHTML = `
        <span class="gps-pulse-dot" style="background:#f59e0b; box-shadow:0 0 8px #f59e0b;"></span>
        <span style="color:#f59e0b;">Acquiring high-precision GPS lock...</span>
      `;
    }

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const lat = parseFloat(position.coords.latitude.toFixed(6));
          const lng = parseFloat(position.coords.longitude.toFixed(6));
          const acc = Math.round(position.coords.accuracy || 5);
          currentDetectedGpsCoords = { lat, lng, accuracy: acc };

          finishGpsLock(lat, lng, acc);
        },
        (error) => {
          console.warn("GPS Access notice:", error.message);
          // Graceful fallback to authentic local municipality coordinates
          const simLat = 17.0010 + (Math.random() - 0.5) * 0.004;
          const simLng = 81.8045 + (Math.random() - 0.5) * 0.004;
          currentDetectedGpsCoords = { lat: parseFloat(simLat.toFixed(6)), lng: parseFloat(simLng.toFixed(6)), accuracy: 4 };
          finishGpsLock(currentDetectedGpsCoords.lat, currentDetectedGpsCoords.lng, 4);
        },
        { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }
      );
    } else {
      finishGpsLock(17.0010, 81.8045, 5);
    }

    function finishGpsLock(lat, lng, acc) {
      setTimeout(() => {
        if (btn) btn.classList.remove('locating');
        if (label) label.textContent = '📍 GPS Locked';
        if (statusText) {
          statusText.innerHTML = `
            <span class="gps-pulse-dot"></span>
            <span style="color:#38bdf8;">GPS Locked: ${lat}° N, ${lng}° E (±${acc}m)</span>
          `;
        }
        if (watermarkGps) {
          watermarkGps.textContent = `📍 GPS: ${lat}° N, ${lng}° E (±${acc}m)`;
        }
        if (streetInput && !streetInput.value) {
          streetInput.value = `Gandhi Statue Main Road (Geotagged #${Math.floor(100+Math.random()*900)})`;
        }
        showToast(`📍 GPS Geotag Locked (${lat}° N, ${lng}° E)!`, 'reward', '📡');
      }, 700);
    }
  };

  // Image Upload / Camera File Selection Handler with Real-Time AI Auto-Scan
  window.handleImageUpload = function(inputEl) {
    if (!inputEl || !inputEl.files || !inputEl.files[0]) return;
    const file = inputEl.files[0];

    const reader = new FileReader();
    reader.onload = function(e) {
      selectedReportImageBase64 = e.target.result;
      displaySelectedImage(selectedReportImageBase64, file.name);
      showToast(`📸 Photo "${file.name}" attached! Scanning with Gemini AI...`, 'reward', '⚡');
      window.autoRunAiDetectionOnImage(selectedReportImageBase64);
    };
    reader.readAsDataURL(file);
  };

  // Clickable Verified Sample Photo Presets with Real-Time AI Auto-Scan
  window.selectSamplePhoto = function(type) {
    const samples = {
      garbage: 'https://images.unsplash.com/photo-1605600659908-0ef719419d41?w=800&auto=format&fit=crop&q=80',
      spark: 'https://images.unsplash.com/photo-1544724569-5f546fd6f2b5?w=800&auto=format&fit=crop&q=80',
      water: 'https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?w=800&auto=format&fit=crop&q=80',
      food: 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800&auto=format&fit=crop&q=80'
    };

    selectedReportImageBase64 = samples[type] || samples.garbage;
    displaySelectedImage(selectedReportImageBase64, `${type}_evidence.jpg`);
    showToast('📸 Photo attached! Scanning with Gemini AI...', 'reward', '⚡');
    window.autoRunAiDetectionOnImage(selectedReportImageBase64);
  };

  // Real-Time Automated AI Auto-Triage & Duplicate Detector
  window.autoRunAiDetectionOnImage = async function(imgSrc) {
    if (!imgSrc) return;

    const banner = document.getElementById('reportAiScanBanner');
    if (banner) {
      banner.style.display = 'flex';
      banner.innerHTML = '<span>⚡ Real-Time Gemini AI Scanning Hazard & Checking Duplicates...</span>';
    }

    try {
      const selectedWard = (document.getElementById('modalReportWard') ? document.getElementById('modalReportWard').value : '');
      
      // 1. Real-Time Duplicate & Crop Detection
      const dupRes = await AiEngine.checkDuplicate(imgSrc, selectedWard);
      if (dupRes && dupRes.isDuplicate && dupRes.matchedIssue) {
        currentAiDuplicateMatch = dupRes.matchedIssue;
        renderAiDuplicateModal(dupRes, imgSrc);
        window.openModal('aiDuplicateModal');
        if (banner) banner.innerHTML = '<span>🚨 Duplicate Match Found with #' + dupRes.matchedIssue.id + '</span>';
        return;
      }

      // 2. Real-Time Multimodal Hazard Auto-Triage
      const aiData = await AiEngine.analyzeHazard(imgSrc);
      if (aiData) {
        const titleInput = document.getElementById('reportTitle');
        const descInput = document.getElementById('reportDesc');
        const deptSelect = document.getElementById('modalReportDept');
        const catSelect = document.getElementById('modalReportCategory');

        if (titleInput) {
          titleInput.value = aiData.title || 'Civic Waste Hazard';
          titleInput.style.borderColor = '#10b981';
        }
        if (descInput) {
          descInput.value = aiData.description || 'Observed municipal hazard requiring squad dispatch.';
          descInput.style.borderColor = '#10b981';
        }
        if (deptSelect && aiData.department) {
          deptSelect.value = aiData.department;
          window.handleModalDeptChange(aiData.department);
        }
        if (catSelect && aiData.category) {
          catSelect.value = aiData.category;
        }

        if (banner) {
          banner.innerHTML = `<span>✨ Gemini AI Auto-Filled: <strong>${aiData.categoryName || 'Hazard'}</strong> (${aiData.estimatedTonnage || 'Bulk'})</span>`;
          banner.style.background = 'rgba(16, 185, 129, 0.2)';
          banner.style.borderColor = '#10b981';
          banner.style.color = '#34d399';
        }
        showToast(`✨ Real-Time AI Auto-Filled: ${aiData.title}`, 'success', '🧠');
      }
    } catch (err) {
      console.error(err);
      if (banner) banner.style.display = 'none';
    }
  };

  function displaySelectedImage(imageUrl, label) {
    const previewCard = document.getElementById('reportImagePreviewCard');
    const thumbnail = document.getElementById('reportPreviewThumbnail');
    const actionsContainer = document.getElementById('imageUploadActionsContainer');
    const zone = document.getElementById('reportImageSubmissionZone');
    const watermarkTime = document.getElementById('previewTimeWatermark');

    if (thumbnail) thumbnail.src = imageUrl;
    if (previewCard) previewCard.classList.add('active');
    if (actionsContainer) actionsContainer.style.display = 'none';
    if (zone) zone.classList.add('has-image');

    if (watermarkTime) {
      watermarkTime.textContent = `⏱️ ${new Date().toLocaleTimeString()} • Swachh Bharat Geotag Proof`;
    }
  }

  window.clearSelectedImage = function() {
    selectedReportImageBase64 = null;
    const previewCard = document.getElementById('reportImagePreviewCard');
    const actionsContainer = document.getElementById('imageUploadActionsContainer');
    const zone = document.getElementById('reportImageSubmissionZone');
    const camInput = document.getElementById('reportCameraInput');
    const galInput = document.getElementById('reportGalleryInput');

    if (previewCard) previewCard.classList.remove('active');
    if (actionsContainer) actionsContainer.style.display = 'block';
    if (zone) zone.classList.remove('has-image');
    if (camInput) camInput.value = '';
    if (galInput) galInput.value = '';
  };

  // e-Challan Handlers
  window.openChallanModal = function() {
    const modal = document.getElementById('challanPaymentModal');
    if (modal) modal.classList.add('active');
  };

  window.simulateChallanPaySuccess = function() {
    db.addFine(500);
    window.closeModal('challanPaymentModal');
    showToast('e-Challan #ECH-2026-881 Paid! ₹500 added to Municipal Fund.', 'reward', '🎉');
    renderMunicipalDashboard();
  };

  window.openCitizenCertificateModal = function() {
    window.openModal('citizenCertModal');
  };

  // =========================================================================
  // 9. LIVE IN-APP WHATSAPP WEB CLIENT ENGINE
  // =========================================================================
  window.handleSendWaMessage = function(customText, mediaUrl, isLocation) {
    const input = document.getElementById('waMsgInput');
    const viewport = document.getElementById('waMessagesViewport');
    if (!viewport) return;

    const text = (customText || (input ? input.value : '')).trim();
    if (!text && !mediaUrl) return;

    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // Render User Message
    const userMsg = document.createElement('div');
    userMsg.className = 'wa-msg user';
    let innerHtml = `<div>${text}</div>`;
    if (mediaUrl) {
      innerHtml += `<img src="${mediaUrl}" class="wa-msg-img-preview" alt="Attachment">`;
    }
    innerHtml += `
      <div class="wa-msg-meta">
        <span>${timeStr}</span>
        <span class="wa-msg-ticks">✓✓</span>
      </div>
    `;
    userMsg.innerHTML = innerHtml;
    viewport.appendChild(userMsg);

    if (input) input.value = '';
    viewport.scrollTop = viewport.scrollHeight;

    // Simulate Bot Response
    setTimeout(() => {
      const botMsg = document.createElement('div');
      botMsg.className = 'wa-msg bot';
      const botTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

      let replyContent = '';
      const q = text.toLowerCase();

      if (mediaUrl || q.includes('garbage') || q.includes('waste') || q.includes('photo') || q.includes('dump') || q.includes('trash')) {
        const quota = db.getCitizenDailyReportsUsage();
        if (quota.isLimitReached) {
          replyContent = `
            ⚠️ <strong>Daily Limit Reached (3/3 Reports Used Today)</strong><br><br>
            You have already reached the maximum limit of <strong>3 civic reports today</strong> across all departments (Food Safety, Smart Electricity, Sanitation & Waste).<br><br>
            ⏳ <em>Why is there a limit?</em> To prevent spam and ensure our municipal rapid squads can uphold our strict <strong>48-Hour SLA resolution guarantee</strong>.<br><br>
            🔄 Your daily quota will automatically reset at <strong>12:00 AM Midnight</strong>.
          `;
          showToast('Daily reporting limit reached (3/3 used today).', 'error', '⚠️');
        } else {
          // Create an official ticket in database!
          try {
            const newTicket = db.createIssue({
              state: selectedState || 'Andhra Pradesh',
              city: selectedCity || 'Surampalem',
              ward: selectedWard !== 'all' ? selectedWard : 'Ward 12 (Market Zone)',
              street: 'Gandhi Statue Main Road',
              department: 'sanitation',
              deptName: 'Sanitation & Waste Management',
              deptIcon: '🏢',
              title: 'WhatsApp Report: Garbage & Roadside Litter',
              description: 'Geotagged hazard reported via Clean & Safe India WhatsApp Business Bot (+91 90000 00000).',
              location: 'Ward 12 (Market Zone), Gandhi Statue Main Road, Surampalem',
              category: 'garbage',
              categoryName: 'WhatsApp Citizen Report',
              categoryIcon: '📱',
              severity: 'medium',
              severityLabel: 'ACTIVE',
              imageBefore: mediaUrl || 'https://images.unsplash.com/photo-1605600659908-0ef719419d41?w=800&auto=format&fit=crop&q=80'
            });

            replyContent = `
              ✅ <strong>Official Ticket Created!</strong><br><br>
              🎫 <strong>Ticket ID:</strong> <code>${newTicket.id}</code><br>
              📍 <strong>Jurisdiction:</strong> ${newTicket.location}<br>
              ⏱️ <strong>48h SLA Guarantee:</strong> Active (Assigned to Collection Truck AP-05-TX)<br>
              📊 <strong>Daily Quota:</strong> ${3 - (db.getCitizenDailyReportsUsage().used)} of 3 reports remaining today.<br><br>
              🎖️ <em>You will automatically receive <strong>+50 Civic Credits</strong> once our municipal squad cleans the site!</em>
            `;
            showToast(`WhatsApp Ticket #${newTicket.id} logged in live feed!`, 'reward', '📱');
            renderCitizenDashboard();
          } catch (err) {
            replyContent = `⚠️ <strong>Error:</strong> ${err.message}`;
            showToast(err.message, 'error', '⚠️');
          }
        }
      } else if (q.includes('power') || q.includes('electric') || q.includes('outage') || q.includes('spark') || q.includes('transformer')) {
        const quota = db.getCitizenDailyReportsUsage();
        if (quota.isLimitReached) {
          replyContent = `
            ⚠️ <strong>Daily Limit Reached (3/3 Reports Used Today)</strong><br><br>
            You have already reached the maximum limit of <strong>3 civic reports today</strong> across all departments.<br><br>
            🚨 For live electrical hazards, call SCADA Emergency directly: <strong>1912 / 112</strong>.<br>
            🔄 Your daily reporting quota resets at <strong>12:00 AM Midnight</strong>.
          `;
          showToast('Daily reporting limit reached (3/3 used today).', 'error', '⚠️');
        } else {
          try {
            const newTicket = db.createIssue({
              state: selectedState || 'Andhra Pradesh',
              city: selectedCity || 'Surampalem',
              ward: selectedWard !== 'all' ? selectedWard : 'Ward 12 (Market Zone)',
              street: 'Commercial Complex Lane',
              department: 'electricity',
              deptName: 'Smart Electricity Department',
              deptIcon: '⚡',
              title: 'WhatsApp Report: Electricity Power Sparking',
              description: 'Power grid fault reported via WhatsApp Business.',
              location: 'Ward 12 (Market Zone), Commercial Complex Lane, Surampalem',
              category: 'transformer_damage',
              categoryName: 'Electrical Sparking',
              categoryIcon: '⚡',
              severity: 'bulk',
              severityLabel: 'HIGH CRITICAL',
              imageBefore: 'https://images.unsplash.com/photo-1544724569-5f546fd6f2b5?w=800&auto=format&fit=crop&q=80'
            });

            replyContent = `
              ⚡ <strong>Emergency Power Alert Registered!</strong><br><br>
              🎫 <strong>Ticket ID:</strong> <code>${newTicket.id}</code><br>
              👷 <strong>Lineman Dispatch:</strong> Squad B (Bucket Van AP-05-EB) dispatched.<br>
              ⏱️ <strong>Restoration ETA:</strong> ~45 Minutes.<br>
              📊 <strong>Daily Quota:</strong> ${3 - (db.getCitizenDailyReportsUsage().used)} of 3 reports remaining today.
            `;
            showToast(`Power alert #${newTicket.id} dispatched!`, 'reward', '⚡');
            renderCitizenDashboard();
          } catch (err) {
            replyContent = `⚠️ <strong>Error:</strong> ${err.message}`;
            showToast(err.message, 'error', '⚠️');
          }
        }
      } else if (isLocation || q.includes('location') || q.includes('gps') || q.includes('pin')) {
        replyContent = `
          📍 <strong>Live GPS Geotag Received:</strong><br>
          • <strong>Coordinates:</strong> 17.0010° N, 81.8045° E<br>
          • <strong>Ward Jurisdiction:</strong> Ward 12 Market Zone, Surampalem (Andhra Pradesh)<br>
          • <strong>Nearest Municipal Squad:</strong> Collection Truck AP-05-TX (400m away).
        `;
      } else if (q.includes('status') || q.includes('track') || q.includes('check')) {
        const userIssues = db.getAllIssues().filter(i => i.reportedBy === (auth.getUser() ? auth.getUser().name : 'KRISH') || i.userId === (auth.getUser() ? auth.getUser().id : 'user-101')).slice(0, 3);
        replyContent = `
          📦 <strong>Your Live Grievance Tracking (Order-Style):</strong><br><br>
          ${userIssues.map(i => {
            const isResolved = i.status === 'resolved';
            const isEscalated = i.status === 'escalated' || i.isSlaBreached;
            return `
              • <strong>#${i.id}</strong>: <em>${i.title}</em><br>
                - 📅 <strong>Reported:</strong> ${formatReportDateTime(i.timestamp)}<br>
                - ⏱️ <strong>SLA Status:</strong> ${isResolved ? '✅ Resolved on schedule' : isEscalated ? '🚨 SLA Breached (>48h) — Forwarded to Commissioner' : `${i.slaHoursLeft}h remaining`}<br>
                - 👷 <strong>Squad:</strong> ${i.assignedWorker || 'Dispatched'} (${i.workerStatus || 'Active'})<br>
            `;
          }).join('')}
        `;
      } else if (q.includes('credit') || q.includes('point') || q.includes('streak') || q.includes('balance')) {
        const user = auth.getUser();
        replyContent = `
          🪙 <strong>Your Civic Standing:</strong><br>
          • <strong>Total Credits:</strong> ${user ? user.civicCredits || 150 : 150} Civic Credits<br>
          • <strong>Active Streak:</strong> 🔥 4-Week Streak<br>
          • <strong>Tier:</strong> Level 3 Silver Civic Guardian<br>
          • <em>You can view and print your Government Certificate in the Rewards tab!</em>
        `;
      } else {
        replyContent = `
          🤖 I am your 24/7 SmartCity WhatsApp Bot. You can:<br>
          1. Send a photo of garbage or water leaks.<br>
          2. Report electricity faults or sparking wires.<br>
          3. Send your GPS location pin.<br>
          4. Type "Track status" or "My credits".
        `;
      }

      botMsg.innerHTML = `
        <div>${replyContent}</div>
        <div class="wa-msg-meta">
          <span>${botTime}</span>
        </div>
      `;

      viewport.appendChild(botMsg);
      viewport.scrollTop = viewport.scrollHeight;
    }, 600);
  };

  window.sendWaQuickAction = function(type) {
    if (type === 'photo') {
      window.handleSendWaMessage(
        '📷 [Hazard Photo Uploaded: Garbage overflowing near Gandhi Statue Market Gate]',
        'https://images.unsplash.com/photo-1605600659908-0ef719419d41?w=800&auto=format&fit=crop&q=80',
        false
      );
    } else if (type === 'power') {
      window.handleSendWaMessage(
        '⚡ [Power Outage Report: Transformer sparking and feeder down at Main Road]',
        null,
        false
      );
    } else if (type === 'location') {
      window.handleSendWaMessage(
        '📍 [GPS Location Pin Shared: 17.0010° N, 81.8045° E - Ward 12 Market Junction]',
        null,
        true
      );
    } else if (type === 'status') {
      window.handleSendWaMessage('Check my ticket status', null, false);
    } else if (type === 'points') {
      window.handleSendWaMessage('Check my civic credits and active streak', null, false);
    }
  };

  window.recordWaVoiceNote = function() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      showToast('Speech Recognition not supported on this browser.', 'error', '🎙️');
      return;
    }

    showToast('🎙️ Live Voice Recording... Speak your complaint now!', 'info', '🎙️');
    try {
      const recognition = new SpeechRecognition();
      recognition.lang = 'en-IN';
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;

      recognition.onresult = function(event) {
        const spoken = event.results[0][0].transcript;
        if (spoken) {
          window.handleSendWaMessage(
            `🎙️ <em>Voice Note: "${spoken}"</em>`,
            null,
            false
          );
          showToast('Voice note transcribed & dispatched!', 'reward', '🎙️');
        }
      };

      recognition.onerror = function(e) {
        if (e.error === 'not-allowed') {
          showToast('Microphone access denied.', 'error', '⚠️');
        } else {
          showToast('Voice error: ' + e.error, 'error', '⚠️');
        }
      };

      recognition.start();
    } catch (err) {
      showToast('Could not start microphone: ' + err.message, 'error', '⚠️');
    }
  };

  // =========================================================================
  // 10. GLOBAL EXPOSED ROUTING & FOOD SAFETY HANDLERS
  // =========================================================================
  let activeCitizenAuthSubMode = 'signin';
  let regOtpCountdownTimer = null;

  window.switchCitizenAuthSubMode = function(mode) {
    activeCitizenAuthSubMode = mode;
    const signInBtn = document.getElementById('citizenSubModeSignInBtn');
    const regBtn = document.getElementById('citizenSubModeRegisterBtn');
    const signInForm = document.getElementById('authLoginForm');
    const regForm = document.getElementById('authRegisterForm');

    if (mode === 'signin') {
      if (signInBtn) {
        signInBtn.style.background = '#10b981';
        signInBtn.style.color = '#060911';
      }
      if (regBtn) {
        regBtn.style.background = 'transparent';
        regBtn.style.color = '#94a3b8';
      }
      if (signInForm) signInForm.style.display = 'block';
      if (regForm) regForm.style.display = 'none';
    } else {
      if (regBtn) {
        regBtn.style.background = '#10b981';
        regBtn.style.color = '#060911';
      }
      if (signInBtn) {
        signInBtn.style.background = 'transparent';
        signInBtn.style.color = '#94a3b8';
      }
      if (signInForm) signInForm.style.display = 'none';
      if (regForm) regForm.style.display = 'block';
    }
  };

  window.handleSendRegistrationOTP = async function() {
    const nameInput = document.getElementById('regCitizenNameInput');
    const emailInput = document.getElementById('regCitizenEmailInput');
    const name = (nameInput ? nameInput.value : '').trim();
    const email = (emailInput ? emailInput.value : '').trim();

    if (!name) {
      showToast('Please enter your Full Name.', 'error', '⚠️');
      if (nameInput) nameInput.focus();
      return;
    }
    if (!email || !email.includes('@') || !email.includes('.')) {
      showToast('Please enter a valid email address.', 'error', '⚠️');
      if (emailInput) emailInput.focus();
      return;
    }

    const sendBtn = document.getElementById('regSendOtpBtn');
    if (sendBtn) {
      sendBtn.disabled = true;
      sendBtn.innerHTML = '<span>⏳</span> Generating OTP...';
    }

    try {
      const res = await fetch('/api/auth/send-otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email })
      });
      const data = await res.json();

      if (data.success && data.otp) {
        // Reveal Step 2
        const verifyStep = document.getElementById('regOtpVerifyStep');
        const sendStep = document.getElementById('regOtpSendStep');
        if (verifyStep) verifyStep.style.display = 'block';
        if (sendStep) sendStep.style.display = 'none';

        // Display OTP Banner
        const codeText = document.getElementById('regOtpCodeText');
        if (codeText) codeText.textContent = data.otp;

        // Auto-fill OTP field for effortless onboarding
        const otpInput = document.getElementById('regOtpInput');
        if (otpInput) otpInput.value = data.otp;

        playNotificationSound('chime');
        showToast(`🔐 Verification OTP Dispatched: ${data.otp}`, 'reward', '📩');

        // Start 60s Resend countdown
        let secondsLeft = 60;
        const timerText = document.getElementById('regOtpTimerText');
        if (regOtpCountdownTimer) clearInterval(regOtpCountdownTimer);
        regOtpCountdownTimer = setInterval(() => {
          secondsLeft--;
          if (timerText) timerText.textContent = `${secondsLeft}s`;
          if (secondsLeft <= 0) {
            clearInterval(regOtpCountdownTimer);
            if (sendStep) sendStep.style.display = 'block';
            if (sendBtn) {
              sendBtn.disabled = false;
              sendBtn.innerHTML = '<span>🔄</span> Resend Verification OTP';
            }
          }
        }, 1000);
      } else {
        showToast(data.error || 'Could not send OTP. Please try again.', 'error', '⚠️');
        if (sendBtn) {
          sendBtn.disabled = false;
          sendBtn.innerHTML = '<span>📲</span> Send Verification OTP';
        }
      }
    } catch (err) {
      showToast(err.message || 'Network error while sending OTP. Please check your connection.', 'error', '⚠️');
      if (sendBtn) {
        sendBtn.disabled = false;
        sendBtn.innerHTML = '<span>📲</span> Send Verification OTP';
      }
    }
  };

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
    const subModeToggle = document.getElementById('citizenAuthSubModeToggle');
    const registerHint = document.getElementById('citizenRegisterHintLink');
    const deptAcc = SYSTEM_ACCOUNTS[dept];

    if (dept === 'citizen') {
      if (headerTitle) headerTitle.textContent = "Citizen Portal Login";
      if (headerDesc) headerDesc.textContent = "Report civic issues, track 48h SLA & earn citizen credits";
      if (submitBtn) {
        submitBtn.className = "auth-btn-submit btn-dept-citizen";
        submitBtn.innerHTML = "<span>🚀</span> Login to Citizen Portal";
      }
      if (subModeToggle) subModeToggle.style.display = 'flex';
      if (registerHint) registerHint.style.display = 'block';
      window.switchCitizenAuthSubMode('signin');
    } else if (dept === 'municipal') {
      if (headerTitle) headerTitle.textContent = "Municipal & Electricity Official Login";
      if (headerDesc) headerDesc.textContent = "Administrative triage, vehicle dispatch & power SCADA control";
      if (submitBtn) {
        submitBtn.className = "auth-btn-submit btn-dept-municipal";
        submitBtn.innerHTML = "<span>🛡️</span> Access Municipal Command";
      }
      if (subModeToggle) subModeToggle.style.display = 'none';
      if (registerHint) registerHint.style.display = 'none';
      const signInForm = document.getElementById('authLoginForm');
      const regForm = document.getElementById('authRegisterForm');
      if (signInForm) signInForm.style.display = 'block';
      if (regForm) regForm.style.display = 'none';
    } else if (dept === 'food') {
      if (headerTitle) headerTitle.textContent = "Food Safety Authority (FSO) Login";
      if (headerDesc) headerDesc.textContent = "Official food hygiene inspections & digital QR certification";
      if (submitBtn) {
        submitBtn.className = "auth-btn-submit btn-dept-food";
        submitBtn.innerHTML = "<span>🍲</span> Access Food Safety Portal";
      }
      if (subModeToggle) subModeToggle.style.display = 'none';
      if (registerHint) registerHint.style.display = 'none';
      const signInForm = document.getElementById('authLoginForm');
      const regForm = document.getElementById('authRegisterForm');
      if (signInForm) signInForm.style.display = 'block';
      if (regForm) regForm.style.display = 'none';
    }

    if (demoEmailEl) demoEmailEl.textContent = deptAcc.email;
    if (demoPassEl) demoPassEl.textContent = deptAcc.password;
  };

  window.fillDemoCredentials = function() {
    const deptAcc = SYSTEM_ACCOUNTS[activeAuthDept];
    const emailInput = document.getElementById('authEmailInput');
    const passInput = document.getElementById('authPasswordInput');
    if (emailInput && passInput) {
      emailInput.value = deptAcc.email;
      passInput.value = deptAcc.password;
      showToast(`Loaded credentials for ${deptAcc.deptTitle}`, "info", "🔑");
    }
  };

  window.handleLogout = function() {
    auth.logout();
    checkAuthAndRoute();
    showToast("Logged out successfully.", "info", "🔒");
  };

  window.switchCitizenSubTab = function(tabName) {
    document.querySelectorAll('.citizen-subview').forEach(v => v.style.display = 'none');
    document.querySelectorAll('.citizen-nav-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.mobile-nav-citizen .mobile-nav-tab').forEach(b => b.classList.remove('active'));

    const targetView = document.getElementById(`citizenTab_${tabName}`);
    const targetBtn = document.querySelector(`.citizen-nav-btn[data-tab="${tabName}"]`);
    const mobileTargetBtn = document.querySelector(`.mobile-nav-citizen .mobile-nav-tab[data-tab="${tabName}"]`);

    if (targetView) targetView.style.display = 'block';
    if (targetBtn) targetBtn.classList.add('active');
    if (mobileTargetBtn) mobileTargetBtn.classList.add('active');

    renderCitizenDashboard();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  window.switchMunicipalSubTab = function(tabName) {
    document.querySelectorAll('.municipal-subview').forEach(v => v.style.display = 'none');
    document.querySelectorAll('.municipal-nav-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.mobile-nav-municipal .mobile-nav-tab').forEach(b => b.classList.remove('active'));

    const targetView = document.getElementById(`munTab_${tabName}`);
    const targetBtn = document.querySelector(`.municipal-nav-btn[data-tab="${tabName}"]`);
    const mobileTargetBtn = document.querySelector(`.mobile-nav-municipal .mobile-nav-tab[data-tab="${tabName}"]`);

    if (targetView) targetView.style.display = 'block';
    if (targetBtn) targetBtn.classList.add('active');
    if (mobileTargetBtn) mobileTargetBtn.classList.add('active');

    if (tabName === 'heatmap') {
      setTimeout(() => initGISMap([17.0010, 81.8045], 14), 80);
    }

    renderMunicipalDashboard();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  window.switchFoodSubTab = function(tabName) {
    if (tabName === 'registry') tabName = 'vendors';
    if (tabName === 'iotgas') tabName = 'gassensor';
    if (tabName === 'guidelines') tabName = 'policies';

    document.querySelectorAll('.food-subview').forEach(v => v.style.display = 'none');
    document.querySelectorAll('.food-nav-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.mobile-nav-food .mobile-nav-tab').forEach(b => b.classList.remove('active'));

    const targetView = document.getElementById(`foodTab_${tabName}`);
    const targetBtn = document.querySelector(`.food-nav-btn[data-tab="${tabName}"]`);
    const mobileTargetBtn = document.querySelector(`.mobile-nav-food .mobile-nav-tab[data-tab="${tabName}"]`);

    if (targetView) targetView.style.display = 'block';
    if (targetBtn) targetBtn.classList.add('active');
    if (mobileTargetBtn) mobileTargetBtn.classList.add('active');

    renderFoodSafetyDashboard();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  window.handleFoodFilter = function(filter, el) {
    foodFilter = filter;
    document.querySelectorAll('.food-filter-chip').forEach(b => b.classList.remove('active'));
    if (el) el.classList.add('active');
    renderFoodSafetyDashboard();
  };

  window.handleVendorFilter = function(filter, el) {
    vendorFilter = filter;
    document.querySelectorAll('.vendor-filter-chip').forEach(b => b.classList.remove('active'));
    if (el) el.classList.add('active');
    renderFoodSafetyDashboard();
  };

  window.openReportModal = function() {
    updateCitizenDailyQuotaUI();
    const quota = db.getCitizenDailyReportsUsage();
    if (quota.isLimitReached) {
      showToast(`Daily Limit: You have reached your maximum of ${quota.limit} reports for today across all departments. Resets at midnight.`, 'error', '⚠️');
    }
    window.openModal('reportIssueModal');
  };

  window.openFoodInspectionModal = function() {
    window.openModal('foodInspectionModal');
  };

  window.openFoodRectifyModal = function(issueId) {
    activeIssueIdForModal = issueId;
    const issue = db.getIssueById(issueId);
    const titleEl = document.getElementById('foodRectifyModalTitle');
    if (titleEl && issue) {
      titleEl.innerHTML = `<strong>Rectifying Complaint #${issue.id}:</strong> ${issue.title} (📍 ${issue.location})`;
    }

    window.openModal('foodRectifyModal');
  };

  window.openModal = function(id) {
    const modal = document.getElementById(id);
    if (modal) {
      modal.style.display = 'flex';
      modal.classList.add('active');
      document.body.style.overflow = 'hidden';
    }
  };

  window.closeModal = function(id) {
    const modal = document.getElementById(id);
    if (modal) {
      modal.classList.remove('active');
      modal.style.display = 'none';
      document.body.style.overflow = '';
    }
  };

  window.viewIssueDetail = function(issueId) {
    try {
      const issue = db.getIssueById(issueId);
      if (!issue) return;
      activeIssueIdForModal = issueId;

      const modal = document.getElementById('issueDetailModal');
      const content = document.getElementById('issueDetailContent');
      if (!modal || !content) return;

      const status = issue.status || 'pending';
      const severity = (issue.severity || 'medium').toUpperCase();
      const isResolved = status === 'resolved';
      const isEscalated = status === 'escalated' || Boolean(issue.isSlaBreached);
      const reportedTimeStr = formatReportDateTime(issue.timestamp || Date.now());
      const resolvedTs = isResolved ? getRealisticResolvedTimestamp(issue) : null;
      const resolvedTimeStr = isResolved ? formatReportDateTime(resolvedTs) : null;
      const turnaroundStr = isResolved ? calculateSlaTurnaround(issue.timestamp, resolvedTs, issue) : '2h 30m Turnaround';
      const deadlineTimestamp = issue.slaDeadline || ((issue.timestamp || Date.now()) + 48 * 3600 * 1000);
      const deadlineTimeStr = formatReportDateTime(deadlineTimestamp);

      const verifiedOfficer = issue.verifiedByOfficer || 'Consultant Officer K. Mukundha (GOV-MUNC-SEC-012)';
      const verifiedTimeStr = formatReportDateTime(issue.verifiedTimestamp || ((issue.timestamp || Date.now()) + 18 * 60 * 1000));
      const assignedWorker = issue.assignedWorker || 'Municipal Rapid Squad';
      const assignedTimeStr = formatReportDateTime(issue.assignedTimestamp || ((issue.timestamp || Date.now()) + 45 * 60 * 1000));
      const workerStatus = issue.workerStatus || (isResolved ? 'Completed & Verified On-Site' : isEscalated ? 'Delayed (>48h) — Auto-Forwarded' : 'Active On-Site Cleaning & Hazard Removal');
      const recommendedResource = issue.recommendedResource || 'Hydraulic Tipper & Sanitization Squad';
      const deptIcon = issue.deptIcon || '🏢';
      const deptName = issue.deptName || 'Sanitation & Civic Works';
      const issueTitle = issue.title || 'Civic Grievance';
      const issueLocation = issue.location || 'Surampalem, Andhra Pradesh';
      const imgBefore = issue.imageBefore || 'https://images.unsplash.com/photo-1605600659908-0ef719419d41?w=800&auto=format&fit=crop&q=80';
      const imgAfter = issue.imageAfter || 'https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=800&auto=format&fit=crop&q=80';

      content.innerHTML = `
        <div>
          <!-- Top Status & SLA Banner -->
          <div class="tracker-header-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 0.75rem;">
              <div>
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.35rem;">
                  <span class="cat-badge">${deptIcon} ${deptName}</span>
                  <span class="badge badge-${status}">${status.replace('_', ' ').toUpperCase()}</span>
                  <span class="badge sev-${(issue.severity || 'medium').toLowerCase()}">${severity}</span>
                </div>
                <h2 style="font-size: 1.35rem; color: white; margin: 0.2rem 0 0.4rem;">${issueTitle}</h2>
                <div style="font-size: 0.85rem; color: #94a3b8; display: flex; align-items: center; gap: 0.4rem;">
                  <span>📍</span> <span>${issueLocation}</span>
                </div>
              </div>
              <div style="text-align: right;">
                <div style="font-family: var(--font-mono); font-size: 1.05rem; color: #38bdf8; font-weight: 800;">${issue.id || 'ISS-2026'}</div>
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
                      <span class="sla-live-ticker" data-deadline="${deadlineTimestamp}">⏱️ 48H SLA ACTIVE: ${issue.slaHoursLeft || 36}H LEFT (Due ${deadlineTimeStr})</span>
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
                  ${isResolved ? `${resolvedTimeStr} (${turnaroundStr})` : isEscalated ? '🚨 Auto-Escalated to Commissioner' : `${issue.slaHoursLeft || 36} Hours Remaining`}
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
                <img src="${imgBefore}" style="width: 100%; height: 100%; object-fit: cover;" alt="Before">
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
    } catch (err) {
      console.error('viewIssueDetail error:', err);
    }
  };

  window.openCommentsModal = function(issueId) {
    window.viewIssueDetail(issueId);
    setTimeout(() => {
      const commentInput = document.getElementById('issueCommentInput');
      if (commentInput) {
        commentInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
        commentInput.focus();
      }
    }, 150);
  };

  window.submitComment = function(issueId) {
    const input = document.getElementById('issueCommentInput');
    if (!input || !input.value.trim()) {
      showToast('Please type a comment before posting.', 'error', '⚠️');
      return;
    }
    const text = input.value.trim();
    const author = auth.getUser() ? auth.getUser().name : 'Citizen Resident';
    db.addComment(issueId, text, author);
    input.value = '';
    showToast('Comment posted to grievance log!', 'reward', '💬');
    window.viewIssueDetail(issueId);
    renderCitizenDashboard();
  };

  window.openResolveModal = function(issueId) {
    activeIssueIdForModal = issueId;
    const issue = db.getIssueById(issueId);
    if (!issue) return;

    const titleEl = document.getElementById('resolveModalIssueTitle');
    if (titleEl) titleEl.textContent = `Resolving: #${issue.id} - ${issue.title}`;

    window.openModal('resolveIssueModal');
  };

  window.toggleUpvote = function(issueId) {
    db.toggleUpvote(issueId);
    renderCitizenDashboard();
    showToast("Upvoted! Priority escalated in local ward.", "info", "👍");
  };

  // View Both Grade A+ Digital Certificate & Statutory Violation Notice
  window.viewDigitalCertificate = function(vendorId) {
    const vendor = db.getAllVendors().find(v => v.id === vendorId);
    if (!vendor) return;

    const modal = document.getElementById('certificateModal');
    const card = document.getElementById('certificateCardContent');
    const headerTitle = document.getElementById('certificateModalHeader');
    if (!modal || !card) return;

    const isViolated = vendor.isViolated;

    if (headerTitle) {
      headerTitle.textContent = isViolated ? '🚨 FSSAI Statutory Violation Notice' : '📜 National Digital Food Hygiene Certificate';
    }

    if (isViolated) {
      // 🔴 Render Statutory Violation & Rectification Notice
      card.innerHTML = `
        <div class="vendor-cert-card violation-cert">
          <div class="cert-header">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
              <div style="width: 50px; height: 50px; border-radius: 10px; background: #ef4444; color: white; display: flex; align-items: center; justify-content: center; font-size: 1.8rem; box-shadow: 0 0 16px rgba(239,68,68,0.5);">⚠️</div>
              <div>
                <h3 style="font-size: 1.3rem; color: #f87171; margin-bottom: 2px;">${vendor.name}</h3>
                <p style="font-size: 0.85rem; color: #fca5a5; font-weight: 700;">OFFICIAL FSSAI STATUTORY VIOLATION & RECTIFICATION NOTICE</p>
              </div>
            </div>
            <div class="cert-stamp violation-stamp">
              <div class="cert-grade">${vendor.hygieneGrade}</div>
              <div>ON NOTICE</div>
            </div>
          </div>

          <div class="violation-notice-box">
            <div style="font-weight: 800; font-size: 0.95rem; color: #f87171; margin-bottom: 4px;">🚨 STATUTORY RECTIFICATION MANDATE (FSSAI ACT 2006)</div>
            <div><strong>Violation Clause:</strong> ${vendor.violationClause || 'Section 56: Stale & Burnt Cooking Oil'}</div>
            <div><strong>Penalty Imposed:</strong> <span style="font-family: var(--font-mono); font-weight: 800; color: #facc15;">${vendor.penaltyImposed || '₹2,000.00'}</span></div>
            <div><strong>Mandatory Rectification Deadline:</strong> <span style="font-weight: 700; color: white;">${vendor.rectificationDeadline || '48 Hours'}</span></div>
            <div><strong>MQ-135 Gas Risk:</strong> ${vendor.mq135GasPpm || '360 PPM'}</div>
            <div style="margin-top: 6px; font-size: 0.8rem; color: #fda4af;"><strong>Officer Directives:</strong> ${vendor.officerDirectives || 'Immediate corrective sanitation required. Re-audit mandatory.'}</div>
          </div>

          <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; font-size: 0.9rem; margin-bottom: 1.5rem; color: #cbd5e1;">
            <div>👤 <strong>Proprietor:</strong> ${vendor.owner}</div>
            <div>📍 <strong>Location:</strong> ${vendor.location}</div>
            <div>📊 <strong>Hygiene Audit Score:</strong> <span style="color: #f87171; font-weight: 800;">${vendor.score}</span></div>
            <div>🔍 <strong>Inspecting Officer:</strong> ${vendor.inspectedBy}</div>
            <div>🆔 <strong>Notice ID:</strong> <span style="font-family: var(--font-mono); color: #fca5a5;">${vendor.id}</span></div>
            <div>⚖️ <strong>Legal Status:</strong> <span style="color: #f87171; font-weight: 800;">${vendor.status}</span></div>
          </div>

          <div style="border-top: 1px dashed rgba(239, 68, 68, 0.4); padding-top: 0.75rem; font-size: 0.78rem; color: #94a3b8; text-align: center;">
            Failure to rectify within the statutory deadline will result in immediate trade license cancellation, outlet sealing, and criminal prosecution.
          </div>
        </div>
      `;
    } else {
      // 🟢 Render Certified Grade A+ Certificate
      card.innerHTML = `
        <div class="vendor-cert-card">
          <div class="cert-header">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
              <div style="width: 50px; height: 50px; border-radius: 10px; background: #10b981; color: white; display: flex; align-items: center; justify-content: center; font-size: 1.8rem; box-shadow: 0 0 16px rgba(16,185,129,0.5);">🍲</div>
              <div>
                <h3 style="font-size: 1.3rem; color: white; margin-bottom: 2px;">${vendor.name}</h3>
                <p style="font-size: 0.85rem; color: #f59e0b; font-weight: 700;">DIGITAL FOOD HYGIENE & SAFETY CERTIFICATE</p>
              </div>
            </div>
            <div class="cert-stamp">
              <div class="cert-grade">${vendor.hygieneGrade}</div>
              <div>VERIFIED</div>
            </div>
          </div>

          <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; font-size: 0.9rem; margin-bottom: 1.5rem; color: #cbd5e1;">
            <div>👤 <strong>Proprietor:</strong> ${vendor.owner}</div>
            <div>📍 <strong>Location:</strong> ${vendor.location}</div>
            <div>📊 <strong>Hygiene Audit Score:</strong> <span style="color: #34d399; font-weight: 800;">${vendor.score}</span></div>
            <div>📅 <strong>Validity:</strong> ${vendor.validTill}</div>
            <div>🔍 <strong>Inspected by:</strong> ${vendor.inspectedBy}</div>
            <div>🆔 <strong>Registration ID:</strong> <span style="font-family: var(--font-mono); color: #38bdf8;">${vendor.id}</span></div>
          </div>

          <div style="border-top: 1px dashed rgba(245, 158, 11, 0.4); padding-top: 0.75rem; font-size: 0.78rem; color: #94a3b8; text-align: center;">
            Officially verified and stamped under Food Safety and Standards Authority (FSSAI) Clean Street Food Hub Guidelines.
          </div>
        </div>
      `;
    }

    window.openModal('certificateModal');
  };

  // =========================================================================
  // 11. SINGLE CLEAN INITIALIZATION & EVENT BINDINGS
  // =========================================================================
  document.addEventListener('DOMContentLoaded', () => {
    checkAuthAndRoute();

    // WhatsApp Input Keydown (Enter to send)
    const waInput = document.getElementById('waMsgInput');
    if (waInput) {
      waInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          window.handleSendWaMessage();
        }
      });
    }

    // Login Form (Strict Async Real-Time Authentication)
    const authForm = document.getElementById('authLoginForm');
    if (authForm) {
      authForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = (document.getElementById('authEmailInput').value || '').trim();
        const pass = (document.getElementById('authPasswordInput').value || '').trim();
        const submitBtn = document.getElementById('authSubmitBtn');
        const origText = submitBtn ? submitBtn.innerHTML : '';

        if (submitBtn) {
          submitBtn.disabled = true;
          submitBtn.innerHTML = '<span>⏳</span> Verifying Credentials...';
        }

        try {
          const session = await auth.login(activeAuthDept, email, pass);
          showToast(`Access granted! Welcome, ${session.user.name}`, 'reward', '🛡️');
          checkAuthAndRoute();
        } catch (err) {
          showToast(err.message, 'error', '⚠️');
        } finally {
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = origText;
          }
        }
      });
    }

    // Citizen OTP Registration Form Submit
    const regForm = document.getElementById('authRegisterForm');
    if (regForm) {
      regForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = (document.getElementById('regCitizenNameInput').value || '').trim();
        const email = (document.getElementById('regCitizenEmailInput').value || '').trim();
        const otp = (document.getElementById('regOtpInput').value || '').trim();
        const pass = (document.getElementById('regPasswordInput').value || '').trim();
        const confirmPass = (document.getElementById('regConfirmPasswordInput').value || '').trim();

        if (!otp || otp.length < 6) {
          showToast('Please enter the 6-digit OTP sent to your email.', 'error', '⚠️');
          return;
        }
        if (!pass || pass.length < 4) {
          showToast('Password must be at least 4 characters.', 'error', '⚠️');
          return;
        }
        if (pass !== confirmPass) {
          showToast('Passwords do not match. Please re-enter.', 'error', '⚠️');
          return;
        }

        const completeBtn = document.getElementById('regCompleteBtn');
        if (completeBtn) {
          completeBtn.disabled = true;
          completeBtn.innerHTML = '<span>⏳</span> Creating Citizen Profile...';
        }

        try {
          const res = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, otp, password: pass })
          });
          const data = await res.json();

          if (data.success && data.user) {
            auth.saveSession({
              token: data.token,
              department: 'citizen',
              user: data.user,
              loginTime: new Date().toISOString()
            });

            playNotificationSound('chime');
            showToast(`🎉 Registration complete! +20 Welcome Civic Credits awarded to ${data.user.name}.`, 'reward', '🎖️');
            checkAuthAndRoute();
          } else {
            showToast(data.error || 'Registration failed. Check OTP.', 'error', '⚠️');
            if (completeBtn) {
              completeBtn.disabled = false;
              completeBtn.innerHTML = '<span>🎉</span> Complete Registration (+20 Welcome Credits)';
            }
          }
        } catch (err) {
          console.warn("Registration network error, falling back to local profile:", err);
          const fallbackUser = {
            id: 'user-' + Date.now().toString().slice(-4),
            name: name || 'Citizen User',
            email: email,
            department: 'citizen',
            roleTitle: 'Verified Civic Citizen',
            officialId: 'CITIZEN-AP-' + Math.floor(1000 + Math.random() * 9000),
            avatar: (name ? name.slice(0, 2).toUpperCase() : 'CU'),
            civicCredits: 20
          };
          auth.saveSession({
            token: 'CIVIC_JWT_' + Date.now(),
            department: 'citizen',
            user: fallbackUser,
            loginTime: new Date().toISOString()
          });
          playNotificationSound('chime');
          showToast(`🎉 Registration complete! +20 Welcome Civic Credits awarded to ${fallbackUser.name}.`, 'reward', '🎖️');
          checkAuthAndRoute();
        }
      });
    }

    // Citizen Report Form
    const reportForm = document.getElementById('reportIssueForm');
    if (reportForm) {
      reportForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const title = document.getElementById('reportTitleInput').value;
        const desc = document.getElementById('reportDescInput').value;
        const street = document.getElementById('reportLocationInput').value;
        const state = document.getElementById('modalReportState').value;
        const city = document.getElementById('modalReportCity').value;
        const ward = document.getElementById('modalReportWard').value;
        const dept = document.getElementById('reportDeptSelect').value;

        // Use user captured photo or default fallback
        const submittedImage = selectedReportImageBase64 || 'https://images.unsplash.com/photo-1605600659908-0ef719419d41?w=800&auto=format&fit=crop&q=80';

        try {
          const newIssue = db.createIssue({
            state: state,
            city: city,
            ward: ward,
            street: street,
            lat: currentDetectedGpsCoords.lat,
            lng: currentDetectedGpsCoords.lng,
            department: dept,
            deptName: dept === 'electricity' ? 'Smart Electricity Department' : dept === 'food_safety' ? 'Food Safety Department' : 'Sanitation & Waste Management',
            deptIcon: dept === 'electricity' ? '⚡' : dept === 'food_safety' ? '🍲' : '🏢',
            title: title,
            description: desc,
            location: `${ward}, ${street}, ${city}`,
            category: 'garbage',
            categoryName: 'Civic Report',
            categoryIcon: '📢',
            severity: document.getElementById('reportSeveritySelect').value,
            severityLabel: 'ACTIVE',
            imageBefore: submittedImage
          });

          reportForm.reset();
          window.clearSelectedImage();
          window.closeModal('reportIssueModal');

          const quota = db.getCitizenDailyReportsUsage();
          showToast(`Complaint #${newIssue.id} registered! (Daily Quota: ${quota.remaining} of ${quota.limit} remaining today)`, 'reward', '🎉');
          checkAuthAndRoute();
        } catch (err) {
          showToast(err.message, 'error', '⚠️');
        }
      });
    }

    // Food Safety Officer: Log Violation Notice Form
    const foodInspectionForm = document.getElementById('foodInspectionForm');
    if (foodInspectionForm) {
      foodInspectionForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const vendorName = document.getElementById('foodVendorNameInput').value;
        const ownerName = document.getElementById('foodOwnerNameInput').value;
        const state = document.getElementById('foodStateSelect').value;
        const city = document.getElementById('foodCitySelect').value;
        const ward = document.getElementById('foodWardInput').value;
        const street = document.getElementById('foodStreetInput').value;
        const clauseEl = document.getElementById('foodViolationTypeSelect');
        const clause = clauseEl.options[clauseEl.selectedIndex].text;
        const fine = document.getElementById('foodNoticeLevelSelect').value;
        const notes = document.getElementById('foodAuditNotesInput').value;

        const res = db.logFoodViolation({
          vendorName,
          ownerName,
          state,
          city,
          ward,
          street,
          violationClause: clause,
          fineAmount: fine,
          notes
        });

        foodInspectionForm.reset();
        window.closeModal('foodInspectionModal');
        showToast(`Notice #${res.vendor.id} logged for ${vendorName}! ₹${fine} fine recorded.`, 'reward', '⚖️');
        renderFoodSafetyDashboard();
      });
    }

    // Food Safety Officer: Rectify & Clear Form
    const foodRectifyForm = document.getElementById('foodRectifyForm');
    if (foodRectifyForm) {
      foodRectifyForm.addEventListener('submit', (e) => {
        e.preventDefault();
        if (!activeIssueIdForModal) return;

        const notes = document.getElementById('foodRectifyNotesInput').value;
        const gasPpm = document.getElementById('foodRectifyGasInput').value;
        const score = document.getElementById('foodRectifyScoreInput').value;
        const outcome = document.getElementById('foodRectifyOutcomeSelect').value;

        db.rectifyFoodIssue(activeIssueIdForModal, notes, gasPpm, score, outcome);

        foodRectifyForm.reset();
        window.closeModal('foodRectifyModal');
        showToast('Problem rectified! Premises re-audited and compliance recorded.', 'reward', '✅');
        renderFoodSafetyDashboard();
      });
    }

    // Municipal Resolve Form
    const resolveForm = document.getElementById('resolveIssueForm');
    if (resolveForm) {
      resolveForm.addEventListener('submit', (e) => {
        e.preventDefault();
        if (!activeIssueIdForModal) return;

        const notes = document.getElementById('resolveNotesInput').value;
        db.resolveIssue(activeIssueIdForModal, notes, 'https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=800&auto=format&fit=crop&q=80');

        resolveForm.reset();
        window.closeModal('resolveIssueModal');
        showToast('Site resolved & verified! +50 Civic Credits issued.', 'reward', '🎖️');
        checkAuthAndRoute();
      });
    }

    // Citizen Filter Chips
    document.querySelectorAll('.citizen-filter-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        document.querySelectorAll('.citizen-filter-chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        citizenCategoryFilter = chip.dataset.filter;
        renderCitizenDashboard();
      });
    });

    // Search
    const sInput = document.getElementById('citizenSearchInput');
    if (sInput) {
      sInput.addEventListener('input', (e) => {
        searchQuery = e.target.value;
        renderCitizenDashboard();
      });
    }

    // Chatbot Toggle & Messages
    const cTrigger = document.getElementById('chatbotTrigger');
    const cWindow = document.getElementById('chatbotWindow');
    const cClose = document.getElementById('chatbotClose');
    const cSendBtn = document.getElementById('chatbotSendBtn');
    const cInput = document.getElementById('chatbotInput');

    if (cTrigger && cWindow) {
      cTrigger.addEventListener('click', () => cWindow.classList.toggle('active'));
    }
    if (cClose && cWindow) {
      cClose.addEventListener('click', () => cWindow.classList.remove('active'));
    }
    if (cSendBtn) {
      cSendBtn.addEventListener('click', () => handleChatbotMessage());
    }
    if (cInput) {
      cInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          handleChatbotMessage();
        }
      });
    }

    // Gas Sensor Interactive Slider
    const gasSlider = document.getElementById('iotGasSlider');
    const gasVal = document.querySelector('.iotGasValue');
    const gasStatus = document.querySelector('.iotGasStatus');
    const gasLed = document.querySelector('.iotGasLed');

    if (gasSlider && gasVal) {
      gasSlider.addEventListener('input', (e) => {
        const ppm = parseInt(e.target.value, 10);
        gasVal.textContent = `${ppm} PPM`;
        if (ppm > 350) {
          gasStatus.textContent = '🚨 CRITICAL SPOILAGE RISK (High Ammonia/Methane)';
          gasStatus.style.color = '#f43f5e';
          if (gasLed) gasLed.className = 'iot-status-led led-red';
        } else if (ppm > 220) {
          gasStatus.textContent = '⚠️ Elevated Volatile Gases Detected';
          gasStatus.style.color = '#f59e0b';
          if (gasLed) gasLed.className = 'iot-status-led led-amber';
        } else {
          gasStatus.textContent = 'Normal Food Safety Atmosphere';
          gasStatus.style.color = '#94a3b8';
          if (gasLed) gasLed.className = 'iot-status-led led-green';
        }
      });
    }

    // Dismiss Modals when tapping outside on background overlay
    document.querySelectorAll('.modal-overlay').forEach(modal => {
      modal.addEventListener('click', (e) => {
        if (e.target === modal) {
          modal.classList.remove('active');
        }
      });
    });

    // Initialize 4-Tier Jurisdiction Dropdowns across Citizen, Municipal and Food portals
    window.handleGeoStateChange(selectedState);

    // Start Live Real-Time Background Engines (1-sec SLA ticking, IoT telemetry heartbeat & Backend SSE stream)
    startLiveSLATimerEngine();
    startLiveIoTSimulator();
    initRealtimeSSE();
  });

})();


  // =========================================================================
  // 12. SMARTCITY REAL AI & COMPUTER VISION ENGINE (GEMINI 2.5/3.7 FLASH)
  // =========================================================================
  const AiEngine = {
    getApiKey: () => localStorage.getItem('clean_safe_gemini_key') || '',
    setApiKey: (key) => localStorage.setItem('clean_safe_gemini_key', (key || '').trim()),

    // Compute Client-Side 64-Bit Difference Hash (dHash)
    computeImageHash: async function(imageSrc) {
      return new Promise((resolve) => {
        if (!imageSrc) return resolve('');
        const img = new Image();
        img.crossOrigin = 'Anonymous';
        img.onload = () => {
          try {
            const canvas = document.createElement('canvas');
            canvas.width = 9;
            canvas.height = 8;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0, 9, 8);
            const imgData = ctx.getImageData(0, 0, 9, 8).data;
            const gray = [];
            for (let i = 0; i < imgData.length; i += 4) {
              gray.push(Math.floor(0.299 * imgData[i] + 0.587 * imgData[i + 1] + 0.114 * imgData[i + 2]));
            }
            let hash = '';
            for (let r = 0; r < 8; r++) {
              for (let c = 0; c < 8; c++) {
                hash += (gray[r * 9 + c] > gray[r * 9 + c + 1] ? '1' : '0');
              }
            }
            resolve(hash);
          } catch (e) {
            resolve('');
          }
        };
        img.onerror = () => resolve('');
        img.src = imageSrc;
      });
    },

    // Check for duplicate / cropped re-upload
    checkDuplicate: async function(imageData, ward) {
      try {
        const hash = await this.computeImageHash(imageData);
        const res = await fetch('/api/ai/vision/duplicate-check', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Gemini-Key': this.getApiKey()
          },
          body: jsonSafeStringify({
            image: imageData,
            imageHash: hash,
            ward: ward || ''
          })
        });
        if (res.ok) return await res.json();
      } catch (e) {
        console.warn('[AI Duplicate Check Error]', e);
      }
      return { success: false, isDuplicate: false };
    },

    // Multimodal Hazard Auto-Triage & Auto-Fill
    analyzeHazard: async function(imageData) {
      try {
        const res = await fetch('/api/ai/vision/analyze-hazard', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Gemini-Key': this.getApiKey()
          },
          body: jsonSafeStringify({ image: imageData })
        });
        if (res.ok) return await res.json();
      } catch (e) {
        console.warn('[AI Hazard Auto-Triage Error]', e);
      }
      return {
        success: true,
        category: 'garbage',
        categoryName: 'Municipal Solid Waste & Garbage Overflow',
        title: 'High-Volume Solid Waste & Mixed Debris Pile',
        description: 'Heavy accumulation of uncollected residential and organic waste obstructing pedestrian walkway. Threat of vector-borne contamination.',
        department: 'sanitation',
        severity: 'bulk',
        estimatedTonnage: '~2.8 Tons',
        recommendedMachinery: '10-Ton Hydraulic Compactor & Heavy Squad 4',
        suggestedSlaHours: 48,
        confidenceScore: 98.2
      };
    },

    // Visual Gas PPM Spoilage Estimator
    estimateVisualPpm: async function(imageData, sensorPpm, foodType) {
      try {
        const res = await fetch('/api/ai/vision/estimate-ppm', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Gemini-Key': this.getApiKey()
          },
          body: jsonSafeStringify({
            image: imageData,
            sensorPpm: sensorPpm || 185,
            foodType: foodType || 'Mixed Foods'
          })
        });
        if (res.ok) return await res.json();
      } catch (e) {
        console.warn('[AI Gas PPM Estimator Error]', e);
      }
      return null;
    },

    // Conversational Chatbot Stream
    chat: async function(message, department) {
      try {
        const res = await fetch('/api/ai/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Gemini-Key': this.getApiKey()
          },
          body: jsonSafeStringify({
            message: message,
            department: department || 'citizen'
          })
        });
        if (res.ok) {
          const data = await res.json();
          return data.reply;
        }
      } catch (e) {
        console.warn('[AI Chat Error]', e);
      }
      return null;
    }
  };

  // Helper safe JSON stringify
  function jsonSafeStringify(obj) {
    try {
      return JSON.stringify(obj);
    } catch (e) {
      return '{}';
    }
  }

  // -------------------------------------------------------------------------
  // AI AUTO-TRIAGE & DUPLICATE DETECTION TRIGGERS
  // -------------------------------------------------------------------------
  let currentAiDuplicateMatch = null;
  let currentSelectedFoodAiPhoto = null;

  window.triggerAiAutoTriage = async function() {
    const btn = document.getElementById('btnAiAutoTriage');
    const previewImg = document.getElementById('reportPreviewThumbnail');
    let imgSrc = previewImg ? previewImg.src : '';

    if (!imgSrc || imgSrc.length < 5 || imgSrc === window.location.href) {
      // Default to standard garbage sample if no image selected yet
      window.selectSamplePhoto('garbage');
      imgSrc = document.getElementById('reportPreviewThumbnail').src;
    }

    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<span>⚡</span> Analyzing with Gemini AI...';
    }

    try {
      const selectedWard = (document.getElementById('modalReportWard') ? document.getElementById('modalReportWard').value : '');
      
      // 1. Run Duplicate & Crop Detection Check
      const dupRes = await AiEngine.checkDuplicate(imgSrc, selectedWard);
      if (dupRes && dupRes.isDuplicate && dupRes.matchedIssue) {
        currentAiDuplicateMatch = dupRes.matchedIssue;
        renderAiDuplicateModal(dupRes, imgSrc);
        window.openModal('aiDuplicateModal');
        if (btn) {
          btn.disabled = false;
          btn.innerHTML = '<span>🧠</span> Auto-Fill with AI';
        }
        return;
      }

      // 2. Run Multimodal Hazard Auto-Triage
      const aiData = await AiEngine.analyzeHazard(imgSrc);
      if (aiData) {
        // Auto-Fill Form Fields
        const titleInput = document.getElementById('reportTitle');
        const descInput = document.getElementById('reportDesc');
        const deptSelect = document.getElementById('modalReportDept');
        const catSelect = document.getElementById('modalReportCategory');

        if (titleInput) titleInput.value = aiData.title || 'Civic Waste Hazard';
        if (descInput) descInput.value = aiData.description || 'Observed municipal hazard requiring squad dispatch.';
        if (deptSelect && aiData.department) {
          deptSelect.value = aiData.department;
          window.handleModalDeptChange(aiData.department);
        }
        if (catSelect && aiData.category) {
          catSelect.value = aiData.category;
        }

        showToast(`✨ Gemini AI Analyzed: ${aiData.categoryName || 'Hazard'} (${aiData.estimatedTonnage || 'Bulk'})`, 'success', '🧠');
      }
    } catch (e) {
      console.error(e);
      showToast('AI analysis completed with civic domain heuristics.', 'info', '✨');
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = '<span>🧠</span> Auto-Fill with AI';
      }
    }
  };

  function renderAiDuplicateModal(dupRes, userImg) {
    const body = document.getElementById('aiDuplicateModalBody');
    if (!body) return;

    const match = dupRes.matchedIssue;
    const sim = dupRes.similarityScore || 96.4;
    const matchType = dupRes.matchType || 'EXACT_DUPLICATE';

    body.innerHTML = `
      <div style="background: rgba(245, 158, 11, 0.1); border: 1px dashed #f59e0b; border-radius: var(--radius-md); padding: 1rem; margin-bottom: 1.25rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
          <span style="font-weight: 800; color: #facc15; font-size: 0.95rem;">
            🚨 ${matchType === 'CROPPED_OR_EDITED' ? 'Cropped / Modified Image Detected' : 'Identical Duplicate Grievance Found'}
          </span>
          <span class="badge badge-escalated" style="font-size: 0.8rem;">${sim.toFixed(1)}% AI Match</span>
        </div>
        <div class="ai-match-meter">
          <div class="ai-match-meter-fill" style="width: ${sim}%;"></div>
        </div>
        <p style="font-size: 0.8rem; color: #cbd5e1; margin: 4px 0 0;">
          Our AI Computer Vision system identified that this incident has already been reported. To prevent duplicate truck dispatch and keep queues fast, your submission will boost this ticket's priority!
        </p>
      </div>

      <div class="grid-2" style="gap: 1rem; margin-bottom: 1rem;">
        <!-- Left: Uploaded Photo -->
        <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 0.75rem;">
          <div style="font-size: 0.75rem; font-weight: 700; color: #94a3b8; margin-bottom: 4px;">YOUR UPLOADED EVIDENCE:</div>
          <div style="height: 140px; border-radius: 6px; overflow: hidden; border: 1px solid var(--border);">
            <img src="${userImg}" style="width: 100%; height: 100%; object-fit: cover;" alt="Your Upload">
          </div>
          <div style="font-size: 0.78rem; color: #cbd5e1; margin-top: 6px;">📍 Live GPS Geotagged</div>
        </div>

        <!-- Right: Matched Existing Ticket -->
        <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 0.75rem;">
          <div style="font-size: 0.75rem; font-weight: 700; color: #f59e0b; margin-bottom: 4px;">MATCHING EXISTING TICKET: ${match.id}</div>
          <div style="height: 140px; border-radius: 6px; overflow: hidden; border: 1px solid var(--border);">
            <img src="${match.imageBefore}" style="width: 100%; height: 100%; object-fit: cover;" alt="Existing Ticket">
          </div>
          <div style="font-size: 0.78rem; color: white; font-weight: 700; margin-top: 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${match.title}</div>
          <div style="font-size: 0.72rem; color: #94a3b8;">Reported by ${match.reportedBy || 'Citizen'} • Status: <span style="color: #38bdf8;">${match.status.toUpperCase()}</span></div>
        </div>
      </div>
    `;
  }

  window.mergeAndUpvoteParentTicket = function() {
    if (currentAiDuplicateMatch) {
      db.toggleUpvote(currentAiDuplicateMatch.id);
      db.addCivicCredits(10);
      window.closeModal('aiDuplicateModal');
      window.closeModal('reportModal');
      showToast(`🔗 Merged with #${currentAiDuplicateMatch.id}! Priority boosted & +10 Civic Credits awarded.`, 'reward', '🎉');
      renderCitizenDashboard();
    }
  };

  window.proceedAsDistinctIssue = function() {
    window.closeModal('aiDuplicateModal');
    showToast('Proceeding as separate distinct hazard.', 'info', '⚠️');
  };

  // -------------------------------------------------------------------------
  // AI IOT VISUAL GAS PPM & SPOILAGE ESTIMATOR
  // -------------------------------------------------------------------------
  window.handleAiFoodPhotoUpload = function(input) {
    if (input.files && input.files[0]) {
      const reader = new FileReader();
      reader.onload = function(e) {
        currentSelectedFoodAiPhoto = e.target.result;
        const prev = document.getElementById('aiFoodPhotoPreview');
        const holder = document.getElementById('aiFoodPhotoPlaceholder');
        const container = document.getElementById('aiFoodPhotoPreviewContainer');
        if (prev) prev.src = currentSelectedFoodAiPhoto;
        if (holder) holder.style.display = 'none';
        if (container) container.style.display = 'block';
      };
      reader.readAsDataURL(input.files[0]);
    }
  };

  window.testFoodPpmSample = function(type) {
    const samples = {
      'spoiled_meat': {
        url: 'https://images.unsplash.com/photo-1544025162-d76694265947?w=800&auto=format&fit=crop&q=80',
        ppm: 580
      },
      'rancid_oil': {
        url: 'https://images.unsplash.com/photo-1605600659908-0ef719419d41?w=800&auto=format&fit=crop&q=80',
        ppm: 370
      },
      'fresh_curry': {
        url: 'https://images.unsplash.com/photo-1589302168068-964664d93dc0?w=800&auto=format&fit=crop&q=80',
        ppm: 180
      }
    };
    const s = samples[type] || samples.spoiled_meat;
    currentSelectedFoodAiPhoto = s.url;
    const prev = document.getElementById('aiFoodPhotoPreview');
    const holder = document.getElementById('aiFoodPhotoPlaceholder');
    const container = document.getElementById('aiFoodPhotoPreviewContainer');
    const slider = document.getElementById('iotGasSlider');
    const gasVal = document.querySelector('.iotGasValue');

    if (prev) prev.src = currentSelectedFoodAiPhoto;
    if (holder) holder.style.display = 'none';
    if (container) container.style.display = 'block';
    if (slider) slider.value = s.ppm;
    if (gasVal) gasVal.textContent = `${s.ppm} PPM`;

    window.runAiVisualPpmAnalysis();
  };

  window.runAiVisualPpmAnalysis = async function() {
    const btn = document.getElementById('aiRunPpmAnalysisBtn');
    const resultsCard = document.getElementById('aiFoodPpmResultsCard');
    const slider = document.getElementById('iotGasSlider');
    const currentSensorPpm = slider ? parseInt(slider.value, 10) : 185;

    if (!currentSelectedFoodAiPhoto) {
      window.testFoodPpmSample('spoiled_meat');
      return;
    }

    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<span>⚡</span> AI Cross-Verifying Sensor & Vision...';
    }

    try {
      const res = await AiEngine.estimateVisualPpm(currentSelectedFoodAiPhoto, currentSensorPpm, 'Commercial Food Establishment');
      if (res && resultsCard) {
        const isCritical = res.visualEstimatedPpm > 350;
        const isElevated = res.visualEstimatedPpm > 220;

        resultsCard.style.display = 'block';
        resultsCard.innerHTML = `
          <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem;">
            <div>
              <span class="badge ${isCritical ? 'badge-escalated' : isElevated ? 'badge-pending' : 'badge-resolved'}">
                ${isCritical ? '🚨 CRITICAL SPOILAGE HAZARD' : isElevated ? '⚠️ ELEVATED VOLATILE GASES' : '🟢 VERIFIED FRESH ATMOSPHERE'}
              </span>
              <h3 style="color: white; font-size: 1.15rem; margin-top: 0.4rem;">AI Vision & IoT Sensor Corroboration</h3>
            </div>
            <div style="text-align: right;">
              <div style="font-size: 1.4rem; font-weight: 900; color: ${isCritical ? '#f87171' : isElevated ? '#f59e0b' : '#34d399'}; font-family: var(--font-mono);">
                ${res.visualEstimatedPpm} PPM
              </div>
              <div style="font-size: 0.72rem; color: #94a3b8;">AI Visual Predicted PPM</div>
            </div>
          </div>

          <div class="grid-3" style="gap: 0.75rem; margin-bottom: 1rem;">
            <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--border); border-radius: 6px; padding: 0.75rem;">
              <div style="font-size: 0.72rem; color: #94a3b8;">MQ-135 Hardware Telemetry:</div>
              <div style="font-size: 1.1rem; font-weight: 800; color: white;">${res.hardwareSensorPpm} PPM</div>
            </div>
            <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--border); border-radius: 6px; padding: 0.75rem;">
              <div style="font-size: 0.72rem; color: #94a3b8;">Vision-Sensor Correlation:</div>
              <div style="font-size: 1.1rem; font-weight: 800; color: #34d399;">${res.crossValidationConfidence.toFixed(1)}% Match</div>
            </div>
            <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--border); border-radius: 6px; padding: 0.75rem;">
              <div style="font-size: 0.72rem; color: #94a3b8;">Statutory Action:</div>
              <div style="font-size: 1.1rem; font-weight: 800; color: ${isCritical ? '#f87171' : isElevated ? '#f59e0b' : '#34d399'};">${res.fssaiStatutorySection}</div>
            </div>
          </div>

          <div style="background: rgba(255,255,255,0.02); border: 1px dashed var(--border); border-radius: 6px; padding: 0.85rem; font-size: 0.82rem; color: #cbd5e1; margin-bottom: 1rem; line-height: 1.5;">
            <div>🔬 <strong>Microbial Analysis:</strong> ${res.discolorationAnalysis}</div>
            <div>💨 <strong>Detected Gases:</strong> ${res.volatileGasesDetected}</div>
            <div>⚖️ <strong>Recommended Penalty:</strong> <strong style="color: #facc15;">${res.recommendedPenalty}</strong></div>
            <div>🛡️ <strong>Officer Directives:</strong> ${res.officerActionDirectives}</div>
          </div>

          ${isCritical || isElevated ? `
            <button class="btn btn-sm btn-saffron" style="width: 100%; border-color: #ef4444; background: #ef4444;" onclick="window.autoDraftFssaiNotice(${res.visualEstimatedPpm}, '${res.fssaiStatutorySection}')">
              ⚠️ Auto-Draft Official FSSAI Statutory Violation Notice (${res.visualEstimatedPpm} PPM)
            </button>
          ` : `
            <div style="text-align: center; color: #34d399; font-size: 0.82rem; font-weight: 700;">
              ✓ Hygiene Standards Fully Cleared & Validated
            </div>
          `}
        `;
        showToast(`✨ AI Visual Telemetry: ${res.visualEstimatedPpm} PPM (${res.crossValidationConfidence.toFixed(1)}% Match)`, 'success', '🥩');
      }
    } catch (e) {
      console.error(e);
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = '✨ Analyze Spoilage & Verify Gas PPM';
      }
    }
  };

  window.autoDraftFssaiNotice = function(ppm, section) {
    window.openFoodInspectionModal();
    const gasInput = document.getElementById('foodGasReading');
    const remarksInput = document.getElementById('foodInspectionRemarks');
    const fineInput = document.getElementById('foodFineImposed');

    if (gasInput) gasInput.value = `${ppm} PPM (AI Cross-Verified)`;
    if (remarksInput) remarksInput.value = `AI Vision & MQ-135 Corroborated Spoilage (${ppm} PPM). Statutory violation under ${section}. Contaminated stocks confiscated.`;
    if (fineInput) fineInput.value = ppm > 350 ? '5000' : '2000';
    showToast('FSSAI Statutory Violation Notice auto-drafted from AI Telemetry!', 'info', '⚖️');
  };

  // -------------------------------------------------------------------------
  // AI SETTINGS & KEY MANAGEMENT
  // -------------------------------------------------------------------------
  window.openAiSettingsModal = function() {
    const input = document.getElementById('customGeminiApiKeyInput');
    if (input) input.value = AiEngine.getApiKey();
    window.openModal('aiSettingsModal');
  };

  window.toggleApiKeyVisibility = function() {
    const input = document.getElementById('customGeminiApiKeyInput');
    if (input) input.type = input.type === 'password' ? 'text' : 'password';
  };

  window.saveGeminiApiKeySetting = function() {
    const input = document.getElementById('customGeminiApiKeyInput');
    const key = input ? input.value.trim() : '';
    AiEngine.setApiKey(key);
    window.closeModal('aiSettingsModal');
    showToast(key ? '✅ Custom Google Gemini API Key Saved!' : 'Operating on SmartCity Built-In Civic AI Engine.', 'success', '✨');
  };

  window.testGeminiApiConnection = async function() {
    const btn = document.getElementById('testApiKeyBtn');
    const input = document.getElementById('customGeminiApiKeyInput');
    const key = input ? input.value.trim() : AiEngine.getApiKey();

    if (btn) {
      btn.disabled = true;
      btn.textContent = 'Testing...';
    }

    try {
      const res = await fetch('/api/ai/test-key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: jsonSafeStringify({ apiKey: key })
      });
      const data = await res.json();
      if (data.isRealAiActive) {
        showToast('🟢 Google Gemini 2.5 Flash Connected Successfully!', 'success', '🚀');
        const badge = document.getElementById('aiLiveStatusBadge');
        if (badge) {
          badge.textContent = '🟢 Real Gemini AI Active';
          badge.style.background = 'rgba(16, 185, 129, 0.2)';
        }
      } else {
        showToast(data.message || 'Civic Simulated AI Engine is Active.', 'info', '🔵');
      }
    } catch (e) {
      showToast('SmartCity Civic AI Engine is active.', 'info', '🔵');
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.textContent = '⚡ Test Connection';
      }
    }
  };
