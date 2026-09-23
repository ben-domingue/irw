# Verification for audit_BrummerHoffman_2021 (#2228, batch_303).
#
# SOURCE. OSF deposit osf.io/p8j2v (Brummer & Hoffman 2021). The decisive file
# is not the questionnaire but the deposit's own processing script,
# 'Deidentified data set/Question_framing_data_processing.Rmd': it renames the
# three raw columns from their Portuguese question text and then car::recode()s
# every option label to the score it becomes. That is a complete, explicit
# option -> resp key, so nothing here is inferred.
#
# Route 1: the three rename targets are the live item codes, and the Portuguese
#   question text in those renames is what item_text ships.
# Route 2: the recode calls reproduce the shipped option_text/resp pairs
#   exactly -- including 'Nao bebo' and '1 ou 2' both scoring 0, which ship as
#   a single joined label because irw-validate blocks two labels on one resp.
# Route 3: the English questionnaire contradicts the Portuguese on the third
#   item (it prints the options descending). Print both, and show the data side
#   with the Portuguese: binge correlates POSITIVELY with the other two.
source(".claude/skills/irw-auto-itemtext/scripts/verify_cache.R")

rmd <- cached_source(".cache/batch_303/audit_processing.Rmd",
       "https://osf.io/download/9yde5/")
enp <- cached_source(".cache/batch_303/audit_q_en.pdf",
       "https://osf.io/download/a4mds/")
d <- as.data.frame(irw::irw_fetch("audit_BrummerHoffman_2021"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item); d$resp <- as.numeric(d$resp)
items <- shipped_items("audit_BrummerHoffman_2021", "itemtables/batch_303/audit_BrummerHoffman_2021__items.csv")
rl <- readLines(rmd, warn = FALSE, encoding = "UTF-8")

cat("=== Route 1: the renames name the items and carry the question text ===\n")
rn <- grep("rename\\(mydata,\\s*audit_", rl, value = TRUE)
rn <- unique(sub(".*rename\\(mydata,\\s*", "", rn))
code <- sub("=.*", "", rn)
qtext <- trimws(gsub("`", "", sub("^[^=]*=", "", sub("\\)\\s*$", "", rn))))
for (i in seq_along(code)) cat(sprintf("  %-20s <- %s\n", code[i], qtext[i]))
sh <- unique(items[, c("item", "item_text")])
key <- setNames(qtext, code)
r1 <- setequal(code, unique(d$item)) && setequal(code, sh$item) &&
      all(mapply(function(a, b) startsWith(a, b), sh$item_text, key[sh$item]))
cat(sprintf("  -> codes match the live set and each item_text opens with its\n"))
cat(sprintf("     administered Portuguese question: %s\n", r1))

cat("\n=== Route 2: the recode calls are the option -> resp key ===\n")
rc <- grep("car::recode\\(audit_", rl, value = TRUE)
rc <- rc[!duplicated(sub(".*recode\\((audit_[a-z_]+).*", "\\1", rc))]
ok <- logical(0)
for (line in rc) {
    v <- sub(".*recode\\((audit_[a-z_]+),.*", "\\1", line)
    body <- sub('.*"(.*)".*', "\\1", line)
    pairs <- trimws(strsplit(body, ";")[[1]])
    pairs <- pairs[nzchar(pairs)]
    lab <- trimws(gsub("'", "", sub("=.*", "", pairs)))
    val <- as.numeric(trimws(sub(".*=", "", pairs)))
    cat(sprintf("  %s\n", v))
    for (i in seq_along(lab)) cat(sprintf("      %-32s -> %d\n", lab[i], val[i]))
    want <- data.frame(option_text = lab, resp = val, stringsAsFactors = FALSE)
    want <- stats::aggregate(option_text ~ resp, data = want,
                             FUN = function(z) paste(z, collapse = " / "))
    got <- items[items$item == v, c("resp", "option_text")]
    got <- got[order(got$resp), ]; want <- want[order(want$resp), ]
    ok <- c(ok, isTRUE(all.equal(got$option_text, want$option_text)) &&
                isTRUE(all.equal(as.numeric(got$resp), as.numeric(want$resp))))
}
r2 <- length(ok) == 3 && all(ok)
cat(sprintf("  -> shipped option_text/resp pairs reproduce all three recodes: %s\n", r2))
nd <- items[items$item == "audit_number_drinks", ]
cat(sprintf("  audit_number_drinks ships %d option rows for %d resp levels;\n",
            nrow(nd), length(unique(nd$resp))))
cat(sprintf("     resp 0 reads '%s' because the recode sends both\n",
            nd$option_text[nd$resp == 0]))
cat("     administered options there.\n")

cat("\n=== Route 3: the English questionnaire disagrees; the data do not ===\n")
cat("  Questionnaire_English.pdf, item 176, prints:\n")
cat("    1. Daily or almost daily / 2. Weekly / 3. Monthly / 4. Less than monthly / 5. Never\n")
cat("  The administered Portuguese (item 222) and the recode both run Nunca -> 0 (ascending).\n")
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
m <- as.matrix(w[, -1]); colnames(m) <- sub("^resp\\.", "", colnames(m))
cm <- stats::cor(m, use = "pairwise.complete.obs")
print(round(cm, 3))
r3 <- cm["audit_binge", "audit_frequency"] > 0 && cm["audit_binge", "audit_number_drinks"] > 0
cat(sprintf("  -> binge keys with the other two, as the Portuguese says: %s\n", r3))

cat("\n=== What this does NOT establish ===\n")
cat("  The standard-drink image that accompanies the second item is described\n")
cat("  in brackets, not reproduced. The English text is the study's own\n")
cat("  questionnaire, which is a loose rather than literal translation.\n")
cat("\nVERDICT:", if (r1 && r2 && r3) "PASS" else "FAIL", "\n")
