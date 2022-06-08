# WTUM_Halite

## Wstęp

Projekt opiera się na stworzeniu działającego i efektywnego rozwiązania do gry Halite. Poniżej znajdują się linki, do odpowiednio strony konkursu na kaggle i do strony twórców gry.

https://www.kaggle.com/c/halite/overview/getting-started

https://halite.io

## Struktura projektu

W plikach projektu istnieją dwa główne katalogi. Pierwszy - starter kit, to kompletna paczka pozwalająca na rozpoczęcie pracy z grą. Ze względu na fakt, że gra skończyła się, zanim projekt się rozpoczął, to poszczególne pliki były zbierane z różnych miejsc. Paczka pozwala na tworzenie projektów w Pythonie.

Drugi, ważniejszy folder - testing_env, to miejsce faktycznej pracy nad projektem. 

Po pierwsze znajdują się tam przygotowane rozwiązania i całość środowiska do testowania ich. foldery logs, models i training_data posiadają pliki potrzebne do wykonania części projektu związanej z machine learningiem, czyli wszelkie modele, dane treningowe i logi pozwalające weryfikować poprawność.

Folder replays zawiera nagrania rozgrywek gotowych do odtworzenia w specjalnym narzędziu na stronie twórców: https://2018.halite.io/watch-games#/replay-bot.

Pliki zaczynające się od MyBot to konkretne rozwiązania, które pozwalają na grę.

Plik run_game.bat pozwala na uruchomienie konkretnej rozgrywki.

Plik run_game.py pozwala na uruchomienie ciągu rozgrywek. Rozgrywki wykonują się do wyłączenia skryptu.

Plik training.py uruchamia skrypt tworzący nowy model na podstawie plików testowych z training_data

## Rozgrywki

Domyślnie rozgrywki są prowadzone poprzez uruchomienie pliku run_game.bat w folderze testing_env. Plik ten uruchamia pojedynczą rozgrywkę. Aby zmienić poszczególne parametry rozgrywki należy zmodyfikować wywołanie aplikacji halite.exe wewnątrz pliku run_game.bat

Niestety ze względu na problemy w zbieraniu paczki początkowej aplikacja halite.exe posiada kilka błędów, które nie pozwalają na modyfikację poszczególnych parametrów.

Parametry, które można zmodyfikować to:

-s -> zmienia seed generowanej mapy z losowego na wskazany

--no-logs -> nie zapisuje logów w trakcie i po grze (wskazane przy generowaniu wielu rozgrywek)

--no-replay -> nie zapisuje nagrań rozgrywek (wskazane przy generowaniu wielu rozgrywek)

--no-timeout -> gra nie kończy się automatycznie, jeżeli tura któregoś z graczy zajmie dłużej niż wskazany czas 200ms

Pozostałe parametry albo nie są odczytywane przy uruchomieniu, albo nie mają znaczenia przy uruchamianiu rozgrywek

W grze mogą brać udział 2 rozwiązania podawane w postaci "python MyBot....py"
