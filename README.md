# HeatFlow

HeatFlow ist ein Python-Projekt zur numerischen Lösung und Visualisierung der zweidimensionalen Wärmeleitungsgleichung. Das System simuliert die zeitliche Ausbreitung von Wärme auf einem konfigurierbaren Gitter und stellt die Ergebnisse grafisch dar.

## Physikalische Grenzen & Annahmen

Um eine effiziente Berechnung zu gewährleisten, basiert die Simulation auf folgenden physikalischen Annahmen und Einschränkungen:
* **Wärmeleitmechanismus:** Der einzige Wärmeleitmechanismus, der in dieser Simulation berücksichtigt wird, ist die Temperaturleitfähigkeit (Thermal diffusivity).
* **Aggregatzustände:** Die Simulation funktioniert nur für Festkörper gut. Simulationen, die Flüssigkeiten beinhalten, stellen einen Worst Case dar, da hier der signifikante Wärmetransport durch Konvektion komplett vernachlässigt wird. Technisch lässt sich die Simulation zwar auch für Gase ausführen, sie liefert in diesem Fall jedoch physikalisch falsche Ergebnisse.
* **Abkühlverhalten:** Ein Abkühlen durch Wärmestrahlung (gemäß dem Stefan-Boltzmann-Gesetz) ist aufgrund des hohen Rechenaufwands vernachlässigt worden. Die Abkühlung an den Rändern erfolgt ausschließlich gemäß dem newtonischen Abkühlungsgesetz. 
* **Aktive Kühlung:** Obwohl die natürliche Abkühlung vereinfacht ist, ermöglicht das System den bewussten Einbau von "Kühlquellen" (als negative Wärmequellen) mit individuell einstellbarer Kühlleistung.

## Features

* **Numerische Lösung:** Verwendet `scipy.integrate.solve_ivp` für die präzise Berechnung der Differentialgleichungen.
* **Zwei Betriebsmodi:** Bequeme Steuerung über eine interaktive grafische Benutzeroberfläche (GUI) oder detaillierte Skript-Steuerung.
* **Flexible Konfiguration:** Systemparameter wie Gittergröße, Dauer der Simulation, Materialien, permanente Wärmequellen und initiale Temperaturfelder lassen sich modular anpassen.
* **Vielseitige Visualisierung:**
  * Setup-Dashboard zur Kontrolle der Ausgangsbedingungen.
  * Statische Darstellung des Anfangs- und Endzustands.
  * Interaktive Heatmap mit einem Slider zur manuellen Navigation durch die Zeitschritte.
  * Automatische Animation der gesamten thermischen Entwicklung.
* **Speicherung:** Speicherung aller Visualisierungen möglich.

## Voraussetzungen & Technologie-Stack

Das Projekt benötigt Python. Folgende Abhängigkeiten müssen installiert sein:
* `numpy`
* `scipy`
* `matplotlib`
* `PyQt6` (für die grafische Benutzeroberfläche)

## Installation

1. Klonen oder herunterladen des Repository.
2. Wechseln in das Hauptverzeichnis des Projekts.
3. Installieren der benötigten Pakete:

```bash
pip install -r requirements.txt
```

## Nutzung & Steuerung

Das Projekt bietet zwei Wege, um Simulationen aufzubauen und auszuführen:

### 1. Steuerung über die grafische Benutzeroberfläche (GUI)
Für einen visuellen Workflow können Sie die interaktive App starten:
```bash
python src/gui.py
```
**Nutzung der GUI:**
* **Simulations-Parameter (Links):** Hier legen Sie die Gittergröße (in mm), die Dauer der Simulation, die Umgebungstemperatur und das Substratmaterial fest. Sie können zudem einstellen, ob die Kühlung nur über die schmalen Ränder oder auch über die Ober- und Unterseite erfolgen soll.
* **Zeichen-Werkzeuge:** Wählen Sie Kategorie (Bauteil, Wärmequelle, Initiale Hitze), Form (Rechteck, Quadrat, Kreis) und Material aus. 
* **Interaktive Vorschau (Rechts):** Mit einem **Rechtsklick und Ziehen** können Sie direkt auf dem Gitter neue Elemente aufziehen. Mit einem **Linksklick** markieren Sie Elemente. Sie können in die Ansicht hinein- und herausscrollen.
* **Bearbeiten:** Bereits platzierte Elemente werden in der Liste unten links aufgeführt. Ein Doppelklick auf einen Listeneintrag öffnet ein Fenster, um Parameter (wie Leistung in W/m² oder Koordinaten) nachträglich exakt anzupassen.
* Nach dem Klick auf "SIMULATION STARTEN" werden die Ergebnisse in neuen Reitern (Tabs) präsentiert.

### 2. Steuerung über das Skript (`main.py`)
Für maximale Kontrolle oder wiederkehrende Setups können Sie die Parameter direkt im Code definieren und das Skript ausführen:
```bash
python src/main.py
```
**Nutzung der `main.py`:**
Öffnen Sie die Datei `src/main.py` in einem Texteditor. Im markierten Bereich `User Input` können Sie alle Variablen anpassen:
* `M` und `N`: Definieren die Gittergröße.
* `t_span`: Legt den zeitlichen Integrationsbereich in Sekunden fest.
* `substrate_material`: Bestimmt das Grundmaterial.
* **Listen für Objekte:** Es gibt drei zentrale Listen, in die Sie geometrische Formen (`Rectangle`, `Square`, `Circle`) eintragen können:
  * `components`: Passive Bauteile auf dem Substrat.
  * `heat_sources`: Permanente Wärmequellen (oder Kühlquellen bei negativen Werten). Hier muss der Parameter `power` (in W/m²) übergeben werden.
  * `initial_heat_spots`: Bereiche, die zu Beginn eine spezifische Starttemperatur (`temp`) aufweisen.
* **Hierarchie:** Die Objekte in den Listen werden nacheinander auf das Gitter gelegt. Das jeweils letzte Objekt in der Liste überschreibt die Werte von vorherigen Objekten an überlappenden Stellen.