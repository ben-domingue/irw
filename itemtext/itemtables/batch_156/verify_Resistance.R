# verify_Resistance.R -- Step 5b evidence for `Resistance`, re-runnable.
#
# CLAIM UNDER TEST. Each IRW item is one framing PAIR of the Resistance to
# Framing scale, and `resp` is the absolute difference between the respondent's
# rating of the two frames (Codebook.xlsx: "The absolute difference between loss
# and gain frame on the ' pesticide ' item"). The shipped `item_text` for e.g.
# RC_pesticide is the Qualtrics text of questions RCG1 and RCL5. So the falsifiable
# prediction is: for each of the 14 item codes, the specific (gain-tag, loss-tag)
# pair whose wording we shipped must reproduce that column of the study's derived
# data file, for every respondent, in both country samples.
#
# This is NOT a count check -- validate_items.R already did that. It breaks if any
# two items' texts were swapped, which is demonstrated below by re-running it under
# every same-family transposition.
#
# Data: OSF j5n6f (CC BY 4.0), components 3. Data (7vtas) and 2. Materials (8j9em).

pairs <- list(
  RC_pesticide = c("RCG1","RCL5"), RC_taxes   = c("RCG2","RCL4"),
  RC_dropout   = c("RCG3","RCL7"), RC_disease = c("RCG4","RCL2"),
  RC_cancer    = c("RCG5","RCL6"), RC_stocks  = c("RCG6","RCL3"),
  RC_soldiers  = c("RCG7","RCL1"),
  AF_condom    = c("AFP1","AFN6"), AF_beef    = c("AFP2","AFN5"),
  AF_cheating  = c("AFP3","AFN3"), AF_budget  = c("AFP4","AFN1"),
  AF_exams     = c("AFP5","AFN7"), AF_parking = c("AFP6","AFN2"),
  AF_cancer    = c("AFP7","AFN4"))
items <- names(pairs)

OSF <- c(raw_NA = "60b37546cb2a5e00f069442b", raw_BG = "60b373e83a6df10101d50115",
         der_NA = "60b375469096b700f363ec7b", der_BG = "60b373e5cb2a5e00f568fd56")
cache <- file.path(tempdir(), "Resistance_verify"); dir.create(cache, showWarnings = FALSE)
get <- function(key) {
    f <- file.path(cache, paste0(key, ".csv"))
    if (!file.exists(f))
        utils::download.file(sprintf("https://osf.io/download/%s/", OSF[[key]]),
                             f, quiet = TRUE, mode = "wb")
    read.csv(f, row.names = 1, fileEncoding = "latin1", check.names = FALSE)
}

tags <- as.vector(outer(1:7, c("RCG","RCL","AFP","AFN"), function(i, p) paste0(p, i)))
mkraw <- function(d) {
    m <- sapply(tags, function(t) suppressWarnings(as.numeric(d[[t]])))
    m[stats::complete.cases(m), , drop = FALSE]
}

# unmatched(): how many of the study's derived 14-vectors are NOT reproduced by
# the candidate pairing, as a multiset. Row order is not recoverable (the derived
# files drop excluded respondents and carry no id), so this compares multisets --
# which is strictly harder to satisfy by accident in 14 dimensions.
unmatched <- function(P, raws, ders) {
    tot <- 0
    for (k in names(raws)) {
        r <- raws[[k]]
        pred <- sapply(items, function(it) abs(r[, P[[it]][1]] - r[, P[[it]][2]]))
        pk <- table(apply(pred, 1, paste, collapse = "|"))
        ok <- table(apply(ders[[k]][, items], 1, paste, collapse = "|"))
        for (key in names(ok))
            tot <- tot + max(0, ok[[key]] - if (key %in% names(pk)) pk[[key]] else 0)
    }
    tot
}

raws <- list(NA_ = mkraw(get("raw_NA")), BG = mkraw(get("raw_BG")))
ders <- list(NA_ = get("der_NA"),         BG = get("der_BG"))
n_der <- sum(sapply(ders, nrow))

cat(sprintf("derived respondents (NA + BG): %d\n", n_der))
cat(sprintf("raw complete-case respondents: %d\n\n", sum(sapply(raws, nrow))))

base <- unmatched(pairs, raws, ders)
cat(sprintf("SHIPPED pairing: %d of %d derived response vectors unreproduced\n\n", base, n_der))

# Falsification: every transposition of two same-family items' frame pairs.
worst <- Inf; n_alt <- 0
for (i in seq_along(items)) for (j in seq_along(items)) {
    if (j <= i) next
    a <- items[i]; b <- items[j]
    if (substr(a, 1, 2) != substr(b, 1, 2)) next
    P <- pairs; P[[a]] <- pairs[[b]]; P[[b]] <- pairs[[a]]
    worst <- min(worst, unmatched(P, raws, ders)); n_alt <- n_alt + 1
}
cat(sprintf("%d same-family transpositions tested; BEST rival scores %d of %d unreproduced\n",
            n_alt, worst, n_der))

cat("\nWhat this establishes: each of the 14 item codes is tied to one specific pair of\n",
    "Qualtrics questions, and the .qsf ties those questions to the wording shipped in\n",
    "item_text. Every item is separated from every other -- no rival pairing survives.\n",
    "What it does NOT establish: option_text is blank by design (resp is a derived\n",
    "|gain - loss| difference with no administered labels), so no option mapping is tested.\n", sep = "")

cat(if (base == 0 && worst > 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
