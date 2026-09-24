# verify_yao_2020_gad.R -- Step 5b mapping evidence, re-runnable.
#
# CLAIM UNDER TEST: the live item codes gad1..gad7 carry the canonical GAD-7
# wording in canonical numbering (gad1 = "Feeling nervous, anxious or on edge"
# ... gad7 = "Feeling afraid as if something awful might happen").
#
# Nothing in the study ties those codes to text. data/yao_2020_intolerance_
# uncertainty.py melts the deposit's own columns gad1..gad7 by name (regex
# 'gad\d+', var_name='item'), so the IRW code IS the source column name --
# no positional step. What is inferred is what the source column NAME means:
# the .sav carries no variable labels and no value labels (0 of 109 columns
# labelled), the .xlsx header is the same bare codes, and readme.txt only
# names the block "GAD-7". So the tie rests on the GAD-7 form's own printed
# numbering 1-7 and has to be tested against content.
#
# The test is cross-instrument: the same respondents completed the BAI-21 and
# (n=838) the BDI-21 in the same deposit file, which this script downloads.
# ids: the processing script assigns id = row index of the .sav (after the
# 999 recode), so live id i == .sav row i; checked below before anything else.
#
# Predictions, each of which a permutation of the GAD labels would break:
#   P1  argmax_i corr(gad_i, bai4) == gad4   [BAI 4 "Unable to relax" <->
#       GAD 4 "Trouble relaxing"], AND reciprocally argmax_j corr(gad4, bai_j)
#       == bai4 across all 21 BAI items.
#   P2  gad6 ("Becoming easily annoyed or irritable") is argmax_i corr(gad_i,
#       bdi11) AND argmax_i corr(gad_i, bdi17) -- the BDI's irritability item
#       is #11 in BDI-I and #17 in BDI-II, and the deposit does not say which
#       version, so the prediction is required at BOTH candidate positions.
#   P3  (route 7, marker) the two least-endorsed items are {gad5, gad7}
#       (restlessness, fear something awful) -- the pair community samples
#       routinely endorse least. Pins the pair, NOT which is which.
#   P4  (option axis) the modal response on every item is 0 ("Not at all") or
#       1 ("Several days") and every item mean is < 1.5 on 0-3; a flipped coding
#       would put the modal response at 2-3 and means near 2.2-2.6. readme.txt states the recode
#       (1=0)(2=1)(3=2)(4=3) applied to gad1-gad7 in the .sav.
#
# REPORTED, NOT PASS CONDITIONS (two natural content-twin predictions that do
# NOT hold, printed so a reader can weigh them):
#   bai5 "Fear of worst happening" -- expected gad7, observed argmax gad3.
#   bai10 "Nervous"               -- expected gad1, observed argmax gad4.
# Both sit inside a strong general factor (every gad item correlates
# 0.35-0.51 with bai5 and 0.35-0.47 with bai10), so they are underpowered
# rather than contradicting, but they are misses and are disclosed.
#
# WHAT THIS DOES NOT ESTABLISH: it pins gad4 and gad6, and the {gad5, gad7}
# pair as a pair. It does NOT distinguish gad1/gad2/gad3 from one another, nor
# gad5 from gad7. Status is therefore PARTIAL, not VERIFIED. P1 also assumes
# the deposit's bai1..bai21 are in canonical BAI order.

suppressMessages(library(irw))

TABLE <- "yao_2020_gad"
KEY   <- "94p8m47y58"
gad <- paste0("gad", 1:7)
bai <- paste0("bai", 1:21)

# --- live IRW data ----------------------------------------------------------
d <- as.data.frame(irw::irw_fetch(TABLE))[, c("id", "item", "resp")]
w <- reshape(d, idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[, c("id", gad)]

# --- the study's deposit (.sav) ---------------------------------------------
meta <- jsonlite::fromJSON(
  sprintf("https://data.mendeley.com/public-api/datasets/%s", KEY))
f <- meta$files
url <- f$content_details$download_url[f$filename == "data upload_IU.sav"]
tf <- tempfile(fileext = ".sav")
utils::download.file(url, tf, quiet = TRUE, mode = "wb")
x <- as.data.frame(haven::zap_labels(haven::read_sav(tf)))
x[x == 999] <- NA
x$id <- seq_len(nrow(x))

# id alignment check (plumbing, not mapping evidence)
xm <- merge(w, x[, c("id", gad)], by = "id", suffixes = c("", ".sav"))
mism <- sum(as.matrix(xm[, gad]) != as.matrix(xm[, paste0(gad, ".sav")]),
            na.rm = TRUE)
cat(sprintf("id alignment: %d live respondents matched to .sav rows; %d cell mismatches\n\n",
            nrow(xm), mism))

m <- merge(w, x[, c("id", bai, "bdi11", "bdi17")], by = "id")
r <- function(a, b) cor(m[[a]], m[[b]], use = "pairwise.complete.obs")

argmax_block <- function(target, label) {
  v <- sapply(gad, r, b = target)
  cat(sprintf("corr(gad_i, %s)  [%s]\n", target, label))
  for (i in gad) cat(sprintf("  %-5s %6.3f\n", i, v[i]))
  top <- names(which.max(v))
  cat(sprintf("  -> strongest: %s\n\n", top))
  top
}

# --- P1 ---------------------------------------------------------------------
t4 <- argmax_block("bai4", "BAI 4 Unable to relax; predicted gad4")
c4 <- sapply(bai, function(b) r("gad4", b))
o <- sort(c4, decreasing = TRUE)[1:3]
cat("corr(gad4, bai_j), top 3 of 21:", paste(sprintf("%s %.3f", names(o), o), collapse = ", "), "\n\n")
p1 <- t4 == "gad4" && names(which.max(c4)) == "bai4"

# --- P2 ---------------------------------------------------------------------
t11 <- argmax_block("bdi11", "BDI-I 11 Irritability; predicted gad6")
t17 <- argmax_block("bdi17", "BDI-II 17 Irritability; predicted gad6")
p2 <- t11 == "gad6" && t17 == "gad6"

# --- P3 ---------------------------------------------------------------------
mu <- tapply(d$resp, d$item, mean)[gad]
cat("item means (0-3):\n")
for (i in names(sort(mu))) cat(sprintf("  %-5s %5.3f\n", i, mu[i]))
low2 <- names(sort(mu))[1:2]
cat(sprintf("  -> two lowest: %s (predicted gad5, gad7)\n\n", paste(low2, collapse = ", ")))
p3 <- setequal(low2, c("gad5", "gad7"))

# --- P4: option axis --------------------------------------------------------
tab <- table(d$item, d$resp)[gad, ]
print(tab)
modal <- colnames(tab)[apply(tab, 1, which.max)]
cat(sprintf("modal resp per item: %s; max item mean %.3f\n\n",
            paste(modal, collapse = " "), max(mu)))
p4 <- all(modal %in% c("0", "1")) && max(mu) < 1.5

# --- reported misses (not pass conditions) ----------------------------------
cat("REPORTED, NOT PASS CONDITIONS:\n")
m5 <- argmax_block("bai5", "BAI 5 Fear of worst happening; content twin of gad7")
m10 <- argmax_block("bai10", "BAI 10 Nervous; content twin of gad1")

ok <- c(P1 = p1, P2 = p2, P3 = p3, P4 = p4)
for (p in names(ok)) cat(sprintf("%s: %s\n", p, if (ok[p]) "PASS" else "FAIL"))
cat("\nScope: pins gad4, gad6, and {gad5,gad7} as a pair. gad1/gad2/gad3 are NOT\n",
    "distinguished from one another, nor gad5 from gad7 -- status PARTIAL.\n", sep = "")

cat(if (all(ok) && mism == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
