import datetime
import pytz

timezone = pytz.timezone("Asia/Shanghai")

# Guarantees Save TZ is always Shanghai
# Will probably have to deprecate soon
def get_current_time(var_format):
    time_now = datetime.datetime.now(timezone)

    if var_format == "str_date":
        var_return = time_now.strftime("%Y-%m-%d")
    elif var_format == "str_time":
        var_return = time_now.strftime("%I:%M:%S %p")
    elif var_format == "str_readable":
        var_return = time_now.strftime("%d %b %Y %I:%M %p")
    else:
        var_return = time_now

    return var_return