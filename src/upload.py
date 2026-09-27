import hashlib
import json
import shutil
import tempfile
from pathlib import Path
import boto3
from metadata import create_metadata

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "config.json"


def cargar_configuracion():
    with CONFIG_PATH.open("r", encoding="utf-8") as archivo:
        return json.load(archivo)


def calcular_sha256(ruta_archivo, bloque=1024 * 1024):
    sha256 = hashlib.sha256()

    with ruta_archivo.open("rb") as archivo:
        while bloque_actual := archivo.read(bloque):
            sha256.update(bloque_actual)

    return sha256.hexdigest()


def crear_zip(carpeta_mundo, ruta_zip):
    shutil.make_archive(
        base_name=str(ruta_zip.with_suffix("")),
        format="zip",
        root_dir=carpeta_mundo.parent,
        base_dir=carpeta_mundo.name
    )


def crear_s3_client(configuracion):
    sesion = boto3.Session(
        profile_name=configuracion["aws_profile"],
        region_name=configuracion["region"]
    )

    return sesion.client("s3")


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


def main():
    configuracion = cargar_configuracion()

    carpeta_mundo = Path(
        input("Ruta de la carpeta del mundo: ")
    ).expanduser().resolve()

    if not carpeta_mundo.is_dir():
        raise ValueError(
            f"La carpeta no existe: {carpeta_mundo}"
        )

    with tempfile.TemporaryDirectory() as directorio_temporal:
        ruta_zip = Path(directorio_temporal) / "latest.zip"

        print("Creando ZIP...")
        crear_zip(carpeta_mundo, ruta_zip)

        print("Calculando SHA-256...")
        sha256 = calcular_sha256(ruta_zip)

        metadata = create_metadata(ruta_zip)
        metadata["sha256"] = sha256

        print("Conectando con S3...")
        s3 = crear_s3_client(configuracion)

        print("Subiendo archivos...")
        claves = subir_archivos(
            s3,
            configuracion,
            ruta_zip,
            metadata
        )

        print("\nPUSH completado.")
        print(f"ZIP:      s3://{configuracion['bucket_name']}/{claves[0]}")
        print(f"Metadata: s3://{configuracion['bucket_name']}/{claves[1]}")
        print(f"SHA-256:  {sha256}")


if __name__ == "__main__":
    main()
