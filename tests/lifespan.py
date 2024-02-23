from functools import partial

import svcs

from app._lifespan import _lifespan

t_lifespan = svcs.fastapi.lifespan(partial(_lifespan, need_fastui=False))
