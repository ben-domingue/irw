# verify_onecm_kay_2025.R -- Step 5b re-runnable check (batch_407)
#
# CLAIM. cm1_xxx_01_x is the statement "I think that the official version of the events
# given by the authorities very often hides the truth." (Lantian et al. 2016 one-item
# conspiracy measure, administered without its preamble), and resp = raw + 4, so
# 1 = Strongly disagree (-3) ... 7 = Strongly agree (3).
#
# DERIVATION. data/kay_2025.R keeps the deposit's own column name as `item`
# (select(cm1_xxx_01_x) / t2_cm1_xxx_01_x with t2_ stripped) and adds 4 to resp. The study's
# own Qualtrics printouts (OSF uzrgk, 'Qualtrics Survey (Time 1).pdf' au83k and
# '(Time 2).pdf' q9m27) print the statement immediately followed by its export tag.
#
# ROUTE. (1) explicit code label in the study's own survey, both waves; (2) response-frequency
# match (route 9): deposit raw + 4 vs live, per wave, cell for cell over all 7 levels -- this
# is what pins the resp axis (a flipped direction or an unshifted table breaks it), since the
# item axis has only one item. Live is fetched with irw_fetch (881 rows; small table).

suppressMessages(library(irw))
V <- "view_only=aca403a5146240bda740e1e6d640751f"
dl <- function(id, f) { p <- file.path(tempdir(), f)
  if (!file.exists(p)) download.file(sprintf("https://osf.io/download/%s/?%s", id, V), p, quiet = TRUE, mode = "wb"); p }
ok <- TRUE
norm <- function(s) gsub("\\s+", " ", trimws(s))
CLAIM <- "I think that the official version of the events given by the authorities very often hides the truth."
LABELS <- c("Strongly disagree", "Moderately disagree", "Slightly disagree", "Neither agree nor disagree",
            "Slightly agree", "Moderately agree", "Strongly agree")

# (0) shipped CSV carries the claim
csvp <- "itemtables/batch_407/onecm_kay_2025__items.csv"
if (file.exists(csvp)) {
  sh <- read.csv(csvp, stringsAsFactors = FALSE, encoding = "UTF-8")
  s0 <- all(sh$item_text == CLAIM) && identical(sh$option_text[order(sh$resp)], LABELS) &&
        identical(sort(sh$resp), 1:7)
  cat(sprintf("(0) shipped CSV item_text == CLAIM and option_text 1..7 == Strongly disagree..Strongly agree: %s\n", s0))
  if (!s0) ok <- FALSE
}

# (1) survey printouts: text immediately preceding the export tag == CLAIM
if (nzchar(Sys.which("pdftotext"))) {
  for (sv in list(c("au83k", "t1.pdf", ""), c("q9m27", "t2.pdf", "t2_"))) {
    txt <- trimws(gsub("\\f", "", system2("pdftotext", c("-raw", dl(sv[1], paste0("kay1cm_", sv[2])), "-"), stdout = TRUE)))
    tagi <- grep("^\\((t2_)?[a-z0-9]+_[a-z0-9_]+\\)$", txt)
    oln  <- grep("^o( o)+$", txt)
    hit <- grep(sprintf("^\\(%scm1_xxx_01_x\\)$", sv[3]), txt)
    if (length(hit) != 1) { cat("  tag not found once in", sv[2], "\n"); ok <- FALSE; next }
    prev <- max(c(tagi[tagi < hit], oln[oln < hit]))
    seg <- txt[(prev + 1):(hit - 1)]
    seg <- seg[!grepl("^Page [0-9]+ of [0-9]+$", seg)]
    stmt <- norm(paste(seg, collapse = " "))
    m <- identical(stmt, CLAIM)
    cat(sprintf("(1) %s %s <- \"%s\"  match=%s\n", sv[2], txt[hit], stmt, m))
    if (!m) ok <- FALSE
    anch <- norm(paste(txt, collapse = " "))
    a <- grepl("Strongly disagree \\(-3\\) Moderately disagree \\(- 2\\) Slightly disagree \\(-1\\) Neither agree nor disagree \\(0\\) Slightly agree \\(1\\) Moderately agree \\(2\\) Strongly agree \\(3\\)", anch)
    cat(sprintf("    anchor header Strongly disagree (-3) ... Strongly agree (3) printed: %s\n", a))
    if (!a) ok <- FALSE
  }
} else { cat("pdftotext unavailable -- cannot run the label route\n"); ok <- FALSE }

# (2) route 9: deposit raw + 4 vs live, per wave, per level
d <- read.csv(dl("z28r4", "kay1cm_data.csv"))
live <- as.data.frame(irw::irw_fetch("onecm_kay_2025"))
for (w in 1:2) {
  col <- if (w == 1) "cm1_xxx_01_x" else "t2_cm1_xxx_01_x"
  raw <- d[[col]]; raw <- raw[!is.na(raw)]
  dep <- table(factor(raw + 4, levels = 1:7))
  lv  <- table(factor(live$resp[live$wave == w & !is.na(live$resp)], levels = 1:7))
  flip <- table(factor(4 - raw, levels = 1:7))
  cat(sprintf("(2) wave %d  raw range %d..%d\n    deposit+4: %s\n    live     : %s\n    (flipped : %s)\n",
              w, min(raw), max(raw), paste(dep, collapse = "/"), paste(lv, collapse = "/"), paste(flip, collapse = "/")))
  if (!identical(as.integer(dep), as.integer(lv)) || identical(as.integer(flip), as.integer(lv))) ok <- FALSE
  if (!all(range(raw) == c(-3, 3))) ok <- FALSE
}

cat("Scope: one item, so the item axis is settled by the tag match alone; (2) pins the resp axis\n",
    "(raw -3..3 = printed anchor values, +4 applied, direction not flipped) cell for cell in both waves.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
