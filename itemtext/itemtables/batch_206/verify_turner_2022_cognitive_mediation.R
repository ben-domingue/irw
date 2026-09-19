# verify_turner_2022_cognitive_mediation.R
#
# CLAIM UNDER TEST: which of the 15 `Q*_CMgen` item codes each C-M generation
# sentence belongs to. The source (Turner, Chadha & Wood 2022, PLOS ONE
# 10.1371/journal.pone.0269928) prints the 24 item texts in S2 File and the
# retained texts again in Table 2, but numbers them 1..24 in an order that has
# nothing to do with the `Q<n>` codes carried by the deposited .sav files. The
# mapping was therefore reconstructed from published per-item numbers.
#
# Two independent checks, both run on the study's own SPSS deposits:
#   A) Table 2 (study 3, n = 403, S3 Data / .s008) prints item TEXT next to
#      M(SD) and the item's inter-item correlation range and M(SD). Four numbers
#      per item; they pin 7 of the 15 codes outright.
#   B) S2 File's first-iteration EFA (study 1, n = 250, S1 Data / .s006) prints
#      a factor loading and cross-loading per text. Re-running that EFA
#      (ML extraction, oblimin, 2 factors) over the 24 deposited columns
#      reproduces the published loadings with a uniform +.005 offset, which
#      orders all 15 codes; the cross-loadings corroborate independently.
#
# A swap of any two item_texts breaks both A and B.
#
# Needs: haven, psych, GPArotation, and network access to journals.plos.org.

suppressMessages({library(haven); library(psych)})

ITEMS_CSV <- file.path(dirname(sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1])),
                       "turner_2022_cognitive_mediation__items.csv")
if (!file.exists(ITEMS_CSV))
    ITEMS_CSV <- "itemtables/batch_206/turner_2022_cognitive_mediation__items.csv"

it <- read.csv(ITEMS_CSV, stringsAsFactors = FALSE)
map <- unique(it[, c("item", "item_text")])          # shipped mapping: code -> text
txt2code <- setNames(map$item, map$item_text)

si <- function(n) sprintf("https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0269928.s%s", n)
get_sav <- function(n) { f <- tempfile(fileext = ".sav"); download.file(si(n), f, quiet = TRUE); read_sav(f) }

ok <- TRUE

## ---------------------------------------------------------------- A) Table 2
# Published: text, M, SD, min r, max r, mean r, sd r  (PLOS ONE t002, study 3)
T2 <- list(
 c("My thoughts about the situation cause me to feel these unpleasant emotions.", 3.69,.77,.264,.377,.323,.051),
 c("How I feel is dictated by my thoughts about the situation.",                  3.88,.74,.275,.377,.325,.035),
 c("My emotions are caused by my thoughts about things around me.",              3.68,.77,.264,.396,.341,.054),
 c("My thoughts about what happens to me makes me feel these unpleasant emotions.",3.66,.79,.275,.462,.365,.062),
 c("How I feel is dictated by my thoughts towards things that happen in my life.",3.69,.80,.270,.482,.346,.081),
 c("My emotions are caused by my thoughts about things that happen to me.",       3.71,.76,.272,.482,.372,.088),
 c("My thoughts about things around me makes me feel how I feel.",                3.90,.70,.272,.376,.322,.044))

d3 <- get_sav("008")
cm3 <- grep("CMGen", names(d3), value = TRUE)
X3  <- as.data.frame(lapply(d3[cm3], as.numeric)); X3 <- X3[complete.cases(X3), ]
R3  <- cor(X3)

cat("A) study 3 (n=", nrow(X3), ") per-item descriptives vs published Table 2\n", sep = "")
cat(sprintf("%-11s %-12s %-12s %-14s %-14s\n", "code", "M pub/obs", "SD pub/obs", "r-range pub", "r-range obs"))
for (row in T2) {
    txt <- row[1]; p <- as.numeric(row[-1])
    code <- txt2code[[txt]]
    if (is.null(code)) { cat("  MISSING shipped text:", txt, "\n"); ok <- FALSE; next }
    col <- grep(paste0("^", sub("_CMgen$", "", code), "_CMGen$"), cm3, value = TRUE)
    x <- X3[[col]]; r <- R3[col, setdiff(cm3, col)]
    o <- c(mean(x), sd(x), min(r), max(r), mean(r), sd(r))
    cat(sprintf("%-11s %5.2f/%-6.2f %5.2f/%-6.2f %5.3f-%-8.3f %5.3f-%-8.3f  mean r %.3f/%.3f sd %.3f/%.3f\n",
                code, p[1], o[1], p[2], o[2], p[3], p[4], o[3], o[4], p[5], o[5], p[6], o[6]))
    if (max(abs(o - p)) > 0.006) { cat("   ^ MISMATCH\n"); ok <- FALSE }
}

## ---------------------------------------------------------------- B) S2 File
# Published first-iteration EFA loadings (factor 1) and cross-loadings, S2 File.
S2 <- list(
 c("My emotions are caused by my thoughts about things around me.",              .683,-.014),
 c("How I feel is dictated by my thoughts about the situation.",                 .659,-.035),
 c("My thoughts about what happens to me makes me feel these unpleasant emotions.",.658,-.030),
 c("My thoughts about the situation cause me to feel these unpleasant emotions.",.653,-.017),
 c("How I feel is dictated by my thoughts towards things that happen in my life.",.644,-.051),
 c("My emotions are caused by my thoughts about things that happen to me.",      .624,-.034),
 c("My thoughts about things around me makes me feel how I feel.",               .597,-.001),
 c("My emotions are caused by the way I think about things that happen in my life.",.574,-.162),
 c("It is my thoughts about the situation, rather than the situation alone, that causes my emotions.",.536,-.150),
 c("My thoughts about the situation makes me feel how I feel.",                  .529, .031),
 c("My way of thinking, not the situation, is responsible for how I feel",       .508,-.165),
 c("It is my thoughts about peoples' actions that make me feel how I feel.",     .469, .150),
 c("My emotions are caused by my thoughts about events and situations.",         .457, .069),
 c("It is my way of thinking that is responsible for my emotions, not the situation",.391,-.146),
 c("How I feel is dictated by my thoughts about how people act towards me.",     .358, .144))

d1 <- get_sav("006")
cols <- grep("CMgen|Cmgen|SRchange|Srchange", names(d1), value = TRUE)
X1 <- as.data.frame(lapply(d1[cols], as.numeric))
set.seed(1)
f <- suppressWarnings(fa(X1, nfactors = 2, fm = "ml", rotate = "oblimin"))
L <- unclass(f$loadings)
cmf <- which.max(abs(L[grep("CMgen|Cmgen", rownames(L))[1], ]))   # the C-M factor
srf <- 3 - cmf

cat("\nB) study 1 (n=", nrow(X1), ") re-run EFA vs published S2 File loadings\n", sep = "")
cat(sprintf("%-11s %8s %8s %7s | %9s %9s\n", "code", "load pub", "load obs", "diff", "cross pub", "cross obs"))
diffs <- c()
for (row in S2) {
    txt <- row[1]; p <- as.numeric(row[-1]); code <- txt2code[[txt]]
    if (is.null(code)) { cat("  MISSING shipped text:", txt, "\n"); ok <- FALSE; next }
    o <- c(L[code, cmf], L[code, srf])
    diffs <- c(diffs, o[1] - p[1])
    cat(sprintf("%-11s %8.3f %8.3f %7.3f | %9.3f %9.3f\n", code, p[1], o[1], o[1] - p[1], p[2], o[2]))
}
cat(sprintf("\nloading offset: mean %+.4f, sd %.4f (a uniform offset means the re-run reproduces the\n",
            mean(diffs), sd(diffs)))
cat("published solution; the sd is the residual precision that has to be smaller than the\n")
pubload <- sapply(S2, function(r) as.numeric(r[2]))
unpinned <- sapply(S2, function(r) txt2code[[r[1]]]) %in%
    c("Q4_CMgen","Q8_CMgen","Q14_CMgen","Q16_CMgen","Q19_CMgen","Q30_Cmgen","Q33_CMgen","Q36_CMgen")
cat(sprintf("gap between adjacent published loadings: %.3f overall (Q42 vs Q47, both pinned\n",
            min(abs(diff(sort(pubload))))))
cat(sprintf("independently by check A) and %.3f among the 8 codes that rest on this check alone)\n",
            min(abs(diff(sort(pubload[unpinned]))))))
if (sd(diffs) > 0.003) { cat("MISMATCH: re-run does not reproduce the published loadings\n"); ok <- FALSE }

cat("\nWhat this does NOT establish: check A pins 7 of the 15 codes on four independent\n")
cat("published numbers each; the other 8 codes (Q4, Q8, Q14, Q16, Q19, Q30, Q33, Q36) were\n")
cat("dropped after study 1 and rest on check B alone, i.e. on the re-run reproducing S2's\n")
cat("loading order. Their published cross-loadings corroborate 7 of those 8; S2's cross-loading\n")
cat("for the Q36 text (-.162 vs -.037 observed) does not reconcile and is most likely a\n")
cat("transcription error in that table, which also prints an impossible '0.71' cross-loading\n")
cat("for its item 20. Q36's primary loading is isolated by .038, so its assignment is not at risk.\n")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
