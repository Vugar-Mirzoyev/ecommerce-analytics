# setup.py
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

from src.data_loader import EcommerceDataLoader

loader = EcommerceDataLoader()
loader.load_raw_data()
print("Setup completed!")