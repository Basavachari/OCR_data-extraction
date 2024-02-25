from flask import Flask, render_template, request, redirect
import os
from script import process_image  
import json
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def upload_form():
    return render_template('sample2.html')

@app.route('/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        data = process_image(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # data = json.dumps(data)
        if isinstance(data, list):
            print("data is a list")
            return render_template('sample2.html', data=data)
        else:
            print("data is not a list")
            # Handle error case when data is not a list
            return "Error: Data format mismatch"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
