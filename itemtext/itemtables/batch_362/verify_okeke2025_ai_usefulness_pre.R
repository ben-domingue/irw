# verify_okeke2025_ai_usefulness_pre.R -- adapted from references/verify_template.R.
#
# Claim: live item codes aiu_pre_1, aiu_pre_2, aiu_pre_3 are the deposit's xlsx columns
# A9, A10, A11 ("Leverage AI Survey.xlsx", figshare 10.6084/m9.figshare.28768874, file
# 53579603), which the deposit's "Leverage SC Survey Instrument.docx" (file 53579606) ties
# to the three shipped statements under the same codes A9/A10/A11. No processing script is
# in the repo, so the A9->aiu_pre_1 rename is checked here against the data itself.
#
# Route: person-level cell matching. Live id k == source "Participant ID" P%03d (checked by
# three covariates), then for every live item count agreements with every Section A column
# A1..A11. A correct mapping gives 200/200 on the claimed column and chance (~40-60) on the
# rest; any swap among A9/A10/A11 would put the 200 off the diagonal.

suppressMessages(library(irw))
TABLE <- "okeke2025_ai_usefulness_pre"
CLAIM <- c(aiu_pre_1 = "A9", aiu_pre_2 = "A10", aiu_pre_3 = "A11")

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
cat(sprintf("id linkage: %d persons merged; covariate agreement industry %d, role %d, years %d\n",
            nrow(mm), cov_ok["industry"], cov_ok["role"], cov_ok["years"]))

w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
m <- merge(w, x, by.x = "id", by.y = "idn")
cols <- paste0("A", 1:11)
agree <- t(sapply(names(CLAIM), function(it)
    sapply(cols, function(a) sum(m[[paste0("resp.", it)]] == as.numeric(m[[a]]), na.rm = TRUE))))
cat("\nagreements (rows = live item, cols = source column), n =", nrow(m), "\n")
print(agree)

best <- apply(agree, 1, function(r) cols[which.max(r)])
diag_ok <- all(best == CLAIM) && all(agree[cbind(names(CLAIM), CLAIM)] == nrow(m))
offmax <- max(agree[, setdiff(cols, CLAIM)], agree["aiu_pre_1", c("A10","A11")],
              agree["aiu_pre_2", c("A9","A11")], agree["aiu_pre_3", c("A9","A10")])
cat(sprintf("\nclaimed cells: %s; best off-claim agreement: %d of %d\n",
            paste(sprintf("%s=%s %d", names(CLAIM), CLAIM, agree[cbind(names(CLAIM), CLAIM)]), collapse = ", "),
            offmax, nrow(m)))
cat("Establishes the code->column tie for every item. The column->wording tie rests on the\n",
    "instrument docx printing the same codes A9-A11 as the xlsx headers (not re-checked here).\n", sep = "")
ok <- nrow(mm) == 200 && all(cov_ok == 200) && diag_ok && offmax < 100
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
