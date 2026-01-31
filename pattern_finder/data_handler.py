import os
import numpy as np
from interfaces import DataHandler


class RawFileDataHandler(DataHandler):
    """
    Reads pkt-stats-cell-X.dat files
    Provides:
    - Loss series (for correlation)
    - TX series (for capacity estimation)
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

    def get_loss_series(self, cell_id):
        """
        Normalized loss magnitude vector (for correlation)
        """
        path = os.path.join(self.data_dir, f"pkt-stats-cell-{cell_id}.dat")

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
                loss_series.append(loss)

        series = np.array(loss_series, dtype=float)

        # Normalize for stable correlation
        if series.size > 0 and series.max() > 0:
            series = series / series.max()

        return series

    def get_tx_series(self, cell_id):
        """
        Transmitted packets per time slot (for capacity estimation)
        """
        path = os.path.join(self.data_dir, f"pkt-stats-cell-{cell_id}.dat")

        tx_series = []
        with open(path, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) < 2:
                    continue

                try:
                    tx = float(parts[1])
                except ValueError:
                    continue

                tx_series.append(tx)

        return np.array(tx_series, dtype=float)
