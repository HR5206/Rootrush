from __future__ import annotations

import math
from itertools import permutations
from typing import Any, Dict, List, Tuple


# ---- Distance utilities ----------------------------------------------------


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Compute great-circle distance between two points in kilometers.

    The inputs are decimal degrees. Output is the distance in kilometers, using
    Earth's mean radius of 6371 km.
    """

    # Convert degrees to radians
    rlat1 = math.radians(lat1)
    rlon1 = math.radians(lon1)
    rlat2 = math.radians(lat2)
    rlon2 = math.radians(lon2)

    dlat = rlat2 - rlat1
    dlon = rlon2 - rlon1

    a = math.sin(dlat / 2.0) ** 2 + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlon / 2.0) ** 2
    c = 2 * math.asin(math.sqrt(a))

    return 6371.0 * c


# ---- Clustering: assign locations to nearest factory -----------------------


def assign_locations_to_factories(
    factories: List[Dict[str, Any]],
    locations: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Assign each project location to its nearest factory.

    Returns a list of assignment dicts that include the original location and
    the chosen factory index, plus the distance in kilometers.
    """

    assignments: List[Dict[str, Any]] = []

    for loc_index, loc in enumerate(locations):
        lat = float(loc["lat"])
        lng = float(loc["lng"])

        best_factory_index: int | None = None
        best_distance_km: float | None = None

        for factory_index, factory in enumerate(factories):
            flat = float(factory["lat"])
            flng = float(factory["lng"])
            d = haversine_km(lat, lng, flat, flng)

            if best_distance_km is None or d < best_distance_km:
                best_distance_km = d
                best_factory_index = factory_index

        assignments.append(
            {
                "location_index": loc_index,
                "location": loc,
                "factory_index": best_factory_index,
                "factory": factories[best_factory_index] if best_factory_index is not None else None,
                "distance_km": best_distance_km,
            }
        )

    return assignments


# ---- Group assigned locations into batches of three ------------------------


def group_into_batches_of_three(
    assignments: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Group assigned locations into per-factory batches of exactly three.

    The function does not mutate the originals. Result structure:

    {
        "batches": [
            {
                "factory_index": int,
                "factory": {...},
                "location_indices": [int, int, int],
                "locations": [loc_dict, loc_dict, loc_dict],
            },
            ...
        ],
        "remainders": [assignment_dict, ...],  # locations that could not
                                               # form a full batch of three
    }

    Later parts may choose to rebalance these remainders globally across
    factories in order to fully respect the "exactly 3 locations per trip"
    constraint.
    """

    # Group assignments by factory index
    by_factory: Dict[int, List[Dict[str, Any]]] = {}
    for a in assignments:
        fi = a.get("factory_index")
        if fi is None:
            continue
        by_factory.setdefault(fi, []).append(a)

    batches: List[Dict[str, Any]] = []
    remainders: List[Dict[str, Any]] = []

    for factory_index, items in by_factory.items():
        # Sort by distance so nearer locations tend to be grouped together
        items_sorted = sorted(items, key=lambda x: (x["distance_km"] or 0.0))

        # Consume in chunks of 3
        i = 0
        while i + 3 <= len(items_sorted):
            chunk = items_sorted[i : i + 3]
            i += 3

            batch_locations = [c["location"] for c in chunk]
            batch_indices = [c["location_index"] for c in chunk]
            factory = chunk[0].get("factory")

            batches.append(
                {
                    "factory_index": factory_index,
                    "factory": factory,
                    "location_indices": batch_indices,
                    "locations": batch_locations,
                }
            )

        # Any leftover 1–2 locations for this factory become remainders
        if i < len(items_sorted):
            remainders.extend(items_sorted[i:])

    return {"batches": batches, "remainders": remainders}


def build_factory_batches(
    factories: List[Dict[str, Any]], locations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """High-level helper: from raw inputs to batches and remainders.

    This is what later planning code will call. It combines nearest-factory
    assignment with per-factory grouping into trip-sized batches.
    """

    assignments = assign_locations_to_factories(factories=factories, locations=locations)
    return group_into_batches_of_three(assignments)


# ---- Route optimisation for batches of three ------------------------------


def _route_distance_for_order(
    factory: Dict[str, Any],
    ordered_locations: List[Dict[str, Any]],
) -> float:
    """Return total route distance in km for Factory -> L1 -> L2 -> L3.

    Assumes ``ordered_locations`` has length 3. Does not include any
    return-to-factory leg because the problem statement only constrains
    Factory → Location 1 → Location 2 → Location 3.
    """

    flat = float(factory["lat"])
    flng = float(factory["lng"])

    total = 0.0

    # Factory -> first
    l1 = ordered_locations[0]
    total += haversine_km(flat, flng, float(l1["lat"]), float(l1["lng"]))

    # First -> second
    l2 = ordered_locations[1]
    total += haversine_km(
        float(l1["lat"]), float(l1["lng"]), float(l2["lat"]), float(l2["lng"])
    )

    # Second -> third
    l3 = ordered_locations[2]
    total += haversine_km(
        float(l2["lat"]), float(l2["lng"]), float(l3["lat"]), float(l3["lng"])
    )

    return total


def optimise_batch_routes(
    batches: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """For each 3-location batch, choose the best visit order.

    This performs a brute-force search over all 3! permutations of the
    locations in each batch. It minimises total route distance from the
    factory through the three locations (no return leg).

    Returns a new list of batch dicts that extend the input with:

    - ``route_order_indices``: indices within the batch's ``locations`` list
      in the chosen order [i0, i1, i2].
    - ``route_locations``: the locations in that chosen order.
    - ``total_distance_km``: total route length.
    """

    optimised: List[Dict[str, Any]] = []

    for batch in batches:
        locations = batch.get("locations", [])
        if len(locations) != 3:
            # Nothing to optimise; carry batch through unchanged.
            optimised.append(batch)
            continue

        factory = batch.get("factory")
        if not factory:
            optimised.append(batch)
            continue

        best_perm_indices: Tuple[int, int, int] | None = None
        best_distance: float | None = None

        # Enumerate permutations of indices [0, 1, 2]
        for order in permutations(range(3)):
            ordered_locs = [locations[i] for i in order]
            dist = _route_distance_for_order(factory, ordered_locs)

            if best_distance is None or dist < best_distance:
                best_distance = dist
                best_perm_indices = order  # type: ignore[assignment]

        if best_perm_indices is None or best_distance is None:
            optimised.append(batch)
            continue

        route_locations = [locations[i] for i in best_perm_indices]

        new_batch = dict(batch)
        new_batch.update(
            {
                "route_order_indices": list(best_perm_indices),
                "route_locations": route_locations,
                "total_distance_km": best_distance,
            }
        )
        optimised.append(new_batch)

    return optimised
