import pathlib
from typing import List, Tuple, Callable, Union

from .colors import rgb2ansi256, val2grayscale

RGB_TEXT_FG_COLOR = (255, 255, 255)
GRAY_TEXT_FG_COLOR = (255, )
RGB_TEXT_BG_COLOR = (0, 0, 0)
GRAY_TEXT_BG_COLOR = (0, )

def float_to_time(msec: float) -> str:
    """
    Convert a time in milliseconds to a string representation
    in the format HH:MM:SS if the time is greater than 1 hour,
    or MM:SS if the time is less than 1 hour
    
    Parameters:
    - msec (float): the time in milliseconds
    
    Returns:
    - str: the string representation of the time
    """
    sec = msec / 1000 
    min = sec / 60
    sec = sec % 60
    hour = min / 60
    min = min % 60
    if int(hour) > 0:
        return f"{int(hour):02}:{int(min):02}:{int(sec):02}"
    return f"{int(min):02}:{int(sec):02}"

def get_overlay_func_color(
        grayscale: bool = False,
        rgb_text_fg_color: Tuple[int, int, int] = RGB_TEXT_FG_COLOR,
        gray_text_fg_color: Tuple[int] = GRAY_TEXT_FG_COLOR,
        rgb_text_bg_color: Tuple[int, int, int] = RGB_TEXT_BG_COLOR,
        gray_text_bg_color: Tuple[int] = GRAY_TEXT_BG_COLOR
        ) -> Tuple[Callable, Union[Tuple[int, int , int], int], Union[Tuple[int, int , int], int]]:
    """
    Return the appropriate color function and text color based on the
    grayscale flag. Allows customization of the colors used, by default
    uses white text on black background for both RGB and grayscale colors

    Parameters:
    - grayscale (bool): if True, will return the grayscale color function,
        and text colors, otherwise will return the RGB color function and
        text colors
    - rgb_text_fg_color (Tuple[int, int, int]): the RGB color to use for the
        text foreground if not grayscale
    - gray_text_fg_color (Tuple[int]): the grayscale color to use for the
        text foreground if grayscale
    - rgb_text_bg_color (Tuple[int, int, int]): the RGB color to use for the
        text background if not grayscale
    - gray_text_bg_color (Tuple[int]): the grayscale color to use for the
        text background if grayscale

    Returns:
    - Tuple[Callable, Union[Tuple[int, int , int], int], Union[Tuple[int, int , int], int]]:
        the color function, the text foreground color, and the text background color
    """
    func = val2grayscale if grayscale else rgb2ansi256
    text_fg_color = gray_text_fg_color if grayscale else rgb_text_fg_color
    text_bg_color = gray_text_bg_color if grayscale else rgb_text_bg_color
    return func, text_fg_color, text_bg_color

def write_media_timeline(
        buffer: List[str],
        columns: int,
        lines: int, 
        position: float, 
        duration: float,
        grayscale: bool = False) -> None:
    """
    Write the media timeline to the buffer along with the current time and the
    total media duration on the last 2 lines of the buffer. The timeline is
    represented as a progress bar that fills the width of the buffer based on
    the current position and duration of the media. The current time and total
    media duration are displayed in HH:MM:SS format on the opposite sides of the
    line below the progress bar. The final result resembles the following:
    #############################################
    HH:MM:SS                             HH:MM:SS

    Parameters:
    - buffer (List[str]): the buffer to write the timeline to, the data is 
        written in place on this buffer
    - columns (int): the number of columns in the buffer
    - lines (int): the number of lines in the buffer
    - position (float): the current position in milliseconds
    - duration (float): the total duration of the media in milliseconds
    - grayscale (bool): if True, the timeline will be displayed in grayscale
    """
    
    get_color, _TEXT_FG_COLOR, _TEXT_BG_COLOR = get_overlay_func_color(grayscale)

    if duration == 0:
        return
    progress = position / duration
    curr_time = float_to_time(position)
    max_time = float_to_time(duration)

    # Progress bar
    line_width = int(progress * columns)
    start_offset = (lines-2) * columns # start from the 2nd last line
    buffer[start_offset:start_offset+line_width] = [
        f"{get_color(*_TEXT_FG_COLOR)}#" 
        for _ in range(line_width)]
    # fill the line with background color
    buffer[start_offset:start_offset+columns] = [ 
        f"{get_color(*_TEXT_BG_COLOR, bg=True)}{buf}" 
        for buf in buffer[start_offset:start_offset+columns]]
    # reset the color at the end of the progress bar to avoid
    # coloring the rest of the buffer
    buffer[start_offset+line_width-1] = buffer[start_offset+line_width-1] + "\x1b[0m"

    # Current time
    buffer[start_offset+columns:start_offset+columns+len(curr_time)] = [
        f"{get_color(*_TEXT_BG_COLOR, bg=True)}{get_color(*_TEXT_FG_COLOR)}{c}"
        for c in curr_time]
    buffer[start_offset+columns+len(curr_time)-1] = buffer[start_offset+columns+len(curr_time)-1] + "\x1b[0m"
    
    # Total time
    buffer[start_offset+columns+columns-len(max_time):start_offset+columns+columns] = [
        f"{get_color(*_TEXT_BG_COLOR, bg=True)}{get_color(*_TEXT_FG_COLOR)}{c}"
        for c in max_time]
    buffer[start_offset+columns+columns-1] = buffer[start_offset+columns+columns-1] + "\x1b[0m"

def write_media_title(
        buffer: List[str],
        columns: int,
        lines: int,
        media_path: str,
        grayscale: bool=False) -> None:
    """
    Write the media title to the buffer on the 3rd last line of the buffer in the
    left corner. The title is the name of the media file without the path

    Parameters:
    - buffer (List[str]): the buffer to write the title to, the data is written
        in place on this buffer
    - columns (int): the number of columns in the buffer
    - lines (int): the number of lines in the buffer
    - media_path (str): the path to the media file
    - grayscale (bool): if True, the title will be displayed in grayscale
    """
    
    get_color, _TEXT_FG_COLOR, _TEXT_BG_COLOR = get_overlay_func_color(grayscale)

    # timeline uses last 2 lines, the title uses the 3rd last line
    start_offset = (lines-3) * columns
    file_name = pathlib.Path(media_path).name
    buffer[start_offset:start_offset+len(file_name)] = [
        f"{get_color(*_TEXT_BG_COLOR, bg=True)}{get_color(*_TEXT_FG_COLOR)}{c}"
        for c in file_name]
    buffer[start_offset+len(file_name)-1] = buffer[start_offset+len(file_name)-1] + "\x1b[0m"


def write_help(
        buffer: List[str],
        columns: int, 
        lines: int,
        grayscale: bool=False) -> None:
    """
    Write the help menu to the buffer. The help menu is displayed in the top left
    corner of the buffer and contains the following options:
    - t: show/hide timeline
    - m: forward frame
    - n: previous frame
    - +: next media
    - -: previous media
    - p: play/pause
    - h: show/hide help
    - q: quit

    Parameters:
    - buffer (List[str]): the buffer to write the help menu to, the data is written
        in place on this buffer
    - columns (int): the number of columns in the buffer
    - lines (int): the number of lines in the buffer
    - grayscale (bool): if True, the help menu will be displayed in grayscale
    """
    get_color, _TEXT_FG_COLOR, _TEXT_BG_COLOR = get_overlay_func_color(grayscale)

    # Maximum width of the help menu
    help_width = 30

    # fill first line of help menu with black
    buffer[0:help_width] = [f"{get_color(*_TEXT_BG_COLOR, bg=True)} " for _ in range(help_width)]
    buffer[help_width-1] = buffer[help_width-1] + "\x1b[0m"
    
    # The text has a space before to have a small margin
    # between the text and the border of the terminal
    line_message = " Help menu"
    buffer[columns:columns+help_width] = [f"{get_color(*_TEXT_BG_COLOR, bg=True)}{get_color(*_TEXT_FG_COLOR)}{c}" for c in line_message] + [f"{get_color(*_TEXT_BG_COLOR, bg=True)} " for _ in range(help_width-len(line_message))]
    buffer[columns+help_width-1] = buffer[columns+help_width-1] + "\x1b[0m"
    
    start_offset = 2*columns
    line_message = " t: show/hide timeline"
    buffer[start_offset:start_offset+help_width] = [f"{get_color(*_TEXT_BG_COLOR, bg=True)}{get_color(*_TEXT_FG_COLOR)}{c}" for c in line_message] + [f"{get_color(*_TEXT_BG_COLOR, bg=True)} " for _ in range(help_width-len(line_message))]
    buffer[start_offset+help_width-1] = buffer[start_offset+help_width-1] + "\x1b[0m"
    
    start_offset = 3*columns
    line_message = " m: forward frame"
    buffer[start_offset:start_offset+help_width] = [f"{get_color(*_TEXT_BG_COLOR, bg=True)}{get_color(*_TEXT_FG_COLOR)}{c}" for c in line_message] + [f"{get_color(*_TEXT_BG_COLOR, bg=True)} " for _ in range(help_width-len(line_message))]
    buffer[start_offset+help_width-1] = buffer[start_offset+help_width-1] + "\x1b[0m"
    
    start_offset = 4*columns
    line_message = " n: previous frame"
    buffer[start_offset:start_offset+help_width] = [f"{get_color(*_TEXT_BG_COLOR, bg=True)}{get_color(*_TEXT_FG_COLOR)}{c}" for c in line_message] + [f"{get_color(*_TEXT_BG_COLOR, bg=True)} " for _ in range(help_width-len(line_message))]
    buffer[start_offset+help_width-1] = buffer[start_offset+help_width-1] + "\x1b[0m"

    start_offset = 5*columns
    line_message = " +: next media"
    buffer[start_offset:start_offset+help_width] = [f"{get_color(*_TEXT_BG_COLOR, bg=True)}{get_color(*_TEXT_FG_COLOR)}{c}" for c in line_message] + [f"{get_color(*_TEXT_BG_COLOR, bg=True)} " for _ in range(help_width-len(line_message))]
    buffer[start_offset+help_width-1] = buffer[start_offset+help_width-1] + "\x1b[0m"

    start_offset = 6*columns
    line_message = " -: previous media"
    buffer[start_offset:start_offset+help_width] = [f"{get_color(*_TEXT_BG_COLOR, bg=True)}{get_color(*_TEXT_FG_COLOR)}{c}" for c in line_message] + [f"{get_color(*_TEXT_BG_COLOR, bg=True)} " for _ in range(help_width-len(line_message))]
    buffer[start_offset+help_width-1] = buffer[start_offset+help_width-1] + "\x1b[0m"
    
    start_offset = 7*columns
    line_message = " p: play/pause"
    buffer[start_offset:start_offset+help_width] = [f"{get_color(*_TEXT_BG_COLOR, bg=True)}{get_color(*_TEXT_FG_COLOR)}{c}" for c in line_message] + [f"{get_color(*_TEXT_BG_COLOR, bg=True)} " for _ in range(help_width-len(line_message))]
    buffer[start_offset+help_width-1] = buffer[start_offset+help_width-1] + "\x1b[0m"
    
    start_offset = 8*columns
    line_message = " h: show/hide help"
    buffer[start_offset:start_offset+help_width] = [f"{get_color(*_TEXT_BG_COLOR, bg=True)}{get_color(*_TEXT_FG_COLOR)}{c}" for c in line_message] + [f"{get_color(*_TEXT_BG_COLOR, bg=True)} " for _ in range(help_width-len(line_message))]
    buffer[start_offset+help_width-1] = buffer[start_offset+help_width-1] + "\x1b[0m"
    
    start_offset = 9*columns
    line_message = " q: quit"
    buffer[start_offset:start_offset+help_width] = [f"{get_color(*_TEXT_BG_COLOR, bg=True)}{get_color(*_TEXT_FG_COLOR)}{c}" for c in line_message] + [f"{get_color(*_TEXT_BG_COLOR, bg=True)} " for _ in range(help_width-len(line_message))]
    buffer[start_offset+help_width-1] = buffer[start_offset+help_width-1] + "\x1b[0m"

    # fill last line of help menu with black
    buffer[10*columns:10*columns+help_width] = [f"{get_color(*_TEXT_BG_COLOR, bg=True)} " for _ in range(help_width)]
    buffer[10*columns+help_width-1] = buffer[10*columns+help_width-1] + "\x1b[0m"


def write_media_position(
        buffer: List[str],
        columns: int,
        lines: int,
        media_index: int,
        media_count: int,
        grayscale: bool=False) -> None:
    """
    Write the media position to the buffer on the 2nd last line of the buffer in the
    right corner. The position is the index of the current media in the sequence of
    media files. The position is displayed as "{media_index}/{media_count}"

    Parameters:
    - buffer (List[str]): the buffer to write the position to, the data is written
        in place on this buffer
    - columns (int): the number of columns in the buffer
    - lines (int): the number of lines in the buffer
    - media_index (int): the index of the current media in the sequence of media files
    - media_count (int): the total number of media files in the sequence
    - grayscale (bool): if True, the position will be displayed in grayscale
    """

    get_color, _TEXT_FG_COLOR, _TEXT_BG_COLOR = get_overlay_func_color(grayscale)

    text = f" {media_index}/{media_count} "
    start_offset = 2 * columns - len(text)
    buffer[start_offset:start_offset+len(text)] = [
        f"{get_color(*_TEXT_BG_COLOR, bg=True)}{get_color(*_TEXT_FG_COLOR)}{c}"
        for c in text]
    buffer[start_offset+len(text)-1] = buffer[start_offset+len(text)-1] + "\x1b[0m"


def write_unsupported_media(
        buffer: List[str],
        columns: int,
        lines: int,
        media_path: str,
        grayscale: bool=False,
        fill_bg: bool = True) -> None:
    
    """
    Write a message to the buffer indicating that the media is unsupported.
    The message is displayed in the center of the screen. The message is
    "Unsupported media extension: {media_extension}". The text is written in
    yellow (white if grayscale) with black background by default

    Parameters:
    - buffer (List[str]): the buffer to write the message to, the data is written
        in place on this buffer
    - columns (int): the number of columns in the buffer
    - lines (int): the number of lines in the buffer
    - media_path (str): the path to the media file
    - grayscale (bool): if True, the message will be displayed in grayscale
    - fill_bg (bool): if True, the buffer will be filled with black before writing
        the message, otherwise the message will be written on top of the existing
        buffer data and only the text will have a black background
    """
    
    get_color, _TEXT_FG_COLOR, _TEXT_BG_COLOR = get_overlay_func_color(
        grayscale,
        rgb_text_fg_color=(255, 255, 0)) # customize text color to yellow

    if fill_bg:
        # write all buffer black
        buffer[:] = [f"{get_color(*_TEXT_BG_COLOR, bg=True)} " for _ in buffer]

    text_message = f"Unsupported media extension: {pathlib.Path(media_path).suffix}"

    # write the message in the center of the screen
    start_offset = int((lines*columns)/2 - columns/2) - int(len(text_message)/2)
    buffer[start_offset: start_offset+len(text_message)] = [
        f"{get_color(*_TEXT_BG_COLOR, bg=True)}{get_color(*_TEXT_FG_COLOR)}{c}"
        for c in text_message]
    buffer[start_offset+len(text_message)-1] = buffer[start_offset+len(text_message)-1] + "\x1b[0m"