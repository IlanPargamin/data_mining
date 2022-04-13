import logging


def setup_logger(name, log_file, level=logging.INFO):
    """
    To setup as many loggers as needed
    """

    handler = logging.FileHandler(log_file)
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))

    a_logger = logging.getLogger(name)
    a_logger.setLevel(level)
    a_logger.addHandler(handler)

    return a_logger


logger = setup_logger('main_logger', 'scraper.log')
