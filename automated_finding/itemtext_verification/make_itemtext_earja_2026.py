"""Item text for the seven earja_2026_* tables.

Source: the deposit's own questionnaire PDF,
"Questionnaire_AI_Streamer_TikTokShop (1).pdf" in
https://zenodo.org/records/23763732 (CC BY 4.0). Its "Section C. Construct
items" tables give, for every item, a `Code` column and both the administered
Indonesian stem and the authors' own English translation. The codes are the
same strings as the response CSV's column headers (`AT1`, `AN3`, ...), so the
item-to-text tie is the source's own label -- nothing here is positional.

Administered in Indonesian via Google Forms, so the Indonesian wording is what
goes in the base fields and the authors' English gloss goes in the
`_translated` fields (itemtext_standard.md, "Administered language"). It is the
authors' own translation, published beside the original, not a machine one.

**The option wording is deliberately incomplete, and that is the source's
doing.** The PDF states the scale once: "Construct items use a five-point
Likert scale: 1 = strongly disagree (sangat tidak setuju), 2 = disagree,
3 = neutral, 4 = agree, 5 = strongly agree (sangat setuju)." The Indonesian is
given for the two extremes ONLY. So `option_text` carries Indonesian at resp 1
and 5 and is blank at 2, 3 and 4, while `option_text_translated` carries the
English for all five. Inventing "tidak setuju" / "netral" / "setuju" for the
middle three would be padding an unlabelled point with a guess, which the
standard forbids -- they are obvious, and they are still not published.

`instructions` is blank for the same reason: the PDF describes the stimulus
("Respondents watched a 1-2 minute video ...") in its own voice for the
codebook, but does not reproduce the instructions the respondents actually
read.

**Only the anchors respondents actually used are emitted.** The schema defines
`resp` as a value "already present in the live response-level IRW dataset", and
`validate_items.R` enforces that as a hard set match. Nobody in this sample of
123 ever answered 1 on any block, and nobody answered 1 or 2 on perceived risk,
so those option rows are dropped per table by intersecting with the staged
response CSV rather than by hand. The scale really is 1-5 -- that fact lives in
the questionnaire and in this file, not in a row the gate would reject.

Run:  python3 make_itemtext_earja_2026.py <out_dir> <staged_response_dir>
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
RESP_DIR = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("../irw_output")

LANGUAGE = "Indonesian"

# resp -> (administered Indonesian, English). The PDF publishes Indonesian for
# the anchors only; see the module docstring.
OPTIONS = [
    (1, "sangat tidak setuju", "strongly disagree"),
    (2, "", "disagree"),
    (3, "", "neutral"),
    (4, "", "agree"),
    (5, "sangat setuju", "strongly agree"),
]

# table -> (instrument name, [(item code, Indonesian stem, English gloss)])
BLOCKS = {
    "earja_2026_algorithmic_transparency": (
        "Algorithmic transparency items, Earja & Nursanti (2026) AI-streamer "
        "questionnaire, Section C",
        [
            ("AT1",
             "Saya memahami mengapa AI streamer ini menampilkan dan "
             "merekomendasikan produk tertentu kepada saya.",
             "I understand why this AI streamer displays and recommends "
             "certain products to me."),
            ("AT2",
             "Platform menjelaskan dengan jelas bahwa streamer yang saya "
             "tonton adalah AI.",
             "The platform clearly explains that the streamer I watched is "
             "an AI."),
            ("AT3",
             "Cara kerja AI streamer dalam merekomendasikan produk mudah "
             "saya pahami.",
             "How the AI streamer recommends products is easy for me to "
             "understand."),
            ("AT4",
             "Saya mengetahui jenis data yang digunakan AI untuk "
             "menyesuaikan rekomendasi produk.",
             "I know what kind of data the AI uses to personalize product "
             "recommendations."),
            ("AT5",
             "Informasi tentang cara kerja AI streamer ini disampaikan "
             "secara terbuka dan jelas.",
             "Information on how this AI streamer works is conveyed openly "
             "and clearly."),
        ]),
    "earja_2026_anthropomorphism": (
        "Anthropomorphism items, Earja & Nursanti (2026) AI-streamer "
        "questionnaire, Section C",
        [
            ("AN1", "AI streamer ini tampak seperti manusia sungguhan.",
             "This AI streamer looks like a real human."),
            ("AN2", "AI streamer ini berbicara dan berekspresi secara alami.",
             "This AI streamer speaks and expresses itself naturally."),
            ("AN3", "AI streamer ini terasa memiliki kepribadian.",
             "This AI streamer seems to have a personality."),
            ("AN4",
             "Saya merasa seolah-olah sedang berinteraksi dengan orang "
             "sungguhan.",
             "I feel as if I am interacting with a real person."),
            ("AN5", "Gerakan dan ekspresi AI streamer ini terlihat hidup.",
             "The movements and expressions of this AI streamer look "
             "lifelike."),
        ]),
    "earja_2026_perceived_risk": (
        "Perceived risk items, Earja & Nursanti (2026) AI-streamer "
        "questionnaire, Section C",
        [
            ("PR1",
             "Saya khawatir produk yang dipromosikan AI streamer ini tidak "
             "sesuai dengan yang dijelaskan.",
             "I worry that the product promoted by this AI streamer does not "
             "match its description."),
            ("PR2",
             "Membeli produk kecantikan melalui live yang dipandu AI streamer "
             "berisiko bagi saya.",
             "Buying beauty products through a live session hosted by an AI "
             "streamer is risky for me."),
            ("PR3",
             "Saya khawatir data pribadi saya disalahgunakan saat "
             "berinteraksi dengan AI streamer ini.",
             "I worry that my personal data may be misused when I interact "
             "with this AI streamer."),
            ("PR4",
             "Saya khawatir mengalami kerugian uang jika membeli dari live "
             "yang dipandu AI streamer.",
             "I worry about losing money if I buy from a live session hosted "
             "by an AI streamer."),
            ("PR5",
             "Saya tidak yakin dengan hasil pembelian dari live yang dipandu "
             "AI streamer.",
             "I am uncertain about the outcome of purchases from a live "
             "session hosted by an AI streamer."),
        ]),
    "earja_2026_trust": (
        "Trust items, Earja & Nursanti (2026) AI-streamer questionnaire, "
        "Section C",
        [
            ("TR1",
             "Saya percaya AI streamer ini memberikan informasi produk yang "
             "akurat.",
             "I believe this AI streamer provides accurate product "
             "information."),
            ("TR2", "AI streamer ini dapat diandalkan.",
             "This AI streamer is reliable."),
            ("TR3",
             "Saya percaya AI streamer ini bertindak demi kepentingan "
             "konsumen.",
             "I believe this AI streamer acts in the interest of consumers."),
            ("TR4",
             "Saya percaya pada kemampuan AI streamer ini dalam "
             "merekomendasikan produk kecantikan.",
             "I trust this AI streamer's ability to recommend beauty "
             "products."),
            ("TR5", "Secara keseluruhan, saya mempercayai AI streamer ini.",
             "Overall, I trust this AI streamer."),
        ]),
    "earja_2026_fomo": (
        "Fear of missing out items, Earja & Nursanti (2026) AI-streamer "
        "questionnaire, Section C",
        [
            ("FO1",
             "Saya takut ketinggalan promo atau flash sale yang sedang "
             "berlangsung di live seperti ini.",
             "I am afraid of missing promotions or flash sales running in "
             "live sessions like this."),
            ("FO2",
             "Saya cemas jika tidak membeli sekarang, stok produk akan habis.",
             "I am anxious that the product will sell out if I do not buy "
             "now."),
            ("FO3",
             "Saya khawatir orang lain mendapatkan penawaran bagus yang tidak "
             "saya dapatkan.",
             "I worry that others get good deals that I miss."),
            ("FO4",
             "Saya merasa gelisah jika melewatkan live dan penawaran yang "
             "sedang ramai.",
             "I feel restless if I miss a popular live session and its "
             "offers."),
            ("FO5",
             "Saya merasa terdorong untuk terus menonton live agar tidak "
             "melewatkan penawaran.",
             "I feel compelled to keep watching live sessions so as not to "
             "miss offers."),
        ]),
    "earja_2026_purchase_intention": (
        "Purchase intention items, Earja & Nursanti (2026) AI-streamer "
        "questionnaire, Section C",
        [
            ("PI1",
             "Saya berminat membeli produk kecantikan dari live yang dipandu "
             "AI streamer ini.",
             "I am interested in buying beauty products from this AI-hosted "
             "live session."),
            ("PI2",
             "Kemungkinan besar saya akan membeli produk yang direkomendasikan "
             "AI streamer ini.",
             "I am likely to buy the products recommended by this AI "
             "streamer."),
            ("PI3",
             "Saya berencana membeli produk kecantikan melalui live TikTok "
             "Shop dalam waktu dekat.",
             "I plan to buy beauty products through TikTok Shop Live in the "
             "near future."),
            ("PI4",
             "Saya akan mempertimbangkan membeli produk yang direkomendasikan "
             "AI streamer ini.",
             "I will consider buying the products recommended by this AI "
             "streamer."),
        ]),
    "earja_2026_ai_literacy": (
        "AI literacy items, Earja & Nursanti (2026) AI-streamer "
        "questionnaire, Section C (collected, not used in the reported model)",
        [
            ("AL1",
             "Saya memahami secara umum cara kerja kecerdasan buatan (AI).",
             "I generally understand how artificial intelligence (AI) works."),
            ("AL2",
             "Saya dapat membedakan konten atau streamer buatan AI dari yang "
             "asli.",
             "I can distinguish AI-generated content or streamers from real "
             "ones."),
            ("AL3",
             "Saya mengetahui bahwa platform media sosial menggunakan AI untuk "
             "menyarankan produk.",
             "I know that social media platforms use AI to suggest products."),
        ]),
}

COLS = ["table", "section_id", "item", "instrument", "language",
        "instructions", "section_prompt", "item_text", "correct_response",
        "option_text", "resp", "instructions_translated",
        "section_prompt_translated", "item_text_translated",
        "option_text_translated"]


def observed_resp(table: str) -> set:
    """The resp values the staged response CSV actually holds."""
    path = RESP_DIR / f"{table}.csv"
    with open(path, newline="", encoding="utf-8") as f:
        return {int(r["resp"]) for r in csv.DictReader(f)}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for table, (instrument, items) in BLOCKS.items():
        seen = observed_resp(table)
        unused = sorted({r for r, _, _ in OPTIONS} - seen)
        if unused:
            print(f"  {table}: anchors {unused} never used by any respondent, "
                  "so no option row is emitted for them")
        rows = []
        for code, stem_id, stem_en in items:
            for resp, opt_id, opt_en in OPTIONS:
                if resp not in seen:
                    continue
                rows.append({
                    "table": table,
                    # No testlets or shared passages, so one section throughout
                    # -- the merge still needs a join key.
                    "section_id": f"{table}_1",
                    # The response table lowercases the deposit's header.
                    "item": code.lower(),
                    "instrument": instrument,
                    "language": LANGUAGE,
                    "instructions": "",
                    "section_prompt": "",
                    "item_text": stem_id,
                    "correct_response": "",
                    "option_text": opt_id,
                    "resp": resp,
                    "instructions_translated": "",
                    "section_prompt_translated": "",
                    "item_text_translated": stem_en,
                    "option_text_translated": opt_en,
                })
        path = OUT / f"{table}__items.csv"
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS)
            w.writeheader()
            w.writerows(rows)
        print(f"  -> {path.name}: {len(rows)} rows, "
              f"{len(items)} items x {len(seen)} observed option(s)")


if __name__ == "__main__":
    main()
