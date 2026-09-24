# verify_sun_2025_morality_study3_moralratings.R  (batch_327)
#
# Claim: each live item code itX is the Study 3 source column it.X of
# study3-maindat.csv (OSF 5e9y3, file wvq64), whose Codebook.xlsx (OSF 9ndt2,
# file e5a26) wording is the adjective shipped in item_text. data/sun_2025_morality.do
# derives the code mechanically: import delimited drops the dot, rename *, lower,
# then `gen id = _n` and `replace resp = round(resp)`.
#
# Route: id-level reproduction. For every live item, rebuild round(maindat[[src]])
# for EVERY candidate source column and count exact agreements with the live
# (id, resp) pairs. The mapping passes only if the claimed column reproduces all
# of the item's rows AND no other candidate column reproduces them all -- i.e. the
# route distinguishes every item from every other item.
# Second, independent check: keying polarity. The six negative adjectives must
# correlate negatively with informant general morality (it.MCQ.GM3-6 mean).

suppressMessages(library(irw))
TABLE <- "sun_2025_morality_study3_moralratings"

src <- read.csv("https://osf.io/download/wvq64/", check.names = FALSE)
src$id <- seq_len(nrow(src))
stata_round <- function(x) ifelse(x >= 0, floor(x + 0.5), -floor(-x + 0.5))

d <- as.data.frame(irw::irw_fetch(TABLE))
d <- d[!is.na(d$resp), ]

adj <- c("aggressive","athletic","attractive","considerate","courageous","cruel","fair",
         "forgiving","funny","generous","grateful","happy","hardworking","helpful","honest",
         "humble","integrity","intelligent","kind","kindness","loyal","manipulative",
         "meanspirited","prejudiced","principled","religious","responsible","selfcontrol",
         "selfish","sincere","socconscious","trustworthy")
cand <- paste0("it.", adj)
stopifnot(all(cand %in% names(src)))
claimed <- setNames(cand, paste0("it", adj))

ok <- TRUE
cat(sprintf("%-15s %5s %14s %10s %s\n", "item", "n", "claimed_match", "n_full_col", "other columns matching all rows"))
for (it in sort(unique(d$item))) {
    di <- d[d$item == it, ]
    hits <- sapply(cand, function(cc) sum(stata_round(src[[cc]][di$id]) == di$resp, na.rm = TRUE))
    full <- names(hits)[hits == nrow(di)]
    others <- setdiff(full, claimed[[it]])
    good <- hits[[claimed[[it]]]] == nrow(di) && length(others) == 0
    if (!good) ok <- FALSE
    cat(sprintf("%-15s %5d %8d/%-5d %10d %s\n", it, nrow(di), hits[[claimed[[it]]]], nrow(di),
                length(full), if (length(others)) paste(others, collapse = ",") else "-"))
}

gm <- rowMeans(src[, paste0("it.MCQ.GM", 3:6)], na.rm = TRUE)
neg <- c("cruel","aggressive","meanspirited","manipulative","selfish","prejudiced")
cat("\nPolarity check: r(item, informant general morality)\n")
w <- reshape(d[, c("id","item","resp")], idvar = "id", timevar = "item", direction = "wide")
w$gm <- gm[w$id]
for (a in adj[!adj %in% c("kindness","integrity")]) {
    r <- cor(w[[paste0("resp.it", a)]], w$gm, use = "pairwise.complete.obs")
    flag <- if ((a %in% neg) != (r < 0)) { ok <- FALSE; "  <-- POLARITY MISMATCH" } else ""
    cat(sprintf("  %-13s %s r = %+.2f%s\n", a, if (a %in% neg) "(neg)" else "     ", r, flag))
}

cat("\nWhat this establishes: every live item's (id, resp) pairs are reproduced exactly by its\n",
    "claimed source column and by no other candidate column, so the code->column tie is per-item.\n",
    "What it does not establish: the informant-form wording itself. The codebook prints the\n",
    "'To what extent is [target's name]...' stem and 1/5/9 anchors for the nominator (nt.*) block;\n",
    "the supplement confirms informants rated the same adjectives minus eight, but does not reprint\n",
    "the informant stem. itkindness/itintegrity are composites (analyses.R lines 218-219), not items.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
