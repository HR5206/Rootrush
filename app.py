from flask import Flask, render_template, redirect, url_for, request, session, make_response
import csv
from io import StringIO
import json

import data_layer
import clustering
import scheduling
import objectives
import huggingface_integration
import demo_helper


def create_app() -> Flask:
    app = Flask(__name__)

    # Simple dev secret key; can be overridden via environment in production
    app.config["SECRET_KEY"] = "dev-route-rush-secret-key"

    @app.route("/")
    def home():
        return render_template("home.html")

    @app.route("/inputs", methods=["GET", "POST"])
    def inputs():
        factories = data_layer.ensure_factories()
        locations = data_layer.ensure_locations()

        if request.method == "POST":
            action = request.form.get("action", "").strip()

            if action == "save_factories":
                updated_factories = []

                for index in range(3):
                    prefix = f"factory_{index}"
                    name = request.form.get(f"{prefix}_name", "").strip() or f"Factory {index + 1}"

                    def _parse_float(field_name, fallback):
                        raw = request.form.get(field_name, "").strip()
                        if not raw:
                            return fallback
                        try:
                            return float(raw)
                        except ValueError:
                            return fallback

                    def _parse_int(field_name, fallback):
                        raw = request.form.get(field_name, "").strip()
                        if not raw:
                            return fallback
                        try:
                            return int(raw)
                        except ValueError:
                            return fallback

                    base = factories[index] if index < len(factories) else data_layer.ensure_factories()[
                        index
                    ]
                    lat = _parse_float(f"{prefix}_lat", base.get("lat"))
                    lng = _parse_float(f"{prefix}_lng", base.get("lng"))
                    weekly_rate = _parse_int(f"{prefix}_weekly", base.get("weekly_rate"))

                    updated_factories.append(
                        {
                            "name": name,
                            "lat": lat,
                            "lng": lng,
                            "weekly_rate": weekly_rate,
                        }
                    )
                factories = updated_factories
                data_layer.save_factories(factories)

            elif action == "save_locations":
                # Read lists of names and coordinates from the submitted table
                names = request.form.getlist("location_name")
                lats = request.form.getlist("location_lat")
                lngs = request.form.getlist("location_lng")

                updated_locations = []

                for name, lat_raw, lng_raw in zip(names, lats, lngs):
                    name = (name or "").strip()
                    if not name and not lat_raw and not lng_raw:
                        continue

                    try:
                        lat = float(lat_raw)
                        lng = float(lng_raw)
                    except (TypeError, ValueError):
                        # Skip rows with invalid coordinates
                        continue

                    updated_locations.append({"name": name or "Site", "lat": lat, "lng": lng})

                if updated_locations:
                    locations = updated_locations
                    data_layer.save_locations(locations)

            elif action == "upload_locations":
                file = request.files.get("locations_csv")
                if file and file.filename:
                    try:
                        content = file.read().decode("utf-8")
                        reader = csv.reader(StringIO(content))
                    except Exception:
                        reader = None

                    if reader is not None:
                        uploaded_locations = []
                        for row in reader:
                            if not row:
                                continue
                            # Expecting at least: name, lat, lng
                            if len(row) < 3:
                                continue
                            name = (row[0] or "").strip()
                            try:
                                lat = float(row[1])
                                lng = float(row[2])
                            except (TypeError, ValueError):
                                continue

                            uploaded_locations.append(
                                {"name": name or "Site", "lat": lat, "lng": lng}
                            )

                        if uploaded_locations:
                            locations = uploaded_locations
                            data_layer.save_locations(locations)

        return render_template("inputs.html", factories=factories, locations=locations)

    @app.route("/demo")
    def demo():
        """Generate a demo plan with 600 random delivery locations across India.
        
        This route:
        1. Sets up 5 distribution factories across India
        2. Generates 600 random delivery locations  
        3. Runs the full optimization pipeline
        4. Saves results to file storage (bypasses session size limits)
        5. Redirects to results
        """
        
        # Get demo factories and locations
        demo_factories = demo_helper.generate_demo_factories()
        demo_locations = demo_helper.generate_random_locations(count=600, cluster_mode="mix", seed=42)
        
        # Save to session for consistency
        data_layer.save_factories(demo_factories)
        data_layer.save_locations(demo_locations)
        
        # Run the full optimization pipeline directly to ensure data is saved
        inputs_snapshot = {
            "factories": demo_factories,
            "locations": demo_locations,
        }
        factories = inputs_snapshot["factories"]
        locations = inputs_snapshot["locations"]

        # Cluster into nearest-factory batches and optimise routes
        clustering_result = clustering.build_factory_batches(factories, locations)
        batches = clustering_result["batches"]
        remainders = clustering_result["remainders"]
        optimised_batches = clustering.optimise_batch_routes(batches)

        # Simulate schedule
        schedule = scheduling.simulate_schedule(factories, optimised_batches)

        # Compute objective metrics
        objective_metrics = objectives.compute_objectives(schedule)

        # Optional AI insights
        settings_data = data_layer.get_settings()

        summary_lines = [
            "Route Rush demo plan (600 locations across India):",
            f"- Total locations: {len(locations)}",
            f"- Total batches (trips): {len(optimised_batches)}",
            f"- Unbatched remainders: {len(remainders)}",
            f"- Completion time (hours): {objective_metrics['completion_time_hours']:.2f}",
            f"- Max factory inventory (cabins): {objective_metrics['max_factory_inventory_cabins']:.2f}",
            f"- Max waiting time (hours): {objective_metrics['max_wait_time_hours']:.2f}",
        ]

        prompt = "\n".join(
            summary_lines
            + [
                "",
                (
                    "Write a concise 'AI Insights & Recommendations' section "
                    "explaining why the batches and routes make sense, "
                    "suggesting 1-2 alternative clustering ideas, and calling out "
                    "potential bottlenecks in production, delivery, or installation."
                ),
            ]
        )

        ai_payload = {"prompt": prompt}
        ai_insights = huggingface_integration.get_ai_insights(ai_payload, settings_data)

        plan_results = {
            "inputs": inputs_snapshot,
            "factories": factories,
            "locations": locations,
            "batches": optimised_batches,
            "remainders": remainders,
            "schedule": schedule,
            "objectives": objective_metrics,
            "ai_insights": ai_insights,
        }

        # Save to file storage (handles large datasets)
        data_layer.save_plan_results(plan_results)

        return redirect(url_for("results"))

    @app.route("/generate")
    def generate():
        # Collect current inputs
        inputs_snapshot = data_layer.get_current_inputs()
        factories = inputs_snapshot["factories"]
        locations = inputs_snapshot["locations"]

        # Cluster into nearest-factory batches and optimise routes
        clustering_result = clustering.build_factory_batches(factories, locations)
        batches = clustering_result["batches"]
        remainders = clustering_result["remainders"]
        optimised_batches = clustering.optimise_batch_routes(batches)

        # Simulate schedule
        schedule = scheduling.simulate_schedule(factories, optimised_batches)

        # Compute objective metrics
        objective_metrics = objectives.compute_objectives(schedule)

        # Optional AI insights
        settings_data = data_layer.get_settings()

        summary_lines = [
            "Route Rush plan summary:",
            f"- Total locations: {len(locations)}",
            f"- Total batches (trips): {len(optimised_batches)}",
            f"- Unbatched remainders: {len(remainders)}",
            f"- Completion time (hours): {objective_metrics['completion_time_hours']:.2f}",
            f"- Max factory inventory (cabins): {objective_metrics['max_factory_inventory_cabins']:.2f}",
            f"- Max waiting time (hours): {objective_metrics['max_wait_time_hours']:.2f}",
        ]

        prompt = "\n".join(
            summary_lines
            + [
                "",
                (
                    "Write a concise 'AI Insights & Recommendations' section "
                    "explaining why the batches and routes make sense, "
                    "suggesting 1-2 alternative clustering ideas, and calling out "
                    "potential bottlenecks in production, delivery, or installation."
                ),
            ]
        )

        ai_payload = {"prompt": prompt}
        ai_insights = huggingface_integration.get_ai_insights(ai_payload, settings_data)

        plan_results = {
            "inputs": inputs_snapshot,
            "factories": factories,
            "locations": locations,
            "batches": optimised_batches,
            "remainders": remainders,
            "schedule": schedule,
            "objectives": objective_metrics,
            "ai_insights": ai_insights,
        }

        data_layer.save_plan_results(plan_results)

        return redirect(url_for("results"))

    @app.route("/results")
    def results():
        plan = data_layer.get_plan_results()
        return render_template("results.html", plan=plan)

    @app.route("/download/plan.json")
    def download_plan_json():
        plan = data_layer.get_plan_results()
        if not plan:
            return redirect(url_for("results"))

        payload = json.dumps(plan, default=str)
        response = make_response(payload)
        response.headers["Content-Type"] = "application/json"
        response.headers["Content-Disposition"] = "attachment; filename=route_rush_plan.json"
        return response

    @app.route("/download/plan.csv")
    def download_plan_csv():
        plan = data_layer.get_plan_results()
        if not plan:
            return redirect(url_for("results"))

        output = StringIO()
        writer = csv.writer(output)

        writer.writerow(
            [
                "factory_name",
                "location_name",
                "depart_time_hours",
                "arrival_time_hours",
                "install_start_hours",
                "install_end_hours",
            ]
        )

        schedule = plan.get("schedule") or {}
        factory_summaries = schedule.get("factories") or []

        for summary in factory_summaries:
            factory = summary.get("factory") or {}
            factory_name = factory.get("name", "")
            for trip in summary.get("trips") or []:
                depart = trip.get("depart_time_hours", 0.0)
                for stop in trip.get("stops") or []:
                    location = stop.get("location") or {}
                    writer.writerow(
                        [
                            factory_name,
                            location.get("name", ""),
                            stop.get("arrival_time_hours", 0.0),
                            stop.get("arrival_time_hours", 0.0),
                            stop.get("install_start_hours", 0.0),
                            stop.get("install_end_hours", 0.0),
                        ]
                    )

        response = make_response(output.getvalue())
        response.headers["Content-Type"] = "text/csv"
        response.headers["Content-Disposition"] = "attachment; filename=route_rush_schedule.csv"
        return response

    @app.route("/insights")
    def insights():
        plan = data_layer.get_plan_results()
        if not plan:
            return redirect(url_for("results"))

        ai = plan.get("ai_insights") or {}
        if not ai.get("enabled") or not ai.get("text"):
            return redirect(url_for("results"))

        return render_template("insights.html", plan=plan, ai=ai)

    @app.route("/settings", methods=["GET", "POST"])
    def settings():
        settings_data = data_layer.get_settings()

        if request.method == "POST":
            enable_ai = request.form.get("enable_ai_insights") == "on"
            token = request.form.get("hf_api_token", "")

            # Never echo the token back to the browser as a value; only store
            # it server-side in the session-backed settings.
            settings_data["enable_ai_insights"] = enable_ai
            if token is not None and token.strip():
                settings_data["hf_api_token"] = token.strip()

            data_layer.save_settings(settings_data)

        # Do not send the raw token back to the template; instead, expose a
        # simple flag that indicates whether a token is configured.
        has_token = bool(settings_data.get("hf_api_token"))

        return render_template(
            "settings.html",
            enable_ai_insights=settings_data.get("enable_ai_insights", True),
            has_hf_token=has_token,
        )

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(debug=True)
