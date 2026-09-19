# verify_ieswriting_molloy_2022.R
#
# This table is BLOCKED, not shipped. There is no {table}__items.csv, so there is
# no item_text<->item or option_text<->resp mapping to verify, and this script does
# NOT pretend to check one. What it does re-run is the verdict that produced the
# block: that the only publication of this instrument's administered wording is
# released under a non-commercial Creative Commons licence.
#
# It is self-contained: it fetches the ETS deposit's own README.md and LICENSE.md
# and asserts the NC clause is present, then asserts no item text was written.
# PASS here means "the block still holds", not "a mapping reproduced".

TABLE <- "ieswriting_molloy_2022"
BASE  <- "https://raw.githubusercontent.com/EducationalTestingService/ies-writing-achievement-study-data/master/"

get_text <- function(path) {
    u <- paste0(BASE, path)
    x <- tryCatch(paste(readLines(url(u), warn = FALSE), collapse = "\n"),
                  error = function(e) NA_character_)
    x
}

readme  <- get_text("README.md")
license <- get_text("LICENSE.md")

if (is.na(readme) || is.na(license)) {
    cat("could not fetch the deposit over the network; falling back to the cached copies\n")
    cdir <- file.path("..", "..", ".cache", TABLE)
    if (is.na(readme)  && file.exists(file.path(cdir, "README.md")))
        readme  <- paste(readLines(file.path(cdir, "README.md"),  warn = FALSE), collapse = "\n")
    if (is.na(license) && file.exists(file.path(cdir, "LICENSE.md")))
        license <- paste(readLines(file.path(cdir, "LICENSE.md"), warn = FALSE), collapse = "\n")
}

# The clause the block rests on, quoted from README.md's License section.
CLAUSE <- "Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License"
hit_readme  <- !is.na(readme)  && grepl(CLAUSE, readme,  fixed = TRUE)
hit_license <- !is.na(license) && grepl("Attribution-NonCommercial-ShareAlike 4.0 International",
                                        license, fixed = TRUE)
hit_nc_link <- !is.na(readme)  && grepl("creativecommons.org/licenses/by-nc-sa/4.0/", readme, fixed = TRUE)

cat(sprintf("%-58s %s\n", "README.md states CC BY-NC-SA 4.0:",  hit_readme))
cat(sprintf("%-58s %s\n", "README.md links licenses/by-nc-sa/4.0/:", hit_nc_link))
cat(sprintf("%-58s %s\n", "LICENSE.md is the CC BY-NC-SA 4.0 deed:", hit_license))
if (hit_readme) {
    ln <- grep(CLAUSE, strsplit(readme, "\n", fixed = TRUE)[[1]], fixed = TRUE, value = TRUE)[1]
    cat("\nquoted clause:\n  ", trimws(gsub("<[^>]*>", "", ln)), "\n\n", sep = "")
}

# The wording that would have been shipped lives inside that same deposit:
# docs/student_data_columns.csv (Description column) and
# docs/surveys/writing_attitudes_survey.pdf. Nothing here is outside the licence.
no_items <- !file.exists(sprintf("%s__items.csv", TABLE))
cat(sprintf("%-58s %s\n", "no __items.csv shipped for this table:", no_items))

cat("\nWhat this does NOT establish: nothing about any item<->text mapping. None was\n",
    "built. Had the table shipped it would have been mapping_basis=data_labels, since\n",
    "data/iewsriting_molloy_2022.r melts the source columns by name and the deposit's\n",
    "docs/student_data_columns.csv describes each of those column names -- but that\n",
    "exemption is unexercised, and is asserted nowhere in this run.\n", sep = "")

ok <- (hit_readme || hit_license || hit_nc_link) && no_items
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
