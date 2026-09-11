# verify_rr98_accuracy.R -- Step 5b evidence, re-runnable.
#
# CLAIM. `item` in rr98_accuracy is `paste("i", strength)` (data/rr98.R), where
# `strength` is the rtdists::rr98 stimulus-strength variable: "33 equally spaced
# proportions [of white to black pixels] from zero (all 1,024 pixels were black)
# to 1 (all 1,024 pixels were white), with 0 darkest and 32 lightest" (rr98.Rd).
# So the shipped item_text for "i k" must describe strength level k.
#
# ROUTE. Re-run the processing script over the raw source (core model section 3,
# "script-generated code -> re-run the script"): download rtdists from CRAN, load
# rr98.rda, apply data/rr98.R's transform, and compare per-item n and per-item
# mean(resp) against live irw_fetch(). A permutation of item_text over items is
# only invisible here if two items share BOTH n and mean; the script prints how
# many of the 33 per-item means are distinct.
#
# Secondary, content-side check: accuracy must be a U-shaped function of |k-16|,
# i.e. near-chance at the middle strengths and near-ceiling at the extremes. That
# is what makes "strength 0 = all pixels black" the right reading rather than an
# arbitrary integer label.
#
# Offline note: needs CRAN (~1MB) and Redivis. rr98_accuracy is 12,205 rows, so
# the irw_fetch() export here is ~0.5MB against the 200GB cap.

suppressMessages(library(irw))
TABLE <- "rr98_accuracy"

cache <- file.path(tempdir(), "rtdists")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
tgz <- file.path(cache, "rtdists.tar.gz")
if (!file.exists(file.path(cache, "rtdists", "data", "rr98.rda"))) {
    utils::download.file("https://cran.r-project.org/src/contrib/rtdists_0.12-0.tar.gz",
                         tgz, quiet = TRUE)
    utils::untar(tgz, exdir = cache)
}
load(file.path(cache, "rtdists", "data", "rr98.rda"))   # -> rr98

# --- data/rr98.R, verbatim in effect ---------------------------------------
x <- rr98
x$resp <- ifelse(x$correct, 1, 0)
x$item <- paste("i", x$strength)
raw <- split(x, x$instruction)$accuracy
# ---------------------------------------------------------------------------

d <- irw::irw_fetch(TABLE)

agg <- function(df) {
    a <- aggregate(resp ~ item, df, function(z) c(length(z), mean(z)))
    data.frame(item = a$item, n = a$resp[, 1], m = a$resp[, 2],
               stringsAsFactors = FALSE)
}
L <- agg(d); R <- agg(raw)
mg <- merge(L, R, by = "item", suffixes = c("_live", "_raw"))
mg$k <- as.integer(sub("^i ", "", mg$item))
mg <- mg[order(mg$k), ]

cat(sprintf("live rows %d | reproduced rows %d\n", nrow(d), nrow(raw)))
cat(sprintf("%-6s %8s %8s %10s %10s\n", "item", "n_live", "n_raw", "acc_live", "acc_raw"))
for (i in seq_len(nrow(mg)))
    cat(sprintf("%-6s %8d %8d %10.4f %10.4f\n", mg$item[i], mg$n_live[i],
                mg$n_raw[i], mg$m_live[i], mg$m_raw[i]))

dn <- max(abs(mg$n_live - mg$n_raw))
dm <- max(abs(mg$m_live - mg$m_raw))
distinct_m <- length(unique(round(mg$m_live, 8)))
cat(sprintf("\nmax |n diff| = %d ; max |mean diff| = %.2e\n", dn, dm))
cat(sprintf("distinct per-item accuracies: %d of %d (each item separable from every other)\n",
            distinct_m, nrow(mg)))

# U-shape: accuracy vs distance from the midpoint strength (16).
mg$dist <- abs(mg$k - 16)
rho <- suppressWarnings(cor(mg$dist, mg$m_live, method = "spearman"))
cat(sprintf("Spearman(|k-16|, accuracy) = %+.3f ; acc at k=15,16,17 = %.2f/%.2f/%.2f ; k=0 = %.2f ; k=32 = %.2f\n",
            rho, mg$m_live[mg$k == 15], mg$m_live[mg$k == 16], mg$m_live[mg$k == 17],
            mg$m_live[mg$k == 0], mg$m_live[mg$k == 32]))

cat("Note: this establishes that item 'i k' IS strength level k, exactly, for all\n",
    "33 items. It does not independently confirm the numeric proportion k/32 printed\n",
    "in item_text -- that is arithmetic on rr98.Rd's '33 equally spaced proportions\n",
    "from zero to 1', not a quantity measurable in the response data.\n", sep = "")

ok <- (nrow(d) == nrow(raw)) && dn == 0 && dm < 1e-12 &&
      distinct_m == nrow(mg) && rho > 0.9
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
