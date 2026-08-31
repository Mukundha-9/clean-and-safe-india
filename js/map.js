/* ==========================================================================
   Clean & Safe India App - GIS Mapping & Leaflet Controller
   Interactive OpenStreetMap, Location Pin Dropper, Ward Red Zones & Heatmaps
   ========================================================================== */

class MapManager {
  constructor() {
    this.mainMap = null;
    this.pickerMap = null;
    this.markers = [];
    this.pickerMarker = null;
    this.defaultCenter = [17.0005, 81.8040]; // Surampalem / Rajahmundry central coordinates
    this.defaultZoom = 14;
  }

  // Initialize the main full GIS Explore Map
  initMainMap(containerId = 'gisMapContainer', issues = []) {
    const container = document.getElementById(containerId);
    if (!container || !window.L) return;

    if (this.mainMap) {
      this.mainMap.remove();
    }

    this.mainMap = L.map(containerId, {
      zoomControl: true,
      attributionControl: true
    }).setView(this.defaultCenter, this.defaultZoom);

    // OpenStreetMap CartoDB Positron / Standard Tile Layer
    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>'
    }).addTo(this.mainMap);

    this.renderIssueMarkers(issues);
  }

  // Render issue pins on main map
  renderIssueMarkers(issues) {
    if (!this.mainMap || !window.L) return;

    // Clear existing
    this.markers.forEach(m => this.mainMap.removeLayer(m));
    this.markers = [];

    issues.forEach(issue => {
      if (!issue.lat || !issue.lng) return;

      const isResolved = issue.status === 'resolved';
      const isEscalated = issue.status === 'escalated';
      const color = isResolved ? '#10b981' : isEscalated ? '#ef4444' : '#f59e0b';

      const customIcon = L.divIcon({
        className: 'custom-map-pin',
        html: `
          <div style="
            background: ${color};
            width: 34px;
            height: 34px;
            border-radius: 50%;
            border: 3px solid white;
            box-shadow: 0 3px 10px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            color: white;
            cursor: pointer;
          ">
            ${issue.categoryIcon || '📌'}
          </div>
        `,
        iconSize: [34, 34],
        iconAnchor: [17, 17],
        popupAnchor: [0, -20]
      });

      const marker = L.marker([issue.lat, issue.lng], { icon: customIcon }).addTo(this.mainMap);

      const popupHtml = `
        <div style="font-family: system-ui; max-width: 220px; padding: 4px;">
          <div style="font-size: 11px; font-weight: 700; color: ${color}; text-transform: uppercase; margin-bottom: 2px;">
            ${issue.status.replace('_', ' ')} • ${issue.id}
          </div>
          <div style="font-weight: 700; font-size: 13px; color: #0f172a; margin-bottom: 4px;">
            ${issue.title}
          </div>
          <div style="font-size: 12px; color: #64748b; margin-bottom: 8px;">
            📍 ${issue.location}
          </div>
          <button onclick="window.viewIssueDetail('${issue.id}')" style="
            width: 100%;
            background: #10b981;
            color: white;
            border: none;
            padding: 5px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
            cursor: pointer;
          ">
            View Case Details
          </button>
        </div>
      `;

      marker.bindPopup(popupHtml);
      this.markers.push(marker);
    });

    // Invalidate map size after render
    setTimeout(() => {
      this.mainMap.invalidateSize();
    }, 200);
  }

  // Initialize Report Modal Location Pin Dropper
  initPickerMap(containerId = 'locationPickerMap', initialCoords = null, onSelect = null) {
    const container = document.getElementById(containerId);
    if (!container || !window.L) return;

    if (this.pickerMap) {
      this.pickerMap.remove();
    }

    const coords = initialCoords || this.defaultCenter;

    this.pickerMap = L.map(containerId, {
      zoomControl: true
    }).setView(coords, 15);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
      maxZoom: 19
    }).addTo(this.pickerMap);

    // Draggable Marker
    this.pickerMarker = L.marker(coords, {
      draggable: true
    }).addTo(this.pickerMap);

    const updatePosition = (lat, lng) => {
      if (onSelect) {
        onSelect(lat, lng, `Ward 12, Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)}`);
      }
    };

    this.pickerMarker.on('dragend', (e) => {
      const pos = e.target.getLatLng();
      updatePosition(pos.lat, pos.lng);
    });

    this.pickerMap.on('click', (e) => {
      this.pickerMarker.setLatLng(e.latlng);
      updatePosition(e.latlng.lat, e.latlng.lng);
    });

    setTimeout(() => {
      this.pickerMap.invalidateSize();
    }, 200);
  }

  // Auto-detect GPS using browser Geolocation API
  detectCurrentGPS(callback) {
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;
          if (this.pickerMap && this.pickerMarker) {
            this.pickerMap.setView([lat, lng], 16);
            this.pickerMarker.setLatLng([lat, lng]);
          }
          if (callback) {
            callback(lat, lng, `Auto-detected GPS: Lat ${lat.toFixed(4)}, Lng ${lng.toFixed(4)}`);
          }
        },
        (error) => {
          console.warn("GPS Geolocation error/declined, using default local coordinates:", error);
          if (callback) {
            callback(this.defaultCenter[0], this.defaultCenter[1], "Ward 12 Central Market Junction, Surampalem");
          }
        }
      );
    } else {
      if (callback) {
        callback(this.defaultCenter[0], this.defaultCenter[1], "Ward 12 Central Market Junction, Surampalem");
      }
    }
  }
}

export const mapManager = new MapManager();
