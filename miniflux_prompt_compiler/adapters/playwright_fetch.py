import logging
import re

from miniflux_prompt_compiler.types import ContentFetchError


def fetch_article_with_playwright(url: str, timeout: int = 20) -> str:
    try:
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise ContentFetchError("Brak zaleznosci playwright w srodowisku.") from exc

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            try:
                logging.info("Playwright: start %s", url)
                page.goto(url, wait_until="domcontentloaded", timeout=timeout * 1000)
            except PlaywrightTimeoutError as exc:
                logging.info("Playwright: failed (timeout)")
                raise ContentFetchError(f"Playwright timeout: {exc}") from exc

            consent_pattern = re.compile(
                r"^(accept|agree|accept all|i agree|zgadzam sie|akceptuj)$",
                re.IGNORECASE,
            )
            try:
                consent_button = page.get_by_role("button", name=consent_pattern)
                if consent_button.count() > 0:
                    consent_button.first.click(timeout=2000)
                    logging.info("Playwright: cookie-consent clicked")
            except Exception:
                pass

            content = page.evaluate(
                "() => (document.body && document.body.innerText) || ''"
            )
            if not isinstance(content, str) or not content.strip():
                logging.info("Playwright: failed (empty content)")
                raise ContentFetchError("Pusta tresc z Playwrighta.")
            logging.info("Playwright: success (%d)", len(content))
            return content
    except ContentFetchError:
        raise
    except Exception as exc:
        logging.info("Playwright: failed (%s)", exc)
        raise ContentFetchError(
            f"Nie udalo sie pobrac tresci Playwright: {exc}"
        ) from exc
