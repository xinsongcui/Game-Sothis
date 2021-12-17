"""
Import necessary modules.
  - `os` to read env variable
  - `requests` to make GET/POST requests
  - `parse_qs` to parse the response
"""
import os
import requests
from urllib.parse import parse_qs


"""
Define the GITHUB_ID and GITHUB_SECRET environment variables
along with the endpoints.
"""
CLIENT_ID = "0225fdee833e3336e259"
CLIENT_SECRET = "daf58d3ed3b618f172843057773a1a949c8d24cf"
AUTHORIZATION_ENDPOINT = f"https://github.com/login/oauth/authorize?response_type=code&client_id={CLIENT_ID}"
TOKEN_ENDPOINT = "https://github.com/login/oauth/access_token"
USER_ENDPOINT = "https://api.github.com/user"


"""
1. Log in via the browser using the 'Authorization URL' outputted in the terminal.
   (If you're already logged in to GitHub, either log out or test in an incognito/private browser window.)
2. Once logged in, the page will redirect. Grab the code from the redirect URL.
3. Paste the code in the terminal.
"""
print(f"Authorization URL: {AUTHORIZATION_ENDPOINT}")
code = input("Enter the code: ")


"""
Using the authorization code, we can request an access token.
"""
# Once we get the code, we sent the code to the access token
# endpoint(along with id and secret). The response contains
# the access_token and we parse is using parse_qs
res = requests.post(
    TOKEN_ENDPOINT,
    data=dict(
        client_id= "0225fdee833e3336e259",
        client_secret= "daf58d3ed3b618f172843057773a1a949c8d24cf",
        code=code,
    ),
)
res = parse_qs(res.content.decode("utf-8"))
token = res["access_token"][0]


"""
Finally, we can use the access token to obtain information about the user.
"""
user_data = requests.get(USER_ENDPOINT, headers=dict(Authorization=f"token {token}"))
username = user_data.json()["login"]
print(f"You are {username} on GitHub")


