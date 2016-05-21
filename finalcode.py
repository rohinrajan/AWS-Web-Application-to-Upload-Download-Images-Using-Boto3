from flask import Flask
from flask import render_template
from flask import request
import boto3
import botocore
import os

app = Flask(__name__, static_url_path='/temp', static_folder='temp')

BUCKET_NAME = 'cloudassignmentbucket3'

s3= boto3.resource('s3',
                 aws_access_key_id='AKIAICB2IHGJKZLKANGQ',
                 aws_secret_access_key='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')

bucket = s3.Bucket(BUCKET_NAME)
exists = True
try:
    s3.meta.client.head_bucket(Bucket=BUCKET_NAME)
except botocore.exceptions.ClientError as e:
    # If a client error is thrown, then check that it was a 404 error.
    # If it was a 404 error, then the bucket does not exist.
    error_code = int(e.response['Error']['Code'])
    if error_code == 404:
        exists = False

@app.route('/')
def startapp():
    return render_template('login.html')


def check_credentials(lgname):
        with open ('names.txt','rb') as fileobj:
                names = fileobj.read().split('\n')
                for name in names:
                        if name == lgname:
                                return True
                return False


@app.route('/login', methods=['GET','POST'])
def login():
   if request.method == 'POST':
        lgname = request.form['username']
        if check_credentials(lgname):
            val = []
            # iterate through the bucket and get the list of files that are stored in the bucket
            for objects in bucket.objects.all():
               val.append(objects.key)
            # method to call the index.html file and passing the contents to the file
            return render_template('index.html',content=val)
        else:
            return "Invalid credentials"



@app.route('/upload', methods=['GET','POST'])
def submit_click():
 #  try:
    if request.method == 'POST':
        fileobj = request.files['file']
        fcontent = fileobj.read()
        #return fcontent
        pathloc = os.path.join('upload', fileobj.filename)
        with open(pathloc,'wb') as flobj:
                flobj.write(fcontent)
                flobj.close()
        bucket.upload_file(pathloc,fileobj.filename,ExtraArgs={'ACL':'public-read'})
        # delete the file
        os.unlink(pathloc)
        #bucket.put_object(Key=fileobj.filename, Body=fcontent, ExtraArgs={'ACL':'public-read'})
        return "Success"
#   except Exception as e:
#       return 'Failure'


@app.route('/deleted', methods=['GET','POST'])
def delete_click():
        if request.method == 'POST':
                filename = request.form['del_filename'] 
                for objects in bucket.objects.all():
                        if objects.key == filename:
                                objects.delete()
                                return 'File Deleted'
        return 'No File Found'

@app.route('/download', methods=['GET','POST'])
def download_file():
        if request.method == 'POST':
                filename = request.form['dwn_filename']
                downloadloc =  'temp/' + filename
                bucket.download_file(Key=filename,Filename=downloadloc)
                return render_template('download.html',filename=filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
