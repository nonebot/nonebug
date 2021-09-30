import nonebot
from nonebot.log import logger, default_filter
from nonebug.config import NonebugCofig
from nonebug.typing import Optional

_config = None


def init(*, _env_file: Optional[str] = None, **kwargs):
    global _config
    nonebot.init(_env_file=_env_file, **kwargs)
    if _config is None:
        base_config = nonebot.get_driver().config
        _config = NonebugCofig(**base_config.dict())
        default_filter.level = _config.nonebug_log_level
        logger.success('Nonebug init success!')


def get_config():
    return _config



from nonebug.constructor import Constructor