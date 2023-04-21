"""
    sct_logging.py
    -------
    Logger setup script
"""

logger_conf_dict = {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(module)s ( %(funcName)s ): %(levelname)s : %(message)s",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["console"]},
    }
