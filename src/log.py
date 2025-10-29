import logging
import sys


console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(levelname)s:     %(asctime)s           %(message)s")
console_handler.setFormatter(formatter)

app_info = logging.getLogger("app.info")
app_error = logging.getLogger("app.error")

app_info.addHandler(console_handler)
app_error.addHandler(console_handler)

app_info.setLevel(logging.INFO)
app_error.setLevel(logging.ERROR)

app_info.propagate = False
app_error.propagate = False

