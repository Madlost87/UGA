# Menu Gioco

Programma Python per generare un PDF A4 orizzontale con il menu/ricettario del gioco da tavolo partendo da un file Excel.

Il file PDF finale viene generato in:

```text
output/menu_ricette.pdf
```

## Requisiti

- Python 3.11 o superiore
- `pip`
- Librerie indicate in `requirements.txt`

Il progetto e stato preparato e testato con un virtual environment locale `.venv`.

## Primo avvio su Linux

Entra nella cartella del progetto:

```bash
cd /home/denny/uga/menu_gioco
```

Crea il virtual environment:

```bash
python3 -m venv .venv
```

Attivalo:

```bash
source .venv/bin/activate
```

Installa le dipendenze:

```bash
pip install -r requirements.txt
```

Genera il PDF:

```bash
python genera_menu.py
```

## Avvii successivi su Linux

Quando il virtual environment esiste gia, basta fare:

```bash
cd /home/denny/uga/menu_gioco
source .venv/bin/activate
python genera_menu.py
```

In alternativa puoi eseguire tutto senza attivare manualmente la venv:

```bash
cd /home/denny/uga/menu_gioco
.venv/bin/python genera_menu.py
```

## Primo avvio su Windows

Da PowerShell:

```powershell
cd percorso\del\progetto\menu_gioco
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python genera_menu.py
```

## File Excel usato dal programma

Il programma cerca il file Excel configurato in `config.py`.

Attualmente la priorita e:

1. `tabella_gioco_A3_ricostruita.xlsx`, se presente
2. `ricette.xlsx`, come file standard o di esempio

Quindi, con il file caricato attuale, il programma usa:

```text
tabella_gioco_A3_ricostruita.xlsx
```

## Colonne Excel supportate

Schema standard:

```text
CREAZIONE
U_CREAZIONE
MATERIALI
U_MATERIALI
POTENZIAMENTO_1
U_POTENZIAMENTO_1
POTENZIAMENTO_2
U_POTENZIAMENTO_2
POTENZIAMENTO_3
```

Il programma supporta anche lo schema del file caricato:

```text
CREAZIONI
U
MATERIALI
POTENZIAMENTO 1
U
POTENZIAMENTO 2
U
POTENZIAMENTO 3
U
AZIONE SPECIALE / NOTE
```

Le colonne vengono trovate per nome, non solo per posizione. Le righe di legenda/note finali vengono ignorate se non sembrano ricette.

## Legenda nel file Excel

Sotto la tabella ricette deve esistere una cella speciale che inizia con:

```text
LEGENDA
```

Nel file attuale la legenda si trova nella cella unita:

```text
A10:J11
```

Il contenuto viene letto dal file Excel e riportato automaticamente sotto la tabella nel PDF. Per modificare la legenda, cambia direttamente il testo in quella cella e rigenera il PDF.

Formato consigliato:

```text
LEGENDA
@  utilizzo creazione        ATTACCO  azione attacco        MOVIMENTO  azione movimento
O  azione estrazione         ▽  difesa                     *  zona speciale
```

La riga che inizia con `LEGENDA` non viene interpretata come una ricetta.

## Creare un Excel di esempio

Se manca un file dati, puoi creare un Excel dimostrativo con:

```bash
python crea_excel_esempio.py
```

Questo genera:

```text
ricette.xlsx
```

## Output console atteso

Eseguendo:

```bash
python genera_menu.py
```

vedrai un output simile:

```text
[1/4] Lettura Excel: tabella_gioco_A3_ricostruita.xlsx...
[2/4] 6 ricette caricate + legenda
[3/4] Generazione layout A4...
[4/4] PDF creato correttamente

output/menu_ricette.pdf
Input usato: tabella_gioco_A3_ricostruita.xlsx
```

## Dove modificare cosa

- `config.py`: percorsi dei file, nome Excel, nome PDF, cartelle asset
- `style.py`: colori, font, margini, padding, bordi, larghezze colonne, sfondi e dimensioni icone
- `genera_menu.py`: logica di lettura Excel e generazione PDF
- `crea_excel_esempio.py`: dati dimostrativi per test

Lo stile della legenda si modifica nella sezione `footer` di `style.py`.

## Icone materiali

Puoi aggiungere icone PNG in:

```text
assets/icons/
```

Esempi:

```text
wood.png
stone.png
rope.png
leather.png
fire.png
action.png
```

Il programma funziona anche se le icone non esistono. Se in futuro i materiali vengono scritti in forma strutturata, per esempio:

```text
legno:2; pietra:1; corda:3
```

la funzione `render_resources()` e gia predisposta per trasformarli in una resa piu grafica.

## Icone legenda

La legenda supporta icone opzionali in:

```text
assets/icons/
```

Nomi previsti:

```text
use.png
attack.png
movement.png
draw.png
defense.png
special.png
```

Se un'icona manca, il PDF usa un fallback testuale pulito. Per `difesa` viene usato un piccolo simbolo vettoriale se `defense.png` non esiste.

## Texture carta

Per aggiungere una texture di sfondo, inserisci un PNG qui:

```text
assets/textures/paper_texture.png
```

Se la texture non esiste, il PDF viene generato comunque con uno sfondo color carta.

## Rigenerare il PDF dopo modifiche all'Excel

1. Modifica e salva il file Excel.
2. Torna nella cartella del progetto.
3. Esegui:

```bash
source .venv/bin/activate
python genera_menu.py
```

Il file `output/menu_ricette.pdf` viene sovrascritto con la nuova versione.
