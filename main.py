# Make a scraper that takes the popular movies from google search
# Whatismymovie.om

from tkinter.constants import CENTER, RIGHT
import PySimpleGUI as sg
import os, re, threading, webbrowser, shutil, requests
from PIL import Image

def JPG_To_PNG(link, picture_name, xsize, ysize):                           # takes in a JPG link, converts to PNG, saves PNG and deletes JPG. Returns None
    default_dir = os.getcwd()
    if not os.path.exists(default_dir + '\Temp'):
        os.mkdir('Temp')    
    os.chdir(default_dir + "\Temp")

    source_link = requests.get(link)
    if ':' in picture_name:
        picture_name = picture_name.replace(':', '-')
    with open(f"{picture_name}.jpg", 'wb') as iH:
        iH.write(source_link.content)
    
    convert_image = Image.open(f"{picture_name}.jpg")
    convert_image = convert_image.resize((xsize, ysize))
    
    convert_image.save(f"{picture_name}.png")
    os.remove(f"{picture_name}.jpg")

    os.chdir(default_dir)
    return None

default_dir = os.getcwd()



# GUI layout
layout = [ [sg.Text('Enter your movie: '), sg.Input(key='IN'), sg.Button('Search'), sg.Button('Next', visible=False), sg.Button('Quit'), sg.Text('loading..', visible=False, key=('loading'))],
           [sg.Image('', key='-movie0image-', enable_events=True), sg.Image('', key='-movie1image-', enable_events=True), sg.Image('', key='-movie2image-', enable_events=True)],
           [sg.Text('', size=(0, 1), key=('-movie0name-')), sg.Text('', size=(0, 1), key=('-movie1name-'), justification=CENTER), sg.Text('', size=(0, 1), key=('-movie2name-'), justification=RIGHT)],
           
         ]

           
screen = sg.Window('Movie Checker', layout, size=(950,600), resizable=True)

movie_0_link = ''
movie_1_link = ''
movie_2_link = ''


while True:
    event, values = screen.read()

    if event == '-movie0image-':                    # events for clicking on movie images, does nothing if empty
        if movie_0_link == '':
            continue
        webbrowser.open(movie_0_link, new=2)
    if event == '-movie1image-':
        if movie_1_link == '':
            continue
        webbrowser.open(movie_1_link, new=2)
    if event == '-movie2image-':
        if movie_2_link == '':
            continue
        webbrowser.open(movie_2_link, new=2)


    if event == sg.WIN_CLOSED or event =='Quit':    # Quits application
        break

    if event == 'Search' or event == 'IN':                           # formats and grabs search from website
        screen.refresh()
        screen['loading'].update(visible=True)
        screen['Next'].update(visible=False)                 
        search_term = screen['IN'].get()                # grabs value from inputbox, reformats for website search
        search_term = search_term.replace(' ', '+')     #   
        
        media_url = f'https://www.whatismymovie.com/results?text={search_term}' # grabs source info
        source = requests.get(media_url).text

        movie_list = list(re.findall("<h3 class='panel-title'><a href='(.+)'>(.+)</a></h3>", source)) # Regex search, and then changes list of tuples to list of lists
        movie_list = [list(x) for x in movie_list]
        
        for i in movie_list:                     # loop that changes each movie index [0] to full URL in the list
            i[0] = f"https://www.whatismymovie.com/{i[0]}"   



        movie_counter = 0
        for i in range(3):
            screen.refresh()
            current_link = movie_list[i][0]
            current_movie = movie_list[i][1]

            if i == 0:                          #changes image links to the movie link
                movie_0_link = current_link
            elif i == 1:
                movie_1_link = current_link
            elif i == 2:
                movie_2_link = current_link

            movie_page_src = requests.get(current_link).text     # request source of website 
            search = re.search('<img src="(.+?)">', movie_page_src) # Regex search for image in the source
            image_id = search.group(1)

            image_source = f"https://www.whatismymovie.com{image_id}" # direct link to image

            threading.Thread(target=JPG_To_PNG(image_source, current_movie, 300, 400))  # threaded to decrease runtime
            

            if ':' in current_movie:
                current_movie = current_movie.replace(':', '-')  # handles movies with ':' in title

            os.chdir(os.getcwd()+ '\Temp')
            screen[f"-movie{i}image-"].update(f"{current_movie}.png")       # pushes movie image to screen
            screen[f"-movie{i}name-"].update(f"{current_movie}      |    ") # pushes movie title to screen
            os.chdir(default_dir)
            
            movie_counter += 1


        screen['loading'].update(visible=False)
        screen['Next'].update(visible=True)
    
    if event == 'Next' and movie_counter >= 3:
        for i in range(3):
            screen.refresh()
            current_link = movie_list[i + movie_counter][0]
            current_movie = movie_list[i + movie_counter][1]
            if i == 0:
                movie_0_link = current_link
            elif i == 1:
                movie_1_link = current_link
            elif i == 2:
                movie_2_link = current_link

            movie_page_src = requests.get(current_link).text     # request source of website 
            search = re.search('<img src="(.+?)">', movie_page_src) # Regex search for image in the source
            image_id = search.group(1)

            image_source = f"https://www.whatismymovie.com{image_id}" # direct link to image

            threading.Thread(target=JPG_To_PNG(image_source, current_movie, 300, 400))         # threaded to run faster
            

            if ':' in current_movie:
                current_movie = current_movie.replace(':', '-') # handles movies with ':' in title

            os.chdir(os.getcwd()+ '\Temp')
            screen[f"-movie{i}image-"].update(f"{current_movie}.png")       # pushes movie image to screen
            screen[f"-movie{i}name-"].update(f"{current_movie}      |    ")
            os.chdir(default_dir)

        movie_counter += 3
        



os.chdir(default_dir)
shutil.rmtree(os.getcwd() + '\Temp')
screen.close()
