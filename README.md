# edgedb-fastapi-mvp
[![tests](https://github.com/jrycw/edgedb-fastapi-mvp/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/jrycw/edgedb-fastapi-mvp/actions/workflows/pytest.yml)

## Project Overview
This repository is the culmination of my journey exploring [EdgeDB](https://github.com/edgedb/edgedb) and [FastAPI](https://github.com/tiangolo/fastapi). Initially inspired by the tutorial provided in [EdgeDB for FastAPI](https://www.edgedb.com/docs/guides/tutorials/rest_apis_with_fastapi), I've extended the project with the following enhancements:

* Updated the schema to leverage EdgeDB v4 features.
* Investigated integration possibilities with [svcs](https://github.com/hynek/svcs/) by [Hynek Schlawack](https://hynek.me/).
* Utilized additional `Pydantic` models for enhanced data validation and serialization.
* Expanded the test suite to achieve comprehensive test coverage.
* Experimented with the new package installer and resolver, [uv](https://github.com/astral-sh/uv).
* Explored the use of [FastUI](https://github.com/pydantic/FastUI) for frontend components (POC for `get_users` and `get_user`).

### Images
#### `get_users`
![get_users](https://github.com/jrycw/edgedb-fastapi-mvp/blob/0df128a28cf20c07dd1348d3e738909b0299b54e/images/users/get_users.png)

#### `get_user`
![get_user](https://github.com/jrycw/edgedb-fastapi-mvp/blob/0df128a28cf20c07dd1348d3e738909b0299b54e/images/users/get_user.png)
