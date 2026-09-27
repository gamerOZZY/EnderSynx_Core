import hashlib
import json
import shutil
import tempfile
from pathlib import Path

import boto3

from checkFiles import obtener_metadata

## Ruta de configuracion lol
CONFIG_PATH = (
    Path(__file__).resolve().parent.parent
    / "config"
    / "config.json"
)

## Cargar los datos de la configuracion en memoria
def cargar_configuracion():
    with CONFIG_PATH.open("r", encoding="utf-8") as archivo:
        return json.load(archivo)


## SHA256 para la encriptacion de los archivos (aunque solo son mundos de minecraft,
## termina siendo una buena practica)
def calcular_sha256(ruta_archivo, bloque=1024 * 1024):
    sha256 = hashlib.sha256()

    with ruta_archivo.open("rb") as archivo:
        while bloque_actual := archivo.read(bloque):
            sha256.update(bloque_actual)

    return sha256.hexdigest()

## Conexion con S3
def crear_s3_client(configuracion):
    sesion = boto3.Session(
        profile_name=configuracion["aws_profile"],
        region_name=configuracion["region"]
    )

    return sesion.client("s3")

## descarga el archivo zip del bucket s3
def descargar_zip(
    s3,
    configuracion,
    world_name,
    ruta_zip
):
    bucket = configuracion["bucket_name"]
    clave_zip = f"worlds/{world_name}/latest.zip"

    s3.download_file(
        bucket,
        clave_zip,
        str(ruta_zip)
    )


## Toma la ruta donde se descargo el archivo zip y lo descomprime aih mismo
def descomprimir_zip(ruta_zip, ruta_destino):
    shutil.unpack_archive(
        str(ruta_zip),
        str(ruta_destino),
        format="zip"
    )


def main():
    configuracion = cargar_configuracion()

    world_name = input(
        "Nombre del mundo a descargar: "
    ).strip()

    print("\nConsultando información del mundo...")

    s3 = crear_s3_client(configuracion)

    metadata = obtener_metadata(
        s3,
        configuracion,
        world_name
    )

    print("\nMundo encontrado:")
    print(f"  Mundo:             {metadata['world_name']}")
    print(f"  Minecraft:         {metadata['minecraft_version']}")
    print(f"  Modpack:           {metadata['modpack']}")
    print(f"  Versión modpack:   {metadata['modpack_version']}")
    print(f"  Fecha:             {metadata['timestamp']}")
    print(f"  Tamaño:            {metadata['file_size_bytes']} bytes")
    print(f"  SHA-256:           {metadata['sha256']}")

    confirmacion = input(
        "\n¿Descargar este mundo? [s/N]: "
    ).strip().lower()

    if confirmacion != "s":
        print("PULL cancelado.")
        return

    ruta_destino = Path(
        input(
            "\nRuta de la carpeta 'saves': "
        )
    ).expanduser().resolve()

    ruta_destino.mkdir(
        parents=True,
        exist_ok=True
    )

    with tempfile.TemporaryDirectory() as directorio_temporal:
        ruta_zip = Path(directorio_temporal) / "latest.zip"

        print("\nDescargando mundo...")
        descargar_zip(
            s3,
            configuracion,
            world_name,
            ruta_zip
        )

        print("Verificando SHA-256...")
        sha256 = calcular_sha256(ruta_zip)

        if sha256 != metadata["sha256"]:
            raise ValueError(
                "El SHA-256 del archivo descargado "
                "no coincide con el registrado en metadata.json."
            )

        print("SHA-256 correcto.")

        print("Descomprimiendo mundo...")
        descomprimir_zip(
            ruta_zip,
            ruta_destino
        )

    print("\nPULL completado.")
    print(f"Mundo instalado en: {ruta_destino}")


if __name__ == "__main__":
    main()