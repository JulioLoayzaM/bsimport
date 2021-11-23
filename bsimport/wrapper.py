"""This module provides an incomplete wrapper for Bookstack's API."""
# bsimport/wrapper.py

import requests

from typing import Any, Dict, List, NamedTuple, Optional

from bsimport import (
    DESC_TOO_LONG_ERROR, NAME_TOO_LONG_ERROR, REQUEST_ERROR, SUCCESS
)


class BResponse(NamedTuple):
    """
    Represents a response from the wrapper.
    Contains:
        - The error code.
        - The result of the operation if expected. For example,
          a list of books when calling list_books.
    """
    error: int
    result: Any


class Bookstack():
    """
    """

    def __init__(self, id: str, secret: str, url: str):
        self._header = {
            'Authorization': f"Token {id}:{secret}"
        }
        self._url = f"{url}/api"

    def _create_shelf(
        self,
        name: str,
        description: Optional[str] = None,
        books: Optional[List[int]] = None
    ) -> BResponse:
        """
        Create a new shelf.

        :param name:
            The name of the shelf (255 characters max).
        :type name: str
        :param description:
            The description (1000 characters max).
        :type description: Optional[str]
        :param books:
            A list of books to add to the shelf.
        :type books: Optional[List[int]]

        :return:
            [description]
        :rtype: BResponse
        """

        if len(name) > 255:
            pass
        if description is not None and len(description) > 1000:
            pass

        url = f"{self._url}/shelves"
        shelf = {'name': name}

        if description is not None:
            shelf['description'] = description
        if books is not None:
            shelf['books'] = books

        response = requests.post(url, json=shelf, headers=self._header)

        if response.status_code == requests.codes.ok:
            pass
        else:
            pass

    def create_book(
        self,
        name: str,
        description: Optional[str] = None,
        tags: Optional[List[Dict[str, str]]] = None
    ) -> BResponse:
        """
        Create a book.

        :param name:
            The name (max 255 characters).
        :type name: str

        :param description:
            The description (max 1000 characters).
        :type description: Optional[str]
        :param tags:
            A list of tags.
        :type tags: Optional[List[Dict[str, str]]]

        :return:
            An error code.
        :rtype: int
        :return:
            The book ID if successful, an error message otherwise.
        :rtype: Union[int, str]
        """

        if len(name) > 255:
            return BResponse(NAME_TOO_LONG_ERROR, "")
        if description is not None and len(description) > 1000:
            return BResponse(DESC_TOO_LONG_ERROR, "")

        url = f"{self._url}/books"
        book = {'name': name}

        if description is not None:
            book['description'] = description
        if tags is not None:
            book['tags'] = tags

        response = requests.post(url, json=book, headers=self._header)

        j = response.json()
        if response.status_code == requests.codes.ok:
            id = j.get('id', -1)
            return BResponse(SUCCESS, id)
        else:
            return BResponse(REQUEST_ERROR, j['error'])

    def create_chapter(
        self,
        book_id: int,
        name: str,
        description: Optional[str] = None,
        tags: Optional[List[Dict[str, str]]] = None
    ) -> BResponse:

        if len(name) > 255:
            return BResponse(NAME_TOO_LONG_ERROR, "")

        if description is not None and len(description) > 1000:
            return BResponse(DESC_TOO_LONG_ERROR, "")

        url = f"{self._url}/chapters"
        chapter = {
            'book_id': book_id,
            'name': name
        }

        if description is not None:
            chapter['description'] = description
        if tags is not None:
            chapter['tags'] = tags

        response = requests.post(url, json=chapter, headers=self._header)

        j = response.json()
        if response.status_code == requests.codes.ok:
            id = j.get('id', -1)
            return BResponse(SUCCESS, id)
        else:
            return BResponse(REQUEST_ERROR, j['error'])

    def create_page(
        self,
        name: str,
        text: str,
        tags: Optional[List[Dict[str, str]]] = None,
        book_id: Optional[int] = -1,
        chapter_id: Optional[int] = -1
    ):

        if len(name) > 255:
            return BResponse(NAME_TOO_LONG_ERROR, "")

        url = f"{self._url}/pages"
        page = {
            'name': name,
            'markdown': text
        }

        if book_id != -1:
            page['book_id'] = book_id
        else:
            page['chapter_id'] = chapter_id

        if tags is not None:
            page['tags'] = tags

        response = requests.post(url, json=page, headers=self._header)

        if response.status_code == requests.codes.ok:
            return BResponse(SUCCESS, "")
        else:
            return BResponse(REQUEST_ERROR, response.json()['error'])

    def _update_shelf(
        self,
        id: int,
        books: List[int]
    ) -> BResponse:
        """
        Updated the shelf.

        :param id:
            The ID of the shelf.
        :type id: int
        :param books:
            The list of books to add.
        :type books: List[int]

        :return:
            [description]
        :rtype: BResponse
        """

        url = f"{self._url}/shelves/{id}"
        data = {'books': books}

        response = requests.post(url, data=data, headers=self._header)

        if response.status_code == requests.codes.ok:
            pass
        else:
            pass

    def list_books(self):

        url = f"{self._url}/books"

        response = requests.get(url, headers=self._header)

        j = response.json()
        if response.status_code == requests.codes.ok:
            return BResponse(SUCCESS, j.get('data', []))
        else:
            return BResponse(REQUEST_ERROR, j['error'])
