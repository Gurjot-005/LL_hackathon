from abc import ABC, abstractmethod
import numpy as np

class DataHandler(ABC):
    @abstractmethod
    def get_cells(self):
        pass

    @abstractmethod
    def get_loss_series(self, cell_id) -> np.ndarray:
        pass

    @abstractmethod
    def get_tx_series(self, cell_id) -> np.ndarray:
        pass


