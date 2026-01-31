import json
import os
from datetime import datetime


def export_topology(
    output_path,
    link_map,
    confidences,
    threshold,
    dataset_mode,
    cell_count,
    capacity_map=None
):
    """
    Exports inferred topology for frontend / visualization layer
    """

    try:
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        export_data = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "dataset": dataset_mode,
            "threshold": threshold,
            "cell_count": cell_count,
            "links": []
        }

        for link, cells in link_map.items():
            export_data["links"].append({
                "id": link,
                "cells": cells,
                "confidence": round(confidences.get(link, 0.0), 3),
                "capacity": capacity_map.get(link, {}) if capacity_map else {}
            })

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2)

        print(f"🧾 Frontend JSON saved to: {output_path}")
        return export_data

    except Exception as e:
        print("❌ Failed to export topology.json")
        print("Error:", e)
        return None
