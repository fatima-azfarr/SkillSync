import logging

# create logger
logger = logging.getLogger("skillsync")
logger.setLevel(logging.DEBUG)

# format - what each line looks like
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# handler 1 - writes to file
file_handler = logging.FileHandler("pipeline.log")
file_handler.setFormatter(formatter)

# handler 2 - prints to terminal
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

# attach both to logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

