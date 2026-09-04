# verify_chen2025_self_esteem.R
#
# chen2025_self_esteem is BLOCKED: no item text was shipped, so there is no
# item_text <-> item mapping to verify. This script therefore verifies the
# FALSIFIABLE claim the NO_ROUTE row actually makes -- that the ten item codes
# are statistically exchangeable, so no route in Step 5b could ever order them
# even if the instrument were assumed to be the RSES.
#
# It deliberately does NOT re-check item counts (validate_items.R's job, and no
# CSV exists to check), and it does NOT touch irw_fetch: the live ground truth
# quoted here came from irw::irw_table_sets (server-side aggregate, no export).
# Everything below is computed from the SOURCE .sav on figshare.
#
# VERDICT: PASS means "the NO_ROUTE finding reproduces" -- NOT that any mapping
# was confirmed. Nothing here establishes the instrument's identity or any
# item's wording.

suppressMessages(library(haven))

SAV_URL <- "https://ndownloader.figshare.com/files/57825856"   # figshare 30093970, CC BY 4.0
CACHE   <- file.path("..", "..", ".cache", "chen2025_self_esteem", "raw.sav")

path <- if (file.exists(CACHE)) CACHE else {
  tmp <- tempfile(fileext = ".sav")
  utils::download.file(SAV_URL, tmp, quiet = TRUE, mode = "wb")
  tmp
}

d  <- haven::read_sav(path)
se <- paste0("SE", 1:10)
X  <- as.data.frame(lapply(d[se], as.numeric))

# --- 1. Level-1 source check: does the file label its own items? -------------
lab <- vapply(d[se], function(v) {
  l <- attr(v, "label"); if (is.null(l)) "" else as.character(l)
}, character(1))
vallab <- sum(vapply(d[se], function(v) length(attr(v, "labels")), integer(1)))
cat(sprintf("variable labels on SE1..SE10 : %d of 10 non-empty\n", sum(nzchar(lab))))
cat(sprintf("value labels across SE1..SE10: %d\n", vallab))

# --- 2. Are the items separable by mean / SD? (routes 1, 7, 8) ---------------
m <- colMeans(X); s <- apply(X, 2, sd)
cat("\nitem       mean     sd\n")
for (i in seq_along(se)) cat(sprintf("%-6s %8.3f %6.3f\n", se[i], m[i], s[i]))
mean_spread <- max(m) - min(m)
cat(sprintf("\nmean spread across all 10 items: %.3f (SD range %.3f-%.3f)\n",
            mean_spread, min(s), max(s)))

# --- 3. Is there a reverse-keyed block? (route 6) ---------------------------
# An RSES administration stored raw would show items 3,5,8,9,10 correlating
# NEGATIVELY with 1,2,4,6,7. If no correlation is negative, polarity cannot
# assign a single item.
C   <- cor(X)
off <- C[upper.tri(C)]
cat(sprintf("\ninter-item correlations: n=%d, range %.3f to %.3f, %d negative\n",
            length(off), min(off), max(off), sum(off < 0)))

# --- 4. Range structure (route 2) -------------------------------------------
rng <- apply(X, 2, function(v) paste0(min(v), "-", max(v)))
cat(sprintf("distinct per-item response ranges: %d (%s)\n",
            length(unique(rng)), paste(unique(rng), collapse = ", ")))

# --- The claim: every route is dead -----------------------------------------
no_labels   <- sum(nzchar(lab)) == 0 && vallab == 0
exchangeable<- mean_spread < 0.10          # observed 0.053
no_polarity <- sum(off < 0) == 0
flat_range  <- length(unique(rng)) == 1

cat("\nclaims:\n")
cat(sprintf("  source file carries no item text (level 1 empty) : %s\n", no_labels))
cat(sprintf("  item means indistinguishable (spread < 0.10)     : %s\n", exchangeable))
cat(sprintf("  no reverse-keyed block (0 negative correlations) : %s\n", no_polarity))
cat(sprintf("  response ranges flat (route 2 dead)              : %s\n", flat_range))
cat("\nThis does NOT verify any mapping -- none was shipped. It establishes only that\n",
    "no statistical route can distinguish SE1..SE10, so only a source document\n",
    "(questionnaire, codebook, or the unpublished paper) can unblock this table.\n", sep = "")

cat(if (no_labels && exchangeable && no_polarity && flat_range)
      "VERDICT: PASS\n" else "VERDICT: FAIL\n")
