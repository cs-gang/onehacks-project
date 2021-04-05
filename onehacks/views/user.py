from sanic import Blueprint
from sanic.exceptions import ServerError
from sanic.request import Request
from sanic.response import html, HTTPResponse, redirect

from onehacks.auth import firebase, User, UnauthenticatedError
from onehacks.forms import LoginForm, SignUpForm
from onehacks.server import app
from onehacks.utils import render_page

user = Blueprint("user", url_prefix="/users")


@user.post("/login")
async def email_login(request: Request) -> HTTPResponse:
    if request.method != "POST":
        raise ServerError(
            "Only POST requests are allowed to this route.", status_code=405
        )
    form = LoginForm(request)

    if form.validate():
        email = form.email.data
        password = form.password.data
        valid = await firebase.authenticate_user(app, email=email, password=password)

        if valid:
            response = redirect("user_dashboard")
            response.cookies["session"] = valid["session_cookie"]
            response.cookies["session"]["httponly"] = True
            response.cookies["session"]["secure"] = True
            response.cookies["session"]["expires"] = valid["expires"]
            return response

        raise UnauthenticatedError("Login failed", status_code=403)
    raise UnauthenticatedError("Form did not validate", status_code=403)


@user.post("/new")
async def email_signup(request: Request) -> HTTPResponse:
    if request.method != "POST":
        raise ServerError(
            "Only POST requests are allowed to this route.", status_code=405
        )

    form = SignUpForm(request)

    if form.validate():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        user = await User.on_firebase(
            app, username=username, email=email, password=password
        )
        url = app.url_for("users.user_dashboard")
        return redirect(url)

    raise UnauthenticatedError("Form did not validate", status_code=403)


@user.post("/logout")
async def user_logout(request: Request) -> HTTPResponse:
    if request.method != "POST":
        raise ServerError(
            "Only POST requests are allowed to this route.", status_code=405
        )

    await firebase.delete_session_cookie(app, request)
    url = app.url_for("index")
    response = redirect(url)
    del response.cookies["session"]

    return response


@user.get("/dashboard")
async def user_dashboard(request: Request) -> HTTPResponse:
    return html("<html><title>sign up worked bro</title></html>")


app.blueprint(user)
