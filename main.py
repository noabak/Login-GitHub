from flask import Flask, render_template, make_response,redirect, request, url_for
from requests_oauthlib import OAuth2Session
import os, json

try:
    import secrets  # only needed for localhost, that's why it's in the try/except statement
except ImportError as e:
    pass

app = Flask(__name__)


@app.route("/")
def index():

        return render_template("index.html")


@app.route("/profile")
def profile():
    state =request.cookies.get("oauth_state")
    if state:
       github= OAuth2Session(os.environ.get("GITHUB_CLIENT_ID"),
                          token=json.loads(request.cookies.get("oauth_token")))
       github_profile_data= github.get('https://api.github.com/user').json()
    else:
       message= "Please log in first to have access to your profile data!"
       return render_template("result.html", message=message)

    return render_template("profile.html", github_profile_data= github_profile_data)

@app.route("/github/login")
def github_login():
    # prepare the Github OAuth session
    github= OAuth2Session(os.environ.get("GITHUB_CLIENT_ID"))
    # Github authorization url
    authorization_url, state = github.authorization_url("https://github.com/login/oauth/authorize")

    # redirect user to Github for authorization
    response =  make_response(redirect(authorization_url))
    # for CSRF purposes
    response.set_cookie("oauth_state", state, httponly=True)

    return response

@app.route("/github/callback")
def github_callback():
    github = OAuth2Session(os.environ.get("GITHUB_CLIENT_ID"), state=request.cookies.get("oauth_state"))
    token = github.fetch_token("https://github.com/login/oauth/access_token",
                               client_secret=os.environ.get("GITHUB_CLIENT_SECRET"),
                               authorization_response=request.url)

    response = make_response(redirect(url_for('profile')))  # redirect to the profile page
    response.set_cookie("oauth_token", json.dumps(token), httponly=True)

    return response

@app.route("/github/logout")
def logout():
    message_bye="Bye, see you again!"
    response =  make_response((redirect(url_for('index'))))
    #delete the oauth cookie to logout
    response.set_cookie("oauth_token","")
    response.set_cookie("oauth_state","")
    response.set_cookie("message_bye", message_bye)

    return response




if __name__ == '__main__':
    app.run(port="5001")