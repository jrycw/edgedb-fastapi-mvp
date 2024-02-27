import svcs

from app._lifespan import _lifespan

t_lifespan = svcs.fastapi.lifespan(_lifespan)
