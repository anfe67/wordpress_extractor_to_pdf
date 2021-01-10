""" The module connects to a wordpress DB, defined in the configuration file and extracts all the ideas
    (idea push plugin) to provide a list of records (dictionaries). These contain also the list of
    boards and tags, and the most probable language,in which the post is written, detected by langdetect """

import os
import sys
import configparser
import atexit
import mysql.connector as msqlc

import language_detection

this = sys.modules[__name__]

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'resources/config.ini'))

this.host = config['WP_DB']['host']
this.db = config['WP_DB']['database']
this.user = config['WP_DB']['user']
this.password = config['WP_DB']['password']
this.prefix = config['WP_DB']['table_prefix']

sql_all_ideas = f"select posts.ID , " \
                f"guid as url, " \
                f"posts.post_title, " \
                f"post_content, " \
                f"post_name, " \
                f"DATE_FORMAT(post_date, '%Y-%m-%d %H:%S') as post_date," \
                f"users.user_nicename " \
                f"from {this.prefix}_posts posts inner join " \
                f"{this.prefix}_users users on posts.post_author = users.ID " \
                f"where posts.post_type ='idea'"
# DB QUERIES
# To get all posts of a certain type from the WP db

# to get number of votes for an idea (to finish with post ID)
sql_votes = f"select meta_value from {this.prefix}_postmeta where meta_key='votes' and post_id="

# to get all tags from a post where
sql_tags_boards = f"select taxonomy,name from  {this.prefix}_term_relationships tr " \
                  f"inner join {this.prefix}_term_taxonomy tt on tr.term_taxonomy_id = tt.term_id " \
                  f"inner join {this.prefix}_terms t on tt.term_taxonomy_id = t.term_id " \
                  f"where tt.taxonomy in ('boards', 'tags') and tr.object_id =  "  # Complete with post ID

# to get all images for a post (add post id)
sql_images = f"select guid from {this.prefix}_posts p where post_type = 'attachment' and post_mime_type like 'image/%' and post_parent = "

# to get the thumbnails
# Get first the thumbnail
sql_thumbnail = f"select meta_value from {this.prefix}_posts inner join {this.prefix}_postmeta " \
                f"on ID = post_id where meta_key like '%thumb%' and post_id ="
# Then get the image guid
sql_guid = f"select guid from {this.prefix}_posts where ID="

# Idea Board lookup table (Names to nice names)... ...must be correct
idea_boards = {
    "TEC": "Transports en commun",
    "OV": "Openbaar vervoer",
    "Magasins": "Magasins",
    "Winkels": "Winkels",
    "Artisans": "Artisans",
    "Vakmanschap": "Vakmanschap",
    "EVFR": "Évènements",
    "EVNL": "Evenementen",
    "HOSP": "Horeca",
    "HORECA": "Horeca",
    "PROFR": "Professions libérales",
    "PRONL": "Ondernemers en vrije beroepen",
    "AUTRES": "Autres",
    "ANDEREN": "Andere",
}


def open_db():
    """ Opens a DB, the parameters are already loaded from the configuration file
        upon importing the module
        """
    try:
        this.conn = msqlc.connect(host=this.host, database=this.db, user=this.user, password=this.password)
        return this.conn
    except msqlc.Error as ex:
        # The connection is not initialized, log the exception message
        print(ex)
        this.conn = None
        return None


def close_db():
    """ Closes the DB after use, automatically called upon module exit """

    this.conn.close()
    this.conn = None


@atexit.register
def close_down():
    """ Upon unloading the module close the DB connection """

    if this.conn is not None:
        close_db()


def ideas_extractor():
    """ conntects to the DB queries the ideas, augment them
        detect the language and then returns them as a list of dictionaries """

    open_db()

    if this.conn is not None:
        all_ideas = []
        cursor = this.conn.cursor()

        cursor.execute(sql_all_ideas)

        fields = [description[0] for description in cursor.description]
        retrieved_records = cursor.fetchall()

        cursor2 = this.conn.cursor()

        for record in retrieved_records:
            record = dict(zip(fields, record))

            # get all tags and boards
            sql_string = sql_tags_boards + str(record['ID'])
            cursor2.execute(sql_string)
            meta_records = cursor2.fetchall()
            boards = []
            tags = []
            for meta in meta_records:
                if meta[0] == "boards":
                    board = idea_boards[meta[1]]
                    boards.append(board)
                else:
                    tag = meta[1].upper().replace("#", "")
                    tags.append(tag)

            record["boards"] = boards
            record["tags"] = tags

            sql_string = sql_votes + str(record['ID'])
            cursor2.execute(sql_string)
            votes_record = cursor2.fetchone()
            if votes_record is not None:
                record["votes"] = votes_record[0]

            # Images lookup
            images= set()
            sql_string = sql_images + str(record['ID'])
            cursor2.execute(sql_string)
            image_records = cursor2.fetchall()
            for image in image_records:
                images.add(image[0])

            record['images'] = images

            # The images may also be in thumbnails
            sql_string = sql_thumbnail + str(record['ID'])
            cursor2.execute(sql_string)
            thumbnail_id = None
            thumbnail_record = cursor2.fetchone()
            if thumbnail_record is not None:
                thumbnail_id = thumbnail_record[0]

            # Fetch resource associated to thumbnail
            thumbnail_resource = None
            if thumbnail_id is not None:
                sql_string = sql_guid + str(thumbnail_id)
                cursor2.execute(sql_string)
                thumbnail_image_record = cursor2.fetchone()
                if thumbnail_image_record is not None:
                    thumbnail_resource = thumbnail_image_record[0]

            record['thumbnail'] = thumbnail_resource

            # date


            # Shall use thumbnails or images...
            # note: Text remains to be cleaned from html tags (maybe) during processing

            # Language lookup...
            record['language'] = language_detection.detect_language(record['post_content'])

            all_ideas.append(record)
        return all_ideas
    else:
        print("Database Error!")
        return None


def test_extraction():
    """ Test extraction and verifies count """

    all_ideas = ideas_extractor()

    french = 0
    dutch = 0
    for idea in all_ideas:

        if idea['language'] == 'FR':
            french += 1
        else:
            dutch += 1
        print(idea)
    print(f"There are {french} ideas in French and {dutch} ideas in Dutch.")

#if __name__ == "main":
test_extraction()

