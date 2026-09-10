# verify_neurodegenerative_huizinga_2019_svc.R
#
# Claim under test: IRW item code SVK.n is question n of the Screening Visuele
# Klachten (SVK / SVC) as printed in Huizinga et al. (2020) PLoS ONE 15(4):
# e0232232, S1 (Dutch) / S2 (English) Appendix.  The processing script
# (data/neurodegenerative_huizinga_2019.R) carries the source column names
# SVK.1..SVK.21 through unchanged, so what needs verifying is the tie between
# those column names and the questionnaire's own item numbers.
#
# Three independent checks, all against numbers the paper published:
#   A. Item 1 marginal counts. The paper states "503 of the 1,461 participants
#      (34%) reported to sometimes experience visual problems in daily life,
#      while 101 participants (7%) reported to often experience visual
#      problems".  This pins SVK.1 AND the 0/1/2 -> Nee-nauwelijks/Soms/
#      Vaak-altijd option coding.
#   B. Response range signature. Questionnaire item 21 is the only 0-10 rating;
#      items 1-20 are 3-point. Pins SVK.21.
#   C. Exploratory factor analysis, paper Table 3 (principal axis factoring,
#      oblimin, subsample 1, n = 730, items 2-20).  Every one of the 19 items
#      has its own published loading triple; reproducing them from the live data
#      distinguishes each item from every other one.
#
# Subsample membership is not in the IRW table, so it is read from the public
# DataverseNL deposit (doi:10.34894/CMJXAK, Data_total.csv) by row index. That
# is legitimate because the processing script sets id <- seq_len(nrow(df)); the
# script asserts the live/raw correspondence cell-for-cell before using it.

suppressMessages({library(irw); library(psych)})
TABLE <- "neurodegenerative_huizinga_2019_svc"
ITEMS <- paste0("SVK.", 1:21)

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)

cat("=== A. Item 1 marginal counts vs the paper's own sentence ===\n")
i1 <- d$resp[d$item == "SVK.1"]
n1 <- sum(i1 == 1, na.rm = TRUE); n2 <- sum(i1 == 2, na.rm = TRUE)
cat(sprintf("published: 'sometimes' = 503, 'often/always' = 101 (of 1,461)\n"))
cat(sprintf("observed : SVK.1 resp==1 -> %d, resp==2 -> %d (n = %d)\n",
            n1, n2, sum(!is.na(i1))))
okA <- (n1 == 503L && n2 == 101L)
cat("A:", if (okA) "MATCH\n" else "MISMATCH\n")

cat("\n=== B. Response-range signature ===\n")
rng <- tapply(d$resp, d$item, function(z) paste(sort(unique(z[!is.na(z)])), collapse = ","))
for (it in ITEMS) cat(sprintf("  %-7s %s\n", it, rng[[it]]))
okB <- rng[["SVK.21"]] == paste(0:10, collapse = ",") &&
       all(vapply(ITEMS[1:20], function(it) rng[[it]] == "0,1,2", TRUE))
cat("B:", if (okB) "only SVK.21 is the 0-10 rating; items 1-20 are 3-point -- MATCH\n"
        else "MISMATCH\n")

cat("\n=== C. Reproduce paper Table 3 factor loadings ===\n")
# Published Table 3 (rows in questionnaire-item order 2..20), F1, F2, F3.
PUB <- rbind(
 "SVK.2" =c( .778,-.064,-.035), "SVK.3" =c( .642, .022, .081),
 "SVK.4" =c( .011, .495,-.020), "SVK.5" =c( .301, .168, .135),
 "SVK.6" =c(-.031, .521, .143), "SVK.7" =c( .110, .472,-.081),
 "SVK.8" =c(-.009, .471,-.021), "SVK.9" =c( .622,-.018, .010),
 "SVK.10"=c( .420, .056, .205), "SVK.11"=c( .505, .043,-.036),
 "SVK.12"=c( .442,-.044, .167), "SVK.13"=c(-.055, .536, .070),
 "SVK.14"=c( .114, .556,-.065), "SVK.15"=c( .009, .099, .557),
 "SVK.16"=c( .092,-.040, .608), "SVK.17"=c( .564, .067, .094),
 "SVK.18"=c( .371, .199, .067), "SVK.19"=c( .369, .160, .035),
 "SVK.20"=c( .612, .001,-.173))

d <- as.data.frame(d)
d$id <- as.integer(as.character(d$id))
wide <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
                direction = "wide")
names(wide) <- sub("^resp\\.", "", names(wide))
wide <- wide[order(wide$id), ]
stopifnot(all(ITEMS %in% names(wide)))

raw_url <- "https://dataverse.nl/api/access/datafile/19456"
f <- file.path(tempdir(), "Data_total.csv")
if (!file.exists(f)) download.file(raw_url, f, quiet = TRUE)
raw <- read.csv(f, sep = ";", stringsAsFactors = FALSE)

# id == row number of Data_total.csv -- assert it rather than assume it.
cat(sprintf("live rows %d, deposit rows %d, id range %d..%d, ids == 1:n : %s\n",
            nrow(wide), nrow(raw), min(wide$id), max(wide$id),
            identical(wide$id, seq_len(nrow(raw)))))
stopifnot(nrow(raw) == nrow(wide), identical(wide$id, seq_len(nrow(raw))))
cmp <- sapply(ITEMS, function(it) {
  a <- suppressWarnings(as.numeric(wide[[it]]))
  b <- suppressWarnings(as.numeric(raw[[it]]))
  stopifnot(length(a) == nrow(raw), length(b) == nrow(raw))
  sum(is.na(a) != is.na(b)) + sum(a != b, na.rm = TRUE)
})
cat(sprintf("live-vs-deposit cell mismatches across 21 items x %d rows: %d\n",
            nrow(raw), sum(cmp)))
okJoin <- sum(cmp) == 0

sub1 <- raw$Group_Subsample == 1
x <- wide[sub1, paste0("SVK.", 2:20)]
x[] <- lapply(x, function(z) suppressWarnings(as.numeric(z)))
cat(sprintf("EFA on subsample 1, n = %d (paper: 730)\n", nrow(x)))
fit <- suppressWarnings(psych::fa(x, nfactors = 3, fm = "pa", rotate = "oblimin"))
L <- unclass(fit$loadings)[rownames(PUB), , drop = FALSE]

# Align the estimated factor columns (arbitrary order/sign) to the published ones.
perm <- integer(3); used <- c()
for (j in 1:3) {
  cors <- sapply(1:3, function(k) if (k %in% used) -Inf else abs(cor(PUB[, j], L[, k])))
  perm[j] <- which.max(cors); used <- c(used, perm[j])
}
L <- L[, perm]
for (j in 1:3) if (cor(PUB[, j], L[, j]) < 0) L[, j] <- -L[, j]

cat(sprintf("%-8s %18s %18s %8s\n", "item", "published F1/F2/F3", "observed F1/F2/F3", "maxdiff"))
for (i in seq_len(nrow(PUB)))
  cat(sprintf("%-8s %6.3f%6.3f%6.3f %6.3f%6.3f%6.3f %8.3f\n", rownames(PUB)[i],
      PUB[i,1], PUB[i,2], PUB[i,3], L[i,1], L[i,2], L[i,3],
      max(abs(PUB[i, ] - L[i, ]))))
worst <- max(abs(PUB - L))
cat(sprintf("largest loading deviation: %.3f (tolerance 0.05)\n", worst))

# Does each observed row match ITS OWN published row better than any other's?
D <- as.matrix(dist(rbind(PUB, L)))[1:nrow(PUB), nrow(PUB) + seq_len(nrow(L))]
nearest <- rownames(PUB)[apply(D, 2, which.min)]
bad <- rownames(PUB)[nearest != rownames(PUB)]
cat(sprintf("items whose nearest published loading triple is their own: %d / %d\n",
            sum(nearest == rownames(PUB)), nrow(PUB)))
if (length(bad)) cat("  not uniquely matched:", paste(bad, collapse = ", "), "\n")
okC <- worst <= 0.05 && length(bad) == 0

cat("\nWhat this does NOT establish: nothing here tests the Dutch-vs-English\n",
    "wording pairing (both come from the same paper's S1/S2 appendices), and the\n",
    "unlabelled scale points 1-9 of SVK.21 carry no text to verify.\n", sep = "")

cat(if (okA && okB && okJoin && okC) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
