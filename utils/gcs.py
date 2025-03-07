from google.cloud import storage
import os

def upload_to_gcs(bucket_name, source_file_path, destination_blob_name):
    """Upload a file to Google Cloud Storage."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_path)
    return f'gs://{bucket_name}/{destination_blob_name}'

def upload_directory_to_gcs(bucket_name, source_dir, destination_prefix=''):
    """Upload all files in a directory to GCS."""
    uploaded_files = []
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                source_path = os.path.join(root, file)
                relative_path = os.path.relpath(source_path, source_dir)
                destination_path = os.path.join(destination_prefix, relative_path)
                gcs_uri = upload_to_gcs(bucket_name, source_path, destination_path)
                uploaded_files.append(gcs_uri)
    return uploaded_files