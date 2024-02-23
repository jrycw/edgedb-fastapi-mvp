from functools import partial

import svcs

from ._lifespan import _lifespan
from .config import settings

lifespan = svcs.fastapi.lifespan(partial(_lifespan, need_fastui=settings.need_fastui))
