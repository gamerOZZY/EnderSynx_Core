import json


def obtener_metadata(s3, configuracion, world_name):
    bucket = configuracion["bucket_name"]
    clave_metadata = f"worlds/{world_name}/metadata.json"

    respuesta = s3.get_object(
        Bucket=bucket,
        Key=clave_metadata
    )

    contenido = respuesta["Body"].read().decode("utf-8")

    return json.loads(contenido)