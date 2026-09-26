# verify_celik_2026_academic_motivation.R -- Step 5b mapping check (batch_453).
#
# Code derivation: data/celik_2026_motivation_distance_ed.py assigns ams01..ams28
# POSITIONALLY, in column order, to the 28 TEZ_412VERI.xlsx columns whose header
# starts "NEDEN OKULA", with id = row index. Each such header carries the item's
# full Turkish wording in [brackets] (Google Forms grid export).
#
# The check, which is what would break if two item texts were swapped:
#   1. Re-derive the table from the raw deposit xlsx and compare to the live table
#      cell for cell (id x item). Every one of 11,536 cells must agree.
#   2. Confirm no two source columns are identical across the 412 respondents, so
#      the cell match distinguishes every item from every other item.
#   3. Confirm the shipped item_text for amsNN is the bracketed header text of the
#      NN-th "NEDEN OKULA" column (the header diff owed for positional codes).
#   4. Content sanity: the AMS amotivation items (5, 12, 19, 26) should be the four
#      lowest-mean items in a student sample.

suppressMessages({ library(irw); library(readxl); library(jsonlite) })

TABLE <- "celik_2026_academic_motivation"
here <- tryCatch(dirname(normalizePath(sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1]))),
                 error = function(e) ".")
items_csv <- file.path(here, paste0(TABLE, "__items.csv"))

# --- raw deposit (Mendeley 10.17632/hwp4wsb549, CC BY 4.0) ---
meta <- fromJSON("https://data.mendeley.com/public-api/datasets/hwp4wsb549")
f <- meta$files
url <- f$content_details$download_url[f$filename == "TEZ_412VERI.xlsx"]
tmp <- tempfile(fileext = ".xlsx")
download.file(url, tmp, mode = "wb", quiet = TRUE)
x <- read_excel(tmp, .name_repair = "minimal")
names(x) <- trimws(names(x))
ams_cols <- names(x)[startsWith(names(x), "NEDEN OKULA")]
cat("source AMS columns:", length(ams_cols), "\n")
src <- as.data.frame(x[, ams_cols])
codes <- sprintf("ams%02d", seq_along(ams_cols))
names(src) <- codes
src$id <- seq_len(nrow(src))
long <- reshape(src, direction = "long", varying = codes, v.names = "resp",
                timevar = "item", times = codes, idvar = "id")
long <- long[!is.na(long$resp), c("id", "item", "resp")]

# --- live ---
live <- irw::irw_fetch(TABLE)[, c("id", "item", "resp")]
m <- merge(long, live, by = c("id", "item"), all = TRUE, suffixes = c("_src", "_live"))
n_both <- sum(!is.na(m$resp_src) & !is.na(m$resp_live))
n_mis <- sum(m$resp_src != m$resp_live, na.rm = TRUE) + sum(is.na(m$resp_src) != is.na(m$resp_live))
cat(sprintf("cells: source %d, live %d, matched %d, disagreeing/unpaired %d\n",
            nrow(long), nrow(live), n_both, n_mis))

# --- distinctness of source columns ---
mat <- as.matrix(src[, codes])
dup_pairs <- 0
for (i in 1:27) for (j in (i + 1):28) if (identical(mat[, i], mat[, j])) dup_pairs <- dup_pairs + 1
min_diff <- min(sapply(1:27, function(i) sapply((i + 1):28, function(j) sum(mat[, i] != mat[, j], na.rm = TRUE)) |> unlist()) |> unlist())
cat(sprintf("identical source column pairs: %d; fewest differing respondents between any two columns: %d\n",
            dup_pairs, min_diff))

# --- header diff: shipped item_text vs bracketed header at that position ---
it <- read.csv(items_csv, stringsAsFactors = FALSE, encoding = "UTF-8")
shipped <- tapply(it$item_text, it$item, function(v) unique(v))
hdr <- sub("^.*\\[(.*)\\]$", "\\1", ams_cols)
names(hdr) <- codes
hd_ok <- sum(shipped[codes] == hdr[codes])
cat(sprintf("header diff: %d/28 shipped item_text identical to header bracket text at that position\n", hd_ok))

# --- content sanity ---
mu <- tapply(live$resp, live$item, mean)
cat("per-item live means:\n"); print(round(mu[codes], 3))
low4 <- names(sort(mu))[1:4]
amot <- c("ams05", "ams12", "ams19", "ams26")
cat("four lowest-mean items:", paste(low4, collapse = ", "),
    "| AMS amotivation key items:", paste(amot, collapse = ", "), "\n")

cat("Does NOT establish: that the study's Google Form showed the Ek.1 scale anchors ",
    "(shipped for 1/4/7 from Unal-Karaguven 2012); the deposit carries no anchors.\n", sep = "")

ok <- n_mis == 0 && n_both == nrow(live) && dup_pairs == 0 && hd_ok == 28 && setequal(low4, amot)
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
