# https://stackoverflow.com/questions/67631/how-can-i-import-a-module-dynamically-given-the-full-path

from data_tracker.data_readers import DataReaderStrategy


import importlib.util
import inspect
import os
import pkgutil
from pathlib import Path
import sys

import inspect
import sys
if not hasattr(sys.modules[__name__], '__file__'):
    __file__ = inspect.getfile(inspect.currentframe())



'''
import importlib
import inspect
import pkgutil

from data_tracker.data_readers import DataReaderStrategy
import data_tracker.data_readers as readers_pkg

def find_reader_classes():
    reader_classes = []

    # Iterate over all submodules in the package
    for _, module_name, is_pkg in pkgutil.iter_modules(readers_pkg.__path__, readers_pkg.__name__ + "."):
        if is_pkg:
            continue  # Skip sub-packages if any

        try:
            module = importlib.import_module(module_name)
        except ImportError:
            continue  # Skip modules that fail to import

        # Look through all classes defined in the module
        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Check if it's a subclass of DataReaderStrategy and defined in this module
            if issubclass(obj, DataReaderStrategy) and obj is not DataReaderStrategy and obj.__module__ == module.__name__:
                reader_classes.append(obj)

    return reader_classes
'''


class DataReaderFacade:
    def __init__(self, search_paths=[os.path.join(Path(__file__).parent.parent, 'data_readers')], path_user_scripts=None):
    # def __init__(self, search_paths=[os.path.join(os.path.abspath('..'), 'data_readers')], path_user_scripts=None):
        self.strategies = {}
        self.search_paths = search_paths or []
        self.path_user_scripts = path_user_scripts or []
        self.search_paths = self.search_paths + self.path_user_scripts
        # print("self.search_paths:    ", self.search_paths)
        self._discover_readers()

    def _discover_readers(self):
        """Dynamically loads and registers all DataReaderStrategy subclasses from file paths."""
        for search_path in self.search_paths:
            search_path = Path(search_path)
            if search_path.is_dir():
                for file_path in search_path.iterdir():
                    if file_path.is_file() and file_path.suffix == ".py" and os.path.basename(file_path).startswith("reader_class_"):
                        module_name = file_path.stem
                        # print('\n', module_name)
                        try:
                            self._import_and_register(module_name, file_path=file_path)
                        except Exception as e:
                            print(f"Warning: Failed to load {module_name} from {file_path}: {e}")

    def _import_and_register(self, module_name, file_path):
        """Imports a module from a file path and registers all DataReaderStrategy subclasses."""
        spec = importlib.util.spec_from_file_location(module_name, str(file_path.absolute()))
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        for _, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, DataReaderStrategy) and obj is not DataReaderStrategy:
                file_types = obj.FILE_TYPE if isinstance(obj.FILE_TYPE, list) else [obj.FILE_TYPE]
                for file_type in file_types:
                    self.strategies[file_type.lower()] = obj()
                    print(f"Registered reader: {file_type} -> {obj.__name__}")

    def register_strategy(self, file_type: str, strategy: DataReaderStrategy):
        """Manually register a new data reader."""
        if not isinstance(strategy, DataReaderStrategy):
            raise TypeError("Strategy must inherit from DataReaderStrategy.")
        self.strategies[file_type] = strategy

    def read(self, file_path: str, file_type: str, **kwargs):
        """Reads data using the appropriate strategy."""
        file_type = file_type.lower()
        strategy = self.strategies.get(file_type)

        if not strategy:
            raise ValueError(f"Unsupported file type: {file_type}")

        df = strategy.read_data(file_path, **kwargs)
        return strategy.normalize(df)


# # this here is full of ugly hacks owing to relative path issues

# from ..data_readers.base import DataReaderStrategy

# import importlib
# import os
# from pathlib import Path
# import pkgutil
# import inspect


# class _DataReaderFacade:
#     def __init__(self, readers_package="../data_readers"):
#         self.strategies = {}
#         self.readers_package = readers_package
#         self._discover_readers()

#     def _discover_readers(self):
#         """Dynamically loads and registers all DataReaderStrategy subclasses from the readers package."""
#         # package_path = Path(self.readers_package.replace(".", "/"))
#         package_path = Path(self.readers_package)  # .replace(".", ""))

#         current_dir = os.path.dirname(os.path.abspath(__file__))
#         print("current_dir:     ", current_dir)
#         package_path = os.path.join(current_dir, self.readers_package)
#         print(package_path)

#         # print('\n\n\n\n\n\n\n')
#         # print("package_path:    ", package_path)

#         for _, module_name, __ in pkgutil.iter_modules([str(package_path)]):
#             # print(_)
#             # print(module_name)
#             # print(__)
#             module_path = f"{self.readers_package}.{module_name}"
#             # print("module_path:    ", module_path)
#             try:
#                 self._import_and_register(module_path)
#             except Exception as e:
#                 print(f"Warning: Failed to load {module_path}: {e}")

#     def _import_and_register(self, module_path):
#         """Imports a module and registers all subclasses of DataReaderStrategy."""
#         print("Wir sind hier.")
#         print(module_path)
#         module = importlib.import_module(
#             module_path[len("../") :], package="data_tracker.data_readers"
#         )
#         print("module:    ", module)
#         # print(ddd)

#         for _, obj in inspect.getmembers(module, inspect.isclass):
#             print("\n======")
#             print(obj)
#             print(DataReaderStrategy)
#             print(obj.FILE_TYPE)
#             print(DataReaderStrategy.FILE_TYPE)
#             print(issubclass(obj, DataReaderStrategy))
#             print(obj is not DataReaderStrategy)
#             print("======\n")

#             if issubclass(obj, DataReaderStrategy) and obj is not DataReaderStrategy:
#                 # if obj.FILE_TYPE and obj is not DataReaderStrategy:
#                 # print('HHHHHHH:    ', obj.FILE_TYPE)
#                 file_type = obj.FILE_TYPE.lower()  # Normalize to lowercase
#                 self.strategies[file_type] = obj()
#                 print(f"Registered reader: {file_type} -> {obj.__name__}")

#     def __import_and_register(self, module_path):
#         """
#         Imports a module and registers all subclasses of DataReaderStrategy.
#         we need to improve that in order to be able to detect multiple file types
#         """
#         module = importlib.import_module(module_path)

#         for _, obj in inspect.getmembers(module, inspect.isclass):
#             if issubclass(obj, DataReaderStrategy) and obj is not DataReaderStrategy:
#                 file_types = (
#                     obj.FILE_TYPE
#                     if isinstance(obj.FILE_TYPE, list)
#                     else [obj.FILE_TYPE]
#                 )
#                 for file_type in file_types:
#                     self.strategies[file_type.lower()] = obj()
#                 print(f"Registered reader: {file_type} -> {obj.__name__}")

#     def register_strategy(self, file_type: str, strategy: DataReaderStrategy):
#         """Manually register a new data reader."""
#         if not isinstance(strategy, DataReaderStrategy):
#             raise TypeError("Strategy must inherit from DataReaderStrategy.")
#         self.strategies[file_type] = strategy

#     def read(self, file_path: str, file_type: str, **kwargs):
#         """Reads data using the appropriate strategy."""
#         file_type = file_type.lower()  # Normalize case
#         strategy = self.strategies.get(file_type)

#         if not strategy:
#             raise ValueError(f"Unsupported file type: {file_type}")

#         df = strategy.read_data(file_path, **kwargs)
#         return strategy.normalize(df)  # Ensure output consistency
