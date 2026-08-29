##Construct descriptions: paraphrase the tags sheet's "Context Text" column.
##
##Issue #1406. Column 4 of the "IRW Tags" sheet holds excerpts pulled close to
##verbatim from source papers. 03_tags.R deliberately never reads that column --
##its positional c(1,6:12,3) selection is the only thing keeping raw paper text
##out of the public CSVs. This script is the ONE sanctioned consumer of column 4,
##and it exists to make that text usable without republishing it: every excerpt
##is paraphrased by an LLM, checked for verbatim overlap, and only the paraphrase
##is ever written to disk.
##
##Two invariants, both load-bearing for the copyright position:
##
##  1. Raw excerpt text is NEVER persisted. Not in the cache, not in the output,
##     not in a log. The Google Sheet stays the sole store. The cache keys on a
##     hash of the excerpt, which is why it can be committed to a public repo.
##  2. A paraphrase sharing a run of N_GRAM+ consecutive tokens with its source is
##     not published. It gets provenance = "pending review" and a NA description
##     until a human clears it. The cache does retain that flagged paraphrase --
##     which, being flagged, is by definition close to its source -- so --review
##     has something to show. That is contained rather than published: the cache
##     is gitignored (metadata/**/*.csv), is not in upload_meta.py's
##     FILE_TABLE_MAP, and the flagged text never reaches the public CSV.
##
##The LLM is Stanford's AI API Gateway rather than a public API -- counsel's
##guidance on issue #1406 asks that paywalled source text stay in a closed
##environment, and the gateway is approved for High Risk data. It is LiteLLM
##behind an OpenAI-compatible surface, so this does NOT reuse 02_biblio.R's
##anthropic_chat() directly: same httr/jsonlite idiom, different auth header and
##a different path to the reply text.
##
##Usage:
##  Rscript 03b_describe.R                # describe uncached rows, write outputs
##  Rscript 03b_describe.R --limit=20     # pilot: only the first 20 uncached rows
##  Rscript 03b_describe.R --review       # print raw vs rewrite for flagged rows
##  Rscript 03b_describe.R --list-models  # what the gateway actually offers
##  Rscript 03b_describe.R --stub         # no network; fixed text, for testing
##  Rscript 03b_describe.R --stub-copy    # no network; echoes the excerpt back,
##                                        # which MUST trip the overlap flag

library(gsheet)
library(httr)
library(jsonlite)
library(digest)

##---------------------------------------------------------------- config ----

##Same sheet as 03_tags.R's dbs$core. Kept as a literal rather than sourced from
##03_tags.R: that script runs its whole pipeline on source(), and this one must
##not trigger a tags.csv rewrite as a side effect.
SHEET_URL <- 'https://docs.google.com/spreadsheets/d/1V3ef0sa7HKtJJd2cgqRAkEdfbpGWDD1JIyQa6HwVK7g/edit?gid=126134123#gid=126134123'

CACHE_FILE  <- "describe_cache.csv"
OUTPUT_FILE <- "construct_descriptions.csv"

##Stanford AI API Gateway. OpenAI-compatible (LiteLLM), Bearer auth.
##https://uit.stanford.edu/service/ai-api-gateway
GATEWAY_BASE    <- "https://aiapi-prod.stanford.edu/v1"
GATEWAY_URL     <- paste0(GATEWAY_BASE, "/chat/completions")
GATEWAY_KEY_VAR <- "STANFORD_AI_API_KEY"

##The gateway fronts Anthropic/OpenAI/Google/Meta/DeepSeek. This id is the one
##Stanford's own docs show in a worked example; the gateway's catalogue moves, so
##confirm with --list-models before a full run rather than trusting this default.
GATEWAY_MODEL <- "claude-3-7-sonnet"

MAX_TOKENS <- 300
##Overlap threshold, confirmed with Ben 2026-08-29. Any shared run of 6+
##consecutive tokens between excerpt and paraphrase flags the row. This is the
##main copyright-risk lever -- do not loosen it without asking.
N_GRAM <- 6
CACHE_FLUSH_EVERY <- 25   # partial-progress writes, so a killed run loses <=25 calls
RETRY_MAX <- 4

##Column positions in the 13-column sheet. Positional for the same reason
##03_tags.R is positional -- see its comment block. Header names as of
##2026-08-29: table, Rater, Construct Name, Context Text, Item text available?,
##Age Range, Child Age, Sample, Construct type, Measurement tool, Item format,
##Primary Language(s), Notes
COL_TABLE <- 1; COL_CONSTRUCT <- 3; COL_CONTEXT <- 4
COL_SAMPLE <- 8; COL_CTYPE <- 9; COL_TOOL <- 10; COL_FORMAT <- 11
N_COLS_MIN <- 12

INSTRUCTION_SENTINEL <- "should match what is on redivis"

##------------------------------------------------------------------ args ----

args <- commandArgs(trailingOnly = TRUE)
has_flag <- function(f) any(args == f)
flag_val <- function(prefix, default = NA) {
    hit <- grep(paste0("^", prefix, "="), args, value = TRUE)
    if (length(hit) == 0) return(default)
    sub(paste0("^", prefix, "="), "", hit[1])
}

OPT_REVIEW   <- has_flag("--review")
OPT_LIST     <- has_flag("--list-models")
OPT_STUB     <- has_flag("--stub")
OPT_STUBCOPY <- has_flag("--stub-copy")
OPT_LIMIT    <- suppressWarnings(as.integer(flag_val("--limit")))
if (!is.null(GATEWAY_MODEL)) GATEWAY_MODEL <- flag_val("--model", GATEWAY_MODEL)

##------------------------------------------------------------- gateway ------

gateway_key <- function() {
    key <- Sys.getenv(GATEWAY_KEY_VAR)
    if (nchar(key) == 0) {
        stop(GATEWAY_KEY_VAR, " is not set. Request a key via the 'Add AI API ",
             "Gateway Key' form linked from ",
             "https://uit.stanford.edu/service/ai-api-gateway, then export it. ",
             "Use --stub to exercise everything except the LLM calls.")
    }
    key
}

list_models <- function() {
    r <- GET(paste0(GATEWAY_BASE, "/models"),
             add_headers(Authorization = paste("Bearer", gateway_key())))
    if (status_code(r) != 200) stop("gateway /models returned ", status_code(r))
    ids <- sapply(content(r, as = "parsed")$data, function(x) x$id)
    cat(paste(sort(unlist(ids)), collapse = "\n"), "\n")
}

##Single point of contact with the LLM. Everything else in this script is
##deterministic and testable without a key.
describe_chat <- function(prompt, model = GATEWAY_MODEL, max_tokens = MAX_TOKENS) {
    body <- toJSON(list(
        model = model,
        max_tokens = max_tokens,
        messages = list(list(role = "user", content = prompt))
    ), auto_unbox = TRUE)

    for (attempt in seq_len(RETRY_MAX)) {
        r <- POST(GATEWAY_URL,
                  add_headers(Authorization = paste("Bearer", gateway_key())),
                  content_type_json(), body = body)
        code <- status_code(r)
        if (code == 200) {
            parsed <- content(r, as = "parsed")
            ##OpenAI shape, not Anthropic's content[[1]]$text -- the one real
            ##difference from 02_biblio.R's anthropic_chat().
            if (length(parsed$choices) == 0) return(NA_character_)
            return(trimws(parsed$choices[[1]]$message$content))
        }
        if (code == 429 || code >= 500) {
            wait <- 2^attempt
            message("  gateway ", code, ", retrying in ", wait, "s")
            Sys.sleep(wait)
            next
        }
        stop("gateway error ", code, ": ",
             substr(rawToChar(r$content), 1, 300))
    }
    stop("gateway still failing after ", RETRY_MAX, " attempts")
}

if (OPT_STUB) {
    describe_chat <- function(prompt, ...)
        "A stub description produced without contacting any model."
}
if (OPT_STUBCOPY) {
    ##Deliberately adversarial: echoes the excerpt straight back, so a working
    ##overlap check MUST flag every sourced row. Verification only.
    describe_chat <- function(prompt, ...) {
        m <- regmatches(prompt, regexpr("(?s)Excerpt: .*$", prompt, perl = TRUE))
        if (length(m) == 0) return("Stub copy with no excerpt available.")
        sub("^Excerpt: ", "", m)
    }
}

##--------------------------------------------------------------- sheet ------

get_sheet <- function() {
    sh <- gsheet2tbl(SHEET_URL)

    ##Both guards lifted from 03_tags.R. A column reorder would silently change
    ##which column this script treats as the verbatim excerpt, so the shape is
    ##asserted rather than assumed.
    if (ncol(sh) < N_COLS_MIN) {
        stop("tags sheet: expected at least ", N_COLS_MIN, " columns, found ",
             ncol(sh), ". Sheet layout changed -- re-check the COL_* positions ",
             "before proceeding.")
    }
    first <- trimws(as.character(sh[[1]][1]))
    if (is.na(first) || !identical(tolower(first), INSTRUCTION_SENTINEL)) {
        stop("tags sheet: expected the instruction row ('", INSTRUCTION_SENTINEL,
             "') directly under the header, found '", first,
             "'. Refusing to drop row 1 -- it looks like real data.")
    }
    if (!identical(tolower(trimws(names(sh)[COL_CONTEXT])), "context text")) {
        stop("tags sheet: column ", COL_CONTEXT, " is '", names(sh)[COL_CONTEXT],
             "', not 'Context Text'. Columns have been reordered -- the excerpt ",
             "column must be identified correctly or raw text could leak.")
    }
    sh <- sh[-1, ]

    blank <- function(x) { x <- trimws(as.character(x)); ifelse(is.na(x) | x == "", NA, x) }
    d <- data.frame(
        table          = tolower(blank(sh[[COL_TABLE]])),
        construct_name = blank(sh[[COL_CONSTRUCT]]),
        context_text   = blank(sh[[COL_CONTEXT]]),
        sample         = blank(sh[[COL_SAMPLE]]),
        construct_type = blank(sh[[COL_CTYPE]]),
        tool           = blank(sh[[COL_TOOL]]),
        item_format    = blank(sh[[COL_FORMAT]]),
        stringsAsFactors = FALSE
    )
    d <- d[!is.na(d$table), ]
    d <- d[!duplicated(d$table), ]

    ##Keys on the excerpt, so editing an excerpt in the sheet invalidates its
    ##cached paraphrase and earns a fresh call. paste() over NA is fine and
    ##stable -- a blank excerpt hashes consistently across runs.
    d$row_hash <- vapply(seq_len(nrow(d)),
                         function(i) digest(paste(d$table[i], d$context_text[i])),
                         character(1))
    d
}

##------------------------------------------------------------ overlap QC ----

tokenize <- function(x) {
    if (is.na(x)) return(character(0))
    x <- tolower(x)
    x <- gsub("[^a-z0-9 ]+", " ", x)
    t <- strsplit(trimws(x), "\\s+")[[1]]
    t[nchar(t) > 0]
}

ngrams <- function(tokens, n) {
    if (length(tokens) < n) return(character(0))
    vapply(seq_len(length(tokens) - n + 1),
           function(i) paste(tokens[i:(i + n - 1)], collapse = " "),
           character(1))
}

##TRUE if the paraphrase reuses any run of N_GRAM consecutive tokens from the
##source. Returns the shared runs too, so --review can show a human exactly what
##tripped it rather than just asserting that something did.
##
##The window shrinks for excerpts shorter than N_GRAM tokens. A fixed 6 would
##make them unflaggable -- 163 of 2342 non-blank excerpts on the sheet are under
##6 tokens (2026-08-29), and a model echoing one back wholesale would have sailed
##through as "sourced". Short excerpts are the least copyright-sensitive case,
##but silently exempting 7% of rows from the only check we have is not a
##defensible default.
overlap <- function(excerpt, rewrite) {
    te <- tokenize(excerpt)
    n <- min(N_GRAM, length(te))
    if (n < 2) return(list(flag = FALSE, shared = character(0)))
    shared <- intersect(ngrams(te, n), ngrams(tokenize(rewrite), n))
    list(flag = length(shared) > 0, shared = shared, n = n)
}

##------------------------------------------------------------- prompts ------

prompt_rewrite <- function(context_text) {
    paste0(
"You will be given a short excerpt describing a psychometric instrument,\n",
"pulled from a research paper. Write a 1-2 sentence description of what\n",
"this instrument measures, in a completely different sentence structure\n",
"than the original. Do not preserve the original's phrasing, clause\n",
"order, or any quoted language. Do not copy any string of ", N_GRAM, "+ consecutive\n",
"words from the excerpt. Focus on: what construct is measured, who was\n",
"measured, and how (if stated). Do not editorialize or evaluate the\n",
"instrument's quality.\n\n",
"Excerpt: ", context_text)
}

prompt_fallback <- function(row) {
    f <- function(x) if (is.na(x)) "(not recorded)" else x
    paste0(
"No source description is available. Using only these structured fields,\n",
"write one factual sentence describing this measure: construct type\n",
"= ", f(row$construct_type), ", sample = ", f(row$sample),
", measurement tool = ", f(row$tool), ", item format = ", f(row$item_format),
". Do not speculate beyond these fields.")
}

##--------------------------------------------------------------- cache ------

CACHE_COLS <- c("row_hash", "table", "construct_description",
                "similarity_flag", "provenance", "reviewed")

read_cache <- function() {
    if (!file.exists(CACHE_FILE)) {
        e <- data.frame(matrix(ncol = length(CACHE_COLS), nrow = 0))
        names(e) <- CACHE_COLS
        e$similarity_flag <- logical(0); e$reviewed <- logical(0)
        return(e)
    }
    ch <- read.csv(CACHE_FILE, stringsAsFactors = FALSE, colClasses = "character")
    missing <- setdiff(CACHE_COLS, names(ch))
    if (length(missing) > 0) stop("cache is missing columns: ", paste(missing, collapse = ", "))
    ch$similarity_flag <- toupper(ch$similarity_flag) %in% c("TRUE", "T")
    ch$reviewed        <- toupper(ch$reviewed) %in% c("TRUE", "T")
    ch
}

write_cache <- function(ch) {
    ##Guard, not decoration: the cache is committed to a public repo, so a
    ##context_text column reaching it is the exact failure this design exists to
    ##prevent. Fail loudly rather than write it.
    stray <- setdiff(names(ch), CACHE_COLS)
    if (length(stray) > 0) {
        stop("refusing to write cache with unexpected column(s): ",
             paste(stray, collapse = ", "),
             " -- the cache must never carry raw excerpt text.")
    }
    readr::write_csv(ch[, CACHE_COLS], CACHE_FILE, na = "NA")
}

##---------------------------------------------------------------- review ----

review_flagged <- function(sheet, ch) {
    pending <- ch[ch$provenance == "pending review" & !ch$reviewed, ]
    if (nrow(pending) == 0) { cat("No rows pending review.\n"); return(invisible()) }

    ##Raw text is pulled live from the sheet for this view and never stored --
    ##`sheet` is in memory only.
    m <- merge(pending, sheet[, c("row_hash", "context_text")], by = "row_hash")
    cat(nrow(m), " row(s) pending review. Threshold: any shared ", N_GRAM,
        "-gram.\n\n", sep = "")
    for (i in seq_len(nrow(m))) {
        ov <- overlap(m$context_text[i], m$construct_description[i])
        cat(strrep("=", 78), "\n", m$table[i], "  [", m$row_hash[i], "]\n", sep = "")
        cat("\n-- RAW (from sheet, not stored) --\n", m$context_text[i], "\n", sep = "")
        cat("\n-- REWRITE --\n", m$construct_description[i], "\n", sep = "")
        cat("\n-- SHARED ", ov$n, "-GRAMS --\n", sep = "")
        cat(paste0("  * ", ov$shared, collapse = "\n"), "\n\n")
    }
    cat(strrep("=", 78), "\n")
    cat("To clear a row: set reviewed = TRUE on its row_hash in ", CACHE_FILE,
        "\nand re-run without --review. It will publish as provenance = 'sourced'.\n",
        sep = "")
}

##----------------------------------------------------------------- main -----

if (OPT_LIST) { list_models(); quit(save = "no") }

sheet <- get_sheet()
cache <- read_cache()
cat("sheet: ", nrow(sheet), " rows | cache: ", nrow(cache), " entries\n", sep = "")

if (OPT_REVIEW) { review_flagged(sheet, cache); quit(save = "no") }

todo <- sheet[!(sheet$row_hash %in% cache$row_hash), ]
if (!is.na(OPT_LIMIT) && OPT_LIMIT < nrow(todo)) {
    cat("--limit=", OPT_LIMIT, ": describing ", OPT_LIMIT, " of ", nrow(todo),
        " uncached rows\n", sep = "")
    todo <- todo[seq_len(OPT_LIMIT), ]
}
cat(nrow(todo), " row(s) to describe (",
    sum(sheet$row_hash %in% cache$row_hash), " reused from cache, ",
    nrow(sheet) - nrow(todo) - sum(sheet$row_hash %in% cache$row_hash),
    " not attempted this run)\n", sep = "")

if (nrow(todo) > 0) {
    if (!OPT_STUB && !OPT_STUBCOPY) gateway_key()   # fail before the first call, not mid-run
    new <- vector("list", nrow(todo))
    for (i in seq_len(nrow(todo))) {
        row <- todo[i, ]
        sourced <- !is.na(row$context_text)
        txt <- describe_chat(if (sourced) prompt_rewrite(row$context_text)
                             else prompt_fallback(row))

        if (!sourced) {
            flag <- FALSE; prov <- "inferred"
        } else {
            flag <- overlap(row$context_text, txt)$flag
            prov <- if (flag) "pending review" else "sourced"
        }

        new[[i]] <- data.frame(row_hash = row$row_hash, table = row$table,
                               construct_description = txt, similarity_flag = flag,
                               provenance = prov, reviewed = FALSE,
                               stringsAsFactors = FALSE)

        cat(sprintf("[%d/%d] %-40s %s%s\n", i, nrow(todo), row$table, prov,
                    if (flag) "  <-- FLAGGED" else ""))

        if (i %% CACHE_FLUSH_EVERY == 0) {
            write_cache(rbind(cache, do.call(rbind, new[seq_len(i)])))
            cat("  ...cache flushed at ", i, "\n", sep = "")
        }
        if (!OPT_STUB && !OPT_STUBCOPY) Sys.sleep(1)   # rate courtesy, as 02_biblio.R does
    }
    cache <- rbind(cache, do.call(rbind, new))
    write_cache(cache)
}

##---------------------------------------------------------------- output ----

out <- merge(sheet[, c("row_hash", "table", "construct_name")],
             cache[, c("row_hash", "construct_description", "provenance", "reviewed")],
             by = "row_hash", all.x = FALSE)

##A human-cleared row publishes as sourced; an uncleared flagged row publishes
##with no description at all. Never auto-publish a paraphrase that sits too close
##to its source.
cleared <- out$provenance == "pending review" & out$reviewed
out$provenance[cleared] <- "sourced"
still_pending <- out$provenance == "pending review"
out$construct_description[still_pending] <- NA

out <- out[order(out$table), c("table", "construct_name", "construct_description", "provenance")]
readr::write_csv(out, OUTPUT_FILE, na = "NA")

cat("\nwrote ", OUTPUT_FILE, ": ", nrow(out), " rows\n", sep = "")
print(table(out$provenance, useNA = "ifany"))
np <- sum(still_pending)
if (np > 0) {
    cat("\n", np, " row(s) pending review (description withheld).",
        "\nRun: Rscript 03b_describe.R --review\n", sep = "")
}
stale <- sum(!(cache$row_hash %in% sheet$row_hash))
if (stale > 0) cat(stale, " stale cache entries (excerpt edited or table removed).\n")
