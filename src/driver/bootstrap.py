from src.core.haproxyupdater.haproxyupdate import HaproxyUpdate
from src.core.nodefetchers.awsfetcher.awsfetcher import AwsFetcher

def bootstrap(**kwargs):
    config = kwargs.get("config")

    
