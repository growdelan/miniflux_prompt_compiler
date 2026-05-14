---
name: codex-flow-implement-planned-batches
description: >
  Użyj, gdy trzeba wykonać wszystkie milestone ze statusem `planned` w trybie batchowym:
  grupowanie logicznie powiązanych milestone, implementacja sekwencyjna, self-review po każdym batchu,
  poprawki tylko jeśli potrzebne, finalize i push raz na końcu.
---

Cel:
- zrealizować wszystkie milestone `planned`
- ograniczyć narzut operacyjny
- zachować jakość przez review i walidację
- wykonać finalize i push tylko raz na końcu

Instrukcje:
- przeanalizuj wszystkie milestone `planned`
- pogrupuj je w batch'e po 2–3, jeśli są logicznie powiązane
- jeśli milestone jest duży, ryzykowny albo architektonicznie odrębny, wykonaj go jako osobny batch
- pokaż krótki plan batchy przed startem

Dla każdego batcha:
- realizuj milestone sekwencyjnie
- dla każdego milestone użyj `$codex-flow-implement-milestone`
- po każdym milestone wykonaj adekwatne testy dla zmienionego zakresu
- nie wykonuj finalize ani push po pojedynczym milestone

Po zakończeniu batcha:
- użyj `$codex-flow-self-review`
- jeśli review wykryje realne problemy, użyj `$codex-flow-apply-self-review-fixes`
- po fixach wykonaj ograniczoną rewalidację
- jeśli review nie wykryje istotnych problemów, nie uruchamiaj fixów na siłę

Po zakończeniu wszystkich batchy:
- wykonaj pełną walidację całości
- jeśli wszystko jest poprawne, użyj `$codex-flow-finalize-and-push-change` tylko raz dla całej paczki

Zasady:
- nie rozszerzaj zakresu milestone
- nie zgaduj niejasnych wymagań — doprecyzuj dokumentację
- minimalizuj zbędne pełne testy i zbędne operacje git
- dbaj o jakość, ale ograniczaj narzut

Wynik:
- pokaż plan batchy przed startem
- po każdym batchu krótko podsumuj wynik
- na końcu podsumuj ukończone milestone, wynik walidacji i status finalize/push
