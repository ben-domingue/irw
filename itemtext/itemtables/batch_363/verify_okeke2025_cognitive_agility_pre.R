# verify_okeke2025_cognitive_agility_pre.R -- batch_363, Step 5b; adapted from
# references/verify_template.R.
#
# Claim: live item codes ca_pre_1..ca_pre_5 are the deposit xlsx columns A1..A5
# ("Leverage AI Survey.xlsx", figshare 10.6084/m9.figshare.28768874, file 53579603),
# whose statements the deposit's "Leverage SC Survey Instrument.docx" (file 53579606)
# prints against the same codes A1-A5 under "Perceived Cognitive Agility (adapted from
# Podsakoff et al., 2012):" in Section A. No IRW processing script for okeke2025_* is
# in the repo, so the A(k) -> ca_pre_k rename is checked against the data itself.
#
# Route: person-level cell matching. Live id k == source "Participant ID" P%03d (checked
# by three covariates), then for every live item count exact agreement with every one of
# the 32 Likert columns A1..A11, B1..B21. A correct mapping gives 200/200 on the claimed
# column and chance-level agreement elsewhere; any swap among A1..A5, or a shifted block,
# puts the 200 off the claimed cell.

suppressMessages(library(irw))
TABLE <- "okeke2025_cognitive_agility_pre"
CLAIM <- c(ca_pre_1 = "A1", ca_pre_2 = "A2", ca_pre_3 = "A3", ca_pre_4 = "A4", ca_pre_5 = "A5")

d <- as.data.frame(irw::irw_fetch(TABLE))
tf <- tempfile(fileext = ".xlsx")
download.file("https://ndownloader.figshare.com/files/53579603", tf, mode = "wb", quiet = TRUE)
x <- as.data.frame(readxl::read_excel(tf, sheet = "Survey Data"))
x$idn <- as.integer(sub("^P", "", x[["Participant ID"]]))

cv <- unique(d[, c("id", "cov_industry", "cov_role", "cov_years_sc_experience")])
mm <- merge(cv, x, by.x = "id", by.y = "idn")
cov_ok <- c(industry = sum(mm$cov_industry == mm$Industry),
            role     = sum(mm$cov_role == mm$Role),
            years    = sum(mm$cov_years_sc_experience == as.numeric(mm[["Years of SC Experience"]])))
cat(sprintf("live ids: %d; merged: %d; covariate agreement industry %d, role %d, years %d\n",
            length(unique(d$id)), nrow(mm), cov_ok["industry"], cov_ok["role"], cov_ok["years"]))

w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
m <- merge(w, x, by.x = "id", by.y = "idn")
cols <- c(paste0("A", 1:11), paste0("B", 1:21))
agree <- t(sapply(names(CLAIM), function(it)
    sapply(cols, function(a) sum(m[[paste0("resp.", it)]] == as.numeric(m[[a]]), na.rm = TRUE))))
cat("\nagreements, n =", nrow(m), "(rows = live item; Section A columns shown)\n")
print(agree[, paste0("A", 1:11)])

ok <- nrow(mm) == 200 && all(cov_ok == 200) && nrow(m) == 200
cat(sprintf("\n%-9s %-7s %7s %10s %8s\n", "item", "claimed", "agree", "best_other", "n_other"))
for (it in names(CLAIM)) {
    oth <- agree[it, cols != CLAIM[[it]]]
    cat(sprintf("%-9s %-7s %3d/%d %10s %8d\n", it, CLAIM[[it]], agree[it, CLAIM[[it]]], nrow(m),
                names(which.max(oth)), max(oth)))
    ok <- ok && agree[it, CLAIM[[it]]] == nrow(m) && max(oth) < 100
}

# per-item level frequencies, live vs claimed source column
cat("\nfreq 1..5, live | source:\n")
for (it in names(CLAIM)) {
    fl <- tabulate(m[[paste0("resp.", it)]], 5); fs <- tabulate(as.numeric(m[[CLAIM[[it]]]]), 5)
    cat(sprintf("%-9s %s | %s=%s\n", it, paste(fl, collapse = "/"), CLAIM[[it]], paste(fs, collapse = "/")))
    ok <- ok && identical(fl, fs)
}

cat("\nEstablishes the code->column tie for every item against all 32 columns. The column->\n",
    "wording tie rests on the instrument docx printing the same codes A1-A5 as the xlsx\n",
    "headers (a label match, not re-checked here).\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
