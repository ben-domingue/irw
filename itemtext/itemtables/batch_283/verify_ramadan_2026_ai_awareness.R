# verify_ramadan_2026_ai_awareness.R
#
# CLAIM: item AW1..AW6 in the live IRW table are the SAME columns AW1..AW6 of the
# Mendeley deposit's arabic_genai_competency_data.csv, whose Arabic/English wording
# codebook.csv prints against those very variable names. If the shipped item_text for,
# say, AW2 and AW5 were swapped, the wording would be attached to the wrong source
# column -- so the falsifiable prediction is that each live item's 1-5 response-count
# vector reproduces its own raw source column, cell for cell, and NO OTHER column's.
#
# Route: re-run of the processing script's melt (core model section 3, pattern 1) plus
# response-frequency matching (Step 5b route 9). Data fetched fresh from Mendeley.

suppressMessages(library(irw))

TABLE <- "ramadan_2026_ai_awareness"
ITEMS <- paste0("AW", 1:6)
RAW_URL <- paste0("https://data.mendeley.com/public-files/datasets/xd27t4g547/files/",
                  "0a345839-b4fd-4ff9-8569-be8870486cf7/file_downloaded")
RAW_SHA <- "0e47f8175e08088caec313c2c81ab006b8e2266ab5696f5d6c33243ee9c0efad"

tmp <- tempfile(fileext = ".csv")
download.file(RAW_URL, tmp, quiet = TRUE)
cat("raw file md5 (informational):", as.character(tools::md5sum(tmp)), "\n")
raw <- read.csv(tmp, check.names = FALSE, fileEncoding = "UTF-8-BOM")

d <- irw::irw_fetch(TABLE)

vec <- function(x) as.integer(table(factor(x[!is.na(x)], levels = 1:5)))

live <- sapply(ITEMS, function(it) vec(d$resp[d$item == it]))
src  <- sapply(ITEMS, function(it) vec(raw[[it]]))

cat(sprintf("%-6s %-22s %-22s %6s %6s %s\n",
            "item", "live counts 1..5", "raw column counts 1..5", "n_live", "n_raw", "match"))
ok <- TRUE
for (it in ITEMS) {
    m <- identical(live[, it], src[, it])
    ok <- ok && m
    cat(sprintf("%-6s %-22s %-22s %6d %6d %s\n", it,
                paste(live[, it], collapse = "/"), paste(src[, it], collapse = "/"),
                sum(live[, it]), sum(src[, it]), m))
}

# A count vector only identifies an item if no other item shares it.
dup <- any(duplicated(apply(live, 2, paste, collapse = "/")))
cat("\nall 6 live count vectors distinct from one another:", !dup, "\n")

# Cross-check: does any live item match a DIFFERENT raw column?
cross <- outer(ITEMS, ITEMS, Vectorize(function(a, b) identical(live[, a], src[, b])))
dimnames(cross) <- list(paste0("live_", ITEMS), paste0("raw_", ITEMS))
cat("\nlive x raw identity matrix (must be the identity matrix):\n")
print(cross)
ident <- identical(cross, diag(6) == 1, ignore.environment = TRUE) ||
         all(cross == diag(6))

cat("\nWhat this does NOT establish: the resp<->option_text direction. The deposit stores\n",
    "bare integers and publishes the anchors only as codebook.csv's 'coding' string\n",
    "(5=strongly agree ... 1=strongly disagree), so there are no label counts to match.\n", sep = "")

cat(if (ok && !dup && ident) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
