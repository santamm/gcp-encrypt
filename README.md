# gcp-encrypt
Encryption and decryption GCP APIs


### Table of Contents

1. [Installation](#installation)
2. [Project Description](#description)
4. [File Descriptions](#files)
6. [Licensing, Authors, and Acknowledgements](#licensing)

## Installation <a name="installation"></a>
The code in this project is written in Python 3.7.6).
The following additional libraries have been used:
* pandas
* google-cloud
* pandas-gbq
* google-cloud-storage
* google-cloud-bigquery
* gcsfs
* pycrypto


To deploy the API into GCP using cloud SDK run the following:

gcloud functions deploy gcp-encrypt \
--runtime python37 \
--trigger-resource YOUR_TRIGGER_BUCKET_NAME \
--trigger-event google.storage.object.finalize



## Project Description<a name="description"></a>
gcp-encrypt loads a csv file from a GCP bucket, encrypts some columns using SHA-256 encryption. A `enc.csv` is stored in another bucket with the encrypted columns replacing the clear ones.
The API is deployed to GCP as a Cloud Function.


## File Descriptions <a name="files"></a>
* requirements.txt
* main.py
* env.yaml
* key.json



## Licensing, Authors, Acknowledgements<a name="licensing"></a>
For licensing see LICENSE file.
