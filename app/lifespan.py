from functools import partial

import svcs

from ._lifespan import _lifespan

lifespan = svcs.fastapi.lifespan(partial(_lifespan, prefill=True))
