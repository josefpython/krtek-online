from flask import Flask, redirect, request, flash, url_for, render_template, send_file
from werkzeug.utils import secure_filename
from os import path, mkdir
import shutil
from misc import namesystem_random


UPLOAD_FOLDER = "./cache/"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
APP_URL = "localhost:5000/"

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["secret_key"] = "sdsajldnasjdjasdjaks"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

open_tunnels = []

@app.route("/")
def main():
    return render_template("new_index.html")

@app.route("/new")
def new():
    new_id = namesystem_random()
    mkdir(path.join(app.config["UPLOAD_FOLDER"], new_id))
    open_tunnels.append(new_id)
    return redirect("/host/"+new_id)

@app.route("/host/<id>")
def host(id):

    qr = APP_URL + "uploadgate/" +id
    dl = APP_URL + "dl/" + id
    dc = APP_URL + "discard/" + id
    
    return render_template("new_tunnel.html", id="'"+qr+"'", tid=id, dl=dl, dc=dc)

@app.route('/uploadgate/<id>', methods=['GET', 'POST'])
def upload_file(id):

    if id in open_tunnels:

        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            files = request.files.getlist("file")
            # If the user does not select a file, the browser submits an
            # empty file without a filename.

            for file in files:

                if file.filename == '':
                    flash('No selected file')
                    return redirect(request.url)

                if file and allowed_file(file.filename):

                    filename = secure_filename(file.filename)
                    file.save(path.join(app.config['UPLOAD_FOLDER'], id+"/"+filename))
            
            return redirect(url_for("success"))

        return render_template("new_submit.html", id=id)
    
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

@app.route("/discard/<id>")
def discard(id):
    if not (id in open_tunnels):
        return redirect("/")
    else:
        try:
            shutil.rmtree("./cache/" + id)
            open_tunnels.remove(id)
            return redirect("/")
        except Exception as e:
            return redirect("/")


if __name__ == "__main__":
    
    try:
        shutil.rmtree("./cache")
    except FileNotFoundError:
        pass
    mkdir("cache")

    app.run(debug=True)