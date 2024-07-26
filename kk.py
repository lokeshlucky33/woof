from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
#from detect_faces import detect_faces_with_labels  # Replace with your module name
import os
import boto3
app = Flask(__name__)

def detect_faces_with_labels(image_path, project_version_arn):
    aws_access_key_id = 'AKIAW3MECWXHQ6DHQ4UG'
    aws_secret_access_key = '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'
    region_name = 'us-east-1'
    
    # Create a Rekognition client
    client = boto3.client('rekognition', 
                          aws_access_key_id=aws_access_key_id,
                          aws_secret_access_key=aws_secret_access_key,
                          region_name=region_name)

    # Load image bytes
    with open(image_path, 'rb') as image_file:
        image_bytes = image_file.read()

    # Call Amazon Rekognition to detect faces in the image
    response = client.detect_custom_labels(
        ProjectVersionArn=project_version_arn,
        Image={'Bytes': image_bytes}
    )

    # Process the response and return relevant information
    detected_labels = []
    if 'CustomLabels' in response:
        for label in response['CustomLabels']:
            name = label['Name']
            confidence = label['Confidence']
            detected_labels.append({'name': name, 'confidence': confidence})

    return detected_labels

# Define a folder to store uploaded images temporarily
UPLOAD_FOLDER = '/tmp/uploads'  # Example path
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your_secret_key'  # Change this to a secure random key

# Function to check if the file type is allowed
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Define your route for the homepage
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']

        # If user does not select file, browser also submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # Securely save the uploaded file
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Your custom project version ARN
            project_version_arn = 'arn:aws:rekognition:us-east-1:471112791503:project/woof/version/woof.2024-07-23T15.22.58/1721728378513'

            # Call the function to detect faces with labels
            detected_labels = detect_faces_with_labels(filepath, project_version_arn)

            # Render the results in index.html
            return render_template('index.html', detected_labels=detected_labels)

    # If GET request or invalid file type, render the initial form
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
