# Importing Required Modules
import PIL
from reportlab.pdfgen import canvas
import csv
import os
import textwrap
import requests
import database_extractor

ROOT_SITE = "https://ideessuspendues.be/idea/"

# For Language - Dutch - French
labels = {'FR' : {"post_date": "Date",
                  "tags": "Étiquettes",
                  "post_title": "Titre",
                  "boards": "Catégories",
                  "post_content": "Texte",
                  "user_nicename":"Auteur",
                  "votes": "Votes"},

          'NL' : {"post_date": "Datum",
                  "tags": "Labels",
                  "post_title": "Titel",
                  "boards":"Categorieën",
                  "post_content": "Tekst",
                  "user_nicename": "Schrijver",
                  "votes": "Votes"}
          }

def get_and_save_image(url):
    """ Get an image (well, any file really) stored at url """
    filename = os.path.basename(url)
    # filename = os.path.join('resources', filename)
    f = open(filename, 'wb')
    f.write(requests.get(url).content)
    f.close()
    return filename

def create_report_page(c, idea):
    """ Creates a page on the canvas """

    # Thumbnail Section
    # Setting th origin to (10,40)
    c.translate(10,40)
    # Inverting the scale for getting mirror Image of thumbnail
    c.scale(1,-1)
    # Inserting thumbnail into the Canvas at required position
    if idea['thumbnail'] is not None:
        file_name = get_and_save_image(idea['thumbnail'])
        c.drawImage(file_name,0,0,width=50,height=30)
        # delete the file...
        os.remove(file_name)

    elif len(idea['images']) > 0:
        file_name = get_and_save_image(list(idea['images'])[0])
        c.drawImage(file_name, 0, 0, width=50, height=30)
        # delete the file...
        os.remove(file_name)

    # Title Section
    # Again Inverting Scale For strings insertion
    c.scale(1,-1)
    # Again Setting the origin back to (0,0) of top-left
    c.translate(-10,-40)
    # Setting the font for Name title of company
    c.setFont("Helvetica-Bold",4)
    # Inserting the name of the company
    idea_title = f"{labels[idea['language']]['post_title']}: {idea['post_title']}"
    lines = textwrap.wrap(idea_title, 55, break_long_words=False)
    start_y= 20
    for idx, line in enumerate(lines):
        c.drawString(70, start_y + 4 * idx, line)

    start_y = 25 + 4 * len(lines)

    # For under lining the title
    c.line(70,start_y - 6,180,start_y - 6) # Check

    # Changing the font size for Specifying Address
    c.setFont("Helvetica",4)
    idea_autor = f"{labels[idea['language']]['user_nicename']}: {idea['user_nicename']}"
    c.drawString(70,start_y, idea_autor)
    start_y += 5
    boards = " ".join(idea['boards'])
    idea_boards = f"{labels[idea['language']]['boards']}: {boards}"
    lines = textwrap.wrap(idea_boards, 55, break_long_words=False)
    for idx, line in enumerate(lines):
        c.drawString(70, start_y + 4 * idx, line)
    start_y = start_y + 5 * len(lines)

    tags = " ".join(idea['tags'])
    idea_tags = f"{labels[idea['language']]['tags']}: {tags}"
    lines = textwrap.wrap(idea_tags, 55, break_long_words=False)
    for idx, line in enumerate(lines):
        c.drawString(70, start_y + 4 * idx, line)
    start_y = start_y + 5 * len(lines)

    # Votes
    c.setFont("Helvetica-Bold",4)
    idea_votes = f"{labels[idea['language']]['votes']}: {idea['votes']}"
    c.drawString(70, start_y, idea_votes)
    start_y += 8

    # Link
    c.setFont("Helvetica", 4)
    idea_url = f"URL: {ROOT_SITE} {idea['post_name']}/"
    c.drawString(10, start_y, idea_url)
    start_y += 4

    # Line Seprating the page header from the body
    c.line(5,start_y, 195, start_y)
    start_y += 8
    # Document Information
    # Changing the font for Document title
    c.setFont("Helvetica-Bold",5)
    idea_content_header = f"{labels[idea['language']]['post_content']}"
    c.drawString(15, start_y, idea_content_header)
    c.setFont("Helvetica",4)
    start_y += 10

    # Split the idea content in strings of a max len

    lines = textwrap.wrap(idea['post_content'], 90, break_long_words=False)
    c.roundRect(12, start_y-5, 178, 6*(len(lines)+1), 5, stroke=1,fill=0)

    for idx, line in enumerate(lines):
        c.drawString(15, start_y + 6 *idx, line)

    start_y = start_y + 4 * len(lines)

    # Images on the bottom of text, all images are boxed in a ...
    # if len(idea['images']) > 0:
    #      box_width = min(int(180 / len(idea['images']))-5, 90)
    #      for idx, image in enumerate(idea['images']):
    #         image_file = get_and_save_image(image)
    #         # Bloody reportlab flips images
    #         img = PIL.Image.open(image_file)
    #         out = img.transpose(PIL.Image.ROTATE_180)
    #         out = out.transpose(PIL.Image.FLIP_LEFT_RIGHT)
    #         out.save(f"rotated{image_file}")
    #         c.drawImage(f"rotated{image_file}", 10+idx*box_width +idx*5, start_y,
    #         width=box_width, preserveAspectRatio=True )
    #         # Delete the file...
    #         os.remove(image_file)
    #         os.remove(f"rotated{image_file}")

    c.showPage()



def get_reports():
    all_ideas = database_extractor.ideas_extractor()

    c_fr= canvas.Canvas("report_fr.pdf",pagesize=(200,250),bottomup=0)
    for idea in all_ideas:
        if idea['language']=='FR':
            create_report_page(c_fr, idea)
    c_fr.save()

    c_nl= canvas.Canvas("report_nl.pdf",pagesize=(200,250),bottomup=0)
    for idea in all_ideas:
        if idea['language']=='NL':
            create_report_page(c_nl, idea)

    c_nl.save()

    fr_ideas = []
    nl_ideas = []
    # Manipulate ideas to save at CSV...
    for idea in all_ideas :
        # Flatten all lists and sets...
        idea['tags'] = " ".join(idea['tags'])
        idea['boards'] = " ".join(idea['boards'])
        idea['images'] = list(idea['images'])
        idea['images'] = " ".join(idea['images'])

        if idea['language']=="FR":
            fr_ideas.append(idea)
        else:
            nl_ideas.append(idea)

    report_csv = open('report_ideas.csv', 'w')

    w = csv.DictWriter(report_csv, all_ideas[0].keys())
    w.writeheader()
    for idea in fr_ideas:
        w.writerow(idea)
    for idea in nl_ideas:
        w.writerow(idea)

    report_csv.close()

get_reports()


