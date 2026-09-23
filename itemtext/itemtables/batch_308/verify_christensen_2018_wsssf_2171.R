# verify_christensen_2018_wsssf_2171.R -- Step 5b, re-runnable mapping evidence.
#
# THE CLAIM BEING TESTED
#   The shipped item_text for code <pfx><nn> is the nn-th item of the matching
#   scale in Appendix A of Winterstein, Silvia, Kwapil, Kelley, Cubbage & Barona
#   (2011), "Brief assessment of schizotypy: Developing short forms of the
#   Wisconsin Schizotypy Scales", Pers Individ Dif 51, 920-924.
#
#   Nothing in the deposit labels an item. The tie is built in two moves, and
#   this script re-runs both:
#
#   (A) WHICH ORIGINAL ITEM each short-form column is. WSS-SF_2171.csv (the file
#       the IRW table is melted from, column names used verbatim as `item`) has a
#       twin file, share_2171n_WSS-SF.csv, holding the FULL-LENGTH Chapman scales
#       for the same 2,171 people in the same row order. Every short-form column
#       is a verbatim copy of exactly one full-length column, so matching on
#       values recovers each short-form item's original item number. Those 60
#       numbers are then compared against the four lists the paper prints in
#       prose ("items 1, 2, 5, 6, 9, ..."). If the appendix and the data
#       disagreed about which items the short forms contain, this fails.
#
#   (B) THE ORDER WITHIN each scale. (A) only fixes the SET. The .sav's value
#       labels say, per full-length item, which literal answer ("True"/"False")
#       is stored as 1 -- i.e. the keyed/deviant direction. Each appendix item's
#       keyed direction is readable from its wording, and is hard-coded below
#       from that reading. Comparing the two is a 60-bit signature that any
#       reordering of the appendix text would have to survive.
#
# WHAT THIS DOES NOT ESTABLISH -- read before trusting the status.
#   The signature in (B) is not injective. Within one scale, items sharing a
#   keyed direction are interchangeable as far as it can see: the Perceptual
#   Aberration short form is keyed True on all 15 items, so it contributes no
#   discrimination at all, Magical Ideation pins only its single False-keyed
#   item, Social Anhedonia splits 9/6 and Physical Anhedonia 4/11. So the
#   verification pins each item to a scale and to a keying class, plus the
#   assumption that Appendix A prints each scale in ascending original-item-number
#   order (which (A) shows the DATA columns follow). It does NOT independently
#   separate two same-scale, same-keying items from each other. PARTIAL.
#
# Data are pulled from the study's OSF node, not from Redivis: the IRW table is a
# verbatim melt of WSS-SF_2171.csv with the column name carried through as `item`,
# so the source file is the same values and costs no export quota.

CACHE <- file.path("..", "..", ".cache", "christensen_2018_wsssf_2171")
if (!dir.exists(CACHE)) CACHE <- tempfile(); dir.create(CACHE, showWarnings = FALSE, recursive = TRUE)
get <- function(osf, name) {
    p <- file.path(CACHE, name)
    if (!file.exists(p))
        utils::download.file(sprintf("https://osf.io/download/%s/", osf), p, quiet = TRUE)
    p
}
sf_path  <- get("xg3hs", "WSS-SF_2171.csv")
co_path  <- get("r2xdf", "share_2171n_WSS-SF.csv")
sav_path <- get("27s93", "share_2171n_WSS-SF.sav")

ITEMS <- read.csv(file.path(dirname(sub("^--file=", "", commandArgs(FALSE)[grep("^--file=", commandArgs(FALSE))][1])),
                            "christensen_2018_wsssf_2171__items.csv"))

sf <- read.csv(sf_path, check.names = FALSE)
co <- read.csv(co_path, fileEncoding = "UTF-8-BOM", check.names = FALSE)
names(co) <- tolower(names(co))

LONG <- c(py = "ph", pb = "bi", mi = "mi", sa = "sa")

# ---- (A) short-form column -> full-length column, by exact value identity ----
map <- character(0)
for (col in names(sf)) {
    pfx <- LONG[[substr(col, 1, 2)]]
    cand <- grep(sprintf("^%s[0-9]+$", pfx), names(co), value = TRUE)
    hit <- cand[vapply(cand, function(c2) all(co[[c2]] == sf[[col]]), logical(1))]
    if (length(hit) != 1L) stop(sprintf("%s matched %d full-length columns", col, length(hit)))
    map[col] <- hit
}
orig_num <- function(pfx) {
    cols <- sprintf("%s%02d", pfx, 1:15)
    as.integer(sub("^[a-z]+", "", map[cols]))
}

# Winterstein et al. (2011), p.921: the original item numbers making up each short form.
PUBLISHED <- list(
    mi = c(1, 2, 5, 6, 9, 12, 13, 21, 22, 23, 24, 25, 26, 27, 29),
    pb = c(8, 10, 11, 13, 16, 19, 21, 23, 24, 25, 26, 27, 29, 30, 31),
    sa = c(1, 3, 4, 7, 10, 13, 14, 17, 19, 21, 26, 30, 31, 35, 37),
    py = c(3, 10, 15, 19, 24, 29, 35, 36, 39, 42, 45, 46, 47, 54, 60))
SCALE <- c(mi = "Magical Ideation", pb = "Perceptual Aberration",
           sa = "Revised Social Anhedonia", py = "Physical Anhedonia")

cat("=== (A) original item numbers: data-derived vs the paper's printed list ===\n")
okA <- TRUE
for (p in names(PUBLISHED)) {
    got <- orig_num(p)
    same <- identical(got, as.integer(PUBLISHED[[p]]))
    okA <- okA && same
    cat(sprintf("%-26s paper: %s\n%-26s data : %s   -> %s\n",
                SCALE[[p]], paste(PUBLISHED[[p]], collapse = ","),
                "", paste(got, collapse = ","), if (same) "MATCH" else "MISMATCH"))
}

# ---- (B) keyed direction: .sav value labels vs the appendix wording ----
# Hard-coded from READING each shipped appendix item: the literal answer that
# indicates the trait. e.g. MI item 11 "Numbers like 13 and 7 have no special
# powers." is the scale's only False-keyed short-form item.
EXPECT <- list(
    mi = c("True","True","True","True","True","True","True","True","True","True",
           "False","True","True","True","True"),
    pb = rep("True", 15),
    sa = c("True","True","True","False","True","True","True","True","False","True",
           "False","False","False","False","True"),
    py = c("False","False","False","False","True","True","False","True","False","True",
           "False","False","False","False","False"))

sav <- haven::read_sav(sav_path, n_max = 1)
keyed <- function(fullcol) {
    lv <- attr(sav[[fullcol]], "labels")
    names(lv)[lv == 1]
}

cat("\n=== (B) keyed direction per item: appendix wording vs the .sav value label ===\n")
cat(sprintf("%-6s %-8s %-14s %-14s %-6s  %s\n",
            "item", "fullcol", "expected(text)", "observed(.sav)", "ok", "item_text (first 58 ch)"))
okB <- TRUE; nB <- 0; agreeB <- 0
for (p in names(EXPECT)) for (i in 1:15) {
    code <- sprintf("%s%02d", p, i)
    exp_k <- EXPECT[[p]][i]
    obs_k <- keyed(map[[code]])
    # and the shipped file must label resp==1 with that same literal answer
    ship <- unique(ITEMS$option_text[ITEMS$item == code & ITEMS$resp == 1])
    good <- identical(exp_k, obs_k) && identical(ship, obs_k)
    okB <- okB && good; nB <- nB + 1; agreeB <- agreeB + good
    txt <- unique(ITEMS$item_text[ITEMS$item == code])
    cat(sprintf("%-6s %-8s %-14s %-14s %-6s  %s\n", code, map[[code]], exp_k, obs_k,
                if (good) "ok" else "FAIL", substr(txt, 1, 58)))
}

cat(sprintf("\n(A) 60/60 original item numbers reproduce the paper's four lists: %s\n",
            if (okA) "yes" else "NO"))
cat(sprintf("(B) %d/%d items agree on keyed direction across appendix wording, .sav value label and shipped option_text\n",
            agreeB, nB))
cat("Discrimination actually supplied by (B): pb 0/15 (all True-keyed), mi 1 of 15 pinned,\n",
    "sa 9 True / 6 False, py 4 True / 11 False. Within-class order rests on Appendix A\n",
    "being printed in ascending original-item-number order, which (A) shows the data follow.\n", sep = "")

cat(if (okA && okB) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
