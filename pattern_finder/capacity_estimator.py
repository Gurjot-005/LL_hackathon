import numpy as np


class LinkCapacityEstimator:
    """
    Estimates required Ethernet capacity per inferred link
    based on transmitted packet rates of grouped cells.
    Uses TX series from the DataHandler interface.
    """

    def __init__(
        self,
        packet_size_bytes=1500,   # Ethernet MTU
        slot_duration_sec=0.001, # 1 ms time slot
        buffer_margin=0.20      # 20% safety margin
    ):
        self.packet_bits = packet_size_bytes * 8
        self.slot_duration = slot_duration_sec
        self.buffer_margin = buffer_margin

    def estimate(self, link_map, handler):
        """
        link_map: dict {link_id: [cell_ids]}
        handler: DataHandler (RAW or PROCESSED)

        Returns:
        {
          "Link_1": {
              "estimated_gbps": float,
              "safe_gbps": float
          },
          ...
        }
        """
        results = {}
        slots_per_second = 1.0 / self.slot_duration

        for link, cells in link_map.items():
            total_packets_per_slot = 0.0

            for cell in cells:
                tx_series = handler.get_tx_series(cell)

                if tx_series is not None and len(tx_series) > 0:
                    total_packets_per_slot += float(np.mean(tx_series))

            # packets/slot → packets/sec → bits/sec → Gbps
            bits_per_second = (
                total_packets_per_slot *
                slots_per_second *
                self.packet_bits
            )

            gbps = bits_per_second / 1e9
            safe_gbps = gbps * (1 + self.buffer_margin)

            results[link] = {
                "estimated_gbps": round(gbps, 3),
                "safe_gbps": round(safe_gbps, 3)
            }

        return results
