"""One uploader for every IRW Redivis dataset. See red_up/README.md."""

__all__ = ["main"]


def main(argv=None):
    from .cli import main as _main

    return _main(argv)
