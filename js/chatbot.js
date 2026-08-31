/* ==========================================================================
   Clean & Safe India App - SmartCity AI Assistant & Customer Support Chatbot
   Real-time ticket tracking, FAQs, reporting guidance, and troubleshooting
   ========================================================================== */

import { db } from './db.js';

class SmartCityChatbot {
  constructor() {
    this.messages = [
      {
        sender: 'bot',
        text: "👋 Namaste! I am your **SmartCity Assistant**. How can I help you today? You can ask me how to report an issue, inquire about the ₹30 citizen rewards, check food safety rules, or track a complaint by its Ticket ID (e.g. `ISS-2026-00123`)."
      }
    ];
  }

  processUserMessage(rawText) {
    const text = rawText.trim();
    if (!text) return null;

    // Add user message
    this.messages.push({ sender: 'user', text });

    // Ticket ID detection regex (e.g. ISS-2026-00123 or ISS-123)
    const ticketMatch = text.match(/ISS[-_]?[0-9]+/i) || text.match(/ISS-2026-\d+/i);
    let botReply = "";

    if (ticketMatch) {
      const queryId = ticketMatch[0].toUpperCase();
      const allIssues = db.getAllIssues();
      const found = allIssues.find(i => i.id.toUpperCase().includes(queryId) || queryId.includes(i.id.toUpperCase()));

      if (found) {
        const slaStatus = found.slaHoursLeft > 0 
          ? `⏳ SLA Window: ${found.slaHoursLeft} hours remaining before escalation`
          : `🚨 SLA Breached: Escalated to Zonal Authority`;

        botReply = `🔎 **Complaint Status for #${found.id}**:\n` +
          `• **Title**: ${found.title}\n` +
          `• **Status**: ${found.status.toUpperCase().replace('_', ' ')}\n` +
          `• **Location**: ${found.location}\n` +
          `• **Assigned Officer**: ${found.assignedOfficer}\n` +
          `• **Allocated Resource**: ${found.recommendedResource}\n` +
          `• **SLA**: ${slaStatus}\n` +
          (found.status === 'resolved' ? `• **Resolution Note**: ${found.resolutionNotes || 'Cleaned & Verified'}` : '');
      } else {
        botReply = `🔍 I searched for ticket **${queryId}**, but couldn't find a matching record. Please check the ticket number (e.g. \`ISS-2026-00123\`) or view your submitted reports in the Feed tab.`;
      }
    } else {
      const lower = text.toLowerCase();
      if (lower.includes("reward") || lower.includes("earn") || lower.includes("money") || lower.includes("wallet") || lower.includes("30")) {
        botReply = "💰 **Incentive-Penalty Model**:\nCitizens receive a **₹30 monetary reward** in their in-app wallet for every valid civic report once it is verified and resolved by field officers! These rewards are funded directly from fines (₹150–₹500) collected from violators.";
      } else if (lower.includes("report") || lower.includes("how to") || lower.includes("submit") || lower.includes("garbage") || lower.includes("pothole")) {
        botReply = "📝 **How to Report an Issue**:\n1. Click the **'+ Report Issue'** button.\n2. Choose a category (*Garbage, Food Hygiene, Spoilage, Littering*).\n3. Take or upload a photo.\n4. Click **'Auto-Detect GPS'** or drag the map pin to pinpoint the exact location.\n5. Click Submit! Our AI and Ward Officers will process it within the 48-hour SLA.";
      } else if (lower.includes("food") || lower.includes("hygiene") || lower.includes("stall") || lower.includes("restaurant") || lower.includes("certificate")) {
        botReply = "🍲 **Food Hygiene & Certification System**:\nOur platform monitors food stall cleanliness, waste proximity, and food spoilage gases. Vendors maintaining Grade A/A+ receive a **Digital Hygiene Certificate** with QR verification. Violators face progressive fines and possible license cancellation.";
      } else if (lower.includes("sla") || lower.includes("48") || lower.includes("escalat") || lower.includes("time")) {
        botReply = "⏱️ **48-Hour SLA Guarantee**:\nEvery complaint has a strict 48-hour resolution window. If field sanitation teams do not resolve the issue within 48 hours, the ticket automatically escalates to senior municipal authorities and the Zonal Commissioner.";
      } else if (lower.includes("cctv") || lower.includes("iot") || lower.includes("anpr") || lower.includes("sensor")) {
        botReply = "📡 **3-in-1 Smart CCTV & IoT System**:\nOur smart CCTV cameras feature **ANPR** (Automatic Number Plate Recognition) to catch vehicle dumping, 3-frame temporal analysis for human littering, and ESP32 gas sensors (MQ-135) to detect food spoilage gases like ammonia.";
      } else if (lower.includes("contact") || lower.includes("team") || lower.includes("creator") || lower.includes("author")) {
        botReply = "👥 **Team Civic Tech Innovators** (Aditya University):\n• K.H. Sameer Reddy (Research & Operations Lead)\n• K. Mukundha (Lead Developer & System Architect)\n• N. Ramya Spoorthi (Communications & Strategic Presentation)\n• Mentors: Dr. Mahesh Babu Kota & Mr. Charan Sanjeev Tadimalla";
      } else {
        botReply = "I can assist you with:\n• 📍 **Reporting** garbage or food hygiene issues\n• 🔍 **Tracking** your Ticket ID (e.g. `ISS-2026-00123`)\n• 💰 **Understanding** the ₹30 citizen rewards\n• ⏱️ **48-hour SLA** escalation policies\n• 📡 **3-in-1 Smart CCTV & IoT** monitoring features";
      }
    }

    this.messages.push({ sender: 'bot', text: botReply });
    return botReply;
  }

  getMessages() {
    return this.messages;
  }
}

export const chatbot = new SmartCityChatbot();
