## Round-trip check for the cov pilot: long CSV -> matrix equals the package
## original exactly, and a lavaan fit on the IRW copy matches the fit on the
## original. The long -> matrix code here is the prototype of the package helper
## irw_cov2matrix().
##
## Usage: Rscript data/covariance/check_roundtrip.R <dir written by pilot_rpackages.R>

suppressMessages(library(lavaan))
dir <- commandArgs(trailingOnly = TRUE)[1]

cov2matrix <- function(df, group = NULL) {
  if (!is.null(group)) df <- df[df$group == group, ]
  cells <- df[df$stat %in% c("cor", "cov"), ]
  v <- unique(c(cells$var1, cells$var2))
  m <- matrix(NA_real_, length(v), length(v), dimnames = list(v, v))
  m[cbind(cells$var1, cells$var2)] <- cells$value
  m[cbind(cells$var2, cells$var1)] <- cells$value
  sd <- df[df$stat == "sd", ]; mn <- df[df$stat == "mean", ]
  list(matrix = m, type = unique(cells$stat), n = max(cells$n),
       sd = setNames(sd$value, sd$var1), mean = setNames(mn$value, mn$var1))
}

orig <- function(name) {
  e <- new.env()
  if (name %in% c("Harman74.cor", "Harman23.cor", "ability.cov")) return(get(name, "package:datasets")$cov)
  for (p in c("psychTools", "psych")) suppressWarnings(utils::data(list = name, package = p, envir = e))
  if (!exists(name, envir = e)) suppressWarnings(utils::data("Schmid", package = "psych", envir = e))
  get(name, envir = e)
}

pairs <- list(holzinger_1937_bifactor14 = "Holzinger", holzinger_1939_grantwhite24 = "Harman74.cor",
              holzinger_1939_grantwhite9 = "Holzinger.9", thurstone_1941_ability9 = "Thurstone",
              tucker_1958_ability9 = "Tucker", mullen_1939_physical8 = "Harman23.cor",
              burt_1915_emotions11 = "burt", reise_2007_health16 = "Reise",
              smith_1983_ability6 = "ability.cov", chen_2006_hrqol18 = "Chen",
              "bechtoldt_1961_ability17|sample1" = "Bechtoldt.1", "bechtoldt_1961_ability17|sample2" = "Bechtoldt.2",
              "brigham_1932_ability9|boys" = "Thurstone.33", "brigham_1932_ability9|girls" = "Thurstone.33G")
ok <- TRUE
for (key in names(pairs)) {
  parts <- strsplit(key, "|", fixed = TRUE)[[1]]
  df <- read.csv(file.path(dir, paste0(parts[1], ".csv")), stringsAsFactors = FALSE)
  got <- cov2matrix(df, if (length(parts) > 1) parts[2] else NULL)$matrix
  want <- as.matrix(orig(pairs[[key]]))
  d <- max(abs(unname(got) - unname(want)))
  cat(sprintf("%-40s %-14s max|diff| = %g\n", key, pairs[[key]], d))
  if (d != 0) ok <- FALSE
}

## Two fits: the classic three-factor Holzinger-Swineford CFA and a one-factor
## model on a covariance (not correlation) table.
fit_both <- function(model, irw, original, n) {
  a <- lavaan::cfa(model, sample.cov = irw, sample.nobs = n)
  b <- lavaan::cfa(model, sample.cov = original, sample.nobs = n)
  c(chisq_irw = fitMeasures(a, "chisq"), chisq_orig = fitMeasures(b, "chisq"),
    max_est_diff = max(abs(coef(a) - coef(b))))
}
hs <- cov2matrix(read.csv(file.path(dir, "holzinger_1939_grantwhite9.csv"), stringsAsFactors = FALSE))
v <- colnames(hs$matrix)
hs_model <- sprintf("visual =~ %s + %s + %s\n textual =~ %s + %s + %s\n speed =~ %s + %s + %s", v[1], v[2], v[3], v[4], v[5], v[6], v[7], v[8], v[9])
r1 <- fit_both(hs_model, hs$matrix, orig("Holzinger.9"), hs$n); print(round(r1, 8))
ab <- cov2matrix(read.csv(file.path(dir, "smith_1983_ability6.csv"), stringsAsFactors = FALSE))
r2 <- fit_both("g =~ general + picture + blocks + maze + reading + vocab", ab$matrix, orig("ability.cov"), ab$n)
print(round(r2, 8))
if (!ok || r1[["max_est_diff"]] > 1e-6 || r2[["max_est_diff"]] > 1e-6) stop("round trip FAILED")
cat("round trip OK\n")
