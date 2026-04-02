from __future__ import annotations

from typing import Any, Dict, List

import clustering


TRUCK_SPEED_KMPH = 40.0
INSTALL_HOURS = 4.0
HOURS_PER_WEEK = 7.0 * 24.0


def _production_rate_per_hour(weekly_rate: float) -> float:
    if weekly_rate <= 0:
        return 0.0
    return weekly_rate / HOURS_PER_WEEK


def _compute_factory_trips(
    factory_index: int,
    factory: Dict[str, Any],
    batches_for_factory: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Simulate production and trips for a single factory.

    Assumptions:
    - Production starts at time 0 with no initial inventory.
    - Production is continuous at weekly_rate / (7*24) cabins/hour.
    - Each trip consumes exactly len(batch["locations"]) cabins (normally 3).
    - Departure time for each trip is when cumulative production reaches
      previous_consumed + required_for_this_trip, keeping factory inventory
      low and never exceeding the 6-cabin storage limit.
    - Trucks are unlimited; there is no truck resource constraint.
    """

    weekly_rate = float(factory.get("weekly_rate", 0))
    rate_per_hour = _production_rate_per_hour(weekly_rate)

    cabins_used = 0.0
    trips: List[Dict[str, Any]] = []
    max_factory_inventory = 0.0

    all_install_end_times: List[float] = []

    for global_batch_index, batch in enumerate(batches_for_factory):
        locations = batch.get("route_locations") or batch.get("locations") or []
        num_cabins = float(len(locations))
        if num_cabins <= 0:
            continue

        if rate_per_hour > 0:
            required_total = cabins_used + num_cabins
            depart_time_hours = required_total / rate_per_hour
            produced_at_departure = depart_time_hours * rate_per_hour
            inventory_before = produced_at_departure - cabins_used
            max_factory_inventory = max(max_factory_inventory, inventory_before)
            cabins_used = required_total
        else:
            # No production capacity defined; treat as immediate departure but
            # mark that production is infeasible via a flag in the summary.
            depart_time_hours = 0.0

        flat = float(factory["lat"])
        flng = float(factory["lng"])

        current_time = depart_time_hours
        previous_lat = flat
        previous_lng = flng

        stops: List[Dict[str, Any]] = []
        total_distance_km = 0.0

        for loc in locations:
            lat = float(loc["lat"])
            lng = float(loc["lng"])

            leg_distance_km = clustering.haversine_km(previous_lat, previous_lng, lat, lng)
            total_distance_km += leg_distance_km

            travel_time_hours = leg_distance_km / TRUCK_SPEED_KMPH if TRUCK_SPEED_KMPH > 0 else 0.0
            arrival_time_hours = current_time + travel_time_hours

            install_start_hours = arrival_time_hours
            install_end_hours = install_start_hours + INSTALL_HOURS

            stops.append(
                {
                    "location": loc,
                    "arrival_time_hours": arrival_time_hours,
                    "install_start_hours": install_start_hours,
                    "install_end_hours": install_end_hours,
                }
            )

            all_install_end_times.append(install_end_hours)

            current_time = arrival_time_hours
            previous_lat = lat
            previous_lng = lng

        total_travel_time_hours = total_distance_km / TRUCK_SPEED_KMPH if TRUCK_SPEED_KMPH > 0 else 0.0

        trips.append(
            {
                "batch": batch,
                "depart_time_hours": depart_time_hours,
                "total_distance_km": total_distance_km,
                "total_travel_time_hours": total_travel_time_hours,
                "stops": stops,
            }
        )

    factory_completion = max(all_install_end_times) if all_install_end_times else 0.0

    return {
        "factory_index": factory_index,
        "factory": factory,
        "weekly_rate": weekly_rate,
        "production_rate_per_hour": rate_per_hour,
        "trips": trips,
        "factory_completion_time_hours": factory_completion,
        "max_factory_inventory_cabins": max_factory_inventory,
        "production_feasible": rate_per_hour > 0,
    }


def simulate_schedule(
    factories: List[Dict[str, Any]],
    batches: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Simulate production, deliveries, and installations for all factories.

    Inputs:
    - factories: list of factory dicts with at least lat, lng, weekly_rate.
    - batches: list of batch dicts, each including factory_index and
      locations/route_locations.

    Time is expressed in hours from t=0.

    Returns a dictionary summarising per-factory and global schedule:

    {
        "factories": [
            {
                "factory_index": int,
                "factory": {...},
                "weekly_rate": float,
                "production_rate_per_hour": float,
                "trips": [
                    {
                        "batch": batch_dict,
                        "depart_time_hours": float,
                        "total_distance_km": float,
                        "total_travel_time_hours": float,
                        "stops": [
                            {
                                "location": {...},
                                "arrival_time_hours": float,
                                "install_start_hours": float,
                                "install_end_hours": float,
                            },
                            ...
                        ],
                    },
                    ...
                ],
                "factory_completion_time_hours": float,
                "max_factory_inventory_cabins": float,
                "production_feasible": bool,
            },
            ...
        ],
        "overall_completion_time_hours": float,
    }

    This structure is intentionally rich so that later parts can derive
    objective metrics (max waiting time, total inventory, completion time)
    without rerunning the simulation.
    """

    # Group batches by factory_index
    by_factory: Dict[int, List[Dict[str, Any]]] = {}
    for batch in batches:
        fi = batch.get("factory_index")
        if fi is None:
            continue
        by_factory.setdefault(int(fi), []).append(batch)

    factory_summaries: List[Dict[str, Any]] = []
    all_completion_times: List[float] = []

    for factory_index, factory in enumerate(factories):
        batches_for_factory = by_factory.get(factory_index, [])
        summary = _compute_factory_trips(factory_index, factory, batches_for_factory)
        factory_summaries.append(summary)
        all_completion_times.append(summary["factory_completion_time_hours"])

    overall_completion = max(all_completion_times) if all_completion_times else 0.0

    return {
        "factories": factory_summaries,
        "overall_completion_time_hours": overall_completion,
    }
