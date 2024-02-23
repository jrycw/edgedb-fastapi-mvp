# edgedb-fastapi-mvp
[![tests](https://github.com/jrycw/edgedb-fastapi-mvp/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/jrycw/edgedb-fastapi-mvp/actions/workflows/pytest.yml)

## Project Overview
This repository is the outcome of my self-practice journey with `EdgeDB` and `FastAPI`. Initially, I followed the tutorial provided in [EdgeDB for FastAPI](https://www.edgedb.com/docs/guides/tutorials/rest_apis_with_fastapi), but I've made the following modifications:

* Updated the schema to utilize EdgeDB v4.
* Explored integration possibilities with [svcs](https://svcs.hynek.me/en/stable/index.html) written by [Hynek Schlawack](https://hynek.me/).
* Employed additional `Pydantic` models for enhanced data validation and serialization.
* Expanded the test suite to ensure comprehensive coverage.
* Testing out the new package installer and resolver, [uv](https://github.com/astral-sh/uv).
* Using [FastUI](https://github.com/pydantic/FastUI) for the frontend(POC for `get_users` and `get_user`).

### Users
#### `get_users`
![get_users](https://github.com/jrycw/edgedb-fastapi-mvp/blob/0df128a28cf20c07dd1348d3e738909b0299b54e/images/users/get_users.png)

#### `get_user`
![get_user](https://github.com/jrycw/edgedb-fastapi-mvp/blob/0df128a28cf20c07dd1348d3e738909b0299b54e/images/users/get_user.png)
