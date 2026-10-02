import tempfile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.metadata import create_metadata
from src.utils import calcular_sha256
from src.utils import cargar_configuracion
from src.utils import cargar_json
from src.utils import crear_s3_client
from src.utils import crear_zip
from src.utils import subir_archivos



rutas_devices = (
    Path(__file__).resolve().parent.parent
    / "config"
    / "rutes_config.json"
)


def main():
    configuracion = cargar_configuracion()
    rutas = cargar_json(rutas_devices)
    carpeta_mundo = Path(
        rutas["pc"]["ruta_carpeta_mundo_upload"]
    ).expanduser()

    if not carpeta_mundo.is_dir():
        raise ValueError(f"La carpeta no existe: {carpeta_mundo}")

    with tempfile.TemporaryDirectory() as directorio_temporal:
        ruta_zip = Path(directorio_temporal) / "latest.zip"

        print("Creando ZIP...")
        crear_zip(carpeta_mundo, ruta_zip)

        print("Calculando SHA-256...")
        sha256 = calcular_sha256(ruta_zip)

        metadata = create_metadata(ruta_zip)
        metadata["world_name"] = carpeta_mundo.name
        metadata["sha256"] = sha256

        print("Conectando con S3...")
        s3 = crear_s3_client(configuracion)

        print("Subiendo archivos...")
        claves = subir_archivos(
            s3,
            configuracion,
            ruta_zip,
            metadata,
        )

        print("\nPUSH completado.")
        print(f"ZIP:      s3://{configuracion['bucket_name']}/{claves[0]}")
        print(f"Metadata: s3://{configuracion['bucket_name']}/{claves[1]}")
        print(f"SHA-256:  {sha256}")


if __name__ == "__main__":
    main()