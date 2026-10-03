# verify_selfcompassionscale_shortform_fuochi_2025.R -- batch_430, Step 5b.
#
# Claim: live item codes (the deposit's own column names in 'Total data 6 samples.csv',
# lower-cased by data/selfcompassionscale_shortform_fuochi_2025.R) map to SCS-SF item
# numbers as  oi1=1 sk1=2 m1=3 i1=4 ch1=5 sk2=6 m2=7 i2=8 oi2=9 ch2=10 sj1=11 sj2=12,
# the numbering Fuochi, Voci & Moe (2025) Table 2 prints against each item's wording.
#
# Route: the SAME OSF deposit (hfvxd) also ships one file per sample ('Sample A.csv' ..
# 'Sample F.csv') in which the SCS-SF columns are named by item NUMBER, sc1..sc12. Join
# the live table to those files person-by-person (live id = "<sample>_<ID>") and ask, for
# every live code, which sc column its responses reproduce. A correct mapping puts ~100%
# agreement on the claimed sc column and chance-level (~20-50%) agreement everywhere else;
# any swap -- including within a subscale pair (sk1 vs sk2) -- moves the maximum off the
# claimed column. Also checks that the per-sample file's OWN reverse-scored duplicates
# (Sample A: sc1r sc4r sc8r sc9r sc11r sc12r) are exactly 6 - raw, i.e. the sc numbering
# is the SCS-SF numbering (reverse set {1,4,8,9,11,12} per Neff's scoring key).
suppressMessages(library(irw))

TABLE <- "selfcompassionscale_shortform_fuochi_2025"
VK <- "51c67658f98149eead09887de0fc9467"
CLAIM <- c(oi1 = 1, sk1 = 2, m1 = 3, i1 = 4, ch1 = 5, sk2 = 6, m2 = 7, i2 = 8,
           oi2 = 9, ch2 = 10, sj1 = 11, sj2 = 12)

osf_list <- function(url) jsonlite::fromJSON(url)$data
root <- osf_list(sprintf("https://api.osf.io/v2/nodes/hfvxd/files/osfstorage/?view_only=%s", VK))
folder <- root$relationships$files$links$related$href[root$attributes$kind == "folder"]
files <- osf_list(folder)
get_sample <- function(s) {
  u <- files$links$download[files$attributes$name == sprintf("Sample %s.csv", s)]
  x <- read.csv2(u, sep = ";", dec = ",", na.strings = c(".", ""))
  names(x) <- tolower(names(x)); x
}

d <- irw::irw_fetch(TABLE)
d <- as.data.frame(d)[, c("id", "item", "resp")]
# The published table's ids are the bare per-sample IDs (the "<sample>_" prefix in the
# current processing script postdates the upload); accept either form. Ids that recur
# across samples give repeated (id,item) pairs (the known 3,024-row defect, irw#1856):
# drop every such pair before joining, since it cannot be attributed to one person.
d$id <- sub("^[A-F]_", "", as.character(d$id))
key <- paste(d$id, d$item)
d <- d[!(key %in% key[duplicated(key)]), ]
wide <- reshape(d, idvar = "id", timevar = "item", direction = "wide")
names(wide) <- sub("^resp\\.", "", names(wide))

agree_num <- matrix(0, 12, 12, dimnames = list(names(CLAIM), paste0("sc", 1:12)))
agree_den <- agree_num
rev_ok <- NA
for (s in LETTERS[1:6]) {
  x <- get_sample(s)
  x <- x[!duplicated(x$id) & !duplicated(x$id, fromLast = TRUE), ]
  x$lid <- as.character(x$id)
  m <- merge(wide, x, by.x = "id", by.y = "lid")
  cat(sprintf("Sample %s: %d persons joined\n", s, nrow(m)))
  for (cc in names(CLAIM)) for (k in 1:12) {
    a <- m[[cc]]; b <- m[[paste0("sc", k)]]; ok <- !is.na(a) & !is.na(b)
    agree_num[cc, k] <- agree_num[cc, k] + sum(a[ok] == b[ok])
    agree_den[cc, k] <- agree_den[cc, k] + sum(ok)
  }
  if (s == "A") {
    rv <- c(1, 4, 8, 9, 11, 12)
    rev_ok <- all(sapply(rv, function(k) all(x[[paste0("sc", k, "r")]] == 6 - x[[paste0("sc", k)]], na.rm = TRUE)))
    cat("Sample A's own reversed columns:", paste0("sc", rv, "r", collapse = " "),
        "== 6 - raw for all rows:", rev_ok, "\n")
  }
}
agree <- agree_num / agree_den
cat("\nAgreement (share of joined responses identical), live code x per-sample sc column:\n")
print(round(agree, 3))

cat(sprintf("\n%-5s %8s %8s %9s %12s\n", "item", "claimed", "argmax", "agree", "next_best"))
pass <- TRUE
for (cc in names(CLAIM)) {
  am <- which.max(agree[cc, ]); nb <- max(agree[cc, -CLAIM[cc]])
  cat(sprintf("%-5s %8s %8s %9.3f %12.3f\n", cc, paste0("sc", CLAIM[cc]), names(am), agree[cc, CLAIM[cc]], nb))
  if (am != CLAIM[cc] || agree[cc, CLAIM[cc]] < 0.95 || nb > 0.7) pass <- FALSE
}
if (!isTRUE(rev_ok)) pass <- FALSE
cat("\nEstablishes: each live code reproduces exactly one per-sample column sc1..sc12 (every code",
    "distinguished from every other, within-subscale pairs included), and sc numbering = SCS-SF numbering",
    "(reverse set {1,4,8,9,11,12}). Does NOT itself establish the wording: that sc<k> is Table 2's item <k>",
    "rests on the numbering, corroborated by the paper naming 'Common Humanity 2' with item 10's wording.\n")
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
