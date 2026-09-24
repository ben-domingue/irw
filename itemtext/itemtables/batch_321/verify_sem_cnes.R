# verify_sem_cnes.R -- Step 5b check for sem_cnes (batch_321).
#
# Claim: IRW item codes MBSA2/MBSA7/MBSA8/MBSA9 are the column names of sem::CNES
# (data/cnes.R: item = names(x)[i], resp = match(label, StronglyDisagree..StronglyAgree)),
# and the sem package's CNES.Rd states each statement against that exact column name.
# Independently, the ICPSR 2593 codebook (CES 1997, 3rd ICPSR version, variable list,
# "MAILBACK QUESTIONNAIRE SECTION A") gives the same four variable names terse labels
# that name the same content (hard-coded below).
#
# What would break if texts were swapped:
#  (1) route 9: the per-item x per-level counts of the live table must equal the CRAN
#      .rda's per-column label counts cell for cell, with StronglyDisagree=1..StronglyAgree=4.
#      Every item has a distinct marginal, so this pins each live code to its .rda column
#      and fixes the option direction.
#  (2) route 6 (keying polarity): the two traditionalist statements (MBSA7 "newer
#      lifestyles ... breakdown", MBSA9 "traditional family values") must correlate
#      positively with each other and negatively with the two permissive statements
#      (MBSA2 "more tolerant", MBSA8 "adapt our view of moral behaviour").
suppressMessages(library(irw))

TABLE <- "sem_cnes"
LEVS <- c("StronglyDisagree", "Disagree", "Agree", "StronglyAgree")
ICPSR_LABELS <- c(MBSA2 = "Be More Tolerant People Choose Standards",
                  MBSA7 = "NewerLifestyles Contrib BreakdownSociety",
                  MBSA8 = "Change=Adapt Our View Of Moral Behaviour",
                  MBSA9 = "Fewer Problems=Traditional Family Values")

# --- CRAN source data -------------------------------------------------------
rda <- file.path(tempdir(), "sem", "data", "CNES.rda")
if (!file.exists(rda)) {
  pg <- readLines("https://cran.r-project.org/web/packages/sem/index.html", warn = FALSE)
  tgz <- regmatches(pg, regexpr("sem_[0-9.-]+\\.tar\\.gz", pg))[1]
  dest <- file.path(tempdir(), tgz)
  download.file(paste0("https://cran.r-project.org/src/contrib/", tgz), dest, quiet = TRUE)
  untar(dest, exdir = tempdir())
}
e <- new.env(); load(rda, envir = e); CNES <- e$CNES

# --- live data (4 items x 1529 persons; tiny) --------------------------------
d <- irw::irw_fetch(TABLE)

ok <- TRUE
cat("Route 9: per-item x level counts, CRAN sem::CNES labels vs live resp 1..4\n")
cat(sprintf("%-6s %-26s %-26s %s\n", "item", "CRAN (SD/D/A/SA)", "live (1/2/3/4)", "match"))
for (v in names(ICPSR_LABELS)) {
  src <- as.integer(table(factor(as.character(CNES[[v]]), levels = LEVS)))
  liv <- as.integer(table(factor(d$resp[d$item == v], levels = 1:4)))
  m <- identical(src, liv)
  ok <- ok && m
  cat(sprintf("%-6s %-26s %-26s %s   [ICPSR label: %s]\n", v,
              paste(src, collapse = "/"), paste(liv, collapse = "/"), m, ICPSR_LABELS[[v]]))
}

w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
r <- cor(w[, c("MBSA2", "MBSA7", "MBSA8", "MBSA9")], use = "pairwise")
cat("\nRoute 6: inter-item correlations (live)\n"); print(round(r, 3))
same <- c(r["MBSA7", "MBSA9"], r["MBSA2", "MBSA8"])
cross <- c(r["MBSA2", "MBSA7"], r["MBSA2", "MBSA9"], r["MBSA8", "MBSA7"], r["MBSA8", "MBSA9"])
pol <- all(same > 0) && all(cross < 0)
cat(sprintf("same-polarity pairs r = %s ; cross-polarity pairs r = %s ; polarity %s\n",
            paste(round(same, 3), collapse = ", "), paste(round(cross, 3), collapse = ", "),
            if (pol) "as predicted" else "NOT as predicted"))
ok <- ok && pol

cat("Note: route 6 pins polarity class only ({MBSA7,MBSA9} vs {MBSA2,MBSA8}); it is the\n",
    "CNES.Rd per-column statement (and the ICPSR label) that separates items within a class,\n",
    "and route 9 that proves the live codes are those same columns.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
