import pandas as pd

from google.cloud import bigquery
from google.cloud import storage
import gcsfs

import os
import json

from Crypto.Cipher import AES
from Crypto.Util import Counter
from Crypto import Random
import binascii
import urllib.parse
import base64
import hashlib

gcp_project = os.getenv('gcp_project')
gcp_credentials = os.getenv('gcp_credentials')
from_bucket = os.getenv('from_bucket')
dest_bucket = os.getenv('dest_bucket')

BS = 32

key="IAaashhrakklab8885$%^&*)))"
_key_ = hashlib.md5(key.encode()).hexdigest()[:BS]


# PKCS5 paddig bytes instead of text (To work with Arabic)
b_pad = lambda b: b + (BS - len(b) % BS) * chr(BS - len(b) % BS).encode('utf-8')
b_unpad = lambda b : b[0:-ord(chr(b[-1]))]

class Crypt:
    """
    AES 256 Encryption/Decryption
    
    """
    def __init__(self, key):
        self.key = key

    def encrypt(self, raw):
        
        
        raw = raw.encode('utf-8')
        raw = b_pad(raw)
        #raw = base64.b64encode(raw)
        iv = Random.new().read(AES.block_size)
        
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        encrypted = binascii.hexlify(iv+cipher.encrypt(raw))
        #encrypted_text = (iv+cipher.encrypt(raw)).hex()
        return encrypted.decode('utf-8') #.upper()


    def decrypt(self, enc):
        """
        Requires hex encoded param to decrypt, assumes iv first 16 bytes of Ciphertext
        """
        enc = binascii.unhexlify(enc)
        #enc = bytearray.fromhex(enc)
        iv = enc[:AES.block_size]
        enc= enc[AES.block_size:]
        #print(len(enc), len(iv))
        
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypt = cipher.decrypt(enc)
        #decrypt = base64.b64decode(decrypt)
        unpadded = b_unpad(decrypt)
        decrypted_text = unpadded.decode('utf-8')
        
        return decrypted_text
    
def load_from_gcp(project, bucket, file):
    """
    Load file from GCP bucket into a pandas dataframe
    
    """
    df=pd.DataFrame()
    path = "gs://"+bucket+"/"+file
    fs = gcsfs.GCSFileSystem(project=project, token=gcp_credentials)
    with fs.open(path) as f:
        df = pd.read_csv(f)
    return df

def save_to_gcp(df, project, bucket, file):
    """
    Save df to GCP path
    """
    path = "gs://"+bucket+"/"+file
    fs = gcsfs.GCSFileSystem(project=project, token=gcp_credentials)
    with fs.open(path, "w") as f:
        df.to_csv(f)


def encrypt_column(df, col, key, suffix='_enc'):
    """
    Encrypt a column in the pandas dataframe and add new encrypted column
    
    """
    cipher = Crypt(key)
    df[col+suffix] = df[col].apply(lambda c: cipher.encrypt(c))
    return df

def decrypt_column(df, col, key, suffix='_dec'):
    """
    Decrypt a column from pandas dataframe and add new decrypted column
    """
    cipher = Crypt(key)
    df[col+suffix] = df[col].apply(lambda c: cipher.decrypt(c))
    return df



def encrypt_from_bucket(event, context):

    """
    Read file from src bucket
    Encrypts sensitive data
    Write on destination bucket
    
    Background Cloud Function to be triggered by Cloud Storage.
       This generic function logs relevant data when a file is changed.

    Args:
        event (dict):  The dictionary with data specific to this type of event.
                       The `data` field contains a description of the event in
                       the Cloud Storage `object` format described here:
                       https://cloud.google.com/storage/docs/json_api/v1/objects#resource
        context (google.cloud.functions.Context): Metadata of triggering event.
    Returns:
        None; the output is written to Stackdriver Logging
    """

    print('Event ID: {}'.format(context.event_id))
    print('Event type: {}'.format(context.event_type))
    print('Bucket: {}'.format(event['bucket']))
    print('File: {}'.format(event['name']))
    print('Metageneration: {}'.format(event['metageneration']))
    print('Created: {}'.format(event['timeCreated']))
    print('Updated: {}'.format(event['updated']))
    
    
    file=event['name']
    root, ext = os.path.splitext(file)
    df = load_from_gcp(gcp_project, from_bucket, file)
    col='string_value'
    if not df.empty:
        dfe = encrypt_column(df, col, _key_)
        dfe.drop(col, axis=1, inplace=True)
        dest_file = root+"_enc.csv"
        save_to_gcp(dfe, gcp_project, dest_bucket, dest_file)
    
    return


#if __name__ == "__main__":
#	main()



