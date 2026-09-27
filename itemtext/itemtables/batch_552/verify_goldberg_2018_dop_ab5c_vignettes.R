# verify_goldberg_2018_dop_ab5c_vignettes.R -- Step 5b mapping check (batch_552).
#
# Claim: live item vig_k carries the k-th vignette printed on DOP.pdf (Dataverse
# doi:10.7910/DVN/MH6FCC, datafile 3139597), read top-to-bottom, pages 1-7. The
# .sav's variable labels are bare ("Vig_1"), so the tie is presentation order
# (mapping_basis=paper_order) and needs an external check.
#
# Route: predicted Big Five domain + direction per vignette, coded from the
# vignette's WORDING ONLY (written down before any correlation was run), tested
# against the same respondents' NEO-PI-R domain scores from the ESCS NEO deposit
# (doi:10.7910/DVN/HE6LJR, NEO_PIR_scales.tab, datafile 3135106). For each vig_k
# the NEO domain with the largest |r| and the sign of that r must match the
# prediction. A shifted or permuted mapping breaks this badly (checked below by
# shifting the text by +/-1..3 positions).
#
# What this does NOT establish: order WITHIN a domain x direction class (~9
# vignettes each, e.g. the E+ vignettes 1, 11, 18, 35, 42, 51, 68, 77). Swaps
# inside a class are invisible to this route, so the status is PARTIAL.

suppressMessages(library(irw))
TABLE <- "goldberg_2018_dop_ab5c_vignettes"

# Prediction per vignette 1..90 from wording. N = neuroticism (+ = more
# anxious/emotional), E, O, A, C. Where the wording is a genuine blend a second
# acceptable domain is given in ALT (AB5C vignettes are facet blends by design).
PRED <- c("E+","A-","C+","N+","O+","E-","C+","O-","A+","N+",   # 1-10
          "E+","C-","E-","A-","N-","A-","C+","E+","C-","O+",   # 11-20
          "A-","C+","E-","C+","O-","A+","C-","C+","A-","N-",   # 21-30
          "O+","E-","N+","O-","E+","A-","C+","N+","O+","N+",   # 31-40
          "C+","E+","N+","C+","O-","C-","A+","C-","N-","O-",   # 41-50
          "E+","E-","O+","A-","N-","A+","C+","O-","A+","N+",   # 51-60
          "A+","C-","E-","C+","O-","A+","C-","E+","C-","O+",   # 61-70
          "A-","C+","C-","A+","N+","O-","E+","N-","O+","E-",   # 71-80
          "A+","C-","N-","O-","N-","C-","N-","C-","O+","E-")   # 81-90
ALT  <- rep("", 90)
ALT[c(9, 11, 24, 28, 33, 54, 56, 64, 67, 73, 74, 78)] <-
    c("C+", "A-", "O+", "E+", "O+", "C-", "E-", "A+", "N+", "E-", "O+", "O-")

d <- irw::irw_fetch(TABLE)          # served from the local irw cache when present
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))

neo <- read.delim("https://dataverse.harvard.edu/api/access/datafile/3135106")
neo <- neo[, c("id", "n", "e", "o", "a", "c")]
m <- merge(w, neo, by = "id")
cat("respondents with both DOP vignettes and NEO-PI-R domains:", nrow(m), "\n\n")

doms <- c(N = "n", E = "e", O = "o", A = "a", C = "c")
R <- sapply(doms, function(x) sapply(paste0("vig_", 1:90), function(v)
    cor(m[[v]], m[[x]], use = "pairwise.complete.obs")))

obs_code <- function(R) apply(R, 1, function(r) {
    k <- which.max(abs(r)); paste0(names(doms)[k], if (r[k] > 0) "+" else "-") })
obs <- obs_code(R)

cat(sprintf("%-7s %-5s %-4s %-5s %6s %6s %6s %6s %6s  %s\n",
            "item", "pred", "alt", "obs", "N", "E", "O", "A", "C", "match"))
hit_strict <- obs == PRED
hit_any <- hit_strict | (ALT != "" & obs == ALT)
for (k in 1:90)
    cat(sprintf("vig_%-3d %-5s %-4s %-5s %6.2f %6.2f %6.2f %6.2f %6.2f  %s\n",
                k, PRED[k], ALT[k], obs[k], R[k, 1], R[k, 2], R[k, 3], R[k, 4],
                R[k, 5], if (hit_strict[k]) "yes" else if (hit_any[k]) "alt" else "NO"))

cat(sprintf("\nstrict matches (primary prediction): %d / 90\n", sum(hit_strict)))
cat(sprintf("matches allowing the listed blend:   %d / 90\n", sum(hit_any)))

# Null: shift the text against the codes. A correct mapping should beat every shift.
cat("\nshifted-mapping controls (strict matches):\n")
shift_hits <- sapply(c(-3:-1, 1:3), function(s) {
    idx <- ((0:89 + s) %% 90) + 1
    h <- sum(obs == PRED[idx]); cat(sprintf("  shift %+d: %d / 90\n", s, h)); h })

# Median |r| of the matched domain -- the signal is not marginal.
cat(sprintf("\nmedian |r| on the predicted domain: %.2f\n",
            median(abs(sapply(1:90, function(k)
                R[k, substr(PRED[k], 1, 1)])))))

cat("\nNot established: order within a domain x direction class (e.g. which of the\n",
    "~9 E+ vignettes is which); status PARTIAL.\n", sep = "")

ok <- sum(hit_any) >= 80 && sum(hit_strict) > max(shift_hits) + 40
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
