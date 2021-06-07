try:
    from .dev_settings import *  # noqa
except Exception:
    from .prod_settings import *  # noqa
