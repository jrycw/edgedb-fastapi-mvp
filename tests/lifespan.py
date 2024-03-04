from functools import partial

import svcs
from fastapi import FastAPI


async def _lifespan(app: FastAPI, registry: svcs.Registry):
    yield
    await registry.aclose()


def make_lifespan():
    return svcs.fastapi.lifespan(partial(_lifespan))


t_lifespan = make_lifespan()
