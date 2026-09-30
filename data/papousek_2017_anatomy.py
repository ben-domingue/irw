"""papousek_2017_anatomy (+ papousek_2017_anatomy_nom) -- issue #1592.

Source: practiceanatomy.com public data set, http://data.practiceanatomy.com
(public-data.zip -> answers.csv; 1,182,065 answers, 18,563 learners, 2,894
terms; 16 Nov 2015 - 3 Jan 2017). Adaptive practice of anatomical terms, run by
the Adaptive Learning group at Masaryk University, the same group and format as
the `geography` table (slepemapy.cz). There is no data paper; the system is
described in Papousek, Pelanek & Stanislav (2014), EDM, hence the table name.

Licence: Open Database License (ODbL) for the database, Database Contents
License for its contents (landing page, "License").

Mapping
- id         = `user`
- item       = `item_asked` (the term id). As in `geography`, the item is the
               term; the task format is a trial detail, not part of the item.
- resp       = 1 if `item_answered == item_asked`, else 0. The file contains no
               "I don't know" answers (item_answered is never empty).
- resp_raw   = `item_answered`, the id of the term the learner chose. The id,
               not `term_name_answered`: every id has exactly one name, but 548
               names are shared by several ids (the same structure in different
               images), so the name loses the choice.
- rt         = `response_time` / 1000 (seconds); the 298 values <= 0 are set
               missing.
- date       = `time` as Unix seconds (UTC assumed; the source gives no zone).
- itemcov_term = `term_name_asked` (one name per item id), so the ids in
               `item` and `resp_raw` stay readable.
- trial_type = `type`: t2d = find the named term on the image, d2t = name the
               highlighted term.
- trial_options = `options`, number of options shown, the asked term included;
               0 = open question (no option list).
- trial_context = `context_name`, the image.
- trial_lang = `lang`, terminology language (cs, en, la (cs), la (en)); blank
               in 41% of rows in the source.

Repeated id-item rows are real: the system re-asks terms adaptively (342,886
repeats). `date` orders them. Dropped: ip_country, ip_id (not needed and
closer to identifying), practice_filter and the JSON systems/locations columns.

The nominal companion is the same table with resp_raw renamed to `text`
(datastandard.md, "The raw response and the nominal tranche").
"""
from pathlib import Path

import numpy as np
import pandas as pd

SRC = Path.home() / ".cache" / "irw_anatom" / "answers.csv"

d = pd.read_csv(SRC, low_memory=False, keep_default_na=False, na_values=[""])

df = pd.DataFrame({
    "id": d["user"],
    "item": d["item_asked"],
    "resp": (d["item_answered"] == d["item_asked"]).astype(int),
    "resp_raw": d["item_answered"].astype("Int64").astype(str),
    "rt": np.where(d["response_time"] > 0, d["response_time"] / 1000, np.nan),
    "date": (pd.to_datetime(d["time"], utc=True)
             - pd.Timestamp("1970-01-01", tz="UTC")) // pd.Timedelta("1s"),
    "itemcov_term": d["term_name_asked"],
    "trial_type": d["type"],
    "trial_options": d["options"],
    "trial_context": d["context_name"],
    "trial_lang": d["lang"],
})
assert df["resp_raw"].ne("<NA>").all()
# 2015-11-16 .. 2017-01-03 in Unix seconds
assert df["date"].between(1447632000, 1483488000).all()
assert df.groupby("item")["itemcov_term"].nunique().max() == 1
df = df.sort_values(["id", "date"], kind="stable")

df.to_csv("papousek_2017_anatomy.csv", index=False)
df.rename(columns={"resp_raw": "text"}).to_csv("papousek_2017_anatomy_nom.csv", index=False)
print(len(df), df["id"].nunique(), df["item"].nunique())
