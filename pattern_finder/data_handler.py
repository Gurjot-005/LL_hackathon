import os
import numpy as np
from interfaces import DataHandler


class RawFileDataHandler(DataHandler):
    """
    Reads pkt-stats-cell-X.dat files
    Supports:
    - Packet loss vectors
    - DU throughput (TX side)
    - RU throughput (RX side)
    - get_tx_series() for backward compatibility
    """

    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.cells = self._scan_cells()

    def _scan_cells(self):
        cells = []
        for fname in os.listdir(self.data_dir):
            if fname.startswith("pkt-stats-cell") and fname.endswith(".dat"):
                cell_id = fname.split("-")[-1].replace(".dat", "")
                cells.append(cell_id)
        return sorted(cells, key=lambda x: int(x))

    def get_cells(self):
        return self.cells

    # ---------------------------
    # Internal file reader
    # ---------------------------
    def _read_file(self, cell_id):
        path = os.path.join(self.data_dir, f"pkt-stats-cell-{cell_id}.dat")

        tx_series = []
        rx_series = []
        loss_series = []

        with open(path, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) < 4:
                    continue

                try:
                    tx = float(parts[1])
                    rx = float(parts[2])
                    late = float(parts[3])
                except ValueError:
                    continue

                loss = max(0.0, tx - rx + late)

                tx_series.append(tx)
                rx_series.append(rx)
                loss_series.append(1.0 if loss > 0 else 0.0)

        return (
            np.array(tx_series, dtype=float),
            np.array(rx_series, dtype=float),
            np.array(loss_series, dtype=float),
        )

    # ---------------------------
    # Interface Methods
    # ---------------------------
    def get_loss_series(self, cell_id):
        _, _, loss = self._read_file(cell_id)
        return loss

    def get_du_throughput(self, cell_id):
        tx, _, _ = self._read_file(cell_id)
        return tx

    def get_ru_throughput(self, cell_id):
        _, rx, _ = self._read_file(cell_id)
        return rx

    # ---------------------------
    # Compatibility Method
    # ---------------------------
    def get_tx_series(self, cell_id):
        """
        Backward compatibility for older estimators:
        TX = DU throughput
        """
        return self.get_du_throughput(cell_id)
