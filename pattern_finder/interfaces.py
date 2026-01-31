# interfaces.py

from abc import ABC, abstractmethod

class DataHandler(ABC):
    """
    Defines how any dataset (raw, cleaned, CSV, database, live feed)
    must provide data to the pattern finder.
    """

    @abstractmethod
    def get_cells(self):
        """Return a list of cell IDs"""
        pass

    @abstractmethod
    def get_loss_series(self, cell_id):
        """
        Return a time-aligned binary packet loss series for a cell.
        Example:
        [0, 1, 0, 0, 1, 1, 0]
        """
        pass
