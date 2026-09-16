# verify_yang_2026_pars3.R -- Step 5b evidence, re-runnable.
#
# Claim under test: item1 = intensity, item2 = duration, item3 = frequency.
# The processing script (data/yang_2026_crisis_coping.py) assigns item1..item3
# POSITIONALLY to raw S1 columns 25, 26, 27, so nothing at the source names them.
#
# Falsifiable prediction: the study's own S1 workbook carries a COMPUTED physical
# activity total in column 74, and the paper states the PARS-3 scoring formula
#     PA = Intensity x (Duration - 1) x Frequency
# The "- 1" applies to the DURATION item only, so the identity holds for exactly
# one of the three possible duration positions. Rebuild it from the LIVE IRW data
# joined to that stored total, per respondent.
#
# What this does NOT establish: the product is commutative, so intensity and
# frequency are interchangeable in the formula. This route pins item2 = duration
# and CANNOT separate item1 from item3. That half rests on presentation order
# (the paper lists intensity, duration, frequency in that order, and the column
# order puts duration second, which the formula confirms).

suppressMessages(library(irw))

TABLE <- "yang_2026_pars3"
SI_URL <- paste0("https://journals.plos.org/plosone/article/file",
                 "?type=supplementary&id=10.1371/journal.pone.0350928.s001")

cache <- file.path(".cache", TABLE, "s001.xlsx")
if (!file.exists(cache)) {
    dir.create(dirname(cache), recursive = TRUE, showWarnings = FALSE)
    utils::download.file(SI_URL, cache, mode = "wb", quiet = TRUE)
}

suppressMessages(library(readxl))
raw <- readxl::read_excel(cache, col_names = FALSE, .name_repair = "minimal")
raw <- as.data.frame(raw)
id_raw <- suppressWarnings(as.numeric(raw[[1]]))
pa_raw <- suppressWarnings(as.numeric(raw[[75]]))   # 0-based col 74 = stored PA total
keep <- !is.na(id_raw) & !is.na(pa_raw)
stored <- data.frame(id = id_raw[keep], pa = pa_raw[keep])

d <- irw::irw_fetch(TABLE)
d <- as.data.frame(d)
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w$id <- as.numeric(as.character(w$id))
m <- merge(w, stored, by = "id")

cat(sprintf("live respondents: %d   stored PA totals matched: %d\n", nrow(w), nrow(m)))
cat(sprintf("stored PA: mean %.3f sd %.3f range %g-%g\n",
            mean(m$pa), sd(m$pa), min(m$pa), max(m$pa)))

cands <- list(
  "duration = item1" = with(m, item2 * (item1 - 1) * item3),
  "duration = item2" = with(m, item1 * (item2 - 1) * item3),
  "duration = item3" = with(m, item1 * (item3 - 1) * item2))

cat("\nexact reproductions of the stored PARS-3 total:\n")
hits <- integer(0)
for (nm in names(cands)) {
    h <- sum(cands[[nm]] == m$pa)
    hits[nm] <- h
    cat(sprintf("  %-18s %5d / %d  (%.1f%%)\n", nm, h, nrow(m), 100 * h / nrow(m)))
}

cat(sprintf("\nper-item means (live): item1 %.3f  item2 %.3f  item3 %.3f\n",
            mean(m$item1), mean(m$item2), mean(m$item3)))
cat("Note: item1 and item3 enter the formula symmetrically, so this route does NOT\n",
    "distinguish intensity from frequency; it pins item2 = duration only.\n", sep = "")

ok <- hits[["duration = item2"]] == nrow(m) &&
      max(hits[c("duration = item1", "duration = item3")]) < nrow(m)
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
