# verify_moon_2023_selfesteem.R -- Step 5b check for batch_313.
#
# The item<->text tie is a LABEL match: the study's own questionnaire supplement
# (PeerJ 10.7717/peerj.16295, peerj-11-16295-s002.pdf, p.1) prints the data code
# (selfesteem1, se2..se10, selfesteem11) beside every item, and the IRW codes are
# the .sav column names unchanged (data/moon_2023_pregnancy_stress.py). That tie
# cannot be recomputed from data. What this script re-runs is what the data CAN
# falsify:
#   (1) keying polarity (route 6): the s002 key prints 4-3-2-1 for se3, se5, se9,
#       se10, selfesteem11 and 1-2-3-4 for the other six. Every item must correlate
#       more with its own printed polarity class than with the other class. A swap
#       of text across classes (e.g. se3<->se4) breaks this.
#   (2) stored direction of the reverse-printed items (routes 3 + external
#       criterion): if the five reverse items are stored already scored (as the s002
#       key says: circling under "not at all" = 4), their mean must correlate
#       POSITIVELY with the same respondents' spousal-support mean and NEGATIVELY
#       with their pregnancy-stress mean, and the stored-value total must reproduce
#       the paper's Table 2 (3.19 +/- 0.42) and Table 3 (r = .263 with support,
#       -.180 with stress). Stored raw, all of these signs would flip. The sibling
#       scales are read from the study's own .sav (same respondents, same id).
# NOT established here: order WITHIN a polarity class (e.g. se2 vs se4) -- that
# rests on the printed code labels in s002.

suppressMessages(library(irw))
TABLE <- "moon_2023_selfesteem"
REV <- c("se3", "se5", "se9", "se10", "selfesteem11")
POS <- c("selfesteem1", "se2", "se4", "se6", "se7", "se8")
PUB_MEAN <- 3.19; PUB_SD <- 0.42

d <- as.data.frame(irw::irw_fetch(TABLE))[, c("id", "item", "resp")]
w <- reshape(d, idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
it <- c(POS, REV)
R <- cor(w[, it], use = "pairwise")

ok1 <- TRUE
cat(sprintf("%-13s %6s %10s %10s\n", "item", "class", "r_own", "r_other"))
for (i in it) {
  own <- if (i %in% REV) REV else POS
  oth <- setdiff(it, own)
  a <- mean(R[i, setdiff(own, i)]); b <- mean(R[i, oth])
  cat(sprintf("%-13s %6s %10.3f %10.3f\n", i, if (i %in% REV) "rev" else "pos", a, b))
  if (a <= b) ok1 <- FALSE
}

pm <- rowMeans(w[, it], na.rm = TRUE)
alt <- w[, it]; alt[, REV] <- 5 - alt[, REV]
pm_alt <- rowMeans(alt, na.rm = TRUE)
cat(sprintf("\nstored-value scale mean %.2f (SD %.2f)  vs published %.2f (SD %.2f)\n",
            mean(pm), sd(pm), PUB_MEAN, PUB_SD))
cat(sprintf("if the 5 reverse items were stored raw, scored mean would be %.2f (SD %.2f)\n",
            mean(pm_alt), sd(pm_alt)))

# External criterion from the study's .sav (Europe PMC supplementary zip).
zipf <- tempfile(fileext = ".zip")
cache <- c("itemtext/.cache/moon_2023_selfesteem/suppl.zip", ".cache/moon_2023_selfesteem/suppl.zip"); cache <- cache[file.exists(cache)][1]; if (is.na(cache)) cache <- "none"
if (file.exists(cache)) invisible(file.copy(cache, zipf)) else
  download.file("https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10629385/supplementaryFiles",
                zipf, mode = "wb", quiet = TRUE)
sav <- unzip(zipf, files = "peerj-11-16295-s001.sav", exdir = tempdir())
s <- haven::read_sav(sav)
num <- function(x, hi) { x <- suppressWarnings(as.numeric(haven::zap_labels(x))); x[!(x >= 1 & x <= hi)] <- NA; x }
sup <- rowMeans(sapply(paste0("socialsupportp", 1:11), function(v) num(s[[v]], 6)), na.rm = TRUE)
st  <- rowMeans(sapply(paste0("pregnancystress", 1:11), function(v) num(s[[v]], 4)), na.rm = TRUE)
ext <- data.frame(id = as.numeric(s$id), sup = sup, st = st)
m <- merge(data.frame(id = as.numeric(w$id), rev = rowMeans(w[, REV], na.rm = TRUE),
                      pos = rowMeans(w[, POS], na.rm = TRUE), tot = pm, tot_alt = pm_alt), ext, by = "id")
cat(sprintf("matched respondents: %d\n", nrow(m)))
cat(sprintf("%-26s %10s %10s\n", "", "r(support)", "r(stress)"))
for (v in c("rev", "pos", "tot", "tot_alt"))
  cat(sprintf("%-26s %10.3f %10.3f\n", c(rev = "reverse-printed 5, stored", pos = "positive 6, stored",
      tot = "total, stored (paper .263/-.180)", tot_alt = "total, if 5 stored raw")[v],
      cor(m[[v]], m$sup, use = "pairwise"), cor(m[[v]], m$st, use = "pairwise")))
ok2 <- abs(mean(pm) - PUB_MEAN) <= 0.02 && abs(sd(pm) - PUB_SD) <= 0.02 &&
       cor(m$rev, m$sup, use = "pairwise") > 0.1 && cor(m$rev, m$st, use = "pairwise") < -0.1 &&
       abs(cor(m$tot, m$sup, use = "pairwise") - 0.263) <= 0.05
cat("polarity classes separate:", ok1, "| reverse items stored scored (key direction):", ok2, "\n")
cat("Note: order within a polarity class is fixed by the s002 printed code labels, not by this script.\n")
cat(if (ok1 && ok2) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
