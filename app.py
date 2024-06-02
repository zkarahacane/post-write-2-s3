from flask import Flask, request, jsonify
import boto3
import os
from datetime import datetime
import mimetypes
app = Flask(__name__)

# AWS S3 Configuration
S3_BUCKET = os.getenv("S3_BUCKET")
S3_KEY = os.getenv("S3_ACCESS_KEY_ID")
S3_SECRET = os.getenv("S3_SECRET_ACCESS_KEY")
S3_REGION = os.getenv("S3_REGION")
S3_ENDPOINTURL = os.getenv("S3_URL")

s3 = boto3.client(
    "s3",
    aws_access_key_id=S3_KEY,
    aws_secret_access_key=S3_SECRET,
    region_name=S3_REGION,
    endpoint_url=S3_ENDPOINTURL
)

@app.route('/ODFClient', methods=['POST'])
def upload_content():
    if not request.data:
        return jsonify({'error': 'No content in the request'}), 400
    
    content = request.data
    content_type = request.headers.get('Content-Type')
    extension = mimetypes.guess_extension(content_type)
    
    if not extension:
        return jsonify({'error': 'Unsupported file type'}), 400
    
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f"odfclient/{current_time}_odf{extension}"
    
    try:
        s3.put_object(Bucket=S3_BUCKET, Key=file_name, Body=content, ContentType=content_type)
        return jsonify({'message': 'Content uploaded successfully', 'file_name': file_name}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)