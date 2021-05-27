try:
    from .dev_settings import *
except Exception:
    from .prod_settings import *
