from pathlib import Path
import json
import tempfile
import hashlib
import boto3
import shutil

CONFIG_PATH = (
    Path(__file__).resolve().parent.parent
  / "config"
    / "config.json"
)  


def cargar_configuracion():
    with CONFIG_PATH.open("r", encoding="utf-8") as archivo:
        return json.load(archivo)


def cargar_json(json_path: Path):
    with json_path.open("r", encoding="utf-8") as archivo:
            return json.load(archivo)


def calcular_sha256(ruta_archivo, bloque=1024 * 1024):
    sha256 = hashlib.sha256()

    with ruta_archivo.open("rb") as archivo:
        while bloque_actual := archivo.read(bloque):
            sha256.update(bloque_actual)

    return sha256.hexdigest()


def crear_s3_client(configuracion):
    sesion = boto3.Session(
        profile_name=configuracion["aws_profile"],
        region_name=configuracion["region"]
    )

    return sesion.client("s3")


def crear_zip(carpeta_mundo, ruta_zip):
    shutil.make_archive(
        base_name=str(ruta_zip.with_suffix("")),
        format="zip",
        root_dir=carpeta_mundo.parent,
        base_dir=carpeta_mundo.name
    )


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


def descomprimir_zip(ruta_zip, ruta_destino):
    shutil.unpack_archive(
        str(ruta_zip),
        str(ruta_destino),
        format="zip"
    )


def subir_archivos(s3, configuracion, ruta_zip, metadata):
    bucket = configuracion["bucket_name"]
    prefijo = f"worlds/{metadata['world_name']}"

    clave_zip = f"{prefijo}/{ruta_zip.name}"
    clave_metadata = f"{prefijo}/metadata.json"

    s3.upload_file(
        str(ruta_zip),
        bucket,
        clave_zip,
        ExtraArgs={
            "ContentType": "application/zip"
        }
    )

    s3.put_object(
        Bucket=bucket,
        Key=clave_metadata,
        Body=json.dumps(
            metadata,
            ensure_ascii=False,
            indent=2
        ).encode("utf-8"),
        ContentType="application/json"
    )

    return clave_zip, clave_metadata