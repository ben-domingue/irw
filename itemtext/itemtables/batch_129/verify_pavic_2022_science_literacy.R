# verify_pavic_2022_science_literacy.R
#
# mapping_basis = data_labels: the IRW item codes Lit1..Lit15 ARE the SPSS column
# names that data/pavic_2022_vaccine_conspiracy.py melts out of the PLOS S1 deposit,
# and the shipped item_text is those columns' own variable labels. Step 5b therefore
# exempts this table. This script records the INDEPENDENT corroboration anyway,
# because the paper happens to publish a per-item statistic that would break if any
# two item_texts were swapped.
#
# Claim under test: the item_text shipped for LitK is the statement whose "% correct"
# the paper prints in row K of Table 4 (10.1371/journal.pone.0264722.t004). Table 4
# lists the 15 statements verbatim, in the same order as the .sav labels, with each
# one's % of respondents scored correct. Live per-item mean(resp) * 100 is exactly
# that quantity, so a permuted mapping would show up immediately.

suppressMessages(library(irw))

TABLE <- "pavic_2022_science_literacy"
ITEMS <- paste0("Lit", 1:15)

# Paper Table 4, "Correct answer (%)" column, rows 1-15 in printed order.
PUBLISHED <- c(87.69, 83.54, 90.81, 88.21, 85.44, 72.77, 85.96, 75.91,
               50.26, 85.44, 66.38, 90.47, 88.39, 93.93, 81.63)
TOL <- 0.02

# The statements as printed in Table 4, abbreviated, in the same row order --
# these are what the shipped item_text must line up with.
STATEMENT <- c("Antibiotics kill viruses as well as bacteria",
               "The Sun goes around the Earth",
               "The center of the Earth is very hot",
               "The oxygen we breathe comes from plants",
               "The earliest human beings lived at the same time as the dinosaurs",
               "By consuming genetically modified fruit we alter our genes",
               "All radioactivity is man-made",
               "It is the mother's genes that decide whether the baby is a boy or a girl",
               "More than half of human genes are identical to those of mice",
               "Electrons are smaller than atoms",
               "Lasers work by focusing sound waves",
               "It takes one month for the Earth to go around the Sun",
               "Radioactive milk can be made safe by boiling it",
               "The continents on which we live have been moving their location for millions of years and will continue to move in the future",
               "Human beings, as we know them today, developed from earlier species of animals")

d <- irw::irw_fetch(TABLE)
obs <- 100 * tapply(d$resp, d$item, mean)[ITEMS]
n   <- tapply(d$resp, d$item, length)[ITEMS]

# The shipped file must pair each code with the Table 4 statement at that row.
csv <- read.csv(file.path(dirname(sub("--file=", "", grep("--file=", commandArgs(), value = TRUE)[1])),
                          "pavic_2022_science_literacy__items.csv"),
                stringsAsFactors = FALSE)
shipped <- csv$item_text[match(ITEMS, csv$item)]
text_ok <- identical(shipped, STATEMENT)

cat(sprintf("%-6s %5s %10s %10s %8s  %s\n",
            "item", "n", "published", "observed", "diff", "statement (Table 4 row)"))
for (i in seq_along(ITEMS))
    cat(sprintf("%-6s %5d %10.2f %10.2f %+8.2f  %s\n",
                ITEMS[i], n[i], PUBLISHED[i], obs[i], obs[i] - PUBLISHED[i],
                substr(STATEMENT[i], 1, 46)))

dev <- abs(obs - PUBLISHED)
cat(sprintf("\nshipped item_text == Table 4 statement, row for row: %s\n", text_ok))
cat(sprintf("items within %.2f pp of the published value: %d of 15\n", TOL, sum(dev <= TOL)))

# The single exception is Lit6, and it is a typo in the paper, not a mapping error:
# a percentage over n = 577 must be an integer count / 577. 577 * 0.7277 = 419.88,
# which is not an integer; 577 * 0.7227 = 417 exactly. So 72.77 is unattainable and
# 72.27 -- the value observed -- is the only reachable figure near it.
lit6_typo <- abs(577 * PUBLISHED[6] / 100 - round(577 * PUBLISHED[6] / 100)) > 0.05 &&
             abs(577 * obs[6] / 100 - round(577 * obs[6] / 100)) < 1e-6
cat(sprintf("Lit6: published %.2f%% implies %.2f correct answers of 577 (not an integer); observed %.2f%% implies %.0f exactly -> paper typo: %s\n",
            PUBLISHED[6], 577 * PUBLISHED[6] / 100, obs[6], 577 * obs[6] / 100, lit6_typo))

# Independently, the paper's own Table 4 column sums to a total-score mean of
# 12.27, against the 12.30 stated in its text -- so the text figure is the one out
# of step with the table, and the live data reproduces the table.
cat(sprintf("total-score mean implied by Table 4: %.4f | from live data: %.4f | paper text states 12.30\n",
            sum(PUBLISHED) / 100, sum(obs) / 100))

cat("\nNote: this route does NOT separate Lit5 from Lit10 -- Table 4 prints 85.44% for\n",
    "both, so their two statements are interchangeable as far as these numbers go.\n",
    "What distinguishes them is the exemption itself: Lit5 and Lit10 are the .sav's own\n",
    "column names and each carries its own variable label, so no order inference is\n",
    "involved for them or for any other item.\n", sep = "")

pass <- text_ok && sum(dev <= TOL) == 14 && which(dev > TOL) == 6 && lit6_typo
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
