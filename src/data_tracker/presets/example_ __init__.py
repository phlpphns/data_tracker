import os
import importlib

__all__ = []

for module_name in os.listdir(os.path.dirname(__file__)):
    if module_name.endswith(".py") and module_name != "__init__.py":
        module = importlib.import_module(f".{module_name[:-3]}", package=__name__)
        globals().update({k: v for k, v in module.__dict__.items() if not k.startswith("_")})
        __all__.extend(module.__all__)




# Similar to pools/__init__.py
import os
import importlib

__all__ = []

for module_name in os.listdir(os.path.dirname(__file__)):
    if module_name.endswith(".py") and module_name != "__init__.py":
        module = importlib.import_module(f".{module_name[:-3]}", package=__name__)
        globals().update({k: v for k, v in module.__dict__.items() if not k.startswith("_")})
        __all__.extend(module.__all__)



# Similar to pools/__init__.py
import os
import importlib

__all__ = []

for module_name in os.listdir(os.path.dirname(__file__)):
    if module_name.endswith(".py") and module_name != "__init__.py":
        module = importlib.import_module(f".{module_name[:-3]}", package=__name__)
        globals().update({k: v for k, v in module.__dict__.items() if not k.startswith("_")})
        __all__.extend(module.__all__)





import importlib
from . import pools, selectors, processors

class DataProcessorFactory:
    def create_pool(self, pool_type):
        pool_class = getattr(pools, f"{pool_type.upper()}Pool")
        return pool_class()

    def create_selector(self, selector_type):
        selector_class = getattr(selectors, f"{selector_type.title()}Selector")
        return selector_class()

    def create_processor(self, processor_type):
        processor_class = getattr(processors, f"{processor_type.title()}Processor")
        return processor_class()


from .factory import DataProcessorFactory

def process_file(filename, file_type, selection_type, processor_type, config):
    factory = DataProcessorFactory()

    pool = factory.create_pool(file_type)
    selector = factory.create_selector(selection_type)
    processor = factory.create_processor(processor_type)

    data_pool = pool.process(filename, config)
    selected_data = selector.select_data(data_pool, config)
    processor.plot_data(selected_data, config)

# Example usage (same as before)




"""
your_project/
    data_processing/
        __init__.py
        pools/
            __init__.py
            csv_pool.py
            json_pool.py
            # ... other pool modules
        selectors/
            __init__.py
            basic_selector.py
            advanced_selector.py
            # ... other selector modules
        processors/
            __init__.py
            simple_processor.py
            complex_processor.py
            # ... other processor modules
        factory.py
        processing_pipeline.py  # Client code
"""

        