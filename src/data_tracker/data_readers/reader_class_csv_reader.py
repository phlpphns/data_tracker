from data_tracker.data_readers import DataReaderStrategy
import pandas as pd

class CSVDataReader(DataReaderStrategy):
    FILE_TYPE = ["csv", "tsv"]  # This is how the facade knows which format this reader supports
    # FILE_TYPE = "csv"  # This is how the facade knows which format this reader supports

    def read_data(self, file_path, **kwargs) -> pd.DataFrame:
        df = pd.read_csv(file_path, **kwargs)
        return self.normalize(df)
    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        return df
