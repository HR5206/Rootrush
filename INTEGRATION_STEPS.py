"""
STEP 6: INTEGRATE API INTO ROUTE RUSH
=====================================

This shows how to use your API throughout the Route Rush application.
"""

# ============================================================================
# MODIFY: clustering.py - Use real distances instead of haversine
# ============================================================================

"""
Current code uses haversine (straight-line distance):

    d = haversine_km(lat1, lng1, lat2, lng2)

Replace with API call for real road distance:

    d = routing_api.get_distance(lat1, lng1, lat2, lng2)['distance_km']
"""

# In clustering.py, add:

def initialize_routing_api():
    """Initialize routing API from settings."""
    from api_integrations import ExampleRoutingAPI
    import data_layer
    
    settings = data_layer.get_settings()
    api_key = settings.get("routing_api_key")
    
    if not api_key:
        print("Warning: Routing API key not configured, using haversine")
        return None
    
    try:
        return ExampleRoutingAPI(api_key)
    except Exception as e:
        print(f"Warning: Could not initialize routing API: {e}")
        return None


# ============================================================================
# MODIFY: app.py - Add API settings page
# ============================================================================

"""
Add to /settings route to let users configure their API key:

@app.route("/settings", methods=["GET", "POST"])
def settings():
    settings_data = data_layer.get_settings()
    
    if request.method == "POST":
        # ... existing code for AI settings ...
        
        # ADD: Store API key from form
        routing_api_key = request.form.get("routing_api_key", "").strip()
        if routing_api_key:
            settings_data["routing_api_key"] = routing_api_key
        
        data_layer.save_settings(settings_data)
    
    return render_template(
        "settings.html",
        enable_ai_insights=settings_data.get("enable_ai_insights", True),
        has_hf_token=bool(settings_data.get("hf_api_token")),
        has_routing_api_key=bool(settings_data.get("routing_api_key")),  # ADD THIS
    )
"""

# ============================================================================
# MODIFY: settings.html - Add API key input
# ============================================================================

"""
Add to the settings template:

<section class="card" style="margin-top: 24px;">
    <h2>🗺️ Routing API Configuration</h2>
    <p class="text-muted">
        Use real-world routing data with turn-by-turn directions and traffic.
        Requires API key from your routing provider.
    </p>
    
    <form method="post">
        <div class="form-col" style="margin-top: 12px;">
            <label>Routing API Key</label>
            <input
                type="password"
                name="routing_api_key"
                placeholder="Enter your API key"
                style="width: 100%; padding: 8px; border-radius: 6px;"
            >
            <small class="text-muted">
                {% if has_routing_api_key %}
                    ✓ API key configured
                {% else %}
                    Get key from: https://example.com/api-keys
                {% endif %}
            </small>
        </div>
        
        <div class="form-actions" style="margin-top: 12px;">
            <button type="submit" class="btn btn-primary">Save Settings</button>
        </div>
    </form>
</section>
"""

# ============================================================================
# STEP 7: FOR 600 LOCATIONS - USE BATCH REQUESTS
# ============================================================================

"""
For 600 deliveries, individual API calls would be too slow!

Instead, use batch/matrix requests where available:

old way (600+ individual requests):
---
for i, loc in enumerate(locations):
    for j, other_loc in enumerate(locations):
        distance = routing_api.get_distance(...)  # SLOW!

new way (1 batch request):
---
distances = routing_api.batch_distances(locations)  # FAST!
"""

# Example: Modify clustering.py

def build_factory_batches_with_real_distances(
    factories,
    locations,
    routing_api=None
):
    """Build batches using real routing distances if available."""
    
    if routing_api is None:
        # Fall back to existing haversine method
        return build_factory_batches(factories, locations)
    
    try:
        # Use batch request for all distances at once
        location_coords = [
            {"lat": loc["lat"], "lng": loc["lng"]}
            for loc in locations
        ]
        
        distance_matrix = routing_api.batch_distances(location_coords)
        
        # Now use distance_matrix instead of calculating haversine
        # in assign_locations_to_factories()
        
        return build_factory_batches_with_matrix(
            factories,
            locations,
            distance_matrix
        )
    
    except Exception as e:
        print(f"Batch distance request failed: {e}")
        print("Falling back to haversine calculation")
        return build_factory_batches(factories, locations)


# ============================================================================
# STEP 8: HANDLE API FAILURES GRACEFULLY
# ============================================================================

"""
APIs can fail! Your app must handle it:

1. Rate limits: Wait and retry
2. Invalid API key: Show user
3. Network errors: Use fallback method
4. Timeouts: Use cached results
"""

# Example: Wrap in error handler

def get_distance_safe(lat1, lng1, lat2, lng2, routing_api=None):
    """Get distance, falling back to haversine if API fails."""
    
    if routing_api is None:
        # Use haversine
        from clustering import haversine_km
        return haversine_km(lat1, lng1, lat2, lng2)
    
    try:
        result = call_api_with_retry(
            lambda: routing_api.get_distance(lat1, lng1, lat2, lng2),
            max_retries=3
        )
        return result["distance_km"]
    
    except Exception as e:
        print(f"API error (using fallback): {e}")
        # Fall back to haversine
        from clustering import haversine_km
        return haversine_km(lat1, lng1, lat2, lng2)


# ============================================================================
# STEP 9: ADD CACHING TO AVOID REPEATED API CALLS
# ============================================================================

"""
If you call get_distance(lat1, lng1, lat2, lng2) twice,
don't call the API twice - cache the result!
"""

import functools

class DistanceCache:
    """Simple cache for distance API calls."""
    
    def __init__(self):
        self.cache = {}
    
    def get_key(self, lat1, lng1, lat2, lng2):
        """Create cache key from coordinates."""
        # Round to 4 decimals to handle floating point differences
        return (
            round(lat1, 4),
            round(lng1, 4),
            round(lat2, 4),
            round(lng2, 4),
        )
    
    def get(self, lat1, lng1, lat2, lng2):
        """Get distance from cache."""
        key = self.get_key(lat1, lng1, lat2, lng2)
        return self.cache.get(key)
    
    def set(self, lat1, lng1, lat2, lng2, distance_km):
        """Store distance in cache."""
        key = self.get_key(lat1, lng1, lat2, lng2)
        self.cache[key] = distance_km
    
    def clear(self):
        """Clear cache."""
        self.cache.clear()


# Usage:
cache = DistanceCache()

def get_distance_cached(lat1, lng1, lat2, lng2, routing_api=None):
    """Get distance with caching."""
    
    # Check cache first
    cached = cache.get(lat1, lng1, lat2, lng2)
    if cached is not None:
        return cached
    
    # Call API or fallback
    distance = get_distance_safe(lat1, lng1, lat2, lng2, routing_api)
    
    # Store in cache
    cache.set(lat1, lng1, lat2, lng2, distance)
    
    return distance

