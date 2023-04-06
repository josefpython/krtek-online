from flask import Flask, redirect, request, session, url_for, render_template, send_file
from werkzeug.utils import secure_filename
from os import path, mkdir
import shutil
from misc import namesystem_random


_="""

TODO:

* captcha 
* tunnel persistence with cookies

"""


UPLOAD_FOLDER = "./cache/"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
APP_URL = "http://f54b-31-30-166-249.ngrok.io/"

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = "sdsajsldnasjdjasdjaks"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

open_tunnels = []

@app.route("/")
def main():

    krtinec = False

    try:
        krtinec = session["krtinec"]
    except KeyError:
        pass

    return render_template("new_index.html", e=bool(krtinec), krtinec=krtinec)

@app.route("/new")
def new():

    try:
        
        return redirect(session["krtinec"])
    
    except KeyError:

        new_id = namesystem_random()
        mkdir(path.join(app.config["UPLOAD_FOLDER"], new_id))
        open_tunnels.append(new_id)
        session["krtinec"] = APP_URL+"host/"+new_id
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
                e = 'No file part'
                return redirect(url_for("upload_file", id=id, state=e))
            files = request.files.getlist("file")
            # If the user does not select a file, the browser submits an
            # empty file without a filename.

            for file in files:

                if file.filename == '':
                    e = 'No selected file'
                    return redirect(url_for("upload_file", id=id, state=e))

                if file and allowed_file(file.filename):

                    filename = secure_filename(file.filename)
                    file.save(path.join(app.config['UPLOAD_FOLDER'], id+"/"+filename))
            
            return redirect(url_for("upload_file", id=id, state="w"))

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
    try:
        session.pop("krtinec", default=None)
    except Exception:
        pass
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