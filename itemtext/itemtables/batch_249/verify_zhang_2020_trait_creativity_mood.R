# verify_zhang_2020_trait_creativity_mood.R -- Step 5b check, batch_249.
#
# Claim being verified: 11 of the 12 item codes are the S1 File's own column
# headers (self-describing adjectives / "originality" / "usefulness"), and the
# one inferred assignment is tired.1 = "sleepy". The S1 xlsx header row reads
#   relaxed, tired, happy, stressed, concentrated, tired, active, angry,
#   depressed, interested
# (pandas renames the duplicate to tired.1), while the paper's Methods list the
# ten mood items as
#   relaxed, tired, happy, stressed, concentrated, sleepy, interested, active,
#   angry, depressed
# so the duplicate header sits exactly where the paper puts "sleepy".
#
# This script checks, with numbers:
#   (1) live per-item means equal the S1 columns they are named after, so the
#       live tired.1 IS the 6th mood column of the S1 file (not the 2nd);
#   (2) the S1 header's first six mood positions reproduce the paper's list
#       order exactly, the 6th being the duplicate "tired";
#   (3) the paper's 5 positive / 5 negative split (PA/NA, Table 1: PA
#       55.79/15.93/9-100, NA 34.89/15.74/0-94) reproduces only with BOTH tired
#       columns in NA -- i.e. the paper's "sleepy" is one of the two;
#   (4) corroboration only: the diurnal profile of tired vs tired.1.
# It does NOT decisively separate tired from tired.1 (r = 0.74); that rests on
# position (2). So the verification status is PARTIAL, not VERIFIED.

suppressMessages({ library(irw); library(readxl) })

TABLE <- "zhang_2020_trait_creativity_mood"
URL <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0236987.s001"
tmp <- tempfile(fileext = ".xlsx")
download.file(URL, tmp, mode = "wb", quiet = TRUE)
s1 <- suppressMessages(read_excel(tmp, sheet = 1, .name_repair = "minimal"))
hdr <- trimws(names(s1))
names(s1) <- make.unique(hdr, sep = ".")   # same dedup pandas applies -> tired.1

ok <- TRUE

# (2) header order vs paper list
paper <- c("relaxed","tired","happy","stressed","concentrated","sleepy",
           "interested","active","angry","depressed")
mood_hdr <- hdr[match("relaxed", hdr) + 0:9]
cat("S1 mood headers :", paste(mood_hdr, collapse = ", "), "\n")
cat("paper item list :", paste(paper, collapse = ", "), "\n")
pos_match <- mood_hdr[1:5] == paper[1:5]
cat(sprintf("positions 1-5 identical: %d/5; position 6: header '%s' vs paper '%s'\n",
            sum(pos_match), mood_hdr[6], paper[6]))
cat(sprintf("header set minus paper set: %s; paper set minus header set: %s\n",
            paste(setdiff(mood_hdr, paper), collapse = ","),
            paste(setdiff(paper, mood_hdr), collapse = ",")))
ok <- ok && all(pos_match) && mood_hdr[6] == "tired" &&
      sum(mood_hdr == "tired") == 2 && setequal(setdiff(paper, mood_hdr), "sleepy")

# (1) live vs S1 per-item means
d <- irw::irw_fetch(TABLE)
live <- tapply(d$resp, d$item, mean)
codes <- c("originality","usefulness","relaxed","tired","happy","stressed",
           "concentrated","tired.1","active","angry","depressed","interested")
src <- sapply(codes, function(k) mean(as.numeric(s1[[k]]), na.rm = TRUE))
cat("\nitem          live_mean  S1_mean\n")
for (k in codes) cat(sprintf("%-13s %9.3f %8.3f\n", k, live[k], src[k]))
cat(sprintf("tired (S1 col 2) mean %.3f vs tired.1 (S1 col 6) mean %.3f -- distinct, so the live codes are pinned to columns\n",
            src["tired"], src["tired.1"]))
ok <- ok && max(abs(live[codes] - src)) < 1e-9 && abs(src["tired"] - src["tired.1"]) > 0.5

# (3) PA / NA against Table 1
X <- as.data.frame(lapply(s1[codes[-(1:2)]], as.numeric))
PA <- rowMeans(X[c("relaxed","happy","concentrated","active","interested")])
NA_ <- rowMeans(X[c("tired","stressed","tired.1","angry","depressed")])
cat(sprintf("\nPA  computed %.2f / %.2f / %.1f-%.1f   published 55.79 / 15.93 / 9.0-100.0\n",
            mean(PA), sd(PA), min(PA), max(PA)))
cat(sprintf("NA  computed %.2f / %.2f / %.1f-%.1f   published 34.89 / 15.74 / 0.0-94.0\n",
            mean(NA_), sd(NA_), min(NA_), max(NA_)))
ok <- ok && abs(mean(PA) - 55.79) < .006 && abs(sd(PA) - 15.93) < .006 &&
      abs(mean(NA_) - 34.89) < .006 && abs(sd(NA_) - 15.74) < .006

# (4) corroboration only
cat(sprintf("\ncor(tired, tired.1) = %.2f; exact agreement %.1f%% of records\n",
            cor(X$tired, X$tired.1), 100 * mean(X$tired == X$tired.1)))
hr <- as.integer(substr(trimws(s1[["StartTime"]]), 12, 13))
early <- hr < 11; late <- hr >= 20
cat(sprintf("before 11:00  tired %.2f  tired.1 %.2f (n=%d)\n", mean(X$tired[early]), mean(X$tired.1[early]), sum(early)))
cat(sprintf("after 20:00   tired %.2f  tired.1 %.2f (n=%d)\n", mean(X$tired[late]),  mean(X$tired.1[late]),  sum(late)))
cat("(tired.1 higher in the morning and lower late, consistent with 'sleepy' vs\n",
    " accumulating fatigue -- a weak, corroborating signal only, not proof.)\n", sep = "")

cat("\nDoes NOT establish: which of the two 'tired' headers the study meant as 'sleepy'\n",
    "beyond their position in the file matching the paper's list order.\n", sep = "")
cat(if (isTRUE(ok)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
