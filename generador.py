import pathlib
import os
from PIL import Image, ImageDraw, ImageFont
import email, smtplib, ssl
import csv
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import img2pdf

def savePdf(listS, outputname):
	outputname = os.path.splitext(outputname)[0] + ".pdf"
	with open(outputname, "wb") as f:
		f.write(img2pdf.convert(listS))

def correoSend(name, receiver_email, constanciaPath, constanciaName):
	#Email data
	smtp_server = "mail.elfiscalista.com"
	port = 587  # For starttls
	sender_email = "email@elfiscalista.com"
	password = ""

	msg = MIMEMultipart()
	msg['From'] = sender_email
	msg['To'] = receiver_email
	msg['Subject'] = "Constancia de el curso de " + constanciaName + " - El Fiscalista"
	msg["Bcc"] = sender_email

	#Mensaje
	html = """\
	<html>
	  <body>
	    <p>Buen día """ + name + """,<br><br>
	       Adjunto a este correo se encuentra la constancia de su curso.<br><br>
	       Le recordamos que puede encontrar más cursos de capacitación fiscal en nuestra página web:<br>
	       <a href="www.elfiscalista.com/cursos-online">El Fiscalista</a><br><br>
	       ¡Gracias por su preferencia!
	    </p>
	  </body>
	</html>
	"""

	#Put message
	msg.attach(MIMEText(html, "html"))

	#FILE
	filename = constanciaPath

	with open(filename, "rb") as attachment:
	    # Add file as application/octet-stream
	    # Email client can usually download this automatically as attachment
	    part = MIMEBase("application", "octet-stream")
	    part.set_payload(attachment.read())

	# Encode file in ASCII characters to send by email    
	encoders.encode_base64(part)

	# Add header as key/value pair to attachment part
	part.add_header(
	    "Content-Disposition",
	    f"attachment; filename= constancia.jpg",
	)

	msg.attach(part)

	# Create a secure SSL context

	s = smtplib.SMTP(host=smtp_server, port=port)
	s.ehlo()
	s.starttls()
	s.ehlo()
	s.login(sender_email, password)
	s.sendmail(sender_email, receiver_email, msg.as_string())
	s.close()

#Función para el tamaño del texto
def textSize(txt, font, imgWidth, maxSize):
	finalsize = 1
	while font.getsize(txt)[0] < imgWidth*maxSize and font.getsize(txt)[1] < 150:
		finalsize += 1
		font = ImageFont.truetype("Arial.ttf", finalsize)
	finalsize -= 1
	return finalsize

def addInfo(imagePath, name):
	
	#Initiate image
	image = Image.open(imagePath)
	draw = ImageDraw.Draw(image)
	imageW = image.size[0]

	#Font max size
	img_max = 0.55

	#Declare variables
	font_size = 1
	font = ImageFont.truetype("Arial.ttf", font_size)

	#Finding optimal size
	font_size = textSize(name, font, imageW, img_max)
	font = ImageFont.truetype("Arial.ttf", font_size)

	#Adjusting text size 
	w, h = draw.textsize(name, font)

	#Adding the text to image
	draw.text(((imageW - w)/2,940-(h/2)), name, fill=(0, 67, 130), font=font)

	image.show()

	return image

#Encontrar folder del programa
myPath = str(pathlib.Path(__file__).parent.absolute())

#Lista de las constancias disponibles
constanciasPath = myPath + "/CONSTANCIAS"
constancias = os.listdir(constanciasPath)
resultsPath = myPath + "/RESULTADOS"

#Formatos para el texto de la consola
class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

#Interacción de usuario
print(color.GREEN + "Bienvenido al generador de Constancias 5000 de El Fiscalista (By ACS)" + color.END)
print("¿Como quieres generar tu constancia?")
print("1.- MANUALMENTE")
print("2.- AUTOMATICO(CON .CSV)")
metodo = input(color.BOLD + "Ingresa la opción que deseas(1 o 2) >>> " + color.END)

if metodo == "1":
	num = 0
	constanciasList = []
	for i in constancias:
		if i.endswith(".jpg"):
			i = os.path.splitext(i)[0]
			num = num + 1
			constanciasList.append(i)
			print(str(num)+ ".- " + i)

	#Selección de constancia
	consNum = int(input("Seleccione el numero de la constancia que desea generar (ej: 1) >>> "))

	#Imagen base de la constancia
	curso = constanciasList[consNum - 1] + ".jpg"
	cursonom = constanciasList[consNum -1]
	imgPath = constanciasPath + "/" + curso

	#Datos de la constancia
	title = input("¿Cúal es el titulo de la persona? (ej: C.P.) >>> ")
	nom = input("¿Cúal es el nombre de la persona? >>> ")
	printname = title + " " + nom

	image = addInfo(imgPath, printname)

	saveDir = resultsPath + "/" + printname + " - " + cursonom + ".jpg"
	image.save(saveDir, "JPEG")

	correo_choice = input("Desa enviar por correo electronico (si o no) >>> ")

	if correo_choice == "si":
		mailreceptor = input("Correo del cliente >>> ")
		correoSend(printname, mailreceptor, saveDir, cursonom)
		print(color.GREEN + "Su correo ha sido enviado, gracias" + color.END)

elif metodo == "2":

	archivo_csv = input("Nombre el archivo .csv (ej: lista.csv) >> ")
	savedList = []
	with open (archivo_csv, "r") as csv_file:
		csv_reader = csv.reader(csv_file)
		next(csv_reader)
		
		for titulo, nombre, curso, correo in csv_reader:
			
			printname = titulo + " " + nombre
			imgPath = constanciasPath + "/" + curso + ".jpg"

			image = addInfo(imgPath, printname)

			saveFile = resultsPath + "/" + printname + " - " + curso + ".jpg"
			savedList.append(saveFile)
			image.save(saveFile, "JPEG")

			if correo != "":
				mailreceptor = correo
				correoSend(printname, mailreceptor, saveFile, curso)
				print(color.GREEN + "Se ha enviado la constancia de "+ nombre + " para el curso de " + curso + " al correo "+ correo + color.END)

			print(color.BLUE + "Se guardo la constancia de " + nombre + " para el curso de " + curso + color.END)

	pdfile= input("Deseas crear un archivo pdf con todas las constancias(si o no) >>> ")

	if pdfile == "si":
		savePdf(savedList, archivo_csv)
		pdfileName = os.path.splitext(archivo_csv)[0]
		print(f"Se gurdaron las constancias en la carpeta {myPath} con el nombre {pdfileName}.pdf")

else:
	print("Opción no disponible :(")

