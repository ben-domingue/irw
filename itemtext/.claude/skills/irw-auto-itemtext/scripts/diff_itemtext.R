# Usage: Rscript diff_itemtext.R <table> <path/to/candidate_items.csv> [diff_report.md]
#
# Audit-mode diffing engine: compares a freshly-extracted candidate
# `{table}__items.csv` against the *current* Redivis-curated ground truth
# (`irw::irw_itemtext(table)`) for that table. Used to reprocess tables that
# already have an existing itemtext entry and check whether that curation
# has drifted from the live `irw::irw_fetch(table)` data -- see SKILL.md's
# "Audit mode" section.
#
# Comparison logic (edit-ratio, Jaccard, resp-set alignment, swap-tolerant
# instructions/section_prompt comparison, bilingual `_translated` column
# handling) is carried over unchanged from the itemtext skill eval's
# itemtext/skill_test/sessionC_batch/grade_batch.R, which was validated
# across a 100-table blind-extraction eval. Dropped from that script
# (eval-only, not applicable here): extraction_log_*.md free-text parsing,
# the hand-categorized pending_index_notes_categorized.csv abstain-category
# join, and manifest_batch.csv stratification columns.
#
# `correct_response` is intentionally not graded here either -- the eval
# found ground truth never populates it meaningfully.
#
# This file can also be `source()`d (set DIFF_ITEMTEXT_SOURCED_ONLY <- TRUE
# first to skip the CLI block) to call diff_itemtext() directly, e.g. for
# the regression check against the eval's cached groundtruth_*.rds files.

LOW_SIMILARITY_THRESHOLD <- 0.6
CONFIRM_SIMILARITY_THRESHOLD <- 0.95

## ---- text helpers (unchanged from grade_batch.R) ---------------------

is_missing <- function(x) {
  if (is.null(x)) return(TRUE)
  x <- as.character(x)
  is.na(x) | trimws(x) == "" | trimws(x) == "NA" | trimws(x) == "NULL"
}

norm_txt <- function(x) {
  if (is_missing(x)) return("")
  x <- tolower(as.character(x))
  x <- gsub("[[:space:]]+", " ", x)
  trimws(x)
}

edit_ratio <- function(a, b) {
  a <- norm_txt(a); b <- norm_txt(b)
  if (nchar(a) == 0 && nchar(b) == 0) return(1)
  if (nchar(a) == 0 || nchar(b) == 0) return(0)
  d <- adist(a, b)[1, 1]
  1 - d / max(nchar(a), nchar(b))
}

jaccard <- function(a, b) {
  a <- norm_txt(a); b <- norm_txt(b)
  ta <- unique(strsplit(gsub("[^a-z0-9 ]", " ", a), "\\s+")[[1]])
  tb <- unique(strsplit(gsub("[^a-z0-9 ]", " ", b), "\\s+")[[1]])
  ta <- ta[ta != ""]; tb <- tb[tb != ""]
  if (length(ta) == 0 && length(tb) == 0) return(1)
  if (length(ta) == 0 || length(tb) == 0) return(0)
  length(intersect(ta, tb)) / length(union(ta, tb))
}

collapse_item <- function(d, item_col, field) {
  tapply(d[[field]], d[[item_col]], function(x) x[1])
}

# See grade_batch.R for the full rationale: candidates write a single
# item_text/option_text/instructions/section_prompt field, but some
# ground-truth tables carry the original-administered-language text in the
# primary field plus a same-content English `<field>_translated` column --
# compare against whichever one actually matches, not just the primary.
get_translated_col <- function(df, field) {
  primary_name <- paste0(field, "_translated")
  if (primary_name %in% names(df) && any(!is_missing(df[[primary_name]]))) return(primary_name)
  NA_character_
}

best_gt_match <- function(primary_val, translated_val, cv) {
  er_p <- edit_ratio(primary_val, cv)
  if (is.na(translated_val) || is_missing(translated_val)) {
    return(list(val = primary_val, edit_ratio = er_p, jaccard = jaccard(primary_val, cv), used = "primary"))
  }
  er_t <- edit_ratio(translated_val, cv)
  if (er_t > er_p) {
    list(val = translated_val, edit_ratio = er_t, jaccard = jaccard(translated_val, cv), used = "translated")
  } else {
    list(val = primary_val, edit_ratio = er_p, jaccard = jaccard(primary_val, cv), used = "primary")
  }
}

## ---- core diff --------------------------------------------------------

# gt: the current curation data frame (irw::irw_itemtext(table) shape, or
#     an equivalent cached data frame for regression testing).
# cand: the freshly-extracted candidate data frame (same shape).
# Returns a list: $summary (one-row data frame), $metrics (long comparison
# table), $mismatches (itemized differences), $classification ("confirm" or
# "review" -- "review" is a suggestion only; whether a reviewed diff should
# become a replace-candidate or a documented ambiguity is a judgment call
# for whoever runs audit mode, informed by $mismatches).
diff_itemtext <- function(table, gt, cand) {
  gt$item <- as.character(gt$item)
  cand$item <- as.character(cand$item)

  metrics_rows <- list()
  mismatch_rows <- list()

  add_metric <- function(item, field, gt_val, cand_val, note = "") {
    er <- edit_ratio(gt_val, cand_val)
    jc <- jaccard(gt_val, cand_val)
    metrics_rows[[length(metrics_rows) + 1]] <<- data.frame(
      item = item, field = field,
      gt_value = as.character(gt_val), cand_value = as.character(cand_val),
      edit_ratio = round(er, 4), jaccard = round(jc, 4), note = note,
      stringsAsFactors = FALSE
    )
    list(edit_ratio = er, jaccard = jc)
  }

  add_mismatch <- function(item, category, detail = "") {
    mismatch_rows[[length(mismatch_rows) + 1]] <<- data.frame(
      item = item, category = category, detail = detail, stringsAsFactors = FALSE
    )
  }

  gt_items <- unique(gt$item)
  cand_items <- unique(cand$item)
  missed <- setdiff(gt_items, cand_items)
  extra <- setdiff(cand_items, gt_items)
  common <- intersect(gt_items, cand_items)

  for (it in missed) add_mismatch(it, "missed_item", "in current curation but not in fresh extraction")
  for (it in extra) add_mismatch(it, "extra_item", "in fresh extraction but not in current curation")
  item_coverage_ok <- (length(missed) == 0) && (length(extra) == 0)

  # resp-set alignment
  gt_resp_ever_populated <- any(!is.na(suppressWarnings(as.numeric(gt$resp[gt$item %in% common]))))
  resp_set_matches <- c()
  option_text_scores <- c()
  for (it in common) {
    if (!gt_resp_ever_populated) break
    g <- gt[gt$item == it, ]
    c <- cand[cand$item == it, ]
    g_resp <- suppressWarnings(as.numeric(g$resp)); g_resp <- g_resp[!is.na(g_resp)]
    c_resp <- suppressWarnings(as.numeric(c$resp)); c_resp <- c_resp[!is.na(c_resp)]
    same_set <- setequal(g_resp, c_resp)
    resp_set_matches <- c(resp_set_matches, same_set)
    if (!same_set) {
      add_mismatch(it, "resp_set_mismatch",
                   paste0("curated={", paste(sort(g_resp), collapse = ","),
                          "} fresh={", paste(sort(c_resp), collapse = ","), "}"))
    }

    ot_transl_col <- get_translated_col(g, "option_text")
    if ("option_text" %in% names(g) && "option_text" %in% names(c)) {
      for (rv in intersect(g_resp, c_resp)) {
        gv <- g[["option_text"]][suppressWarnings(as.numeric(g$resp)) == rv][1]
        gvt <- if (!is.na(ot_transl_col)) g[[ot_transl_col]][suppressWarnings(as.numeric(g$resp)) == rv][1] else NA_character_
        cv <- c[["option_text"]][suppressWarnings(as.numeric(c$resp)) == rv][1]
        if (!is_missing(gv) || !is_missing(gvt) || !is_missing(cv)) {
          if (!is_missing(cv) && (!is_missing(gv) || !is_missing(gvt))) {
            bm <- best_gt_match(gv, gvt, cv)
            m <- add_metric(it, paste0("option_text[resp=", rv, "]"), bm$val, cv, note = bm$used)
            if (m$edit_ratio < LOW_SIMILARITY_THRESHOLD) add_mismatch(it, "option_text_mismatch", paste0("resp=", rv))
            option_text_scores <- c(option_text_scores, m$edit_ratio)
          } else {
            add_mismatch(it, "option_text_presence_mismatch", paste0("resp=", rv))
          }
        }
      }
    }
  }
  resp_alignment_rate <- if (gt_resp_ever_populated && length(resp_set_matches) > 0) mean(resp_set_matches) else NA

  # item_text
  item_text_scores <- c()
  gt_it_vec <- collapse_item(gt, "item", "item_text")[common]
  cand_it_vec <- collapse_item(cand, "item", "item_text")[common]
  it_transl_col <- get_translated_col(gt, "item_text")
  gt_it_transl_vec <- if (!is.na(it_transl_col)) collapse_item(gt, "item", it_transl_col)[common] else rep(NA_character_, length(common))
  for (i in seq_along(common)) {
    it <- common[i]
    gv <- gt_it_vec[i]; gvt <- gt_it_transl_vec[i]; cv <- cand_it_vec[i]
    if (is_missing(gv) && is_missing(gvt) && is_missing(cv)) next
    bm <- best_gt_match(gv, gvt, cv)
    m <- add_metric(it, "item_text", bm$val, cv, note = bm$used)
    if (m$edit_ratio < LOW_SIMILARITY_THRESHOLD) add_mismatch(it, "item_text_mismatch", "")
    item_text_scores <- c(item_text_scores, m$edit_ratio)
  }

  # instructions/section_prompt, swap-tolerant
  gt_instr_vec <- collapse_item(gt, "item", "instructions")[common]
  gt_sp_vec <- collapse_item(gt, "item", "section_prompt")[common]
  cand_instr_vec <- collapse_item(cand, "item", "instructions")[common]
  cand_sp_vec <- collapse_item(cand, "item", "section_prompt")[common]
  instr_transl_col <- get_translated_col(gt, "instructions")
  sp_transl_col <- get_translated_col(gt, "section_prompt")
  gt_instr_transl_vec <- if (!is.na(instr_transl_col)) collapse_item(gt, "item", instr_transl_col)[common] else rep(NA_character_, length(common))
  gt_sp_transl_vec <- if (!is.na(sp_transl_col)) collapse_item(gt, "item", sp_transl_col)[common] else rep(NA_character_, length(common))
  context_scores <- c(); swap_flags <- 0
  for (i in seq_along(common)) {
    it <- common[i]
    gi <- gt_instr_vec[i]; gs <- gt_sp_vec[i]
    git <- gt_instr_transl_vec[i]; gst <- gt_sp_transl_vec[i]
    ci <- cand_instr_vec[i]; cs <- cand_sp_vec[i]
    if (is_missing(gi) && is_missing(git) && is_missing(gs) && is_missing(gst)) next

    bm_i_direct <- best_gt_match(gi, git, ci)
    bm_s_direct <- best_gt_match(gs, gst, cs)
    bm_i_swap <- best_gt_match(gi, git, cs)
    bm_s_swap <- best_gt_match(gs, gst, ci)

    sim_direct <- 0; n_direct <- 0
    if (!is_missing(gi) || !is_missing(git)) { sim_direct <- sim_direct + bm_i_direct$edit_ratio; n_direct <- n_direct + 1 }
    if (!is_missing(gs) || !is_missing(gst)) { sim_direct <- sim_direct + bm_s_direct$edit_ratio; n_direct <- n_direct + 1 }
    sc_direct <- if (n_direct > 0) sim_direct / n_direct else 0

    sim_swap <- 0; n_swap <- 0
    if (!is_missing(gi) || !is_missing(git)) { sim_swap <- sim_swap + bm_i_swap$edit_ratio; n_swap <- n_swap + 1 }
    if (!is_missing(gs) || !is_missing(gst)) { sim_swap <- sim_swap + bm_s_swap$edit_ratio; n_swap <- n_swap + 1 }
    sc_swap <- if (n_swap > 0) sim_swap / n_swap else 0

    if (sc_swap > sc_direct + 0.15) {
      context_scores <- c(context_scores, sc_swap)
      swap_flags <- swap_flags + 1
      add_metric(it, "instructions_or_section_prompt(swap-detected)",
                 paste0("instr=", substr(gi, 1, 60), " | sp=", substr(gs, 1, 60)),
                 paste0("instr=", substr(ci, 1, 60), " | sp=", substr(cs, 1, 60)),
                 "field_placement_swap_suspected")
      add_mismatch(it, "instructions_section_prompt_swap_suspected", "")
    } else {
      context_scores <- c(context_scores, sc_direct)
      if (!is_missing(gi) || !is_missing(git)) {
        m <- add_metric(it, "instructions", bm_i_direct$val, ci, note = bm_i_direct$used)
        if (m$edit_ratio < LOW_SIMILARITY_THRESHOLD) add_mismatch(it, "instructions_mismatch", "")
      }
      if (!is_missing(gs) || !is_missing(gst)) {
        m <- add_metric(it, "section_prompt", bm_s_direct$val, cs, note = bm_s_direct$used)
        if (m$edit_ratio < LOW_SIMILARITY_THRESHOLD) add_mismatch(it, "section_prompt_mismatch", "")
      }
    }
  }

  metrics_df <- if (length(metrics_rows) > 0) do.call(rbind, metrics_rows) else
    data.frame(item = character(0), field = character(0), gt_value = character(0),
               cand_value = character(0), edit_ratio = numeric(0), jaccard = numeric(0),
               note = character(0), stringsAsFactors = FALSE)
  mismatch_df <- if (length(mismatch_rows) > 0) do.call(rbind, mismatch_rows) else
    data.frame(item = character(0), category = character(0), detail = character(0), stringsAsFactors = FALSE)

  mean_or_na <- function(x) if (length(x) > 0) round(mean(x), 4) else NA_real_

  summary <- data.frame(
    table = table,
    n_gt_items = length(gt_items),
    n_cand_items = length(cand_items),
    n_missed_items = length(missed),
    n_extra_items = length(extra),
    item_coverage_ok = item_coverage_ok,
    resp_alignment_rate = round(resp_alignment_rate, 4),
    mean_item_text_similarity = mean_or_na(item_text_scores),
    mean_option_text_similarity = mean_or_na(option_text_scores),
    mean_context_similarity = mean_or_na(context_scores),
    n_context_swap_detected = swap_flags,
    stringsAsFactors = FALSE
  )

  all_clean <- item_coverage_ok &&
    (is.na(resp_alignment_rate) || resp_alignment_rate >= 1) &&
    (is.na(summary$mean_item_text_similarity) || summary$mean_item_text_similarity >= CONFIRM_SIMILARITY_THRESHOLD) &&
    (is.na(summary$mean_option_text_similarity) || summary$mean_option_text_similarity >= CONFIRM_SIMILARITY_THRESHOLD) &&
    (is.na(summary$mean_context_similarity) || summary$mean_context_similarity >= CONFIRM_SIMILARITY_THRESHOLD) &&
    swap_flags == 0

  summary$classification <- if (all_clean) "confirm" else "review"

  list(summary = summary, metrics = metrics_df, mismatches = mismatch_df,
       classification = summary$classification)
}

## ---- markdown diff report ----------------------------------------------

write_diff_report <- function(table, result, path) {
  s <- result$summary
  lines <- c(
    paste0("# Audit diff: ", table),
    "",
    paste0("Classification (suggested): **", s$classification, "**"),
    "",
    "## Summary",
    "",
    paste0("- item coverage: ", ifelse(s$item_coverage_ok, "OK", "MISMATCH"),
           " (missed=", s$n_missed_items, ", extra=", s$n_extra_items, ")"),
    paste0("- resp-set alignment rate: ", ifelse(is.na(s$resp_alignment_rate), "n/a", s$resp_alignment_rate)),
    paste0("- mean item_text similarity: ", ifelse(is.na(s$mean_item_text_similarity), "n/a", s$mean_item_text_similarity)),
    paste0("- mean option_text similarity: ", ifelse(is.na(s$mean_option_text_similarity), "n/a", s$mean_option_text_similarity)),
    paste0("- mean context (instructions/section_prompt) similarity: ", ifelse(is.na(s$mean_context_similarity), "n/a", s$mean_context_similarity)),
    paste0("- instructions/section_prompt swaps detected: ", s$n_context_swap_detected),
    "",
    "## Itemized mismatches",
    ""
  )
  if (nrow(result$mismatches) == 0) {
    lines <- c(lines, "(none)")
  } else {
    for (i in seq_len(nrow(result$mismatches))) {
      r <- result$mismatches[i, ]
      lines <- c(lines, paste0("- `", r$item, "` -- ", r$category,
                                if (nzchar(r$detail)) paste0(" (", r$detail, ")") else ""))
    }
  }
  lines <- c(lines, "", "## Field-level values for mismatched items", "")
  low_sim <- result$metrics[!is.na(result$metrics$edit_ratio) & result$metrics$edit_ratio < CONFIRM_SIMILARITY_THRESHOLD, ]
  if (nrow(low_sim) == 0) {
    lines <- c(lines, "(none)")
  } else {
    for (i in seq_len(nrow(low_sim))) {
      r <- low_sim[i, ]
      lines <- c(lines,
                 paste0("### `", r$item, "` / ", r$field, " (similarity ", r$edit_ratio, ")"),
                 paste0("- curated: `", r$gt_value, "`"),
                 paste0("- fresh: `", r$cand_value, "`"),
                 "")
    }
  }
  writeLines(lines, path)
}

## ---- CLI ------------------------------------------------------------

if (!isTRUE(getOption("diff_itemtext.sourced_only", FALSE)) && !isTRUE(exists("DIFF_ITEMTEXT_SOURCED_ONLY"))) {
  args <- commandArgs(trailingOnly = TRUE)
  if (length(args) < 2) stop("Usage: Rscript diff_itemtext.R <table> <candidate_items.csv> [diff_report.md]")
  table <- args[1]
  cand_path <- args[2]
  report_path <- if (length(args) >= 3) args[3] else NULL

  cand <- read.csv(cand_path, stringsAsFactors = FALSE)
  gt <- irw::irw_itemtext(table)
  if (is.null(gt)) stop(table, " has no existing itemtext entry -- audit mode is for reprocessing tables that already have one; use the normal queue workflow instead.")

  result <- diff_itemtext(table, gt, cand)
  cat("=== Diff summary:", table, "===\n")
  print(result$summary)
  cat("\n=== Mismatches (", nrow(result$mismatches), ") ===\n", sep = "")
  if (nrow(result$mismatches) > 0) print(result$mismatches)

  if (!is.null(report_path)) {
    write_diff_report(table, result, report_path)
    cat("\nWrote diff report to", report_path, "\n")
  }
}
