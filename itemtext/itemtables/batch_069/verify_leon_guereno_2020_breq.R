# verify_leon_guereno_2020_breq.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST: item code BREQ<n> in the live IRW table carries the wording
# printed at position <n> of the official 23-item Spanish BREQ-3 form
# (Gonzalez-Cutre, Sicilia y Fernandez, 2010; https://cid.umh.es/files/2010/12/breq-3.pdf).
#
# FALSIFIABLE PREDICTION: that form publishes a fixed item-number -> subscale key.
# The study's own SPSS deposit (PLOS S1 File) carries six precomputed subscale MEAN
# columns. If the shipped numbering is right, the row-mean of the LIVE items named by
# the published key must reproduce each deposit aggregate exactly, for every
# respondent. Any item assigned across a subscale boundary breaks this immediately.
#
# What this does NOT establish: it cannot separate items WITHIN a subscale
# (e.g. BREQ4 / BREQ12 / BREQ18 / BREQ22 are interchangeable as far as the
# aggregates are concerned). Within-subscale order rests on the printed form's own
# numbering, not on this test. Hence status PARTIAL.

suppressMessages({library(irw); library(haven)})

TABLE <- "leon_guereno_2020_breq"
SI <- paste0("https://journals.plos.org/plosone/article/file",
             "?type=supplementary&id=10.1371/journal.pone.0231628.s001")

# Published subscale key, official Spanish BREQ-3 form (verbatim from the PDF footer).
KEY <- list(
  Intrinsic    = c(4, 12, 18, 22),   # Regulacion intrinseca
  Integrated   = c(5, 10, 15, 20),   # Regulacion integrada
  Identified   = c(3, 9, 17),        # Regulacion identificada
  Introjected  = c(2, 8, 16, 21),    # Regulacion introyectada
  External     = c(1, 7, 13, 19),    # Regulacion externa
  Amotivation  = c(6, 11, 14, 23)    # Desmotivacion
)
TOL <- 1e-9

tmp <- file.path(tempdir(), "leon_guereno_s001.sav")
if (!file.exists(tmp))
  download.file(SI, tmp, quiet = TRUE, mode = "wb",
                headers = c("User-Agent" = "IRW-itemtext/1.0"))
sav <- haven::read_sav(tmp)
sav$id <- as.character(sav$Code)

d <- irw::irw_fetch(TABLE)
wide <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
                idvar = "id", timevar = "item", direction = "wide")
names(wide) <- sub("^resp\\.", "", names(wide))
wide$id <- as.character(wide$id)
m <- merge(wide, as.data.frame(sav[, c("id", names(KEY))]), by = "id")
cat(sprintf("live respondents matched to the SPSS deposit by id: %d\n\n", nrow(m)))
stopifnot(nrow(m) > 1000)

cat(sprintf("%-12s %-22s %10s %10s %12s\n",
            "subscale", "live items (key)", "dep.mean", "live mean", "max|diff|"))
worst <- 0
for (s in names(KEY)) {
  cols <- paste0("BREQ", KEY[[s]])
  live <- rowMeans(m[, cols])
  dep  <- as.numeric(m[[s]])
  ok   <- !is.na(dep) & !is.na(live)
  dif  <- max(abs(live[ok] - dep[ok]))
  worst <- max(worst, dif)
  cat(sprintf("%-12s %-22s %10.4f %10.4f %12.2e\n", s,
              paste(KEY[[s]], collapse = ","), mean(dep[ok]), mean(live[ok]), dif))
}
cat(sprintf("\nlargest per-respondent deviation across all 6 subscales: %.3e (tol %.0e)\n",
            worst, TOL))
cat(sprintf("all 23 items are used exactly once by the key: %s\n",
            identical(as.integer(sort(unlist(KEY, use.names = FALSE))), 1:23)))

# Direction of the resp coding (option_text axis): recreational runners must be
# high on intrinsic and low on amotivation if 1=least true .. 5=most true.
mi <- mean(rowMeans(m[, paste0("BREQ", KEY$Intrinsic)]), na.rm = TRUE)
ma <- mean(rowMeans(m[, paste0("BREQ", KEY$Amotivation)]), na.rm = TRUE)
cat(sprintf("\nresp direction check: intrinsic mean %.2f vs amotivation mean %.2f",
            mi, ma))
cat(sprintf(" -- %s\n", if (mi > ma) "ascending (1 = least true) as shipped" else "INVERTED"))

cat("\nNot established by this test: order WITHIN a subscale.\n")
cat(if (worst <= TOL && mi > ma) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
