# Verification for gcbs_brotherton_2013 (batch_455).
#
# SOURCE. openpsychometrics.org/_rawdata/GCBS.zip (codebook.txt + data.csv) and the
# administered online form, openpsychometrics.org/tests/GCBS/1.php (fetched
# 2026-09-25). The IRW script (data/gcbs_brotherton_2013.R) pivots starts_with("Q")
# with names_to = "item": the IRW code IS the source column name, no rename.
#
# Route A (label tie, distinguishes every item): on the administered form each
#   statement sits in the same <tr> as <input type="radio" name="Qk">, so the
#   form's field name ties code to text. Independently, codebook.txt states
#   "question numbers match to items in TABLE A1 of Brotherton, et. al. 2013".
#   Both ties must agree for all 15 items, and shipped item_text must equal the
#   form text.
# Route B (code derivation): live per-item resp distributions must equal the raw
#   data.csv column of the same name cell for cell (proves no rename/shift).
# Route C (structure, PARTIAL on its own): GCBS facets per Brotherton 2013
#   Table 3 -- GM 1,6,11; MG 2,7,12; ET 3,8,13; PW 4,9,14; CI 5,10,15. Items
#   should correlate most with their own facet.
#
# Run from itemtext/.
suppressMessages(library(irw))
TABLE <- "gcbs_brotherton_2013"
CACHE <- ".cache/gcbs_brotherton_2013"
dir.create(CACHE, showWarnings = FALSE, recursive = TRUE)

items <- read.csv("itemtables/batch_455/gcbs_brotherton_2013__items.csv",
                  stringsAsFactors = FALSE, na.strings = "NA")
d <- as.data.frame(irw::irw_fetch(TABLE))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)

# ---- Route A ---------------------------------------------------------------
form_f <- file.path(CACHE, "q1.html")
if (!file.exists(form_f)) {
  # the question page is POST-only and needs the landing page's session fields
  ck <- tempfile()
  idx <- tempfile()
  system2("curl", c("-sS", "-c", ck, "-b", ck, "-A", "Mozilla/5.0", "-o", idx,
                    "https://openpsychometrics.org/tests/GCBS/"))
  h <- paste(readLines(idx, warn = FALSE), collapse = "\n")
  u <- sub('.*name="unqid" value="([^"]*)".*', "\\1", h)
  s <- sub('.*name="seconds" value="([^"]*)".*', "\\1", h)
  system2("curl", c("-sS", "-c", ck, "-b", ck, "-A", "Mozilla/5.0", "-X", "POST",
                    "--data", shQuote(sprintf("unqid=%s&seconds=%s&w=1200&h=800", u, s)),
                    "-o", form_f, "https://openpsychometrics.org/tests/GCBS/1.php"))
}
h <- paste(readLines(form_f, warn = FALSE), collapse = "\n")
m <- regmatches(h, gregexpr('<tr[^>]*><td>[^<]*</td>\\s*<td align="center"><input type="hidden" name="E[0-9]+"[^>]*/><input type="radio" name="Q[0-9]+"', h))[[1]]
form_txt  <- sub('<tr[^>]*><td>([^<]*)</td>.*', "\\1", m)
form_code <- sub('.*name="(Q[0-9]+)"$', "\\1", m)
names(form_txt) <- form_code
cat("=== Route A: administered form field names vs shipped item_text ===\n")
cat(sprintf("  form rows parsed: %d\n", length(m)))
sh <- unique(items[, c("item", "item_text")])
eqA <- sh$item_text == form_txt[sh$item]
cat(sprintf("  shipped item_text identical to the form text beside name=Qk: %d/%d\n",
            sum(eqA, na.rm = TRUE), nrow(sh)))

# Brotherton et al. 2013 Table A1 (PMC3659314), items 1-15 as printed.
A1 <- c(
 "The government is involved in the murder of innocent citizens and/or well-known public figures, and keeps this a secret",
 "The power held by heads of state is second to that of small unknown groups who really control world politics",
 "Secret organizations communicate with extraterrestrials, but keep this fact from the public",
 "The spread of certain viruses and/or diseases is the result of the deliberate, concealed efforts of some organization",
 "Groups of scientists manipulate, fabricate, or suppress evidence in order to deceive the public",
 "The government permits or perpetrates acts of terrorism on its own soil, disguising its involvement",
 "A small, secret group of people is responsible for making all major world decisions, such as going to war",
 "Evidence of alien contact is being concealed from the public",
 "Technology with mind-control capacities is used on people without their knowledge",
 "New and advanced technology which would harm current industry is being suppressed",
 "The government uses people as patsies to hide its involvement in criminal activity",
 "Certain significant events have been the result of the activity of a small group who secretly manipulate world events",
 "Some UFO sightings and rumors are planned or staged in order to distract the public from real alien contact",
 "Experiments involving new drugs or technologies are routinely carried out on the public without their knowledge or consent",
 "A lot of important information is deliberately concealed from the public out of self-interest")
cat("\n  codebook: 'question numbers match to items in TABLE A1' -> Qk must be A1 item k.\n")
cat("  For each form item, the nearest Table A1 item (edit distance):\n")
dist <- adist(tolower(form_txt[paste0("Q", 1:15)]), tolower(A1))
okA2 <- TRUE
for (k in 1:15) {
  best <- which.min(dist[k, ]); second <- sort(dist[k, ])[2]
  cat(sprintf("    Q%-3d nearest A1 #%-2d dist %3d (next-nearest %3d)%s\n",
              k, best, dist[k, best], second, if (best != k) "   <-- DISAGREES" else ""))
  if (best != k) okA2 <- FALSE
}
cat("  Nonzero distances are the form's deviations from Table A1: a trailing period on\n",
    "  every item, Q7 'all major decisions' (A1: 'all major world decisions'), Q13\n",
    "  'rumours' (A1: 'rumors'). The shipped text is the form's.\n", sep = "")
rA <- all(eqA) && length(m) == 15 && okA2

# ---- Route B ---------------------------------------------------------------
raw_f <- file.path(CACHE, "data", "data.csv")
if (!file.exists(raw_f)) {
  z <- file.path(CACHE, "GCBS.zip")
  download.file("https://openpsychometrics.org/_rawdata/GCBS.zip", z, quiet = TRUE)
  unzip(z, exdir = CACHE)
}
raw <- read.csv(raw_f)
cat("\n=== Route B: live per-item distribution vs raw data.csv column of that name ===\n")
okB <- logical(15)
for (k in 1:15) {
  q <- paste0("Q", k)
  lv <- table(factor(d$resp[d$item == q], levels = 0:5))
  rw <- table(factor(raw[[q]], levels = 0:5))
  okB[k] <- identical(as.integer(lv), as.integer(rw))
  cat(sprintf("  %-4s live %s | raw %s %s\n", q, paste(lv, collapse = "/"),
              paste(rw, collapse = "/"), if (okB[k]) "" else "<-- DIFFERS"))
}
cat(sprintf("  identical (counts of 0/1/2/3/4/5): %d/15\n", sum(okB)))
cat(sprintf("  resp=0 cells (no radio button selected; not an offered option): %d\n",
            sum(d$resp == 0)))
rB <- all(okB)

# ---- Route C ---------------------------------------------------------------
cat("\n=== Route C: facet block structure (Brotherton 2013 Table 3) ===\n")
w <- reshape(d[d$resp > 0, c("id", "item", "resp")], idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
R <- cor(w[, paste0("Q", 1:15)], use = "pairwise.complete.obs")
g <- list(GM = c(1, 6, 11), MG = c(2, 7, 12), ET = c(3, 8, 13), PW = c(4, 9, 14), CI = c(5, 10, 15))
hits <- 0
for (k in 1:15) {
  own <- names(g)[sapply(g, function(v) k %in% v)]
  mc <- sapply(g, function(v) mean(R[paste0("Q", k), paste0("Q", setdiff(v, k))]))
  best <- names(which.max(mc)); hits <- hits + (best == own)
  cat(sprintf("  Q%-3d own %s %.2f  best %s %.2f %s\n", k, own, mc[own], best, max(mc),
              if (best != own) "<-- rival" else ""))
}
cat(sprintf("  %d/15 items correlate most with their own facet\n", hits))
rC <- hits >= 12

cat("\n=== What this does NOT establish ===\n")
cat("  Route C alone pins facet membership, not order within a facet, and the CI\n",
    "  facet (Q5, Q10, Q15) is the weakest block here (paper CFA loadings 0.69-0.75,\n",
    "  not markedly lower than the other facets). Route A is what\n",
    "  distinguishes every item. The form was fetched in 2026; the data were collected\n",
    "  in 2016, and no archived 2016 copy of the question page could be retrieved,\n",
    "  so the form wording is the current administration, corroborated item for item by\n",
    "  the codebook's Table A1 tie.\n", sep = "")
cat(if (rA && rB && rC) "\nVERDICT: PASS\n" else "\nVERDICT: FAIL\n")
