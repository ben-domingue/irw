# verify_pierro_2018_tf_past_s4.R
#
# TABLE: pierro_2018_tf_past_s4  (Temporal Focus Scale, Past Focus subscale;
#        Pierro, Pica, Giannini, Higgins & Kruglanski 2018, PLoS ONE 13(3):e0193357,
#        Study 4, N=189 Sapienza students, item codes TFpast1..TFpast4, resp 1-7).
#
# WHAT IS BEING VERIFIED -- and, just as important, what is NOT.
#
# The shipped item text is the ENGLISH Temporal Focus Scale wording of Shipp, Edwards &
# Lambert (2009), taken from Table 9 of the CC BY Italian validation
# (Nuzzo? / BMC Psychology 2021, PMC7851924, doi 10.1186/s40359-020-00510-5), whose
# Table 3 note states "Item number relates to Shipp et al. 2009".
#
# CLAIM 1 (tested here, mechanically): each English sentence can be tied to its number in
#   Shipp et al.'s ORIGINAL 12-item instrument. Table 3 gives the past/future/current
#   factor membership in SHIPP numbering (past = 1, 6, 9, 11); Table 9 prints the reduced
#   10-item TFS-I in ITS OWN renumbering 1..10 with a PF/FF/CF tag per line. If the TFS-I
#   renumbering is simply Shipp's order with the two dropped items (Shipp 5 and 10)
#   removed, then mapping Shipp -> TFS-I positions must reproduce Table 9's factor pattern
#   EXACTLY. There are 10!/(4!3!3!) = 4200 ways to lay 4 PF / 3 FF / 3 CF over ten
#   positions, so an exact hit is not a coincidence a reader has to take on trust.
#   PASS/FAIL is decided on this.
#
# CLAIM 2 (NOT established -- this is why the table is recorded NO_ROUTE): that the IRW
#   code TFpastK is the K-th past item of that instrument order (1, 6, 9, 11). Nothing in
#   the deposit or the paper ties the codes to wording: the .sav carries no variable
#   labels, and the PLOS article quotes exactly one past item as an illustration. All four
#   items are same-subscale, same-range, same-polarity near-synonyms, so no statistical
#   route can separate them. The cross-sample mean check printed below is run as the only
#   available falsification attempt and is reported as NON-DIAGNOSTIC; it is not part of
#   the verdict.

ok <- requireNamespace("haven", quietly = TRUE)
if (!ok) stop("needs the 'haven' package to read the deposit .sav")

## ---------------------------------------------------------------- source text
xml_url <- "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7851924/fullTextXML"
x <- paste(readLines(xml_url, warn = FALSE), collapse = "\n")
cat(sprintf("Fetched Europe PMC full text for PMC7851924 (%d bytes)\n\n", nchar(x)))

# --- Table 3: factor membership in SHIPP numbering --------------------------
t3 <- regmatches(x, regexpr("Pattern matrix EFA.{0,4000}", x, perl = TRUE))
rows <- regmatches(t3, gregexpr("Item ([0-9]+)</td>(.{0,200}?)</tr>", t3, perl = TRUE))[[1]]
num <- as.integer(sub("Item ([0-9]+)</td>.*", "\\1", rows))
# three loading columns per row, in the order Past, Future, Current
loads <- lapply(rows, function(r) {
    v <- regmatches(r, gregexpr("[-\u2212]?\\s?\\.[0-9]{3}", r, perl = TRUE))[[1]]
    as.numeric(sub("^[-−]\\s?", "-", gsub(" ", "", v)))
})
fac3 <- c("PF", "FF", "CF")[sapply(loads, function(v) which.max(abs(v)))]
shipp <- setNames(fac3, num)
shipp <- shipp[order(as.integer(names(shipp)))]
cat("Table 3 (EFA), factor of each item in SHIPP et al. 2009 numbering:\n")
print(shipp)
past_shipp <- as.integer(names(shipp)[shipp == "PF"])
cat(sprintf("  -> past-focus items in Shipp numbering: %s\n\n",
            paste(past_shipp, collapse = ", ")))

# --- Table 9: the reduced 10-item list, TFS-I numbering ----------------------
t9 <- regmatches(x, regexpr("Temporal focus scale \\(TFS-I\\).{0,6000}", x, perl = TRUE))
lines9 <- regmatches(t9, gregexpr("([0-9]{1,2})\\. ([A-Z][^<]*?) \\((PF|CF|FF)\\)", t9, perl = TRUE))[[1]]
n9  <- as.integer(sub("^([0-9]{1,2})\\..*", "\\1", lines9))
tx9 <- sub("^[0-9]{1,2}\\. (.*) \\((PF|CF|FF)\\)$", "\\1", lines9)
f9  <- sub(".*\\((PF|CF|FF)\\)$", "\\1", lines9)
o   <- order(n9); n9 <- n9[o]; tx9 <- tx9[o]; f9 <- f9[o]
cat("Table 9, the 10-item TFS-I in its own numbering:\n")
for (i in seq_along(n9)) cat(sprintf("  %2d  %-45s (%s)\n", n9[i], tx9[i], f9[i]))

## ------------------------------------------------- CLAIM 1: the deletion map
dropped <- setdiff(1:12, as.integer(names(shipp)))
kept    <- sort(as.integer(names(shipp)))
cat(sprintf("\nShipp items dropped from the TFS-I: %s\n", paste(dropped, collapse = ", ")))
predicted <- shipp[as.character(kept)]           # order-preserving renumber 1..10
names(predicted) <- seq_along(kept)
cat("Factor pattern PREDICTED at TFS-I positions 1..10 by order-preserving deletion:\n  ")
cat(paste(predicted, collapse = " "), "\n")
cat("Factor pattern OBSERVED in Table 9:\n  ")
cat(paste(f9, collapse = " "), "\n")
exact <- identical(unname(predicted), unname(f9)) && identical(n9, 1:10)
cat(sprintf("  exact match: %s   (1 arrangement in %d if it were chance)\n",
            exact, round(factorial(10) / (factorial(4) * factorial(3) * factorial(3)))))

wording <- setNames(tx9[f9 == "PF"], past_shipp)   # Shipp number -> English wording
cat("\nDerived tie, English wording -> Shipp et al. (2009) item number:\n")
for (k in names(wording)) cat(sprintf("  Shipp %-2s  %s\n", k, wording[k]))

shipped <- c("I think about things from my past",
             "I replay memories of the past in my mind",
             "I reflect on what has happened in my life",
             "I think back to my earlier days")
cat("\nShipped item_text for TFpast1..TFpast4, in code order:\n")
for (i in 1:4) cat(sprintf("  TFpast%d  %s\n", i, shipped[i]))
same_order <- identical(unname(wording), shipped)
cat(sprintf("  equals the past items in Shipp instrument order (%s): %s\n",
            paste(past_shipp, collapse = ","), same_order))

## ------------------------------- CLAIM 2 falsification attempt (NON-DIAGNOSTIC)
sav <- tempfile(fileext = ".sav")
utils::download.file("https://doi.org/10.1371/journal.pone.0193357.s004", sav,
                     quiet = TRUE, mode = "wb")
d <- haven::read_sav(sav)
cols <- paste0("TFpast", 1:4)
m <- as.data.frame(d[, cols]); m[m < 1 | m > 7] <- NA
live_mean <- sapply(m, mean, na.rm = TRUE)
val_mean  <- c(`1` = 3.70, `6` = 3.67, `9` = 3.92, `11` = 3.51)   # PMC7851924 Table 2, N=1458
cat("\n--- NON-DIAGNOSTIC cross-sample check (reported, not part of the verdict) ---\n")
cat(sprintf("Live per-item means (deposit S4 File, the IRW codes themselves, N=%d):\n", nrow(m)))
print(round(live_mean, 2))
cat("Italian-validation per-item means for Shipp past items 1, 6, 9, 11 (Table 2, N=1458):\n")
print(val_mean)
rho <- suppressWarnings(cor(rank(live_mean), rank(val_mean)))
cat(sprintf("Spearman rho between the two mean profiles under the shipped mapping: %.2f\n", rho))
cat("Levels differ by ~1.4 scale points between the two samples and the four validation\n")
cat("means span only 3.51-3.92, so this neither confirms nor refutes the code order.\n")

cat("\nWHAT THIS SCRIPT DOES NOT ESTABLISH: which of TFpast1..TFpast4 is which sentence.\n")
cat("The four are interchangeable under every statistic available; the shipped order is\n")
cat("the instrument's own past-item order and is an inference. Status NO_ROUTE.\n\n")

cat(if (exact && same_order) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
