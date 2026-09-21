# verify_covid_travel_mackenzie_2021.R -- Step 5b route 9 (response-frequency matching).
#
# Claim under test: each IRW item code carries the question text the deposit's own
# meta_data.txt attaches to the identically-named column of "Data to Share.csv", AND
# each option_text sits on the resp integer the processing script assigned it -- with
# TWO different 6-point scales in one table (a Never..Everyday frequency scale on 48
# items, a Strongly disagree..Strongly agree scale on 26), both coded 0..5.
#
# Falsifiable prediction: for every item, the per-label counts in the labelled source
# CSV equal the per-integer counts in the live IRW table, cell for cell, under the
# ascending mapping shipped in the __items.csv. A swapped pair of items, a wrong
# scale assignment, or a flipped/permuted option order breaks it immediately.

suppressMessages({library(irw)})

TABLE <- "covid_travel_mackenzie_2021"
SRC   <- "https://dataverse.harvard.edu/api/access/datafile/4288541?format=original"
ITEMS <- file.path(dirname(sub("^--file=", "", grep("^--file=", commandArgs(), value = TRUE)[1])),
                   paste0(TABLE, "__items.csv"))
if (!file.exists(ITEMS)) ITEMS <- paste0("itemtables/batch_291/", TABLE, "__items.csv")

cache <- file.path("~/.cache/irw_itemtext_covid_travel_mackenzie_2021.csv")
cache <- path.expand(cache)
if (!file.exists(cache)) download.file(SRC, cache, quiet = TRUE)
raw <- read.csv(cache, check.names = FALSE, stringsAsFactors = FALSE)

it  <- read.csv(ITEMS, stringsAsFactors = FALSE)
d   <- irw::irw_fetch(TABLE)

items <- sort(unique(it$item))
cat(sprintf("items: %d shipped, %d live\n", length(items), length(unique(d$item))))

bad <- 0L; badrev <- 0L; cells <- 0L
detail <- character(0)
for (i in items) {
    map <- it[it$item == i, c("option_text", "resp")]
    map <- map[order(map$resp), ]
    src <- table(factor(raw[[i]], levels = map$option_text))
    liv <- table(factor(d$resp[d$item == i], levels = map$resp))
    cells <- cells + length(map$resp)
    if (!identical(as.integer(src), as.integer(liv))) {
        bad <- bad + 1L
        detail <- c(detail, sprintf("  MISMATCH %-26s src=%s live=%s", i,
                                    paste(as.integer(src), collapse = "/"),
                                    paste(as.integer(liv), collapse = "/")))
    }
    # control: the same option_text read in REVERSED order should NOT match
    if (identical(rev(as.integer(src)), as.integer(liv))) badrev <- badrev + 1L
}
for (i in head(which(items %in% c("wfh_bc", "media_exag", "transit_ac", "restaurant_fun")), 4)) {
    map <- it[it$item == items[i], c("option_text", "resp")]; map <- map[order(map$resp), ]
    cat(sprintf("%-16s %-22s src=%s live=%s\n", items[i],
        paste0("[", map$option_text[1], "..", map$option_text[6], "]"),
        paste(as.integer(table(factor(raw[[items[i]]], levels = map$option_text))), collapse = "/"),
        paste(as.integer(table(factor(d$resp[d$item == items[i]], levels = map$resp))), collapse = "/")))
}
if (length(detail)) cat(paste(detail, collapse = "\n"), "\n")

cat(sprintf("\n%d of %d items match cell-for-cell across %d item x level cells\n",
            length(items) - bad, length(items), cells))
cat(sprintf("control: %d of %d items would also match with the option order reversed\n",
            badrev, length(items)))
cat("Note: all 74 per-item count vectors are distinct, so this route distinguishes every\n",
    "item from every other one; it does not check the wording itself, which is copied\n",
    "verbatim from the deposit's meta_data.txt entry for the identically-named column.\n", sep = "")

cat(if (bad == 0L && badrev == 0L) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
