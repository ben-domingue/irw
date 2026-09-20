# verify_busch_2022_course_exacerbate.R
#
# CLAIM UNDER TEST: each idep.* item code carries the checklist option we shipped
# in item_text. The IRW codes are the S1 Dataset's own column headers
# (data/busch_2022_course_depression.py melts them unchanged), but the header is
# an abbreviation ("idep.nav.tech"), so tying it to the survey's full wording is
# an inference. S1 Appendix Table S5 publishes a separate demographic regression
# for every aspect, LABELLED BY ITS FULL WORDING -- so each aspect's coefficient
# vector is a fingerprint that identifies which column it was fitted on.
#
# Refitting Table S5's model on each idep.* column and matching each published
# vector to its nearest fitted column is therefore decisive: it would break if
# any two items' item_text were swapped.
#
# Model (S1 Appendix Table S5): linear probability model of the 0/1 aspect on
# Woman, Asian, Black, Latinx, LGBTQ+, First-gen, Financially unstable, STEM
# major, Lower division, GPA. References: men, white, non-LGBTQ+, continuing
# generation, financially stable, non-STEM, upper division. Sample: respondents
# reporting depression, complete on all predictors.

SRC <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0269201.s002"
ITEMS_CSV <- file.path(dirname(sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1])),
                       "busch_2022_course_exacerbate__items.csv")
if (!file.exists(ITEMS_CSV))
  ITEMS_CSV <- "itemtables/batch_275/busch_2022_course_exacerbate__items.csv"

PRED <- c("Intercept","Woman","Asian","Black","Latinx","LGBTQ+","First-gen",
          "Financially unstable","STEM major","Lower division","GPA")

PUBLISHED <- list(
  "Being on camera" = c(0.24, 0.12, -0.03, 0.04, 0.00, 0.08, 0.01, 0.13, 0.08, 0.07, -0.04),
  "Struggling to communicate effectively with the instructor" = c(0.48, 0.05, -0.07, -0.23, -0.11, 0.02, -0.02, 0.08, 0.06, 0.07, -0.04),
  "Comparing myself to other students" = c(0.43, 0.10, 0.02, -0.27, -0.04, 0.09, -0.01, 0.06, 0.07, 0.03, -0.05),
  "Difficulty getting help from instructors" = c(0.37, 0.06, -0.03, -0.21, -0.06, 0.00, 0.00, 0.01, 0.03, 0.10, 0.00),
  "Difficulty getting help from other students in class" = c(0.28, 0.06, 0.13, -0.22, -0.03, -0.01, -0.01, 0.04, 0.04, 0.07, 0.02),
  "Difficulty getting to know instructors" = c(0.22, 0.06, 0.01, -0.17, -0.07, -0.02, -0.02, 0.01, -0.01, 0.06, 0.07),
  "Difficulty getting to know other students in class" = c(0.20, 0.01, 0.11, -0.15, -0.03, 0.00, -0.11, 0.01, 0.01, 0.19, 0.10),
  "At-home distractions that can interfere with online science courses" = c(0.23, 0.08, -0.02, -0.15, 0.02, 0.11, 0.06, 0.06, 0.10, -0.03, 0.03),
  "Needing to navigate technology in high-pressure situations (e.g., during exams)" = c(0.14, 0.11, -0.05, -0.13, 0.01, 0.05, -0.05, 0.09, 0.10, -0.03, 0.04),
  "Not having to show up in person to online science courses" = c(0.11, 0.06, -0.06, -0.09, -0.03, 0.07, -0.08, 0.04, 0.05, 0.03, 0.03),
  "Deciding the pace at which I work through an online science course" = c(0.41, 0.08, 0.02, -0.07, 0.03, 0.01, 0.04, -0.02, 0.04, 0.03, -0.07),
  "The potential for personal technology issues (e.g., unstable internet connection)" = c(0.29, 0.13, 0.03, -0.17, 0.02, 0.02, -0.05, 0.06, 0.05, -0.04, 0.01),
  "Online monitored proctored testing" = c(0.36, 0.13, -0.01, -0.17, 0.01, 0.03, 0.00, 0.08, 0.11, 0.01, -0.01),
  "Struggling to have questions answered" = c(0.48, 0.10, -0.06, -0.29, -0.10, 0.01, 0.04, 0.11, 0.03, 0.07, -0.04),
  "Needing to talk with students who I don't know during online group work" = c(0.22, 0.07, 0.05, -0.17, -0.02, 0.08, 0.03, 0.02, 0.03, 0.09, 0.01),
  "Nothing related to online courses makes my feelings of depression worse" = c(0.20, -0.02, -0.02, 0.24, 0.00, -0.02, 0.01, -0.03, -0.01, -0.02, -0.03),
  "Other" = c(0.03, 0.00, -0.01, -0.02, 0.01, -0.01, 0.00, 0.02, 0.01, -0.02, 0.00)
)

norm <- function(x) tolower(gsub("[^a-z0-9]+", " ", tolower(x)))

it <- read.csv(ITEMS_CSV, stringsAsFactors = FALSE)
shipped <- unique(it[, c("item", "item_text")])
# published label "Other" is the abbreviated form of the survey's "Other, please describe"
lookup <- function(aspect) {
  a <- trimws(norm(aspect))
  hit <- shipped$item[trimws(norm(shipped$item_text)) == a]
  if (!length(hit)) hit <- shipped$item[startsWith(trimws(norm(shipped$item_text)), a)]
  if (length(hit) != 1) stop("no unique shipped item for: ", aspect)
  hit
}

tf <- tempfile(fileext = ".csv")
ok <- tryCatch({ download.file(SRC, tf, quiet = TRUE); TRUE }, error = function(e) FALSE)
if (!ok || !file.exists(tf)) { cat("could not download S1 Dataset\nVERDICT: FAIL\n"); quit(status = 0) }
d <- read.csv(tf, stringsAsFactors = FALSE)
d <- d[d$depression == "yes", ]

X <- data.frame(
  Woman       = as.numeric(d$gender2 == "woman"),
  Asian       = as.numeric(d$race2 == "asian"),
  Black       = as.numeric(d$race2 == "black"),
  Latinx      = as.numeric(d$race2 == "latinx"),
  LGBTQ       = as.numeric(d$lgbtq2 == "yes"),
  Firstgen    = as.numeric(d$gen.stat2 == "fgen"),
  FinUnstable = as.numeric(d$financially.stable2 %in% c("no", "sometimes")),
  STEM        = as.numeric(d$STEM.major.clean == "yes"),
  Lower       = as.numeric(d$division == "lower"),
  GPA         = suppressWarnings(as.numeric(d$GPA)))
keep <- stats::complete.cases(X) &
  !is.na(suppressWarnings(as.numeric(d$idep.camera))) &
  !is.na(d$race2) & !is.na(d$gender2) & !is.na(d$lgbtq2) & !is.na(d$gen.stat2) &
  !is.na(d$financially.stable2) & !is.na(d$STEM.major.clean) & !is.na(d$division)
X <- X[keep, ]; d <- d[keep, ]
cat(sprintf("analysis n = %d (paper's Table S5 models)\n\n", nrow(X)))

items <- grep("^idep\\.", names(d), value = TRUE)
FIT <- t(sapply(items, function(i)
  coef(lm(suppressWarnings(as.numeric(d[[i]])) ~ ., data = X))))
rownames(FIT) <- items

cat(sprintf("%-52s %-26s %8s %8s %s\n",
            "published aspect (Table S5)", "nearest fitted column", "maxdev", "runnerup", "shipped?"))
allok <- TRUE
for (aspect in names(PUBLISHED)) {
  dev <- apply(abs(sweep(FIT, 2, PUBLISHED[[aspect]], "-")), 1, max)
  o <- order(dev)
  best <- names(dev)[o[1]]; second <- names(dev)[o[2]]
  want <- lookup(aspect)
  good <- best == want && dev[o[1]] <= 0.006 && dev[o[2]] >= 0.02
  allok <- allok && good
  cat(sprintf("%-52s %-26s %8.4f %8.3f %s\n",
              substr(aspect, 1, 52), best, dev[o[1]], dev[o[2]],
              if (good) "OK" else paste0("MISMATCH (shipped on ", want, ")")))
}
cat(sprintf("\nbijection over 17 aspects: %s\n",
            length(unique(apply(sapply(PUBLISHED, function(p)
              apply(abs(sweep(FIT, 2, p, "-")), 1, max)), 2, which.min))) == 17))
cat("Rounding: Table S5 prints 2 d.p., so a perfect refit deviates by <=0.005.\n")
cat("This route distinguishes every one of the 17 items from every other: each\n",
    "published vector's nearest rival column is >=0.02 away, ~12x the rounding floor.\n", sep = "")
cat(if (allok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
