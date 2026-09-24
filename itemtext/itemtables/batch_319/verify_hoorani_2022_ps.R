# verify_hoorani_2022_ps.R -- Step 5b, route 9 (response-frequency matching)
# plus route 6 (keying polarity).
#
# CLAIM UNDER TEST: each IRW item code PS1..PS4 carries the item text of the
# identically named variable in the study's Stata deposit (S2 File, .s016), and
# the integer resp 1..4 encodes "Strongly disagree".."Strongly agree" in that
# order. NOTE the .dta's own NUMERIC codes run the other way (1 = Strongly agree
# ... 4 = Strongly disagree); data/hoorani_2022_young_lives_battery.py maps the
# LABELS through MAP_AGREE4, so the live resp is the reverse of the Stata code.
#
# FALSIFIABLE PREDICTION: for every item, the count of each raw label in the .dta
# equals the count of the corresponding integer in the live IRW table. The four
# items' count vectors are mutually distinct, so swapping any two items, or any
# permutation/reversal of the four levels, breaks the match.
#
# Verifies the MAPPING (both axes), not the item/resp sets (validate_items.R).

suppressMessages(library(irw))

TABLE  <- "hoorani_2022_ps"
ITEMS  <- c("PS1", "PS2", "PS3", "PS4")
LEVELS <- c("Strongly disagree", "Disagree", "Agree", "Strongly agree")  # resp 1..4
SI_URL <- paste0("https://journals.plos.org/plosone/article/file",
                 "?type=supplementary&id=10.1371/journal.pone.0271374.s016")

## ---- source side: label counts per item from the .dta -------------------
dta <- tempfile(fileext = ".dta")
utils::download.file(SI_URL, dta, quiet = TRUE, mode = "wb")
raw <- haven::read_dta(dta)

for (it in ITEMS) cat(sprintf("%s .dta variable label: %s\n", it, attr(raw[[it]], "label")))

src <- sapply(ITEMS, function(it) {
    v <- as.character(haven::as_factor(raw[[it]]))
    v <- v[!is.na(v)]
    sapply(LEVELS, function(l) sum(v == l))
})

## ---- live side: resp counts per item, one server-side GROUP BY ----------
s <- irw::irw_table_sets(TABLE, source = "core", per_item = FALSE)
sql <- sprintf(paste("SELECT CAST(item AS STRING) AS item,",
                     "SAFE_CAST(TRIM(CAST(resp AS STRING)) AS FLOAT64) AS resp,",
                     "COUNT(*) AS n FROM `%s` GROUP BY 1,2"), s$table)
d <- suppressWarnings(redivis::redivis$query(sql)$to_tibble())

live <- sapply(ITEMS, function(it) {
    sapply(1:4, function(k) {
        n <- d$n[as.character(d$item) == it & !is.na(d$resp) & d$resp == k]
        if (length(n) == 0) 0L else as.integer(sum(n))
    })
})
rownames(live) <- LEVELS

cat(sprintf("\n%-22s %s\n", "level (resp)",
            paste(sprintf("%-14s", paste0(ITEMS, " src/live")), collapse = "")))
for (i in seq_along(LEVELS))
    cat(sprintf("%-18s (%d) %s\n", LEVELS[i], i,
                paste(sprintf("%-14s", paste0(src[i, ], "/", live[i, ])), collapse = "")))

ok <- all(src == live)
cat(sprintf("\nall %d item x level cells match: %s\n", length(src), ok))
distinct <- length(unique(apply(src, 2, paste, collapse = "-"))) == length(ITEMS)
cat("item count-vectors mutually distinct (so a swap would be detected):", distinct, "\n")

## ---- route 6 corroboration: polarity from the source file itself --------
## PS1 is positively worded ("proud"), PS2-PS4 negatively ("ashamed",
## "embarrassed", "worried"); the paper's Table 1 loadings are +0.132 / -0.412 /
## -0.481 / -0.760. On the live 1..4 = disagree..agree coding PS1 should correlate
## negatively with PS2-PS4 and PS2-PS4 positively with each other.
w <- sapply(ITEMS, function(it) {
    v <- as.character(haven::as_factor(raw[[it]])); match(v, LEVELS)
})
w <- w[stats::complete.cases(w), ]
r <- stats::cor(w)
cat("\ninter-item correlations (resp 1..4 coding, n =", nrow(w), "):\n")
print(round(r, 3))
pol <- all(r["PS1", c("PS2", "PS3", "PS4")] < 0) &&
       all(r[c("PS2", "PS3", "PS4"), c("PS2", "PS3", "PS4")][upper.tri(diag(3))] > 0)
cat("polarity pattern matches wording (PS1 +, PS2-4 -):", pol, "\n")

cat("Note: route 9 pins item<->text and resp<->option_text via the .dta whose variable\n",
    "labels supply the wording. It does not establish the administered language or any\n",
    "instruction text, neither of which the deposit or the paper contains.\n", sep = "")

cat(if (ok && distinct && pol) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
