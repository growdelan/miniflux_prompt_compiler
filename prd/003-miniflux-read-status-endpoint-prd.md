# PRD - Poprawny endpoint oznaczania wpisow Miniflux jako read

## 1. Cel produktu

Celem jest usuniecie z workflow **Miniflux Prompt Compiler** blednych prob oznaczania wpisow jako przeczytane, ktore generuja `400 Bad Request` w logach Miniflux.

Zmiana ma zachowac dotychczasowa semantyke aplikacji:

* wpisy przetworzone z sukcesem sa oznaczane jako `read`,
* wpisy nieprzetworzone lub pominiete pozostaja `unread`,
* CLI i konfiguracja pozostaja bez zmian.

## 2. Problem do rozwiazania

Adapter Miniflux probowal kilku wariantow API do oznaczania wpisu jako przeczytanego. Pierwszy wariant wysylal:

```text
PUT /v1/entries?status=read
```

z payloadem zawierajacym `entry_ids`.

Aktualna instancja Miniflux odrzuca taki request jako `400 Bad Request` z komunikatem o niepoprawnym statusie. Kod dopiero po tym bledzie przechodzil do poprawnego endpointu. W praktyce kazdy poprawnie przetworzony wpis mogl zostawiac w logach Miniflux niepotrzebny blad.

## 3. Zakres funkcjonalny (In-Scope)

### 3.1 Uzycie oficjalnego endpointu Update Entries

Funkcja oznaczania pojedynczego wpisu jako przeczytanego ma uzywac od razu endpointu:

```text
PUT /v1/entries
Content-Type: application/json
```

z payloadem:

```json
{
  "entry_ids": [123],
  "status": "read"
}
```

### 3.2 Usuniecie fallbackow generujacych oczekiwane bledy

Z kodu nalezy usunac sekwencje prob, ktora celowo zaczyna od endpointu odrzucanego przez Miniflux.

Bledy HTTP i sieciowe nadal maja byc mapowane na `MinifluxError`, tak aby orkiestracja mogla zalogowac problem oznaczania `read` bez przerywania calego przebiegu.

### 3.3 Test kontraktu API

Test jednostkowy ma weryfikowac, ze `mark_entry_read()` wykonuje pojedyncze wywolanie:

* metoda: `PUT`
* URL: `/v1/entries`
* body: `{"entry_ids": [...], "status": "read"}`

## 4. Poza zakresem (Out-of-Scope)

Poza zakresem tej zmiany pozostaje:

* zmiana momentu oznaczania wpisow jako `read`,
* batchowanie wielu wpisow w jednym requestcie,
* zmiana obslugi `unread`,
* zmiana trybu `--links`,
* zmiana ekstrakcji tresci lub fallbackow artykulowych.

## 5. Wplyw na interfejsy i kontrakty

### 5.1 CLI

Bez zmian:

* brak nowych flag,
* brak zmiany komend uruchomieniowych,
* brak zmiany konfiguracji `.env`.

### 5.2 Integracja Miniflux

Zmieniony zostaje kontrakt adaptera Miniflux dla oznaczania wpisow:

* stary wariant probny `PUT /v1/entries?status=read` nie jest juz uzywany,
* jedynym wariantem dla statusu `read` jest oficjalny `PUT /v1/entries`.

## 6. Kryteria akceptacji

* [ ] `mark_entry_read()` wysyla `PUT /v1/entries`.
* [ ] Payload zawiera `entry_ids` jako liste oraz `status: "read"`.
* [ ] Funkcja nie wykonuje probnego requestu do `/v1/entries?status=read`.
* [ ] Testy jednostkowe pokrywaja poprawny endpoint i body.
* [ ] Dotychczasowe workflow sukcesow, porazek i trybu `--links` pozostaja bez zmian.

## 7. Wartosc biznesowa

* Czystsze logi Miniflux bez oczekiwanych bledow `400`.
* Latwiejsza diagnoza realnych problemow integracyjnych.
* Mniej zbednego ruchu HTTP przy kazdym oznaczanym wpisie.
* Zgodnosc z oficjalnym kontraktem API Miniflux.
