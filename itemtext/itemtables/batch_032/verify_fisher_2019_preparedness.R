# verify_fisher_2019_preparedness.R
#
# CLAIM UNDER TEST
#   prepared1 = "first semester of GRADUATE technical course work" item
#   prepared2 = "advanced UNDERGRADUATE technical courses" item
#   resp 1/2/3 = less / as / more prepared than the students in these classes
#
# Source of the claim: PLOS ONE 10.1371/journal.pone.0209279, S1 Data legend
# ("prepared1 = preparation for graduate classes; prepared2 = preparation for
# advanced undergraduate classes") + the Measures sentence giving both stems.
#
# WHAT MAKES IT FALSIFIABLE: the paper's Fig 2 path model prints coefficients
# that DIFFER between the two preparation boxes. If prepared1/prepared2 were
# swapped, every one of the four comparisons below would flip.
#
#   Fig 2, "Prepared for Grad Classes":  Female -0.14, Black -0.17,
#                                        NO path from Latino or Asian;
#                                        -> Perceived Success  0.30
#   Fig 2, "Prepared for UG Classes":    Female -0.17, Black -0.21,
#                                        Latino -0.27, Asian -0.21;
#                                        -> Feel Accepted in STEM  0.15
#
# Plus: the live IRW per-item n (server-side, no export) ties each source
# spreadsheet column to its live item code, since the two columns have
# different numbers of non-missing responses (460 vs 454).

suppressMessages({library(irw); library(readxl)})

TABLE <- "fisher_2019_preparedness"
URL <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0209279.s001"

ok <- TRUE

## ---- 1. live per-item n vs source column n (server-side aggregate) ----
s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
live <- setNames(s$per_item$n, s$per_item$item)

tmp <- file.path(tempdir(), "fisher_s1.xlsx")
utils::download.file(URL, tmp, mode = "wb", quiet = TRUE)
d <- as.data.frame(readxl::read_excel(tmp, sheet = "newdat"))
for (cc in names(d)) d[[cc]] <- suppressWarnings(as.numeric(d[[cc]]))
src <- c(prepared1 = sum(!is.na(d$prepared1)), prepared2 = sum(!is.na(d$prepared2)))

cat("--- source column n vs live item n ---\n")
for (nm in names(src)) {
  cat(sprintf("  %s: xlsx n=%d   live n=%d   %s\n", nm, src[[nm]], live[[nm]],
              ifelse(src[[nm]] == live[[nm]], "match", "MISMATCH")))
  if (src[[nm]] != live[[nm]]) ok <- FALSE
}
if (src[["prepared1"]] == src[["prepared2"]]) {
  cat("  NOTE: column n are equal -- this tie is not discriminating\n"); ok <- FALSE
}

## ---- 2. Fig 2 path pattern, analytic subsample (completed coursework) ----
z <- function(x) as.numeric(scale(x))
sub <- subset(d, courses == 1)
cat(sprintf("\n--- Fig 2 predictors of each preparation item (n analytic = %d) ---\n", nrow(sub)))
co <- list()
for (y in c("prepared1", "prepared2")) {
  m <- lm(as.formula(paste0("z(", y, ") ~ z(female)+z(black)+z(latino)+z(asian)")), sub)
  cf <- summary(m)$coefficients[-1, c(1, 4)]
  co[[y]] <- cf
  cat(sprintf("  %s (n=%d)\n", y, stats::nobs(m)))
  print(round(cf, 3))
}
cat("\n  published (Fig 2): Grad = Female -0.14, Black -0.17, Latino --, Asian --\n")
cat("                     UG   = Female -0.17, Black -0.21, Latino -0.27, Asian -0.21\n")

lat1 <- co$prepared1["z(latino)", ]; asi1 <- co$prepared1["z(asian)", ]
lat2 <- co$prepared2["z(latino)", ]; asi2 <- co$prepared2["z(asian)", ]
test_a <- lat1[2] > .05 && asi1[2] > .05 && lat2[2] < .01 && asi2[2] < .01 &&
          lat2[1] < -0.15 && asi2[1] < -0.10
cat(sprintf("\n  Latino/Asian load on prepared2 only? %s  (prepared1 p: latino %.3f asian %.3f | prepared2 beta/p: latino %.2f/%.4f asian %.2f/%.4f)\n",
            ifelse(test_a, "YES", "NO"), lat1[2], asi1[2], lat2[1], lat2[2], asi2[1], asi2[2]))
if (!test_a) ok <- FALSE

## ---- 3. downstream paths: Grad->Success 0.30, UG->Accepted 0.15 ----
cat("\n--- downstream Fig 2 paths ---\n")
outs <- list(success = "Perceived Success (published 0.30 from GRAD prep)",
             accepted = "Feel Accepted (published 0.15 from UG prep)")
res <- list()
for (y in names(outs)) {
  m <- lm(as.formula(paste0("z(", y, ") ~ z(prepared1)+z(prepared2)")), sub)
  cf <- summary(m)$coefficients[-1, c(1, 4)]
  res[[y]] <- cf
  cat(sprintf("  %s -- %s (n=%d)\n", y, outs[[y]], stats::nobs(m)))
  print(round(cf, 3))
}
test_b <- res$success["z(prepared1)", 1] > res$success["z(prepared2)", 1] &&
          res$success["z(prepared1)", 2] < .01 &&
          res$accepted["z(prepared2)", 1] > res$accepted["z(prepared1)", 1] &&
          res$accepted["z(prepared2)", 2] < .01
cat(sprintf("\n  success carried by prepared1 AND accepted carried by prepared2? %s\n",
            ifelse(test_b, "YES", "NO")))
if (!test_b) ok <- FALSE

## ---- 4. option direction: 1=less ... 3=more prepared ----
# Paper: "Female students ... perceived that they were less prepared for
# advanced undergraduate classes and graduate classes". So female must be
# NEGATIVE on both items if higher resp = more prepared.
f1 <- co$prepared1["z(female)", ]; f2 <- co$prepared2["z(female)", ]
cat(sprintf("\n--- option direction ---\n  female beta: prepared1 %.3f (p=%.4f), prepared2 %.3f (p=%.4f); both negative required for 1=less..3=more\n",
            f1[1], f1[2], f2[1], f2[2]))
test_c <- f1[1] < 0 && f2[1] < 0 && f1[2] < .05 && f2[2] < .05
if (!test_c) ok <- FALSE

cat("\n", if (ok) "VERDICT: PASS" else "VERDICT: FAIL", "\n", sep = "")
