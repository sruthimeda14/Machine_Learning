# Pose Analysis
Does pose analysis on human focus hfi videos. Detect good bend, bad bend and twist
## Setup
Create a python environment and install requirements
```bash
python3 -m venv .env
source .env/bin/activate
pip install -r requirements.txt
```
## Inference
Only on 1 image
```bash
python3 main.py -v path/to/video
```
On all the mp4 videos in a directory, use the following command:
```bash
./inference.sh path/to/dir
```
## Training
- `-b` is used to enable bootstraper
- `-r` is used to remove the outlier example in dataset, optional argument
```bash
python3 main.py -ds path/to/dataset -r
```
