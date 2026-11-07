# Action team is not the possession-sequence label

Data: **2019 FIFA Women's World Cup**, StatsBomb competition 72 / season 30.
Reading: [Soccermatics Lesson 3 — Normalisation, Pressure Regains](https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#normalisation). This audit is our custom extension.
Primary field definitions: [StatsBomb specification — team, possession and possession_team](https://raw.githubusercontent.com/statsbomb/open-data/master/doc/StatsBomb%20Open%20Data%20Specification%20v1.1.pdf). The specification identifies possession_team as the team that started the sequence in control; new possession sequences require established control, and consecutive sequences can belong to the same team.

## Finding

Lesson 77 kept 240 own-labelled pressure cases unclear, plus one separate period-end case. We audited all 240 own-labelled cases: **240** occur after their own labelled sequence's first event timestamp; **200** belong to sequences containing at least one opponent Pass or Carry. The latter is a sequence-level observation; the opponent action may be before or after the particular pressure and need not be adjacent. Several pressure rows can share the same sequence and opponent events, so these counts are not unique sequences or independent samples.

We found no pressure-before-sequence-start case in this selected subset. That check does not prove all match timestamps are correctly ordered or that every label has been validated. The initial idea that these cases might be clock-order anomalies was not supported by this specific comparison.

## The field distinction

- team: the side performing the recorded event.
- possession_team: the side that started the labelled sequence in control.

A Scotland pass can therefore sit inside a sequence labelled England. Do not treat the sequence label as a frame-by-frame statement of who touches the ball or proof of continuous control. Equally, an opponent touch does not alone establish that a new controlled possession should have been labelled. We have not reviewed footage or demonstrated a provider error.

## Two indexed context examples

### Lucy Bronze — match 22936, period 1

```text
 281  00:06:43.781  Pass            actor=Scotland W | possession=17 (England Women's)
 282  00:06:43.941  Ball Receipt*   actor=Scotland W | possession=17 (England Women's)
 283  00:06:43.941  Block           actor=England Women's | possession=17 (England Women's)
 284  00:06:45.362  Pressure        actor=England Women's | possession=17 (England Women's)
 285  00:06:45.418  Pass            actor=Scotland W | possession=18 (Scotland W)
 286  00:06:47.242  Ball Receipt*   actor=Scotland W | possession=18 (Scotland W)
 287  00:06:47.242  Carry           actor=Scotland W | possession=18 (Scotland W)
```

Pressure ID: `c543af09-bb3b-4cc7-a196-32cbded861b8`. Its sequence's first-index event precedes pressure start by 29.462 seconds. Opponent Pass/Carry records in that complete labelled sequence: 1.
### Amel Majri — match 22921, period 1

```text
 605  00:15:57.782  Pass            actor=France Women's | possession=39 (France Women's)
 606  00:15:59.420  Ball Receipt*   actor=France Women's | possession=39 (France Women's)
 607  00:15:59.420  Pass            actor=France Women's | possession=39 (France Women's)
 608  00:16:03.342  Pressure        actor=France Women's | possession=39 (France Women's)
 609  00:16:04.526  Ball Receipt*   actor=France Women's | possession=39 (France Women's)
 610  00:16:04.526  Pass            actor=Korea Republic Women's | possession=39 (France Women's)
 611  00:16:10.616  Ball Receipt*   actor=Korea Republic Women's | possession=39 (France Women's)
```

Pressure ID: `fb96a1cf-d47a-46cd-a0da-82ab6288aba7`. Its sequence's first-index event precedes pressure start by 8.209 seconds. Opponent Pass/Carry records in that complete labelled sequence: 4.

## All profiles (alphabetical)

- Argentina Women's — Eliana Noemí Stábile: 3 audited own-labelled pressures; 3 have an opponent Pass/Carry somewhere in their labelled sequence.
- Australia Women's — Ellie Madison Carpenter: 14 audited own-labelled pressures; 14 have an opponent Pass/Carry somewhere in their labelled sequence.
- Brazil Women's — Letícia Santos de Oliveira: 4 audited own-labelled pressures; 4 have an opponent Pass/Carry somewhere in their labelled sequence.
- Brazil Women's — Tamires Cássia Dias de Britto: 14 audited own-labelled pressures; 13 have an opponent Pass/Carry somewhere in their labelled sequence.
- Cameroon W — Yvonne Patrice Leuko: 1 audited own-labelled pressures; 0 have an opponent Pass/Carry somewhere in their labelled sequence.
- Canada Women's — Allysha Lyn Chapman: 7 audited own-labelled pressures; 5 have an opponent Pass/Carry somewhere in their labelled sequence.
- Canada Women's — Ashley Elizabeth Marie Lawrence: 11 audited own-labelled pressures; 10 have an opponent Pass/Carry somewhere in their labelled sequence.
- China PR Women's — Peng Han: 8 audited own-labelled pressures; 7 have an opponent Pass/Carry somewhere in their labelled sequence.
- China PR Women's — Shanshan Liu: 3 audited own-labelled pressures; 2 have an opponent Pass/Carry somewhere in their labelled sequence.
- England Women's — Alex Greenwood: 8 audited own-labelled pressures; 8 have an opponent Pass/Carry somewhere in their labelled sequence.
- England Women's — Demi Stokes: 4 audited own-labelled pressures; 4 have an opponent Pass/Carry somewhere in their labelled sequence.
- England Women's — Lucy Bronze: 21 audited own-labelled pressures; 16 have an opponent Pass/Carry somewhere in their labelled sequence.
- France Women's — Amel Majri: 18 audited own-labelled pressures; 13 have an opponent Pass/Carry somewhere in their labelled sequence.
- France Women's — Marion Torrent: 8 audited own-labelled pressures; 5 have an opponent Pass/Carry somewhere in their labelled sequence.
- Germany Women's — Giulia Gwinn: 8 audited own-labelled pressures; 7 have an opponent Pass/Carry somewhere in their labelled sequence.
- Germany Women's — Verena Schweers: 1 audited own-labelled pressures; 1 have an opponent Pass/Carry somewhere in their labelled sequence.
- Italy Women's — Alia Guagni: 3 audited own-labelled pressures; 3 have an opponent Pass/Carry somewhere in their labelled sequence.
- Italy Women's — Elisa Bartoli: 6 audited own-labelled pressures; 4 have an opponent Pass/Carry somewhere in their labelled sequence.
- Jamaica Women's — Deneisha Selena Blackwood: 6 audited own-labelled pressures; 5 have an opponent Pass/Carry somewhere in their labelled sequence.
- Japan Women's — Aya Sameshima: 5 audited own-labelled pressures; 4 have an opponent Pass/Carry somewhere in their labelled sequence.
- Japan Women's — Risa Shimizu: 1 audited own-labelled pressures; 0 have an opponent Pass/Carry somewhere in their labelled sequence.
- Korea Republic Women's — Sel-Gi Jang: 5 audited own-labelled pressures; 4 have an opponent Pass/Carry somewhere in their labelled sequence.
- Netherlands Women's — Desiree van Lunteren: 11 audited own-labelled pressures; 8 have an opponent Pass/Carry somewhere in their labelled sequence.
- Netherlands Women's — Merel van Dongen: 4 audited own-labelled pressures; 2 have an opponent Pass/Carry somewhere in their labelled sequence.
- Nigeria Women's — Chidinma Nkeruka Okeke: 2 audited own-labelled pressures; 2 have an opponent Pass/Carry somewhere in their labelled sequence.
- Nigeria Women's — Ngozi Ebere: 2 audited own-labelled pressures; 2 have an opponent Pass/Carry somewhere in their labelled sequence.
- Norway Women's — Ingrid Moe Wold: 5 audited own-labelled pressures; 5 have an opponent Pass/Carry somewhere in their labelled sequence.
- Norway Women's — Kristine Minde: 8 audited own-labelled pressures; 7 have an opponent Pass/Carry somewhere in their labelled sequence.
- South Africa Women's — Lebogang Ramalepe: 6 audited own-labelled pressures; 5 have an opponent Pass/Carry somewhere in their labelled sequence.
- Spain Women's — Marta Corredera Rueda: 8 audited own-labelled pressures; 8 have an opponent Pass/Carry somewhere in their labelled sequence.
- Sweden Women's — Hanna Erica Maria Glas: 9 audited own-labelled pressures; 7 have an opponent Pass/Carry somewhere in their labelled sequence.
- Sweden Women's — Magdalena Lilly Eriksson: 4 audited own-labelled pressures; 4 have an opponent Pass/Carry somewhere in their labelled sequence.
- Thailand W — Sunisa Srangthaisong: 2 audited own-labelled pressures; 0 have an opponent Pass/Carry somewhere in their labelled sequence.
- United States Women's — Crystal Alyssia Dunn Soubrier: 9 audited own-labelled pressures; 8 have an opponent Pass/Carry somewhere in their labelled sequence.
- United States Women's — Kelley Maureen O'Hara: 11 audited own-labelled pressures; 10 have an opponent Pass/Carry somewhere in their labelled sequence.

## What changes?

Nothing in lesson 77's results. Bronze's 21 and Majri's 18 own-labelled pressure cases remain unclear for that narrowly defined proxy. This audit gives a reason to inspect the label semantics rather than count all unclear rows as failures, relabel events by guesswork or claim exact official Pressure Regains. We do not infer individual ball-winning credit, actual recovery times or pressure causation from adjacent event rows.

## Reproduce

Run `python 78_pressure_possession_label_audit.py` in Spyder. [Evidence](../data/78_pressure_possession_label_audit_evidence.json) · [Lesson](../lessons/0060-pressure-possession-labels.html).
Assisted code/data audit; no independent mastery or video observation claimed.
