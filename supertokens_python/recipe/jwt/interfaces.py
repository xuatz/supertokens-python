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
from abc import ABC, abstractmethod
from typing import Union, List
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal
from supertokens_python.framework import BaseRequest, BaseResponse
from supertokens_python.recipe.jwt.types import JsonWebKey


class CreateJwtResult(ABC):
    def __init__(
            self, status: Literal['OK', 'UNSUPPORTED_ALGORITHM_ERROR'], jwt: str = None):
        self.status = status
        self.jwt = jwt


class CreateJwtResultOk(CreateJwtResult):
    def __init__(self, jwt: str):
        super().__init__('OK', jwt)


class CreateJwtResultUnsupportedAlgorithm(CreateJwtResult):
    def __init__(self):
        super().__init__('UNSUPPORTED_ALGORITHM_ERROR')


class GetJWKSResult(ABC):
    def __init__(
            self, status: Literal['OK'], keys: List[JsonWebKey]):
        self.status = status
        self.keys = keys


class RecipeInterface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def create_jwt(self, payload: dict = None, validity_seconds: int = None) -> CreateJwtResult:
        pass

    @abstractmethod
    async def get_jwks(self) -> GetJWKSResult:
        pass


class APIOptions:
    def __init__(self, request: BaseRequest, response: Union[BaseResponse, None], recipe_id: str,
                 config, recipe_implementation: RecipeInterface):
        self.request = request
        self.response = response
        self.recipe_id = recipe_id
        self.config = config
        self.recipe_implementation = recipe_implementation


class JWKSGetResponse:
    def __init__(
            self, status: Literal['OK'], keys: List[JsonWebKey]):
        self.status = status
        self.keys = keys

    def to_json(self):
        keys = []
        for key in self.keys:
            keys.append({
                'kty': key.kty,
                'kid': key.kid,
                'n': key.n,
                'e': key.e,
                'alg': key.alg,
                'use': key.use,
            })

        return {
            'status': 'OK',
            'keys': keys
        }


class APIInterface:
    def __init__(self):
        self.disable_jwks_get = False

    @abstractmethod
    async def jwks_get(self, api_options: APIOptions) -> JWKSGetResponse:
        pass
