import datetime

def generate_filename():
    """Generates a filename with the current date and time in the specified format."""
    current_time = datetime.datetime.now()
    # Format the date and time as YYYY-mm-dd_HHmm_SS
    filename = current_time.strftime("%Y-%m-%d_%H%M_%S")
    return f"report_{filename}.html"