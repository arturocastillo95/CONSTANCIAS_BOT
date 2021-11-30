import pathlib
import os
from PIL import Image, ImageDraw, ImageFont
import email, smtplib, ssl
import csv
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# import img2pdf

#Global variables
FONT_PATH = "FONTS/Roboto-Bold.ttf" 

def text_size(txt, font, imgWidth, maxSize):
	finalsize = 1
	while font.getsize(txt)[0] < imgWidth*maxSize and font.getsize(txt)[1] < 150:
		finalsize += 1
		font = ImageFont.truetype(FONT_PATH, finalsize)
	finalsize -= 1
	return finalsize

def add_text_overlay(image_path, text):

	#Initiate image
	image = Image.open(image_path)
	draw = ImageDraw.Draw(image)
	imageW = image.size[0]

	#Font max size
	img_max = 0.55

	#Declare variables
	font_size = 1
	font = ImageFont.truetype("Arial.ttf", font_size)

	#Finding optimal size
	font_size = text_size(text, font, imageW, img_max)
	font = ImageFont.truetype("Arial.ttf", font_size)

	#Adjusting text size 
	w, h = draw.textsize(text, font)

	#Adding the text to image
	draw.text(((imageW - w)/2,940-(h/2)), text, fill=(0, 67, 130), font=font)

	image.show()

	return image

def main():
    print('Hello!')

if __name__ == "__main__":
    main()