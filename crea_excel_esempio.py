from pathlib import Path

from openpyxl import Workbook

from config import INPUT_FILE, REQUIRED_COLUMNS


SAMPLE_ROWS = [
    {
        "CREAZIONE": "Ciabatta",
        "U_CREAZIONE": 1,
        "MATERIALI": "pelle:2; corda:1",
        "U_MATERIALI": 2,
        "POTENZIAMENTO_1": "Suola rinforzata con pelle grezza",
        "U_POTENZIAMENTO_1": 1,
        "POTENZIAMENTO_2": "Lacci stretti, movimento piu stabile",
        "U_POTENZIAMENTO_2": 2,
        "POTENZIAMENTO_3": "Passo rapido su terreno roccioso",
    },
    {
        "CREAZIONE": "Lastra",
        "U_CREAZIONE": 1,
        "MATERIALI": "pietra:3; legno:1",
        "U_MATERIALI": 2,
        "POTENZIAMENTO_1": "Bordo levigato",
        "U_POTENZIAMENTO_1": 1,
        "POTENZIAMENTO_2": "Superficie piu resistente",
        "U_POTENZIAMENTO_2": 2,
        "POTENZIAMENTO_3": "Base pesante per lavorazioni dure",
    },
    {
        "CREAZIONE": "Coltello",
        "U_CREAZIONE": 1,
        "MATERIALI": "pietra:2; ramo:1; corda:1",
        "U_MATERIALI": 3,
        "POTENZIAMENTO_1": "Lama scheggiata affilata",
        "U_POTENZIAMENTO_1": 1,
        "POTENZIAMENTO_2": "Manico legato con corda",
        "U_POTENZIAMENTO_2": 2,
        "POTENZIAMENTO_3": "Taglio preciso per pelle e rami",
    },
    {
        "CREAZIONE": "Bastone",
        "U_CREAZIONE": 1,
        "MATERIALI": "ramo:2",
        "U_MATERIALI": 1,
        "POTENZIAMENTO_1": "Punta indurita al fuoco",
        "U_POTENZIAMENTO_1": 1,
        "POTENZIAMENTO_2": "Impugnatura avvolta in pelle",
        "U_POTENZIAMENTO_2": 2,
        "POTENZIAMENTO_3": "Asta lunga per caccia e spinta",
    },
    {
        "CREAZIONE": "Attrezzo",
        "U_CREAZIONE": 1,
        "MATERIALI": "legno:2; pietra:2; corda:1",
        "U_MATERIALI": 3,
        "POTENZIAMENTO_1": "Testa di pietra fissata",
        "U_POTENZIAMENTO_1": 1,
        "POTENZIAMENTO_2": "Nodo doppio piu robusto",
        "U_POTENZIAMENTO_2": 2,
        "POTENZIAMENTO_3": "Uso efficace su legno e roccia",
    },
    {
        "CREAZIONE": "Torcia",
        "U_CREAZIONE": 1,
        "MATERIALI": "ramo:1; pelle:1; fuoco:1",
        "U_MATERIALI": 2,
        "POTENZIAMENTO_1": "Fascia piu stretta",
        "U_POTENZIAMENTO_1": 1,
        "POTENZIAMENTO_2": "Brucia piu a lungo",
        "U_POTENZIAMENTO_2": 2,
        "POTENZIAMENTO_3": "Fiamma stabile anche nel vento",
    },
]


def create_sample_excel(path: Path = INPUT_FILE) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Ricette"
    sheet.append(REQUIRED_COLUMNS)

    for row in SAMPLE_ROWS:
        sheet.append([row.get(column, "") for column in REQUIRED_COLUMNS])

    for column_cells in sheet.columns:
        max_length = max(len(str(cell.value or "")) for cell in column_cells)
        sheet.column_dimensions[column_cells[0].column_letter].width = min(max(max_length + 2, 12), 34)

    workbook.save(path)
    return path


if __name__ == "__main__":
    created = create_sample_excel()
    print(f"Excel di esempio creato: {created}")
