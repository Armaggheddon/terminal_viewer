import sys
import os
from typing import List, Union, Tuple
import time
from enum import Enum

import cv2
import numpy as np

from .colors import rgb2ansi256, val2grayscale
from .media_handler import MediaHandler, EndMediaError, UnsupportedMediaError
from .keyboard_handler import KeyboardHandler
from .overlay import write_media_timeline, write_help, write_media_title, write_unsupported_media, write_media_position


class MediaControl:
    """
    MediaControl is a class that holds the state of a media control
    """
    def __init__(self, initial_value: bool = False) -> None:
        self.should_perform = initial_value

    def toggle(self) -> None:
        """ Toggle the state of the media control """
        self.should_perform = not self.should_perform


class VideoBuffer:
    """
    VideoBuffer is a class that holds the state of the video buffer
    """
    def __init__(self, cols: int, lines: int) -> None:
        self.cols = cols
        self.lines = lines
        self.buffer_size = cols * lines
        self.buffer = [" " for _ in range(self.buffer_size)]

    def clear(self) -> None:
        """
        Clear the buffer by filling it with empty spaces
        """
        self.buffer.clear()
        self.buffer = [" " for _ in range(self.buffer_size)]
    
    def update_size(self, cols: int, lines: int) -> None:
        """
        Update the size of the buffer and clear it

        Parameters:
        - cols (int): the number of columns
        - lines (int): the number of lines
        """
        self.cols = cols
        self.lines = lines
        self.buffer_size = cols * lines
        self.clear()

class KeyboardCommand(Enum):
    QUIT = "q"
    REWIND = "r"
    NEXT_MEDIA = "m"
    PREVIOUS_MEDIA = "n"
    NEXT_FRAME = "+"
    PREVIOUS_FRAME = "-"
    PLAY_PAUSE = "p"
    SHOW_HIDE_TIMELINE = "t"
    SHOW_HIDE_HELP = "h"


def handle_ctrl_c(func):
    """
    wrapper function to handle keyboard interrupt
    """
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except KeyboardInterrupt:
            pass
        finally:
            # restore terminal style on close
            Display.clear_display()
    return wrapper


class Display():
    def __init__(
            self, 
            media_paths: List[str] = None, 
            folders: List[str] = None, 
            grayscale: bool = False) -> None:
        """
        Display is a class that handles the display of media files in the terminal

        Parameters:
        - media_paths (List[str]): a list of media paths to display
        - folders (List[str]): a list of folders containing media files to display
        - grayscale (bool): display the media in grayscale
        """

        self.terminal_size = os.get_terminal_size()
        self.cols = self.terminal_size.columns
        self.lines = self.terminal_size.lines
        self.buffer_size = self.cols * self.lines
        self.is_grayscale = grayscale
        
        self.content_buffer = VideoBuffer(self.cols, self.lines)
        self.overlay_buffer = VideoBuffer(self.cols, self.lines)
        self.command_buffer = []
        
        self.media_files = []
        if media_paths:
            self.media_files.extend(media_paths)
        if folders:
            for folder in folders:
                for entry in os.scandir(folder):
                    if not entry.is_file(): 
                        continue

                    self.media_files.append(os.path.join(folder, entry.name))
                
        self.current_media_index = 0
        self.media_count = len(self.media_files)

        # controls for the media that require state holding
        self.controls = {
            KeyboardCommand.SHOW_HIDE_TIMELINE.value: MediaControl(False),
            KeyboardCommand.SHOW_HIDE_HELP.value: MediaControl(False),
        }

        # disable cursor
        sys.stdout.write("\x1b[?25l")
        Display.clear_display()
        self.move_to(0, 0)
        self.kb = KeyboardHandler()

    def __update_display(self) -> None:
        """ Update the buffers if the terminal size has changed """
        # TODO: maybe limit a minimum size for resize?? 
        # RN if the terminal is resized to a very small size
        # the application will crash
        if (new_terminal_size := os.get_terminal_size()) != self.terminal_size:
            self.terminal_size = new_terminal_size
            self.cols = self.terminal_size.columns
            self.lines = self.terminal_size.lines
            self.content_buffer.update_size(
                self.terminal_size.columns,
                self.terminal_size.lines
            )

            self.overlay_buffer.update_size(
                self.terminal_size.columns,
                self.terminal_size.lines
            )
    
    def move_to(self, x: int, y: int) -> None:
        """ Move the cursor to the specified position """
        sys.stdout.write(f"\x1b[{y};{x}H")

    @staticmethod
    def clear_display():
        """ Clear the display restoring the terminal to its original state """
        sys.stdout.write("\n")
        sys.stdout.write("\x1b[0m")
        sys.stdout.write("\n")

    def get_color(self, color: Union[int, Tuple[int, int, int]]) -> str:
        """ 
        Get the ANSI color code for the given color. 
        Handles grayscale and RGB colors returning the appropriate
        ANSI color code
        
        Parameters:
        - color (Union[int, Tuple[int, int, int]]): the color to convert
        
        Returns:
        - str: the ANSI color code
        """
        if self.is_grayscale:
            return val2grayscale(color, bg=True)
        return rgb2ansi256(*color, bg=True)

    def write_frame(self, frame: np.ndarray) -> None:
        """ 
        Write the frame to the content buffer 
        
        Parameters:
        - frame (np.ndarray): the frame to write
        """
        _frame = cv2.resize(frame, (self.cols, self.lines), interpolation=cv2.INTER_NEAREST)
        # OpenCV reads images in BGR format convert to RGB
        _frame = _frame[:, :, ::-1]
        if self.is_grayscale:
            _frame = cv2.cvtColor(_frame, cv2.COLOR_RGB2GRAY)
        pos = 0
        for y in range(self.lines):
            for x in range(self.cols):
                px_color = _frame[y, x]
                self.content_buffer.buffer[pos] = f"{self.get_color(px_color)} "
                pos += 1

    def write_overlay(self, media_handler: MediaHandler) -> None:
        """
        Write the overlay to the overlay buffer
        
        Parameters:
        - media_handler (MediaHandler): the media handler for the 
            currently playing media
        """
        self.overlay_buffer.clear()
        if self.controls[KeyboardCommand.SHOW_HIDE_TIMELINE.value].should_perform:
            write_media_title(
                self.overlay_buffer.buffer,
                self.cols,
                self.lines,
                media_handler.media_path,
                grayscale=self.is_grayscale
            )

            write_media_position(
                self.overlay_buffer.buffer,
                self.cols,
                self.lines,
                self.current_media_index + 1,
                self.media_count,
                grayscale=self.is_grayscale
            )

            if media_handler.is_video:
                write_media_timeline(
                    self.overlay_buffer.buffer,
                    self.cols, 
                    self.lines, 
                    media_handler.current_time(),
                    media_handler.duration(),
                    grayscale=self.is_grayscale
                )
        if self.controls[KeyboardCommand.SHOW_HIDE_HELP.value].should_perform:
            write_help(
                self.overlay_buffer.buffer,
                self.cols,
                self.lines,
                grayscale=self.is_grayscale
            )

    def draw(self) -> None:
        """ Draw the content and overlay buffers to the terminal """
        self.move_to(0, 0)

        # Combine the content and overlay buffers
        # by using the content buffer as the base
        # and overlaying the overlay buffer on top only if the
        # overlay buffer has an empty space or no character
        buffer_out = [ 
            c_px if o_px == " " or o_px == "" else o_px
            for c_px, o_px in zip(self.content_buffer.buffer, self.overlay_buffer.buffer)
        ]
        buffer_out = "".join(buffer_out)
        sys.stdout.write(buffer_out)
        sys.stdout.flush() # force the buffer to be written to the terminal
        
        # at the end check if the terminal size has changed
        # so that at the next redraw the buffers are of the 
        # correct size
        self.__update_display() 

    @handle_ctrl_c
    def show(self) -> None:
        """
        Show the media files in the terminal.
        This function will display the media files in the terminal
        and handle the keyboard commands to control the media files
        """
        close = False
        
        # Use while True so that we can freely move between media files
        while True:
            media_handler = MediaHandler(self.media_files[self.current_media_index]) 
            while True:

                # check if there are any keyboard commands
                if self.command_buffer:
                    action = self.command_buffer.pop(0)

                    # clear the buffer to avoid command build-up
                    self.command_buffer.clear()
                    if action == KeyboardCommand.QUIT.value:
                        close = True
                        break
                    elif action == KeyboardCommand.REWIND.value:
                        media_handler.rewind()
                    elif action == KeyboardCommand.NEXT_MEDIA.value:
                        break
                    elif action == KeyboardCommand.PREVIOUS_MEDIA.value:
                        # decrement by 2 since we increment at the end of the loop
                        # therefore acting like a -1
                        self.current_media_index -= 2
                        if self.current_media_index < -1:
                            self.current_media_index = -1
                        break
                    elif action == KeyboardCommand.NEXT_FRAME.value:
                        media_handler.skip_frame()
                    elif action == KeyboardCommand.PREVIOUS_FRAME.value:
                        media_handler.prev_frame()
                    elif action == KeyboardCommand.PLAY_PAUSE.value:
                        media_handler.play_pause()
                    elif action == (keyboard_command := KeyboardCommand.SHOW_HIDE_TIMELINE.value):
                        self.controls[keyboard_command].toggle()
                    elif action == (keyboard_command := KeyboardCommand.SHOW_HIDE_HELP.value):
                        self.controls[keyboard_command].toggle()
                self.write_overlay(media_handler)
                
                try:
                    frame = media_handler.next_frame()
                    self.write_frame(frame)
                except EndMediaError:
                    # the video has ended
                    # break this while True loop
                    # so that we can move to the next media file
                    break
                except UnsupportedMediaError:
                    # set the content buffer
                    # with the text "Unsupported media"
                    write_unsupported_media(
                        self.content_buffer.buffer, 
                        self.cols, 
                        self.lines, 
                        media_handler.media_path, 
                        grayscale=self.is_grayscale)

                if self.kb.kbhit():
                    self.command_buffer.append(self.kb.getch())
                self.draw()
                time.sleep(0.025) # good tradeoff between CPU usage and responsiveness
            
            media_handler.close()

            self.current_media_index += 1
            if self.current_media_index >= len(self.media_files):
                # we have displayed all media files
                break 
        
            if close:
                Display.clear_display()
                break