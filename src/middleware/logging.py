import coloredlogs
import logging
import sys

logging.basicConfig()
logger = logging.getLogger(name="app")
coloredlogs.install(logger=logger)
logger.propagate = False
coloredFormatter = coloredlogs.ColoredFormatter(
    fmt="[%(name)s] %(asctime)s %(funcName)s %(lineno)-3d  %(message)s",
    level_styles=dict(
        debug=dict(color="white"),
        info=dict(color="cyan", bold=True, bright=True),
        warning=dict(color="yellow", bold=True, bright=True),
        error=dict(color="red", bold=True, bright=True),
        critical=dict(color="white", bold=True, background="red"),
    ),
    field_styles=dict(
        name=dict(color="yellow", bold=True, bright=True),
        asctime=dict(color="green", bold=True, bright=True),
        funcName=dict(color="magenta", bold=True, bright=True),
        lineno=dict(color="red", bold=True, bright=True),
    ),
)
ch = logging.StreamHandler(stream=sys.stdout)
ch.setFormatter(fmt=coloredFormatter)
logger.addHandler(hdlr=ch)
logger.setLevel(level=logging.DEBUG)
# uvicorn_error = logging.getLogger("uvicorn.error")
# uvicorn_error.disabled = True
# uvicorn_access = logging.getLogger("uvicorn.access")
# uvicorn_access.disabled = True
