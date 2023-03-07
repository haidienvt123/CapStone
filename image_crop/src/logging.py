import logging

error = logging.error
warn = logging.warn
info = logging.info
debug = logging.debug

def setup(filename='ai-service.log', level=logging.INFO):
    # Setup logging handler
    logging.basicConfig(level=level,
                        format='[%(asctime)s] %(levelname)s - %(message)s at %(pathname)s:%(lineno)d')
