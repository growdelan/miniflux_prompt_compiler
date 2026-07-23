# Aktualny stan
- co dziala: pobieranie unread z Miniflux, ekstrakcja artykulow przez Miniflux fetch-content z fallbackiem Jina/Playwright (w tym po timeoutach fetch-content) i YouTube z timeoutami, normalizacja HTML z Miniflux do markdown przez trafilatura wraz z cleanupem portalowego noise, prompty z chunkowaniem, odporne liczenie zewnetrznej tresci zawierajacej sekwencje specjalne `tiktoken`, etykiety tokenow, tryb interaktywny (Enter przed kopiowaniem nawet jednego promptu) i --no-interactive, tryb `--links` zwracajacy same URL-e wpisow artykulowych bez pobierania tresci, konfiguracja MINIFLUX_BASE_URL, logowanie przez logging oraz oznaczanie `read` dopiero po dostarczeniu wyniku przez oficjalny endpoint `PUT /v1/entries`.
- co jest skonczone: milestone'y 0.5-24 w ROADMAP.md.
- co jest nastepne: brak planned milestone'ow; kolejne kroki po nowym PRD/ustaleniach.
- blokery: brak.
