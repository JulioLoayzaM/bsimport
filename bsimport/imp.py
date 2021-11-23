"""This module provides a layer between the CLI and the API wrapper."""
# bsimport/imp.py

from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Optional, Tuple
from bsimport import EMPTY_FILE_ERROR, FILE_READ_ERROR, SUCCESS

from bsimport.wrapper import Bookstack


class IResponse(NamedTuple):
    """
    Represents a response from an Importer.
    Contains:
    - An error code.
    - The data from the request, e.g the book ID, an error message, etc.
    """
    error: int
    data: Any


class Importer():
    """
    A class to add a layer between the CLI and the wrapper.
    """

    def __init__(self, id: str, secret: str, url: str):
        self._wrapper = Bookstack(id, secret, url)

    def _parse_front_matter(
        self,
        content: List[str]
    ) -> Tuple[List[Dict[str, str]], int]:
        """
        Parse the YAML front matter in search of tags.

        :param content:
            The content of the Markdown file to parse.
        :type content: List[str]

        :return:
            The tags found, if any.
        :rtype: List[Dict[str, str]]
        :return:
            The position of the end of the front matter, if it exists.
        :rtype: int
        """

        tags = list()
        end = -1

        if not content[0].startswith('---'):
            return tags, end

        tmp = []

        for count, line in enumerate(content[1:]):
            # Found the end of the front matter
            if line.startswith('---'):
                end = count + 1
                break

            lc = line.split(':')

            # Improperly formatted or YAML list (not supported)
            if len(lc) == 1:
                continue
            # Skip all other front matter content
            if lc[0] != 'tags':
                continue

            # Retrieve the tags
            tmp = lc[1]
            tmp = tmp.rstrip().lstrip()
            tmp = tmp.rstrip(']')
            tmp = tmp.lstrip('[')
            tmp = tmp.split(', ')

        for tag in tmp:
            tags.append({'name': tag})

        return tags, end

    def _parse_file(
        self,
        content: List[str]
    ) -> Tuple[str, str, List[Dict[str, str]]]:
        """
        Parse the Markdown file to get the name from the title
        and the tags from the front matter.

        :param content:
            The content of the Markdown file to parse.
        :type content: List[str]

        :return:
            The name of the page, taken from the title of the file
            (H1 header).
        :rtype: str
        :return:
            The rest of the text, without the H1 header.
        :rtype: str
        :return:
            The tags found, if any.
        :rtype: List[Dict[str, str]]
        """
        tags, end = self._parse_front_matter(content)
        start = 0 if (end == -1) else (end + 1)

        text_start = -1
        name = ""
        for count, line in enumerate(content[start:]):
            if line.startswith('# '):
                name = line.rstrip()
                name = name.lstrip('# ')
            if line.startswith('## ') and text_start == -1:
                text_start = count + start
                break

        text = ''.join(content[text_start:])

        return name, text, tags

    def import_page(
        self,
        file_path: Path,
        book_id: Optional[int] = -1,
        chapter_id: Optional[int] = -1
    ) -> IResponse:
        """
        Parse a Markdown file and import it as a page.

        :param file_path:
            The path to the file to import.
        :type file_path: Path

        :param book_id:
            The ID of the book the page will be attached to.
            Required without `chapter_id`.
        :type book_id: Optional[int]
        :param chapter_id:
            The ID of the chapter the page will be attached to.
            Required without `book_id`.
        :type chapter_id: Optional[int]

        :return:
            An error code.
        :rtype: int
        :return:
            The name of the page if successful, the error message otherwise.
        :rtype: str
        """

        try:
            with file_path.open('r') as file:
                content = file.readlines()
        except OSError:
            return IResponse(FILE_READ_ERROR, "")

        if len(content) == 0:
            return IResponse(EMPTY_FILE_ERROR, "")

        name, text, tags = self._parse_file(content)

        if not name:
            name = file_path.stem

        if not tags:
            tags = None

        if book_id != -1:
            error, msg = self._wrapper.create_page(
                name, text, tags, book_id=book_id
            )
        else:
            error, msg = self._wrapper.create_page(
                name, text, tags, chapter_id=chapter_id
            )

        if error:
            return IResponse(error, msg)
        else:
            return IResponse(SUCCESS, name)

    def import_chapter(
        self,
        path: Path,
        book_id: int
    ) -> IResponse:
        """
        Create a chapter from the directory's name.

        :param path:
            The path to the directory.
        :type path: Path
        :param book_id:
            The ID of the book the chapter belongs to.
        :type book_id: int

        :return:
            An error code.
        :rtype: int
        :return:
            The chapter's ID if successful, the error message otherwise.
        :rtype: Union[int, str]
        """

        name = path.stem

        # description = None
        # tags = None

        error, data = self._wrapper.create_chapter(book_id, name)

        if error:
            return IResponse(error, data)
        else:
            chapter_id = data
            return IResponse(SUCCESS, chapter_id)

    def import_book(
        self,
        path: Path
    ) -> IResponse:
        """
        Create a book from the directory's name.

        :param path:
            The path to the directory.
        :type path: Path

        :return:
            An error code.
        :rtype: int
        :return:
            The book's ID if successful, the error message otherwise.
        :rtype: Union[int, str]
        """

        name = path.stem

        # description = None
        # tags = None

        error, data = self._wrapper.create_book(name)

        if error:
            return IResponse(error, data)
        else:
            book_id = data
            return IResponse(SUCCESS, book_id)

    def list_books(self) -> IResponse:
        """
        Get the list of all accessible books.

        :return:
            An error code.
        :rtype: int
        :return:
            If successful, a dictionnary of books with the book's ID
            as key and the book's name as value, the error message otherwise.
        :rtype: Union[Dict[int, str], str]
        """

        error, data = self._wrapper.list_books()

        if error:
            return IResponse(error, data)

        books = dict()
        for book in data:
            books[book['id']] = book['name']

        return IResponse(SUCCESS, books)
