# verify_tian2026_digital_competence.R -- Step 5b mapping check, batch_188.
#
# CLAIM: live item dc_N is the Nth item column (spreadsheet column 10+N, header
# "N.<Chinese stem>") of the study's own deposit, BMC Psychology Supplementary
# Material 1 (figshare 10.6084/m9.figshare.32564154.v1, 40359_2026_4551_MOESM1_ESM.xlsx),
# so item_text for dc_N is that header with its "N." prefix stripped.
#
# ROUTE: re-derivation, cell for cell. Join live rows to the deposit on id (= the
# sheet's first column) and, for every live item x every deposit item column, count
# the respondents whose values agree. A correct mapping puts 764/764 on the diagonal
# and strictly less everywhere else; any swap, shift or permutation breaks it.
# Secondary: the paper's Table 2 domain sum-score means/SDs (N = 764), which pin
# domain membership (q1-5, q6-8, q9-18, q19-24, q25-29) but not order within a domain.

suppressMessages(library(irw))
TABLE <- "tian2026_digital_competence"
URL <- "https://ndownloader.figshare.com/files/65236020"

xl <- tempfile(fileext = ".xlsx")
download.file(URL, xl, mode = "wb", quiet = TRUE)
src <- as.data.frame(readxl::read_excel(xl, sheet = 1))
hdr <- names(src)[11:39]
cat("deposit rows:", nrow(src), "| item headers:", length(hdr), "\n")
hdr_num <- as.integer(sub("^([0-9]+)\\..*$", "\\1", hdr))
cat("header leading numbers == column position 1..29:", identical(hdr_num, 1:29), "\n")

d <- as.data.frame(irw::irw_fetch(TABLE))
src_id <- as.character(src[[1]])
cat("live ids:", length(unique(d$id)), "| matched to deposit ids:",
    sum(unique(as.character(d$id)) %in% src_id), "\n\n")

agree <- matrix(NA_integer_, 29, 29)
for (i in 1:29) {
    li <- d[d$item == paste0("dc_", i), ]
    rows <- match(as.character(li$id), src_id)
    for (j in 1:29) agree[i, j] <- sum(as.numeric(src[[10 + j]][rows]) == li$resp, na.rm = TRUE)
}
n_item <- as.integer(table(d$item)[paste0("dc_", 1:29)])
diag_ok <- all(diag(agree) == n_item)
offmax <- sapply(1:29, function(i) max(agree[i, -i]))
cat(sprintf("%-6s %6s %10s %14s %10s\n", "item", "n", "own_col", "best_other_col", "best_col"))
for (i in 1:29)
    cat(sprintf("%-6s %6d %10d %14d %10d\n", paste0("dc_", i), n_item[i], agree[i, i],
                offmax[i], which.max(agree[i, ])))
cat(sprintf("\ndiagonal exact for all 29: %s | max off-diagonal agreement: %d of %d\n",
            diag_ok, max(offmax), max(n_item)))
uniq <- all(offmax < n_item)

# Secondary: paper Table 2 domain sum scores (M, SD), N = 764.
pub <- list(awareness = list(1:5, 21.760, 2.880), skills = list(6:8, 12.530, 2.000),
            application = list(9:18, 41.520, 6.430), responsibility = list(19:24, 25.840, 3.430),
            development = list(25:29, 21.220, 3.010))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
cat("\ndomain       published M (SD)   live M (SD)\n")
dom_ok <- TRUE
for (nm in names(pub)) {
    s <- rowSums(w[, paste0("resp.dc_", pub[[nm]][[1]])])
    cat(sprintf("%-14s %7.3f (%5.3f)   %7.3f (%5.3f)\n", nm, pub[[nm]][[2]], pub[[nm]][[3]], mean(s), sd(s)))
    if (abs(mean(s) - pub[[nm]][[2]]) > 0.05 || abs(sd(s) - pub[[nm]][[3]]) > 0.05) dom_ok <- FALSE
}
cat("domain sums within 0.05 of Table 2:", dom_ok, "\n")
cat("Note: the domain check alone cannot order items within a domain; the cell-for-cell\n",
    "diagonal is what distinguishes every item from every other.\n", sep = "")

cat(if (diag_ok && uniq && identical(hdr_num, 1:29)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
