import numpy as np

class DualCaptureCapacityEstimator:
    """
    Estimates Ethernet link capacity using dual capture points:
    - DU side = demand (before congestion)
    - RU side = delivered traffic (after congestion)

    Outputs:
    - Peak demand (Gbps)
    - Congestion score
    - Safe capacity with buffer margin
    """

    def __init__(self, buffer_margin=0.25, slot_duration_us=143):
        """
        buffer_margin: safety margin for Ethernet provisioning (25% default)
        slot_duration_us: 1 slot = 143 microseconds (from Nokia spec)
        """
        self.buffer_margin = buffer_margin
        self.slot_duration_us = slot_duration_us

    def _series_to_gbps(self, packet_series):
        """
        Converts packets per slot into Gbps
        Assumes:
        - 1500 byte packets
        - slot_duration_us per slot
        """
        if len(packet_series) == 0:
            return np.array([])

        bits_per_packet = 1500 * 8
        slot_seconds = self.slot_duration_us / 1_000_000

        return (packet_series * bits_per_packet) / slot_seconds / 1e9

    def estimate(self, link_map, handler):
        """
        handler must implement:
        - get_du_throughput(cell_id)
        - get_ru_throughput(cell_id)
        """

        capacity_map = {}

        for link, cells in link_map.items():
            du_series_all = []
            ru_series_all = []

            for cell in cells:
                du = handler.get_du_throughput(cell)
                ru = handler.get_ru_throughput(cell)

                du_series_all.append(du)
                ru_series_all.append(ru)

            if not du_series_all:
                capacity_map[link] = {}
                continue

            # Align lengths
            min_len = min(map(len, du_series_all + ru_series_all))

            du_sum = np.sum([s[:min_len] for s in du_series_all], axis=0)
            ru_sum = np.sum([s[:min_len] for s in ru_series_all], axis=0)

            du_gbps = self._series_to_gbps(du_sum)
            ru_gbps = self._series_to_gbps(ru_sum)

            if len(du_gbps) == 0:
                capacity_map[link] = {}
                continue

            peak_demand = float(np.max(du_gbps))
            avg_demand = float(np.mean(du_gbps))

            congestion = float(
                np.mean(
                    np.clip((du_gbps - ru_gbps) / (du_gbps + 1e-9), 0, 1)
                )
            )

            safe_capacity = peak_demand * (1 + self.buffer_margin)

            capacity_map[link] = {
                "peak_demand_gbps": round(peak_demand, 3),
                "average_demand_gbps": round(avg_demand, 3),
                "safe_capacity_gbps": round(safe_capacity, 3),
                "congestion_score": round(congestion, 3),
                "buffer_margin": self.buffer_margin
            }

        return capacity_map
