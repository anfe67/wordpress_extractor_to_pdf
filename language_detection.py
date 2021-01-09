""" Derived from my article published here:
    http://antonio-ferraro.eu5.net/nlp-simple-language-detection-in-python/ """

import langdetect


def detect_language(text):
    """ Makes use of the library and output the most likely language in which the text is written using the
    2 letters ISO code of the language, which shall be first of the list (most probable) """

    languages = langdetect.detect_langs(text)
    # This is a list, I should return the topmost language 2 letters code in uppercase

    language = str(languages[0]).upper()
    language = language[0:2]
    return language


if __name__ == "main":
    print(detect_language("Dessiner des cercles sur le trottoir dans lequel les gens se placeront"))
