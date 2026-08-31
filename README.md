# 🇮🇳 Clean & Safe India App
### A Smart Mobile-Based System for Cleaning, Hygiene, and Safety Issue Reporting & Monitoring
**Innovated by Team Civic Tech Innovators (Aditya University, Surampalem)**

---

## 🌟 Project Overview
**Clean & Safe India** is a modern, full-stack civic governance and public health monitoring platform built with **HTML5, CSS3, Modern JavaScript (ES Modules)**, and **Firebase**.

It addresses urban sanitation challenges and food safety through real-time citizen reporting, automated AI verification, a self-sustaining incentive-penalty model (₹30 reward / ₹150–₹500 fine), 3-in-1 smart CCTV & IoT hardware telemetry, and an interactive municipal command center.

---

## 🚀 Key Modules & Capabilities

1. **Citizen Reporting Portal**:
   - Multi-category reporting: Urban Garbage Accumulation, Food Hygiene Violation, Food Spoilage & Odor, Roadside Littering.
   - Geo-tagged camera capture with live GPS coordinate extraction and timestamp stamping.
   - Interactive OpenStreetMap (Leaflet.js) location pin picker.
   - Severity classification (*Low*, *Medium*, *Bulk*) with automated vehicle dispatch recommendation.

2. **Municipal Command Centre & Hierarchical Routing**:
   - Role-based routing: *Citizen Reporter*, *Welfare Secretary (Ward-Level)*, *Sanitation Inspector*, and *Food Safety Officer*.
   - **48-Hour SLA Countdown**: Strict SLA monitoring with automatic visual escalation flags.
   - **Dynamic Resource Allocation Matrix**:
     - *Low Severity* $\rightarrow$ Sanitation Worker with Pushcart
     - *Medium Severity* $\rightarrow$ Garbage Collection Vehicle (`#AP-05-TX`)
     - *Bulk Severity* $\rightarrow$ Tractor & Heavy Compactor Machine
   - **Before-and-After Verification Slider**: Interactive split-screen comparison verifying that sites are restored prior to complaint closure.

3. **Incentive & Penalty Economy**:
   - **Citizen Reward Wallet**: ₹30 monetary reward credited to citizens upon verified report resolution.
   - **Violator Fines**: ₹150 to ₹500+ penalty notices issued to illegal dumpers and food safety violators.
   - Self-sustaining circular model where violator fines fund citizen surveillance rewards.

4. **3-in-1 Smart CCTV & IoT Hardware Telemetry**:
   - **Case 1: Vehicle Garbage Dumping** with Automatic Number Plate Recognition (ANPR overlay e.g., `MH12 AB 1234`).
   - **Case 2: Person Littering** with 3-stage temporal action detection (*Before / During / After*).
   - **Case 3: Food Hygiene Monitoring** with AI bounding boxes on dirty prep surfaces and waste near food.
   - **ESP32 IoT Sensor Telemetry**: Live interactive telemetry for *MQ-135 Gas Sensor (Ammonia/CO₂/Spoilage PPM)*, *HC-SR04 Ultrasonic Sensor (Bin Fill %)*, *HX711 Load Cell (Waste Weight kg)*, and *NEO-6M GPS*.

5. **Food Hygiene & Digital Vendor Certification**:
   - Certified hygienic vendors directory with grades (*A+, A, C*).
   - Verifiable Digital Hygiene Certificate generator with printable layout and QR code verification badge.
   - Progressive penalty tracker (*1st Violation $\rightarrow$ Fine*, *Repeat $\rightarrow$ Heavy Fine*, *Continuous $\rightarrow$ License Cancellation*).

6. **SmartCity AI Assistant & Chatbot**:
   - 24/7 AI chatbot answering civic FAQs, guiding submissions, and tracking live complaint status by Ticket ID (e.g. `ISS-2026-00123`).

---

## 💻 How to Run Locally

Since the application is built using standard Vanilla JavaScript ES Modules, you can run it instantly using any static server (like Python):

```powershell
# 1. Open terminal and navigate to the project folder
cd C:\Users\Admin\.gemini\antigravity\scratch\clean-and-safe-india

# 2. Start a local server
python -m http.server 8000
```

Open your browser and navigate to:
👉 `http://localhost:8000`

---

## 🔧 Configuring Live Firebase

The application includes a built-in mock database that works immediately out of the box. To connect your live Firebase project:

1. Open `js/config.js`
2. Replace the placeholder values in `FIREBASE_CONFIG` with your Firebase project credentials from the Firebase Console.
3. Deploy security rules:
   ```bash
   firebase deploy --only firestore:rules,storage
   ```

---

## 👥 Team Civic Tech Innovators (Aditya University)

- **K.H. Sameer Reddy**: Research & Operations Lead *(Data analysis on KMC/BMC waste scales & reward/penalty model)*
- **K. Mukundha**: Lead Developer & System Architect *(App core logic and technical framework)*
- **N. Ramya Spoorthi**: Communications & Strategic Presentation *(Stakeholder outreach & vision pitch)*

### Mentors:
- **Dr. Mahesh Babu Kota** (M.Tech, Ph.D. Assistant Professor & Coordinator R&C)
- **Mr. Charan Sanjeev Tadimalla** (EDC Coordinator - Entrepreneurship Development Cell)
