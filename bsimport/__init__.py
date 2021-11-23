"""Top-level package for bsimport."""
# bsimport/__init__.py

__app_name__ = "bsimport"
__version__ = "0.1.0"

(
    SUCCESS,
    CONF_DIR_ERROR,
    CONF_FILE_ERROR,
    CONF_WRITE_ERROR,
    NO_FILE_ERROR,
    EXT_ERROR,
    FILE_READ_ERROR,
    EMPTY_FILE_ERROR,
    NAME_TOO_LONG_ERROR,
    DESC_TOO_LONG_ERROR,
    REQUEST_ERROR,
    NO_ID_ERROR
) = range(12)

ERRORS = {
    CONF_DIR_ERROR: "config directory error",
    CONF_FILE_ERROR: "config file error",
    CONF_WRITE_ERROR: "error writing to config file",
    NO_FILE_ERROR: "config file doesn't exist",
    EXT_ERROR: "file extension error",
    FILE_READ_ERROR: "error reading file",
    EMPTY_FILE_ERROR: "file is empty",
    NAME_TOO_LONG_ERROR: "the name is too long (max 255 characters)",
    DESC_TOO_LONG_ERROR: "the description is too long (max 1000 characters)",
    REQUEST_ERROR: "API request error",
    NO_ID_ERROR: "no book or chapter ID provided"
}
