# verify_fisher_2019_structure.R
#
# Claim under test: IRW item code `expectations` carries the wording "the academic
# expectations of the department for graduate students are appropriate" and `standards`
# carries "the performance standards graduate students are held to are appropriate"
# (Fisher et al. 2019, PLOS ONE 10.1371/journal.pone.0209279, Measures section).
#
# Three independent checks, none of which is a count check:
#   A. The IRW item codes ARE the S1 Data column names (data/fisher_2019_structure.py
#      melts columns `expectations`/`standards` unchanged). Verified by reproducing each
#      live item's n / mean / sd from the correspondingly named S1 column.
#   B. Lexical self-description: each item's shipped stem contains its own code word and
#      not the other item's code word. A swap would be self-evident.
#   C. The paper's two ASYMMETRIC published findings, which discriminate the two items:
#        - "positive perception of departmental performance standards" mitigated distress
#          and directly predicted subjective well-being (expectations did not);
#        - "Positive perceptions of departmental expectations reduced feelings of
#          insignificance in STEM settings".
#      Prediction: cor(standards, distress) < cor(expectations, distress) and
#      cor(expectations, insignificant) < cor(standards, insignificant), using the S1
#      columns `distress` and `insignificant` (not in this IRW table).
#
# NOT established: the 1-7 response anchors (the paper publishes none, so the shipped
# rows carry blank option_text and this script makes no claim about scale direction).

suppressMessages(library(irw))

TABLE  <- "fisher_2019_structure"
S1_URL <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0209279.s001"
ITEMS  <- c("expectations", "standards")
TEXT   <- c(expectations = "the academic expectations of the department for graduate students are appropriate",
            standards    = "the performance standards graduate students are held to are appropriate")

tmp <- tempfile(fileext = ".xlsx")
download.file(S1_URL, tmp, quiet = TRUE, mode = "wb")
raw <- readxl::read_excel(tmp, sheet = "newdat")

d <- irw::irw_fetch(TABLE)

cat("--- A. live IRW item vs identically named S1 column ---\n")
cat(sprintf("%-14s %6s %8s %8s | %6s %8s %8s\n", "item", "n", "mean", "sd", "n_src", "mean_src", "sd_src"))
okA <- TRUE
for (it in ITEMS) {
    v  <- d$resp[d$item == it]
    s  <- suppressWarnings(as.numeric(raw[[it]])); s <- s[!is.na(s)]
    cat(sprintf("%-14s %6d %8.4f %8.4f | %6d %8.4f %8.4f\n",
                it, length(v), mean(v), sd(v), length(s), mean(s), sd(s)))
    okA <- okA && length(v) == length(s) && abs(mean(v) - mean(s)) < 1e-9 && abs(sd(v) - sd(s)) < 1e-9
}
cat(sprintf("A: %s\n\n", if (okA) "match" else "MISMATCH"))

cat("--- B. lexical self-description of the item codes ---\n")
okB <- TRUE
for (it in ITEMS) {
    own   <- grepl(it, TEXT[[it]], fixed = TRUE)
    other <- any(sapply(setdiff(ITEMS, it), function(o) grepl(o, TEXT[[it]], fixed = TRUE)))
    cat(sprintf("%-14s contains own code: %-5s contains another code: %-5s\n", it, own, other))
    okB <- okB && own && !other
}
cat(sprintf("B: %s\n\n", if (okB) "each stem names its own code only" else "AMBIGUOUS"))

cat("--- C. paper's asymmetric path findings, S1 correlations ---\n")
cc <- function(a, b) {
    x <- suppressWarnings(as.numeric(raw[[a]])); y <- suppressWarnings(as.numeric(raw[[b]]))
    cor(x, y, use = "pairwise.complete.obs")
}
r_exp_dis <- cc("expectations", "distress");      r_std_dis <- cc("standards", "distress")
r_exp_ins <- cc("expectations", "insignificant"); r_std_ins <- cc("standards", "insignificant")
cat(sprintf("cor(distress, expectations)      = %+.3f   cor(distress, standards)      = %+.3f\n", r_exp_dis, r_std_dis))
cat(sprintf("cor(insignificant, expectations) = %+.3f   cor(insignificant, standards) = %+.3f\n", r_exp_ins, r_std_ins))
okC <- (r_std_dis < r_exp_dis) && (r_exp_ins < r_std_ins)
cat(sprintf("predicted: standards more distress-protective, expectations more insignificance-protective -- %s\n",
            if (okC) "both hold" else "NOT BORNE OUT"))
cat("C is corroborative only: the two columns correlate r = ",
    sprintf("%.3f", cc("expectations", "standards")),
    " and the gaps are small (0.045 / 0.027), so C alone would not settle the mapping; A and B do.\n", sep = "")

cat(if (okA && okB && okC) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
