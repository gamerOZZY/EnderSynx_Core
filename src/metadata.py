from datetime import datetime, timezone
from pathlib import Path


def create_metadata(ruta_zip):
    return {
        "world_name": "New Worldrr\"==",
        "minecraft_version": "1.20.1",
        "modpack": "Chocolate Edition",
        "modpack_version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "file_name": ruta_zip.name,
        "file_size_bytes": ruta_zip.stat().st_size
    }

def get_minecraft_version():
    pass

def get_modpack():
    pass

def get_modpack_version():
    pass

