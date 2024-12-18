from datetime import datetime, timedelta
import json
import logging
import os
import uuid
from io import BytesIO
import requests
import azure.functions as func
from azure.storage.blob import BlobServiceClient, ContentSettings
from PIL import Image
import moondream

app = func.FunctionApp()

@app.route(route="GetThumbnail", auth_level=func.AuthLevel.ANONYMOUS)
def GetThumbnail(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Processing request to resize image and upload to Azure Blob Storage.")
    start_time = datetime.now()
    try:
        image_file = req.files.get('image')
        if not image_file:
            return func.HttpResponse("Image file is missing.", status_code=400)

        image = Image.open(image_file)
        image = image.resize((512, 512))

        elapsed_time = (datetime.now() - start_time).total_seconds()
        logging.info(f"Time to resize image: {elapsed_time:.2f} seconds!")
        start_time = datetime.now()

        img_byte_arr = BytesIO()
        image_format = image.format if image.format else "JPEG"
        image.save(img_byte_arr, format=image_format)
        img_byte_arr.seek(0)

        blob_connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        container_name = os.getenv('AZURE_CONTAINER_NAME')
        if not blob_connection_string or not container_name:
            return func.HttpResponse("Azure Storage configuration is missing.", status_code=500)

        img_id = uuid.uuid4()
        unique_img_name = f"{img_id}__{image_file.filename}"

        blob_service_client = BlobServiceClient.from_connection_string(blob_connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=unique_img_name)

        blob_client.upload_blob(
            img_byte_arr,
            overwrite=True,
            content_settings=ContentSettings(content_type=f'image/{image_format.lower()}')
        )

        blob_url = f"{blob_service_client.primary_endpoint}{container_name}/{unique_img_name}"

        elapsed_time = (datetime.now() - start_time).total_seconds()
        logging.info(f"Time to upload image: {elapsed_time:.2f} seconds!")

        return func.HttpResponse(blob_url+"\n", status_code=200)

    except Exception as e:
        logging.error(f"Error processing the request: {e}")
        return func.HttpResponse(f"An error occurred: {str(e)}\n", status_code=500)

@app.route(route="GetCaption", auth_level=func.AuthLevel.ANONYMOUS)
def GetCaption(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Processing request to generate caption from image URL.")
    start_time = datetime.now()
    try:
        url = req.params.get('url')
        if not url:
            try:
                req_body = req.get_json()
                url = req_body.get('url')
            except ValueError:
                pass

        if not url:
            return func.HttpResponse("URL parameter is missing.", status_code=400)

        elapsed_time = (datetime.now() - start_time).total_seconds()
        logging.info(f"Received URL: {url}. Time taken: {elapsed_time:.2f} seconds!")
        start_time = datetime.now()

        model = moondream.vl(model=os.path.join(os.path.dirname(__file__), 'moondream-0_5b-int4.mf')) 
        im = Image.open(requests.get(url, stream=True).raw)
        encoded_img = model.encode_image(im)
        caption = model.caption(encoded_img)["caption"]

        elapsed_time = (datetime.now() - start_time).total_seconds()
        logging.info(f"Generated caption: {caption}. Time taken: {elapsed_time:.2f} seconds!")

        return func.HttpResponse(f"{caption}", status_code=200)

    except Exception as e:
        logging.error(f"Error processing the request: {e}")
        return func.HttpResponse(f"An error occurred: {str(e)}\n", status_code=500)