from subprocess import CalledProcessError, run as run_process


def copy_to_clipboard(text: str) -> None:
    try:
        run_process(["pbcopy"], input=text, text=True, check=True)
    except (CalledProcessError, FileNotFoundError) as exc:
        raise RuntimeError(f"Nie udalo sie skopiowac do schowka: {exc}") from exc
