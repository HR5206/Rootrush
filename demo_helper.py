"""Demo data generator for Route Rush.

Generates randomized logistics scenarios across India for testing and demonstration.
"""

import random
from typing import Any, Dict, List, Tuple


# Refined India bounding boxes by region (excluding coastal water areas)
# These bounds are more conservative and focus on land areas
INDIA_REGIONS = [
    {
        "name": "North",
        "lat_range": (25.5, 34.5),
        "lng_range": (73.0, 89.0),
    },
    {
        "name": "South",
        "lat_range": (8.5, 15.5),
        "lng_range": (73.0, 85.0),
    },
    {
        "name": "East",
        "lat_range": (20.0, 28.5),
        "lng_range": (84.0, 97.0),
    },
    {
        "name": "West",
        "lat_range": (17.0, 25.0),
        "lng_range": (68.0, 77.5),
    },
    {
        "name": "Central",
        "lat_range": (17.0, 25.0),
        "lng_range": (76.0, 83.0),
    },
]

# Major city centers across India (definitely on land)
INDIAN_CITIES = [
    {"name": "Delhi", "lat": 28.7041, "lng": 77.1025},
    {"name": "Mumbai", "lat": 19.0760, "lng": 72.8777},
    {"name": "Bangalore", "lat": 12.9716, "lng": 77.5946},
    {"name": "Hyderabad", "lat": 17.3850, "lng": 78.4867},
    {"name": "Chennai", "lat": 13.0827, "lng": 80.2707},
    {"name": "Kolkata", "lat": 22.5726, "lng": 88.3639},
    {"name": "Pune", "lat": 18.5204, "lng": 73.8567},
    {"name": "Ahmedabad", "lat": 23.0225, "lng": 72.5714},
    {"name": "Jaipur", "lat": 26.9124, "lng": 75.7873},
    {"name": "Lucknow", "lat": 26.8467, "lng": 80.9462},
    {"name": "Surat", "lat": 21.1702, "lng": 72.8311},
    {"name": "Kochi", "lat": 9.9312, "lng": 76.2673},
    {"name": "Indore", "lat": 22.7196, "lng": 75.8577},
    {"name": "Visakhapatnam", "lat": 17.6869, "lng": 83.2185},
    {"name": "Nagpur", "lat": 21.1458, "lng": 79.0882},
]


def _is_in_india_land(lat: float, lng: float) -> bool:
    """Check if coordinates are within India's land area (not on water).
    
    Uses region-based validation to avoid coastal water areas.
    """
    for region in INDIA_REGIONS:
        lat_min, lat_max = region["lat_range"]
        lng_min, lng_max = region["lng_range"]
        
        if lat_min <= lat <= lat_max and lng_min <= lng <= lng_max:
            return True
    
    return False


def generate_random_locations(
    count: int = 600,
    cluster_mode: str = "balanced",
    seed: int | None = None,
) -> List[Dict[str, Any]]:
    """Generate random delivery locations across India (land only, no water).

    Args:
        count: Number of locations to generate (default 600)
        cluster_mode: How to distribute locations:
            - "balanced": Evenly across India (by region)
            - "clustered": Around major cities
            - "mix": Mix of both approaches
        seed: Random seed for reproducibility (None = random)

    Returns:
        List of location dicts with name, lat, lng (all on land within India)
    """

    if seed is not None:
        random.seed(seed)

    locations: List[Dict[str, Any]] = []

    if cluster_mode == "clustered":
        # Distribute around major cities
        locs_per_city = count // len(INDIAN_CITIES)
        extra_locs = count % len(INDIAN_CITIES)

        for city_idx, city in enumerate(INDIAN_CITIES):
            needed = locs_per_city + (1 if city_idx < extra_locs else 0)

            # Try to generate each required location, with flexible retry strategy
            generated = 0
            max_retry_radius = 0.5  # Start with ±0.3, expand to ±0.5 if needed
            
            for attempt_radius in [0.3, 0.4, 0.5]:
                attempts = 0
                max_attempts = needed * 20  # Very generous retries
                
                while generated < needed and attempts < max_attempts:
                    lat = city["lat"] + random.uniform(-attempt_radius, attempt_radius)
                    lng = city["lng"] + random.uniform(-attempt_radius, attempt_radius)
                    attempts += 1

                    if _is_in_india_land(lat, lng):
                        locations.append(
                            {
                                "name": f"{city['name']} Site {generated + 1}",
                                "lat": round(lat, 4),
                                "lng": round(lng, 4),
                            }
                        )
                        generated += 1
                
                if generated >= needed:
                    break

    elif cluster_mode == "mix":
        # 70% clustered, 30% random across India
        clustered_count = int(count * 0.7)
        random_count = count - clustered_count

        # Clustered portion around cities
        locs_per_city = clustered_count // len(INDIAN_CITIES)
        for city_idx, city in enumerate(INDIAN_CITIES):
            needed = locs_per_city + (1 if city_idx < (clustered_count % len(INDIAN_CITIES)) else 0)
            
            # Try with expanding retry radius
            generated = 0
            for attempt_radius in [0.3, 0.4, 0.5]:
                attempts = 0
                max_attempts = needed * 20
                
                while generated < needed and attempts < max_attempts:
                    lat = city["lat"] + random.uniform(-attempt_radius, attempt_radius)
                    lng = city["lng"] + random.uniform(-attempt_radius, attempt_radius)
                    attempts += 1

                    if _is_in_india_land(lat, lng):
                        locations.append(
                            {
                                "name": f"{city['name']} Site {generated + 1}",
                                "lat": round(lat, 4),
                                "lng": round(lng, 4),
                            }
                        )
                        generated += 1
                
                if generated >= needed:
                    break

        # Random portion scattered across India (by region)
        locs_per_region = random_count // len(INDIA_REGIONS)
        extra_random = random_count % len(INDIA_REGIONS)

        for region_idx, region in enumerate(INDIA_REGIONS):
            region_count = locs_per_region + (1 if region_idx < extra_random else 0)
            lat_min, lat_max = region["lat_range"]
            lng_min, lng_max = region["lng_range"]

            for i in range(region_count):
                lat = random.uniform(lat_min, lat_max)
                lng = random.uniform(lng_min, lng_max)
                locations.append(
                    {
                        "name": f"{region['name']} Site {i + 1}",
                        "lat": round(lat, 4),
                        "lng": round(lng, 4),
                    }
                )

    else:  # balanced (default)
        # Distribute evenly across each region
        locs_per_region = count // len(INDIA_REGIONS)
        extra_locs = count % len(INDIA_REGIONS)

        for region_idx, region in enumerate(INDIA_REGIONS):
            region_count = locs_per_region + (1 if region_idx < extra_locs else 0)
            lat_min, lat_max = region["lat_range"]
            lng_min, lng_max = region["lng_range"]

            for i in range(region_count):
                lat = random.uniform(lat_min, lat_max)
                lng = random.uniform(lng_min, lng_max)

                locations.append(
                    {
                        "name": f"Delivery Site {i + 1}",
                        "lat": round(lat, 4),
                        "lng": round(lng, 4),
                    }
                )

    return locations

    return locations


def generate_demo_factories() -> List[Dict[str, Any]]:
    """Generate a set of factories distributed across India for demo purposes."""

    return [
        {
            "name": "Northern Hub (Delhi)",
            "lat": 28.7041,
            "lng": 77.1025,
            "weekly_rate": 60,
        },
        {
            "name": "Western Hub (Mumbai)",
            "lat": 19.0760,
            "lng": 72.8777,
            "weekly_rate": 70,
        },
        {
            "name": "Southern Hub (Bangalore)",
            "lat": 12.9716,
            "lng": 77.5946,
            "weekly_rate": 65,
        },
        {
            "name": "Eastern Hub (Kolkata)",
            "lat": 22.5726,
            "lng": 88.3639,
            "weekly_rate": 55,
        },
        {
            "name": "Central Hub (Hyderabad)",
            "lat": 17.3850,
            "lng": 78.4867,
            "weekly_rate": 60,
        },
    ]
