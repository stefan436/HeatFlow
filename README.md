# HeatFlow

HeatFlow ist ein Python-Projekt zur numerischen Lösung und Visualisierung der zweidimensionalen Wärmeleitungsgleichung. Das System simuliert die zeitliche Ausbreitung von Wärme auf einem konfigurierbaren Gitter und stellt die Ergebnisse grafisch dar.

## Features

* **Numerische Lösung:** Verwendet `scipy.integrate.solve_ivp` für die Berechnung der Differentialgleichungen.
* **Flexible Konfiguration:** Systemparameter wie Gittergröße (`N`, `M`), räumliche Auflösung (`dx`, `dy`), Temperaturleitfähigkeit (`alpha`) und Anfangsbedingungen (`u0`) lassen sich zentral steuern.
* **Vielseitige Visualisierung:**
  * Statische Darstellung des Anfangs- und Endzustands.
  * Interaktive Heatmap mit einem Slider zur manuellen Navigation durch die Zeitschritte.
  * Automatische Animation der gesamten thermischen Entwicklung.

## Voraussetzungen

Das Projekt benötigt Python. Folgende Abhängigkeiten müssen installiert sein:
* `numpy`
* `scipy`
* `matplotlib`

## Installation

1. Klonen oder laden Sie das Repository herunter.
2. Navigieren Sie in das Hauptverzeichnis des Projekts.
3. Installieren Sie die benötigten Pakete über die `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Nutzung

Starten Sie die Simulation über das Hauptskript:

```bash
python src/main.py
```

Das Skript führt Sie nacheinander durch die verschiedenen Visualisierungen. Drücken Sie bei den statischen Plots die Enter-Taste, um zur nächsten Darstellung (Slider bzw. Animation) zu gelangen.

## Konfiguration

Um die Parameter der Simulation anzupassen, öffnen Sie die Datei `src/code/config_system.py`. Dort können Sie unter anderem die Gitterdimensionen (`N`, `M`), den zeitlichen Integrationsbereich (`t_span`) sowie das Array für die anfängliche Temperaturverteilung (`u0`) modifizieren.