# Document ingestion and parsing module for vendor release analysis.
#
# Usage example:
#     python -m release_analysis.ingestion /path/to/watch
#
# This module watches a directory for new PDF or Word documents, extracts text,
# and segments the text into individual change entries.
#
# Dependencies:
# - watchdog
# - pdfminer.six
# - python-docx
# - spacy
#
# See README or docstring for more details.

import os  # access filesystem helpers
import time  # sleep while waiting for events
from dataclasses import dataclass  # structure parsed change information
from typing import List  # type hints for collections

from watchdog.observers import Observer  # watches filesystem for changes
from watchdog.events import FileSystemEventHandler  # handles file events

from pdfminer.high_level import extract_text as extract_pdf_text  # PDF text extraction
from docx import Document  # reading .docx files

import spacy  # NLP library used for sentence segmentation
import logging  # standard logging module

# configure simple logging to stdout
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# exported names when `from release_analysis import *` is used
__all__ = [
    "ChangeEntry",  # data object for parsed changes
    "DocumentParser",  # parser utility class
    "watch_folder",  # helper to start the watcher
]

# Load spaCy English model for sentence segmentation
try:
    nlp = spacy.load("en_core_web_sm")  # try the small English model
except OSError:
    # Fallback to a blank pipeline if the model isn't installed
    # Users should run: python -m spacy download en_core_web_sm
    nlp = spacy.blank("en")


def extract_docx_text(path: str) -> str:
    """Extract text from a docx file."""
    doc = Document(path)  # open the document
    return "\n".join(p.text for p in doc.paragraphs)  # join all paragraphs


@dataclass
class ChangeEntry:
    """Represents a single change entry parsed from a document."""

    text: str


class DocumentParser:
    """Parse documents and split them into change entries."""

    def __init__(self) -> None:
        pass  # placeholder for future configuration

    def extract_text(self, path: str) -> str:
        """Read file content based on extension."""
        if path.lower().endswith(".pdf"):
            return extract_pdf_text(path)  # handle PDFs
        if path.lower().endswith(".docx"):
            return extract_docx_text(path)  # handle Word docs
        raise ValueError(f"Unsupported file type: {path}")  # unknown format

    def segment(self, text: str) -> List[ChangeEntry]:
        """Segment raw text into change entries using spaCy."""
        doc = nlp(text)  # run NLP pipeline for sentence segmentation
        entries = [
            ChangeEntry(sent.text.strip())  # build change for each sentence
            for sent in doc.sents
            if sent.text.strip()
        ]
        return entries

    def parse(self, path: str) -> List[ChangeEntry]:
        """Extract and segment a document into changes."""
        text = self.extract_text(path)  # read file text
        return self.segment(text)  # convert text to change entries


class NewDocumentHandler(FileSystemEventHandler):
    """Watchdog handler for new documents."""

    def __init__(self, parser: DocumentParser) -> None:
        self.parser = parser  # parser used for new documents

    def on_created(self, event):  # triggered when a file appears
        if event.is_directory:
            return  # ignore directories
        if not event.src_path.lower().endswith((".pdf", ".docx")):
            return  # only process supported types
        logger.info("Detected new document: %s", event.src_path)
        changes = self.parser.parse(event.src_path)  # parse the file
        for i, change in enumerate(changes, 1):
            logger.info("Change %d: %s", i, change.text)  # output each change


def watch_folder(folder: str):
    parser = DocumentParser()  # create parser
    event_handler = NewDocumentHandler(parser)  # handle events using parser
    observer = Observer()  # set up watchdog observer
    observer.schedule(event_handler, folder, recursive=False)  # watch folder
    observer.start()  # start listening
    logger.info("Watching folder: %s for new documents...", folder)
    try:
        while True:
            time.sleep(1)  # keep thread alive
    except KeyboardInterrupt:
        logger.info("Stopping watcher...")  # user interrupted
    finally:
        observer.stop()  # stop observer
        observer.join()  # wait for thread cleanup


if __name__ == "__main__":
    import argparse  # CLI argument parsing

    parser = argparse.ArgumentParser(
        description="Watch a folder for new release documents and parse them"
    )
    parser.add_argument("folder", help="Folder path to watch")  # folder argument
    args = parser.parse_args()  # parse CLI args
    watch_folder(args.folder)  # start watching based on user input
