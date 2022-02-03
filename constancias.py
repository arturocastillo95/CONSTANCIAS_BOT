from tkinter import *
import tkinter as tk
import tkinter.messagebox as messagebox
from tkinter import ttk
import tkinter.filedialog as filedialog
import generador_v2 as gn
from pathlib import Path
from PIL import Image

from datetime import datetime
from tkcalendar import Calendar, DateEntry
import locale

SIGNATURES_PATH = Path("FIRMAS/")
COURSE_DB_PATH = Path("BASE_DE_DATOS_CURSOS.csv")
GUI_ELEMENTS = Path("GUI/")
ICON = GUI_ELEMENTS / "favicon.ico"
print(ICON)
COURSE_DB = gn.csv_to_dict(COURSE_DB_PATH)
TEMPLATE_SETTINGS = gn.csv_to_dict(gn.TEMPLATE_SETTINGS)

def abrir_archivo(window, progress_label, progress_bar):
    #open file anc center button
    archivo = filedialog.askopenfilename(initialdir = "/",title = "Selecciona el archivo",filetypes = (("Archivos CSV","*.csv"),))

    if archivo != "":
        constancias = gn.csv_to_dict(archivo)

        total_constancias = len(constancias)
        current_progress = 0
        
        for constancia in constancias:
            try:
                course_data = get_course_data(constancia['course'])
                dict_data = constancia | course_data
                gn.generate_certificate(dict_data, TEMPLATE_SETTINGS)
                current_progress += 1
                progress_label.config(text="Procesando: " + str(current_progress) + "/" + str(total_constancias))
                progress_percentage = (current_progress*100)/total_constancias
                progress_bar['value'] = progress_percentage
                root.update()

            except:
                print("Error al generar la constancia")

        messagebox.showinfo("Proceso completado", "Se han generado " + str(current_progress) + " constancias")

        #close window
        window.destroy()
    else:
        messagebox.showinfo("Error", "No se ha seleccionado ningun archivo")

#Function to match the course name with the course database and return the course data
def get_course_data(course):
    for course_data in COURSE_DB:
        if course_data['course'] == course:
            return course_data

def generar_individual(window, name, email, rfc, course, date):
    
    if course=="Selecciona un curso":
        messagebox.showinfo("Error", "No se ha seleccionado ningun curso")
        return
    
    #Date to spanish locale
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    print(date)
    date = "San Luis Potosí, S.L.P. a " + date.strftime('%d %B %Y')


    #Generate the certificate
    course_data = get_course_data(course)

    dict_data = {'name': name, 'email': email, 'rfc': rfc, 'course': course, 'expositor': course_data['expositor'], 'expositor_firma': course_data['expositor_firma'], 'dpc': course_data['dpc'], 'area': course_data['area'], 'duration': course_data['duration'], 'date': date}
    result = gn.generate_certificate(dict_data, TEMPLATE_SETTINGS)

    #Open the generated certificate image file
    img = Image.open(result['image_path'])
    img.show()

    #Message box to confirm the certificate creation and if email was sent
    if result['email_sent']:
        messagebox.showinfo("Constancia generada", "Constancia generada y enviada al correo electronico " + email)
    else:
        messagebox.showinfo("Constancia generada", "Constancia generada pero no se pudo enviar el correo electronico")

    #close window
    window.destroy()

def generar_individual_window():
    #open new window
    window = Toplevel(frame)
    #center window
    root.eval(f'tk::PlaceWindow {str(window)} center')
    window.title("Generar Constancia Individual")
    window.resizable(False,False)
    window.config(bg="#100f31")

    #Add grid spacers
    spacer_1 = Label(window, text="                 ", bg="#100f31", fg="white", font=("Arial", 12)).grid(row=0, column=0)
    spacer_2 = Label(window, text="                 ", bg="#100f31", fg="white", font=("Arial", 12)).grid(row=11, column=2)
    spacer_3 = Label(window, text="                 ", bg="#100f31", fg="white", font=("Arial", 12)).grid(row=9, column=1)
    spacer_4 = Label(window, text="                 ", bg="#100f31", fg="white", font=("Arial", 12)).grid(row=13, column=1)

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

    #Get current date
    current_date = datetime.now()

    #Add date input field
    Label(window, text="Fecha de la Constancia:", bg="#100f31", fg="white", font=("Arial", 12)).grid(row=7, column=1)
    date_entry = DateEntry(window, width=30, background='darkblue', foreground='white', borderwidth=2, year=current_date.year, month=current_date.month, day=current_date.day)
    date_entry.grid(row=8, column=1)

    #Read course database and add course options
    courses = []
    for course in COURSE_DB:
        courses.append(course['course'])

    courses.sort()
    courses.insert(0, "Selecciona un curso")
    course_var = StringVar()
    course_var.set(courses[0])
    Label(window, text="Curso:", bg="#100f31", fg="white", font=("Arial", 12)).grid(row=9, column=1)
    course_menu = ttk.Combobox(window, textvariable=course_var, values=courses, width=30)
    course_menu.grid(row=10, column=1)

    #Add generate button
    generate_button = Button(window, text="Generar Constancia", command=lambda: generar_individual(window, nombre_alumno.get(), email_alumno.get(), rfc_alumno.get(), course_var.get(), date_entry.get_date()),bg="#100f31", fg="white", font=("Arial", 12))
    generate_button.grid(row=12, column=1)

def generar_multiple():
    #open a new window
    window = Toplevel(frame)
    #Center window
    root.eval(f'tk::PlaceWindow {str(window)} center')
    window.title("Generar Constancia")
    window.resizable(False,False)
    window.config(bg="#100f31")
    # window.iconbitmap("logo.ico")

    #Add progress bar
    progress_bar = ttk.Progressbar(window, orient="horizontal", length=300, mode="determinate")
    progress_bar.grid(row=4, column=1)

    #Add label
    progress_label = Label(window, text="Procesando: 0/0", bg="#100f31", fg="white", font=("Arial", 12))
    progress_label.grid(row=3, column=1)


    #Add open file button in the center with grid 
    open_button = Button(window, text="Abrir archivo", command=lambda: abrir_archivo(window, progress_label, progress_bar), bg="#100f31", fg="white", font=("Arial", 12))
    open_button.grid(row=2, column=1)

    #Grid spacers
    spacer_1 = Label(window, text="                 ", bg="#100f31", fg="white", font=("Arial", 12)).grid(row=1, column=0)
    spacer_2 = Label(window, text="                 ", bg="#100f31", fg="white", font=("Arial", 12)).grid(row=5, column=2)     

root = Tk()
root.eval('tk::PlaceWindow . center')
root.title("Constancias")
root.geometry("500x250")
root.resizable(False,False)
root.config(bg="#ffffff")
# icon_image = tk.Image("photo", file=str(ICON))
# root.tk.call('wm', 'iconphoto', root._w, icon_image)

#Frame
frame = Frame(root, bg="#100f31")
frame.pack(fill="both", expand=True)

#Add label with title
label_title = Label(frame, text="Generar Constancias", font=("Arial", 25), bg="#100f31")
label_title.pack(pady=10)

#Create 2 buttons and center them
button_individual = Button(frame, text="Individual", command=generar_individual_window, bg="#ffffff", fg="#100f31", font=("Arial", 12), relief="flat", borderwidth=0)
button_individual.pack(side="left", padx=10, pady=10)
button_multiple = Button(frame, text="Multiple", command=generar_multiple, bg="#ffffff", fg="#100f31", font=("Arial", 12), relief="flat", borderwidth=0)
button_multiple.pack(side="right", padx=10, pady=10)

root.mainloop()
