# verify_rogers_2021_financial_knowledge.R
#
# CLAIM UNDER TEST: each shipped item_text is the stem the study printed under the
# very variable code the live IRW table uses.
#
# Two independent links, both re-run here:
#
#   LINK A (code -> wording).  The deposit's own questionnaire, FinalForm.pdf, prints
#   the data's variable code in brackets immediately before every stem and states in a
#   footnote "Codigos das variaveis conforme banco de dados (FinalDataBase.dta) entre
#   colchetes". This script re-downloads that PDF from Mendeley, extracts its text, and
#   checks that each shipped item_text is the string that follows "[Qn]" CHARACTER FOR
#   CHARACTER (whitespace-normalised). A swap of any two item texts breaks this.
#
#   LINK B (code -> live column).  The paper (Souza, Arantes, Rogers & Rogers 2021,
#   Rev. Educ. Mat. 18:e021053) Table 1 publishes a per-item correct-answer rate and SD
#   for Q1..Q13. This script recomputes both from the live IRW table and compares, and
#   additionally checks that no permutation of the 13 codes would fit better.
#
# WHAT THIS DOES NOT ESTABLISH: that the authors' own bracketed labelling inside
# FinalForm.pdf is itself correct -- a mislabel there would satisfy both links. It also
# says nothing about the four multiple-choice alternatives, which are not shipped
# (resp is 0/1 correctness, not the chosen alternative).

suppressMessages(library(irw))

TABLE    <- "rogers_2021_financial_knowledge"
ITEMS_CSV <- file.path(dirname(sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1])),
                       paste0(TABLE, "__items.csv"))
if (!file.exists(ITEMS_CSV)) ITEMS_CSV <- paste0("itemtables/batch_280/", TABLE, "__items.csv")

CODES <- paste0("Q", 1:13)

# ---- published values, paper Table 1 ("Taxa de acerto das questoes de conhecimento
# financeiro"), n = 232 for every item. Percentages as printed.
PUB_MEAN <- c(Q1=68.97, Q2=37.07, Q3=71.98, Q4=79.31, Q5=34.05, Q6=78.02, Q7=82.33,
              Q8=60.34, Q9=64.66, Q10=93.10, Q11=97.84, Q12=72.84, Q13=92.24)
PUB_SD   <- c(Q1=46.36, Q2=48.40, Q3=45.01, Q4=40.60, Q5=47.49, Q6=41.50, Q7=38.23,
              Q8=49.02, Q9=47.91, Q10=25.39, Q11=14.55, Q12=44.57, Q13=26.81)
TOL <- 0.02   # percentage points

norm <- function(x) trimws(gsub("[[:space:]]+", " ", x))

shipped <- read.csv(ITEMS_CSV, stringsAsFactors = FALSE, encoding = "UTF-8")
shipped <- shipped[!duplicated(shipped$item), c("item", "item_text")]
rownames(shipped) <- shipped$item

# ---------------- LINK A ----------------
PDF_URL <- paste0("https://data.mendeley.com/public-files/datasets/fzw7dthwh6/files/",
                  "363be1a6-e216-4a6d-be53-044f34460e17/file_downloaded")
CACHE <- "../.cache/rogers_2021_financial_knowledge/FinalForm.pdf"
if (!file.exists(CACHE)) CACHE <- ".cache/rogers_2021_financial_knowledge/FinalForm.pdf"
pdf <- tempfile(fileext = ".pdf")
got <- tryCatch({ download.file(PDF_URL, pdf, quiet = TRUE, mode = "wb"); file.size(pdf) > 1e5 },
                error = function(e) FALSE)
if (!got && file.exists(CACHE)) { file.copy(CACHE, pdf, overwrite = TRUE)
                                  cat("NOTE: Mendeley fetch failed; using cached FinalForm.pdf\n"); got <- TRUE }
linkA_ok <- 0
if (got) {
  cat(sprintf("FinalForm.pdf md5: %s\n",
              tryCatch(as.character(tools::md5sum(pdf)), error = function(e) "?")))
  txt <- norm(paste(system2("pdftotext", c("-layout", shQuote(pdf), "-"), stdout = TRUE), collapse = " "))
  cat("\n-- LINK A: shipped item_text vs the string printed after [Qn] in FinalForm.pdf --\n")
  for (cd in CODES) {
    m <- regexpr(sprintf("\\[%s\\]\\*? ?", cd), txt)
    after <- if (m > 0) substr(txt, m + attr(m, "match.length"),
                              m + attr(m, "match.length") + nchar(norm(shipped[cd, "item_text"])) - 1) else ""
    ok <- identical(after, norm(shipped[cd, "item_text"]))
    linkA_ok <- linkA_ok + ok
    cat(sprintf("  %-4s %s  %s\n", cd, if (ok) "MATCH" else "DIFF ", substr(after, 1, 62)))
  }
  cat(sprintf("  LINK A: %d/13 exact matches after the bracketed code\n", linkA_ok))
} else cat("LINK A: could not obtain FinalForm.pdf (network) -- unverified\n")

# ---------------- LINK B ----------------
d <- irw::irw_fetch(TABLE)
obs_mean <- 100 * tapply(d$resp, d$item, mean)[CODES]
obs_sd   <- 100 * tapply(d$resp, d$item, stats::sd)[CODES]
cat("\n-- LINK B: paper Table 1 vs live IRW data (correct-answer rate %, SD %) --\n")
cat(sprintf("%-5s %9s %9s %8s %9s %9s %8s\n", "item", "pub.mean", "obs.mean", "diff", "pub.SD", "obs.SD", "diff"))
for (cd in CODES)
  cat(sprintf("%-5s %9.2f %9.2f %8.3f %9.2f %9.2f %8.3f\n", cd,
              PUB_MEAN[cd], obs_mean[cd], obs_mean[cd] - PUB_MEAN[cd],
              PUB_SD[cd], obs_sd[cd], obs_sd[cd] - PUB_SD[cd]))
worst <- max(abs(obs_mean - PUB_MEAN[CODES]), abs(obs_sd - PUB_SD[CODES]))
cat(sprintf("  LINK B: largest deviation %.3f pp over 26 published cells (tolerance %.2f)\n", worst, TOL))

# how distinctive is the fit? compare against random permutations of the code labels
set.seed(1)
perm_worst <- replicate(200, { p <- sample(13); max(abs(obs_mean[p] - PUB_MEAN[CODES])) })
cat(sprintf("  identity permutation deviation %.3f pp vs %.1f pp median over 200 random permutations;\n",
            max(abs(obs_mean - PUB_MEAN[CODES])), median(perm_worst)))
cat(sprintf("  permutations fitting within tolerance: %d/200\n", sum(perm_worst <= TOL)))

cat("\nNOT established: whether the authors' own [Qn] labelling inside FinalForm.pdf is correct;\n",
    "and nothing about the multiple-choice alternatives, which are not shipped (resp is 0/1 correctness).\n", sep = "")

cat(if (linkA_ok == 13 && worst <= TOL) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
