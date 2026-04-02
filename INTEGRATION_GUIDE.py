"""
STEP-BY-STEP API INTEGRATION GUIDE FOR ROUTE RUSH
==================================================

This shows the complete pattern for integrating ANY API into Route Rush.
We'll use a generic example, then you can adapt for your specific API.
"""

# ============================================================================
# STEP 1: UNDERSTAND YOUR API
# ============================================================================

"""
Before coding, gather this information about your API:

1. API Endpoint: What's the base URL?
   Example: https://api.example.com/v1

2. Authentication: How do you authenticate?
   - API Key in header: Header("Authorization", "Bearer YOUR_KEY")
   - API Key in query: ?api_key=YOUR_KEY
   - OAuth2: More complex flow
   - Basic auth: username:password

3. Rate Limits: How many requests per minute/hour?
   - This matters for 600 locations!
   - May need request batching or caching

4. Input Format: What data do you send?
   Example for routing: {"origin": [lat, lng], "destination": [lat, lng]}

5. Output Format: What data do you receive?
   Example: {"distance_km": 45.2, "time_minutes": 52, ...}

6. Cost: Is it free or paid? Pricing model?

7. Error Handling: What status codes mean what?
   - 200: Success
   - 400: Bad request
   - 401: Unauthorized
   - 429: Rate limit exceeded
   - 500: Server error
"""

# ============================================================================
# STEP 2: CREATE THE API MODULE
# ============================================================================

# File: api_integrations.py

import os
import json
import time
from typing import Any, Dict, List, Optional
import urllib.request
import urllib.error


class APIIntegration:
    """Base class for all API integrations."""
    
    def __init__(self, api_key: str):
        """Initialize with API credentials.
        
        Args:
            api_key: Your API key (from environment or settings)
        """
        self.api_key = api_key
        self.base_url = ""  # Override in subclass
        self.timeout = 30
        self.last_request_time = 0
        self.min_request_interval = 0.1  # seconds between requests (rate limiting)
    
    def _rate_limit(self):
        """Enforce minimum interval between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()
    
    def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request to API.
        
        Args:
            endpoint: API endpoint (appended to base_url)
            method: HTTP method (GET, POST, etc.)
            data: Request body data (for POST)
            headers: Additional headers
        
        Returns:
            Parsed JSON response
        
        Raises:
            Exception: If request fails
        """
        # Rate limiting
        self._rate_limit()
        
        # Build URL
        url = f"{self.base_url}/{endpoint}"
        
        # Prepare headers
        if headers is None:
            headers = {}
        headers["Content-Type"] = "application/json"
        
        # Add authentication (customize for your API)
        headers["Authorization"] = f"Bearer {self.api_key}"
        
        # Prepare request
        if data:
            data_bytes = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(
                url,
                data=data_bytes,
                headers=headers,
                method=method
            )
        else:
            req = urllib.request.Request(url, headers=headers, method=method)
        
        try:
            # Make request
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                response_data = response.read().decode('utf-8')
                return json.loads(response_data)
        
        except urllib.error.HTTPError as e:
            # Handle HTTP errors
            if e.code == 401:
                raise Exception("Authentication failed - check your API key")
            elif e.code == 429:
                raise Exception("Rate limit exceeded - wait before retrying")
            elif e.code == 400:
                raise Exception(f"Bad request: {e.reason}")
            else:
                raise Exception(f"API error {e.code}: {e.reason}")
        
        except urllib.error.URLError as e:
            raise Exception(f"Network error: {e.reason}")
        
        except json.JSONDecodeError:
            raise Exception("Invalid JSON response from API")


class ExampleRoutingAPI(APIIntegration):
    """Example: Integration with a routing/distance API.
    
    This is a template. Replace with your actual API.
    """
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = "https://api.example.com/v1"  # Change to your API
    
    def get_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> Dict[str, Any]:
        """Get distance and time between two points.
        
        Args:
            lat1, lng1: Starting point
            lat2, lng2: Ending point
        
        Returns:
            {
                "distance_km": float,
                "time_minutes": float,
                "route": [[lat, lng], ...]  # if available
            }
        """
        
        # Prepare request (customize for your API)
        data = {
            "from": {"lat": lat1, "lng": lng1},
            "to": {"lat": lat2, "lng": lng2}
        }
        
        # Make request
        response = self._make_request("distance", method="POST", data=data)
        
        # Extract and normalize response (your API format will differ)
        return {
            "distance_km": response.get("distance_km", 0),
            "time_minutes": response.get("duration_minutes", 0),
        }
    
    def batch_distances(
        self,
        locations: List[Dict[str, float]]
    ) -> List[Dict[str, Any]]:
        """Get distances between multiple locations (batch mode).
        
        Useful for 600 deliveries - much faster than individual requests.
        
        Args:
            locations: List of {"lat": lat, "lng": lng} dicts
        
        Returns:
            Distance matrix
        """
        
        data = {"locations": locations}
        response = self._make_request("distance-matrix", method="POST", data=data)
        return response.get("distances", [])


# ============================================================================
# STEP 3: STORE API CREDENTIALS SAFELY
# ============================================================================

"""
NEVER hardcode API keys in your code!

Option 1: Environment Variables (Recommended for development)
---
In your terminal:
  set ROUTING_API_KEY=your_api_key_here
  
In your Python code:
  import os
  api_key = os.getenv("ROUTING_API_KEY")

Option 2: Settings File (For app configuration)
---
Already in Route Rush via data_layer.py!
"""


def load_api_key_from_settings(setting_name: str) -> str:
    """Load API key from app settings.
    
    Example:
        api_key = load_api_key_from_settings("routing_api_key")
    """
    import data_layer
    settings = data_layer.get_settings()
    return settings.get(setting_name, "")


# ============================================================================
# STEP 4: ERROR HANDLING AND RETRIES
# ============================================================================

def call_api_with_retry(
    api_call,
    max_retries: int = 3,
    backoff_factor: float = 2.0
) -> Any:
    """Wrap any API call with automatic retry logic.
    
    # Example usage:
    result = call_api_with_retry(
        lambda: routing_api.get_distance(lat1, lng1, lat2, lng2),
        max_retries=3
    )
    """
    
    for attempt in range(max_retries):
        try:
            return api_call()
        except Exception as e:
            if attempt == max_retries - 1:
                # Last attempt failed
                raise e
            
            # Wait before retrying (exponential backoff)
            wait_time = (backoff_factor ** attempt)
            print(f"API call failed, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
            time.sleep(wait_time)


# ============================================================================
# STEP 5: TESTING THE API
# ============================================================================

if __name__ == "__main__":
    print("=== API Integration Testing ===\n")
    
    # Test 1: Check if API key is configured
    print("1. Checking API credentials...")
    api_key = os.getenv("ROUTING_API_KEY")
    if not api_key:
        print("   ⚠️  API_KEY not set in environment variables")
        print("   Set it with: set ROUTING_API_KEY=your_key")
    else:
        print("   ✓ API key found")
    
    # Test 2: Initialize API
    print("\n2. Initializing API client...")
    try:
        api = ExampleRoutingAPI(api_key)
        print("   ✓ API client ready")
    except Exception as e:
        print(f"   ❌ Failed to initialize: {e}")
    
    # Test 3: Test single request
    print("\n3. Testing single distance request...")
    try:
        result = api.get_distance(28.6139, 77.2090, 28.7041, 77.1025)  # Delhi
        print(f"   ✓ Distance: {result['distance_km']:.1f} km")
        print(f"   ✓ Time: {result['time_minutes']:.0f} minutes")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test 4: Test batch requests (for 600 locations)
    print("\n4. Testing batch distance request...")
    try:
        test_locations = [
            {"lat": 28.6139, "lng": 77.2090},
            {"lat": 28.7041, "lng": 77.1025},
            {"lat": 28.5244, "lng": 77.1855},
        ]
        result = api.batch_distances(test_locations)
        print(f"   ✓ Batch request succeeded")
        print(f"   ✓ Results: {len(result)} distance pairs")
    except Exception as e:
        print(f"   ❌ Batch request failed: {e}")

