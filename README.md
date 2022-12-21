# bsimport

A Python tool for importing Markdown files to a
[Bookstack](https://www.bookstackapp.com) instance.

## Important notice

This project is no longer maintained. I don't use Bookstack anymore so I'm not
sure if it still works: if you have any feedback, please share it by opening an
issue.

## Motivation

I currently use [Obsidian](https://obsidian.md/) for all my note-taking needs.
I wanted to test Bookstack with my existing notes, and since it has an API, I
created this tool to import them.

I used [Typer](https://typer.tiangolo.com/) to create the CLI, and implemented
my own incomplete wrapper of the API.

## Features

- Import a single file or an entire directory:
    - A single file is imported as a page, so it will ask for the ID of the book
      you want to add the page to. You can list your accessible books with
      `python -m bsimport list-books`.
    - A directory is imported as a book: any Markdown files found directly
      inside will be imported as pages of this book.
        - If a subdirectory is found, it will be imported as a chapter, and any
          Markdown files inside it will be imported as pages of that chapter.
        - If a subdirectory of a subdirectory is found, it will be completely
          ignored, even if it contains Markdown files.

- Support for tags: Obsidian uses a [YAML front
  matter](https://help.obsidian.md/Advanced+topics/YAML+front+matter) to add
  tags and other information at the top of the page. Currently, only tags
  created with the format `tags: [tag1, tag2, tag3]` are supported.  This means
  the following YAML list format **is not** supported:
  ```YAML
  tags:
  - tag1
  - tag2
  - tag3
  ```
    - Additionally, any other front matter key such as `aliases` will be ignored.

- The API token and Bookstack URL are saved in a configuration file. You can get
  the path to the file with `python -m bsimport where`.

## Usage

- Get the API token:
  - Login to your Bookstack instance.
  - Edit your profile.
  - At the bottom of the page, create a new token.
    Save both the ID and the secret.

- Install the package with:
  ```bash
  python3 -m pip install bsimport
  ```

- Run the `init` command:
  ```bash
  python -m bsimport init
  ```
  It will ask you for the token ID and secret, as well as the URL to your
  Bookstack.

- Then import your files with:
  ```bash
  python -m bsimport import /path/to/file
  ```

## To modify the code

- Download or clone the code.

- (Optional but recommended) Create a virtual environment: see
  https://docs.python.org/3/library/venv.html.
  Example:
    ```bash
    python3 -m venv .venv
    ```

- Install the dependencies:
  ```bash
  python -m pip install -r requirements.txt -r dev-requirements.txt
  ```
