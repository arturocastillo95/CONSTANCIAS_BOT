from pathlib import Path
import os
from PIL import Image, ImageDraw, ImageFont
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import configparser
import re

from jinja2 import Template

# import img2pdf

#Read config file
CONFIG_FILE_PATH = Path(__file__).parent / "config.ini"
CONFIG_FILE = configparser.ConfigParser()
CONFIG_FILE.read(CONFIG_FILE_PATH)

#Global variables
FONT_FOLDER = Path("FONTS/")
FONT_PATH = str(FONT_FOLDER / "Roboto-Bold.ttf")

#Some fonts have padding on top, I use this to remove the top padding 
FONT_COLOR = (64, 64, 63)

TEMPLATE_PATH = Path("TEMPLATES/")
TEMPLATE_IMAGE_PATH = TEMPLATE_PATH / "constancia_2021.png"
RESULTS_PATH = Path("RESULTS/")

#Email config variables
EMAIL_SENDER = CONFIG_FILE['EMAIL']['Sender']
EMAIL_PASSWORD = CONFIG_FILE['EMAIL']['Password']
EMAIL_PORT = CONFIG_FILE['EMAIL']['Port']
EMAIL_HOST = CONFIG_FILE['EMAIL']['Host']
EMAIL_TEMPLATE_NAME = CONFIG_FILE['EMAIL']['Template']
EMAIL_SUBJECT = CONFIG_FILE['EMAIL']['Subject']
EMAIL_TEMPLATE_PATH = Path("EMAIL_TEMPLATES/")
EMAIL_TEMPLATE_FILE = EMAIL_TEMPLATE_PATH / EMAIL_TEMPLATE_NAME


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

def generate_certificate(data, field_list, template_image_path=TEMPLATE_IMAGE_PATH, result_path=RESULTS_PATH, font_path=FONT_PATH, font_color=FONT_COLOR, email_template=EMAIL_TEMPLATE_FILE, email_subject=EMAIL_SUBJECT, email_sender=EMAIL_SENDER, email_password=EMAIL_PASSWORD, email_port=EMAIL_PORT, email_host=EMAIL_HOST):
    #Initiate variables
    result_name = data['name'] + " - " + data['course'] + ".jpg"
    result_image_path = result_path / result_name

    #Check if the template exists
    if not os.path.exists(template_image_path):
        print("Template not found")
        return

    #Check if the result folder exists
    if not os.path.exists(result_path):
        os.mkdir(result_path)

    #Initiate image
    image = Image.open(template_image_path)

    #For each field on field_list, add the text to the image
    for field in field_list:
        field_type = field['field_type']

        match field_type:
            case 'text':
                topX = int(field['topX'])
                topY = int(field['topY'])
                bottomX = int(field['bottomX'])
                bottomY = int(field['bottomY'])
                padding_percent = float(field['padding_percent'])
                alignment = field['alignment']

                text = str(data[field['field_name']])

                image = add_text_overlay(image, text, font_path, font_color, alignment, topX, topY, bottomX, bottomY, padding_percent)
            case _:
                pass

    #Save the image as jpeg
    image.convert('RGB').save(result_image_path, 'JPEG')
    print("Generated certificate for " + result_name)

    #check if email is not empty and if it is a string and if email is valid
    if data['email'] != '' and isinstance(data['email'], str) and re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
        reciever_email = data['email']
        body = mail_template_body(email_template, data)
        send_email(reciever_email, email_subject, body, result_image_path ,email_sender, email_password, email_port, email_host)
        print("Sent email to " + reciever_email)

def generate_certificates(csv_path, field_list):
    dict_list = csv_to_dict(csv_path)

    for dict in dict_list:
        generate_certificate(dict, field_list)

def send_email(reciever, subject, body, attachment_path ,sender=EMAIL_SENDER, password=EMAIL_PASSWORD, port=EMAIL_PORT, host=EMAIL_HOST, email_body_template=EMAIL_TEMPLATE_PATH):
    #Initiate message variables
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = reciever
    msg['Subject'] = subject
    msg['Bcc'] = sender

    #Initiate body
    msg.attach(MIMEText(body, 'html'))

    #File attachment
    with open(attachment_path, 'rb') as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
    
    encoders.encode_base64(part)

    #Leave only attachment filename without full path
    filename = os.path.basename(attachment_path)

    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(part)

    #Initiate email server
    server = smtplib.SMTP(host, port)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(sender, password)
    server.sendmail(sender, reciever, msg.as_string())
    server.close()

def mail_template_body(template_path, data):
    #Initiate variables
    template_body = ""

    #Open the template file
    with open(template_path, 'r') as template_file:
        template_body = template_file.read()

    template = Template(template_body)
    return template.render(data)

def main():

    #Generate certificates
    data_csv = input("Enter the path to the csv file: ")

    TEMPLATE_IMAGE = TEMPLATE_PATH / "constancia_2021.png"
    TEMPLATE_SETTINGS = TEMPLATE_PATH / (TEMPLATE_IMAGE.name.split(".")[0] + ".csv")

    #Getting the settings from the csv
    fields = csv_to_dict(TEMPLATE_SETTINGS)

    #Generate the certificates
    generate_certificates(data_csv, fields)

if __name__ == "__main__":
    main()