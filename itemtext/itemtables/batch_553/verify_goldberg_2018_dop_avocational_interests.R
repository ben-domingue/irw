# verify_goldberg_2018_dop_avocational_interests.R -- Step 5b mapping check (batch_553).
#
# Claim: live item ai_k carries the k-th activity printed in the "Your Personal
# Interests" section of DOP.pdf (Dataverse doi:10.7910/DVN/MH6FCC, datafile
# 3139597), read top-to-bottom, pp.7-15. The .sav's variable labels are bare
# ("Ai_1") and its value labels bare numbers, so the tie is presentation order
# (mapping_basis=paper_order) and needs an external check.
#
# Routes (all read the SHIPPED item_text, not a hard-coded answer):
#  A. Content -> data clustering. Each shipped item_text is assigned to an
#     interest category by keyword rules over its wording only. For every item
#     with a category, the category whose OTHER items it correlates with most
#     (mean r, leave-one-out) should be its own; compared with a random-
#     permutation null (see comment at the route).
#  B. Content -> the study's own scoring syntax. DOP_scales.sps (datafile in
#     the same deposit) groups ai_ codes into 34 named scales (music=ai_1,ai_32..).
#     The keyword category of the text at ai_k must equal (one of) the SPS
#     scale(s) containing ai_k. Shifting the text by +/-1..3 must collapse this.
#  C. Marker pair. The form prints "Wrote poetry" twice (ai_82 and ai_199);
#     those two codes should be each other's highest correlate.
#  D. Nested pairs. "Spent more than an hour thinking about what to wear"
#     implies the "10 minutes" item; "Spent an hour or more in a non-grocery
#     store" implies "10 minutes or more". The implied item should almost never
#     score higher than the implying one, and not vice versa.
#
# What this does NOT establish: order WITHIN a content category (e.g. which of
# the 8 music codes is "Listened to music on the radio" vs "...while working"),
# except where route C/D pins a specific pair. 11 items carry no category.
# Status is therefore PARTIAL.

suppressMessages(library(irw))
TABLE <- "goldberg_2018_dop_avocational_interests"
here <- tryCatch(dirname(normalizePath(sys.frame(1)$ofile)), error = function(e) NULL)
if (is.null(here)) { a <- grep("^--file=", commandArgs(FALSE), value = TRUE)
                     here <- dirname(normalizePath(sub("^--file=", "", a))) }
it <- read.csv(file.path(here, paste0(TABLE, "__items.csv")), stringsAsFactors = FALSE)
txt <- unique(it[, c("item", "item_text")])
txt <- setNames(txt$item_text, txt$item)[paste0("ai_", 1:209)]

rules <- c(  # first match wins
  gambling = "bingo|Gambled|scratch ticket|casino|Bet money",
  creativi = "work of art|Wrote poetry|Acted in a play|Painted|musical instrument|instrument in public|completely new",
  green    = "public transportation|Composted|bicycle to work|environment|both sides|litter|Recycled",
  alone    = "alone|by myself",
  child    = "child|baby sitter",
  socialnt = "social networking|personal web-page|online discussion|instant messaging",
  computng = "^Used a computer$|e-mail|Surfed|computer game|information on the Internet|news on the Internet",
  religion = "religi|Prayed|Bible|blessing|church",
  music    = "\\bmusic\\b|mp3|musical album",
  sports   = "Discussed sports|sports event|athletic event|team sport|basketball|tennis",
  housekp  = "Washed dishes|Made a bed|Cleaned the house|Ironed|Cooked a meal|Baked|Knitted",
  exercise = "running|weights|exercise|Exercised|aerobic|yoga",
  culture  = "public lecture|art exhibition|museum|ballet|an opera|stage play|artistic topic",
  travel   = "Took a trip|sightseeing|travel photographs|hotel|train or plane|cruise",
  garden   = "potted plant|Gardened|yard work|transplanted|flowers|plants for a garden",
  summer   = "picnic|hike|beach|swimming|camping|boating|fishing",
  writing  = "diary|postcard|handwritten letter|thank-you note|photo album|scrap book",
  parties  = "over for dinner|small party|large party|Planned a party|Entertained",
  understa = "news magazine|editorial page|Read poetry|dictionary|encyclopedia|educational channel",
  reading  = "^Read a book$|^Bought a book$|Read in bed",
  financil = "stock|financial|real estate|commodity|retirement",
  politica = "petition|rally|Donated money|Volunteered|town meeting|letter to a newspaper",
  pets     = "pet animal",
  romance  = "love letter|date$|Went dancing|candle|formal dance|formal clothing",
  games    = "jigsaw|Played cards|board game|chess|board or card game",
  fashion  = "what to wear|fashion",
  shopping = "non-grocery|other than groceries|sales ads|Shopped on the web|eBay",
  self_imp = "self-help|Studied|new skill|course of study",
  collect  = "collect",
  food     = "gum|candy|restaurant|food|Ate too much|Ate or drank while driving",
  driving  = "motorcycle|car magazine",
  drinkng  = "beer|whiskey|bar or night club|intoxicated|hangover",
  tv       = "television|TV")
cat_of <- function(s) { for (n in names(rules)) if (grepl(rules[[n]], s)) return(n); NA_character_ }
CAT <- vapply(txt, cat_of, "")
cat("items with a keyword category:", sum(!is.na(CAT)), "/ 209\n")

# ---- Route B: SPS scoring syntax (hard-coded from DOP_scales.sps) ----
SPS <- list(
 music=c(1,32,65,97,130,162,183,208), religion=c(2,33,66,98,131,163,193),
 computng=c(3,34,60,93,132,80), socialnt=c(10,43,75,108,148),
 sports=c(4,35,68,100,133,165), gambling=c(198,37,69,102,134,166),
 housekp=c(5,38,70,103,135,167,191), exercise=c(6,39,71,104,129,168,196),
 culture=c(7,40,72,105,137,169,197), travel=c(8,41,73,106,138,170),
 garden=c(9,42,74,107,139,171), summer=c(11,44,76,109,141,173,194),
 writing=c(12,45,77,110,142,174,82), parties=c(13,46,78,111,143),
 child=c(14,47,79,112,140,175), understa=c(15,48,145,36,101,30),
 reading=c(113,176,200), financil=c(16,56,81,114,146,177),
 creativi=c(17,50,82,115,147,178,201), politica=c(18,51,83,116,144,188,202),
 pets=c(28,52,84,117,149), romance=c(20,53,85,118,150,181),
 games=c(54,86,119,151,182), green=c(22,55,87,120,152,192,204),
 alone=c(23,49,88,121,153,184), food=c(24,57,96,122,154,185,205),
 tv=c(25,58,90,123,155,186,206), driving=c(59,91,124,156),
 drinkng=c(27,62,92,125,157), shopping=c(19,61,99,126,158,179,207),
 fashion=c(29,67,94,127,159), self_imp=c(63,95,128,160,190),
 collect=c(31,64,89,136,161))
sps_of <- lapply(1:209, function(k) names(SPS)[vapply(SPS, function(v) k %in% v, TRUE)])
spsB <- function(cat) { a <- which(lengths(sps_of) > 0)
  c(n = length(a), hit = sum(vapply(a, function(k) isTRUE(cat[k] %in% sps_of[[k]]), TRUE))) }
b0 <- spsB(CAT)
cat(sprintf("\nRoute B: text category agrees with the SPS scale of that code: %d / %d\n", b0["hit"], b0["n"]))
bm <- which(lengths(sps_of) > 0); bm <- bm[!vapply(bm, function(k) isTRUE(CAT[k] %in% sps_of[[k]]), TRUE)]
if (length(bm)) cat("  disagreements:", paste0("ai_", bm, " '", txt[bm], "' text=", CAT[bm], " sps=",
    vapply(sps_of[bm], paste, "", collapse = "/"), collapse = "; "), "\n")
for (s in c(-3:-1, 1:3)) { b <- spsB(CAT[((0:208 + s) %% 209) + 1])
  cat(sprintf("  text shifted %+d: %d / %d\n", s, b["hit"], b["n"])) }

# ---- live data (served from the local irw cache when present) ----
d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
X <- as.matrix(w[, paste0("ai_", 1:209)])
R <- cor(X, use = "pairwise.complete.obs"); diag(R) <- NA
cat(sprintf("\nlive: %d respondents x %d items\n", nrow(X), ncol(X)))

# ---- Route A: content -> data clustering ----
routeA <- function(cat) {
  cats <- unique(na.omit(cat)); hit <- 0; n <- 0; miss <- c()
  for (k in which(!is.na(cat))) {
    m <- vapply(cats, function(cc) { j <- setdiff(which(cat == cc), k)
      if (length(j) < 2) NA else mean(R[k, j], na.rm = TRUE) }, 0)
    if (is.na(m[cat[k]])) next
    n <- n + 1
    if (names(which.max(m)) == cat[k]) hit <- hit + 1 else miss <- c(miss, k)
  }
  list(n = n, hit = hit, miss = miss) }
a0 <- routeA(CAT)
cat(sprintf("\nRoute A: item's highest-mean-r category is its own text category: %d / %d\n", a0$hit, a0$n))
if (length(a0$miss)) cat("  misses:", paste0("ai_", a0$miss, " (", txt[a0$miss], ")", collapse = "; "), "\n")
# Null for route A: random permutations of the text over codes. (A shift is NOT a
# useful null here: route A only asks whether the text-defined GROUPS of codes are
# coherent in the data, and the form cycles its scales in a near-fixed order, so a
# shifted grouping is largely another real scale's grouping. Route B is the
# shift-sensitive route.)
set.seed(553)
sh <- replicate(200, { a <- routeA(sample(CAT)); a$hit / a$n })
cat(sprintf("  random-permutation null (200 draws): median %.3f, max %.3f (observed %.3f)\n",
            median(sh), max(sh), a0$hit / a0$n))

# ---- Route C: duplicated wording ----
p <- which(txt == "Wrote poetry")
cat(sprintf("\nRoute C: 'Wrote poetry' printed at %s; r = %.2f\n",
            paste0("ai_", p, collapse = " & "), R[p[1], p[2]]))
top <- sapply(p, function(k) names(which.max(R[k, ])))
cat("  top correlate of each:", paste(paste0("ai_", p), "->", top, collapse = "; "), "\n")
cOK <- length(p) == 2 && all(top == rev(paste0("ai_", p)))
cat("  next-highest r for ai_", p[1], ": ", sprintf("%.2f", sort(R[p[1], ], decreasing = TRUE)[2]), "\n", sep = "")

# ---- Route D: nested pairs ----
nest <- function(a, b) {  # a implies b: resp_a > resp_b should be rare
  ia <- which(txt == a); ib <- which(txt == b)
  ok <- complete.cases(X[, c(ia, ib)])
  v1 <- mean(X[ok, ia] > X[ok, ib]); v2 <- mean(X[ok, ib] > X[ok, ia])
  cat(sprintf("  ai_%d '%s' > ai_%d '%s': %.3f   reverse: %.3f\n", ia, a, ib, b, v1, v2))
  v1 < 0.05 && v2 > 0.2 }
cat("\nRoute D: implied-item ordering (share of respondents)\n")
d1 <- nest("Spent more than an hour thinking about what to wear",
           "Spent more than 10 minutes thinking about what to wear")
d2 <- nest("Spent an hour or more in a non-grocery store",
           "Spent 10 minutes or more in a non-grocery store")

cat("\nNot established: order within a content category beyond the pinned pairs;\n",
    "11 items have no SPS scale and are covered only by route A where they have a category.\n", sep = "")

pass <- b0["hit"] == b0["n"] && a0$hit / a0$n >= 0.75 && max(sh) < 0.25 && cOK && d1 && d2
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
