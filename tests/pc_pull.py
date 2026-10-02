import tempfile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.checkFiles import obtener_metadata
from src.utils import calcular_sha256
from src.utils import cargar_configuracion
from src.utils import cargar_json
from src.utils import crear_s3_client
from src.utils import descargar_zip
from src.utils import descomprimir_zip



rutas_devices = (
    Path(__file__).resolve().parent.parent
    / "config"
    / "rutes_config.json"
)


def main():
    configuracion = cargar_configuracion()
    rutas = cargar_json(rutas_devices)
    pc = rutas["pc"]
    world_name = pc["nombre_mundo_pull"]

    print("\nConsultando información del mundo...")

    s3 = crear_s3_client(configuracion)
    metadata = obtener_metadata(s3, configuracion, world_name)

    print("\nMundo encontrado:")
    print(f"  Mundo:             {metadata['world_name']}")
    print(f"  Minecraft:         {metadata['minecraft_version']}")
    print(f"  Modpack:           {metadata['modpack']}")
    print(f"  Versión modpack:   {metadata['modpack_version']}")
    print(f"  Fecha:             {metadata['timestamp']}")
    print(f"  Tamaño:            {metadata['file_size_bytes']} bytes")
    print(f"  SHA-256:           {metadata['sha256']}")

    if rutas["op_pull"] != "s":
        print("PULL cancelado.")
        return

    ruta_destino = Path(pc["ruta_carpeta_saves_pull"]).expanduser()
    ruta_destino.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as directorio_temporal:
        ruta_zip = Path(directorio_temporal) / "latest.zip"

        print("\nDescargando mundo...")
        descargar_zip(s3, configuracion, world_name, ruta_zip)

        print("Verificando SHA-256...")
        sha256 = calcular_sha256(ruta_zip)
        if sha256 != metadata["sha256"]:
            raise ValueError(
                "El SHA-256 del archivo descargado "
                "no coincide con el registrado en metadata.json."
            )

        print("SHA-256 correcto.")
        print("Descomprimiendo mundo...")
        descomprimir_zip(ruta_zip, ruta_destino)

    print("\nPULL completado.")
    print(f"Mundo instalado en: {ruta_destino}")


if __name__ == "__main__":
    main()