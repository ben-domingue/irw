#!/usr/bin/env Rscript
# Deterministic batch grading script for the irw-auto-itemtext skill eval.
# Reads groundtruth_<table>.rds (../sessionA_batch), candidate_<table>.rds +
# extraction_log_<table>.md (../sessionB_batch), and pending_index_notes.csv
# (../sessionB_batch) for all 100 tables in manifest_batch.csv. Metric
# definitions (edit-ratio, Jaccard, swap-tolerant instructions/section_prompt
# comparison) are carried over unchanged from verify_fix/grade.R /
# sessionC/grade.R. content-similarity only -- correct_response is not
# graded (pilot finding: ground truth never populates it meaningfully).

LOW_SIMILARITY_THRESHOLD <- 0.6

SESSION_A <- file.path("..", "sessionA_batch")
SESSION_B <- file.path("..", "sessionB_batch")

manifest <- read.csv(file.path(SESSION_A, "manifest_batch.csv"), stringsAsFactors = FALSE)
notes <- read.csv(file.path(SESSION_B, "pending_index_notes.csv"), stringsAsFactors = FALSE)
stopifnot(all(c("table", "note") %in% names(notes)))

## ---- text helpers (unchanged from verify_fix/grade.R) ---------------------

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

# Bilingual ground truth: 14 tables in this batch carry the original-language
# text in the primary field (item_text/option_text/instructions/
# section_prompt) plus a same-content English `<field>_translated` column
# (confirmed real, non-blank content -- not the case for every table that
# merely has the column). fad_dataset2's `item_text_translated` column
# additionally got its header mangled to `___5` somewhere in the Session
# A_batch caching step (a duplicate/blank-header collision), so `___5` is
# special-cased as an alias when it holds real content and the table has no
# properly-named item_text_translated column. Candidates correctly write
# their own translated/back-translated wording into the single `item_text`
# field (there is no field split on the candidate side), so grading must
# compare against whichever of primary/translated ground truth actually
# matches, not just the primary field -- otherwise a fully correct English
# transcription scores 0 against Chinese/Serbian/Spanish/Portuguese ground
# truth for no real reason (discovered via fad_dataset1/fad_dataset2, which
# both scored exactly 0.00 item_text similarity before this fix despite
# being verbatim-correct extractions -- see report_batch.md).
get_translated_col <- function(df, field) {
  primary_name <- paste0(field, "_translated")
  if (primary_name %in% names(df) && any(!is_missing(df[[primary_name]]))) return(primary_name)
  if (field == "item_text" && "___5" %in% names(df) && any(!is_missing(df[["___5"]]))) return("___5")
  NA_character_
}

# Returns the ground-truth value (primary or translated, whichever scores
# higher against cv) plus which one was used, for one item/field pair.
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

## ---- extraction_log parsing -----------------------------------------------
# Free-text logs, not structured data. Section headers are inconsistent
# across the 100 logs (contributors used many variant header strings), so
# we extract by matching a fixed set of header regexes rather than assuming
# one canonical header name, and fall back to NA (treated conservatively)
# when a table's log has no matching section at all.

read_log <- function(nm) {
  f <- file.path(SESSION_B, paste0("extraction_log_", nm, ".md"))
  if (!file.exists(f)) return(NULL)
  paste(readLines(f, warn = FALSE), collapse = "\n")
}

get_section <- function(txt, header_regex) {
  if (is.null(txt)) return(NA_character_)
  lines <- strsplit(txt, "\n")[[1]]
  starts <- grep(header_regex, lines)
  if (length(starts) == 0) return(NA_character_)
  s <- starts[1]
  if (s >= length(lines)) return("")
  rest <- lines[(s + 1):length(lines)]
  end_rel <- which(grepl("^## ", rest))
  e <- if (length(end_rel) > 0) end_rel[1] - 1 else length(rest)
  if (e < 1) return("")
  paste(trimws(rest[seq_len(e)]), collapse = " ")
}

get_source_type <- function(txt) {
  sec <- get_section(txt, "^## Source type used")
  if (is.na(sec) || nchar(trimws(sec)) == 0) sec <- get_section(txt, "^## Source used")
  if (is.na(sec) || nchar(trimws(sec)) == 0) return(NA_character_)
  substr(sec, 1, 300)
}

# ocr_sourced: TRUE only for a genuine positive claim of OCR/image-based
# transcription. The overwhelming majority of "## OCR / image-based
# extraction" sections open with an explicit negation ("None." / "Not
# applicable." / "No OCR was needed") -- those are FALSE. A handful of
# sections describe pdftotext ligature-glyph artifacts (e.g. "di erent" ->
# "different") from native text-layer PDFs; these explicitly disclaim being
# scanned/raster content ("not scanned raster", "no other OCR ambiguity")
# and are NOT genuine OCR, so they are also FALSE. Verified by manual read
# of every non-negation-opening section in this batch (see report_batch.md).
NEG_START <- "^(none|not applicable|not needed|no\\.|no,|no ocr|not used|no\\b)"
OCR_DISCLAIM <- "no other ocr ambiguity|not (a )?scanned raster|not a scanned image|machine-generated text"

get_ocr_sourced <- function(txt) {
  sec <- get_section(txt, "^## OCR")
  if (is.na(sec)) return(FALSE)
  sec_trim <- trimws(sec)
  if (nchar(sec_trim) == 0) return(FALSE)
  if (grepl(NEG_START, sec_trim, ignore.case = TRUE)) return(FALSE)
  if (!grepl("\\bocr\\b", sec_trim, ignore.case = TRUE)) return(FALSE)
  if (grepl(OCR_DISCLAIM, sec_trim, ignore.case = TRUE)) return(FALSE)
  TRUE
}

# derived items: pull the "Derived vs. directly-read values" section, then
# keep only tokens from it that literally match one of this table's actual
# item IDs (gt or candidate) -- avoids treating arbitrary prose words as
# item references.
get_derived_items <- function(txt, all_item_ids) {
  sec <- get_section(txt, "^## Derived vs")
  if (is.na(sec) || nchar(trimws(sec)) == 0) return(character(0))
  if (grepl("^none\\b", trimws(sec), ignore.case = TRUE)) return(character(0))
  # only look inside clauses that actually say "derived"
  derived_clauses <- regmatches(sec, gregexpr("[Dd]erived[^.]*\\.", sec))[[1]]
  if (length(derived_clauses) == 0) return(character(0))
  hit <- character(0)
  for (id in all_item_ids) {
    pat <- paste0("(?<![A-Za-z0-9_])", gsub("([\\W])", "\\\\\\1", id, perl = TRUE), "(?![A-Za-z0-9_])")
    if (any(grepl(pat, derived_clauses, perl = TRUE))) hit <- c(hit, id)
  }
  hit
}

## ---- pending_index_notes.csv category classification ---------------------
# No `category` column exists in the file as produced by Session B_batch
# (table, note only). An earlier version of this script inferred a category
# via blunt keyword-matching, which over-matched on words like "recover"/
# "disclos" appearing inside negated clauses ("was NOT recovered") and
# lumped 27 tables into "abstained" when a manual read of all 51 notes
# found only 15 are genuinely blank end-to-end (12 source-truly-
# unrecoverable + 3 commercial-copyright-withheld) -- the other ~12 have
# partial/gradable content (bare item counts matched, option_text/resp
# populated, only item_text or a sub-field missing) and should not be
# excluded wholesale. `pending_index_notes_categorized.csv` is the
# corrected, manually-read category assignment for all 51 rows (one of:
# Item text unrecoverable, Full-recovery documentation-only, Standard-scale
# wording, Table-name mismatch, Commercial-copyright withheld,
# Response-scale incomplete, Undocumented quirk,
# Disclosed-but-wrong-variable-set, Numbering ambiguous, Partial language
# gap, Author-revised wording, Other) written once by hand so this doesn't
# need to be re-derived by keyword-matching in any future grading run.

cat_file <- file.path(SESSION_B, "pending_index_notes_categorized.csv")
if (!file.exists(cat_file)) stop("pending_index_notes_categorized.csv not found -- run the manual categorization pass first")
cats <- read.csv(cat_file, stringsAsFactors = FALSE)
# join case-insensitively: pending_index_notes.csv has one case mismatch
# ("FEDSP_Trzcinska_2023_SMSD" vs the manifest's lowercase
# "fedsp_trzcinska_2023_smsd") inherited from the source file.
notes$.key <- tolower(notes$table)
cats$.key <- tolower(cats$table)
notes <- merge(notes, cats[, c(".key", "category")], by = ".key", all.x = TRUE, sort = FALSE)
notes$.key <- NULL

cat("pending_index_notes.csv category breakdown (corrected, manually read):\n")
print(table(notes$category, useNA = "ifany"))

# Only these two categories mean item_text is blank on the candidate side
# for a source-availability reason across the whole table -- everything
# else (table-name mismatches, numbering ambiguity, incomplete response
# scales, etc.) has real per-item content and flows through normal grading.
ABSTAIN_CATEGORIES <- c("Item text unrecoverable", "Commercial-copyright withheld")

## ---- per-table grading -----------------------------------------------------

metrics_rows <- list()
mismatch_rows <- list()
summary_rows <- list()
comparison_rows <- list()

add_metric <- function(table, item, field, gt_val, cand_val, note = "") {
  er <- edit_ratio(gt_val, cand_val)
  jc <- jaccard(gt_val, cand_val)
  metrics_rows[[length(metrics_rows) + 1]] <<- data.frame(
    table = table, item = item, field = field,
    gt_len = nchar(as.character(gt_val)), cand_len = nchar(as.character(cand_val)),
    edit_ratio = round(er, 4), jaccard = round(jc, 4), note = note,
    stringsAsFactors = FALSE
  )
  list(edit_ratio = er, jaccard = jc)
}

add_mismatch <- function(table, item, category, detail = "") {
  mismatch_rows[[length(mismatch_rows) + 1]] <<- data.frame(
    table = table, item = item, category = category, detail = detail,
    stringsAsFactors = FALSE
  )
}

add_comparison <- function(table, item, field, edit_ratio_v, jaccard_v,
                            ocr_sourced, derived_item, mismatch_category,
                            note_category) {
  comparison_rows[[length(comparison_rows) + 1]] <<- data.frame(
    table = table, item = item, field = field,
    edit_ratio = round(edit_ratio_v, 4), jaccard = round(jaccard_v, 4),
    ocr_sourced = ocr_sourced, derived_item = derived_item,
    mismatch_category = mismatch_category, note_category = note_category,
    stringsAsFactors = FALSE
  )
}

grade_table <- function(nm) {
  gtf <- file.path(SESSION_A, paste0("groundtruth_", nm, ".rds"))
  cf <- file.path(SESSION_B, paste0("candidate_", nm, ".rds"))
  gt <- readRDS(gtf)
  cand <- readRDS(cf)
  gt$item <- as.character(gt$item)
  cand$item <- as.character(cand$item)

  txt <- read_log(nm)
  ocr_sourced <- get_ocr_sourced(txt)
  source_type_used <- get_source_type(txt)
  all_item_ids <- union(unique(gt$item), unique(cand$item))
  derived_items <- get_derived_items(txt, all_item_ids)

  note_row <- notes[tolower(notes$table) == tolower(nm), ]
  note_category <- if (nrow(note_row) > 0) note_row$category[1] else NA_character_

  # "extraction abstained" tables: item text withheld/unrecoverable across
  # the whole table per the audited note -- reported in a dedicated section
  # and excluded from the main aggregate's summary rollup, but NOT used to
  # bypass per-item grading below: item/field pairs that are genuinely
  # blank on both sides are already skipped by the is_missing() checks in
  # each loop, and pairs that aren't blank (e.g. a table tagged unrecoverable
  # for item_text but with option_text/resp fully populated) should still
  # be graded normally rather than discarded wholesale.
  abstained <- !is.na(note_category) && note_category %in% ABSTAIN_CATEGORIES

  gt_items <- unique(gt$item)
  cand_items <- unique(cand$item)
  missed <- setdiff(gt_items, cand_items)
  extra <- setdiff(cand_items, gt_items)
  common <- intersect(gt_items, cand_items)

  for (it in missed) { add_mismatch(nm, it, "missed_item"); add_comparison(nm, it, "item", NA, NA, ocr_sourced, it %in% derived_items, "missed_item", note_category) }
  for (it in extra) { add_mismatch(nm, it, "extra_hallucinated_item"); add_comparison(nm, it, "item", NA, NA, ocr_sourced, it %in% derived_items, "extra_hallucinated_item", note_category) }

  # tripwire-only: item coverage
  item_coverage_ok <- (length(missed) == 0) && (length(extra) == 0)

  # tripwire-only: resp-set alignment
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
    if (!same_set) add_mismatch(nm, it, "wrong_resp_option_mapping", "resp value sets differ")

    is_derived <- it %in% derived_items
    ot_transl_col <- get_translated_col(g, "option_text")
    if ("option_text" %in% names(g) && "option_text" %in% names(c)) {
      for (rv in intersect(g_resp, c_resp)) {
        gv <- g[["option_text"]][suppressWarnings(as.numeric(g$resp)) == rv][1]
        gvt <- if (!is.na(ot_transl_col)) g[[ot_transl_col]][suppressWarnings(as.numeric(g$resp)) == rv][1] else NA_character_
        cv <- c[["option_text"]][suppressWarnings(as.numeric(c$resp)) == rv][1]
        if (!is_missing(gv) || !is_missing(gvt) || !is_missing(cv)) {
          if (is_missing(gv) && is_missing(gvt) && !is_missing(cv)) {
            add_mismatch(nm, it, "wrong_resp_option_mapping", paste0("resp=", rv, " presence mismatch"))
          } else if (!is_missing(cv) && (!is_missing(gv) || !is_missing(gvt))) {
            bm <- best_gt_match(gv, gvt, cv)
            m <- add_metric(nm, it, paste0("option_text[resp=", rv, "]"), bm$val, cv, note = bm$used)
            mcat <- if (m$edit_ratio < LOW_SIMILARITY_THRESHOLD) "low_text_similarity" else NA_character_
            if (!is.na(mcat)) add_mismatch(nm, it, mcat, paste0("option_text resp=", rv))
            if (!is_derived) option_text_scores <- c(option_text_scores, m$edit_ratio)
            add_comparison(nm, it, paste0("option_text[resp=", rv, "]"), m$edit_ratio, m$jaccard, ocr_sourced, is_derived, mcat, note_category)
          } else if (is_missing(cv) && (!is_missing(gv) || !is_missing(gvt))) {
            add_mismatch(nm, it, "wrong_resp_option_mapping", paste0("resp=", rv, " presence mismatch"))
          }
        }
      }
    }
  }
  resp_alignment_rate <- if (gt_resp_ever_populated && length(resp_set_matches) > 0) mean(resp_set_matches) else NA

  item_text_scores <- c(); item_text_jaccard <- c()
  gt_it_vec <- collapse_item(gt, "item", "item_text")[common]
  cand_it_vec <- collapse_item(cand, "item", "item_text")[common]
  it_transl_col <- get_translated_col(gt, "item_text")
  gt_it_transl_vec <- if (!is.na(it_transl_col)) collapse_item(gt, "item", it_transl_col)[common] else rep(NA_character_, length(common))
  for (i in seq_along(common)) {
    it <- common[i]
    gv <- gt_it_vec[i]; gvt <- gt_it_transl_vec[i]; cv <- cand_it_vec[i]
    is_derived <- it %in% derived_items
    if (is_missing(gv) && is_missing(gvt) && is_missing(cv)) {
      # genuinely undefined comparison (blank on both sides) -- not scored.
      # Reported separately (count only) when the table is in one of the
      # two genuine-abstention categories; otherwise silently skipped, same
      # as any other optional blank field.
      if (abstained) add_comparison(nm, it, "item_text", NA, NA, ocr_sourced, is_derived, "extraction_abstained", note_category)
      next
    }
    bm <- best_gt_match(gv, gvt, cv)
    m <- add_metric(nm, it, "item_text", bm$val, cv, note = bm$used)
    mcat <- if (m$edit_ratio < LOW_SIMILARITY_THRESHOLD) "low_text_similarity" else NA_character_
    if (!is.na(mcat)) add_mismatch(nm, it, mcat, "item_text")
    if (!is_derived) { item_text_scores <- c(item_text_scores, m$edit_ratio); item_text_jaccard <- c(item_text_jaccard, m$jaccard) }
    add_comparison(nm, it, "item_text", m$edit_ratio, m$jaccard, ocr_sourced, is_derived, mcat, note_category)
  }

  gt_instr_vec <- collapse_item(gt, "item", "instructions")[common]
  gt_sp_vec <- collapse_item(gt, "item", "section_prompt")[common]
  cand_instr_vec <- collapse_item(cand, "item", "instructions")[common]
  cand_sp_vec <- collapse_item(cand, "item", "section_prompt")[common]
  instr_transl_col <- get_translated_col(gt, "instructions")
  sp_transl_col <- get_translated_col(gt, "section_prompt")
  gt_instr_transl_vec <- if (!is.na(instr_transl_col)) collapse_item(gt, "item", instr_transl_col)[common] else rep(NA_character_, length(common))
  gt_sp_transl_vec <- if (!is.na(sp_transl_col)) collapse_item(gt, "item", sp_transl_col)[common] else rep(NA_character_, length(common))
  context_scores <- c(); direct_scores <- c(); swap_scores <- c(); swap_flags <- 0
  for (i in seq_along(common)) {
    it <- common[i]
    gi <- gt_instr_vec[i]; gs <- gt_sp_vec[i]
    git <- gt_instr_transl_vec[i]; gst <- gt_sp_transl_vec[i]
    ci <- cand_instr_vec[i]; cs <- cand_sp_vec[i]
    if (is_missing(gi) && is_missing(git) && is_missing(gs) && is_missing(gst)) next
    is_derived <- it %in% derived_items

    # bilingual GT: use whichever of primary/translated wording best matches
    # the candidate's own field before running swap detection.
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

    direct_scores <- c(direct_scores, sc_direct)
    swap_scores <- c(swap_scores, sc_swap)

    if (sc_swap > sc_direct + 0.15) {
      context_scores <- c(context_scores, sc_swap)
      swap_flags <- swap_flags + 1
      add_metric(nm, it, "instructions_or_section_prompt(swap-detected)",
                 paste0("instr=", substr(gi, 1, 40), " | sp=", substr(gs, 1, 40)),
                 paste0("instr=", substr(ci, 1, 40), " | sp=", substr(cs, 1, 40)),
                 "field_placement_swap_suspected")
      add_mismatch(nm, it, "wrong_section_assignment", "instructions/section_prompt swap suspected")
      add_comparison(nm, it, "instructions_or_section_prompt", sc_swap, NA, ocr_sourced, is_derived, "field_placement_swap_suspected", note_category)
    } else {
      context_scores <- c(context_scores, sc_direct)
      if (!is_missing(gi) || !is_missing(git)) {
        m <- add_metric(nm, it, "instructions", bm_i_direct$val, ci, note = bm_i_direct$used)
        add_comparison(nm, it, "instructions", m$edit_ratio, m$jaccard, ocr_sourced, is_derived, NA, note_category)
      }
      if (!is_missing(gs) || !is_missing(gst)) {
        m <- add_metric(nm, it, "section_prompt", bm_s_direct$val, cs, note = bm_s_direct$used)
        add_comparison(nm, it, "section_prompt", m$edit_ratio, m$jaccard, ocr_sourced, is_derived, NA, note_category)
      }
    }
  }

  list(
    summary = data.frame(
      table = nm,
      n_gt_items = length(gt_items),
      n_cand_items = length(cand_items),
      n_missed_items = length(missed),
      n_extra_items = length(extra),
      item_coverage_ok = item_coverage_ok,
      resp_alignment_rate = round(resp_alignment_rate, 4),
      mean_item_text_similarity = if (length(item_text_scores) > 0) round(mean(item_text_scores), 4) else NA,
      median_item_text_similarity = if (length(item_text_scores) > 0) round(median(item_text_scores), 4) else NA,
      mean_item_text_jaccard = if (length(item_text_jaccard) > 0) round(mean(item_text_jaccard), 4) else NA,
      median_item_text_jaccard = if (length(item_text_jaccard) > 0) round(median(item_text_jaccard), 4) else NA,
      n_item_text_graded = length(item_text_scores),
      mean_option_text_similarity = if (length(option_text_scores) > 0) round(mean(option_text_scores), 4) else NA,
      median_option_text_similarity = if (length(option_text_scores) > 0) round(median(option_text_scores), 4) else NA,
      n_option_text_graded = length(option_text_scores),
      mean_context_similarity = if (length(context_scores) > 0) round(mean(context_scores), 4) else NA,
      n_context_graded = length(context_scores),
      n_context_swap_detected = swap_flags,
      ocr_sourced = ocr_sourced,
      source_type_used = source_type_used,
      n_derived_items = length(intersect(derived_items, common)),
      note_category = note_category,
      extraction_abstained = abstained,
      stringsAsFactors = FALSE
    )
  )
}

results <- list()
for (nm in manifest$table) {
  cat("Grading", nm, "...\n")
  res <- tryCatch(grade_table(nm), error = function(e) {
    cat("ERROR on", nm, ":", conditionMessage(e), "\n")
    NULL
  })
  if (!is.null(res)) results[[nm]] <- res
}

summary_df <- do.call(rbind, lapply(results, function(x) x$summary))
metrics_df <- do.call(rbind, metrics_rows)
mismatch_df <- do.call(rbind, mismatch_rows)
comparison_df <- do.call(rbind, comparison_rows)

mismatch_df <- mismatch_df[mismatch_df$category %in% c(
  "missed_item", "extra_hallucinated_item", "wrong_section_assignment",
  "wrong_resp_option_mapping", "truncated_text", "low_text_similarity"
), , drop = FALSE]
# derived_item_reasonable_variation: a mismatch on an item already tagged
# derived_item=TRUE in comparison_df may just be reasonable rewording of a
# computed/recoded value, not an extraction error -- flag rather than drop.
mismatch_df$derived_item_reasonable_variation <- FALSE
if (nrow(mismatch_df) > 0) {
  di_lookup <- unique(comparison_df[comparison_df$derived_item, c("table", "item")])
  di_lookup$key <- paste(di_lookup$table, di_lookup$item)
  mismatch_df$derived_item_reasonable_variation <- paste(mismatch_df$table, mismatch_df$item) %in% di_lookup$key
}

## ---- join manifest stratification vars into comparison_long --------------

strat_cols <- c("table", "has_bare_integer_items", "has_multi_option", "n_items", "n_sections")
comparison_df <- merge(comparison_df, manifest[, strat_cols], by = "table", all.x = TRUE, sort = FALSE)

write.csv(summary_df, "summary_table.csv", row.names = FALSE)
write.csv(metrics_df, "metrics.csv", row.names = FALSE)
write.csv(mismatch_df, "mismatch_detail.csv", row.names = FALSE)
write.csv(comparison_df, "comparison_long.csv", row.names = FALSE)

cat("\n=== SUMMARY (first 10 rows) ===\n")
print(head(summary_df, 10))
cat("\nWrote summary_table.csv (", nrow(summary_df), "rows), metrics.csv (", nrow(metrics_df),
    "rows), mismatch_detail.csv (", nrow(mismatch_df), "rows), comparison_long.csv (", nrow(comparison_df), "rows)\n")

saveRDS(results, "grade_results.rds")
