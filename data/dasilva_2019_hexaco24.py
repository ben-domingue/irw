#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Dataset_for_the_paper_Incomplete_Information_Choices_Cognitive_Ability_and_Personality/7582019
# DOI: 10.6084/m9.figshare.7582019.v1
# License: CC BY 4.0

import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://ndownloader.figshare.com/files/14080583"
HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

# HEXACO-24: item text (in original column order) -> (item number, dimension, reverse-scored)
# Mapping taken from the source file's "Dimensões" sheet.
ITEM_INFO = [
    ("Posso olhar para uma pintura por um longo tempo.", 1, "openness", False),
    ("Me certifico que as coisas estão no lugar certo.", 2, "conscientiousness", False),
    ("Fico indiferente com alguém que foi ruim comigo.", 3, "agreeableness", True),
    ("Ninguém gosta de falar comigo.", 4, "extraversion", True),
    ("Tenho medo de sentir dor.", 5, "emotionality", False),
    ("Acho difícil mentir.", 6, "honesty_humility", False),
    ("Acho que conhecimento é algo chato.", 7, "openness", True),
    ("Adio tarefas complicadas o maior tempo possível.", 8, "conscientiousness", True),
    ("Critico as pessoas com frequência.", 9, "agreeableness", True),
    ("Me aproximo de pessoas estranhas com facilidade.", 10, "extraversion", False),
    ("Me preocupo muito menos do que a maioria das pessoas.", 11, "emotionality", True),
    ("Gostaria de saber como ganhar muito dinheiro de maneira desonesta.", 12, "honesty_humility", True),
    ("Tenho muita imaginação.", 13, "openness", False),
    ("Trabalho muito precisamente, dou atenção aos pequenos detalhes.", 14, "conscientiousness", False),
    ("Tendo a concordar com a opinião dos outros.", 15, "agreeableness", False),
    ("Gosto de conversar com os outros.", 16, "extraversion", False),
    ("Posso facilmente superar as dificuldades por conta própria.", 17, "emotionality", True),
    ("Quero ser uma pessoa famosa.", 18, "honesty_humility", True),
    ("Gosto de pessoas com ideias novas.", 19, "openness", False),
    ("Costumo fazer coisas sem pensar.", 20, "conscientiousness", True),
    ("Mesmo quando sou maltratado, mantenho a calma.", 21, "agreeableness", False),
    ("Raramente sou alegre.", 22, "extraversion", True),
    ("Choro ao assistir filmes tristes ou românticos.", 23, "emotionality", False),
    ("Tenho direito a tratamento diferenciado.", 24, "honesty_humility", True),
]

RESP_MAP = {
    "Discordo muito": 1,
    "Discordo pouco": 2,
    "Nem concordo nem discordo": 3,
    "Concordo pouco": 4,
    "Concordo muito": 5,
}


def convert():
    os.makedirs(OUT_DIR, exist_ok=True)
    raw_path = os.path.join(OUT_DIR, "_dasilva_2019_raw.xlsx")
    r = requests.get(URL, headers=HEADERS)
    r.raise_for_status()
    with open(raw_path, "wb") as f:
        f.write(r.content)

    df = pd.read_excel(raw_path, sheet_name="Base de dados")
    os.remove(raw_path)

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)

    item_cols = [text for text, *_ in ITEM_INFO]
    for c in item_cols:
        assert c in df.columns, f"expected item column not found: {c!r}"
        assert set(df[c].dropna().unique()) <= set(RESP_MAP), f"unexpected value in {c!r}"

    rename = {text: f"HEXACO24_{num}" for text, num, *_ in ITEM_INFO}
    df = df.rename(columns=rename)
    item_cols = list(rename.values())

    long = df.melt(id_vars=["id"], value_vars=item_cols,
                   var_name="item", value_name="resp")
    long["resp"] = long["resp"].map(RESP_MAP)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)

    dim_map = {f"HEXACO24_{num}": dim for _, num, dim, _ in ITEM_INFO}
    rev_map = {f"HEXACO24_{num}": int(rev) for _, num, _, rev in ITEM_INFO}
    long["itemcov_dimension"] = long["item"].map(dim_map)
    long["itemcov_reverse_scored"] = long["item"].map(rev_map)

    out_cols = ["id", "item", "resp", "itemcov_dimension", "itemcov_reverse_scored"]
    long = long[out_cols].sort_values(["id", "item"]).reset_index(drop=True)

    out_name = "dasilva_2019_hexaco24"
    csv_path = os.path.join(OUT_DIR, out_name + ".csv")
    long.to_csv(csv_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
