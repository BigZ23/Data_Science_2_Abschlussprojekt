Geospace Machine Learning Model

Dieses Projekt beinhaltet die Entwicklung eines Machine-Learning-Modells zur automatischen Klassifikation von Landnutzungstypen anhand von Satellitenbildern und OpenStreetMap-Daten. Das Modell verwendet einen U-Net-Ansatz und wurde mit Hilfe von FastAI und PyTorch implementiert.
Schnellstart (Windows)

    Modell herunterladen

    Laden Sie die Modedatei von Google Drive herunter und platzieren Sie sie im Verzeichnis /Model/.

    Programm starten

    Führen Sie die Datei start_program.bat aus. Stellen Sie sicher, dass Python 3 installiert ist. Das Programm installiert automatisch alle erforderlichen Abhängigkeiten und startet sowohl den HTML- als auch den Backend-Server.

Manuelle Installation (Windows/Linux)

    Modell herunterladen

    Laden Sie die Modedatei von Google Drive herunter und platzieren Sie sie im Verzeichnis /Model/.

    Abhängigkeiten installieren

    Navigieren Sie in der Konsole zum Verzeichnis /Application/Backend/ und führen Sie folgenden Befehl aus:

    bash

pip install -r requirements.txt

Backend-Server starten

Navigieren Sie zum Verzeichnis /Application/Backend/app/ und führen Sie aus:

bash

uvicorn main:app

oder alternativ:

bash

python3 -m uvicorn main:app

HTML-Server starten

Navigieren Sie zum Verzeichnis /Application/ und führen Sie aus:

bash

    python3 -m http.server -b 127.0.0.1 8080

    Webseite öffnen

    Öffnen Sie Ihren bevorzugten Browser und rufen Sie die Adresse http://127.0.0.1:8080/ auf.

Projektstruktur

    Application/: Enthält Frontend und Backend der Anwendung.
        Backend/: Enthält den Backend-Server.
            app/: Enthält die Dateien zum Ausführen des Backend-Servers.
                temp/: Enthält temporäre Dateien wie OSM-Daten, Vorhersagen und kombinierte Bilder.
                Backend_Test.ipynb: Jupyter Notebook zum Testen des Codes.
                main.py: Hauptdatei zum Starten des Backends.
            requirements.txt: Liste der Python-Abhängigkeiten.
        Frontend/: Enthält die Dateien für das Frontend.
            css/: Enthält die CSS-Dateien.
            js/: Enthält die JavaScript-Dateien.
            svg/: Enthält SVG-Dateien für Grafiken.
            index.html: Startseite für die Vorhersage.
            result.html: Seite zur Anzeige der Vorhersageergebnisse.
    Model/: Enthält alles zur Modellerstellung und Datengenerierung.
        Data/: Enthält die Trainingsdaten.
            Images/: Satellitenbilder.
            Masks/: Masken für das Training.
        Data_generation.ipynb: Code zur Datengenerierung.
        Dataset_analysis.ipynb: Analyse des Datensatzes.
        Model.ipynb: Code zum Training und Exportieren des Modells.
        requirements.txt: Abhängigkeiten für das Modell.
    Capstone_Project_TOD2.ipynb: Präsentation des Projekts in einem Jupyter Notebook.
    start_program.bat: Skript zum Starten des Programms unter Windows.
    README.md: Diese Datei.
