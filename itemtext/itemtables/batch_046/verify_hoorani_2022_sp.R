# verify_hoorani_2022_sp.R -- Step 5b, route 9 (response-frequency matching).
#
# CLAIM UNDER TEST: each IRW item code SP1..SP4 carries the item text of the
# identically named variable in the study's Stata deposit (S2 File), and the
# integer resp 1..5 encodes "Strongly disagree".."Strongly agree" in that order
# (data/hoorani_2022_young_lives_battery.py's MAP_AGREE5).
#
# FALSIFIABLE PREDICTION: for every item, the count of each raw label in the .dta
# must equal the count of the corresponding integer in the live IRW table. The
# four items' count vectors are mutually distinct, so a swap of any two items --
# or any permutation/reversal of the five levels -- breaks the match.
#
# This verifies the MAPPING (both axes), not the item/resp sets, which
# validate_items.R already checked.

suppressMessages(library(irw))

TABLE  <- "hoorani_2022_sp"
ITEMS  <- c("SP1", "SP2", "SP3", "SP4")
LEVELS <- c("Strongly disagree", "Disagree", "More or less", "Agree", "Strongly agree")
SI_URL <- paste0("https://journals.plos.org/plosone/article/file",
                 "?type=supplementary&id=10.1371/journal.pone.0271374.s016")

## ---- source side: label counts per item from the .dta -------------------
dta <- tempfile(fileext = ".dta")
utils::download.file(SI_URL, dta, quiet = TRUE, mode = "wb")
raw <- haven::read_dta(dta)

src <- sapply(ITEMS, function(it) {
    v <- haven::as_factor(raw[[it]])
    v <- as.character(v[!is.na(v)])
    sapply(LEVELS, function(l) sum(v == l))
})

## ---- live side: resp counts per item, one server-side GROUP BY ----------
s <- irw::irw_table_sets(TABLE, source = "core", per_item = FALSE)
sql <- sprintf(paste("SELECT CAST(item AS STRING) AS item,",
                     "SAFE_CAST(TRIM(CAST(resp AS STRING)) AS FLOAT64) AS resp,",
                     "COUNT(*) AS n FROM `%s` GROUP BY 1,2"), s$table)
d <- suppressWarnings(redivis::redivis$query(sql)$to_tibble())

live <- sapply(ITEMS, function(it) {
    sapply(1:5, function(k) {
        n <- d$n[as.character(d$item) == it & !is.na(d$resp) & d$resp == k]
        if (length(n) == 0) 0L else as.integer(n)
    })
})
rownames(live) <- LEVELS

cat(sprintf("%-18s %s\n", "level (resp)",
            paste(sprintf("%-16s", paste0(ITEMS, " src/live")), collapse = "")))
for (i in seq_along(LEVELS))
    cat(sprintf("%-13s (%d) %s\n", LEVELS[i], i,
                paste(sprintf("%-16s", paste0(src[i, ], "/", live[i, ])), collapse = "")))

ok <- all(src == live)
cat(sprintf("\nall %d item x level cells match: %s\n", length(src), ok))

# Are the item count-vectors mutually distinct? If not, a swap would be invisible.
distinct <- length(unique(apply(src, 2, paste, collapse = "-"))) == length(ITEMS)
cat("item count-vectors mutually distinct (so a swap would be detected):", distinct, "\n")

cat("Note: this pins item<->text and resp<->option_text via the .dta, whose variable\n",
    "labels supply the wording. It does not establish the administered language or\n",
    "any instruction text, neither of which the deposit or the paper contains.\n", sep = "")

cat(if (ok && distinct) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
