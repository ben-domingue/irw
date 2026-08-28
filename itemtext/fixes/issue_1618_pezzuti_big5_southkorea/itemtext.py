import csv

TABLE = "pezzuti_2025_coolpeople_main_big5_SouthKorea"   # matches live `table` value
INSTRUMENT = "Big Five personality trait assessments for South Korean nominees"
SECTION = "main"
NA = "NA"   # live table uses the literal string, not empty

# First nine texts are the existing curation verbatim (incl. the curly
# apostrophe in "other's"). korean_big5_art is the item recovered from the
# source .sav; it takes the text previously mis-attributed to _faults.
ITEMS = [
    ("korean_big5_conservative", "Conservative."),
    ("korean_big5_trustworthy",  "Trustworthy."),
    ("korean_big5_lazy",         "Lazy."),
    ("korean_big5_sociable",     "Likes to get along and is sociable."),
    ("korean_big5_faults",       "Good at seeing other’s faults."),
    ("korean_big5_nervous",      "Gets nervous easily."),
    ("korean_big5_imaginative",  "Imaginative."),
    ("korean_big5_thorough",     "Does job thoroughly."),
    ("korean_big5_laidback",     "Laid back and relieves stress well."),
    ("korean_big5_art",          "Has little interest in art."),
]

# 7-point scale; source value labels anchor only the extremes
# (1 = 전혀 동의 하지 않는다, 7 = 매우 동의한다)
ANCHORS = {1: "strongly disagree", 7: "strongly agree"}

COLS = ["table","section_id","item","instrument","instructions",
        "section_prompt","item_text","option_text","resp"]

out = "pezzuti_2025_coolpeople_main_big5_southkorea__items.csv"  # lowercase = Redivis table name
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(COLS)
    for item, text in ITEMS:
        for resp in range(1, 8):
            w.writerow([TABLE, SECTION, item, INSTRUMENT, NA, NA,
                        text, ANCHORS.get(resp, NA), resp])
print("wrote", len(ITEMS) * 7, "rows ->", out)
