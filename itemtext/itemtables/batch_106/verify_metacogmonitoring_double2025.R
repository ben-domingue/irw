# verify_metacogmonitoring_double2025.R
#
# CLAIM UNDER TEST: each IRW item code (Q1_1 .. Q7_7, the raw Qualtrics column
# names) carries the correct one of the 64 item wordings printed in Double (2025)
# Supplementary Materials. The mapping was inferred positionally -- the 64-item
# list is the 67 data columns in file order minus the two attention checks
# (Q6_5, Q7_6) and the repeated item (Q3_7), which the study's own analysis
# script removes in exactly that way.
#
# FALSIFIABLE PREDICTION: the same Supplementary Materials print a two-factor
# promax loading table with one row per pool item (Q1..Q64). Re-running the
# study's analysis on the live IRW data yields a loading pair per IRW item code;
# looking up each SHIPPED item_text in the published item list and comparing the
# published loadings for THAT list position against the loadings observed for
# the item code the text was shipped on is sensitive to any permutation -- swap
# the text of two items and the two comparisons both break.
#
# What this does NOT establish: nothing about Q3_7 / Q6_5 / Q7_6 (shipped with
# blank item_text), and nothing about option_text<->resp, whose only published
# anchors are the endpoints 1 = "Strongly Disagree" and 6 = "Strongly Agree".

suppressMessages(library(irw))

TABLE <- "metacogmonitoring_double2025"
ITEMS_CSV <- file.path(dirname(sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1])),
                       paste0(TABLE, "__items.csv"))
if (!file.exists(ITEMS_CSV)) ITEMS_CSV <- paste0("itemtables/batch_106/", TABLE, "__items.csv")

# --- Published values, Double (2025) Supplementary Materials -----------------
PUB_TEXT <- c(
  "I monitor how I'm performing at all times",
  "I always have a sense of how well I'm performing",
  "I deliberately assess my performance on all tasks",
  "In the back of my mind I am keeping track of how well I’m doing",
  "I have clear sense of whether my decisions are good ones or not",
  "I monitor how confident I am in every decision",
  "I evaluate how confident I am after each decision",
  "I know how likely I am to be successful at a task",
  "When I perform I keep close track of how well I am doing",
  "I monitor the outcomes of my actions",
  "I know how well I have performed without external feedback",
  "I tend to be accurate in my self-assessments",
  "My sense of confidence in my decisions aligns well with the accuracy of the decision",
  "I always assess my performance",
  "I have a clear sense of how competent I am in every domain",
  "I am a aware of my strengths and weaknesses",
  "I know when I am performing well",
  "I know when I am performing poorly",
  "I never really keep track of how well I am doing",
  "I don’t spend time second guessing myself",
  "I don’t really have a good sense of whether my decisions are right or wrong",
  "I prioritize performance monitoring, even when I'm busy.",
  "I tend to know if a task is easy or difficult",
  "I'm aware of my cognitive strengths and weaknesses (e.g., attention, memory, problem-solving)",
  "I track my reaction times or speed on cognitive exercises",
  "I notice variations in how quickly I process information at different times",
  "My confidence level usually reflects my actual performance",
  "I'm realistic about my capabilities",
  "I can accurately assess when a task is beyond my current abilities",
  "I avoid comparing myself to others in a way that undermines my self-assessment",
  "I regularly set aside time to reflect on my performance",
  "I actively compare my work to predetermined standards",
  "I find it difficult to identify areas where I need improvement",
  "I remain objective when evaluating my own work",
  "I sometimes find myself surprised by how well (or poorly) I've performed on a task",
  "I take both my successes and failures into account when assessing my performance",
  "I approach self-monitoring with a curious and non-judgmental mindset",
  "I find it motivating to track my performance improvements over time",
  "I analyze my performance data to identify recurring patterns",
  "I learn from my mistakes and adjust my approach accordingly",
  "I'm comfortable trying new methods to see if they improve my results",
  "I regularly experiment with different performance monitoring techniques",
  "I'm open to rethinking previous self-assessments based on new information",
  "I can quickly recognize when the criteria for assessing my performance have changed",
  "I'm flexible about shifting my monitoring focus depending on the task requirements",
  "I can effectively communicate my performance strengths and weaknesses",
  "Before I start a task, I predict how well I'll do",
  "After I finish a task, I compare my predicted performance with how I actually did",
  "I regularly adjust my confidence levels based on my performance history",
  "My confidence in my abilities is closely aligned with my objective performance",
  "There's rarely a big difference between how confident I feel and how well I actually perform",
  "I'm good at recognizing when I'm overconfident about a task",
  "I'm good at recognizing when I'm underconfident about a task",
  "If I'm very confident about something, I'm usually correct",
  "If I have low confidence about something, I'm often correct to be doubtful",
  "I'm more likely to seek help if my confidence is low",
  "I avoid making decisions when I'm feeling overly confident",
  "I'm comfortable admitting when I don't know something",
  "I carefully consider the information available before expressing my level of confidence",
  "I welcome opportunities to test the accuracy of my self-assessments",
  "I enjoy getting feedback to help calibrate my confidence with my actual performance",
  "I believe that honest self-awareness is important for success",
  "I do not have a realistic sense of my own capabilities",
  "I make an effort to stay realistic about my capabilities"
)
PUB_F1 <- c(-0.1377552, 0.33776418, -0.1521126, 0.0136258, 0.71471266, -0.0519829, -0.0990533, 0.59214638, 0.04534402, 0.21340039, 0.66438684, 0.71176442, 0.57882086, -0.1003099, 0.52587736, 0.7623708, 0.74810944, 0.43706959, -0.111813, 0.40829338, -0.7486891, -0.0404557, 0.69000689, 0.56935791, -0.0503649, 0.03849675, 0.58062427, 0.76641127, 0.57318005, 0.42651659, 0.00861401, -0.0375917, -0.2855012, 0.6174017, -0.1614615, 0.59384155, 0.53783218, 0.10855836, 0.04275792, 0.63845573, 0.56696311, 0.11533625, 0.4386204, 0.46931609, 0.47446761, 0.56465109, -0.0013146, 0.00132203, 0.04629104, 0.55816252, 0.51556926, 0.46141331, 0.40817217, 0.49752383, 0.3238589, 0.21379302, -0.1546905, 0.45509179, 0.39476544, 0.29347675, 0.22527478, 0.33900536, -0.7747929, 0.6257979)
PUB_F2 <- c(0.86704274, 0.43360757, 0.86814142, 0.69334144, 0.00341445, 0.79859921, 0.81679346, 0.09079384, 0.71944282, 0.48696433, -0.1075442, -0.0544197, 0.12586542, 0.76144659, 0.20285518, -0.1006791, -0.0180201, 0.10969125, -0.2789449, -0.1261415, 0.26586496, 0.70914579, -0.0626114, 0.02818494, 0.65140172, 0.56643135, 0.08026874, -0.1687248, -0.1039762, -0.0970513, 0.63437133, 0.60606278, 0.00784695, 0.01012966, 0.18591287, 0.00505783, 0.10556439, 0.57360794, 0.66513616, -0.0716506, 0.05775935, 0.55465543, 0.10605572, 0.30933271, 0.16389468, 0.12178255, 0.57018074, 0.66651024, 0.43527592, 0.09921557, -0.0372279, 0.07941847, 0.10136069, 0.01325083, -0.1471223, 0.00026959, 0.31834793, -0.0958143, 0.18583447, 0.36565266, 0.32508367, 0.08187611, 0.25953941, -0.0385566)

DROP <- c("Q3_7", "Q6_5", "Q7_6")   # repeated item + 2 attention checks
COL_ORDER <- c(paste0("Q1_", 1:10), paste0("Q2_", 1:10), paste0("Q3_", 1:10),
               paste0("Q4_", 1:10), paste0("Q5_", 1:10), paste0("Q6_", 1:10),
               paste0("Q7_", 1:7))

norm <- function(s) tolower(gsub("[^a-z0-9]", "", tolower(iconv(s, "UTF-8", "ASCII//TRANSLIT"))))

# --- Live data ---------------------------------------------------------------
d <- as.data.frame(irw::irw_fetch(TABLE))
d$resp <- as.numeric(d$resp)
wide <- as.data.frame(reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide"))
names(wide) <- sub("^resp\\.", "", names(wide))
rownames(wide) <- wide$id; wide$id <- NULL
wide <- wide[, COL_ORDER]

# The study's own exclusion: drop anyone failing BOTH attention checks.
keep <- !(wide$Q6_5 != 5 & wide$Q7_6 != 2)
cat(sprintf("live respondents: %d; dropped by attention check: %d\n", nrow(wide), sum(!keep)))
items <- wide[keep, setdiff(COL_ORDER, DROP)]
cat(sprintf("items entering the factor analysis: %d\n\n", ncol(items)))

fit <- factanal(items, 2, rotation = "promax")
L <- unclass(fit$loadings)

# --- Look each SHIPPED item_text up in the published list --------------------
csv <- read.csv(ITEMS_CSV, stringsAsFactors = FALSE, encoding = "UTF-8")
ship <- unique(csv[, c("item", "item_text")])
ship <- ship[!is.na(ship$item_text) & nzchar(trimws(ship$item_text)), ]
cat(sprintf("shipped items with item_text: %d (blank: %d)\n\n",
            nrow(ship), length(COL_ORDER) - nrow(ship)))

pubn <- norm(PUB_TEXT)
bad <- 0; worst <- 0; unmatched <- character(0)
cat(sprintf("%-7s %5s  %8s %8s   %8s %8s   %7s\n",
            "item", "pub#", "pubF1", "obsF1", "pubF2", "obsF2", "maxdiff"))
for (i in seq_len(nrow(ship))) {
    it <- ship$item[i]
    k <- match(norm(ship$item_text[i]), pubn)
    if (is.na(k)) { unmatched <- c(unmatched, it); next }
    o1 <- L[it, 1]; o2 <- L[it, 2]
    dd <- max(abs(o1 - PUB_F1[k]), abs(o2 - PUB_F2[k]))
    worst <- max(worst, dd); if (dd > 1e-4) bad <- bad + 1
    cat(sprintf("%-7s %5d  %8.4f %8.4f   %8.4f %8.4f   %7.5f\n",
                it, k, PUB_F1[k], o1, PUB_F2[k], o2, dd))
}

cat(sprintf("\nitems compared: %d   mismatched (>1e-4): %d   largest deviation: %.7f\n",
            nrow(ship) - length(unmatched), bad, worst))
if (length(unmatched)) cat("item_text not found in the published pool:", paste(unmatched, collapse = ", "), "\n")

# --- Independent corroboration of the list<->loading-row numbering ----------
# The paper quotes two monitoring items and two self-awareness items by wording,
# and the study's analysis script names the CFA marker items for each factor.
cat("\nPaper-quoted marker items (Double 2025, Study 1 Materials; CFA blocks from\n",
    "ex1-self-reports-metacognition-analysis.R). Monitoring loads Factor2, self-awareness Factor1:\n", sep = "")
MARK <- list(monitoring = c("Q1_3", "Q1_7", "Q1_9", "Q2_4"),
             selfaware  = c("Q2_2", "Q2_6", "Q2_7", "Q3_9"))
for (g in names(MARK)) for (it in MARK[[g]])
    cat(sprintf("  %-10s %-6s F1=%7.3f  F2=%7.3f   %s\n", g, it, L[it, 1], L[it, 2],
                substr(ship$item_text[match(it, ship$item)], 1, 52)))
mono <- min(L[MARK$monitoring, 2]); selfa <- min(L[MARK$selfaware, 1])
cross <- max(abs(L[MARK$monitoring, 1]), abs(L[MARK$selfaware, 2]))
cat(sprintf("  min primary loading %.3f / %.3f vs max cross-loading %.3f\n", mono, selfa, cross))
marker_ok <- mono > 0.5 && selfa > 0.5 && cross < 0.3

# Polarity: exactly the reverse-worded items should carry negative loadings.
REV <- c("Q2_9", "Q3_1", "Q7_5")   # "I never really keep track...", "I don't really have a good sense...", "I do not have a realistic sense..."
cat("\nReverse-worded items, strongest negative loadings in the pool:\n")
for (it in REV) cat(sprintf("  %-6s F1=%7.3f F2=%7.3f  %s\n", it, L[it, 1], L[it, 2],
                            substr(ship$item_text[match(it, ship$item)], 1, 52)))
strongneg <- rownames(L)[L[, 1] < -0.7]
cat("  items with Factor1 < -0.7:", paste(strongneg, collapse = ", "), "\n")
polarity_ok <- setequal(strongneg, c("Q3_1", "Q7_5")) && L["Q2_9", 2] < 0

cat("\nNote: this route says nothing about Q3_7 (the study's repeated item),\n",
    "Q6_5 or Q7_6 (attention checks) -- all three ship blank item_text -- and\n",
    "nothing about the option_text<->resp axis.\n", sep = "")

ok <- (bad == 0) && length(unmatched) == 0 && nrow(ship) == 64 && marker_ok && polarity_ok
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
