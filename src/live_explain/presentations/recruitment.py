"""Igor's recruitment talk: six corresponding chapters, three authored lengths."""

from ..authoring import Beat, Event, Landing, Presentation, Script

CHAPTERS = (
    ("about", "Igor Zwierzchowski", "17 lat · trzecia klasa liceum", "Programowanie\nCyberbezpieczeństwo"),
    ("ft", "FT", "Biblioteka C++17: GUI, TUI i WWW", "Okno aplikacji\nTerminal\nPrzeglądarka"),
    (
        "kalwer",
        "Kalwer",
        "Launcher aplikacji, terminal i kalkulator",
        "Wyszukiwanie aplikacji\nPolecenia\nObliczenia",
    ),
    (
        "voice",
        "vctts / Phonomenal",
        "Synteza mowy i wyjścia audio",
        "vctts: synteza i wyjścia audio\nPhonomenal: synteza z nagrań",
    ),
    (
        "learning",
        "Jak chcę się uczyć",
        "Plan nauki, egzaminy i projekty",
        "Podstawa programowa\nCzas na własne projekty\nWsparcie, gdy jest trudniej",
    ),
    (
        "future",
        "Mój dalszy kierunek",
        "Matura i planowane studia",
        "Ukończenie klasy\nPrzygotowanie do matury\nStudia związane z cyberbezpieczeństwem",
    ),
)

# Paragraph 1 belongs to the first hold, paragraph 2 to the revealed second hold.
# Animation seconds are separate from the speaking budget; there is no autoplay.
TEXT = {
    "simple": (
        (
            "Mam na imię Igor, mam siedemnaście lat i jestem w trzeciej klasie liceum. Interesuję się "
            "programowaniem i cyberbezpieczeństwem.",
            "Rozwijam bibliotekę interfejsów FT, launcher Kalwer oraz vctts i Phonomenal, czyli "
            "projekty związane z syntezą mowy. Pokażę ich funkcje, a potem opowiem o swoim planie "
            "nauki.",
        ),
        (
            "FT to biblioteka C++ do tworzenia interfejsów graficznych, terminalowych i "
            "przeglądarkowych. Udostępnia wspólne API, czyli zestaw funkcji wywoływanych przez "
            "aplikację.",
            "Ten sam kod może wyświetlić pola tekstowe, przyciski i suwaki w trzech trybach. Na "
            "ekranie pokazuję jeden program uruchomiony w każdym z nich. Biblioteka jest dostępna w "
            "jednym pliku nagłówkowym.",
        ),
        (
            "Kalwer to launcher: wyszukuje i uruchamia aplikacje, obsługuje polecenia terminala oraz "
            "obliczenia. Wyszukiwanie aplikacji korzysta z backendu Elephant.",
            "Interfejs linuksowy wykorzystuje GTK3 i Cairo. Efekt punktowej maski jest wykonywany na "
            "GPU. Wbudowany kalkulator pokazuje wynik jako liczbę dziesiętną, ułamek i procent, co "
            "widać na drugim zrzucie.",
        ),
        (
            "vctts zamienia wpisany tekst na mowę i odtwarza ją na wybranych wyjściach audio. Może "
            "skierować dźwięk do komunikatora i równocześnie do odsłuchu.",
            "Phonomenal generuje mowę przez łączenie fragmentów nagrań. Zapisuje je w paczce głosu, "
            "którą może odczytać vctts. Obecny profil językowy jest angielski. Zrozumiałość zależy od "
            "dostępnych głosek i dokładności podziału nagrań.",
        ),
        (
            "Z nauką indywidualną mam doświadczenie od pierwszej klasy szkoły podstawowej, a od "
            "czwartej również z nauką online. Korzystam z dokumentacji technicznej i materiałów "
            "edukacyjnych.",
            "W Chmurze chcę samodzielnie planować realizację podstawy programowej, przygotowanie do "
            "egzaminów i pracę nad projektami. Potrzebuję spokojniejszych warunków nauki. Przy "
            "zaległościach zamierzam zmieniać harmonogram i korzystać ze wsparcia rodziny.",
        ),
        (
            "W najbliższym roku chcę ukończyć klasę, przygotowywać się do matury i rozwijać pokazane "
            "projekty.",
            "Planuję studia związane z cyberbezpieczeństwem na Politechnice Warszawskiej. Zależy mi na "
            "organizacji nauki, która pozwoli przygotować się do egzaminów i poświęcać więcej czasu "
            "informatyce. Dziękuję.",
        ),
    ),
    "normal": (
        (
            "Mam na imię Igor Zwierzchowski, mam siedemnaście lat i jestem uczniem trzeciej klasy "
            "liceum. Interesuję się programowaniem, informatyką i cyberbezpieczeństwem. Rozwijam "
            "projekty w C++ i Pythonie.",
            "Pokażę FT, czyli bibliotekę interfejsów, Kalwer, czyli launcher aplikacji, oraz vctts i "
            "Phonomenal, które służą do syntezy i odtwarzania mowy. Potem opowiem, jak zamierzam "
            "organizować naukę w Chmurze i jakie mam dalsze plany.",
        ),
        (
            "FT to biblioteka C++17 dostępna w jednym pliku nagłówkowym. Udostępnia wspólne API dla "
            "trzech backendów: natywnego interfejsu graficznego, terminala i strony internetowej. "
            "Programista opisuje pola, przyciski i układ widoku za pomocą tych samych funkcji.",
            "Tryb wybiera się przy uruchomieniu programu. Na ekranie pokazuję tę samą aplikację z "
            "polem tekstowym, suwakiem i przyciskiem w każdym z trzech trybów. FT działa w modelu "
            "immediate mode: aplikacja opisuje potrzebne kontrolki przy kolejnych odświeżeniach. Nie "
            "wszystkie funkcje mają odpowiednik w każdym backendzie. Dlatego poza wspólnym API "
            "dostępne są też funkcje właściwe dla konkretnego trybu.",
        ),
        (
            "Kalwer to launcher do wyszukiwania i uruchamiania aplikacji. Korzysta z backendu Elephant "
            "i dodaje własny interfejs, obsługę poleceń oraz kalkulator. Wersja linuksowa wykorzystuje "
            "GTK3 i Cairo. Program działa w tle, więc wywołanie okna nie wymaga uruchamiania nowego "
            "procesu GTK.",
            "Na pierwszym zrzucie widać wyniki wyszukiwania aplikacji, a na drugim obliczenie. "
            "Kalkulator obsługuje kolejność działań, nawiasy i kilka postaci wyniku: dziesiętną, "
            "ułamkową oraz procentową. Polecenia mogą działać w interaktywnym terminalu lub w tle. "
            "Efekt graficzny to maska GPU nakładana na wcześniej wyrenderowany interfejs, razem z "
            "tekstem i ikonami.",
        ),
        (
            "vctts jest nakładką do syntezy mowy z tekstu i odtwarzania dźwięku. Pozwala wybrać głos oraz "
            "urządzenia wyjściowe. W Linuksie obsługuje także wirtualny mikrofon, przez który dźwięk "
            "trafia do Discorda lub innego komunikatora. Odsłuch może działać równocześnie na drugim "
            "wyjściu.",
            "Phonomenal jest jednym z silników dostępnych w vctts. Generuje wypowiedzi przez wybór i "
            "łączenie fragmentów nagrań. Python przygotowuje paczkę głosu: nagrania, transkrypcje oraz "
            "granice słów i głosek. Część w C++ dobiera fragmenty i składa wynikowy dźwięk. Paczka ma "
            "format vcpack. Na ekranie widać interfejs nagrywania materiału. Obecny profil jest "
            "angielski; brakujące głoski lub niedokładne granice fragmentów mogą pogarszać "
            "zrozumiałość i brzmienie.",
        ),
        (
            "Uczę się indywidualnie od pierwszej klasy szkoły podstawowej, a od czwartej również "
            "online. W informatyce korzystam głównie z dokumentacji technicznej, internetu i "
            "materiałów edukacyjnych. Sprawdzam postępy, wykorzystując poznane zagadnienia w "
            "projektach oraz przygotowując się do egzaminów.",
            "Dotychczasowa nauka wiązała się dla mnie z dużą presją. W Chmurze chcę mieć spokojniejsze "
            "warunki i samodzielnie planować tydzień. W harmonogramie muszę uwzględnić podstawę "
            "programową, egzaminy oraz projekty informatyczne. Przy opóźnieniach lub spadku motywacji "
            "zamierzam dostosowywać plan, stopniowo nadrabiać zaległości i korzystać ze wsparcia "
            "rodziny.",
        ),
        (
            "Na najbliższy rok planuję ukończenie klasy, przygotowanie do matury i dalszą pracę nad "
            "FT, Kalwerem oraz projektami głosowymi. Chcę pogłębiać wiedzę z programowania i "
            "cyberbezpieczeństwa.",
            "Planuję studia związane z cyberbezpieczeństwem na Politechnice Warszawskiej. Żeby się do "
            "nich przygotować, potrzebuję zarówno czasu na informatykę, jak i realizacji szkolnych "
            "wymagań. W Chmurze zależy mi przede wszystkim na możliwości samodzielnego rozłożenia tej "
            "pracy. Dziękuję, chętnie odpowiem na pytania.",
        ),
    ),
    "deep": (
        (
            "Mam na imię Igor Zwierzchowski, mam siedemnaście lat i jestem w trzeciej klasie liceum. "
            "Interesuję się programowaniem, informatyką i cyberbezpieczeństwem. Rozwijam projekty w C++ "
            "i Pythonie, dotyczące interfejsów aplikacji, narzędzi systemowych i przetwarzania dźwięku.",
            "Przedstawię bibliotekę FT, launcher Kalwer oraz vctts i Phonomenal. Omówię ich funkcje i "
            "podstawy implementacji. Prezentację uruchamiam w swoim Live Explain, które oddziela widok "
            "odbiorcy od prywatnego tekstu i sterowania. Na końcu opowiem o doświadczeniu w nauce "
            "indywidualnej, powodach wyboru Chmury i planach związanych z maturą oraz studiami.",
        ),
        (
            "FT to biblioteka C++17 w jednym pliku nagłówkowym. Wspólne API w przestrzeni nazw ft "
            "obsługuje trzy backendy: FTUI dla natywnego GUI, FTTI dla terminala i FTHT dla interfejsu "
            "przeglądarkowego. Aplikacja wywołuje te same funkcje do opisu kontrolek i układu, a backend "
            "odpowiada za ich wyświetlanie. Tryb można wybrać flagą przy uruchomieniu. Tryb automatyczny "
            "uwzględnia dostępność środowiska graficznego i terminala. Przeglądarkowy backend uruchamia "
            "wbudowany serwer HTTP.",
            "Na ekranie jest ten sam program w trzech trybach: pole tekstowe, checkbox, suwak, wskaźnik "
            "postępu i przycisk. Kod aplikacji pozostaje ten sam. FT wykorzystuje model immediate mode: "
            "w pętli obsługi zdarzeń aplikacja ponownie opisuje potrzebne kontrolki. Wspólna warstwa "
            "udostępnia funkcje, które można odwzorować w różnych środowiskach, ale nie ukrywa "
            "wszystkich różnic. Natywne okna potomne, obrazy lub dialogi plikowe nie mają identycznej "
            "obsługi w terminalu i przeglądarce. Gdy aplikacja potrzebuje funkcji specyficznej dla "
            "jednego backendu, może użyć bezpośrednio jego API. Biblioteka pozwala też uruchomić "
            "interfejs WWW z działającej aplikacji okienkowej.",
        ),
        (
            "Kalwer jest rezydentnym launcherem. Wersja linuksowa korzysta z GTK3 i Cairo, a "
            "wyszukiwanie aplikacji deleguje do backendu Elephant. Okno obsługuje wyniki wyszukiwania, "
            "ulubione aplikacje, polecenia terminala i kalkulator. Można też wyszukiwać znaki Unicode "
            "oraz aliasy hostów SSH. Proces pozostaje uruchomiony w tle. Ponowne wywołanie pokazuje jego "
            "okno zamiast uruchamiać kolejną instancję interfejsu. Przy krótkim zamknięciu i ponownym "
            "otwarciu przywracane są zapytanie, zaznaczenie i pozycja listy.",
            "Pierwszy zrzut pokazuje wyszukiwanie aplikacji. Drugi przedstawia kalkulator, który "
            "uwzględnia kolejność działań i nawiasy oraz podaje wynik w postaci dziesiętnej, ułamkowej i "
            "procentowej. Polecenia mogą działać interaktywnie lub w tle. Zakończenie zadania w tle "
            "wywołuje powiadomienie z wynikiem. Od strony renderowania GTK i Cairo najpierw przygotowują "
            "pełny obraz interfejsu. Dopiero na niego nakładana jest punktowa maska przez shader GPU. "
            "Maska steruje widocznością gotowych pikseli, więc obejmuje również tekst i ikony. "
            "Klawiatura pozwala edytować zapytanie, wybierać wyniki i uruchamiać zaznaczoną pozycję bez "
            "przechodzenia do myszy.",
        ),
        (
            "vctts obsługuje syntezę mowy z tekstu i odtwarzanie dźwięku. Użytkownik wybiera głos i wyjścia audio. "
            "Dźwięk może jednocześnie trafić do odsłuchu oraz do komunikatora przez wirtualny mikrofon. "
            "Dostępne są różne źródła głosu, w tym Phonomenal. Ten projekt generuje mowę przez wybór i "
            "łączenie fragmentów wcześniejszych nagrań. Paczka vcpack zawiera dźwięk, transkrypcje, "
            "położenie słów i głosek oraz dane potrzebne do wyboru fragmentów. Granice zapisane są jako "
            "pozycje próbek, co pozwala wycinać fragmenty dokładniej niż na podstawie napisów z czasem "
            "zaokrąglonym do sekund.",
            "Python przygotowuje paczkę: odczytuje nagrania, wykonuje transkrypcję i dopasowuje słowa "
            "oraz głoski do dźwięku. Część w C++ planuje wypowiedź i składa wynik. Preferuje dłuższe, "
            "ciągłe fragmenty, a w razie potrzeby buduje słowa z krótszych odcinków. Przy wyborze "
            "połączeń uwzględnia cechy dźwięku, między innymi energię i wysokość tonu. Na ekranie widać "
            "interfejs nagrywania materiału. Obecnie używany profil językowy to angielski i ARPABET. "
            "Jeśli w nagraniach brakuje potrzebnej głoski, program musi ją przybliżyć lub zgłosić brak "
            "pokrycia. Błędna transkrypcja albo granica fragmentu może pogorszyć wynik. Dlatego kontrola "
            "jakości obejmuje odsłuch i porównanie rozpoznanego tekstu z tekstem wejściowym.",
        ),
        (
            "Mam doświadczenie nauki indywidualnej od pierwszej klasy szkoły podstawowej, a od czwartej "
            "również nauki online. W informatyce korzystam z dokumentacji technicznej, internetu i "
            "materiałów edukacyjnych. Projekty pozwalają sprawdzać wykorzystanie wiedzy w działającym "
            "programie. Egzaminy sprawdzają z kolei realizację szkolnego materiału. Chcę uwzględniać oba "
            "te wyniki przy planowaniu dalszej pracy.",
            "W dotychczasowej szkole trudne były dla mnie presja i ograniczony czas na zainteresowania. "
            "W Chmurze szukam spokojniejszych warunków oraz możliwości samodzielnego planowania "
            "tygodnia. Muszę uwzględnić wymagane przedmioty, terminy egzaminów, przygotowanie do matury "
            "i pracę nad projektami. Przy opóźnieniach zamierzam zmieniać harmonogram i nadrabiać "
            "materiał stopniowo. W razie trudności mam wsparcie rodziny. Chcę poprawić regularność "
            "planowania i wcześniej reagować na zaległości.",
        ),
        (
            "W najbliższym roku chcę ukończyć klasę, przygotowywać się do matury i rozwijać FT, Kalwer "
            "oraz vctts i Phonomenal. Chcę też pogłębiać wiedzę z cyberbezpieczeństwa. Planuję studia "
            "związane z tą dziedziną na Politechnice Warszawskiej. Ukończenie szkoły i wynik matury są "
            "istotną częścią przygotowania do tego celu.",
            "W Chmurze chcę samodzielnie rozłożyć szkolne obowiązki i pracę nad projektami. Na "
            "informatykę potrzebuję więcej czasu, niż zapewniają same lekcje tego przedmiotu. "
            "Jednocześnie chcę opanować wymagany materiał z pozostałych przedmiotów i przygotować się do "
            "egzaminów. Elastyczny harmonogram pozwoli mi planować te zadania z uwzględnieniem moich "
            "potrzeb. Dziękuję, chętnie odpowiem na pytania o projekty lub organizację nauki.",
        ),
    ),
}

SECONDS = {
    "simple": (20, 35, 30, 40, 30, 25),
    "normal": (30, 60, 45, 65, 55, 45),
    "deep": (45, 95, 75, 105, 90, 70),
}

DETOURS = {
    "ft-detail": (
        "ft",
        "FT — backendy GUI, TUI i WWW",
        "Wspólne API i funkcje specyficzne dla backendu",
        "Przestrzeń nazw ft udostępnia wspólne API do kontrolek i układu. Backend wybiera się "
        "przy uruchomieniu programu: GUI, TUI lub WWW. Tryb automatyczny uwzględnia dostępność "
        "pulpitu i interaktywnego terminala. Funkcje specyficzne dla backendu pozostają dostępne "
        "przez jego własną przestrzeń nazw. Dotyczy to na przykład natywnych okien potomnych lub "
        "funkcji serwera HTTP. Ta sama aplikacja może więc używać wspólnych kontrolek, a wybrane "
        "funkcje implementować osobno dla danego środowiska.",
    ),
    "kalwer-detail": (
        "kalwer",
        "Kalwer — renderowanie interfejsu",
        "GTK3, Cairo i shader maski GPU",
        "GTK3 i Cairo renderują interfejs do powierzchni ARGB poza ekranem. Gotowy obraz "
        "jest przesyłany do tekstury po zmianie jego zawartości. Shader GPU nakłada na "
        "teksturę animowaną maskę punktową. Maska określa widoczność pikseli, a ich kolor "
        "pochodzi z obrazu interfejsu. Wyszukiwanie aplikacji działa asynchronicznie przez "
        "Elephant. Obsługa poleceń korzysta z terminala VTE i pozwala przenieść działającą "
        "sesję do Ghostty lub pozostawić zadanie w tle.",
    ),
    "voice-detail": (
        "voice",
        "Phonomenal — segmentacja i dobór fragmentów",
        "Paczka .vcpack i silnik C++",
        "Paczka vcpack zawiera dźwięk, transkrypcje, wymowę i granice słów oraz głosek "
        "zapisane jako pozycje próbek. Silnik C++ dobiera fragmenty wypowiedzi, preferując "
        "dłuższe ciągłe nagrania. Krótsze fragmenty pozwalają składać nowe słowa. Ocena "
        "połączeń uwzględnia energię, wysokość tonu i cechy widma. Brakujące głoski oraz "
        "błędy transkrypcji lub segmentacji ograniczają jakość. vctts wczytuje paczkę, "
        "generuje wynikowy dźwięk i odtwarza go na wybranych wyjściach audio.",
    ),
}


def initial(beat):
    return {"revealed": False}


def reduce(model, event):
    if event.kind == "reveal":
        model["revealed"] = True


def build():
    beats, routes, checkpoints = {}, {}, {}
    for canonical, texts in TEXT.items():
        route = []
        for index, ((chapter, title, subtitle, highlights), paragraphs) in enumerate(zip(CHAPTERS, texts)):
            key = f"{canonical}.{chapter}"
            following = CHAPTERS[index + 1][1] if index + 1 < len(CHAPTERS) else "Pytania"
            branch = {"ft": "ft-detail", "kalwer": "kalwer-detail", "voice": "voice-detail"}.get(chapter)
            beats[key] = Beat(
                id=key,
                checkpoint=chapter,
                title=title,
                subtitle=subtitle,
                composition="recruitment:" + chapter,
                script=Script(
                    objective="Przeczytaj pierwszą część; wybierz Dalej przed drugą.",
                    cue=subtitle,
                    wording="\n\n".join(paragraphs),
                    next_sentence=f"Dalej: {following}.",
                    boundary="Nie musisz mówić z pamięci. Zatrzymaj się, jeśli pojawi się pytanie.",
                    recap=highlights.replace("\n", "; "),
                    resume_sentence=f"Wracając do tematu: {title}.",
                    entry_sentence=f"Pozostajemy przy temacie: {title}.",
                ),
                holds=(0.0, 1.2),
                events=(Event(1.2, "reveal"),),
                planned_seconds=SECONDS[canonical][index],
                stage_cues=(
                    "Przeczytaj akapit 1; następnie Dalej i poczekaj na animację.",
                    "Przeczytaj akapit 2; następnie Dalej do następnego rozdziału.",
                ),
                detours=(branch,) if branch else (),
                diagram={"chapter": chapter, "highlights": highlights, "index": index + 1},
            )
            route.append(key)
            checkpoints.setdefault(chapter, {})[canonical] = Landing(canonical, key)
        routes[canonical] = tuple(route)
    detours = {}
    for name, (chapter, title, subtitle, wording) in DETOURS.items():
        key = "detour." + name
        base = beats["deep." + chapter]
        beats[key] = Beat(
            id=key,
            checkpoint=chapter,
            title=title,
            subtitle=subtitle,
            composition=base.composition,
            script=Script(
                objective="Opcjonalna odpowiedź; po niej wybierz Powrót.",
                cue=subtitle,
                wording=wording,
                next_sentence="Wybierz Powrót do przerwanego miejsca.",
                boundary="Tylko jeśli rekruter chce więcej szczegółów.",
            ),
            holds=base.holds,
            events=base.events,
            detours=(),
            planned_seconds=40,
            diagram={**base.diagram, "detail": True},
        )
        detours[name] = key
    presentation = Presentation(
        id="igor-recruitment",
        beats=beats,
        routes=routes,
        detours=detours,
        landings=checkpoints["about"],
        checkpoint_landings=checkpoints,
        initial=initial,
        reduce=reduce,
    )
    presentation.validate()
    return presentation
