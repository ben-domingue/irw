##Choice-based conjoint on decorative "firefly" garden/indoor lights (Akaro Fireflies) from
##Deschepper, T. (2026). Conjoint Survey Results Akaro Fireflies With Non Chosen Options [Data set].
##Zenodo. https://doi.org/10.5281/zenodo.20754003 (concept DOI 10.5281/zenodo.20754002), CC BY 4.0.
##No article. File read: "Conjoint results with nonchosen.xlsx" (Sheet1, 184 rows, 34 columns).
##Usage: Rscript deschepper_2026.R <dir holding the xlsx, named f.xlsx or by its original name> <output dir>
##
##184 Dutch-speaking respondents (survey April-May 2026), 10 tasks, each a pair "Optie A" / "Optie B" plus
##"Geen van beide" (neither). Fixed design: every respondent saw the same 10 pairs in the same order (the
##option texts are identical across respondents, 20 distinct profiles). 5 attributes shown as a one-line
##text: number of lights (5/10/20 lampjes), effect (statisch licht / subtiel flikkerend / realistisch
##effect), panel (zichtbaar / gedeeltelijk verborgen / volledig verborgen), installation (handmatige
##installatie / eenvoudige installatie / volledig automatisch), price (EUR 19/29/39/49).
##Outcome: choice = the option picked in "Keuze k" (column 9+2(k-1)); "Geen van beide" = neither, so
##choice = 0 on both profiles (opt-out). Question wording is not in the deposit (the survey is Dutch).
##Columns "Keuze k - niet gekozen" hold the other option (or, after a "neither", both options as
##"Beide getoond, geen gekozen"); they were used only to verify the reconstructed design.
##Inferred / caveats (the reason the earlier ledger entry for the version DOI was held):
##  * In the chosen-answer text the installation phrase is missing in 879 of 1,304 chosen options
##    (never in the non-chosen text): the survey-label export dropped it. The 20 profiles are fixed and
##    the other four attributes identify each profile uniquely within its task, so the installation level
##    is taken from the fully worded occurrences of the same task/position (checked: exactly one full
##    wording per task and option; all full occurrences agree). That respondents saw the installation
##    attribute in these cases is inferred (it is in every non-chosen text and in the title of the study).
##  * "realistisch vuurvlieg-effect" (tasks 2, 3) and "realistisch effect" (tasks 4, 6, 7, 8, 10) are
##    stored as one level, "realistisch effect" (same effect level, two wordings in the export).
##  * Task number = column order (display order not documented); profile = Optie A/B label.
##Dropped: platform columns (start/finish/modification times, E-mail "anonymous", Naam empty), and the
##non-chosen text columns. Respondent covariates kept: cov_gender (Man = male, Vrouw = female, from the
##Dutch answer text), cov_age_group (answer text), cov_housing (answer text, "Wat is je huidige
##woonsituatie?"), cov_use_place ("Waar zou je dit product gebruiken?", answer text),
##cov_purchase_likelihood (1-7, "Hoe waarschijnlijk is het dat je dit product zou kopen?", asked once
##about the product, not per profile), cov_value_atmosphere / cov_value_sustainability / cov_value_ease
##("... is belangrijk voor mij", 1 = totaal niet mee eens, 7 = volledig mee eens). No survey weight.
##Rows with no outcome: none. Every respondent answered all 10 tasks.
invisible(Sys.setlocale("LC_ALL", "C.UTF-8"))
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- list.files(raw, pattern = "\\.xlsx$", full.names = TRUE)[1]
x <- as.data.table(read_excel(f))
ch <- as.matrix(x[, 10 + 2 * (0:9), with = FALSE])
nc <- as.matrix(x[, 11 + 2 * (0:9), with = FALSE])
parse_opt <- function(s) {                      # "Optie A: 10 lampjes, ..., EUR29" -> list
  s <- trimws(gsub("\u00a0", " ", s, fixed = TRUE)); m <- regmatches(s, regexec("^Optie ([AB]): (.*)$", s))[[1]]
  p <- trimws(strsplit(m[3], ",")[[1]])
  p[2] <- sub("^realistisch vuurvlieg-effect$", "realistisch effect", p[2])
  if (length(p) == 5) list(letter = m[2], lamps = p[1], effect = p[2], panel = p[3], install = p[4], price = p[5])
  else if (length(p) == 4) list(letter = m[2], lamps = p[1], effect = p[2], panel = p[3], install = NA_character_, price = p[4])
  else stop("unexpected option text: ", s)
}
## design: every option text seen, from chosen cells, non-chosen cells and 'both shown' cells
design <- list()
for (t in 1:10) {
  txt <- c(ch[, t], nc[, t])
  parts <- unlist(lapply(txt, function(s) {
    if (startsWith(s, "Geen van beide")) return(NULL)
    if (startsWith(s, "Beide getoond")) return(trimws(strsplit(sub("^.*— ", "", s), "\\|")[[1]]))
    s
  }))
  o <- rbindlist(lapply(unique(parts), function(s) as.data.table(parse_opt(s))))
  full <- o[!is.na(install)]
  stopifnot(nrow(full) == 2, setequal(full$letter, c("A", "B")))   # one full wording per option
  for (l in c("A", "B")) {                      # every partial wording agrees with the full one
    p <- o[letter == l & is.na(install)]
    fl <- full[letter == l]
    if (nrow(p)) stopifnot(all(p$lamps == fl$lamps, p$effect == fl$effect, p$panel == fl$panel, p$price == fl$price))
  }
  design[[t]] <- full
}
rows <- list()
for (i in seq_len(nrow(x))) for (t in 1:10) {
  c0 <- ch[i, t]
  chosen <- if (startsWith(c0, "Geen van beide")) NA_character_ else parse_opt(c0)$letter
  if (!is.na(chosen)) stopifnot(identical(parse_opt(c0)[c("lamps", "effect", "panel", "price")],
                                          as.list(design[[t]][letter == chosen, .(lamps, effect, panel, price)])[c("lamps", "effect", "panel", "price")]))
  for (l in c("A", "B")) {
    dd <- design[[t]][letter == l]
    rows[[length(rows) + 1]] <- data.table(id = i, task = t, profile = match(l, c("A", "B")),
      choice = as.integer(!is.na(chosen) && chosen == l),
      attr_lights = dd$lamps, attr_effect = dd$effect, attr_panel = dd$panel, attr_installation = dd$install, attr_price = dd$price)
  }
}
d <- rbindlist(rows)
cv <- data.table(id = seq_len(nrow(x)),
  cov_gender = c(Man = "male", Vrouw = "female")[x[["Wat is je geslacht?"]]],
  cov_age_group = x[[8]], cov_housing = x[[9]], cov_use_place = x[[31]],
  cov_purchase_likelihood = as.integer(x[[30]]), cov_value_atmosphere = as.integer(x[[32]]),
  cov_value_sustainability = as.integer(x[[33]]), cov_value_ease = as.integer(x[[34]]))
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
stopifnot(d[, sum(choice), .(id, task)][, all(V1 <= 1)], !anyNA(d[, .SD, .SDcols = patterns("^attr_")]))
fwrite(d, file.path(out, "deschepper_2026_firefly_lights.csv"))
