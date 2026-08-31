/* ==========================================================================
   Clean & Safe India App - 3-in-1 CCTV & IoT Hardware Telemetry Simulator
   ESP32-CAM, MQ-135 Gas Sensor, HC-SR04 Ultrasonic, HX711 Load Cell, ANPR
   ========================================================================== */

import { INITIAL_DATA } from './config.js';

class IoTTelemetrySimulator {
  constructor() {
    this.telemetry = { ...INITIAL_DATA.iotTelemetry };
    this.timer = null;
    this.subscribers = [];
  }

  start() {
    if (this.timer) return;
    this.timer = setInterval(() => {
      this.tick();
    }, 3000);
  }

  stop() {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
  }

  subscribe(callback) {
    this.subscribers.push(callback);
    callback(this.telemetry);
  }

  notify() {
    this.subscribers.forEach(cb => cb(this.telemetry));
  }

  tick() {
    // Slight realistic sensor telemetry fluctuation
    const gasDelta = Math.floor(Math.random() * 15) - 7;
    const currentGas = Math.max(120, Math.min(650, this.telemetry.mq135GasSensor.valuePpm + gasDelta));
    
    let gasStatus = "NORMAL";
    let spoilageRisk = "Low";
    if (currentGas > 400) {
      gasStatus = "CRITICAL_SPOILAGE";
      spoilageRisk = "High (Dangerous Gases Detected)";
    } else if (currentGas > 280) {
      gasStatus = "ELEVATED";
      spoilageRisk = "Moderate Spoilage";
    }

    this.telemetry.mq135GasSensor = {
      valuePpm: currentGas,
      status: gasStatus,
      spoilageRisk: spoilageRisk
    };

    // Ultrasonic Bin level
    const fillDelta = (Math.random() > 0.6) ? 1 : 0;
    const newFill = Math.min(95, this.telemetry.ultrasonicBinLevel.fillPercentage + fillDelta);
    this.telemetry.ultrasonicBinLevel = {
      fillPercentage: newFill,
      distanceCm: Math.round(100 - newFill),
      alert: newFill > 80 ? "🚨 Critical Overflow (>80%)" : newFill > 60 ? "Approaching Capacity" : "Normal Level"
    };

    // Load cell weight
    const newWeight = +(this.telemetry.loadCellWeight.weightKg + (fillDelta * 0.2)).toFixed(1);
    this.telemetry.loadCellWeight.weightKg = Math.min(24.5, newWeight);

    this.notify();
  }

  // Interactive slider overrides
  setGasPpm(ppm) {
    let gasStatus = "NORMAL";
    let spoilageRisk = "Low";
    if (ppm > 400) {
      gasStatus = "CRITICAL_SPOILAGE";
      spoilageRisk = "High (Dangerous Gases Detected)";
    } else if (ppm > 280) {
      gasStatus = "ELEVATED";
      spoilageRisk = "Moderate Spoilage";
    }

    this.telemetry.mq135GasSensor = {
      valuePpm: ppm,
      status: gasStatus,
      spoilageRisk: spoilageRisk
    };
    this.notify();
  }

  setBinLevel(percent) {
    this.telemetry.ultrasonicBinLevel = {
      fillPercentage: percent,
      distanceCm: Math.round(100 - percent),
      alert: percent > 80 ? "🚨 Critical Overflow (>80%)" : percent > 60 ? "Approaching Capacity" : "Normal Level"
    };
    this.telemetry.loadCellWeight.weightKg = +((percent / 100) * 20).toFixed(1);
    this.notify();
  }
}

export const iotSimulator = new IoTTelemetrySimulator();
