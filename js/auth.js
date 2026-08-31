/* ==========================================================================
   Smart Civic Connect - Enterprise Authentication & Role-Based Access Control
   3 Distinct Login Portals: Citizen, Municipal & Electricity, Food Safety
   ========================================================================== */

const STORAGE_SESSION_KEY = 'smart_civic_auth_session';

// Registered Official System Accounts
export const SYSTEM_ACCOUNTS = {
  citizen: {
    department: 'citizen',
    deptTitle: 'Citizen Portal',
    email: 'citizen@civictech.in',
    password: 'password123',
    name: 'KRISH',
    ward: 'Ward 12 - Central Circle',
    role: 'citizen',
    roleTitle: 'Verified Citizen Reporter',
    officialId: 'CIT-IND-2026-8941',
    avatar: 'KR',
    walletBalance: 90,
    rewardPoints: 150
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
    walletBalance: 0,
    rewardPoints: 0
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
    walletBalance: 0,
    rewardPoints: 0
  }
};

class AuthManager {
  constructor() {
    this.session = this.loadSession();
    this.listeners = [];
  }

  loadSession() {
    try {
      const stored = localStorage.getItem(STORAGE_SESSION_KEY);
      if (stored) {
        return JSON.parse(stored);
      }
    } catch (e) {
      console.warn("Auth session parse error:", e);
    }
    return null; // Not logged in initially
  }

  saveSession(sessionData) {
    this.session = sessionData;
    try {
      if (sessionData) {
        localStorage.setItem(STORAGE_SESSION_KEY, JSON.stringify(sessionData));
      } else {
        localStorage.removeItem(STORAGE_SESSION_KEY);
      }
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

  // Attempt Login
  login(department, email, password) {
    const targetAccount = SYSTEM_ACCOUNTS[department];
    if (!targetAccount) {
      throw new Error("Invalid department selected.");
    }

    const cleanEmail = email.trim().toLowerCase();
    const cleanPass = password.trim();

    // Check credentials
    if (cleanEmail === targetAccount.email.toLowerCase() && cleanPass === targetAccount.password) {
      const sessionData = {
        token: `CIVIC_JWT_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        department: department,
        user: { ...targetAccount },
        loginTime: new Date().toISOString()
      };
      this.saveSession(sessionData);
      return sessionData;
    }

    // Allow user to register/login with custom credentials if in citizen mode
    if (department === 'citizen' && cleanEmail.length > 3 && cleanPass.length >= 6) {
      const citizenUser = {
        ...SYSTEM_ACCOUNTS.citizen,
        email: cleanEmail,
        name: cleanEmail.split('@')[0].toUpperCase(),
        officialId: `CIT-IND-${Math.floor(1000 + Math.random() * 9000)}`
      };
      const sessionData = {
        token: `CIVIC_JWT_${Date.now()}`,
        department: 'citizen',
        user: citizenUser,
        loginTime: new Date().toISOString()
      };
      this.saveSession(sessionData);
      return sessionData;
    }

    throw new Error("Invalid email or password for this department portal.");
  }

  // Logout
  logout() {
    this.saveSession(null);
  }

  subscribe(callback) {
    this.listeners.push(callback);
    callback(this.session);
  }

  notify() {
    this.listeners.forEach(cb => cb(this.session));
  }

  // Add reward to Citizen wallet
  addReward(amount, points = 50) {
    if (this.session && this.session.user && this.session.department === 'citizen') {
      this.session.user.walletBalance = (this.session.user.walletBalance || 0) + amount;
      this.session.user.rewardPoints = (this.session.user.rewardPoints || 0) + points;
      this.saveSession(this.session);
    }
  }
}

export const auth = new AuthManager();
