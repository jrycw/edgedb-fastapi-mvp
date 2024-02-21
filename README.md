# edgedb-fastapi-mvp
[![tests](https://github.com/jrycw/edgedb-fastapi-mvp/actions/workflows/pytest.yml/badge.svg?branch=master)](https://github.com/jrycw/edgedb-fastapi-mvp/actions/workflows/pytest.yml)

## Project Overview
This repository is the outcome of my self-practice journey with `EdgeDB` and `FastAPI`. Initially, I followed the tutorial provided in [EdgeDB for FastAPI](https://www.edgedb.com/docs/guides/tutorials/rest_apis_with_fastapi), but I've made the following modifications:

* Updated the schema to utilize EdgeDB v4.
* Explored integration possibilities with [svcs](https://svcs.hynek.me/en/stable/index.html) written by [Hynek Schlawack](https://hynek.me/).
* Employed additional `Pydantic` models for enhanced data validation and serialization.
* Expanded the test suite to ensure comprehensive coverage.
