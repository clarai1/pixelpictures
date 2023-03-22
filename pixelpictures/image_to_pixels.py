import numpy as np 
from PIL import Image, ImageDraw, ImageFont
import math

def distance_colors(color1, color2):
    '''
    Computes the square distance between two colors using weighted euclidean distance.

    Parameters
    ----------
        color1, color2 : 3-tuples of ints representing a color
    
    Returns
    -------
        Weighted euclidean distance between color1 and color2, the formula is from: https://www.compuphase.com/cmetric.htm
    '''
    r = (color1[0] + color2[0]) / 2
    return (2 + r / 256) * (color1[0] - color2[0]) ** 2 + 4 * (color1[1] - color2[1]) ** 2 + (2 + (255 - r) / 256) * (color1[2] - color2[2]) ** 2

def get_color(prev_color, colors):
    '''
    Finds color in colors closer to prev_color.

    Parameters
    ----------
        prev_color : 3-tuple of ints representing a color
        colors : list, containing tuples representing colors
    
    Returns
    -------
        Element in colors closer (using distance_colors) to prev_color.
    '''

    min_dist = math.inf
    closer_color = colors[0]
    for color in colors:
        curr_distance = distance_colors(prev_color, color)
        if curr_distance < min_dist:
            min_dist = curr_distance
            closer_color = color
    return closer_color

def resize(grid_width, grid_height, image):
    '''
    Resizes an image.

    Parameters
    ----------
        grid_width : int, desired width
        grid_height : int, desired height
        image : PIL.Image
    
    Returns
    -------
        PIL.Image of height grid_height and width grid_width, containing image as big as possible maintaining the ratio.
    '''

    image_width = image.width
    image_height = image.height

    image = image.convert("RGBA")

    a = min(grid_height / image_height, grid_width / image_width)

    resized = image.resize((math.ceil(image_width * a), math.ceil(image_height * a)), Image.NEAREST)
    
    background = Image.new("RGBA", (grid_width, grid_height), (255, 255, 255))
    background.paste(resized, ((grid_width - int(image_width * a))//2, (grid_height - int(image_height * a))//2), mask=resized)

    return background

def to_pixels(image_arr, colors):
    '''
    Return image in form of array in which every color is in colors.

    Parameters
    ----------
        image_arr : np.array, containing tuples representing colors
        colors : list, containing tuples representing colors
    
    Returns
    -------
        list of same dimension as image_arr representing an image containing only colors in colors.
    '''

    new_image = []

    for i in range(len(image_arr)):
        new_row = []
        for j in range(len(image_arr[0])):
            new_row.append(get_color(image_arr[i][j], colors))
        new_image.append(new_row)

    return new_image

def add_grid(image, start_row=1, start_col=1, dir_rows='tb', dir_cols='lr', grid_color=(0,0,0), size_cell=20, step=1):
    '''
    Adds a personalized grid over a pillow Image.

    Parameters
    ----------
        image : PIL.Image, 18 pixels form one colored pixel.
        start_row : int, starting number to count the rows grid
        start_col : int, starting number to count the columns of the gris
        dir_rows : str, if equal to 'bt' the count of the rows starts from bottom, else it starts from top
        dir_cols : str, if equal to 'rl' the count of the columns starts from right, else it starts from left
        grid_color : 3-tuple of ints that represents desired color of the grid
        size_cell : int, size in pixels of the side of each cell in the grid
        step : int, desired step of displayed numbers of the rows and columns
    
    Returns
    -------
        Resized image with grid on it and count of rows and cols.
    '''

    if step <= 0:
        step = 1

    border = 40
    font_size = 10
    resized = image.resize((image.width // 18 * size_cell, image.height // 18 * size_cell ), Image.NEAREST)
    width = resized.width + border * 2
    height = resized.height + border * 2

    background = Image.new("RGB", (width, height), (255, 255, 255))

    background.paste(resized, (border, border))

    # Draw grid with numbers
    font = ImageFont.truetype("pixelpictures/static/pixelpictures/arial_unicode.ttf", font_size)
    draw = ImageDraw.Draw(background)

    for l in range(resized.height // size_cell):
        draw.line((border , border + l * size_cell) + (width - border, border + l * size_cell),fill=grid_color, width=1)

        if dir_rows.lower() == 'bt':
            row_num = resized.height // size_cell - 1 + start_row - l 
        else:
            row_num = start_row + l
        
        if row_num % step == 0:
            draw.text((border - size_cell // 2, border + l * size_cell + size_cell // 2), f'{row_num}', fill=grid_color, font=font, anchor='rm')
            draw.text((width - border + size_cell // 2, border + l * size_cell + size_cell // 2), f'{row_num}', fill=grid_color, font=font, anchor='lm')

    for l in range(resized.width // size_cell):
        draw.line((border + l * size_cell, border) + (border + l * size_cell, height - border), fill=grid_color, width=1)

        if dir_cols.lower() == 'rl':
            col_num = resized.width // size_cell - 1 + start_row - l 
        else:
            col_num = start_col + l

        if col_num % step == 0:
            draw.text((border + l * size_cell + size_cell // 2, border - size_cell // 2), f'{col_num}', fill=grid_color, font=font, anchor='ms')
            draw.text((border + l * size_cell + size_cell // 2, height - border +  size_cell // 2), f'{col_num}', fill=grid_color, font=font, anchor='mt')

    draw.line((border, border + resized.height) + (width - border, border + resized.height), fill=grid_color, width=1)
    draw.line((border + resized.width, border) + (border + resized.width, height - border), fill=grid_color, width=1)

    return background