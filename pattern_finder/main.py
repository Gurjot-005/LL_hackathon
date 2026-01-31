# main.py

import os
import json
import numpy as np

from config import DATA_PATH, CORRELATION_THRESHOLD, OUTPUT_DIR
from data_handler import RawFileDataHandler
from loss_vector_builder import LossVectorBuilder
from correlation_engine import CorrelationEngine
from clustering_engine import ClusteringEngine
from validator import LinkValidator
from visualization import Visualizer


def main():
    print("📡 Nokia Fronthaul Pattern Finder Starting...\n")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Load data
    print("🔍 Loading raw telemetry...")
    handler = RawFileDataHandler(DATA_PATH)

    cells = handler.get_cells()
    print(f"Found {len(cells)} cells")

    # 2. Build loss vectors
    print("🧠 Building behavior fingerprints...")
    vector_builder = LossVectorBuilder(handler)
    vectors = vector_builder.build()

    np.save(f"{OUTPUT_DIR}/loss_vectors.npy", vectors)

    # 3. Correlation
    print("📊 Computing correlation matrix...")
    corr_engine = CorrelationEngine(CORRELATION_THRESHOLD)
    corr_df = corr_engine.compute_matrix(vectors)
    corr_df.to_csv(f"{OUTPUT_DIR}/corr_matrix.csv")

    # 4. Clustering
    print("🕸️ Inferring topology...")
    cluster_engine = ClusteringEngine(CORRELATION_THRESHOLD)
    link_map = cluster_engine.cluster(corr_df)

    # 5. Validation
    print("✅ Validating inferred links...")
    validator = LinkValidator()
    issues = validator.validate(link_map)

    # 6. Visualization
    print("🎨 Generating heatmap...")
    viz = Visualizer()
    viz.save_heatmap(corr_df, f"{OUTPUT_DIR}/heatmap.png")

    # 7. Save results
    print("💾 Saving topology mapping...")
    with open(f"{OUTPUT_DIR}/cell_to_link.json", "w") as f:
        json.dump(link_map, f, indent=2)

    print("\n🏁 DONE — Network Topology Discovered\n")

    print("Link Map:")
    for link, cells in link_map.items():
        print(f"{link}: {cells}")

    if issues:
        print("\n⚠️ Warnings:")
        for issue in issues:
            print("-", issue)
    else:
        print("\nNo validation issues found.")


if __name__ == "__main__":
    main()
