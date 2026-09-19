# Step 5b re-runnable evidence for medvedev_2018_pan (mapping_basis = reconstructed).
#
# THE CLAIM: pan_1..pan_20 are the Watson, Clark & Tellegen (1988) PANAS adjectives
# in canonical printed order -- interested, distressed, excited, upset, strong,
# guilty, scared, hostile, enthusiastic, proud, irritable, alert, ashamed, inspired,
# nervous, determined, attentive, jittery, active, afraid.
#
# WHAT WOULD BREAK IT: nothing in the deposit labels PAN1..PAN20. But the same
# workbook carries the study's OWN scored composites PANPOS, PANNEG and PANNEGR.
# If the canonical valence assignment is right, PANPOS must equal the raw sum of
# the 10 canonical positive positions and PANNEG the raw sum of the 10 negative
# positions, respondent by respondent. Any single item assigned to the wrong
# valence block breaks that identity for almost every respondent.
#
# WHAT THIS DOES NOT ESTABLISH: the composite identity pins each code's VALENCE
# CLASS, not its position within that class. Swapping e.g. pan_1 (interested) with
# pan_3 (excited) would leave PANPOS untouched. Check 3 is the (weaker, semantic)
# corroboration for within-block order and is NOT proof.

suppressMessages(library(irw))

TABLE <- "medvedev_2018_pan"
ADJ <- c("interested","distressed","excited","upset","strong","guilty","scared",
         "hostile","enthusiastic","proud","irritable","alert","ashamed","inspired",
         "nervous","determined","attentive","jittery","active","afraid")
PA <- c(1,3,5,9,10,12,14,16,17,19)   # canonical positive-affect item numbers
NA_ <- c(2,4,6,7,8,11,13,15,18,20)   # canonical negative-affect item numbers

## ---- source workbook (Europe PMC supplementary zip for PMC5985772) ----------
zip_path <- file.path(tempdir(), "medvedev_supp.zip")
url <- "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5985772/supplementaryFiles"
ok <- tryCatch({ download.file(url, zip_path, quiet = TRUE, mode = "wb"); TRUE },
               error = function(e) FALSE)
if (!ok) { cat("could not fetch supplement\nVERDICT: FAIL\n"); quit(status = 0) }
xl <- unzip(zip_path, exdir = tempdir())
xl <- grep("s001[.]xlsx$", xl, value = TRUE)[1]
src <- as.data.frame(readxl::read_excel(xl))

## ---- CHECK 1: composite identity in the SOURCE workbook ---------------------
sPA <- rowSums(src[, paste0("PAN", PA)])
sNA <- rowSums(src[, paste0("PAN", NA_)])
n1 <- sum(!is.na(src$PANPOS)); m1 <- sum(abs(sPA - src$PANPOS) < 1e-9, na.rm = TRUE)
n2 <- sum(!is.na(src$PANNEG)); m2 <- sum(abs(sNA - src$PANNEG) < 1e-9, na.rm = TRUE)
n3 <- sum(!is.na(src$PANNEGR)); m3 <- sum(abs((60 - sNA) - src$PANNEGR) < 1e-9, na.rm = TRUE)
cat("CHECK 1 -- study's own composites vs canonical valence blocks (source workbook)\n")
cat(sprintf("  PANPOS  == sum(PAN %s) : %d / %d respondents exact\n",
            paste(PA, collapse = ","), m1, n1))
cat(sprintf("  PANNEG  == sum(PAN %s) : %d / %d respondents exact\n",
            paste(NA_, collapse = ","), m2, n2))
cat(sprintf("  PANNEGR == 60 - sum(NA block)   : %d / %d respondents exact\n", m3, n3))
c1 <- (m1 == n1 && n1 > 100) && (m2 == n2 && n2 > 100) && (m3 == n3)

## ---- CHECK 2: the LIVE table reproduces those same composites ---------------
## ties the shipped pan_N codes (not just the workbook's PANn) to the valence blocks
d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
names(w) <- sub("^resp[.]", "", names(w))
lPA <- rowSums(w[, paste0("pan_", PA)])
lNA <- rowSums(w[, paste0("pan_", NA_)])
key <- data.frame(id = as.character(w$id), lPA, lNA, stringsAsFactors = FALSE)
ref <- data.frame(id = as.character(src$CASES), PANPOS = src$PANPOS,
                  PANNEG = src$PANNEG, stringsAsFactors = FALSE)
mg <- merge(key, ref, by = "id")
mg <- mg[complete.cases(mg), ]
lm1 <- sum(abs(mg$lPA - mg$PANPOS) < 1e-9); lm2 <- sum(abs(mg$lNA - mg$PANNEG) < 1e-9)
cat("\nCHECK 2 -- same identity computed from the LIVE irw table's pan_N codes\n")
cat(sprintf("  matched respondents: %d\n", nrow(mg)))
cat(sprintf("  sum(pan_%s) == PANPOS : %d / %d\n", "PA", lm1, nrow(mg)))
cat(sprintf("  sum(pan_%s) == PANNEG : %d / %d\n", "NA", lm2, nrow(mg)))
c2 <- nrow(mg) > 100 && lm1 == nrow(mg) && lm2 == nrow(mg)

## ---- CHECK 3: within-block semantic corroboration (NOT proof) ---------------
cm <- cor(w[, paste0("pan_", 1:20)], use = "pairwise.complete.obs")
dimnames(cm) <- list(ADJ, ADJ)
pairs <- function(idx) {
  o <- data.frame()
  for (a in seq_along(idx)) for (b in seq_len(a - 1))
    o <- rbind(o, data.frame(p = sprintf("%s-%s", ADJ[idx[b]], ADJ[idx[a]]),
                             r = cm[idx[b], idx[a]]))
  o[order(-o$r), ][1:3, ]
}
cat("\nCHECK 3 -- top within-block correlations under the shipped labelling\n")
cat("  negative block:\n"); invisible(apply(pairs(NA_), 1, function(r) cat(sprintf("    %-28s %s\n", r[1], format(round(as.numeric(r[2]),3), nsmall=3)))))
cat("  positive block:\n"); invisible(apply(pairs(PA), 1, function(r) cat(sprintf("    %-28s %s\n", r[1], format(round(as.numeric(r[2]),3), nsmall=3)))))
wPA <- mean(cm[PA, PA][upper.tri(diag(10))]); wNA <- mean(cm[NA_, NA_][upper.tri(diag(10))])
bt <- mean(cm[PA, NA_])
cat(sprintf("  mean r within PA %.3f, within NA %.3f, between %.3f\n", wPA, wNA, bt))
c3 <- wPA > 0.2 && wNA > 0.2 && bt < 0

cat("\nNote: checks 1 and 2 pin every code's VALENCE CLASS exactly (a specific\n",
    "20-position partition, 1 of 184756). They do NOT distinguish items within a\n",
    "block -- swapping interested/excited leaves both composites unchanged. Check 3\n",
    "is semantic corroboration of the within-block order (the top pairs are the\n",
    "near-synonyms canonical order predicts), not proof of it. Status is PARTIAL.\n", sep = "")

cat(if (c1 && c2 && c3) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
