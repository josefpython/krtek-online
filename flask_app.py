from flask import Flask, redirect, request, flash, url_for, render_template, send_file
from uuid import uuid4
from werkzeug.utils import secure_filename
from os import path, mkdir
import shutil


UPLOAD_FOLDER = "./cache/"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
APP_URL = "localhost:5000/"

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

open_tunnels = []

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/new")
def new():
    new_id = str(uuid4())
    mkdir(path.join(app.config["UPLOAD_FOLDER"], new_id))
    open_tunnels.append(new_id)
    return redirect("/host/"+new_id)

@app.route("/host/<id>")
def host(id):

    qr = APP_URL + "uploadgate/" +id
    dl = APP_URL + "dl/" + id
    
    return render_template("tunnel.html", id="'"+qr+"'", tid=id, dl=dl)

@app.route('/uploadgate/<id>', methods=['GET', 'POST'])
def upload_file(id):

    if id in open_tunnels:

        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(path.join(app.config['UPLOAD_FOLDER'], id+"/"+filename))
                return redirect(url_for("success"))
        return '''    
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form method=post enctype=multipart/form-data>
        <input type=file name=file>
        <input type=submit value=Upload>
        </form>
        '''
    
    else:
        return "Invalid gate id."

@app.route("/success")
def success():
    return "Files uploaded."

@app.route("/dl/<id>")
def download(id):
    if id in open_tunnels:
        output_filename = path.join(app.config["UPLOAD_FOLDER"], "zipd/"+id)
        dir_name = path.join(app.config["UPLOAD_FOLDER"], id)
        shutil.make_archive(output_filename, 'zip', dir_name)
        return send_file(output_filename+".zip")
    else:
        return "No."

if __name__ == "__main__":
    
    try:
        shutil.rmtree("./cache")
    except FileNotFoundError:
        pass
    mkdir("cache")

    app.run(host="0.0.0.0")