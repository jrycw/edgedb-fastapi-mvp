import svcs

from ._lifespan import _lifespan

lifespan = svcs.fastapi.lifespan(_lifespan)
