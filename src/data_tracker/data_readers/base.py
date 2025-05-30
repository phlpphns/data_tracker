from abc import ABC, abstractmethod
import pandas as pd


class DataReaderStrategy(ABC):
    """Base class for all data readers."""

    FILE_TYPE = None  # This should be overridden in subclasses

    @abstractmethod
    def read_data(self, file_path, **kwargs) -> pd.DataFrame:
        """Reads data from a file and returns a normalized DataFrame."""
        pass

    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensures the DataFrame follows a consistent structure."""
        # df = df.copy()

        # # Standardize timestamp
        # if "timestamp" not in df.columns:
        #     df["timestamp"] = pd.Timestamp.now()

        # # Ensure ID column
        # if "id" not in df.columns:
        #     df.insert(0, "id", range(1, len(df) + 1))

        return df
