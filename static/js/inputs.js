document.addEventListener("DOMContentLoaded", function () {
  const tbody = document.getElementById("locations-tbody");
  const addBtn = document.getElementById("add-location-btn");

  function addLocationRow(initial) {
    const row = document.createElement("tr");
    const name = initial && initial.name ? initial.name : "";
    const lat = initial && initial.lat !== undefined ? initial.lat : "";
    const lng = initial && initial.lng !== undefined ? initial.lng : "";

    row.innerHTML = `
      <td>
        <input
          type="text"
          name="location_name"
          aria-label="Project location name"
          value="${name}"
        />
      </td>
      <td>
        <input
          type="number"
          step="0.0001"
          name="location_lat"
          aria-label="Project location latitude"
          value="${lat}"
        />
      </td>
      <td>
        <input
          type="number"
          step="0.0001"
          name="location_lng"
          aria-label="Project location longitude"
          value="${lng}"
        />
      </td>
      <td>
        <button type="button" class="btn btn-outline location-delete" style="padding: 6px 12px; font-size: 0.85rem;">🗑 Delete</button>
      </td>
    `;
    tbody.appendChild(row);
  }

  if (tbody && addBtn) {
    addBtn.addEventListener("click", function () {
      addLocationRow();
    });

    tbody.addEventListener("click", function (event) {
      const target = event.target;
      if (target instanceof HTMLElement && target.classList.contains("location-delete")) {
        const row = target.closest("tr");
        if (row && tbody.contains(row)) {
          tbody.removeChild(row);
        }
      }
    });
  }

  // Leaflet map integration
  const mapElement = document.getElementById("inputs-map");

  if (mapElement && typeof L !== "undefined" && window.routeRushData) {
    const data = window.routeRushData;
    const center = Array.isArray(data.mapCenter) ? data.mapCenter : [11.6643, 78.1460];
    const zoom = typeof data.zoom === "number" ? data.zoom : 11;

    const map = L.map("inputs-map").setView(center, zoom);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: "&copy; OpenStreetMap contributors",
    }).addTo(map);

    const factoryMarkers = [];

    if (Array.isArray(data.factories)) {
      data.factories.forEach((factory, index) => {
        if (typeof factory.lat === "number" && typeof factory.lng === "number") {
          const marker = L.circleMarker([factory.lat, factory.lng], {
            radius: 7,
            color: "#003087",
            fillColor: "#003087",
            fillOpacity: 0.9,
          })
            .addTo(map)
            .bindTooltip(`Factory ${index + 1}: ${factory.name || ""}`);

          factoryMarkers[index] = marker;
        } else {
          factoryMarkers[index] = null;
        }
      });
    }

    if (Array.isArray(data.locations)) {
      data.locations.forEach((loc) => {
        if (typeof loc.lat === "number" && typeof loc.lng === "number") {
          L.circleMarker([loc.lat, loc.lng], {
            radius: 6,
            color: "#0f766e",
            fillColor: "#0f766e",
            fillOpacity: 0.9,
          })
            .addTo(map)
            .bindTooltip(loc.name || "Site");
        }
      });
    }

    let selectedFactoryIndex = null;
    const factoryModeInputs = document.querySelectorAll('input[name="map_factory_select"]');
    const modeIndicator = document.getElementById("map-mode-indicator");

    function updateModeIndicator() {
      if (modeIndicator) {
        if (selectedFactoryIndex === null) {
          modeIndicator.textContent = "➕ Click mode: Add Locations";
          modeIndicator.style.display = "block";
          modeIndicator.style.background = "var(--accent-green, #10b981)";
          // Make map cursor indicate clickable
          map.getContainer().style.cursor = "crosshair";
        } else {
          const factory = data.factories ? data.factories[selectedFactoryIndex] : null;
          const factoryName = factory ? (factory.name || `Factory ${selectedFactoryIndex + 1}`) : "Unknown";
          modeIndicator.textContent = `📍 Click mode: Move ${factoryName}`;
          modeIndicator.style.display = "block";
          modeIndicator.style.background = "var(--accent-blue, #3b82f6)";
          map.getContainer().style.cursor = "pointer";
        }
      }
    }

    factoryModeInputs.forEach((input) => {
      input.addEventListener("change", () => {
        const value = input.value;
        if (!input.checked) {
          return;
        }
        if (value === "-1") {
          selectedFactoryIndex = null;
        } else {
          const parsed = parseInt(value, 10);
          selectedFactoryIndex = Number.isNaN(parsed) ? null : parsed;
        }
        updateModeIndicator();
      });
    });

    // Initialize the mode indicator
    updateModeIndicator();

    map.on("click", (event) => {
      const lat = event.latlng.lat;
      const lng = event.latlng.lng;

      if (selectedFactoryIndex !== null) {
        const latInput = document.querySelector(
          `input[name="factory_${selectedFactoryIndex}_lat"]`,
        );
        const lngInput = document.querySelector(
          `input[name="factory_${selectedFactoryIndex}_lng"]`,
        );

        if (latInput && lngInput) {
          latInput.value = lat.toFixed(4);
          lngInput.value = lng.toFixed(4);
        }

        const marker = factoryMarkers[selectedFactoryIndex];
        if (marker) {
          marker.setLatLng([lat, lng]);
          marker.setStyle({ fillOpacity: 1 });
          setTimeout(() => {
            marker.setStyle({ fillOpacity: 0.9 });
          }, 200);
        }
      } else if (tbody) {
        const newIndex = tbody.children.length + 1;
        const latFixed = lat.toFixed(4);
        const lngFixed = lng.toFixed(4);

        addLocationRow({
          name: `Site ${newIndex}`,
          lat: latFixed,
          lng: lngFixed,
        });

        const newMarker = L.circleMarker([lat, lng], {
          radius: 6,
          color: "#0f766e",
          fillColor: "#0f766e",
          fillOpacity: 0.9,
          weight: 2,
        })
          .addTo(map)
          .bindTooltip(`Site ${newIndex}`);

        // Flash animation feedback
        setTimeout(() => {
          newMarker.setStyle({ weight: 3, fillOpacity: 1 });
          setTimeout(() => {
            newMarker.setStyle({ weight: 2, fillOpacity: 0.9 });
          }, 150);
        }, 50);
      }
    });
  }
});
