/* ==========================================================================
   Smart Civic Connect (Clean & Safe India) - Config & Comprehensive Data Store
   3 Core Departments: Sanitation & Waste, Food Safety, Smart Electricity
   ========================================================================== */

export const FIREBASE_CONFIG = {
  apiKey: "YOUR_FIREBASE_API_KEY",
  authDomain: "clean-safe-india.firebaseapp.com",
  projectId: "clean-safe-india",
  storageBucket: "clean-safe-india.appspot.com",
  messagingSenderId: "1234567890",
  appId: "1:1234567890:web:abcdef123456"
};

export const INITIAL_DATA = {
  // Current user state
  currentUser: {
    id: "user-101",
    name: "KRISH",
    email: "krish@civictech.in",
    role: "citizen", // "citizen" | "government_admin" | "field_worker" | "food_officer"
    ward: "Ward 12 - Central Circle",
    walletBalance: 90, // Earned from verified reports
    rewardPoints: 150, // 3 x 50 points
    avatar: "KR",
    roleTitle: "Active Citizen Reporter ⭐"
  },

  // Power Outage & Grid Status for Smart Electricity Department
  powerGridStatus: {
    gridName: "Surampalem Central Substation (33/11 KV)",
    overallStatus: "OPERATIONAL", // OPERATIONAL | PARTIAL_OUTAGE | CRITICAL
    activeOutagesCount: 2,
    substationsOnline: "14 / 16 Sub-Feeders Active",
    lastUpdated: "Just now",
    activeOutages: [
      {
        id: "OUTAGE-PWR-101",
        feeder: "Feeder 4 - Gandhi Nagar & Market Road",
        ward: "Ward 12 & Ward 14",
        status: "UNSCHEDULED_OUTAGE",
        reason: "Transformer Thermal Overload & Damaged Jumper Wire",
        affectedConsumers: 1420,
        startTime: "11:45 AM Today",
        estimatedRestoration: "02:30 PM Today (Est. 1h 15m remaining)",
        assignedLineman: "Suresh Babu (Senior Lineman #LN-402)",
        repairStage: "Lineman on site replacing 11KV HT fuse & jumper"
      },
      {
        id: "OUTAGE-PWR-102",
        feeder: "Feeder 2 - College Road Industrial Zone",
        ward: "Ward 8",
        status: "SCHEDULED_MAINTENANCE",
        reason: "Tree Branch Trimming near 33KV High Tension Line",
        affectedConsumers: 650,
        startTime: "09:00 AM Today",
        estimatedRestoration: "01:00 PM Today",
        assignedLineman: "K. Venkatesh (Field Crew Lead)",
        repairStage: "Maintenance 85% completed"
      }
    ]
  },

  // Issues & Complaints Queue across the 3 Public Service Departments
  issues: [
    // -------------------------------------------------------------
    // DEPARTMENT 1: SANITATION & WASTE MANAGEMENT
    // -------------------------------------------------------------
    {
      id: "ISS-2026-00123",
      department: "sanitation",
      deptName: "Sanitation & Waste Management",
      deptIcon: "🏢",
      title: "Garbage Overflow at Main Market Bus Stand",
      category: "garbage",
      categoryName: "Urban Garbage Overflow",
      categoryIcon: "🗑️",
      severity: "medium",
      severityLabel: "Medium (Truck Required)",
      recommendedResource: "Garbage Collection Vehicle",
      resourceIcon: "🚛",
      description: "Severe garbage accumulation behind the bus shelter causing foul smell and health hazard. Waste overflowing for 3 days.",
      location: "Sector 14, Main Market Road, Ward 12",
      lat: 17.0005,
      lng: 81.8040,
      reportedBy: "Sameer Reddy",
      userId: "user-101",
      timestamp: new Date(Date.now() - 18 * 3600 * 1000).toISOString(),
      slaHoursLeft: 30,
      status: "in_progress",
      assignedWorker: "Ramesh Kumar (Sanitation Crew Lead)",
      imageBefore: "https://images.unsplash.com/photo-1605600659908-0ef719419d41?w=800&auto=format&fit=crop&q=80",
      imageAfter: null,
      upvotes: 24,
      upvotedBy: ["user-101"],
      rewardIssued: false,
      rewardPoints: 50,
      rewardAmount: 30,
      fineAmount: 200,
      fineIssued: false,
      comments: [
        { author: "Ramesh Kumar (Worker)", text: "Sanitation crew assigned with Vehicle #AP-05-TX-9901. En route.", time: "4 hours ago" }
      ]
    },
    {
      id: "ISS-2026-00125",
      department: "sanitation",
      deptName: "Sanitation & Waste Management",
      deptIcon: "🏢",
      title: "Deep Pothole on Highway Junction Causing Accidents",
      category: "pothole",
      categoryName: "Damaged Road / Pothole",
      categoryIcon: "🕳️",
      severity: "bulk",
      severityLabel: "Bulk (Asphalt Compactor Required)",
      recommendedResource: "Road Repair & Bitumen Compactor Machine",
      resourceIcon: "🚜",
      description: "Massive 2-foot wide pothole on fast lane. Two two-wheelers skidded yesterday. Immediate tarring needed.",
      location: "Bypass Junction near NH-16, Ward 8",
      lat: 16.9950,
      lng: 81.7980,
      reportedBy: "Ramya Spoorthi",
      userId: "user-103",
      timestamp: new Date(Date.now() - 52 * 3600 * 1000).toISOString(), // >48h escalated!
      slaHoursLeft: -4,
      status: "escalated",
      assignedWorker: "Municipal Roads & Public Works Team",
      imageBefore: "https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?w=800&auto=format&fit=crop&q=80",
      imageAfter: null,
      upvotes: 56,
      upvotedBy: ["user-101"],
      rewardIssued: false,
      rewardPoints: 50,
      rewardAmount: 30,
      fineAmount: 0,
      fineIssued: false,
      comments: [
        { author: "System SLA Watchdog", text: "🚨 Complaint SLA breached (>48h). Auto-escalated to Zonal Roads Commissioner.", time: "4 hours ago" }
      ]
    },
    {
      id: "ISS-2026-00120",
      department: "sanitation",
      deptName: "Sanitation & Waste Management",
      deptIcon: "🏢",
      title: "Roadside Littering Cleared & Swept",
      category: "garbage",
      categoryName: "Roadside Littering",
      categoryIcon: "🧹",
      severity: "low",
      severityLabel: "Low (Pushcart Worker)",
      recommendedResource: "Sanitation Worker with Pushcart",
      resourceIcon: "🛒",
      description: "Litter scattered near primary school gate.",
      location: "Govt School Road, Ward 12",
      lat: 16.9985,
      lng: 81.8015,
      reportedBy: "Sameer Reddy",
      userId: "user-101",
      timestamp: new Date(Date.now() - 72 * 3600 * 1000).toISOString(),
      slaHoursLeft: 0,
      status: "resolved",
      assignedWorker: "Appa Rao (Ward Pushcart Staff)",
      imageBefore: "https://images.unsplash.com/photo-1530587191325-3db32d826c18?w=800&auto=format&fit=crop&q=80",
      imageAfter: "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=800&auto=format&fit=crop&q=80",
      upvotes: 18,
      upvotedBy: ["user-101"],
      rewardIssued: true,
      rewardPoints: 50,
      rewardAmount: 30,
      fineAmount: 0,
      fineIssued: false,
      resolutionNotes: "Area swept, disinfected with bleaching powder, and dustbins placed by Ward 12 team.",
      resolvedAt: new Date(Date.now() - 24 * 3600 * 1000).toISOString(),
      comments: [
        { author: "Appa Rao (Worker)", text: "Cleaned and post-cleaning image verified.", time: "Yesterday" }
      ]
    },

    // -------------------------------------------------------------
    // DEPARTMENT 2: FOOD SAFETY DEPARTMENT
    // -------------------------------------------------------------
    {
      id: "ISS-2026-00124",
      department: "food_safety",
      deptName: "Food Safety Department",
      deptIcon: "🍲",
      title: "Unhygienic Food Stall & Open Drain Contamination",
      category: "food_hygiene",
      categoryName: "Food Hygiene Violation",
      categoryIcon: "🍲",
      severity: "bulk",
      severityLabel: "Critical / High Risk",
      recommendedResource: "Food Safety Inspection Officer",
      resourceIcon: "🔍",
      description: "Street food stall operating with uncovered food right next to an open sewage drain. Foul odor and flies detected.",
      location: "Railway Station West Gate, Food Street, Ward 12",
      lat: 17.0028,
      lng: 81.8062,
      reportedBy: "Mukundha K.",
      userId: "user-102",
      timestamp: new Date(Date.now() - 44 * 3600 * 1000).toISOString(),
      slaHoursLeft: 4,
      status: "pending",
      assignedWorker: "Dr. Lakshmi Prasad (Food Safety Officer)",
      imageBefore: "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800&auto=format&fit=crop&q=80",
      imageAfter: null,
      upvotes: 42,
      upvotedBy: [],
      rewardIssued: false,
      rewardPoints: 50,
      rewardAmount: 30,
      fineAmount: 500,
      fineIssued: true,
      comments: [
        { author: "Dr. Lakshmi Prasad (FSO)", text: "Inspection notice dispatched to vendor under Food Safety Regulation Sec 32.", time: "1 hour ago" }
      ]
    },

    // -------------------------------------------------------------
    // DEPARTMENT 3: SMART ELECTRICITY DEPARTMENT
    // -------------------------------------------------------------
    {
      id: "ISS-2026-00126",
      department: "electricity",
      deptName: "Smart Electricity Department",
      deptIcon: "⚡",
      title: "Damaged Electric Pole & Sparking Transformer",
      category: "electricity_hazard",
      categoryName: "Damaged Transformer & Sparking",
      categoryIcon: "⚡",
      severity: "bulk",
      severityLabel: "Critical Hazard (Immediate Disconnect Required)",
      recommendedResource: "Emergency Lineman Squad & Boom Lift Truck",
      resourceIcon: "⚡",
      description: "Electric distribution pole tilted after heavy rain. Heavy sparking seen at 11KV transformer bushings. High risk of shock/fire.",
      location: "Near Shanti Theater Cross, Ward 12",
      lat: 17.0018,
      lng: 81.8020,
      reportedBy: "Sameer Reddy",
      userId: "user-101",
      timestamp: new Date(Date.now() - 6 * 3600 * 1000).toISOString(),
      slaHoursLeft: 42,
      status: "in_progress",
      assignedWorker: "Suresh Babu (Lineman #LN-402)",
      imageBefore: "https://images.unsplash.com/photo-1544724569-5f546fd6f2b5?w=800&auto=format&fit=crop&q=80",
      imageAfter: null,
      upvotes: 38,
      upvotedBy: ["user-101"],
      rewardIssued: false,
      rewardPoints: 50,
      rewardAmount: 30,
      fineAmount: 0,
      fineIssued: false,
      comments: [
        { author: "Suresh Babu (Lineman)", text: "Substation isolated the feeder. Lineman team on spot replacing burnt insulator jumper.", time: "30 mins ago" }
      ]
    },
    {
      id: "ISS-2026-00127",
      department: "electricity",
      deptName: "Smart Electricity Department",
      deptIcon: "⚡",
      title: "Broken Street Light & Dark Danger Zone",
      category: "street_light",
      categoryName: "Street Light Failure",
      categoryIcon: "💡",
      severity: "low",
      severityLabel: "Low (Lineman Inspection)",
      recommendedResource: "Street Light Maintenance Lineman",
      resourceIcon: "💡",
      description: "3 consecutive LED street lights not working for past 4 days. Total darkness creating safety concerns for women & pedestrians.",
      location: "Bank Colony 3rd Lane, Ward 14",
      lat: 17.0040,
      lng: 81.8080,
      reportedBy: "K. Mukundha",
      userId: "user-102",
      timestamp: new Date(Date.now() - 22 * 3600 * 1000).toISOString(),
      slaHoursLeft: 26,
      status: "pending",
      assignedWorker: "Venkatesh (Lineman #LN-108)",
      imageBefore: "https://images.unsplash.com/photo-1517457373958-b7bdd4587205?w=800&auto=format&fit=crop&q=80",
      imageAfter: null,
      upvotes: 15,
      upvotedBy: [],
      rewardIssued: false,
      rewardPoints: 50,
      rewardAmount: 30,
      fineAmount: 0,
      fineIssued: false,
      comments: [
        { author: "System AI", text: "Report assigned to Electricity Feeder #4 Maintenance squad.", time: "12 hours ago" }
      ]
    }
  ],

  // 3-in-1 Smart CCTV AI Detections
  cctvIncidents: [
    {
      id: "CCTV-ANPR-901",
      type: "vehicle_dumping",
      title: "Vehicle Illegal Garbage Dumping Detected (ANPR)",
      camera: "CCTV Cam #04 - Sector 15 Main Road",
      timestamp: "Today, 10:24 AM",
      vehiclePlate: "MH12 AB 1234",
      vehicleType: "Light Commercial Truck (Tata Ace)",
      confidence: "98.4%",
      evidenceImg: "https://images.unsplash.com/photo-1580273916550-e323be2ae537?w=800&auto=format&fit=crop&q=80",
      fineIssued: 500,
      status: "e-Challan Dispatched to Vehicle Owner"
    },
    {
      id: "CCTV-LITTER-902",
      type: "person_littering",
      title: "Individual Littering Action (3-Frame Temporal AI)",
      camera: "CCTV Cam #02 - Market Pedestrian Walkway",
      timestamp: "Today, 11:15 AM",
      confidence: "94.6%",
      actionSequence: ["Frame 1: Object Held", "Frame 2: Throwing Motion Detected", "Frame 3: Waste on Ground"],
      fineIssued: 150,
      status: "Citizen Warning Alert Sent"
    },
    {
      id: "CCTV-HYGIENE-903",
      type: "food_hygiene",
      title: "Food Stall Unhygienic Prep & Waste Proximity",
      camera: "Smart FoodGuard AI Cam #01 - Food Court Stall 7",
      timestamp: "Today, 12:47 PM",
      cleanlinessScore: "42% (POOR)",
      detectedViolations: ["Open Garbage Bin < 1m from Food Prep", "Uncovered Food Containers"],
      status: "Notice Issued to Stall Owner"
    }
  ],

  // Certified Food Vendors
  certifiedVendors: [
    {
      id: "VEND-CERT-01",
      name: "Annapurna Pure Veg Kitchen",
      owner: "S. Venkatesh",
      location: "Main Road, Ward 12",
      hygieneGrade: "A+",
      score: "96/100",
      status: "Certified Hygienic",
      validTill: "31 Dec 2026",
      inspectedBy: "Dr. Lakshmi Prasad (FSO)",
      violationsCount: 0
    },
    {
      id: "VEND-CERT-02",
      name: "Green Leaf Tiffins & Cafe",
      owner: "K. Narayana",
      location: "College Road, Ward 8",
      hygieneGrade: "A",
      score: "88/100",
      status: "Certified Hygienic",
      validTill: "15 Nov 2026",
      inspectedBy: "Dr. Lakshmi Prasad (FSO)",
      violationsCount: 0
    },
    {
      id: "VEND-CERT-03",
      name: "Highway Spice Corner",
      owner: "M. Rajesh",
      location: "Bypass Junction, Ward 15",
      hygieneGrade: "C (Probation)",
      score: "52/100",
      status: "Under Notice",
      validTill: "Pending Re-inspection",
      inspectedBy: "Dr. Lakshmi Prasad (FSO)",
      violationsCount: 1,
      fineAmount: 500
    }
  ],

  // Rewards Ledger
  rewardsHistory: [
    { id: "TX-901", type: "reward", title: "Valid Report Verified (#ISS-2026-00120)", amount: 30, points: 50, date: "24 Aug 2026", status: "Credited to Wallet" },
    { id: "TX-902", type: "reward", title: "Valid Report Verified (#ISS-2026-00115)", amount: 30, points: 50, date: "20 Aug 2026", status: "Credited to Wallet" },
    { id: "TX-903", type: "reward", title: "Valid Report Verified (#ISS-2026-00108)", amount: 30, points: 50, date: "15 Aug 2026", status: "Credited to Wallet" }
  ],

  // IoT Hardware Telemetry Stream
  iotTelemetry: {
    deviceId: "CLEAN-SAFE-IOT-ESP32-01",
    status: "ONLINE",
    battery: "92% (3.7V 2000mAh)",
    gps: { lat: 17.0012, lng: 81.8035, satellites: 9 },
    mq135GasSensor: {
      valuePpm: 185,
      status: "NORMAL",
      spoilageRisk: "Low (Safe Environment)"
    },
    ultrasonicBinLevel: {
      fillPercentage: 68,
      distanceCm: 32,
      alert: "Approaching Capacity (>65%)"
    },
    loadCellWeight: {
      weightKg: 14.8,
      maxCapacityKg: 25.0
    }
  },

  // Technical Support Tickets
  supportTickets: [
    { id: "TECH-2026-01", issueType: "App Lagging on Camera Capture", desc: "Camera takes 2 seconds to focus on mobile view.", status: "Resolved", date: "Yesterday" }
  ]
};
