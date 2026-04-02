from __future__ import annotations

from typing import Any, Dict, List


def _collect_all_stops(schedule: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Flatten all trip stops across all factories into a single list."""

    all_stops: List[Dict[str, Any]] = []
    for factory_summary in schedule.get("factories", []):
        for trip in factory_summary.get("trips", []):
            for stop in trip.get("stops", []):
                enriched = dict(stop)
                enriched["factory_index"] = factory_summary.get("factory_index")
                enriched["factory"] = factory_summary.get("factory")
                all_stops.append(enriched)
    return all_stops


def compute_objectives(schedule: Dict[str, Any]) -> Dict[str, Any]:
    """Compute key objectives from a schedule structure.

    Objectives:
    - max_wait_time_hours: max (install_start - arrival) over all sites.
      In the current model installation starts immediately, so this will
      typically be 0.0, but leaving the calculation explicit makes later
      enhancements straightforward.
    - total_inventory_cabins: approximate total inventory exposure across
      factories and sites (sum over time slices is expensive; instead we
      aggregate:
        - max factory inventory across all factories
        - count of in-progress installations as "site inventory" at any point
      This is a simplification but keeps the metric interpretable.
    - completion_time_hours: overall project completion from the schedule
      (already provided as overall_completion_time_hours).
    """

    all_stops = _collect_all_stops(schedule)

    max_wait_time_hours = 0.0
    for stop in all_stops:
        arrival = float(stop.get("arrival_time_hours", 0.0))
        install_start = float(stop.get("install_start_hours", arrival))
        wait = max(0.0, install_start - arrival)
        if wait > max_wait_time_hours:
            max_wait_time_hours = wait

    # Approximated inventory metrics
    factory_inventory_peaks = [
        float(f.get("max_factory_inventory_cabins", 0.0))
        for f in schedule.get("factories", [])
    ]
    max_factory_inventory = max(factory_inventory_peaks) if factory_inventory_peaks else 0.0

    # Site inventory: installations are 4h; we approximate exposure by counting
    # how many installations exist and multiplying by one cabin each.
    total_cabins = len(all_stops)

    completion_time_hours = float(schedule.get("overall_completion_time_hours", 0.0))

    return {
        "max_wait_time_hours": max_wait_time_hours,
        "max_factory_inventory_cabins": max_factory_inventory,
        "total_cabins": total_cabins,
        "completion_time_hours": completion_time_hours,
    }
