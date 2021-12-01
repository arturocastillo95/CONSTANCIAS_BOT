from pathlib import Path
import shutil
import os
from typing import Match
from PIL import Image, ImageDraw, ImageFont
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
# import img2pdf

#Global variables
FONT_FOLDER = Path("FONTS/")
FONT_PATH = str(FONT_FOLDER / "Roboto-Bold.ttf")

#Some fonts have padding on top, I use this to remove the top padding 
FONT_PADDING_PERCENT = 0.21
FONT_COLOR = (64, 64, 63)

TEMPLATE_PATH = Path("TEMPLATES/")
RESULTS_PATH = Path("RESULTS/")


def text_sizer(txt, font, max_width, max_height, padding_percent=0):
    finalsize = 1
    while font.getsize(txt)[0] < max_width and font.getsize(txt)[1] * (1-padding_percent) < max_height:
        finalsize += 1
        font = ImageFont.truetype(FONT_PATH, finalsize)
    finalsize -= 1
    return finalsize

def add_text_overlay(image, text, font_path, font_color , alignment ,topX, topY, bottomX, bottomY, padding_percent=0):

    #Initiate image
    draw = ImageDraw.Draw(image)

    #Font max size
    max_width = bottomX - topX
    max_height = bottomY - topY

    #Declare variables
    font_size = 1
    font = ImageFont.truetype(font_path, font_size)

    #Finding optimal size
    font_size = text_sizer(text, font, max_width, max_height, padding_percent=padding_percent)
    font = ImageFont.truetype(font_path, font_size)

    #Getting the final text size 
    w, h = draw.textsize(text, font)

    #For Y we get the true height of the font without the padding -> h minus h * padding percent
    y_position = topY - (h*padding_percent) + ((max_height - (h-(h*padding_percent)))/2)

    #Adding the text to image
    match alignment:
        case 'left':
            draw.text((topX, y_position), text, fill=font_color, font=font, spacing=0)
            return image

        case 'center':
            x_position = topX + ((max_width - w)/2)
            draw.text((x_position, y_position), text, fill=font_color, font=font, spacing=0)
            return image

        case 'right':
            x_position = bottomX - w
            draw.text((x_position, y_position), text, fill=font_color, font=font, spacing=0)
            return image

    return image

def add_image_overlay(image, image_overlay_path, alignment, topX, topY, bottomX, bottomY):
    #Initiate image
    draw = ImageDraw.Draw(image)

    #Getting the image
    img = Image.open(image_overlay_path)

    #Getting the size of the image
    img_width, img_height = img.size

    #For X we get the true width of the image -> img_width
    x_position = topX + ((bottomX - topX) - img_width)/2

    #For Y we get the true height of the image -> img_height
    y_position = topY + ((bottomY - topY) - img_height)/2

    #Adding the image to the image
    match alignment:
        case 'left':
            draw.bitmap((x_position, y_position), img, fill=(255, 255, 255))
            return image

        case 'center':
            draw.bitmap((x_position, y_position), img, fill=(255, 255, 255))
            return image

        case 'right':
            draw.bitmap((x_position, y_position), img, fill=(255, 255, 255))
            return image

    return image

def csv_to_dict(csv_path):
    df = pd.read_csv(csv_path)
    dict_list = []
    for index, row in df.iterrows():
        dict_list.append(row.to_dict())
    return dict_list

def main():
    example_data = {'name': 'Juanito Perez', 'rfc': 'PEPE123456789', 'course': 'Ingenieria en Sistemas', 'area': 'Sistemas', 'dpc':'5', 'duration': '1', 'expositor': 'Juanito Perez'}


    TEMPLATE_IMAGE = TEMPLATE_PATH / "constancia_2021.png"
    TEMPLATE_SETTINGS = TEMPLATE_PATH / (TEMPLATE_IMAGE.name.split(".")[0] + ".csv")

    #Getting the settings from the csv
    fields = csv_to_dict(TEMPLATE_SETTINGS)

    #Duplicating the template image
    new_file_path = RESULTS_PATH / (example_data['name'] + ' - ' + example_data['course'] + ".jpg")

    image = Image.open(TEMPLATE_IMAGE)

    #Iterate over the settings
    for field in fields:
        #Getting the coordinates
        topX = int(field['topX'])
        topY = int(field['topY'])
        bottomX = int(field['bottomX'])
        bottomY = int(field['bottomY'])

        #Getting the alignment
        alignment = field['alignment']

        #Getting the padding
        padding_percent = float(field['padding_percent'])

        #Getting the text
        text = example_data[field['field_name']]

        #Adding the text to the image
        image = add_text_overlay(image, text, FONT_PATH, FONT_COLOR, alignment, topX, topY, bottomX, bottomY, padding_percent)
    
    #save the image as a jpg
    image.convert('RGB').save(new_file_path)

if __name__ == "__main__":
    main()