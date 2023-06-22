import os


def pytest_logger_config(logger_config):
    logger_config.add_loggers(["testing"], stdout_level="debug")
    logger_config.set_log_option_default("testing")


def pytest_logger_logdirlink(config):
    return os.path.join(os.path.dirname(__file__), "tests", "logs")
