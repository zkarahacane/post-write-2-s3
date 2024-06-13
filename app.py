from flask import Flask, request, jsonify, Blueprint
import boto3
import os
from datetime import datetime
import mimetypes
import logging

app = Flask(__name__)

# Configurer le logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS S3 Configuration
S3_BUCKET = os.getenv("S3_BUCKET")
S3_KEY = os.getenv("S3_ACCESS_KEY_ID")
S3_SECRET = os.getenv("S3_SECRET_ACCESS_KEY")
S3_REGION = os.getenv("S3_REGION")
S3_ENDPOINTURL = os.getenv("S3_URL")
S3_FOLDER = os.getenv("S3_FOLDER")
s3 = boto3.client(
    "s3",
    aws_access_key_id=S3_KEY,
    aws_secret_access_key=S3_SECRET,
    region_name=S3_REGION,
    endpoint_url=S3_ENDPOINTURL,
)

health_check_bp = Blueprint('health_check', __name__)

@health_check_bp.route('/health')
def health_check():
    # Check database connectivity, pings, roundtrip request timings, etc
    # Return a JSON response with a status code of 200 if the application is healthy
    # Return a status code of 500 along with an error message if there are any issues
    return jsonify({'status': 'ok'}), 200


@app.route('/ODFClient', methods=['POST'])
def upload_content():
    logger.info("ODFClient upload called")
    if not request.data:
        logger.error("No content in the request")
        return jsonify({'error': 'No content in the request'}), 400
    
    content = request.data
    content_type = request.headers.get('Content-Type')
    extension = mimetypes.guess_extension(content_type)
    
    if not extension:
        logger.error("Unsupported file type: %s", content_type)
        return jsonify({'error': 'Unsupported file type'}), 400
    
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f"/{S3_FOLDER}/odfclient/{current_time}_odf{extension}"
    
    try:
        s3.put_object(Bucket=S3_BUCKET, Key=file_name, Body=content, ContentType=content_type)
        logger.info("Content uploaded successfully: %s", file_name)
        return jsonify({'message': 'Content uploaded successfully', 'file_name': file_name}), 200
    except Exception as e:
        logger.error("Error uploading content: %s", str(e))
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)