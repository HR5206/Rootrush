document.addEventListener("DOMContentLoaded", function () {
  const data = window.routeRushPlan;
  if (!data) {
    return;
  }

  const factories = Array.isArray(data.factories) ? data.factories : [];
  const batches = Array.isArray(data.batches) ? data.batches : [];
  const schedule = data.schedule || {};

  // Shared colour palette for routes and charts
  const colours = [
    "#ef4444", // red
    "#f97316", // orange
    "#eab308", // yellow
    "#22c55e", // green
    "#06b6d4", // cyan
    "#3b82f6", // blue
    "#a855f7", // purple
    "#ec4899", // pink
  ];

  // --- Leaflet map for routes ---
  const mapElement = document.getElementById("results-map");
  if (mapElement && typeof L !== "undefined") {
    let centerLat = 11.6643;
    let centerLng = 78.146;

    if (factories.length > 0) {
      const f0 = factories[0];
      if (typeof f0.lat === "number" && typeof f0.lng === "number") {
        centerLat = f0.lat;
        centerLng = f0.lng;
      }
    }

    const map = L.map("results-map").setView([centerLat, centerLng], 11);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: "&copy; OpenStreetMap contributors",
    }).addTo(map);

    // Draw factory markers
    const factoryMarkers = [];
    factories.forEach((factory, index) => {
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

    // Draw location markers separately for context
    const locationSet = new Set();
    const batchesForLocations = Array.isArray(batches) ? batches : [];

    batchesForLocations.forEach((batch) => {
      const locs = batch.route_locations || batch.locations || [];
      locs.forEach((loc) => {
        const key = `${loc.name}|${loc.lat}|${loc.lng}`;
        if (locationSet.has(key)) {
          return;
        }
        locationSet.add(key);
        if (typeof loc.lat === "number" && typeof loc.lng === "number") {
          L.circleMarker([loc.lat, loc.lng], {
            radius: 5,
            color: "#0f766e",
            fillColor: "#0f766e",
            fillOpacity: 0.9,
          })
            .addTo(map)
            .bindTooltip(loc.name || "Site");
        }
      });
    });

    // Draw batch routes
    batches.forEach((batch, index) => {
      const factoryIndex =
        typeof batch.factory_index === "number" ? batch.factory_index : null;
      if (factoryIndex === null || factoryIndex < 0 || factoryIndex >= factories.length) {
        return;
      }
      const factory = factories[factoryIndex];
      if (typeof factory.lat !== "number" || typeof factory.lng !== "number") {
        return;
      }

      const locs = batch.route_locations || batch.locations || [];
      if (!Array.isArray(locs) || locs.length === 0) {
        return;
      }

      const points = [];
      points.push([factory.lat, factory.lng]);
      locs.forEach((loc) => {
        if (typeof loc.lat === "number" && typeof loc.lng === "number") {
          points.push([loc.lat, loc.lng]);
        }
      });

      if (points.length < 2) {
        return;
      }

      const colour = colours[index % colours.length];

      L.polyline(points, {
        color: colour,
        weight: 3,
        opacity: 0.9,
      }).addTo(map);
    });
  }

  // --- Chart.js installation timeline ---
  const timelineCanvas = document.getElementById("installation-timeline");
  if (
    timelineCanvas &&
    typeof Chart !== "undefined" &&
    schedule &&
    Array.isArray(schedule.factories)
  ) {
    const factorySummaries = schedule.factories;
    const datasets = [];

    factorySummaries.forEach((summary, factoryIndex) => {
      const points = [];
      const trips = Array.isArray(summary.trips) ? summary.trips : [];

      trips.forEach((trip) => {
        const stops = Array.isArray(trip.stops) ? trip.stops : [];
        stops.forEach((stop) => {
          if (typeof stop.install_start_hours === "number") {
            points.push({ x: stop.install_start_hours, y: factoryIndex });
          }
        });
      });

      if (points.length === 0) {
        return;
      }

      const colour = colours[factoryIndex % colours.length];
      const label =
        summary.factory && summary.factory.name
          ? summary.factory.name
          : `Factory ${factoryIndex + 1}`;

      datasets.push({
        label,
        data: points,
        backgroundColor: colour,
        borderColor: colour,
        pointRadius: 4,
      });
    });

    if (datasets.length > 0) {
      const ctx = timelineCanvas.getContext("2d");
      // eslint-disable-next-line no-new
      new Chart(ctx, {
        type: "scatter",
        data: { datasets },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: "bottom" },
            tooltip: {
              callbacks: {
                label(context) {
                  const label = context.dataset.label || "";
                  const x = context.parsed.x;
                  return `${label}: start ~ ${x.toFixed(1)} h`;
                },
              },
            },
          },
          scales: {
            x: {
              type: "linear",
              title: {
                display: true,
                text: "Hours from start",
              },
            },
            y: {
              type: "linear",
              ticks: {
                stepSize: 1,
                callback(value) {
                  const idx = Math.round(value);
                  const summary = factorySummaries[idx];
                  if (summary && summary.factory && summary.factory.name) {
                    return summary.factory.name;
                  }
                  return `Factory ${idx + 1}`;
                },
              },
              title: {
                display: true,
                text: "Factory",
              },
            },
          },
        },
      });
    }
  }
});
