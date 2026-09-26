# verify_den_kay_2025.R -- Step 5b re-runnable check (batch_449)
#
# CLAIM. den_xxx_01_x..04_x carry the four Denialism statements in the order shipped
# (01 "Much of the information we receive is wrong.", 02 "I often disagree with conventional
# views about the world.", 03 "Official government accounts of events cannot be trusted.",
# 04 "Major events are not always what they seem."), and live resp = deposit raw + 4, so
# 1 = Strongly disagree (-3) ... 7 = Strongly agree (3).
#
# DERIVATION. data/kay_2025.R keeps the deposit's own column names as `item`
# (select(starts_with("den_xxx_")) + pivot_longer, names kept; single administration, no wave)
# and adds 4 to resp. The only link to establish is column -> wording; the study's own
# Qualtrics printout (OSF uzrgk, 'Qualtrics Survey (Time 1).pdf' au83k) prints each
# statement immediately followed by its export tag. DEN is not in the Time 2 printout (q9m27).
#
# ROUTE. Explicit code labels in the study's own survey (label match), with (0) tying the
# deposit CSV to the live table cell for cell (item x resp counts) so the deposit's column
# names are shown to BE the live codes and the +4 shift is confirmed. Uses the deposit, not
# irw_fetch(), to stay off the Redivis export cap; live counts hard-coded from
# table(item, resp) on the live table, run 2026-09-25.

V <- "view_only=aca403a5146240bda740e1e6d640751f"
dl <- function(id, f) { p <- file.path(tempdir(), f)
  if (!file.exists(p)) download.file(sprintf("https://osf.io/download/%s/?%s", id, V), p, quiet = TRUE, mode = "wb"); p }
d  <- read.csv(dl("z28r4", "kay_data.csv"))
ok <- TRUE
codes <- sprintf("den_xxx_%02d_x", 1:4)

# (0) deposit (+4) reproduces the live table cell for cell
LIVE <- rbind(den_xxx_01_x = c(41, 74, 79, 104, 113, 59, 22),
              den_xxx_02_x = c(41, 68, 73, 127, 114, 49, 20),
              den_xxx_03_x = c(40, 67, 61,  85, 113, 72, 54),
              den_xxx_04_x = c(41, 64, 49,  77, 141, 73, 47))
cat("(0) deposit (raw + 4) counts at resp 1..7 vs live\n")
for (k in codes) {
  x <- d[[k]] + 4; dep <- as.numeric(table(factor(x, levels = 1:7)))
  cat(sprintf("  %-14s deposit %s\n  %-14s live    %s\n", k, paste(dep, collapse = " "), "", paste(LIVE[k, ], collapse = " ")))
  if (!all(dep == LIVE[k, ])) ok <- FALSE
}
# unshifted deposit would NOT match (guards against the gcb5_2025 live-unshifted case)
unsh <- as.numeric(table(factor(d$den_xxx_01_x, levels = 1:7)))
cat(sprintf("  unshifted deposit den_xxx_01_x at 1..7: %s (must differ from live)\n", paste(unsh, collapse = " ")))
if (all(unsh == LIVE["den_xxx_01_x", ])) ok <- FALSE

# (1) survey printout: text immediately preceding each export tag == shipped item_text
norm <- function(s) gsub("\\s+", " ", trimws(s))
CLAIM <- c(den_xxx_01_x = "Much of the information we receive is wrong.",
           den_xxx_02_x = "I often disagree with conventional views about the world.",
           den_xxx_03_x = "Official government accounts of events cannot be trusted.",
           den_xxx_04_x = "Major events are not always what they seem.")
csvp <- "itemtables/batch_449/den_kay_2025__items.csv"
if (file.exists(csvp)) {
  sh <- unique(read.csv(csvp, stringsAsFactors = FALSE, encoding = "UTF-8")[, c("item", "item_text")])
  same <- nrow(sh) == 4 && all(sh$item_text == CLAIM[sh$item])
  cat(sprintf("(1a) shipped CSV item_text == CLAIM for all 4 items: %s\n", same)); if (!same) ok <- FALSE
} else cat("(1a) shipped CSV not found from this working directory; skipped\n")
if (nzchar(Sys.which("pdftotext"))) {
  txt <- trimws(gsub("\\f", "", system2("pdftotext", c("-raw", dl("au83k", "kay_t1.pdf"), "-"), stdout = TRUE)))
  tagi <- grep("^\\((t2_)?[a-z0-9]+_[a-z0-9_]+\\)$", txt)   # every export tag line
  oln  <- grep("^o( o)+$", txt)                              # radio-button rows
  cat("(1) Time 1 printout: statement printed immediately before each tag\n")
  for (k in 1:4) {
    pat <- sprintf("^\\(den_xxx_%02d_x\\)$", k)
    hit <- grep(pat, txt); if (length(hit) != 1) { cat("  tag not found once:", pat, "\n"); ok <- FALSE; next }
    prev <- max(c(tagi[tagi < hit], oln[oln < hit]))
    seg <- txt[(prev + 1):(hit - 1)]
    seg <- seg[!grepl("^Page [0-9]+ of [0-9]+$", trimws(seg))]
    stmt <- norm(paste(seg, collapse = " "))
    match <- which(sapply(CLAIM, function(c) norm(c) == stmt))
    cat(sprintf("  %-16s -> %s  [%s]\n", txt[hit], if (length(match)) names(CLAIM)[match] else "NO MATCH", stmt))
    if (!identical(unname(names(CLAIM)[match]), codes[k])) ok <- FALSE
  }
  t2 <- system2("pdftotext", c("-raw", dl("q9m27", "kay_t2.pdf"), "-"), stdout = TRUE)
  cat(sprintf("  Time 2 printout den tags: %d (expected 0: single administration)\n", length(grep("den_", t2))))
} else { cat("pdftotext unavailable -- cannot run the label route\n"); ok <- FALSE }

# (2) direction: printout anchors Strongly disagree (-3) ... Strongly agree (3); deposit den
# columns span -3..3, none is an _r column, all inter-item r positive (no reverse keying).
rng <- range(unlist(d[, codes]), na.rm = TRUE)
r <- cor(d[, codes], use = "pair"); rmin <- min(r[upper.tri(r)])
cat(sprintf("(2) deposit raw range %d..%d -> live 1..7 after +4; _r columns: %d; min inter-item r %.2f\n",
            rng[1], rng[2], length(grep("^den_.*_r$", names(d))), rmin))
if (!all(rng == c(-3, 3)) || rmin <= 0) ok <- FALSE

cat("Scope: (1) ties each code to one statement by the study's own export tag, distinguishing all 4;\n",
    "(0) only shows the deposit IS the live table and fixes the +4 shift; it does not order items by itself.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
