# Copyright (c) 2021, VRAI Labs and/or its affiliates. All rights reserved.
#
# This software is licensed under the Apache License, Version 2.0 (the
# "License") as published by the Apache Software Foundation.
#
# You may not use this file except in compliance with the License. You may
# obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import os

import typing
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse, PlainTextResponse
from starlette.datastructures import Headers
from starlette.exceptions import ExceptionMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp

from supertokens_python import init, get_all_cors_headers, SupertokensConfig, InputAppInfo
from supertokens_python.framework.fastapi import Middleware
from supertokens_python.recipe import session, thirdpartyemailpassword, thirdparty, emailpassword
from supertokens_python.recipe.emailpassword.types import InputFormField
from supertokens_python.recipe.session import SessionInterface
from supertokens_python.recipe.session.framework.fastapi import verify_session
from supertokens_python.recipe.thirdparty import Github, Google, Facebook

load_dotenv()

app = FastAPI(debug=True)
app.add_middleware(Middleware)
os.environ.setdefault('SUPERTOKENS_ENV', 'testing')


def get_api_port():
    return '8083'


def get_website_port():
    return '3031'


def get_website_domain():
    return 'http://localhost:' + get_website_port()


latest_url_with_token = None


async def create_and_send_custom_email(_, url_with_token):
    global latest_url_with_token
    latest_url_with_token = url_with_token


async def validate_age(value):
    try:
        if int(value) < 18:
            return "You must be over 18 to register"
    except Exception:
        pass

    return None

form_fields = [
    InputFormField('name'),
    InputFormField('age', validate=validate_age),
    InputFormField('country', optional=True)
]


init(
    supertokens_config=SupertokensConfig('http://localhost:9000'),
    app_info=InputAppInfo(
        app_name="SuperTokens Demo",
        api_domain="0.0.0.0:" + get_api_port(),
        website_domain=get_website_domain()
    ),
    framework='fastapi',
    recipe_list=[
        session.init(),
        emailpassword.init(
            sign_up_feature=emailpassword.InputSignUpFeature(form_fields),
            reset_password_using_token_feature=emailpassword.InputResetPasswordUsingTokenFeature(
                create_and_send_custom_email=create_and_send_custom_email
            ),
            email_verification_feature=emailpassword.InputEmailVerificationConfig(
                create_and_send_custom_email=create_and_send_custom_email
            )
        ),
        thirdparty.init(
            sign_in_and_up_feature=thirdparty.SignInAndUpFeature([
                Google(
                    client_id=os.environ.get('GOOGLE_CLIENT_ID'),
                    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET')
                ), Facebook(
                    client_id=os.environ.get('FACEBOOK_CLIENT_ID'),
                    client_secret=os.environ.get('FACEBOOK_CLIENT_SECRET')
                ), Github(
                    client_id=os.environ.get('GITHUB_CLIENT_ID'),
                    client_secret=os.environ.get('GITHUB_CLIENT_SECRET')
                )
            ])
        ),
        thirdpartyemailpassword.init(
            sign_up_feature=thirdpartyemailpassword.InputSignUpFeature(form_fields),
            providers=[
                Google(
                    client_id=os.environ.get('GOOGLE_CLIENT_ID'),
                    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET')
                ), Facebook(
                    client_id=os.environ.get('FACEBOOK_CLIENT_ID'),
                    client_secret=os.environ.get('FACEBOOK_CLIENT_SECRET')
                ), Github(
                    client_id=os.environ.get('GITHUB_CLIENT_ID'),
                    client_secret=os.environ.get('GITHUB_CLIENT_SECRET')
                )
            ]
        )
    ],
    telemetry=False
)


@app.exception_handler(Exception)
async def exception_handler(_, __):
    return JSONResponse(status_code=500, content={})


app.add_middleware(ExceptionMiddleware, handlers=app.exception_handlers)


@app.get('/ping')
def ping():
    return PlainTextResponse(content='success')


@app.get('/sessionInfo')
async def get_session_info(session_: SessionInterface = Depends(verify_session())):
    return JSONResponse({
        'sessionHandle': session_.get_handle(),
        'userId': session_.get_user_id(),
        'accessTokenPayload': session_.get_access_token_payload(),
        'sessionData': await session_.get_session_data()
    })


@app.get("/token")
async def get_token():
    global latest_url_with_token
    return JSONResponse({
        'latestURLWithToken': latest_url_with_token
    })


@app.exception_handler(405)
def f_405(_, e):
    return PlainTextResponse('', status_code=404)


# cors middleware added like this due to issue with add_middleware
# ref: https://github.com/tiangolo/fastapi/issues/1663

class CustomCORSMiddleware(CORSMiddleware):
    def __init__(
        self,
        app_: ASGIApp,
        allow_origins: typing.Sequence[str] = (),
        allow_methods: typing.Sequence[str] = ("GET",),
        allow_headers: typing.Sequence[str] = (),
        allow_credentials: bool = False,
        allow_origin_regex: str = None,
        expose_headers: typing.Sequence[str] = (),
        max_age: int = 600,
    ) -> None:
        super().__init__(app_, allow_origins, allow_methods, allow_headers, allow_credentials, allow_origin_regex,
                         expose_headers, max_age)

    def preflight_response(self, request_headers: Headers) -> Response:
        result = super().preflight_response(request_headers)
        if result.status_code == 200:
            result.headers.__delitem__('content-type')
            result.headers.__delitem__('content-length')
            return Response(status_code=204, headers=dict(result.headers))
        return result


# cors middleware added like this due to issue with add_middleware
# ref: https://github.com/tiangolo/fastapi/issues/1663

app = CustomCORSMiddleware(
    app_=app,
    allow_origins=[
        get_website_domain()
    ],
    allow_credentials=True,
    allow_methods=["GET", "PUT", "POST", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type"] + get_all_cors_headers(),
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=get_api_port())
