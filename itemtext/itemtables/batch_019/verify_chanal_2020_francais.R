# verify_chanal_2020_francais.R
#
# STATUS: this table is BLOCKED -- no chanal_2020_francais__items.csv was written.
# What this script verifies is the recorded Step 5b finding (status NO_ROUTE):
# that the ONLY candidate item<->code mapping available for this table -- the
# published order of the 33-item instrument in Appendix A of Chanal, Cheval,
# Courvoisier & Paumier (2019), Psych Sport Exerc 43:233-242,
# https://ars.els-cdn.com/content/image/1-s2.0-S1469029218304254-mmc1.docx --
# is CONTRADICTED by the response data, so no mapping could be shipped.
#
# The IRW item code is a number-preserving rename of the source column
# (data/chanal_2020_selfconcept.py: "Francais<N>" -> "francais_<N>"), so the
# mapping question is entirely about the source columns Francais1..Francais33.
# This script therefore reads the study's own public S1 Dataset rather than
# exporting the IRW table (200GB/30d Redivis export cap).
#
# Falsifiable prediction of the appendix-order hypothesis:
#   cols  1-4 = intrinsic-stimulation, 5-8 = intrinsic-achievement,
#   9-12 = identified, 13-16 = introjected approach, 17-20 = introjected
#   avoidance, 21-25 = external approach, 26-29 = external avoidance,
#   30-33 = amotivation.
# Two consequences that must hold if it is true:
#   (A) every hypothesised subscale must cohere better than a random set of
#       items, i.e. mean within-block r > the overall mean inter-item r;
#   (B) the amotivation block (30-33) must hold the most negative item-grade
#       correlations of the 33 columns.
# PASS here means the refutation reproduces (i.e. the recorded NO_ROUTE finding
# stands). It is NOT a claim that any mapping is correct.

suppressMessages({library(readxl)})

URL <- paste0("https://journals.plos.org/plosone/article/file?",
              "id=10.1371/journal.pone.0230103.s001&type=supplementary")
f <- file.path(tempdir(), "chanal2020_s001.xlsx")
if (!file.exists(f)) download.file(URL, f, mode = "wb", quiet = TRUE)
d <- as.data.frame(read_excel(f))

prefixes <- c("Ecole", "Maths", "Francais", "Anglais", "EducPhy")
num <- function(x) suppressWarnings(as.numeric(as.character(x)))
getdom <- function(p) {
    X <- sapply(1:33, function(i) num(d[[paste0(p, i)]]))
    X[X < 1 | X > 7] <- NA
    colnames(X) <- 1:33
    X
}
doms <- lapply(prefixes, getdom); names(doms) <- prefixes

# average the 5 parallel administrations of the SAME 33 items
Cs <- lapply(doms, function(X) cor(X, use = "pairwise.complete.obs"))
C  <- Reduce(`+`, Cs) / length(Cs)

blocks <- list(`IM-stimulation` = 1:4, `IM-achievement` = 5:8, `identified` = 9:12,
               `introj-approach` = 13:16, `introj-avoidance` = 17:20,
               `external-approach` = 21:25, `external-avoidance` = 26:29,
               `amotivation` = 30:33)
off <- C[upper.tri(C)]
overall <- mean(off)

cat("(A) mean within-block inter-item r under the appendix-order hypothesis\n")
cat(sprintf("    overall mean inter-item r across all 33 columns = %.3f\n\n", overall))
cat(sprintf("    %-20s %8s %10s\n", "hypothesised block", "within r", "vs overall"))
below <- 0
for (nm in names(blocks)) {
    ix <- blocks[[nm]]
    sub <- C[ix, ix]
    w <- mean(sub[upper.tri(sub)])
    flag <- if (w < overall) { below <- below + 1; "BELOW" } else "ok"
    cat(sprintf("    %-20s %8.3f %10s\n", nm, w, flag))
}
cat(sprintf("\n    %d of 8 hypothesised subscales cohere WORSE than a random set of\n",
            below))
cat("    items from the questionnaire. A genuine subscale cannot do that.\n\n")

cat("(B) convergent item-grade correlations (each domain's item vs that\n")
cat("    subject's own end-of-year grade), averaged over the 4 school subjects\n")
gcols <- c(Maths = "Note_MA", Francais = "Note_FR", Anglais = "Note_AN", EducPhy = "Note_EP")
R <- sapply(names(gcols), function(p) {
    g <- num(d[[gcols[[p]]]])
    apply(doms[[p]], 2, function(v) cor(v, g, use = "pairwise.complete.obs"))
})
m <- rowMeans(R)
ord <- order(m)
cat("    five most negative columns (amotivation must live here):\n")
for (i in ord[1:5]) cat(sprintf("      col %2d  mean r = %+.3f\n", i, m[i]))
cat("    hypothesised amotivation block 30-33:\n")
for (i in 30:33) cat(sprintf("      col %2d  mean r = %+.3f\n", i, m[i]))
inB <- sum(30:33 %in% ord[1:5])
cat(sprintf("\n    %d of the 4 hypothesised amotivation columns are among the 5 most\n", inB))
cat("    negative. Column 33 in particular is one of the MOST positive columns,\n")
cat(sprintf("    mean r = %+.3f, which no amotivation item can be.\n\n", m[33]))

cat("What this does NOT establish: it does not identify the correct mapping, and\n")
cat("no alternative mapping was shipped. It only shows the published instrument\n")
cat("order is not the source file's column order, which is why the table is\n")
cat("blocked with mapping_basis=unknown / status=NO_ROUTE.\n\n")

refuted <- (below >= 3) && (inB <= 1) && (m[33] > 0)
cat(if (refuted) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
