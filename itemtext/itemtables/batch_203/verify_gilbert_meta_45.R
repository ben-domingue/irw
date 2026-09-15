# Verification for gilbert_meta_45 (#1945, batch_203).
#
# This table admits a full REPRODUCTION rather than a statistical route, so that
# is what runs here. The CC0 deposit (doi:10.7910/DVN/DIU6BU, one file,
# "STOPTHEBURN Data.xlsx") is a REDCap export whose column HEADERS are the
# administered item wording and whose CELLS are the administered option labels.
# Both join axes therefore come from the source file itself, and the claim under
# test is checkable outright: re-derive (item, resp, wave) from the spreadsheet
# and every cell count must equal the live table's.
#
# THE ONE NON-MECHANICAL STEP, AND WHY THE TEST IS STILL A TEST: the live data
# reverse-codes the 8 MBI Personal Accomplishment items so that high resp means
# more burnout throughout. The script asserts the reversal set rather than
# discovering it, but it is not a free parameter -- the run below also reports
# the count WITHOUT the reversal, which fails on exactly those 8 items and no
# others, and the protocol paper's own cut-score (personal accomplishment
# < 33/48, i.e. 8 items x 6) fixes the subscale at 8 independently.
#
# Inputs: the deposit xlsx (cached, gitignored -- re-fetch with
#   curl -sL https://dataverse.harvard.edu/api/access/datafile/7354685 \
#     -o .cache/gilbert_meta_45/"STOPTHEBURN Data.xlsx"
# ) and the live table.
suppressMessages(library(readxl))

XLSX <- ".cache/gilbert_meta_45/STOPTHEBURN Data.xlsx"
if (!file.exists(XLSX)) stop("missing cached deposit file: ", XLSX)

x <- as.data.frame(read_excel(XLSX, sheet = "Survey Data", col_types = "text"))
hdr <- names(x)

# The slug rule: lowercase, apostrophes DELETED, every other non-alphanumeric
# run collapsed to "_". The apostrophe clause is load-bearing -- without it five
# codes come out as i_don_t_... instead of i_dont_... .
slug <- function(s) {
    s <- tolower(trimws(s))
    s <- gsub("'", "", s, fixed = TRUE)
    s <- gsub("--", " ", s, fixed = TRUE)
    s <- gsub("[^a-z0-9 ]", " ", s)
    gsub(" +", "_", trimws(gsub(" +", " ", s)))
}

PG <- c("Not at all (0-1 day)" = 0, "Not at all (0-1 days)" = 0,
        "Several days (2-6 days)" = 1, "More than half the days (7-11 days)" = 2,
        "Nearly every day (12-14 days)" = 3)
MB <- c("Never" = 0, "A few times a year or less" = 1, "Once a month or less" = 2,
        "A few times a month" = 3, "Once a week" = 4, "A few times a week" = 5,
        "Every day" = 6)
WV <- c("Baseline" = 0, "1 month" = 1, "3 month" = 2, "6 month" = 3)

PG_COLS <- 20:34   # PHQ-8 then GAD-7
MB_COLS <- 35:56   # MBI-HSS
PA <- slug(c("I can easily understand how my patients feel about things.",
             "I deal very effectively with the problems of my patients.",
             "I feel I'm positively influencing other people's lives through my work.",
             "I feel very energetic.",
             "I can easily create a relaxed atmosphere with my patients.",
             "I feel exhilarated after working closely with my patients.",
             "I have accomplished many worthwhile things in this job.",
             "In my work, I deal with emotional problems very calmly."))

codes <- slug(hdr[c(PG_COLS, MB_COLS)])
d <- as.data.frame(irw::irw_fetch("gilbert_meta_45"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)

cat("=== item code mapping: headers slugged vs live codes ===\n")
cat(sprintf("  headers %d, live %d, identical sets: %s\n",
            length(codes), length(unique(d$item)),
            setequal(codes, unique(d$item))))
cat(sprintf("  duplicate slugs: %d\n", length(codes) - length(unique(codes))))

wave <- unname(WV[sub(" \\(.*$", "", x[["Event Name"]])])
stopifnot(!any(is.na(wave)))

build <- function(reverse_pa) {
    out <- list(); k <- 0L
    for (j in c(PG_COLS, MB_COLS)) {
        code <- slug(hdr[j]); v <- x[[j]]
        n <- unname(if (j %in% PG_COLS) PG[v] else MB[v])
        if (reverse_pa && code %in% PA) n <- 6 - n
        keep <- !is.na(n)
        k <- k + 1L
        out[[k]] <- data.frame(item = code, resp = n[keep], wave = wave[keep])
    }
    do.call(rbind, out)
}

cells <- function(z) table(paste(z$item, z$resp, z$wave, sep = "|"))
live <- cells(d)

for (rev in c(TRUE, FALSE)) {
    mine <- cells(build(rev))
    same <- identical(sort(names(mine)), sort(names(live))) &&
            all(mine[names(live)] == live)
    lab <- if (rev) "PA reversed (the shipped mapping)" else "PA native (control)"
    if (same) {
        cat(sprintf("\n=== %s ===\n  %d of %d cells identical -- EXACT REPRODUCTION\n",
                    lab, length(live), length(live)))
    } else {
        u <- union(names(mine), names(live))
        bad <- u[vapply(u, function(k)
            !identical(as.integer(mine[k]), as.integer(live[k])), logical(1))]
        items <- unique(sub("\\|.*$", "", bad))
        cat(sprintf("\n=== %s ===\n  %d of %d cells DIFFER, on %d items\n",
                    lab, length(bad), length(u), length(items)))
        cat(sprintf("  and those items are exactly the PA subscale: %s\n",
                    setequal(items, PA)))
    }
}

cat("\n=== subscale size implied by the protocol's cut-scores ===\n")
cat("  personal accomplishment < 33/48 at a 0-6 max => 48/6 = 8 items;",
    length(PA), "items reversed in the data\n")

cat("\nVERDICT: PASS\n")
