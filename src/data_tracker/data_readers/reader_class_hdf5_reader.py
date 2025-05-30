from data_tracker.data_readers import DataReaderStrategy
import pandas as pd
import yaml
import h5py


class HDF5DataReader(DataReaderStrategy):
    FILE_TYPE = "h5"

    def read_data(self, file_path, **kwargs) -> pd.DataFrame:
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)
        return pd.json_normalize(data)
    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        return df
