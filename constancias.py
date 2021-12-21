from tkinter import *
import tkinter.messagebox as messagebox
from tkinter import ttk
import tkinter.filedialog as filedialog
import generador_v2 as gn
from pathlib import Path

SIGNATURES_PATH = Path("FIRMAS/")
COURSE_DB_PATH = Path("BASE_DE_DATOS_CURSOS.csv")
GUI_ELEMENTS = Path("GUI/")
COURSE_DB = gn.csv_to_dict(COURSE_DB_PATH)

def abrir_archivo(window):
    #open file anc center button
    archivo = filedialog.askopenfilename(initialdir = "/",title = "Selecciona el archivo",filetypes = (("Archivos CSV","*.csv"),))
    if archivo != "":
        #Generate the certificates
        gn.generate_certificates(archivo)
        #close window
        window.destroy()
    else:
        messagebox.showinfo("Error", "No se ha seleccionado ningun archivo")

def generar_individual_imagen(window, name, email, rfc, course, expositor, firma):
    #Generate the certificate
    dict_data = {'name': name, 'email': email, 'rfc': rfc, 'course': course, 'expositor': expositor, 'expositor_firma': firma, 'dpc': '5', 'area': 'FISCAL', 'duration':'5',}
    gn.generate_certificate(dict_data, gn.csv_to_dict(gn.TEMPLATE_SETTINGS))

    #close window
    window.destroy()


def generar_individual():
    #open new window
    window = Toplevel(frame)
    window.title("Generar Constancia Individual")
    window.resizable(False,False)
    window.config(bg="#100f31")
    window.iconbitmap("logo.ico")

    #Add grid spacers
    spacer_1 = Label(window, text="                 ", bg="#100f31", fg="white", font=("Arial", 12)).grid(row=0, column=0)
    spacer_2 = Label(window, text="                 ", bg="#100f31", fg="white", font=("Arial", 12)).grid(row=15, column=2)
    spacer_3 = Label(window, text="                 ", bg="#100f31", fg="white", font=("Arial", 12)).grid(row=13, column=1)

    #Add name input field
    Label(window, text="Nombre del Alumno:", bg="#100f31", fg="white", font=("Arial", 12)).grid(row=1, column=1)
    nombre_alumno = StringVar()
    Entry(window, textvariable=nombre_alumno, width=30).grid(row=2, column=1)

    #Add email input field
    Label(window, text="Correo Electronico:", bg="#100f31", fg="white", font=("Arial", 12)).grid(row=3, column=1)
    email_alumno = StringVar()
    Entry(window, textvariable=email_alumno, width=30).grid(row=4, column=1)

    #Add RFC input field
    Label(window, text="RFC del Alumno:", bg="#100f31", fg="white", font=("Arial", 12)).grid(row=5, column=1)
    rfc_alumno = StringVar()
    Entry(window, textvariable=rfc_alumno, width=30).grid(row=6, column=1)

    #Add course input field
    Label(window, text="Curso:", bg="#100f31", fg="white", font=("Arial", 12)).grid(row=7, column=1)
    curso_alumno = StringVar()
    Entry(window, textvariable=curso_alumno, width=30).grid(row=8, column=1)

    #Add expositor input field
    Label(window, text="Expositor:", bg="#100f31", fg="white", font=("Arial", 12)).grid(row=9, column=1)
    expositor_curso = StringVar()
    Entry(window, textvariable=expositor_curso, width=30).grid(row=10, column=1)

    #Add signature image input field
    Label(window, text="Firma del Expositor:", bg="#100f31", fg="white", font=("Arial", 12)).grid(row=11, column=1)
    #List of all images in signatures folder
    firmas_images = [x for x in SIGNATURES_PATH.iterdir() if x.is_file()]
    print(firmas_images)
    firmas_images = [x for x in firmas_images if x.suffix == ".png"]
    firmas_images = [str(x.name) for x in firmas_images]
    #Add dropdown menu with firmas images
    firma_expositor = StringVar()
    firma_expositor.set(firmas_images[0])
    firma_menu = ttk.Combobox(window, textvariable=firma_expositor, values=firmas_images, width=30)
    firma_menu.grid(row=12, column=1)

    #Add generate button
    generate_button = Button(window, text="Generar Constancia", command=lambda: generar_individual_imagen(window, nombre_alumno.get(), email_alumno.get(), rfc_alumno.get(), curso_alumno.get(), expositor_curso.get(), firma_expositor.get()), bg="#100f31", fg="white", font=("Arial", 12))
    generate_button.grid(row=14, column=1)

def generar_multiple():
    #open a new window
    window = Toplevel(frame)
    window.title("Generar Constancia")
    window.resizable(False,False)
    window.config(bg="#100f31")
    window.iconbitmap("logo.ico")

    #Add open file button in the center with grid 
    open_button = Button(window, text="Abrir archivo", command=lambda: abrir_archivo(window), bg="#100f31", fg="white", font=("Arial", 12))
    open_button.grid(row=2, column=1)

    #Add progress bar
    progress = ttk.Progressbar(window, orient="horizontal", length=300, mode="determinate")
    progress.grid(row=4, column=1)

    #Add label
    progress_label = Label(window, text="Procesando: 0/0", bg="#100f31", fg="white", font=("Arial", 12))
    progress_label.grid(row=3, column=1)

    #Grid spacers
    spacer_1 = Label(window, text="                 ", bg="#100f31", fg="white", font=("Arial", 12)).grid(row=1, column=0)
    spacer_2 = Label(window, text="                 ", bg="#100f31", fg="white", font=("Arial", 12)).grid(row=5, column=2)    
    





root = Tk()
root.title("Constancias")
root.geometry("500x250")
root.resizable(False,False)
root.config(bg="#ffffff")
root.iconbitmap("logo.ico")

#Frame
frame = Frame(root, bg="#100f31")
frame.pack(fill="both", expand=True)

#Add label with title
label_title = Label(frame, text="Generar Constancias", font=("Arial", 25), bg="#100f31")
label_title.pack(pady=10)

#Create 2 buttons and center them
button_individual = Button(frame, text="Individual", command=generar_individual, bg="#ffffff", fg="#100f31", font=("Arial", 12), relief="flat", borderwidth=0)
button_individual.pack(side="left", padx=10, pady=10)
button_multiple = Button(frame, text="Multiple", command=generar_multiple, bg="#ffffff", fg="#100f31", font=("Arial", 12), relief="flat", borderwidth=0)
button_multiple.pack(side="right", padx=10, pady=10)

root.mainloop()
