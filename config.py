from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

DEFAULT_INPUT_FILE = BASE_DIR / "ricette.xlsx"
UPLOADED_INPUT_FILE = BASE_DIR / "tabella_gioco_A3_ricostruita.xlsx"
INPUT_FILE = UPLOADED_INPUT_FILE if UPLOADED_INPUT_FILE.exists() else DEFAULT_INPUT_FILE
OUTPUT_FILE = BASE_DIR / "output" / "menu_ricette.pdf"
PREVIEW_FILE = BASE_DIR / "output" / "preview.png"
SHEET_NAME = None

ASSETS_DIR = BASE_DIR / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
ICONS_DIR = ASSETS_DIR / "icons"
TEXTURES_DIR = ASSETS_DIR / "textures"
WATERCOLOR_DIR = ASSETS_DIR / "watercolor"
PAPER_TEXTURE = TEXTURES_DIR / "paper_texture.png"
GENERATED_PAPER_TEXTURE = TEXTURES_DIR / "generated_paper_texture.png"
DOWNLOADED_PAPER_TEXTURE = TEXTURES_DIR / "old_paper_texture_cc0.jpg"
BOTANICAL_WATERCOLOR = WATERCOLOR_DIR / "barberry_watercolor.webp"

REQUIRED_COLUMNS = [
    "CREAZIONE",
    "U_CREAZIONE",
    "MATERIALI",
    "U_MATERIALI",
    "POTENZIAMENTO_1",
    "U_POTENZIAMENTO_1",
    "POTENZIAMENTO_2",
    "U_POTENZIAMENTO_2",
    "POTENZIAMENTO_3",
    "U_POTENZIAMENTO_3",
]

DISPLAY_HEADERS = [
    "CREAZIONE",
    "U",
    "MATERIALI",
    "U",
    "POTENZIAMENTO I",
    "U",
    "POTENZIAMENTO II",
    "U",
    "POTENZIAMENTO III",
    "U",
]
