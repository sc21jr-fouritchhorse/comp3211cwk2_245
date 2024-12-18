from extensions import celery, Session, session_factory
import requests
import os

@celery.task
def process_image_upload(image_upload_id):
    from app import create_app
    from models import ImageUpload, db

    app = create_app()
    
    with app.app_context():
        session_factory.configure(bind=db.engine)
        session = Session()

        try:
            image_upload = session.query(ImageUpload).get(image_upload_id)
            if not image_upload:
                return False
            
            with open(image_upload.temp_file_path, 'rb') as f:
                thumbnail_response = requests.post(
                    'https://comp3211cwkthumbnail.azurewebsites.net/api/GetThumbnail',
                    files={'image': f}
                )
            
            if thumbnail_response.status_code == 200:
                thumbnail_url = thumbnail_response.text.strip()
                image_upload.thumbnail_url = thumbnail_url
                session.commit()
                
                caption_response = requests.post(
                    'https://comp3211cwkthumbnail.azurewebsites.net/api/GetCaption',
                    json={'url': thumbnail_url},
                    timeout=600 
                )
                
                if caption_response.status_code == 200:
                    image_upload.caption = caption_response.text.strip()
                    session.commit()
                    return True
            
            return False
        
        except Exception as e:
            print(f"Error processing image upload: {e}")
            return False
        finally:
            Session.remove()