# verify_avilatamayo_2022_empl_stab.R -- Step 5b re-runnable evidence.
#
# mapping_basis = paper_order. The IRW item codes ARE the S1 .sav column names
# (data/avilatamayo_2022_csr.py melts them verbatim), and the .sav variable labels
# read "Employee stability 1" .. "Employee stability 7". The inference this script
# tests is the remaining one: that row N of the S2 Appendix's "Estabilidad en el
# empleo" block is questionnaire item N.
#
# Two checks:
#   A. resp axis (decisive). The .sav stores 1-7 with value labels
#      "Totally disagree".."Totally agree"; the processing script recoded those label
#      STRINGS to 1-7. If option_text were mis-assigned or the direction flipped, the
#      per-item x per-level counts would not reproduce. 49 cells compared.
#   B. item axis (partial). Item 7 of the appendix block is the summary item
#      ("En general, la organizacion proporciona ... una alta estabilidad laboral" /
#      "Overall, the company provides employees with very high employment stability").
#      A summary item must carry the HIGHEST corrected item-total correlation of the
#      block; item 1 ("nunca despediria a los empleados de manera discrecional" -- the
#      most absolute, most idiosyncratic claim) the lowest. This pins positions 1 and 7
#      only; it does NOT separate positions 2-6 from one another.

suppressMessages(library(irw))

TABLE <- "avilatamayo_2022_empl_stab"
ITEMS <- paste0("Empl_Stab_1.", 1:7, "_1")
SAV   <- file.path("~/irw-queue-runner/itemtext/.cache", TABLE, "s001.sav")
URL   <- paste0("https://journals.plos.org/plosone/article/file",
                "?type=supplementary&id=10.1371/journal.pone.0266711.s001")

sav <- path.expand(SAV)
if (!file.exists(sav)) {
    dir.create(dirname(sav), recursive = TRUE, showWarnings = FALSE)
    utils::download.file(URL, sav, mode = "wb", quiet = TRUE)
}
raw  <- haven::read_sav(sav)
live <- irw::irw_fetch(TABLE)

ok <- TRUE

## ---- A. resp axis: per-item x per-level counts, source vs live -------------
cat("=== A. option_text <-> resp: per-item x level counts (.sav vs live IRW) ===\n")
cat(sprintf("%-16s %-22s %8s %8s\n", "item", "label", "sav_n", "live_n"))
LAB <- c("Totally disagree", "Disagree", "Partially disagree",
         "Not in disagree or agree", "Partially agree", "Agree", "Totally agree")
mismatch <- 0
for (it in ITEMS) {
    v <- as.numeric(raw[[it]])
    for (k in 1:7) {
        a <- sum(v == k, na.rm = TRUE)
        b <- sum(live$item == it & live$resp == k)
        if (a != b) mismatch <- mismatch + 1
        cat(sprintf("%-16s %-22s %8d %8d%s\n", it, LAB[k], a, b,
                    if (a != b) "   <-- MISMATCH" else ""))
    }
}
cat(sprintf("\ncells compared: 49   mismatched: %d\n", mismatch))
if (mismatch != 0) ok <- FALSE

## ---- B. item axis: marker item ---------------------------------------------
cat("\n=== B. item_text <-> item: corrected item-total correlations ===\n")
m <- sapply(ITEMS, function(it) as.numeric(raw[[it]]))
tot <- rowSums(m)
r <- sapply(seq_along(ITEMS), function(j) cor(m[, j], tot - m[, j], use = "complete.obs"))
mu <- colMeans(m, na.rm = TRUE)
names(r) <- ITEMS
cat(sprintf("%-16s %6s %8s\n", "item", "mean", "r_itc"))
for (j in seq_along(ITEMS)) cat(sprintf("%-16s %6.2f %8.3f\n", ITEMS[j], mu[j], r[j]))

top <- ITEMS[which.max(r)]; bot <- ITEMS[which.min(r)]
cat(sprintf("\nhighest r_itc: %s (%.3f)  -- predicted Empl_Stab_1.7_1 (the 'En general/Overall' item)\n",
            top, max(r)))
cat(sprintf("lowest  r_itc: %s (%.3f)  -- predicted Empl_Stab_1.1_1 (the absolute 'nunca despediria' item)\n",
            bot, min(r)))
cat(sprintf("highest mean : %s (%.2f)  -- predicted Empl_Stab_1.7_1\n",
            ITEMS[which.max(mu)], max(mu)))
if (top != "Empl_Stab_1.7_1" || bot != "Empl_Stab_1.1_1" ||
    ITEMS[which.max(mu)] != "Empl_Stab_1.7_1") ok <- FALSE

cat("\nNote: check B pins positions 1 and 7 of the 7-item block ONLY. It does NOT\n",
    "distinguish appendix rows 2-6 from one another; those rest on the appendix's\n",
    "presentation order, corroborated by the fact that the appendix's seven subscale\n",
    "headings appear in exactly the order of the .sav's subscale prefix numbers 1..7\n",
    "(Estabilidad=1, Entorno=2, Desarrollo=3, Diversidad=4, Equilibrio=5, Tangible=6,\n",
    "Empoderamiento=7). Hence status PARTIAL, not VERIFIED.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
