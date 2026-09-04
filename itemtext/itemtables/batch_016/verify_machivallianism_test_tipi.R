# verify_machivallianism_test_tipi.R
#
# CLAIM UNDER TEST: each IRW item code TIPI1..TIPI10 carries the trait pair the
# OpenPsychometrics MACH_data codebook assigns to the source column of the same
# name (TIPI1 = "Extraverted, enthusiastic.", ... TIPI10 = "Conventional,
# uncreative.").
#
# ROUTE: per-item n fingerprint (a re-run of the processing script's own filter)
# plus keying polarity. data/machivallianism_test.R pivots the raw deposit's
# TIPI1..TIPI10 columns by NAME and drops resp == 0, so each live item's row
# count is predicted exactly by the count of non-zero values in the deposit
# column of that name. The ten counts are all DISTINCT, so the prediction is a
# per-item fingerprint: any permutation of the ten codes would break at least
# two of the ten comparisons. Route 6 (keying polarity) is printed as a
# secondary, content-side check.
#
# QUOTA: uses irw::irw_table_sets() (server-side GROUP BY), never irw_fetch(),
# which would export all 728,729 rows.

suppressMessages(library(irw))

TABLE <- "machivallianism_test_tipi"
CACHE <- file.path("..", "..", ".cache", TABLE)   # run from itemtables/batch_016/
if (!dir.exists(CACHE)) CACHE <- tempdir()
ZIP  <- file.path(CACHE, "MACH_data.zip")
CSV  <- file.path(CACHE, "MACH_data", "MACH_data", "data.csv")

if (!file.exists(CSV)) {
    if (!file.exists(ZIP))
        download.file("https://openpsychometrics.org/_rawdata/MACH_data.zip",
                      ZIP, mode = "wb", quiet = TRUE)
    unzip(ZIP, exdir = file.path(CACHE, "MACH_data"))
}

# Codebook (MACH_data/codebook.txt) trait labels, verbatim.
TRAITS <- c("Extraverted, enthusiastic.", "Critical, quarrelsome.",
            "Dependable, self-disciplined.", "Anxious, easily upset.",
            "Open to new experiences, complex.", "Reserved, quiet.",
            "Sympathetic, warm.", "Disorganized, careless.",
            "Calm, emotionally stable.", "Conventional, uncreative.")
names(TRAITS) <- paste0("TIPI", 1:10)

raw <- read.delim(CSV, stringsAsFactors = FALSE)
cols <- names(TRAITS)
# data/machivallianism_test.R: filter(resp != 0)
pred <- sapply(cols, function(c) sum(raw[[c]] != 0, na.rm = TRUE))

s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- as.data.frame(s$per_item)
live <- setNames(as.numeric(pi$n), as.character(pi$item))[cols]

cat(sprintf("%-7s %-34s %12s %12s %8s\n",
            "item", "codebook trait pair", "deposit n", "live n", "diff"))
for (i in cols)
    cat(sprintf("%-7s %-34s %12d %12d %8d\n",
                i, TRAITS[[i]], pred[[i]], live[[i]], live[[i]] - pred[[i]]))

n_match  <- all(pred == live)
distinct <- length(unique(pred)) == length(pred)
cat(sprintf("\nall ten counts match exactly: %s\n", n_match))
cat(sprintf("all ten counts mutually distinct (so the match is a per-item fingerprint,\n  not a coincidence of equal columns): %s\n", distinct))

# Secondary: route 6, keying polarity. TIPI pairs one straight and one
# reverse-worded adjective set per Big Five domain; each pair must correlate
# NEGATIVELY in raw (un-reversed) data.
tp <- raw[, cols]; tp[tp == 0] <- NA
cm <- cor(tp, use = "pairwise.complete.obs")
prs <- list(c(1,6,"Extraversion"), c(2,7,"Agreeableness"), c(3,8,"Conscientiousness"),
            c(4,9,"Emotional stability"), c(5,10,"Openness"))
cat("\nkeying polarity (raw data; each canonical pair must be negative):\n")
pol <- sapply(prs, function(p) {
    a <- as.integer(p[1]); b <- as.integer(p[2])
    r <- cm[a, b]
    cat(sprintf("  %-20s TIPI%-2d x TIPI%-2d r = %+0.3f\n", p[3], a, b, r))
    r
})
cat(sprintf("all five canonical pairs negative: %s\n", all(pol < 0)))

cat("\nWhat this does NOT establish: it does not check the wording of the shipped\n",
    "anchors against anything but the codebook's own list, and it cannot detect an\n",
    "error already present in the deposit's codebook itself.\n", sep = "")

cat(if (n_match && distinct && all(pol < 0)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
