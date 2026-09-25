# verify_nfc_kay_2025.R -- Step 5b re-runnable check (batch_407)
#
# CLAIM. nfc_xxx_01_x..07_x carry the seven Need for Chaos statements in the order shipped
# (01 "I get a kick when natural disasters...", 02 "I fantasize about a natural disaster...",
# 03 "I think society should be burned...", 04 "When I think about our political and social
# institutions...", 05 "We cannot fix the problems...", 06 "I need chaos around me...",
# 07 "Sometimes I just feel like destroying..."), and resp = raw + 4, so
# 1 = Strongly disagree (-3) ... 7 = Strongly agree (3).
#
# DERIVATION. data/kay_2025.R keeps the deposit's own column names as `item`
# (select(starts_with("nfc_xxx_")) + pivot_longer, names kept; single administration, no wave)
# and adds 4 to resp. The only link to establish is column -> wording; the study's own
# Qualtrics printout (OSF uzrgk, 'Qualtrics Survey (Time 1).pdf' au83k) prints each
# statement immediately followed by its export tag. NfC is not in the Time 2 printout (q9m27).
#
# ROUTE. Explicit code labels in the study's own survey (label match), with (0) tying the
# deposit CSV to the live table by per-item n/mean/floor/ceiling so the deposit's column
# names are shown to BE the live codes. Uses the deposit, not irw_fetch(), to stay off the
# Redivis export cap; live numbers hard-coded from item_stats.R run 2026-09-24.

V <- "view_only=aca403a5146240bda740e1e6d640751f"
dl <- function(id, f) { p <- file.path(tempdir(), f)
  if (!file.exists(p)) download.file(sprintf("https://osf.io/download/%s/?%s", id, V), p, quiet = TRUE, mode = "wb"); p }
d  <- read.csv(dl("z28r4", "kay_data.csv"))
ok <- TRUE
codes <- sprintf("nfc_xxx_%02d_x", 1:7)

# (0) deposit reproduces the live table (resp = raw + 4)
L <- list(n = rep(492, 7), m = c(1.40, 1.69, 1.78, 2.68, 2.76, 1.72, 1.42),
          fl = c(83.5, 73.6, 66.1, 38.4, 34.3, 69.1, 78.9), ce = c(1.6, 0.6, 1.6, 3.9, 3.3, 0.4, 0.8))
cat("(0) deposit (+4) vs live\n")
for (k in 1:7) {
  x <- d[[codes[k]]] + 4; x <- x[!is.na(x)]
  n <- length(x); m <- mean(x); fl <- 100 * mean(x == 1); ce <- 100 * mean(x == 7)
  cat(sprintf("  %-14s n %d/%d  mean %.4f/%.2f  floor%% %.1f/%.1f  ceil%% %.1f/%.1f\n",
              codes[k], n, L$n[k], m, L$m[k], fl, L$fl[k], ce, L$ce[k]))
  if (n != L$n[k] || abs(m - L$m[k]) > 0.006 || abs(fl - L$fl[k]) > 0.06 || abs(ce - L$ce[k]) > 0.06) ok <- FALSE
}

# (1) survey printout: text immediately preceding each export tag == shipped item_text
norm <- function(s) gsub("\\s+", " ", trimws(s))
CLAIM <- c(nfc_xxx_01_x = "I get a kick when natural disasters strike in foreign countries.",
           nfc_xxx_02_x = "I fantasize about a natural disaster wiping out most of humanity such that a small group of people can start all over.",
           nfc_xxx_03_x = "I think society should be burned to the ground.",
           nfc_xxx_04_x = "When I think about our political and social institutions, I cannot help thinking ‘just let them all burn’.",
           nfc_xxx_05_x = "We cannot fix the problems in our social institutions, we need to tear them down and start over.",
           nfc_xxx_06_x = "I need chaos around me—it is too boring if nothing is going on.",
           nfc_xxx_07_x = "Sometimes I just feel like destroying beautiful things.")
csvp <- "itemtables/batch_407/nfc_kay_2025__items.csv"
if (file.exists(csvp)) {
  sh <- unique(read.csv(csvp, stringsAsFactors = FALSE, encoding = "UTF-8")[, c("item", "item_text")])
  same <- nrow(sh) == 7 && all(sh$item_text == CLAIM[sh$item])
  cat(sprintf("(1a) shipped CSV item_text == CLAIM for all 7 items: %s\n", same)); if (!same) ok <- FALSE
}
if (nzchar(Sys.which("pdftotext"))) {
  txt <- trimws(gsub("\\f", "", system2("pdftotext", c("-raw", dl("au83k", "kay_t1.pdf"), "-"), stdout = TRUE)))
  tagi <- grep("^\\((t2_)?[a-z0-9]+_[a-z0-9_]+\\)$", txt)   # every export tag line
  oln  <- grep("^o( o)+$", txt)                              # radio-button rows
  cat("(1) Time 1 printout: statement printed immediately before each tag\n")
  for (k in 1:7) {
    pat <- sprintf("^\\(nfc_xxx_%02d_x\\)$", k)
    hit <- grep(pat, txt); if (length(hit) != 1) { cat("  tag not found once:", pat, "\n"); ok <- FALSE; next }
    prev <- max(c(tagi[tagi < hit], oln[oln < hit]))
    seg <- txt[(prev + 1):(hit - 1)]
    seg <- seg[!grepl("^Page [0-9]+ of [0-9]+$", trimws(seg))]
    seg <- sub("( o){7}$", "", seg)
    stmt <- norm(paste(seg, collapse = " "))
    match <- which(sapply(CLAIM, function(c) norm(c) == stmt))
    cat(sprintf("  %-16s -> %s\n", txt[hit], if (length(match)) names(CLAIM)[match] else paste("NO MATCH:", stmt)))
    if (!identical(unname(names(CLAIM)[match]), codes[k])) ok <- FALSE
  }
  t2 <- system2("pdftotext", c("-raw", dl("q9m27", "kay_t2.pdf"), "-"), stdout = TRUE)
  cat(sprintf("  Time 2 printout nfc tags: %d (expected 0: single administration)\n", length(grep("nfc_", t2))))
} else { cat("pdftotext unavailable -- cannot run the label route\n"); ok <- FALSE }

# (2) direction: printout anchors Strongly disagree (-3) ... Strongly agree (3); deposit
# nfc columns span -3..3, none is an _r column, script adds 4; all inter-item r positive
# (no reverse-keyed Chaos-R items administered).
rng <- range(unlist(d[, codes]), na.rm = TRUE)
r <- cor(d[, codes], use = "pair"); rmin <- min(r[upper.tri(r)])
cat(sprintf("(2) deposit raw range %d..%d -> live 1..7 after +4; min inter-item r %.2f\n", rng[1], rng[2], rmin))
if (!all(rng == c(-3, 3)) || rmin <= 0) ok <- FALSE

cat("Scope: (1) ties each code to one statement by the study's own tag, distinguishing all 7;\n",
    "(0) only shows the deposit IS the live table, it does not order items by itself.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
