# verify_hoorani_2022_epreas.R -- Step 5b, route 9 (response-frequency matching)
# plus a label-to-wording crosswalk check.
#
# CLAIM UNDER TEST: each IRW item code EPREAS1..EPREAS5 is the identically named
# variable in the study's Stata deposit (S2 File, .s016); its .dta variable label
# identifies exactly one of the five numbered 'reasons for wanting children' the
# paper prints (the wording shipped); and resp 1..5 encodes "Not important at
# all".."Very important" in that order (data/hoorani_2022_young_lives_battery.py
# MAP_IMPORTANCE, which here coincides with the .dta's own numeric codes).
#
# FALSIFIABLE PREDICTIONS: (a) for every item x level, the count of each raw label
# in the .dta equals the count of the corresponding integer in the live table
# (both waves pooled); the five items' count vectors are mutually distinct, so any
# item swap or level permutation breaks the match. (b) each .dta label shares its
# distinguishing keyword with exactly one shipped item_text, the one on the same code.
#
# Verifies the MAPPING (both axes), not the item/resp sets (validate_items.R).

suppressMessages(library(irw))

TABLE  <- "hoorani_2022_epreas"
ITEMS  <- paste0("EPREAS", 1:5)
LEVELS <- c("Not important at all", "Not very important", "Moderately important",
            "Important", "Very important")  # resp 1..5
SI_URL <- paste0("https://journals.plos.org/plosone/article/file",
                 "?type=supplementary&id=10.1371/journal.pone.0271374.s016")
# shipped item_text (paper's numbered list, items 1-5) and a keyword unique to each
SHIPPED <- c(EPREAS1 = "Because having children increases your sense of responsibility and helps you to develop.",
             EPREAS2 = "Because it is fun to have young children around the house.",
             EPREAS3 = "Because of the pleasure you get from watching your children grow.",
             EPREAS4 = "Because of the special feeling of love that develops between a parent and a child.",
             EPREAS5 = "Because raising children helps you to learn about life and yourself.")
KEYS <- c("responsibility", "fun", "pleasure", "love", "learn")

## ---- source side ----------------------------------------------------------
dta <- tempfile(fileext = ".dta")
utils::download.file(SI_URL, dta, quiet = TRUE, mode = "wb")
raw <- haven::read_dta(dta)

labs <- sapply(ITEMS, function(it) attr(raw[[it]], "label"))
hit <- sapply(KEYS, function(k) grepl(k, labs, ignore.case = TRUE))      # labels x keys
hit2 <- sapply(KEYS, function(k) grepl(k, SHIPPED, ignore.case = TRUE))  # shipped x keys
for (i in seq_along(ITEMS)) cat(sprintf("%s  label: %-62s | shipped: %s\n", ITEMS[i], labs[i], SHIPPED[i]))
cross_ok <- all(hit == diag(5)) && all(hit2 == diag(5))
cat("each keyword hits exactly one label and one shipped text, on the same code:", cross_ok, "\n")

src <- sapply(ITEMS, function(it) {
    v <- as.character(haven::as_factor(raw[[it]])); v <- v[!is.na(v)]
    sapply(LEVELS, function(l) sum(v == l))
})

## ---- live side: one server-side GROUP BY, no export ------------------------
s <- irw::irw_table_sets(TABLE, source = "core", per_item = FALSE)
sql <- sprintf(paste("SELECT CAST(item AS STRING) AS item,",
                     "SAFE_CAST(TRIM(CAST(resp AS STRING)) AS FLOAT64) AS resp,",
                     "COUNT(*) AS n FROM `%s` GROUP BY 1,2"), s$table)
d <- suppressWarnings(redivis::redivis$query(sql)$to_tibble())
live <- sapply(ITEMS, function(it) sapply(1:5, function(k) {
    n <- d$n[as.character(d$item) == it & !is.na(d$resp) & d$resp == k]
    if (length(n) == 0) 0L else as.integer(sum(n))
}))
rownames(live) <- LEVELS

cat("\nlevel (resp)             ", paste(sprintf("%-16s", paste0(ITEMS, " src/live")), collapse = ""), "\n")
for (i in seq_along(LEVELS))
    cat(sprintf("%-22s (%d) %s\n", LEVELS[i], i,
                paste(sprintf("%-16s", paste0(src[i, ], "/", live[i, ])), collapse = "")))
ok <- all(src == live)
cat(sprintf("\nall %d item x level cells match (.dta rows, both rounds, vs live rows): %s\n", length(src), ok))
distinct <- length(unique(apply(src, 2, paste, collapse = "-"))) == length(ITEMS)
cat("item count-vectors mutually distinct (so a swap would be detected):", distinct, "\n")
cat("Note: does not establish the administered-language wording or any instruction text,\n",
    "neither of which the deposit or the paper contains.\n", sep = "")

cat(if (ok && distinct && cross_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
