# verify_ravenscroft_2017_transition.R
#
# CLAIM UNDER TEST (two axes):
#   (1) item <-> item_text.  The 25 IRW item codes are the raw S2 CSV's own column
#       headers (data/ravenscroft_2017_transition.py melts them verbatim), but the
#       administered WORDING lives in the S1 File questionnaire, which carries no
#       codes.  The claim is that the S2 columns align to the S1 questions in
#       order, one question per column-group.
#   (2) resp <-> option_text.  The S1 questionnaire prints every item's options
#       positive-pole-first; the claim is that the stored 1-5 coding runs the
#       OTHER way, i.e. resp 5 = the first-printed (positive/high) option.
#
# Both are derived here from scratch and compared to the shipped CSV.  Nothing
# below re-checks item counts -- validate_items.R already did that.

suppressMessages({library(xml2); library(irw)})

TABLE <- "ravenscroft_2017_transition"
S1 <- "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0179904.s001&type=supplementary"
S2 <- "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0179904.s002&type=supplementary"

cache <- file.path("itemtext/.cache", TABLE)
if (!dir.exists(cache)) cache <- file.path(".cache", TABLE)
if (!dir.exists(cache)) cache <- tempfile(); dir.create(cache, recursive = TRUE, showWarnings = FALSE)
docx <- file.path(cache, "S1_questionnaire.docx"); csvf <- file.path(cache, "S2_data.csv")
if (!file.exists(docx)) download.file(S1, docx, quiet = TRUE, mode = "wb")
if (!file.exists(csvf)) download.file(S2, csvf, quiet = TRUE, mode = "wb")

## ---- parse S1: ilvl 0 paragraphs are question stems, ilvl 1 are its options ----
ex <- file.path(cache, "docx_x"); unzip(docx, exdir = ex, overwrite = TRUE)
doc <- read_xml(file.path(ex, "word", "document.xml"))
ns  <- xml_ns(doc)
qs <- list()
for (p in xml_find_all(doc, ".//w:p", ns)) {
    txt <- paste(xml_text(xml_find_all(p, ".//w:t", ns)), collapse = "")
    txt <- trimws(txt); if (!nzchar(txt)) next
    il <- xml_find_first(p, "./w:pPr/w:numPr/w:ilvl", ns)
    if (inherits(il, "xml_missing")) next
    lvl <- as.integer(xml_attr(il, "val"))
    if (identical(lvl, 0L)) qs[[length(qs) + 1L]] <- list(stem = txt, opts = character(0))
    else if (identical(lvl, 1L) && length(qs))
        qs[[length(qs)]]$opts <- c(qs[[length(qs)]]$opts, txt)
}
cat(sprintf("S1 questionnaire parsed: %d questions\n", length(qs)))

## ---- collapse S2 columns into question slots -------------------------------
raw <- read.csv(csvf, check.names = FALSE, stringsAsFactors = FALSE)
cn  <- names(raw)
pref <- ifelse(grepl("/", cn, fixed = TRUE), sub("/.*$", "", cn), cn)
grp  <- cumsum(c(TRUE, pref[-1] != pref[-length(pref)]))
slots <- tapply(cn, grp, function(x) x[1])
slots <- as.character(slots)
slots <- sub("/.*$", "", slots)
# RespondentID and Language are survey metadata, not questions
slots <- slots[!slots %in% c("RespondentID", "Language")]
cat(sprintf("S2 collapsed to %d question slots; S1 has %d questions (last is free text, absent from CSV)\n",
            length(slots), length(qs)))
stopifnot(length(slots) == length(qs) - 1L)   # forced 1:1, order-preserving

## ---- anchors: slots whose stored VALUES are verbatim S1 option strings ------
# These are interleaved among the ordinal items and are what makes the
# arithmetic alignment above evidence rather than assumption.
anchor_slots <- c("Professional assessment done", "Attendance at transition meetings",
                  "Respondant gender", "Country", "Child age", "Child gender")
cat("\n-- anchor check: stored labels vs the S1 option list at the aligned position --\n")
ok_anchor <- TRUE
for (s in anchor_slots) {
    qi <- match(s, slots)
    vals <- unique(na.omit(raw[[grep(paste0("^", s), cn, fixed = FALSE)[1]]]))
    vals <- vals[nzchar(as.character(vals))]
    hit <- sum(tolower(vals) %in% tolower(qs[[qi]]$opts))
    cat(sprintf("  %-34s -> Q%-3d %-58s %d/%d labels verbatim\n",
                s, qi, substr(qs[[qi]]$stem, 1, 56), hit, length(vals)))
    if (hit < 2) ok_anchor <- FALSE
}

## ---- skip-pattern check ----------------------------------------------------
# S1 Q7 reads "...(if no/NA - survey will jump to Q10)", so the Q9 column must be
# populated only for respondents who answered Yes to Q7.  This pins Q9's slot
# independently of the counting argument.
q7 <- raw[["Professional assessment done"]]
q9 <- suppressWarnings(as.numeric(raw[["Support plan developed by professionals"]]))
tab <- tapply(!is.na(q9), q7, sum)
cat("\n-- Q7 skip pattern: n non-missing on 'Support plan developed by professionals' --\n")
print(tab)
ok_skip <- isTRUE(tab[["Yes"]] > 150) && all(unlist(tab[names(tab) != "Yes"]) == 0)
cat(sprintf("  S1 Q7 says the survey jumps past Q9 unless the answer is Yes: %s\n",
            if (ok_skip) "matches" else "DOES NOT MATCH"))

## ---- (1) derived item<->stem mapping vs shipped -----------------------------
cand <- c(file.path("itemtables/batch_153", paste0(TABLE, "__items.csv")),
          file.path("itemtext/itemtables/batch_153", paste0(TABLE, "__items.csv")),
          paste0(TABLE, "__items.csv"))
f <- cand[file.exists(cand)][1]
sa <- commandArgs(FALSE); sa <- sub("^--file=", "", grep("^--file=", sa, value = TRUE))
if (is.na(f) && length(sa)) f <- file.path(dirname(sa[1]), paste0(TABLE, "__items.csv"))
it <- read.csv(f, stringsAsFactors = FALSE, encoding = "UTF-8")
cat(sprintf("\nshipped file: %s\n", f))

items <- unique(it$item)
cat("\n-- item_text vs the S1 stem at the derived slot --\n")
ok_text <- TRUE; ok_opts <- TRUE
for (i in items) {
    qi <- match(i, slots)
    stem <- if (is.na(qi)) NA_character_ else qs[[qi]]$stem
    got  <- unique(it$item_text[it$item == i])
    same <- !is.na(qi) && identical(trimws(got), trimws(stem))
    # options: shipped resp 5..1 must be the S1 list in printed order 1..5
    sub_ <- it[it$item == i, ]; sub_ <- sub_[order(-sub_$resp), ]
    same_o <- !is.na(qi) && identical(trimws(sub_$option_text), trimws(qs[[qi]]$opts))
    if (!same) ok_text <- FALSE
    if (!same_o) ok_opts <- FALSE
    cat(sprintf("  %-50s Q%-3d stem:%-5s opts(5..1 = printed 1..5):%s\n",
                i, qi, same, same_o))
}
cat(sprintf("all 25 item_text verbatim at derived slot: %s ; all option lists verbatim & reversed: %s\n",
            ok_text, ok_opts))

## ---- (2) direction of the 1-5 coding ---------------------------------------
# The S1 option lists all print the positive/high pole FIRST.  If resp 5 were the
# last-printed option instead, every contrast below would flip sign.
num <- function(x) suppressWarnings(as.numeric(raw[[x]]))
att <- raw[["Attendance at transition meetings"]]
kp  <- raw[["Key person coordinated transition"]]
cat("\n-- direction: mean of each item by an unambiguous external indicator --\n")
cat(sprintf("%-50s %8s %8s %8s %8s\n", "item", "meet:Y", "meet:N", "keyp:Y", "keyp:N"))
diffs <- c()
for (i in items) {
    v <- num(i)
    a <- c(mean(v[att == "Yes"], na.rm = TRUE), mean(v[att == "No"], na.rm = TRUE),
           mean(v[kp  == "Yes"], na.rm = TRUE), mean(v[kp  == "No"], na.rm = TRUE))
    diffs <- c(diffs, a[1] - a[2], a[3] - a[4])
    cat(sprintf("%-50s %8.2f %8.2f %8.2f %8.2f\n", i, a[1], a[2], a[3], a[4]))
}
pos <- mean(diffs > 0, na.rm = TRUE)
cat(sprintf("\n%.0f%% of the 50 contrasts are positive (mean difference %+.2f).\n",
            100 * pos, mean(diffs, na.rm = TRUE)))
cat("Parents who attended transition meetings, and whose transition had a named\n",
    "coordinator, must score HIGHER on involvement/satisfaction/teamwork.  They do,\n",
    "so the high numeric code is the positive pole = the FIRST-printed option.\n", sep = "")
ok_dir <- pos >= 0.9

# corroboration: Q4 'Information Tranfer' is stored 1-3 for a Yes/No/I-don't-know
# list printed Yes-first.  Under the same reversal, 3 = Yes.
inf <- num("Information Tranfer"); si <- num("Satisfaction with info")
m <- tapply(si, inf, mean, na.rm = TRUE)
cat(sprintf("\nQ4 'Information Tranfer' (printed Yes / No / I don't know), mean 'Satisfaction with info':\n"))
print(round(m, 2))
ok_inf <- m[["3"]] > max(m[["1"]], m[["2"]]) + 0.3
cat(sprintf("  code 3 is the satisfied group -> 3 = 'Yes' = first-printed: %s\n", ok_inf))

## ---- tie the raw file to the live IRW table (server-side, no export) -------
s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- as.data.frame(s$per_item)
live_n <- setNames(pi$n, pi$item)
raw_n  <- sapply(items, function(i) { v <- num(i); sum(!is.na(v) & v >= 1 & v <= 5) })
cat("\n-- per-item n: live IRW vs the S2 columns this mapping was derived from --\n")
cat(sprintf("%-50s %8s %8s\n", "item", "live", "S2"))
for (i in items) cat(sprintf("%-50s %8d %8d\n", i, as.integer(live_n[[i]]), raw_n[[i]]))
ok_n <- all(sapply(items, function(i) as.integer(live_n[[i]]) == raw_n[[i]]))
cat(sprintf("all %d per-item n reproduce: %s\n", length(items), ok_n))

cat("\nWhat this does NOT establish: the S1 questionnaire is the ENGLISH master.\n",
    "149 of 306 respondents answered a Bulgarian, Catalan, Greek or Romanian\n",
    "translation that the deposit does not publish; those wordings are unverified.\n", sep = "")

cat(if (ok_anchor && ok_skip && ok_text && ok_opts && ok_dir && ok_inf && ok_n)
    "VERDICT: PASS\n" else "VERDICT: FAIL\n")
