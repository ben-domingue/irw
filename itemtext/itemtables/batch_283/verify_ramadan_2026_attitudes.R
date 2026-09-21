# Step 5b mapping verification: ramadan_2026_attitudes (batch_283)
# Route: response-frequency fingerprint matching, live vs raw deposit column.
# Verifies the MAPPING: each live item code must reproduce the 1-5 response-count
# vector of the raw source column of the SAME name, and of no other column.
suppressMessages(library(irw))
tab <- "ramadan_2026_attitudes"; pre <- "AS"; k <- 8
d <- irw_fetch(tab)
raw <- read.csv(".cache/ramadan_2026_applied_practice/data.csv", check.names = FALSE)
items <- paste0(pre, seq_len(k))
M <- matrix(FALSE, k, k, dimnames = list(items, items))
for (i in seq_along(items)) {
  liv <- as.integer(table(factor(d$resp[d$item == items[i]], levels = 1:5)))
  for (j in seq_along(items)) {
    r <- raw[[items[j]]]; r <- r[!is.na(r)]
    M[i, j] <- identical(liv, as.integer(table(factor(r, levels = 1:5))))
  }
  r <- raw[[items[i]]]; r <- r[!is.na(r)]
  cat(items[i], " live:", paste(liv, collapse = "/"),
      " raw:", paste(as.integer(table(factor(r, levels = 1:5))), collapse = "/"),
      " n:", sum(liv), "\n")
}
print(M)
ok <- all(diag(M)) && sum(M) == k   # identity: self-match, and no cross-match
cat("VERDICT:", if (ok) "PASS" else "FAIL", "\n")
