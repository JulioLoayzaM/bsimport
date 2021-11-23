"""This module provides the bsimport's CLI."""
# bsimport/cli.py

import typer

from pathlib import Path
from typing import Any, Optional, Tuple

from bsimport import (
    ERRORS, EXT_ERROR, NO_FILE_ERROR, NO_ID_ERROR, SUCCESS,
    __app_name__, __version__, config, imp
)

app = typer.Typer()


@app.command()
def init(
    id: str = typer.Option(
        ...,
        help="",
        prompt="Enter the API token ID",
    ),
    secret: str = typer.Option(
        ...,
        help="",
        prompt="Enter the API token secret",
    ),
    url: str = typer.Option(
        ...,
        help="",
        prompt="What's the URL of your Bookstack instance?"
    )
) -> None:
    """
    Initialize the config file with the token info and
    the URL of the Bookstack instance.
    """

    error, config_path = config.init_app(id, secret, url)

    if error:
        typer.secho(
            f"Creating config file failed with {ERRORS[error]}",
            fg=typer.colors.RED
        )
        raise typer.Exit(error)

    typer.secho(
        f"The config file is {config_path}",
        fg=typer.colors.GREEN
    )


def get_importer() -> imp.Importer:
    """
    Read the config file and get an Importer instance.

    :return:
        An Importer created with the config information.
    :rtype: imp.Importer
    """

    error, info = config.read_config()

    if error == NO_FILE_ERROR:
        typer.secho(
            "No config file found, please run 'bsimport init' to setup"
            "your API keys and Bookstack URL."
        )
        raise typer.Exit(error)
    elif error:
        typer.secho(
            f"Read config file failed with: {ERRORS[error]}"
        )
        raise typer.Exit(error)

    id, secret, url = info
    return imp.Importer(id, secret, url)


@app.command()
def where() -> None:
    """
    Show where the config file is.
    """
    if not config.CONFIG_FILE_PATH.exists():
        typer.secho(
            "Config file not found, please run \"bsimport init\".",
            fg=typer.colors.RED
        )
        raise typer.Exit(1)

    typer.secho(f"Config file: {config.CONFIG_FILE_PATH}")


@app.command()
def modify(
    id: str = typer.Option(
        "",
        help="The token ID",
        prompt="Leave a field blank to keep it.\n"
        "Enter the token ID"
    ),
    secret: str = typer.Option(
        "",
        help="The token secret",
        prompt="Enter the token secret"
    ),
    url: str = typer.Option(
        "",
        help="The URL of your Bookstack instance",
        prompt="Enter the instance's URL"
    )
) -> None:
    """
    Modify the config file values (id, secret and/or URL).
    """

    if not (id or secret or url):
        typer.secho(
            "No changes to apply."
        )
        raise typer.Exit()

    error, msg = config.modify_config(id, secret, url)

    if error:
        typer.secho(
            f"Config file update failed with {ERRORS[error]}",
            fg=typer.colors.RED
        )
        raise typer.Exit(error)

    typer.secho(
        msg,
        fg=typer.colors.GREEN
    )


def import_single_file(importer: imp.Importer, path: Path):
    """
    Import a file in single-file mode, i.e. asking the user
    for a book ID.

    :param importer:
        The Importer to use.
    :type importer: imp.Importer
    :param path:
        The path to the file.
    :type path: Path
    """

    book_id = typer.prompt(
        "What's the book ID? [leave empty if you don't know]",
        default=-1,
        type=int
    )

    if book_id == -1:
        typer.secho(
            "Use 'bsimport list_books' to get a list of all "
            "accessible books and their ID."
        )
        raise typer.Exit()

    else:

        error, msg = importer.import_page(path, book_id)

        if error:
            typer.secho(
                f"Import file failed with: {ERRORS[error]}",
                fg=typer.colors.RED
            )
            typer.secho(f"Debug: {msg}")
            raise typer.Exit(error)

        typer.secho(
            f"Imported page {msg}",
            fg=typer.colors.GREEN
        )
        raise typer.Exit()


def import_file(
    importer: imp.Importer,
    path: Path,
    book_id: Optional[int] = -1,
    chapter_id: Optional[int] = -1
) -> Tuple[int, Any]:
    """
    Import a file in batch mode.

    :param importer:
        The importer to use.
    :type importer: imp.Importer
    :param path:
        The path to the file.
    :type path: Path

    :param book_id:
        The ID of the book that will hold this page.
        Required without `chapter_id`.
    :type book_id: Optional[int]
    :param chapter_id:
        The ID of the chapter that will hold this page.
        Required without `book_id`.
    :type chapter_id: Optional[int]

    :return:
        The error code.
    :rtype: int
    :return:
        The name of the page if successful, the error message otherwise.
    :rtype: str

    .. note::
        If both `book_id` and `chapter_id` are provided, `book_id`
        takes precedence.
    """

    if book_id == -1 and chapter_id == -1:
        return (NO_ID_ERROR, "")

    if book_id != -1:
        error, data = importer.import_page(path, book_id=book_id)
    else:
        error, data = importer.import_page(path, chapter_id=chapter_id)

    if error:
        return (error, data)

    name = data

    return (error, name)


def import_subdir(
    importer: imp.Importer,
    path: Path,
    book_id: int
) -> Tuple[int, Any]:
    """
    Import a directory as a chapter.

    :param importer:
        The Importer to use.
    :type importer: imp.Importer
    :param path:
        The path to the directory.
    :type path: Path
    :param book_id:
        The ID of the book the chapter will be attached to.
    :type book_id: int

    :return:
        An error code.
    :rtype: int
    :return:
        The name of the page if successful, the error message otherwise.
    :rtype: str
    """

    name = path.stem

    typer.secho(f"Creating the chapter '{name}'")

    error, data = importer.import_chapter(path, book_id)

    if error:
        typer.secho(
            f"Create chapter failed with: {ERRORS[error]}",
            fg=typer.colors.RED
        )
        return (error, data)

    chapter_id = data

    for child in path.iterdir():

        if child.is_file() and child.suffix == '.md':

            page_error, page_name = import_file(
                importer, child, chapter_id=chapter_id
            )

            if page_error:
                typer.secho(
                    f"Import page failed with: {ERRORS[page_error]}",
                    fg=typer.colors.RED
                )
                typer.secho(f"Debug: {page_name}")
                typer.secho(
                    f"Skipping page '{str(child)}'",
                    fg=typer.colors.YELLOW
                )

            else:
                typer.secho(
                    f"Imported page '{page_name}'"
                )

        else:
            continue

    return (SUCCESS, name)


def import_dir(importer: imp.Importer, path: Path):
    """
    Import a directory as a book.

    :param importer:
        The Importer to use.
    :type importer: imp.Importer
    :param path:
        The path to the directory.
    :type path: Path
    """

    name = path.stem

    typer.secho(f"Creating the book '{name}'")

    error, data = importer.import_book(path)

    if error:
        typer.secho(
            f"Create book failed with: {ERRORS[error]}"
        )
        raise typer.Exit(error)

    book_id = data

    for child in path.iterdir():

        if child.is_dir():
            subdir_error, subdir_data = import_subdir(importer, child, book_id)
            if subdir_error:
                typer.secho(
                    f"Import chapter failed with: {ERRORS[subdir_error]}",
                    fg=typer.colors.RED
                )
                typer.secho(
                    f"Skipping chapter '{str(child)}'",
                    fg=typer.colors.YELLOW
                )
            else:
                typer.secho(
                    f"Imported chapter '{subdir_data}'"
                )

        elif child.is_file() and child.suffix == '.md':
            page_error, page_data = import_file(
                importer, child, book_id=book_id
            )
            if page_error:
                typer.secho(
                    f"Import page failed with: {ERRORS[page_error]}",
                    fg=typer.colors.RED
                )
                typer.secho(
                    f"Skipping page '{str(child)}'",
                    fg=typer.colors.YELLOW
                )
            else:
                typer.secho(
                    f"Imported page '{page_data}'"
                )

        else:
            continue

    typer.secho(
        f"Imported book {name}",
        fg=typer.colors.GREEN
    )
    raise typer.Exit()


@app.command(name="import")
def import_from(
    path: Path = typer.Argument(
        ...,
        help="The directory or file to import.",
        exists=True,
        readable=True,
        resolve_path=True
    )
) -> None:
    """
    Import a directory or a file.

    You can import a single file or an entire directory, just pass the path
    and it will detect the type:

    - If a file is detected, it will be imported as a page and
    it will ask for the book ID (you can use 'bsimport list_books'
    to display the books you can access).

    - If a directory is detected, it will be imported as a book.

        - If subdirectories are detected, they will be imported as chapters.

        - If sub-subdirectories are detected, they will be ignored.
    """

    importer = get_importer()

    if path.is_dir():
        typer.secho("Directory detected, importing as book.")
        import_dir(importer, path)

    elif path.is_file():
        typer.secho("File detected, importing as page.")
        if path.suffix != '.md':
            typer.secho(
                "This doesn't seem to be a Markdown file,"
                "check the extension.",
                fg=typer.colors.YELLOW
            )
            raise typer.Exit(EXT_ERROR)
        import_single_file(importer, path)


@app.command()
def list_books() -> None:
    """
    List all the accessible books and their ID.
    """

    importer = get_importer()

    error, books = importer.list_books()

    if error:
        typer.secho(
            f"Read list of books failed with: {ERRORS[error]}",
            fg=typer.colors.RED
        )
        typer.secho(f"Debug: {books}")
        raise typer.Exit(error)

    typer.secho(
        "\nBook list:\n"
    )
    columns = (
        "ID.  ",
        "| Title  "
    )
    headers = "".join(columns)
    typer.secho(headers)

    max_length = len(max(books.values(), key=len))
    total_length = len(headers) - len(" Title  ") + max_length + 1
    typer.secho("-" * total_length)

    for k, v in books.items():
        typer.secho(
            f"{k}{(len(columns[0]) - len(str(k))) * ' '}"
            f"| {v}"
        )

    typer.secho("-" * total_length + "\n")


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    """
    Import Markdown files to your Bookstack instance using the API.
    """
    return
