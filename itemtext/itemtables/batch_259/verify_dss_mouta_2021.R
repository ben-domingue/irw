# verify_dss_mouta_2021.R -- Step 5b check for dss_mouta_2021 (batch_259).
#
# Claim: dss_NN is item NN of the study's own Portuguese DSS form (OSF 4xz8s,
# dss_brasilian_pt.pdf), where odd items are the rational style and even items the
# intuitive style (Hamilton et al. 2016 order). The processing script renames vNN ->
# dss_NN (number-preserving); the codebook says only "v1 = Item 1".
#
# Falsifiable prediction: the authors' own score columns in the raw OSF data
# (Racional_A, Intuitivo_A) must equal, person by person, the sum of the LIVE items we
# assigned to each style -- and no other 5-item subset may do so.
#
# What this does NOT establish: the ORDER of items within each style block (e.g. that
# dss_03 is "avalio minuciosamente" rather than "investigar os fatos"). That rests on
# the codebook's vN = "Item N" and the form's printed numbering. Hence PARTIAL.

suppressMessages(library(irw))
TABLE <- "dss_mouta_2021"
RAW_URL <- "https://osf.io/download/xz4nc/"   # Mouta_et_al_2020_Data_from_DSS_Manuscript.csv

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
codes <- sprintf("dss_%02d", 1:10)

tf <- tempfile(fileext = ".csv")
download.file(RAW_URL, tf, quiet = TRUE)
raw <- read.csv(tf, sep = ";", fileEncoding = "latin1", stringsAsFactors = FALSE)
raw$ID <- trimws(raw$ID)
m <- merge(w, raw[, c("ID", "Racional_A", "Intuitivo_A")], by.x = "id", by.y = "ID")
cat(sprintf("persons: live %d, raw %d, joined %d\n", nrow(w), nrow(raw), nrow(m)))

rat <- sprintf("dss_%02d", c(1, 3, 5, 7, 9))
int <- sprintf("dss_%02d", c(2, 4, 6, 8, 10))
r_ok <- mean(rowSums(m[, rat]) == m$Racional_A)
i_ok <- mean(rowSums(m[, int]) == m$Intuitivo_A)
cat(sprintf("rational  {01,03,05,07,09} sum == Racional_A : %.4f of persons\n", r_ok))
cat(sprintf("intuitive {02,04,06,08,10} sum == Intuitivo_A: %.4f of persons\n", i_ok))

subs <- combn(codes, 5, simplify = FALSE)
hitsR <- Filter(function(s) all(rowSums(m[, s]) == m$Racional_A), subs)
hitsI <- Filter(function(s) all(rowSums(m[, s]) == m$Intuitivo_A), subs)
cat(sprintf("5-item subsets (of %d) reproducing Racional_A exactly: %d -> %s\n",
            length(subs), length(hitsR), paste(sapply(hitsR, paste, collapse = ","), collapse = " | ")))
cat(sprintf("5-item subsets reproducing Intuitivo_A exactly: %d -> %s\n",
            length(hitsI), paste(sapply(hitsI, paste, collapse = ","), collapse = " | ")))

# Supporting marker (content): item 10, "Considero mais meus sentimentos do que analises
# racionais", explicitly contrasts feeling with analysis, so it should be the intuitive
# item most negatively related to the rational block.
cm <- cor(m[, codes])
negR <- sapply(int, function(x) mean(cm[x, rat]))
cat("mean r with rational block, per intuitive item:\n")
print(round(negR, 3))
marker <- names(which.min(negR)) == "dss_10"
cat(sprintf("dss_10 is the most negative intuitive item: %s\n", marker))

pass <- r_ok == 1 && i_ok == 1 && length(hitsR) == 1 && length(hitsI) == 1 && marker
cat("Pins: style membership of every item (unique split) + dss_10 position.\n",
    "Does NOT pin: order of the four remaining items within each style block.\n", sep = "")
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
