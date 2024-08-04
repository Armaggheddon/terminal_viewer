FG_256_TEMPLATE = "\x1b[38;2;{r};{g};{b}m"
BG_256_TEMPLATE = "\x1b[48;2;{r};{g};{b}m"

# color is from 232 to 255 included, 24 values
FG_GRAY_TEMPLATE = "\x1b[38;5;{color}m"
BG_GRAY_TEMPLATE = "\x1b[48;5;{color}m"


def val2grayscale(val: int, bg: bool=False) -> str:
    """ 
    Convert a grayscale value to an ANSI escape code representation 
    
    Parameters:
    - val (int): the grayscale value
    - bg (bool): if True, the color is set as background, otherwise
        the color is set as foreground

    Returns:
    - str: the ANSI escape code representation of the color

    Raises:
    - ValueError: if val is not between 0 and 255
    """
    # clamp value between 0 and 255
    if val < 0 or val > 255:
        raise ValueError("val must be between 0 and 255")
    
    # scale color in 0-23 as the available grayscale values
    color_id = int((val / 255) * 23)
    template = BG_GRAY_TEMPLATE if bg else FG_GRAY_TEMPLATE
    return template.format(color=color_id + 232)


def rgb2ansi256(r: int, g: int, b: int, bg: bool=False) -> str:
    """
    Convert an RGB color to an ANSI escape code representation
    
    Parameters:
    - r (int): the red value
    - g (int): the green value
    - b (int): the blue value
    - bg (bool): if True, the color is set as background, otherwise
        the color is set as foreground
        
    Returns:
    - str: the ANSI escape code representation of the color
    
    Raises:
    - ValueError: if r, g, or b are not between 0 and 255
    """
    if r < 0 or r > 255:
        raise ValueError("r must be between 0 and 255")
    if g < 0 or g > 255:
        raise ValueError("g must be between 0 and 255")
    if b < 0 or b > 255:
        raise ValueError("b must be between 0 and 255")
    
    template = BG_256_TEMPLATE if bg else FG_256_TEMPLATE
    
    return template.format(
        r=r,
        g=g,
        b=b
    )




