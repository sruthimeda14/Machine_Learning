from os import makedirs, path
import sys
import json
import time
import logging

import boto3
from fastapi import FastAPI, Request, Response
from fastapi import FastAPI, UploadFile

import shutil
import uvicorn
import urllib.request
from pathlib import Path
from inference import predict

def load_json_file(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    return data



# PATH = os.path.cwd()
def save_upload_file_tmp(upload_file: UploadFile, filename) -> Path:
    try:
        with open(filename, 'wb') as tmp:
            shutil.copyfileobj(upload_file.file, tmp)
            tmp_path = Path(tmp.name)
    finally:
        upload_file.file.close()
    return tmp_path

def download_video(s3_bucket_link):
    filename = s3_bucket_link.split('/')[-1]
    file_path = path.join("downloads", filename)
    if not path.exists(file_path):
        urllib.request.urlretrieve(s3_bucket_link, file_path)
    return filename, file_path

from botocore.exceptions import NoCredentialsError
def upload_file_to_s3(file_path, bucket_name):
    s3 = boto3.client('s3')
    file_name = file_path.split('/')[-1]

    # Upload the file to S3 bucket
    try:
        s3.upload_file(file_path, bucket_name, file_name)
        # Generate the HTTP link for the uploaded file
        file_url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
        return file_url
    except NoCredentialsError:
        return "AWS credentials not found. Ensure you have set up your AWS credentials properly."
    except Exception as e:
        return str(e)    


bucket_name = "manual-handling-processed-v1"
# Logging setup
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = FastAPI()

@app.get("/ping")
def ping_check():
    logger.info("PING!")
    return Response(content=json.dumps({"ping_status": "ok"}), status_code=200)

@app.post('/invocations')
@app.put('/invocations')
async def handler(req: Request):
    tic = time.time()
    output_folder = "api_results"
    try:
        url=""
        video_info = await req.json()
        if not isinstance(video_info, dict):
            video_info = json.loads(video_info)
        if not video_info["ProcessedVideoURL"]:
            print(f"video {video_info['Id']} is not processed.")
            makedirs("downloads", exist_ok=True)
            videoname, video_path = download_video(video_info["UnProcessedVideoURL"])
            
            print('Predicting...')
            try:
                predict(video_path, output_folder)
                print('Done')
            except Exception as e:
                return e
            url = "upload skipped"
            # url = upload_file_to_s3(video_path,bucket_name)
        time_taken = f'{time.time() - tic:.4f}'
        return Response(status_code=200, content=json.dumps({"url": url,
                                                             'time_taken': time_taken}))
    except Exception as e:
        time_taken = f'{time.time() - tic:.4f}'
        return Response(status_code=200, content=json.dumps({"error": f"{e}",
                                                             'time_taken': time_taken}))

if __name__=='__main__':
    uvicorn.run('app:app', host='0.0.0.0', port=8080, reload=False)