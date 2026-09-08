"""Authored Polish speaking routes. Wording is a fallback, not an auto-running teleprompter.

The speaker chooses pacing, questions and detours. Bracketed cues are private directions.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Chapter:
    id: str
    title: str
    subtitle: str
    seconds: int
    cue: str
    simple: str
    normal: str
    deep: str
    next_sentence: str
    boundary: str
    question: str


CHAPTERS = (
    Chapter(
        id="opening",
        title="Odrzucone nie znaczy niewidoczne.",
        subtitle="Spectre i Meltdown: co może zdradzić sam sposób wykonania programu?",
        seconds=55,
        cue="Dwa pytania: jaki jest wynik i jaki zostaje ślad?",
        simple="""Chcę pokazać wam dwie rzeczy, które łatwo pomylić. Pierwsza: co program oficjalnie zrobił. Druga: co zmieniło się w komputerze podczas jego pracy. Wynik może być prawidłowy, a sposób dojścia do niego może zdradzać informację.

Na ekranie będziemy obserwować oba te poziomy. Zaczniemy od kilku pól pamięci. Potem zobaczymy pracę wykonaną na próbę, której wynik zostanie odrzucony. Pytanie brzmi: czy razem z wynikiem znika każdy ślad?

Nie trzeba znać programowania. Każdy potrzebny zapis przeczytamy. To przygotowany model, więc możemy go zatrzymać i wrócić do dowolnego ruchu. Nie próbujemy włamać się do tego laptopa.""",
        normal="""Czy program może odmówić pokazania sekretu, a mimo to coś o nim zdradzić? Nie przez komunikat na ekranie i nie przez wysłanie pliku, tylko przez to, jak długo trwa pewna operacja. To będzie punkt wyjścia do Spectre i Meltdown.

Będziemy śledzić dwie rzeczy oddzielnie: oficjalny wynik programu oraz ślad wykonania w komputerze. Przez większość czasu obie rzeczy pasują do naszej intuicji. Ciekawie robi się wtedy, kiedy procesor wykona trochę pracy na próbę, a później odrzuci jej wynik. Odrzucenie wyniku nie musi wymazać wszystkich skutków tej pracy.

Zaczniemy od bajtu, adresu i pamięci podręcznej. Potem złożymy z nich mechanizm wycieku. Kod na ekranie jest krótkim zapisem działań, które przeczytamy wspólnie; nie zakładam znajomości języka programowania. To model poglądowy z umownymi czasami. Dzięki temu każdą część można zatrzymać, a wynik nie zależy od podatności tego laptopa.""",
        deep="""Punktem wyjścia jest różnica między poprawnością funkcjonalną a poufnością informacji. Procesor może zachować wynik wymagany przez program, a jednocześnie pozostawić mierzalne różnice w swoim stanie wewnętrznym. Obserwator nie musi dostać sekretu jako oficjalnego wyniku, żeby czegoś się o nim dowiedzieć.

Rozdzielimy stan architektoniczny, czyli to, co ma być widoczne zgodnie z modelem wykonywania instrukcji, od efektów mikroarchitektonicznych, takich jak obecność danych w cache. Te nazwy będą skrótami dla rzeczy, które pokażemy na diagramie, a nie warunkiem udziału w rozmowie.

Przejdziemy przez czas odczytu, kodowanie wartości w śladzie oraz pracę przejściową. Spectre omówimy na przykładzie wariantu pierwszego, z warunkiem zakresu. Oryginalny Meltdown dostanie osobny mechanizm: dostęp naruszający uprawnienia. Nie zrobimy z obu jednej historii o źle przewidzianym ifie. Wszystkie pomiary będą symulowane; model nie opisuje dokładnego potoku konkretnego procesora.""",
        next_sentence="Najpierw ustalmy, przed czym komputer ma chronić dane.",
        boundary="Opowiadamy o Spectre v1 i oryginalnym Meltdown. Nie o każdym ataku przejściowego wykonania.",
        question="Czy odmowa pokazania danych wystarcza, jeśli można jeszcze obserwować czas? Na razie zostaw to pytanie otwarte.",
    ),
    Chapter(
        id="isolation",
        title="Program nie powinien widzieć wszystkiego.",
        subtitle="Dane programu • granica dostępu • dane chronione",
        seconds=55,
        cue="Ochrona danych to ograniczenie obserwacji, nie tylko ukrycie okna.",
        simple="""Na komputerze działa wiele programów. Nie chcemy, żeby dowolny z nich czytał wszystkie pozostałe dane. Samo schowanie tekstu z ekranu nie wystarczy: dane nadal gdzieś istnieją.

Dlatego są granice dostępu. Część pilnuje system i sprzęt. Część wynika z reguł konkretnego programu: ta funkcja może pokazać tylko osiem elementów, chociaż program przechowuje znacznie więcej.

To dwa różne rodzaje granic. Zapamiętajmy je, bo później jedna pojawi się w przykładzie Spectre, a druga w Meltdown. Zwykły odczyt chronionego miejsca ma się nie udać. Nasze pytanie będzie trudniejsze: czy dane mogą wcześniej wpłynąć na coś, co da się zaobserwować?""",
        normal="""Wyobraźmy sobie program, który przechowuje zarówno dane dostępne przez pewną funkcję, jak i dane prywatne. Użytkownik ma dostać tylko dozwolony fragment. To granica ustanowiona przez logikę programu. Funkcja może na przykład sprawdzać, czy numer wybranego elementu mieści się w zakresie.

Jest też drugi poziom: system operacyjny i procesor rozdzielają uprawnienia do pamięci. Kod zwykłej aplikacji nie powinien po prostu czytać danych jądra systemu, czyli części zarządzającej działaniem komputera. Tę granicę wspiera sprzęt.

Na diagramie granica nie oznacza fizycznej ściany w kości RAM. Oznacza regułę: ten odczyt jest dozwolony, a tamten nie. To ważne, ponieważ później zobaczymy dwa różne problemy. W przykładzie Spectre program-ofiara ma dostęp do danych, ale jego funkcja nie powinna ich ujawniać. W oryginalnym Meltdown sam odczyt narusza uprawnienia. Nie zacierajmy tej różnicy tylko dlatego, że oba ataki mogą zostawić podobny ślad w cache.""",
        deep="""Rozdzielmy granicę programową od sprzętowych uprawnień dostępu. W jednym procesie może istnieć funkcja, która ujawnia tylko ograniczoną część danych tego procesu. Sprawdzenie indeksu realizuje wtedy regułę programu; sam proces może mieć prawo odczytać również dane leżące poza ujawnianym fragmentem.

Osobną granicę tworzą uprawnienia przypisane mapowaniom pamięci. Procesor tłumaczy adresy i sprawdza, czy dany rodzaj dostępu jest dozwolony przy bieżących uprawnieniach. To, że jakiś obszar jest odwzorowany, nie znaczy, że kod użytkownika ma prawo go odczytać. Historyczne mapowanie pamięci jądra w przestrzeni adresowej procesów okaże się istotne dla oryginalnego Meltdown.

Dla Spectre v1 będziemy obserwować ofiarę posiadającą dostęp do sekretu, lecz wykonującą niewłaściwą sekwencję przejściowo. Dla Meltdown zobaczymy niedozwolony odczyt i zależną pracę na podatnym sprzęcie. To jeszcze nie są kompletne modele zagrożeń wszystkich wariantów. Na razie ustalamy, którą granicę rysujemy, żeby później nie przypisać jej niewłaściwego mechanizmu.""",
        next_sentence="Żeby śledzić odczyt, potrzebujemy dwóch pojęć: adresu i wartości.",
        boundary="Granica funkcji i uprawnienia strony pamięci nie są zamienne. Diagram nie jest fizycznym planem RAM.",
        question="Czy program może mieć dostęp do danych, których nie wolno mu oddać przez konkretną funkcję?",
    ),
    Chapter(
        id="bytes",
        title="Adres wskazuje. Wartość jest w środku.",
        subtitle="Jedno pole = jeden bajt. Numer pola nie jest jego zawartością.",
        seconds=60,
        cue="Wskaż najpierw adres 4, potem zawartość pola. Nie zlewaj tych liczb.",
        simple="""Każde pole reprezentuje mały fragment pamięci: jeden bajt. Bajt może przyjąć jedną z 256 wartości. Nie musimy zapamiętywać tej liczby, żeby śledzić ruch na ekranie.

Adres wskazuje miejsce, a wartość jest zawartością tego miejsca. To dwie różne role liczby. Jeśli wybieramy pole numer cztery, nie wynika z tego, że w środku jest cztery. W naszym przykładzie pod tym adresem będzie siedem.

Zapis memory[index] przeczytajmy tak: wybierz z pamięci miejsce wskazane przez index. Ruch zaczyna się od wybrania miejsca. Dopiero odczyt daje jego zawartość. Przy kolejnym diagramie będziemy zmieniać sposób dostępu, ale te dwie role pozostaną takie same.

[Pauza: pozwól komuś wskazać miejsce, zanim odsłonisz wartość.]""",
        normal="""Na ekranie jest mały wycinek pamięci. Jedno pole przedstawia jeden bajt, czyli osiem bitów. Bajt ma 256 możliwych wartości. Litery A, B i dalsze w niektórych polach nie są tu słowami: to cyfry zapisu szesnastkowego, którego używa się do zwartego pokazywania bajtów.

Nie trzeba teraz przeliczać całej tabeli. Najważniejsze jest rozróżnienie adresu i wartości. Adres wybiera miejsce. Wartość jest tym, co w tym miejscu zapisano. Numer cztery może wskazywać pole zawierające siedem. Ten sam numer nie oznacza jednocześnie obu rzeczy.

Przeczytajmy krótki kod: index określa wybór, a memory[index] oznacza odczyt pod wybranym adresem. Rejestr na diagramie to małe miejsce przechowujące informację używaną przez procesor. Nasza poruszająca się liczba pokazuje zależność między wyrażeniem a odczytem; jej podróż przez ekran nie odpowiada długości przewodów ani rzeczywistemu czasowi procesora.

Za chwilę zawartość jednego miejsca sama posłuży do wybrania innego miejsca. Warto wtedy pamiętać, w którym kroku liczba jest adresem, a w którym wartością.""",
        deep="""Ten panel jest widokiem bajtów, a etykiety w lewym marginesie oznaczają przesunięcia w pokazanym wycinku. To adresy symulowane, niezwiązane z pamięcią procesu uruchamiającego prezentację. Bajt ma osiem bitów i 256 możliwych wartości; zapis szesnastkowy reprezentuje go dwoma cyframi.

Rozdzielmy indeks, wyliczony adres i odczytaną wartość. W krótkim przykładzie traktujemy wybór elementu bajtowej tablicy jako wybór pokazanego pola. W rzeczywistym kodzie adres zależy również od początku tablicy i rozmiaru elementu. Tego rachunku nie ukrywamy jako ogólnej prawdy; po prostu ustalamy go w modelu.

Wartość siedem pod przesunięciem cztery jest innym obiektem semantycznym niż samo przesunięcie. Później zobaczymy osobny przykład, w którym odczytana wartość wybiera adres w obszarze probe. Tutaj uczymy się odróżniać zawartość od miejsca.

Endianness ma znaczenie przy składaniu wielu bajtów w większą liczbę. Dzisiaj sekret jest jednym bajtem, więc kolejność bajtów nie rozstrzyga tego przykładu. To dobry moment, żeby usunąć niepotrzebną komplikację, zanim przejdziemy do cache.""",
        next_sentence="Ten sam odczyt nie zawsze musi sięgać do tego samego poziomu pamięci.",
        boundary="Pola to wycinek modelu. Rejestr, kolejność przesyłania i animacja są schematem zależności.",
        question="Jeżeli adres to 4, a w polu jest 7, którą liczbę dostajemy po odczycie?",
    ),
    Chapter(
        id="cache",
        title="Cache przechowuje użyteczne kopie.",
        subtitle="Procesor może korzystać z bliższego poziomu pamięci.",
        seconds=50,
        cue="Cache nie zgaduje sekretu. Przechowuje kopie danych.",
        simple="""Procesor potrzebuje danych, ale czekanie na pamięć zajmuje czas. Dlatego korzysta z pamięci podręcznej, czyli cache. Mogą w niej znaleźć się kopie danych używanych podczas pracy.

Jeśli potrzebna kopia już jest w cache, odczyt często kończy się szybciej. Jeśli jej nie ma, trzeba sprowadzić dane z dalszego poziomu. To sposób na przyspieszenie zwykłej pracy.

Na ekranie cache należy do układu procesora, a RAM pokazujemy osobno. Nie jest to dokładna fotografia wnętrza laptopa. Ważna jest relacja: dane mogą być dostępne bliżej albo trzeba na nie poczekać.

Odczyt nie tylko zwraca wartość. Może też zmienić stan cache. Ten drugi skutek za chwilę wykorzystamy jako ślad.""",
        normal="""Procesor potrafi wykonywać obliczenia szybciej, niż zawsze udaje się dostarczyć dane z pamięci głównej. Cache, czyli pamięć podręczna, ogranicza część tego czekania. Przechowuje kopie danych w strukturach pozwalających na szybszy dostęp.

Na schemacie mamy rdzeń, bliskie poziomy cache i dalszy poziom, który może być współdzielony. RAM jest osobnym poziomem. Dokładna organizacja zależy od układu; nie każdy procesor wygląda tak samo i nie każdy dostęp przechodzi przez wszystkie narysowane elementy.

Dla naszej historii wystarczy jeden skutek: jeśli odpowiednia kopia już jest dostępna w cache, czas odczytu może być krótszy. Gdy odczyt sprowadzi dane do cache, zmienia warunki późniejszego odczytu. Program może dostać identyczną wartość, ale operacja potrwa inaczej.

Nie twierdzimy, że cache pamięta wszystko na zawsze. Dane mogą zostać usunięte lub zastąpione. W ataku trzeba wykorzystać ślad, dopóki jest obserwowalny. Najpierw zobaczmy ten efekt bez sekretu i bez żadnego oszustwa.""",
        deep="""Cache przechowuje linie obejmujące grupy kolejnych bajtów, nie niezależną miniaturową kopię każdego pojedynczego odczytu. Wybranie jednego bajtu może więc sprowadzić również sąsiednie bajty. Nasze krótkie grupy na ekranie są skrótem graficznym, nie deklaracją rzeczywistej długości linii.

Trafienie oznacza, że potrzebne dane można znaleźć na rozpatrywanym poziomie cache. Chybienie wymaga sięgnięcia dalej. Istnieje kilka poziomów, a szczegóły obejmują między innymi współdzielenie, zastępowanie linii i koherencję. Nie potrzebujemy teraz modelować wszystkich tych mechanizmów, ale pamiętajmy, że dwa stany nie wyczerpują rzeczywistej hierarchii.

W naszej ilustracji odczyt pozostawia kopię użytecznych danych. Kolejny odczyt może wykorzystać ją szybciej. Z punktu widzenia poufności interesuje nas zależność między wcześniejszą aktywnością a późniejszym czasem dostępu.

Dlatego obszary probe będą w przykładzie rozdzielone. Nie chcemy, żeby kilka różnych wartości sprowadzało tę samą linię i dawało nierozróżnialny ślad. Rozstaw obszarów jest parametrem demonstracji, a nie synonimem długości linii cache.""",
        next_sentence="Zróbmy dwa odczyty tego samego miejsca i porównajmy ich czas.",
        boundary="Organizacja, rozmiar linii, poziomy i opóźnienia zależą od sprzętu. Kopie nie pozostają bezterminowo.",
        question="Co może zmienić pierwszy odczyt, nawet jeśli nie zmieni samej wartości w pamięci?",
    ),
    Chapter(
        id="timing",
        title="Ten sam adres. Inny czas.",
        subtitle="Wynik odczytu jest taki sam; stan cache może być inny.",
        seconds=70,
        cue="Najpierw ruch i 9 jednostek. Potem ten sam odczyt i 2. Zapytaj o przyczynę.",
        simple="""Wybieramy to samo miejsce dwa razy. Za pierwszym razem w modelu nie ma potrzebnej kopii w cache. Czekamy dłużej. Po odczycie kopia już tam jest.

Teraz powtarzamy dokładnie ten wybór. Zwrócona wartość się nie zmieniła, ale czas jest krótszy. Dziewięć i dwa na ekranie to umowne jednostki, wybrane po to, żeby różnicę było dobrze widać. Nie są wynikiem pomiaru laptopa.

Gdybym nie widział pierwszego odczytu, ale mógł wykonać drugi i zmierzyć jego czas, dostałbym wskazówkę o tym, co działo się wcześniej. Nie byłby to jeszcze dowód z jednego pomiaru. Byłaby to obserwacja, z której można próbować wnioskować.

[Pauza po drugim odczycie. Nie przechodź dalej tylko dlatego, że skończyła się animacja.]""",
        normal="""Zatrzymajmy się na pierwszym odczycie. Wybieramy adres cztery. W naszym stanie początkowym odpowiedniej kopii nie ma w cache, więc odczyt trwa dłużej. Po zakończeniu mamy zarówno wartość, jak i zmianę stanu pamięci podręcznej.

Teraz wybieramy ten sam adres jeszcze raz. Nie podmieniamy danych i nie przełączamy programu. W przykładzie zmienił się stan cache. Dlatego drugie wykonanie może zakończyć się szybciej.

Liczby dziewięć i dwa są symulowane. Rzeczywiste czasy zależą od wielu rzeczy, a wyniki trafień i chybień nie muszą układać się w dwie idealnie rozłączne grupy. Na razie celowo usuwamy szum, żeby zobaczyć samą zależność.

Istotny jest odwrócony kierunek rozumowania. Wiedząc, że był dostęp, spodziewamy się możliwej zmiany czasu. Ale mierząc czas, możemy też próbować wnioskować o wcześniejszym dostępie, którego nie widzieliśmy. W ten sposób pozornie techniczny szczegół wydajności staje się obserwacją.

Taki pomiar nie czyta jeszcze dowolnego sekretu. Musimy dopiero sprawić, żeby to sekret decydował, który ślad zostanie pozostawiony.""",
        deep="""Porównujemy dwa odczyty tego samego adresu przy różnych stanach początkowych cache. Pierwszy sprowadza dane, drugi może trafić w pozostawioną kopię. Oficjalnie oba zwracają tę samą wartość, lecz ich opóźnienie może się różnić.

Dziewięć i dwa to jawnie umowne wyniki modelu. W realnym eksperymencie trzeba ustalić metodę pomiaru, uporządkować operacje względem licznika i uwzględnić zakłócenia. Wpływ mają między innymi inne poziomy pamięci, prefetching, współbieżna praca i zmiany częstotliwości. Nie będziemy odgrywać takiego eksperymentu przez powolną animację.

Dla kanału interesuje nas rozróżnialność rozkładów obserwacji, nie magiczna stała mówiąca, że każdy szybki dostęp ma zawsze dokładnie ten sam czas. W praktyce potrzebne bywają powtórzenia oraz ostrożna klasyfikacja.

Odwracamy teraz zależność: obserwacja czasu może ujawnić coś o wcześniejszym dostępie. Sama obecność różnicy nie oznacza jeszcze wycieku sekretu. Potrzebujemy zależności sekretu od wybranego adresu oraz możliwości obserwowania tego wyboru. Te dwa warunki złożymy w następnej części.""",
        next_sentence="Jak sprawić, żeby taki ślad niósł informację o konkretnej wartości?",
        boundary="9 i 2 to jednostki umowne. Pojedynczy szybki odczyt nie jest automatycznie wiarygodnym dowodem.",
        question="Jeśli oba odczyty dają tę samą wartość, czego dowiadujemy się z różnicy czasu?",
    ),
    Chapter(
        id="channel",
        title="Wartość może wybrać miejsce.",
        subtitle="Wartość → wybrany obszar probe → obserwowalny ślad",
        seconds=65,
        cue="Kodowanie: wartość 1 wybiera probe[1]. Nie odczytuj jeszcze sekretu z podpisu.",
        simple="""Wyobraźmy sobie cztery rozdzielone miejsca w probe; pokażemy je przy pomiarze. Przyjmijmy, że wartość wybiera jedno z nich: zero pierwsze, jeden drugie, dwa trzecie. To zwykła reguła wyboru.

Jeśli dotkniemy tylko miejsca numer jeden, jego dane mogą trafić do cache. Teraz osoba, która nie widziała wartości, sprawdza czasy odczytu tych miejsc. Jeśli jedno jest wyraźnie szybsze, może próbować odgadnąć, które wcześniej wybrano.

Wartość nie została wypisana jako odpowiedź. Wpłynęła jednak na wybór miejsca, a ten wybór wpłynął na czas. To połączenie zależności tworzy kanał boczny.

Cztery pola pomagają nam śledzić przykład. Dla całego bajtu możliwości byłoby 256. Nie trzeba rysować wszystkich, żeby zrozumieć zasadę.""",
        normal="""Zbudujmy najpierw kanał bez ataku. Przyjmujemy prostą regułę: dana wartość wybiera jeden z rozdzielonych obszarów pamięci. Ten pomocniczy obszar nazwiemy probe. Wartość jeden wybiera miejsce oznaczone jedynką.

Dotknięcie tego miejsca może sprowadzić jego dane do cache. Następnie ktoś sprawdza czas dostępu do kolejnych kandydatów. Nie obserwuje bezpośrednio wartości użytej wcześniej. Obserwuje ślad zależny od tej wartości.

To są trzy połączone kroki: wartość wybiera adres, dostęp pod tym adresem wpływa na cache, a czas kolejnego dostępu pozwala próbować rozpoznać zmianę. Jeśli zerwiemy jedną z tych zależności, ten konkretny kanał przestanie działać.

Przy pomiarze pokażemy czterech kandydatów, żeby wybór był czytelny. Bajt może mieć 256 wartości; pełny przykład potrzebowałby odpowiednio większego zbioru możliwości. Obszary są rozdzielone, żeby różne wybory miały szansę zostawić różne ślady.

Jeszcze nie wyjaśniliśmy, dlaczego sekret miałby w ogóle trafić do takiego wyboru. Teraz potrzebujemy mechanizmu wykonującego pracę, która nie powinna zostać oficjalnie zatwierdzona.""",
        deep="""Rozdzielmy nadajnik śladu od jego późniejszego odczytu. W fazie kodowania wartość v wpływa na adres probe[v × stride]. Odczyt pod tym adresem może zmienić stan konkretnej linii. W fazie obserwacji mierzymy dostęp do kandydatów i próbujemy ustalić, który z nich został wcześniej dotknięty.

Stride zapewnia rozdzielenie kandydatów w konstrukcji przykładu; nie jest nazwą rozmiaru linii cache. Dobór adresów i sposób przygotowania ich stanu wpływają na wiarygodność kanału. Znane techniki wykorzystują różne możliwości obserwatora, więc nie zakładamy, że dowolny proces zawsze może dowolnie zobaczyć cały cache.

Przy pomiarze pokażemy cztery kandydatury z większej przestrzeni możliwych wartości bajtu. Reguła wyboru jest jawna: znając wybrany obszar, obserwator może próbować odtworzyć wartość. Do tego musi jednak rozróżnić skutki wcześniejszych dostępów.

Istotny jest przepływ informacji: sekret nie musi być oficjalnie zwrócony, jeżeli zależne od niego operacje wytworzą rozróżnialny efekt. To jeszcze ogólny mechanizm kodowania. Spectre i Meltdown dadzą nam różne sposoby dopuszczenia danych do przejściowej sekwencji, która taki efekt pozostawia.""",
        next_sentence="Skąd bierze się praca, której program później nie zatwierdza?",
        boundary="Cztery widoczne kandydatury to wycinek 256 możliwości bajtu. Kanał wymaga odpowiednich możliwości obserwacji.",
        question="Co by się stało, gdyby każda wartość wybierała dokładnie to samo miejsce?",
    ),
    Chapter(
        id="speculation",
        title="Procesor może zacząć przed rozstrzygnięciem.",
        subtitle="Przewiduje kierunek wykonania — nie treść sekretu.",
        seconds=55,
        cue="Warunek czeka. Przewidziana ścieżka rusza. Wynik nadal jest tymczasowy.",
        simple="""Program czasem musi wybrać jedną z dwóch dalszych dróg. Na przykład: jeśli numer mieści się w zakresie, odczytaj element. Sprawdzenie warunku może wymagać danych, na które trzeba poczekać.

Procesor nie zawsze czeka bezczynnie. Może przewidzieć, którą drogą prawdopodobnie pójdzie program, i zacząć ją wykonywać. Taki wynik pozostaje tymczasowy.

Jeśli przewidywanie było dobre, wcześniejsza praca się przyda. Jeśli było błędne, jej wynik trzeba odrzucić i wrócić na właściwą drogę. To technika przyspieszania zwykłych programów.

Procesor nie zgaduje tutaj wartości sekretu. Zgadł tylko kierunek. Dane użyte po tej decyzji mogą być rzeczywiście odczytanymi danymi. To rozróżnienie będzie kluczowe.""",
        normal="""W kodzie jest warunek. Zanim wiadomo, czy jest prawdziwy, procesor może potrzebować wyniku wcześniejszego odczytu lub obliczenia. Sam fakt, że my patrząc na zapis widzimy odpowiedź, nie znaczy, że wszystkie potrzebne informacje są już dostępne w procesorze.

Żeby nie tracić czasu, procesor może przewidzieć kierunek wykonania i zacząć pracę po przewidzianej ścieżce. Na diagramie zaznaczamy ją osobno, bo to jeszcze nie jest zatwierdzona historia programu. Przewidywanie może opierać się na wcześniejszym zachowaniu, ale nie jest nieomylne.

Gdy warunek zostanie rozstrzygnięty, są dwie możliwości. Dobre przewidywanie pozwala wykorzystać wcześniejszą pracę. Złe wymaga odrzucenia jej oficjalnych wyników i kontynuowania poprawną drogą.

Nie mówimy, że procesor przepowiada sekret. Przewidywany jest kierunek pracy. Instrukcje uruchomione na tej drodze mogą używać prawdziwych danych. Ten szczegół często ginie w zbyt krótkim opisie Spectre: błędnie wybrana droga nie oznacza, że wszystkie wartości na niej są zmyślone.""",
        deep="""Warunek sterujący przepływem może czekać na operand. Predykcja kierunku gałęzi pozwala wcześniej pobierać i wykonywać instrukcje z wybranej ścieżki. Praca jest spekulatywna, dopóki nie wiadomo, że należy do prawidłowego wykonania.

Wykonanie instrukcji i zatwierdzenie jej skutków nie muszą być tą samą chwilą. Nowoczesne procesory mogą także wykonywać gotowe instrukcje poza kolejnością programu, zachowując wymagany porządek widocznych skutków. Te pojęcia są powiązane, ale nie są synonimami: wykonywanie poza kolejnością nie musi wynikać z błędnego przewidzenia gałęzi.

Na naszym diagramie rozdzielamy moment rozpoczęcia pracy, rozstrzygnięcie warunku i to, co ostatecznie pozostaje zatwierdzone. Nie modelujemy rozmiaru bufora zmian kolejności, szerokości wydawania instrukcji ani czasów konkretnego rdzenia.

Ważne, że przewidywany kierunek może doprowadzić do rzeczywistego odczytu danych. Predyktor nie odgaduje bajtu sekretu. Jeśli taka zależna sekwencja zostanie później odrzucona, nazwiemy ją pracą przejściową. To określenie obejmie później także przypadek związany z błędem dostępu, bez potrzeby złego ifa.""",
        next_sentence="Co dokładnie znika po odrzuceniu niewłaściwej pracy?",
        boundary="Spekulacja, wykonanie poza kolejnością i zatwierdzanie instrukcji są odrębnymi pojęciami. Nie pokazujemy potoku konkretnego CPU.",
        question="Czy procesor przewidział wartość danych, czy drogę, na której wykona odczyt?",
    ),
    Chapter(
        id="rollback",
        title="Wynik znika. Ślad może zostać.",
        subtitle="Dwie warstwy stanu: zatwierdzony wynik i stan cache.",
        seconds=50,
        cue="Odrzuć wynik u góry. Zachowaj ślad na dole. Daj chwilę na tę różnicę.",
        simple="""Przewidywanie okazało się błędne. Program nie powinien dostać wyniku z tej drogi, więc wynik zostaje odrzucony. Z punktu widzenia zwykłej odpowiedzi wszystko może wyglądać poprawnie.

Ale podczas pracy zdążył wydarzyć się odczyt. Mógł on sprowadzić dane do cache. Odrzucenie wyniku nie oznacza automatycznie przywrócenia każdego szczegółu pamięci podręcznej.

Dlatego pokazujemy dwie osobne warstwy. W górnej znika tymczasowy wynik. W dolnej pozostaje możliwy do zbadania ślad. Nie twierdzimy, że każdy taki ślad jest wieczny lub zawsze łatwy do odczytania.

Teraz możemy połączyć poprzednie części: jeżeli tę pozostającą zmianę wybierał sekret, obserwacja czasu może zdradzać coś o sekrecie.""",
        normal="""Spójrzmy najpierw tylko na oficjalny wynik. Procesor rozstrzygnął warunek i ustalił, że przewidziana droga była niewłaściwa. Wyniki tej pracy nie zostają zatwierdzone. Program kontynuuje właściwą ścieżką.

Teraz spójrzmy na drugą warstwę. Podczas niewłaściwej pracy mogły wydarzyć się odczyty, które wpłynęły na cache. Mechanizm odrzucania oficjalnych wyników nie musi usuwać wszystkich tych zmian. To właśnie różnica między poprawnym wynikiem a całkowitym brakiem obserwowalnego śladu.

Nie oznacza to, że procesor ignoruje błędny warunek i zwyczajnie oddaje zakazane dane. W naszym przykładzie oficjalna odpowiedź ich nie zawiera. Problem jest subtelniejszy: odrzucona praca zdążyła wpłynąć na coś, co można później zmierzyć.

Gdy połączymy to z poprzednim diagramem, otrzymamy trzy etapy: dane wpływają na wybór adresu, dostęp zmienia cache, a potem mierzymy pozostały ślad. Samo cofnięcie wyniku programu nie zrywa automatycznie tego łańcucha. To najważniejszy moment całego wyjaśnienia — warto go zatrzymać, zamiast szybko przejść do nazw ataków.""",
        deep="""Odrzucenie pracy przejściowej chroni architektoniczny przebieg programu: niewłaściwe instrukcje nie mają zostać zatwierdzone jako jego poprawna historia. Nie jest to jednak transakcja przywracająca każdy element mikroarchitektury do identycznego stanu.

Odczyty wykonane przejściowo mogą pozostawić zmiany w cache. Późniejszy czas dostępu może zależeć od tych zmian. Rozbieżność między warstwami tworzy możliwość przepływu informacji mimo braku zatwierdzonego wyniku zawierającego sekret.

Nie potrzebujemy do tego twierdzenia, że każdy rodzaj stanu zawsze przetrwa cofnięcie. Wystarczy konkretny rozróżnialny efekt w danej konstrukcji i warunkach. Rzeczywista dostępność okna czasowego, danych i kanału ma znaczenie dla powodzenia ataku.

Na diagramie kasujemy wynik u góry, ale nie udajemy, że strzałka odwrócona w czasie oznacza fizyczne cofnięcie wszystkich operacji. Dolny ślad pozostaje do późniejszego testu. Ostateczna poprawność programu i brak ujawnienia informacji są więc osobnymi wymaganiami. Teraz sprawdzimy, jak atakujący może doprowadzić ofiarę do odpowiedniej przejściowej pracy.""",
        next_sentence="W przykładzie Spectre punktem wejścia będzie zwykłe sprawdzenie zakresu.",
        boundary="Może pozostać określony efekt mikroarchitektoniczny. Nie każdy skutek jest trwały ani automatycznie dostępny atakującemu.",
        question="Co zostało odrzucone, a co obserwator może jeszcze próbować zmierzyć?",
    ),
    Chapter(
        id="bounds",
        title="Warunek ma ograniczać dostęp.",
        subtitle="Dozwolone indeksy: 0–7. Żądanie: 12. Poprawna odpowiedź: odmowa.",
        seconds=60,
        cue="Najpierw poprawne zachowanie. Dopiero potem pytaj o spekulację.",
        simple="""Ta funkcja pozwala wybrać jeden z ośmiu elementów. Numerujemy je od zera do siedmiu. Zanim odczyta element, sprawdza, czy podany numer jest mniejszy od ośmiu.

Podajemy dwanaście. Dwanaście nie jest mniejsze od ośmiu, więc poprawne wykonanie nie powinno wejść do środka warunku. Nie powinno odczytać wskazanego tam elementu ani wykonać zależnego wyboru probe.

W tym samym programie istnieją jednak inne dane. Funkcja nie ma ich ujawniać, choć sam program ma do nich dostęp. To granica ustalona przez kod, a nie sprzętowy zakaz odczytu dla całego programu.

Na razie niczego nie obchodzimy. Chcemy dobrze zobaczyć, jakie zachowanie jest poprawne. Dopiero wtedy będzie jasne, co niewłaściwego wydarzy się przejściowo.""",
        normal="""Przeczytajmy warunek bez pośpiechu. Funkcja przyjmuje numer x. Udostępnia osiem elementów, numerowanych od zera do siedmiu. Zapis x < length znaczy: wejdź do tego fragmentu tylko wtedy, gdy x jest mniejsze od długości.

Dla naszego żądania x wynosi dwanaście, a długość osiem. Warunek jest fałszywy. Przy poprawnym wykonaniu instrukcje w środku nie powinny się wydarzyć. Dotyczy to zarówno odczytu data[x], jak i zależnego od niego dostępu do probe.

Zakładamy w tym przykładzie nieujemny indeks; nie rozważamy osobnego błędu obsługi liczb ujemnych. Sekret znajduje się poza fragmentem, który ta funkcja ma udostępniać, lecz w pamięci dostępnej programowi-ofierze. To nie jest jeszcze przypadek łamania sprzętowych uprawnień strony.

Warto zaznaczyć tę granicę w pamięci: dozwolony zakres kończy się wcześniej niż cała pamięć programu. Poprawny warunek ma pilnować reguły ujawniania danych. Pytanie Spectre będzie brzmiało: czy przewidziana ścieżka zdąży użyć czegoś za tą granicą, zanim warunek zostanie rozstrzygnięty?""",
        deep="""To klasyczny kształt przykładu Spectre v1: warunek ogranicza indeks, a wewnętrzna sekwencja odczytuje data[x] i wykonuje dostęp do probe zależny od otrzymanej wartości. Przyjmujemy nieujemny indeks i właściwe typy; nie wykorzystujemy zwykłego błędu porównania liczb ze znakiem.

Przy x równym dwanaście i długości osiem poprawne wykonanie omija ciało warunku. Atak nie wymaga jednak, żeby samo data[x] trafiało do strony niedostępnej ofierze. W tej konstrukcji sekret jest w pamięci, do której ofiara ma dostęp, ale poza zakresem, który funkcja powinna ujawniać.

Dla nas wynik porównania jest oczywisty, ponieważ obie liczby są narysowane obok siebie. W procesorze rozstrzygnięcie może jeszcze czekać na operand, na przykład długość sprowadzaną z pamięci. To daje warunki do przejściowego rozpoczęcia niewłaściwej ścieżki.

Nie utożsamiajmy jednak każdego ifa z gotowym wyciekiem. Potrzebna jest odpowiednia zależna sekwencja, dostępne dane, możliwość wpłynięcia na przewidywanie i obserwowalny kanał. Ten przykład pokazuje ich złożenie, a nie uniwersalną podatność dowolnego warunku.""",
        next_sentence="Jak można zwiększyć szansę przewidzenia niewłaściwej drogi?",
        boundary="Przyjmujemy nieujemne indeksy. Dane poza zakresem funkcji pozostają sprzętowo dostępne ofierze.",
        question="Które linie powinny zostać pominięte dla x = 12 i długości 8?",
    ),
    Chapter(
        id="training",
        title="Historia może wpłynąć na przewidywanie.",
        subtitle="Poprawne żądania przygotowują sytuację; później przychodzi żądanie spoza zakresu.",
        seconds=50,
        cue="Kilka legalnych wejść → przewidywana odpowiedź TAK → wejście 12.",
        simple="""Najpierw wielokrotnie podajemy numery mieszczące się w zakresie. Funkcja wchodzi do warunku i wykonuje dozwoloną pracę. Zaznaczone wcześniej odpowiedzi to historia, która może wpłynąć na przewidywanie procesora.

Potem podajemy dwanaście. Tym razem prawidłowa odpowiedź brzmi nie. Procesor może jednak przewidzieć wejście tak jak wcześniej i na krótko rozpocząć tę drogę.

Nie zmieniliśmy matematyki: dwanaście nadal nie jest mniejsze od ośmiu. Nie przekonaliśmy też programu, żeby oficjalnie uznał fałszywy warunek za prawdziwy. Wpłynęliśmy na wcześniejsze, tymczasowe przewidywanie.

Rysunek pokazuje ideę przygotowania. Kilka narysowanych prób nie jest instrukcją, która zawsze zapewnia sukces na dowolnym komputerze.""",
        normal="""W przykładzie atakujący może wywoływać funkcję z wybranymi argumentami. Zaczyna od wielu poprawnych indeksów. Warunek okazuje się prawdziwy i funkcja wielokrotnie wchodzi do jego środka.

Taką historię można wykorzystać, żeby wpłynąć na późniejsze przewidywanie kierunku gałęzi. Na ekranie pokazujemy kilka wejść jako skrót przygotowania, a nie dokładny algorytm rzeczywistego predyktora.

Następnie pojawia się indeks spoza zakresu. Jeżeli rozstrzygnięcie warunku nie jest jeszcze gotowe, procesor może przewidzieć wejście do środka, mimo że prawidłowa odpowiedź okaże się przecząca. Potrzebne warunki nie muszą wystąpić przy każdej próbie; w rzeczywistym ataku przygotowanie i powtarzanie mają znaczenie.

Nie przepisaliśmy warunku i nie wyłączyliśmy jego sprawdzania. Ostatecznie nadal może zostać rozstrzygnięty poprawnie. Celem jest dopuszczenie odpowiednich instrukcji do pracy przejściowej. Jeśli podczas tego krótkiego okna dane zdążą wpłynąć na cache, samo późniejsze odrzucenie wyniku może już nie usunąć informacji.""",
        deep="""Faza przygotowania wpływa na mikroarchitektoniczny stan przewidywania. Dla pokazywanego wariantu atakujący dostarcza poprawne indeksy, tak aby gałąź wielokrotnie była wykonywana w kierunku prowadzącym do ciała warunku. Późniejsza próba używa indeksu spoza zakresu.

Nie symulujemy tu konkretnej tablicy liczników ani całego algorytmu predykcji. Historia pokazana na ekranie jest wyjaśnieniem roli przygotowania. Cztery legalne wywołania nie stanowią gwarantowanej recepty na sterowanie każdym współczesnym predyktorem.

Poza przewidywaniem potrzebne jest okno, w którym zależna sekwencja zdąży wykonać użyteczną pracę. Istotne są dostępność danych, opóźnienie rozstrzygnięcia i konstrukcja kanału. Dlatego praktyczne przykłady przygotowują więcej niż sam ciąg argumentów.

Warunek nadal ma prawidłową wartość logiczną, kiedy już zostanie rozstrzygnięty. Atakujący stara się wykorzystać różnicę między tym ostatecznym rozstrzygnięciem a wcześniejszą pracą na przewidzianej ścieżce. To przygotowuje nas do właściwego przepływu: odczyt spoza udostępnianego zakresu, kodowanie w probe i odrzucenie wyniku.""",
        next_sentence="Połączmy warunek, tymczasowy odczyt i kodowanie w jednym przebiegu.",
        boundary="Historia na ekranie nie emuluje konkretnego predyktora i nie gwarantuje sukcesu po określonej liczbie prób.",
        question="Czy zmieniła się prawda warunku, czy przewidywanie wykonywane przed jego rozstrzygnięciem?",
    ),
    Chapter(
        id="spectre",
        title="Spectre v1: ofiara zostawia ślad.",
        subtitle="Błędna ścieżka → dane ofiary → dostęp zależny od wartości → odrzucenie wyniku",
        seconds=80,
        cue="Zatrzymaj osobno: przewidywanie, odczyt, kodowanie, odrzucenie. Sekret pozostaje zasłonięty.",
        simple="""Teraz oglądamy cały mechanizm, ale zatrzymamy go w kilku miejscach. Podajemy numer dwanaście. Procesor przewiduje wejście do warunku. To przewidywanie okaże się złe.

Na tej chwilowej drodze odczytywane są dane, których funkcja nie powinna ujawniać. Nie pokażemy jeszcze ich wartości. Ważne jest to, co ta wartość robi: wybiera miejsce w probe. Odczyt tego miejsca zostawia ślad w cache.

Warunek zostaje wreszcie rozstrzygnięty. Wynik niewłaściwej pracy jest odrzucony. Program nie musi oddać sekretu jako odpowiedzi. Ale obserwator może spróbować rozpoznać wcześniejszy wybór na podstawie czasu.

To nasz przykład Spectre v1. Ofiara sama wykonuje zależną pracę na danych, do których ma dostęp. Atakujący wykorzystuje jej ślad.""",
        normal="""Pierwsze zatrzymanie: funkcja dostała indeks dwanaście, a procesor przewiduje wejście do warunku. Przypomnijmy, że poprawne wykonanie powinno tę gałąź ominąć.

Drugie zatrzymanie: przejściowa praca dochodzi do data[x]. W modelu jest to miejsce poza fragmentem udostępnianym przez funkcję, lecz dostępne programowi-ofierze. Wartość pozostaje zasłonięta na ekranie, żebyśmy później nie pomylili przeczytania podpisu z odczytaniem kanału.

Trzecie zatrzymanie: otrzymana wartość wybiera adres w probe. To zależny dostęp, który może pozostawić zmianę w cache. Nie wystarczyłoby odczytać sekret i niczego obserwowalnego z nim nie zrobić; tutaj wskazujemy konkretną drogę przepływu informacji.

Czwarte zatrzymanie: warunek okazuje się fałszywy. Oficjalny wynik niewłaściwej pracy zostaje odrzucony. Pozostały ślad nie jest jednak oficjalnym wynikiem programu, więc odrzucenie jednego nie musi usunąć drugiego.

Dopiero następny etap należy do obserwatora: sprawdza on kandydatów i próbuje rozpoznać, które miejsce wybrała ukryta wartość. Całość dotyczy naszego przykładu wariantu pierwszego, nie wszystkich mechanizmów nazywanych Spectre.""",
        deep="""Łączymy teraz składniki wariantu pierwszego. Atakujący kontroluje argument x i wpływa na przewidywanie kierunku. Ofiara posiada dostęp do interesujących danych, ale warunek powinien ograniczać zakres ujawniany przez tę funkcję.

Błędnie przewidziane wejście pozwala rozpocząć data[x] przejściowo. Odczytana wartość zasila wyliczenie adresu probe[value × stride]. Jest to zależność danych, nie osobne losowe żądanie. Dostęp do probe koduje informację w mikroarchitektonicznym śladzie.

Kiedy rozstrzyga się warunek, niewłaściwe instrukcje nie zostają zatwierdzone jako prawidłowe wykonanie. To nie musi wycofać zmiany cache potrzebnej kanałowi. Następnie atakujący obserwuje odpowiednio przygotowane miejsca i wnioskuje o wartości.

Na każdym etapie istnieją praktyczne warunki powodzenia: przewidywanie musi być odpowiednie, dane dostępne, okno wystarczające, a kanał rozróżnialny. Nie udajemy, że pojedynczy przejazd tokenu dowodzi niezawodnego ataku na dowolnym sprzęcie.

Granica naruszona w tej konstrukcji wynika z zamierzonego zachowania ofiary. Nie podstawiamy w jej miejsce sprzętowego błędu uprawnień strony, bo za chwilę potrzebujemy tego rozróżnienia do wyjaśnienia Meltdown.""",
        next_sentence="Sekret nie został oficjalnie zwrócony. Sprawdźmy, co można odczytać ze śladu.",
        boundary="Sekret pozostaje ukryty do etapu obserwacji. Przepływ jest poglądowy, nie jest działającym exploitem.",
        question="W którym kroku ukryta wartość wpływa na coś, co może później zobaczyć atakujący?",
    ),
    Chapter(
        id="decode",
        title="Obserwator porównuje czasy.",
        subtitle="Szybszy kandydat jest wskazówką o wcześniejszym wyborze.",
        seconds=75,
        cue="Najpierw porównanie. Dopiero potem odsłoń 2. Oddziel kodowanie od pomiaru.",
        simple="""Obserwator sprawdza pokazane miejsca w probe. W naszej czystej symulacji jedno z nich daje krótszy czas dostępu. To miejsce oznaczone dwójką.

Przypomnijmy regułę: wartość dwa wybierała miejsce dwa. Dlatego szybszy dostęp do tego miejsca jest wskazówką, że wcześniejsza wartość wynosiła dwa. Dopiero teraz odsłaniamy ją w modelu i sprawdzamy zgodność.

W prawdziwym komputerze pomiary bywają zakłócone. Trzeba odróżnić użyteczny sygnał od przypadku, a próby mogą się nie udać. Idealne słupki na ekranie pokazują zasadę, nie skuteczność rzeczywistego ataku.

Najważniejsze jest to, że informacja nie przyszła jako odpowiedź funkcji. Została rozpoznana dzięki skutkowi pracy, której oficjalny wynik wcześniej odrzucono.""",
        normal="""Teraz zmieniamy punkt widzenia. Ofiara skończyła swoją część, a obserwator sprawdza czasy dostępu do kandydatów w probe. W naszej symulacji miejsce oznaczone dwójką jest szybsze od pozostałych.

To jeszcze nie jest magiczne czytanie każdej komórki pamięci. Korzystamy z reguły zbudowanej wcześniej: ukryta wartość wybierała konkretny adres. Jeżeli rozpoznamy ten adres po śladzie, możemy wnioskować o wartości, która go wybrała.

Teraz odsłaniamy bajt w modelu: dwa. Ten krok jest kontrolą naszej symulacji, a nie osobnym kanałem ujawniania danych. Wcześniej nie pokazywaliśmy sekretu w innym panelu ani w etykiecie lecącego tokenu.

W rzeczywistych pomiarach proste, idealne słupki zastąpiłyby wyniki obarczone szumem. Inna praca może zmienić cache, a poszczególne czasy mogą się nakładać. Dlatego praktyczne wnioskowanie zwykle wymaga starannego przygotowania i powtórzeń.

Jeżeli ktoś pyta, gdzie dokładnie doszło do wycieku, wróćmy do łańcucha: wartość wpłynęła na adres, adres na cache, a cache na obserwowany czas. Nie wystarczy powiedzieć, że procesor źle zgadywał.""",
        deep="""Faza dekodowania następuje po przejściowym kodowaniu. Obserwator sonduje kandydatów w probe i klasyfikuje czasy dostępu. W idealizowanej demonstracji kandydat dwa ma krótki czas, a pozostałe długi. Znamy regułę kodowania, więc możemy odtworzyć odpowiadającą mu wartość.

Nie pokazujemy tu wszystkich szczegółów przygotowania kanału, sposobu usuwania linii ani procedury pomiarowej. Nie zakładamy też, że obserwator ma dowolny wgląd w cudzy cache. Te możliwości należą do konkretnego modelu zagrożenia i użytej techniki.

Cztery widoczne obszary to czytelny wycinek przestrzeni 256 kandydatur. W praktyce rozstaw, kolejność prób i prefetching wpływają na rozróżnialność. Pojedynczy niski wynik może mieć inne przyczyny; powtórzenia pozwalają ocenić, czy obserwacja jest stabilna.

Dopiero po zobaczeniu wyniku odsłaniamy znaną modelowi wartość. To sprawdzenie spójności demonstracji. Nie należy go mylić z dodatkową wiedzą dostępną atakującemu.

Przydatne jest rozdzielenie trzech momentów: dane zostały użyte przejściowo, ślad przetrwał odrzucenie, a obserwator później przeprowadził pomiar. Czas trwania animacji nie mówi, jak długie było rzeczywiste okno przejściowego wykonania.""",
        next_sentence="Meltdown może wykorzystać podobny kanał, ale dane trafiają do niego inną drogą.",
        boundary="Czasy są symulowane, bez pomiaru sprzętu. Słupki nie dowodzą niezawodnego rozpoznania z jednej próby.",
        question="Dlaczego szybkie miejsce dwa pozwala wnioskować o wartości dwa? Gdzie ustaliliśmy tę regułę?",
    ),
    Chapter(
        id="meltdown",
        title="Meltdown: granica uprawnień.",
        subtitle="Oryginalny atak: niedozwolony odczyt może zasilić pracę przejściową na podatnym układzie.",
        seconds=85,
        cue="Usuń if. Pokaż brak uprawnień i osobno przejściowy wpływ danych. Potem pozostający ślad.",
        simple="""Zostawiamy podobny sposób odczytywania śladu, ale zmieniamy przyczynę. Tym razem problemem nie jest źle przewidziana droga przez warunek zakresu.

Kod próbuje odczytać miejsce, do którego nie ma uprawnień. Zwykły, zatwierdzony odczyt powinien się nie udać. W oryginalnym Meltdown na podatnym sprzęcie chronione dane mogły jednak przejściowo wpłynąć na dalszą pracę, zanim błąd zatrzymał poprawny przebieg programu.

Ta dalsza praca mogła wybrać miejsce w probe i zmienić cache. Oficjalnie odczyt nie dawał dozwolonego wyniku, ale pozostały ślad można było próbować rozpoznać.

Nie każdy procesor zachowuje się w ten sposób. To opis konkretnej klasy podatności, a nie twierdzenie, że wystarczy wpisać zakazany adres na dowolnym komputerze.""",
        normal="""W przykładzie Spectre ofiara miała dostęp do danych, a warunek programu miał ograniczać ich ujawnianie. Teraz zmieniamy granicę: kod zwykłej aplikacji próbuje odczytać chronioną pamięć, do której nie ma odpowiednich uprawnień.

Przy prawidłowym zachowaniu nie dostaje z takiego odczytu dozwolonego, zatwierdzonego wyniku. Oryginalny Meltdown wykorzystywał jednak to, że na podatnych układach chronione dane mogły zostać wykorzystane przez zależne instrukcje przejściowo, zanim obsługa błędu dostępu stała się widoczna w architektonicznym wykonaniu.

Na diagramie nie ma już warunku zakresu, który trzeba błędnie przewidzieć. Jest niedozwolony odczyt, a obok niego zaznaczamy przejściowy wpływ danych na wybór adresu w probe. Potem wraca znany nam kanał: zmiana cache i próba rozpoznania jej przez czas.

W praktycznym ataku trzeba również poradzić sobie z błędem dostępu, żeby móc kontynuować obserwacje. Nie pokazujemy tutaj kodu obsługi ani tłumienia wyjątków. Nie uruchamiamy też żadnej takiej próby na laptopie.

Zachowajmy sedno: wspólny może być ślad, ale dostęp do danych i mechanizm pracy przejściowej nie są takie same jak w naszym przykładzie Spectre v1.""",
        deep="""Oryginalny Meltdown dotyczy przejściowego użycia danych po odczycie naruszającym uprawnienia na podatnych mikroarchitekturach. W historycznym scenariuszu interesujące strony jądra mogły być odwzorowane w przestrzeni adresowej procesu, lecz oznaczone jako niedostępne dla kodu użytkownika. Mapowanie nie było równoznaczne z prawem odczytu.

Kluczowy problem polegał na tym, że chroniona wartość mogła zasilić zależną sekwencję przed architektonicznym ujawnieniem błędu. Dostęp do probe zależny od tej wartości pozostawiał efekt mikroarchitektoniczny, mimo że nie powstawał dozwolony wynik odczytu.

Nie potrzebujemy przedstawiać tego jako źle przewidzianego warunku if. Nie musimy też twierdzić, że na każdym procesorze sprawdzanie uprawnień po prostu odbywa się na samym końcu. Diagram rozdziela brak uprawnień, niedozwolony przepływ danych na podatnym układzie i późniejsze architektoniczne skutki błędu.

Praktyczne konstrukcje obsługiwały lub tłumiły wyjątek, aby kontynuować dekodowanie. Te szczegóły pozostają poza dzisiejszym modelem. Zależy nam na poprawnym rozróżnieniu mechanizmów, nie na działającym exploicie czy twierdzeniu o podatności każdego obecnego komputera.""",
        next_sentence="Połóżmy oba mechanizmy obok siebie i nazwijmy różnicę jednym zdaniem.",
        boundary="Mówimy o oryginalnym Meltdown na podatnych układach. Brak uprawnień nie oznacza uniwersalnie dostępnego sekretu.",
        question="Czy potrzebowaliśmy tutaj błędnego przewidzenia warunku zakresu?",
    ),
    Chapter(
        id="compare",
        title="Podobny kanał. Różne wejście.",
        subtitle="Spectre v1: niewłaściwa ścieżka ofiary. Meltdown: niedozwolony odczyt.",
        seconds=55,
        cue="Najpierw różnica, potem wspólny łańcuch wartości i śladu.",
        simple="""W naszym przykładzie Spectre procesor na chwilę wykonuje niewłaściwą drogę w programie-ofierze. Program ma dostęp do danych, ale ta funkcja nie powinna ich ujawniać. Dane wybierają ślad, zanim wynik zostanie odrzucony.

W oryginalnym Meltdown kod próbuje odczytać dane bez odpowiednich uprawnień. Na podatnym układzie dane mogą przejściowo wpłynąć na ślad, mimo że zwykły odczyt nie powinien się udać.

Wspólna część znajduje się po prawej stronie obu historii: dane wpływają na cache, a czas pozwala próbować rozpoznać ten wpływ. Różni się sposób, w jaki dane znalazły się w tej pracy.

Dlatego jedna nazwa nie jest po prostu drugim imieniem tego samego błędu.""",
        normal="""Sprawdźmy, czy potrafimy opowiedzieć różnicę bez długiej listy nazw. W przykładzie Spectre v1 atakujący wpływa na przewidywanie, a ofiara przejściowo wykonuje drogę, którą poprawne rozstrzygnięcie warunku powinno pominąć. Odczytuje dane dostępne ofierze, ale nieprzeznaczone do ujawnienia przez tę funkcję.

W oryginalnym Meltdown źródłem problemu jest niedozwolony odczyt na podatnym sprzęcie. Chronione dane mogą wpłynąć na zależną pracę przed architektonicznym skutkiem błędu. Nie musimy wstawiać do tej historii źle przewidzianego warunku zakresu.

Oba przykłady mogą następnie użyć podobnego kodowania w cache i podobnej obserwacji czasu. To wspólny kanał, nie dowód identyczności całego mechanizmu.

Z tego wynika też ważna praktyczna rzecz: zabezpieczenie jednej drogi nie musi zamknąć wszystkich innych. Jeśli usuniemy określone mapowanie pamięci, pomoże to w pewnym scenariuszu, ale nie naprawi automatycznie każdego przejściowego przepływu danych w programie-ofierze. Warto więc pytać, który etap konkretna ochrona rzeczywiście przerywa.""",
        deep="""Wariant pierwszy Spectre wiąże się w naszym przykładzie z błędną predykcją kierunku gałęzi oraz sekwencją ofiary, która przejściowo koduje dostępne jej dane. Oryginalny Meltdown wiąże się z nieuprawnionym odczytem, którego dane mogą zasilić zależne instrukcje na podatnej mikroarchitekturze.

W obu przypadkach można otrzymać przepływ: dane do adresu, adres do stanu cache, stan cache do pomiaru czasu. Wspólny kanał nie oznacza identycznych założeń dotyczących adresów, uprawnień, predyktora czy dostępnej sekwencji instrukcji.

Nazwa Spectre obejmuje również inne warianty. Wariant drugi dotyczy wpływu na przewidywany cel pośredniego skoku, a nie tego samego warunku zakresu. Wymieniam go tylko po to, żeby granice dzisiejszego przykładu były uczciwe; nie otwieramy teraz drugiego pełnego wykładu.

Zamiast zapamiętywać dwie etykiety jako jeden problem procesora, zachowajmy mapę przyczyn. Co pozwala na pracę przejściową? Jak dane wpływają na obserwowalny stan? Kto może go zmierzyć? Te pytania przydadzą się także przy ocenie zabezpieczeń.""",
        next_sentence="Jakie zabezpieczenia przerywają konkretne części tego łańcucha?",
        boundary="Porównanie dotyczy jawnie wskazanych mechanizmów. Spectre ma inne warianty, których tu nie rozwijamy.",
        question="Która granica występowała w Spectre v1, a która w oryginalnym Meltdown?",
    ),
    Chapter(
        id="defenses",
        title="Ochrona musi przerwać drogę informacji.",
        subtitle="Kod i kompilator • system i mapowania • zachowanie sprzętu",
        seconds=65,
        cue="Nie ma jednego przycisku „usuń każdy ślad”. Nazwij etap chroniony przez każdą zmianę.",
        simple="""Skoro znamy drogę informacji, możemy zapytać, gdzie ją przerwać. Można zmienić kod lub sposób jego wykonywania, żeby niewłaściwa droga nie użyła sekretu. Można też ograniczyć, jakie dane są w ogóle dostępne w danej sytuacji.

W ochronie przed oryginalnym Meltdown ważną rolę odegrało oddzielenie mapowań pamięci jądra od mapowań używanych przez zwykły program. Samo podobieństwo śladu nie sprawia jednak, że ta zmiana usuwa każdy wariant Spectre.

Są też poprawki sprzętu i jego sterowania. Dlatego aktualizacje mogą obejmować programy, system, firmware i sam projekt kolejnych procesorów.

Nie wynika z tego rada, żeby wyłączyć wszystkie mechanizmy przyspieszania. Chodzi o zapewnienie ochrony także podczas pracy tymczasowej. Szczegółowe rozwiązanie zależy od konkretnego mechanizmu.""",
        normal="""Nie ma jednego miejsca, w którym można nacisnąć przycisk i usunąć wszystkie możliwe kanały. Zabezpieczenie powinno odpowiadać konkretnemu etapowi przepływu informacji.

W przypadku sekwencji podobnej do naszego Spectre v1 stosuje się między innymi odpowiednio dobrane bariery wykonania lub ograniczanie używanego indeksu. Celem jest niedopuszczenie do użytecznego przejściowego dostępu w danym miejscu. Dokładne rozwiązanie zależy od platformy i wygenerowanego kodu, więc nie przedstawiam jednej linii pseudokodu jako uniwersalnej poprawki.

Dla historycznego scenariusza Meltdown ważną ochroną była izolacja tablic stron, znana w Linuksie jako PTI: zwykły kod użytkownika nie korzysta z mapowania obejmującego prawie całą pamięć jądra. Pozostaje niewielka część potrzebna do wejścia do systemu i wyjścia z niego. To zmiana dostępności danych, a nie czyszczenie wszystkich cache po każdym odczycie.

Pozostałe zabezpieczenia mogą obejmować system, kompilator, mikrokod oraz nowe projekty sprzętu. Ich koszty i zakres są różne. Praktyczny wniosek to utrzymywanie wspieranych aktualizacji, a techniczny: zawsze pytajmy, którą zależność usuwa dana ochrona i czego jeszcze nie obejmuje.""",
        deep="""Dla Spectre v1 ochrony są dobierane do konkretnych sekwencji, na przykład przez bariery o odpowiedniej semantyce na danej platformie lub przez ograniczanie indeksów. Liczy się efekt wygenerowanego kodu i właściwości sprzętu; sam wygląd warunku w języku źródłowym nie jest wystarczającym dowodem.

PTI ogranicza mapowania jądra dostępne przy wykonywaniu kodu użytkownika, pozostawiając minimalne obszary potrzebne do przejścia między kontekstami. To ważna ochrona historycznego scenariusza Meltdown, ale nie ogólna naprawa dowolnego gadżetu Spectre w pamięci dostępnej ofierze.

Inne warianty wymagają innych mechanizmów, w tym ochron związanych z przewidywaniem skoków, mikrokodem czy izolacją kontekstów. Nie przypisujmy retpoline automatycznie roli poprawki dla pokazanego ifa tylko dlatego, że oba tematy występują pod nazwą Spectre.

Sprzęt może też zapobiegać udostępnianiu niedozwolonych danych zależnym operacjom przejściowym. Każda ochrona ma zakres i założenia, a koszt zależy od obciążenia. Nie podajemy jednej procentowej kary wydajności bez pomiaru.

Wspólny cel jest szerszy od prawidłowego końcowego wyniku: poufność ma obowiązywać również wobec obserwowalnych skutków pracy, która nie zostanie zatwierdzona.""",
        next_sentence="Zamknijmy tę historię trzema zależnościami, które można odtworzyć samodzielnie.",
        boundary="To przegląd zasad ochrony, nie instrukcja wdrożenia uniwersalnej poprawki. Nie oceniamy aktualnej podatności laptopa.",
        question="Który krok chroni usunięcie dostępu do danych, a który kontrola wykonywania niewłaściwej ścieżki?",
    ),
    Chapter(
        id="recap",
        title="Dane. Praca przejściowa. Obserwacja.",
        subtitle="Poprawny wynik nie wystarcza, jeśli sekret wpływa na mierzalny ślad.",
        seconds=45,
        cue="Poproś o odtworzenie łańcucha. Zostaw czas na pytania, nie dopowiadaj automatycznie.",
        simple="""Zaczęliśmy od prostego odczytu. Ten sam adres może dać inny czas, jeśli zmienił się stan cache. Potem zobaczyliśmy, że wartość może wybrać miejsce, a wybrane miejsce może zostawić ślad.

Do tego dołączyliśmy pracę przejściową. Jej oficjalny wynik może zniknąć, a określony skutek w cache może pozostać. Dlatego odmowa oddania sekretu nie zawsze oznacza brak wycieku informacji.

W naszym Spectre v1 prowadziła do tego niewłaściwa droga w programie-ofierze. W oryginalnym Meltdown chodziło o niedozwolony odczyt na podatnym sprzęcie.

Nie musicie pamiętać nazw wszystkich części procesora. Warto umieć wskazać te zależności i zapytać, co rzeczywiście może zobaczyć obserwator. Teraz wróćmy do fragmentu, który wymaga dopowiedzenia.""",
        normal="""Złóżmy wszystko jeszcze raz, już bez dokładania nowych pojęć. Po pierwsze: wcześniejszy dostęp może zmienić cache, a przez to czas późniejszego odczytu. Po drugie: wartość może wybrać adres, dzięki czemu ślad zaczyna nieść informację o tej wartości.

Po trzecie: praca przejściowa może użyć danych, nawet jeśli jej oficjalny wynik zostanie później odrzucony. Odrzucenie wyniku nie jest automatycznie wymazaniem każdego obserwowalnego skutku.

Spectre v1 pokazało niewłaściwą przejściową ścieżkę ofiary. Oryginalny Meltdown pokazał niedozwolony odczyt na podatnym sprzęcie. Podobny kanał nie sprawił, że mechanizmy stały się identyczne.

Jeżeli chcecie sprawdzić własne rozumienie, spróbujcie powiedzieć, gdzie w naszym przykładzie ukryta wartość wpłynęła na obserwację. Możemy zatrzymać się przy dowolnym etapie: adresie, cache, warunku, odrzuceniu albo pomiarze. Samo zobaczenie animacji nie rozstrzyga, czy wszystko już jest jasne — po to mamy możliwość powrotu.""",
        deep="""Najważniejszy wniosek dotyczy przepływu informacji między warstwami. Architektonicznie prawidłowe odrzucenie pracy nie daje automatycznie gwarancji, że mikroarchitektoniczny stan nie zależy od użytych danych. Jeżeli ta zależność jest rozróżnialna dla obserwatora, może powstać kanał wycieku.

W przedstawionej konstrukcji wartość wpływała na adres probe, dostęp na stan cache, a stan na późniejszy czas. Spectre v1 i oryginalny Meltdown dostarczały różnych sposobów dopuszczenia danych do tej przejściowej sekwencji.

Dobra analiza powinna więc oddzielnie wskazać źródło przejściowego wykonania, granicę dostępu, zależną sekwencję i możliwości obserwatora. Podobieństwo końcowych słupków czasu nie zastępuje takiej analizy.

Nie wykazaliśmy podatności tego komputera, nie zmierzyliśmy jego opóźnień i nie omówiliśmy każdego wariantu. Zbudowaliśmy natomiast model, w którym można odtworzyć przyczyny. Jeżeli któryś krok wymaga powrotu, wybierzmy właśnie ten krok. To lepsze sprawdzenie wyjaśnienia niż samo zapamiętanie dwóch nazw.""",
        next_sentence="Który fragment chcecie jeszcze raz zobaczyć albo zakwestionować?",
        boundary="To koniec autorskiej trasy, nie automatyczna ocena zrozumienia. Przeznacz pozostały czas na pytania.",
        question="Odtwórzmy razem: jak ukryta wartość znalazła drogę do obserwowanego czasu?",
    ),
)
