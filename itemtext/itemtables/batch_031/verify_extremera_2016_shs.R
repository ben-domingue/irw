# verify_extremera_2016_shs.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST: shs1..shs4 correspond, in order, to items 1..4 of the authors'
# own Spanish SHS ("Adaptación al castellano del Subjective Happiness Scale",
# Extremera & Fernandez-Berrocal, Univ. de Malaga 2014), whose item 4 is the
# reverse-worded one ("Algunas personas suelen ser muy poco felices...") and whose
# printed scoring rule is: "Contrabalancear puntuaciones del item 4 (4r);
# Felicidad subjetiva total = (1+2+3+4r)/4".
#
# The falsifiable prediction: the study's OWN pre-computed happiness score in the
# PLOS S1 SPSS file (variable Happiness_Scores, SPSS label "Felicidad Subjetiva")
# must equal (shs1+shs2+shs3+(8-shs4))/4 -- and must NOT be reproduced by reversing
# any other single item. That is what would break if shs4's text were swapped with
# another item's. Data is read from the PLOS S1 file, which is the file
# data/extremera_2016_unemployment_wellbeing.py melts BY COLUMN NAME into the live
# IRW table, so the codes are identical by construction (no export needed).

SI <- paste0("https://journals.plos.org/plosone/article/file",
             "?type=supplementary&id=10.1371/journal.pone.0163656.s001")
f <- tempfile(fileext = ".sav")
utils::download.file(SI, f, quiet = TRUE, mode = "wb")
d <- haven::read_sav(f)
d <- as.data.frame(lapply(d[, c("shs1","shs2","shs3","shs4","Happiness_Scores")], as.numeric))
cat(sprintf("rows: %d\n\n", nrow(d)))

exact <- function(rev_item) {
  s <- rowSums(sapply(1:4, function(j) {
    x <- d[[paste0("shs", j)]]
    if (j == rev_item) 8 - x else x
  })) / 4
  sum(abs(s - d$Happiness_Scores) < 1e-9, na.rm = TRUE)
}
none <- sum(abs(rowSums(d[, 1:4]) / 4 - d$Happiness_Scores) < 1e-9, na.rm = TRUE)

cat("Rows where the study's own 'Felicidad Subjetiva' score is reproduced:\n")
cat(sprintf("  no item reversed        : %4d / %d\n", none, nrow(d)))
for (j in 1:4)
  cat(sprintf("  shs%d reversed           : %4d / %d\n", j, exact(j), nrow(d)))

n4 <- exact(4); rivals <- max(c(none, exact(1), exact(2), exact(3)))

cat("\nCorrelations with the other three items (raw storage, so the reverse-worded\n",
    "item must be the negatively-correlating one):\n", sep = "")
cm <- cor(d[, 1:4], use = "complete.obs")
print(round(cm, 3))

cat("\nMidpoint (resp = 4) mass per item -- secondary, semantic (route 8): the\n",
    "peer-comparison item ('Comparado con la mayoria de la gente que me rodea')\n",
    "should pile up on 'the same as others':\n", sep = "")
for (j in 1:4)
  cat(sprintf("  shs%d: %.1f%% at 4, mean %.2f, sd %.2f\n", j,
              100 * mean(d[[j]] == 4, na.rm = TRUE),
              mean(d[[j]], na.rm = TRUE), sd(d[[j]], na.rm = TRUE)))

cat("\nWhat this does NOT establish: it pins shs4 to questionnaire item 4 and pins\n",
    "shs1/shs2/shs3 as the non-reversed block, but a sum over those three is\n",
    "invariant to permuting them, so the shs1-vs-shs2-vs-shs3 assignment rests on\n",
    "the trailing digit of the authors' own column names, not on these numbers.\n",
    "Status is therefore PARTIAL, not VERIFIED.\n", sep = "")

ok <- n4 >= 0.99 * nrow(d) && rivals < 0.30 * nrow(d) &&
      all(cm[4, 1:3] < 0) && all(cm[1:3, 1:3][upper.tri(matrix(0, 3, 3))] > 0)
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
