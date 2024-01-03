from flask import Flask, render_template, request, send_file
import requests, json, os, time, pytz
from datetime import datetime
from reportlab.pdfgen import canvas
from io import BytesIO

app = Flask(__name__, template_folder="views")


def createpdf(dict):
    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    p.drawString(100, 750, "details")
    p.drawString(100, 700, f"username: {dict['username']}")
    p.drawString(100, 650, f"range: {dict['range']}")
    p.drawString(100, 600, f"time: {dict['time']}")
    p.drawString(100, 550, f"date: {dict['date']}")

    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer


@app.route("/", methods=["GET", "POST"])
def UserLogin():
    if request.method == "GET":
        return render_template("UserLogin.html")
    elif request.method == "POST":
        data = {
            "username": request.form["username"],
            "UserLogintime": time.mktime(datetime.now().timetuple()),
        }
        try:
            with open("creds.json", "r") as f:
                creds = json.load(f)

            usermatches = [
                x
                for x in creds
                if (
                    x["username"] == data["username"]
                    and x["password"] == request.form["password"]
                )
            ]
            match = usermatches[0] if len(usermatches) > 0 else None

            if not match:
                return render_template("UserLogin.html")
        except Exception as e:
            return render_template("UserLogin.html")

        return render_template(
            "print.html",
            data=match,
            href="/pdf?"
            + "&".join([x + "=" + match[x] for x in match if x != "password"]),
        )


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        data = {
            "username": request.form["username"],
            "password": request.form["password"],
            "date": request.form["date"],
            "time": request.form["time"],
            "range": request.form["range"],
        }
        if os.path.isfile("creds.json"):
            with open("creds.json", "r") as f:
                try:
                    creds = json.load(f)
                except:
                    creds = []
                finally:
                    creds.append(data)
                    with open("creds.json", "w") as f:
                        json.dump(creds, f, indent=4)
        else:
            with open("creds.json", "w") as f:
                json.dump([data], f, indent=4)
        return render_template("UserLogin.html")


@app.route("/pdf")
def pdf():
    return send_file(
        createpdf(dict(request.args)), as_attachment=True, download_name="details.pdf"
    )


if __name__ == "__main__":
    app.run()
