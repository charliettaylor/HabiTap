from functools import lru_cache
import src.config as config

@lru_cache()
def get():
    return config.Settings()
