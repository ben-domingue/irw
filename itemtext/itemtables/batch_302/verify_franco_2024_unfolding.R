# Verification for franco_2024_unfolding (#2228, batch_302).
#
# SOURCE. Franco & Carvalho (2023), 'A Tutorial on Unidimensional Unfolding',
# PsyArXiv doi:10.31234/osf.io/5hnkz, CC BY; deposit osf.io/pqjhv (CoombsGPT.csv).
#
# TWO THINGS HAD TO BE GOT RIGHT AND BOTH COME FROM THE PAPER, not from the data.
# (1) WHICH SET. The paper generated THREE sets of six items with ChatGPT and
#     printed all eighteen in Table 1, then says "we decided to collect the
#     psychometric data with the third set of items". Taking the obvious first
#     set would have shipped six wrong statements.
# (2) WHICH ORDER. Table 1 labels rows A-F by assumed level of attention-seeking
#     rather than by item number. The paper fixes the correspondence when it
#     says that if the judges ordered the items as in Table 1 "the only response
#     pattern should be 654321" -- i.e. item 1 is row A, the most
#     attention-seeking, through item 6 = row F.
#
# Route 1: six codes, and the ranking scale.
# Route 2: the ranking constraint -- each respondent uses each rank once.
suppressWarnings(suppressMessages({library(dplyr); library(tidyr)}))
d <- as.data.frame(irw::irw_fetch("franco_2024_unfolding"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
items <- read.csv("itemtables/batch_302/franco_2024_unfolding__items.csv",
                  stringsAsFactors = FALSE, na.strings = "NA")

cat("=== Route 1: codes and scale ===\n")
r1 <- setequal(unique(d$item), paste0("p_", 1:6))
lv <- sort(unique(d$resp))
r1b <- identical(as.numeric(lv), as.numeric(1:6))
cat(sprintf("  codes %s -- exactly p_1..p_6: %s\n", paste(sort(unique(d$item)), collapse=","), r1))
cat(sprintf("  resp levels %s -- ranks 1 to 6: %s\n", paste(lv, collapse=","), r1b))

cat("\n=== Route 2: this is a RANKING, and the data proves it ===\n")
w <- d %>% select(id, item, resp) %>% distinct(id, item, .keep_all = TRUE) %>%
     pivot_wider(names_from = item, values_from = resp)
m <- as.matrix(w[, paste0("p_", 1:6)])
m <- m[complete.cases(m), , drop = FALSE]
perm <- apply(m, 1, function(r) identical(sort(as.numeric(r)), as.numeric(1:6)))
cat(sprintf("  %d complete respondents; %d of them use each rank 1-6 exactly once\n",
            nrow(m), sum(perm)))
r2 <- all(perm)
cat(sprintf("  -> every response vector is a permutation of 1-6: %s\n", r2))
cat("  That is what makes resp a RANK rather than a rating, and it is why\n")
cat("  option_text labels only the two ends ('rank 1 -- describes me best',\n")
cat("  'rank 6 -- describes me worst') instead of offering six agreement levels.\n")

cat("\n=== the shipped statements, in assumed order ===\n")
sh <- unique(items[, c("item","item_text","item_text_translated","section_prompt")])
sh <- sh[order(as.integer(sub("p_", "", sh$item))), ]
for (i in seq_len(nrow(sh)))
    cat(sprintf("  %-5s %-58s\n        %s\n", sh$item[i],
                substr(sh$item_text_translated[i], 1, 58), substr(sh$item_text[i], 1, 58)))

cat("\n=== What this does NOT establish ===\n")
cat("  That the set-3 assignment and the A-F ordering are right, beyond the\n")
cat("  paper's own two statements. Nothing in the response data distinguishes\n")
cat("  set 1 from set 3, and an unfolding model does not require the items to be\n")
cat("  in any particular order, so no numeric route can confirm it. That is why\n")
cat("  the status is PARTIAL. The administered language is Brazilian Portuguese\n")
cat("  and ships in item_text with the paper's own English in item_text_translated.\n")
cat("\nVERDICT:", if (r1 && r1b && r2) "PASS" else "FAIL", "\n")
