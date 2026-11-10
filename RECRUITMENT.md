# Igor — rozmowa rekrutacyjna do Szkoły w Chmurze

## Wersja WWW / ProLiant

Dodano host renderujący tę samą prezentację na serwerze oraz dwa oddzielne widoki
przeglądarkowe: odbiorcy i prezentera. Panel działa na telefonie bez aplikacji Android.
Lokalny test: `.venv/bin/python -m live_explain.web --port 18766`.
Widok odbiorcy: `http://127.0.0.1:18766/`; prezenter: `http://127.0.0.1:18766/presenter/`.

Docelowe adresy to `https://prol.aridlin.pl/live-explain/` oraz
`https://prol.aridlin.pl/live-explain/presenter/`, za istniejącym logowaniem portalu.
**2026-10-27: aplikacja, usługa, Caddy i oba wpisy w indeksie zostały wdrożone.**
Publiczne HTTPS wymaga dotychczasowego logowania portalu (sprawdzono 401 bez logowania).
Sterowanie sprawdzono na działającej usłudze; końcowy test w zalogowanej przeglądarce WAN
i próba fizycznego telefonu wymagają logowania użytkownika. Sesja testowa przeglądarki
nie miała poświadczeń portalu. Stan: `artifacts/proliant-deploy/deployment-status.json`.
Procedura i konfiguracja są w `deploy/PROLIANT.md`; paczka w `artifacts/proliant-deploy/`.
Dotychczasowy APK pozostaje klientem LAN. Dostęp przez WAN zapewnia panel przeglądarkowy.

Rozmowa: **27 października 2026, 14:40–15:20, Europe/Warsaw**.
Termin i wymagania techniczne pochodzą z zaproszenia przekazanego przez Igora.
Nie zapisano linków do spotkania, odwołania ani panelu kandydata.

## Uruchomienie

Z dowolnego katalogu:

```sh
/home/aridlin/mama/live-explain-recruitment/start-recruitment
```

Otwiera okno odbiorcy oraz prywatny dialog połączenia telefonu.
Gotowe środowisko `.venv` jest już zainstalowane; uruchamianie nie wymaga internetu.
Publiczne obrazy projektów i fonty są zapisane lokalnie.

Alternatywnie w katalogu projektu:

```sh
./run --presentation recruitment --canonical normal --windowed --remote
./run --presentation recruitment --canonical simple --windowed --remote
./run --presentation recruitment --canonical deep --windowed --remote
```

`./run` bez argumentów nadal uruchamia dotychczasową prezentację o Spectre/Meltdown.
Rekrutacja używa osobnego pliku odzyskiwania `recovery-recruitment.json`.
Opcjonalne `--recover` rozpoczyna od bezpiecznego punktu ostatniej zapisanej sesji.

## Telefon i prowadzenie

Telefon i komputer powinny być w tej samej sieci lokalnej.
W dotychczasowej aplikacji Live Explain na Androidzie wybierz wykrytą prezentację
albo wpisz adres z prywatnego dialogu Wi-Fi. Używany jest istniejący protokół i port 8080.
Nie trzeba instalować zmodyfikowanej aplikacji Android.

Każdy rozdział ma dwa akapity i dwa zatrzymania:

1. Przeczytaj akapit 1 z telefonu.
2. Wybierz **Dalej** i poczekaj około 1,2 sekundy na odsłonięcie drugiej części.
3. Przeczytaj akapit 2.
4. Wybierz **Dalej**, aby przejść do kolejnego rozdziału; krótka zmiana obrazu musi się zakończyć.

Tekst prywatny zawiera całą wypowiedź danego rozdziału. Wskazówki etapów mówią,
który akapit czytać. Nie trzeba zapamiętywać tekstu. Nie ma automatycznego lektora.
Na pytania można zatrzymać prezentację, otworzyć jedną z trzech dygresji projektowych
i wybrać **Powrót**. Wraca dokładna pozycja animacji, wstrzymana.

Zmiana ścieżki zachowuje temat, ale rozpoczyna jego nową wersję od początku.
Z dygresji przełączenie poziomu prowadzi do odpowiadającego jej głównego rozdziału.
**Cofnij** przywraca poprzednią nawigację. Dotychczasowe skróty nadal działają:
strzałka w prawo — Dalej, spacja — pauza/wznowienie, Backspace — Powrót,
U — Cofnij, B — zasłona, P — prywatny pulpit, F11 — pełny ekran.

## Treść i czas

| Ścieżka | Słów | Budżet | Średnie tempo |
| --- | ---: | ---: | ---: |
| Prosta (`simple`) | 284 | 3 min | 95 słów/min |
| Standardowa (`normal`) | 482 | 5 min | 96 słów/min |
| Szczegółowa (`deep`) | 771 | 8 min | 96 słów/min |

Budżety są szacunkiem, obejmującym krótki czas na przejścia. Rzeczywisty czas
trzeba zmierzyć podczas czytania na głos; dygresje i pytania go wydłużają.

Rozdziały: o mnie, FT, Kalwer, vctts/Phonomenal, sposób nauki i wybór Chmury, dalsze plany.
Skrypty są w `src/live_explain/presentations/recruitment.py`.
Prezentacja korzysta z neutralnego określenia „rozwijam projekty”. Nie zawiera
szczegółów leczenia, prywatnych relacji rodzinnych ani niepotwierdzonych osiągnięć.
Zrzuty FT przedstawiają tę samą prostą aplikację w trzech trybach; jej kod
jest w `tools/recruitment_ft_example.cpp`. Nie każda funkcja biblioteki ma identyczny
odpowiednik w każdym trybie. Phonomenal jest opisany jako eksperymentalny, z profilem angielskim.

Źródła obrazów, przypięte commity i SHA-256:
`src/live_explain/assets/recruitment/sources.json`. Oryginalne pliki są zachowane;
kadrowanie Kalwera odbywa się dopiero przy wyświetlaniu. Obok są licencje repozytoriów.

## Awaryjna wersja

W `artifacts/recruitment/` są katalogi `simple`, `normal` i `deep`.
Każdy zawiera:

- `public/` — 12 obrazów w kolejności wyświetlania, po dwa na rozdział;
- `PRIVATE-presenter-script.txt` — pełny tekst, którego nie należy udostępniać odbiorcom.

Obrazy można otworzyć w zwykłej przeglądarce zdjęć. Jest to wersja bez animacji i pilota.
Po zmianie tekstów lub obrazów eksport trzeba odświeżyć:

```sh
./run --presentation recruitment --canonical normal --export artifacts/recruitment/normal
```

## Próba przed rozmową

W Google Meet wybierz udostępnianie **okna „Live Explain — audience”**.
Przy jednym ekranie lepiej pozostawić prezentację w oknie.
Nie udostępniaj całego pulpitu, prywatnego czytnika, terminala ani dialogu Wi-Fi.
Kamera i udział rodzica są wymagane według przekazanego zaproszenia; dalsza część
dotycząca kształcenia specjalnego przebiega zgodnie z instrukcjami szkoły.

Przed spotkaniem wykonaj próbę z fizycznym telefonem: połączenie, tekst, Dalej,
dygresja, Powrót i zmiana poziomu. Sprawdź także widok udostępnionego okna z drugiego
urządzenia i zmierz czas czytania wersji standardowej. Automatyczne testy HTTP
i obrazy z renderera nie zastępują tej próby.
