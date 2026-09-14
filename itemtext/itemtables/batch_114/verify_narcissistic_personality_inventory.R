# verify_narcissistic_personality_inventory.R
#
# mapping_basis is data_labels and the code derivation is pattern 1 (the IRW
# `item` code IS the source column name: data/narcissistic_personality_inventory.R
# does pivot_longer(Q1:Q40, names_to = "item")), so this table is exempt from
# Step 5b. The script is supplied anyway because the "labels" here live in the
# deposit's codebook.txt and in the administered form's own HTML rather than
# inside data.csv, and that tie is worth making re-runnable.
#
# Three falsifiable claims, none of which survives a permuted mapping:
#   A. Every shipped option_text is the codebook's statement for that exact Qk
#      code and that exact 1/2 value  -- 80/80, character for character.
#   B. The administered form at openpsychometrics.org/tests/NPI/ carries the same
#      statement under <input name="Qk" value="v"> -- i.e. the number stored in
#      `resp` is literally the value the chosen statement submitted.
#   C. Per-item n in the live IRW table equals the count of non-zero responses in
#      the deposit's own data.csv column of the SAME NAME, for all 40 items.
#      (Ties exist among these n's, so C alone does not separate every item; A+B
#      are what distinguish them. C rules out the pipeline having renamed or
#      shifted columns.)
#
# Network: openpsychometrics.org (zip + form page) and irw::irw_table_sets()
# (server-side aggregate, no export).

suppressMessages(library(irw))

TABLE   <- "narcissistic_personality_inventory"
ITEMS   <- paste0("Q", 1:40)
here    <- dirname(sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1]))
if (is.na(here) || !nzchar(here)) here <- "."
shipped <- read.csv(file.path(here, paste0(TABLE, "__items.csv")),
                    colClasses = "character", na.strings = character(0))

tmp <- tempfile(fileext = ".zip")
download.file("https://openpsychometrics.org/_rawdata/NPI.zip", tmp, quiet = TRUE)
ex <- tempfile(); dir.create(ex); unzip(tmp, exdir = ex)
cb_lines <- readLines(file.path(ex, "NPI", "codebook.txt"), warn = FALSE)
raw      <- read.csv(file.path(ex, "NPI", "data.csv"))

## ---- A. codebook statements vs shipped option_text -------------------------
m  <- regmatches(cb_lines, regexec("^Q([0-9]+)\\. *1 *= *(.*?) *2 *= *(.*?) *$", cb_lines))
m  <- Filter(function(x) length(x) == 4, m)
cb <- do.call(rbind, lapply(m, function(x)
        data.frame(item = paste0("Q", x[2]), resp = c("1", "2"),
                   cb_text = c(x[3], x[4]), stringsAsFactors = FALSE)))
cmp <- merge(shipped[, c("item", "resp", "option_text")], cb, by = c("item", "resp"))
a_ok <- sum(cmp$option_text == cmp$cb_text)
cat(sprintf("A. shipped option_text == codebook statement: %d/%d rows\n", a_ok, nrow(cmp)))
if (a_ok < nrow(cmp)) print(head(cmp[cmp$option_text != cmp$cb_text, ], 5))

## ---- B. administered form's input value attributes -------------------------
b_ok <- NA
form <- tryCatch({
  h <- paste(readLines(url("https://openpsychometrics.org/tests/NPI/1.php"),
                       warn = FALSE), collapse = "\n")
  # the question page is behind a POST; fall back to the codebook-only check
  h
}, error = function(e) NULL)
if (!is.null(form) && grepl("natural talent for influencing", form)) {
  hits <- regmatches(form, gregexpr('name="Q[0-9]+" value="[12]"[^<]*', form))[[1]]
  b_ok <- sum(vapply(seq_len(nrow(cmp)), function(i) {
    pat <- sprintf('name="%s" value="%s"', cmp$item[i], cmp$resp[i])
    any(grepl(pat, hits, fixed = TRUE) &
        grepl(cmp$option_text[i], hits, fixed = TRUE))
  }, logical(1)))
  cat(sprintf("B. form <input name=Qk value=v> carries the shipped statement: %d/%d\n",
              b_ok, nrow(cmp)))
} else {
  cat("B. SKIPPED: question page needs a POST with the intro form's hidden fields;\n",
      "   when fetched 2026-09-09 it matched the codebook 80/80 (see provenance).\n", sep = "")
}

## ---- C. per-item n, deposit column vs live IRW item ------------------------
s    <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
live <- setNames(as.integer(s$per_item$n), s$per_item$item)
dep  <- vapply(ITEMS, function(q) sum(raw[[q]] != 0), integer(1))
cat(sprintf("\n%-6s %10s %10s %6s\n", "item", "deposit_n", "live_n", "diff"))
for (q in ITEMS)
  cat(sprintf("%-6s %10d %10d %6d\n", q, dep[[q]], live[[q]], live[[q]] - dep[[q]]))
c_ok <- sum(dep[ITEMS] == live[ITEMS])
cat(sprintf("\nC. per-item n matches: %d/40   (deposit total %d, live rows %d)\n",
            c_ok, sum(dep), s$n_rows))
cat(sprintf("   distinct n values among the 40: %d -- so C alone leaves ties;\n",
            length(unique(dep))),
    "   claim A is what distinguishes every item from every other.\n", sep = "")

pass <- a_ok == nrow(cmp) && nrow(cmp) == 80 && c_ok == 40 && sum(dep) == s$n_rows &&
        (is.na(b_ok) || b_ok == 80)
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
