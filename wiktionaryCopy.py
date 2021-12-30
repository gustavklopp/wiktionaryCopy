"""
Entry point for WiktionaryCopy add-on from Anki
"""

from __future__ import print_function
import logging
import sys
def warning(*objs):
    print("WARNING: ", *objs, file=sys.stderr)

__all__ = []


if __name__ == "__main__":
    warning(
        "WiktionaryCopy is an add-on for Anki.\n"
        "It is not intended to be run directly.\n"
        "To learn more or download Anki, please visit <http://ankisrs.net>.\n"
    )
    exit(1)

import os
from anki.hooks import addHook
from aqt.editor import Editor
from aqt import mw

config = mw.addonManager.getConfig(__name__)
origin_lang = config['origin language']
dest_lang = config['destination language']
dest_lang_field = config['destination language field']

# import wiktionarygrabber module with the actual code
import wiktionarycopy
from .fetcher import Wiktionary


""" Initialize logging """
def initLog(self):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fileHandler = logging.FileHandler('ankiwiktionarycopy.log')    
    fileHandler.setFormatter(formatter)
    fileHandler.setLevel(logging.DEBUG)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)
    streamHandler.setLevel(logging.ERROR)
    
    myLogger = logging.getLogger("ankiwiktionarycopy")
    myLogger.setLevel(logging.DEBUG)
    myLogger.addHandler(fileHandler)
    myLogger.addHandler(streamHandler)
    return myLogger
    

"""The main function"""
def wiktionaryCopy(self):
    logger = initLog(self) #Initialize logging
    logger.info('Logging started.')
    
    self.mw.checkpoint("Get info from wiktionary on the current note")

    if not dest_lang_field in mw.col.models.field_names(self.note.note_type()):
        logger.error('This add-on requires a field called "{}" (mind the capitalization) to work.'.format(
            dest_lang_field))
    else:
        entry = self.note[origin_lang]
    
        #Call the grabber method
        wik = Wiktionary(dest_lang, origin_lang)
        myWord = wik.word(entry)
        
        if myWord:
            logger.debug("Retrieved word: %s" % myWord)
        else:
            logger.warning("Could not find word %s" % entry)
    
        if myWord:
            for name in mw.col.models.field_names(self.note.note_type()):
                # Put what is from Wiktionary into the field "English"
                if name==dest_lang_field:
                    self.note[dest_lang_field] = myWord
                    
            self.stealFocus = True;
            
            '''Saving the field which has been filled'''
            def flush_field():
                if not self.addMode:  # save
                    self.note.flush()
                self.loadNote()

            self.saveNow(flush_field, keepFocus=True)
            #self.loadNote();
        else:
            logger.error("Failed to find word '{}' in {}. Please check if Wiktionary has it: {}".format(
                entry, origin_lang, "https://"+dest_lang+".wiktionary.org/wiki/"+entry))

        logger.info('Logging finished.')



''' Add the addon button to the anki Editor'''
def add_editor_button(buttons: [], editor: Editor):
    icon_path = os.path.join(mw.pm.addonFolder(), 'wiktionarycopy', 'icons', 'wiktionary.png')
    b = editor.addButton(icon_path, "wiktionarycopy", wiktionaryCopy, tip="Add fields with Wiktionary data")
    buttons.append(b)
    return buttons

addHook("setupEditorButtons", add_editor_button)
