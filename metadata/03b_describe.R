##Construct descriptions: say what each table measures (issue #1406).
##
##The goal is to offer additional information about the construct a table
##measures, assembled from whatever evidence IRW holds. It is NOT "paraphrase
##one column" -- an earlier draft was built that way and it inherited the
##weaknesses of its single source. Here every available signal for a unit is
##gathered into one bundle, the model sees the bundle, and ONE description comes
##back out.
##
##Evidence, in the order a reader would weigh it:
##
##  construct name        tags.csv, 55% of tables
##  dictionary Description biblio.csv, 98% -- the widest signal we have
##  structured tags       construct type / sample / tool / item format / language
##  instrument label      itemtext_metadata.csv, 14%
##  Context Text          tags sheet column 4          RESTRICTED
##  item wording          items_alltext.Rdata          RESTRICTED
##  paper abstract        OpenAlex via DOI or title    RESTRICTED
##  table name            the authorname_year_construct convention, 100%
##
##Three invariants, all load-bearing for the rights position:
##
##  1. RESTRICTED SOURCE text is never persisted by this script. Context Text
##     stays in the Sheet, item wording stays in items_alltext.Rdata, abstracts
##     are fetched into memory and dropped. The cache keys on a hash of the
##     bundle, never the bundle itself.
##
##     Be precise about the one thing the cache DOES retain: a flagged
##     description, which by definition sits close to its source. That is
##     deliberate -- --review has to show a human what tripped the check -- and
##     it is contained rather than published: the cache is gitignored and the
##     flagged text is blanked out of the public CSV. It is NOT a claim that
##     nothing source-shaped is ever on disk.
##
##     --stub-copy is the exception that proves it. Its "description" IS the
##     restricted text, by construction, so that mode writes nothing at all.
##  2. A description sharing a run of N_GRAM+ consecutive tokens with ANY
##     restricted input that fed it is not published. It gets provenance
##     "pending review" and a NA description until a human clears it. This is
##     the check that must not be loosened: the earlier draft only ever compared
##     against Context Text, which left item wording and abstracts unguarded.
##  3. Item wording from a rights-barred instrument never enters a bundle at
##     all. "A derivative of a barred instrument stays barred" -- paraphrasing
##     withdrawn wording would reintroduce exactly what was withdrawn. The gate
##     is itemtext_rights_exclusions.csv and it is fail-closed.
##
##The unit of description is the CONSTRUCT, not the table, wherever a construct
##name exists (2299 of 4221 tables): all 26 PISA tables should read alike. The
##remaining tables are keyed on themselves. Output is one row per table either
##way, so the join is unaffected; construct_key makes the reuse visible.
##
##Usage:
##  Rscript 03b_describe.R                 # describe uncached units
##  Rscript 03b_describe.R --sample        # the stratified 20-row sample
##  Rscript 03b_describe.R --limit=20      # first 20 uncached units
##  Rscript 03b_describe.R --review        # raw vs rewrite for flagged units
##  Rscript 03b_describe.R --list-models   # what the gateway actually offers
##  Rscript 03b_describe.R --stub          # no network; fixed text
##  Rscript 03b_describe.R --stub-copy     # no network; echoes restricted text
##                                         # back, which MUST trip every flag

library(gsheet)
library(httr)
library(jsonlite)
library(digest)
source("gsheet_retry.R")   ## masks gsheet2tbl with a retrying version

##---------------------------------------------------------------- config ----

##Same sheet as 03_tags.R's dbs$core. Kept as a literal rather than sourced from
##03_tags.R: that script runs its whole pipeline on source(), and this one must
##not trigger a tags.csv rewrite as a side effect.
SHEET_URL <- 'https://docs.google.com/spreadsheets/d/1V3ef0sa7HKtJJd2cgqRAkEdfbpGWDD1JIyQa6HwVK7g/edit?gid=126134123#gid=126134123'

CACHE_FILE      <- "describe_cache.csv"
OUTPUT_FILE     <- "construct_descriptions.csv"
SHARE_FILE      <- "construct_descriptions_sample.csv"
EXCLUSIONS_FILE <- "itemtext_rights_exclusions.csv"
ITEMTEXT_RDATA  <- "items_alltext.Rdata"

##Stanford AI API Gateway. OpenAI-compatible (LiteLLM), Bearer auth.
##https://uit.stanford.edu/service/ai-api-gateway
GATEWAY_BASE    <- "https://aiapi-prod.stanford.edu/v1"
GATEWAY_URL     <- paste0(GATEWAY_BASE, "/chat/completions")
GATEWAY_KEY_VAR <- "STANFORD_AI_API_KEY"

##Confirmed against the live catalogue 2026-09-05: this is the ONLY model the
##gateway offers. Stanford's docs show `claude-3-7-sonnet` in a worked example
##and it does not exist. Re-check with --list-models before a full run.
GATEWAY_MODEL <- "claude-haiku-4-5"

MAX_TOKENS <- 300
##Overlap threshold, confirmed with Ben 2026-08-29. Any shared run of 6+
##consecutive tokens between a restricted input and the description flags the
##unit. This is the main rights lever -- do not loosen it without asking.
N_GRAM <- 6
CACHE_FLUSH_EVERY <- 25   # partial-progress writes, so a killed run loses <=25
RETRY_MAX <- 4

##Item wording is sampled rather than sent whole: a 200-item instrument would
##swamp the bundle and every other signal in it.
MAX_ITEMS_IN_BUNDLE <- 12

##Column positions in the 13-column tags sheet. Positional for the same reason
##03_tags.R is positional -- see its comment block. The header names are
##asserted below: a reorder must fail loudly, because position 4 is the only
##thing keeping raw excerpts out of the public CSVs.
COL_TABLE <- 1; COL_CONSTRUCT <- 3; COL_CONTEXT <- 4
COL_SAMPLE <- 8; COL_CTYPE <- 9; COL_TOOL <- 10; COL_FORMAT <- 11
COL_LANG <- 12
N_COLS_MIN <- 12

##Every position this script reads, checked by name. The earlier draft asserted
##only column 4's name; a swap of, say, Sample and Construct type would have
##gone through silently and mislabelled every bundle.
COL_NAMES <- c("table", "construct name", "context text", "sample",
               "construct type", "measurement tool", "item format",
               "primary language(s)")
COL_POS   <- c(COL_TABLE, COL_CONSTRUCT, COL_CONTEXT, COL_SAMPLE,
               COL_CTYPE, COL_TOOL, COL_FORMAT, COL_LANG)

INSTRUCTION_SENTINEL <- "should match what is on redivis"

OPENALEX_BASE <- "https://api.openalex.org"
OPENALEX_MAIL <- "ben.domingue@gmail.com"

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
OPT_SAMPLE   <- has_flag("--sample")
OPT_NOFETCH  <- has_flag("--no-abstracts")
OPT_LIMIT    <- suppressWarnings(as.integer(flag_val("--limit")))
GATEWAY_MODEL <- flag_val("--model", GATEWAY_MODEL)

##------------------------------------------------------------- gateway ------

gateway_key <- function() {
    key <- Sys.getenv(GATEWAY_KEY_VAR)
    if (nchar(key) == 0) {
        stop(GATEWAY_KEY_VAR, " is not set. Request a key via the 'Add AI API ",
             "Gateway Key' form linked from ",
             "https://uit.stanford.edu/service/ai-api-gateway, then put it in ",
             "~/.Renviron. Use --stub to exercise everything except the calls.")
    }
    key
}

list_models <- function() {
    r <- GET(paste0(GATEWAY_BASE, "/models"),
             add_headers(Authorization = paste("Bearer", gateway_key())))
    if (status_code(r) != 200) stop("gateway /models returned ", status_code(r))
    ids <- fromJSON(rawToChar(r$content))$data$id
    cat(paste(sort(ids), collapse = "\n"), "\n")
}

##The gateway is LiteLLM behind an OpenAI-compatible surface, so this does NOT
##reuse 02_biblio.R's anthropic_chat(): same httr/jsonlite idiom, different auth
##header and a different path to the reply text.
describe_chat <- function(prompt) {
    key <- gateway_key()
    body <- list(model = GATEWAY_MODEL, max_tokens = MAX_TOKENS,
                 messages = list(list(role = "user", content = prompt)))
    for (attempt in seq_len(RETRY_MAX)) {
        r <- POST(GATEWAY_URL,
                  add_headers(Authorization = paste("Bearer", key),
                              `Content-Type` = "application/json"),
                  body = toJSON(body, auto_unbox = TRUE))
        code <- status_code(r)
        if (code == 200) {
            parsed <- fromJSON(rawToChar(r$content), simplifyVector = FALSE)
            if (length(parsed$choices) == 0) return(NA_character_)
            return(trimws(parsed$choices[[1]]$message$content))
        }
        if (code == 429 || code >= 500) {
            Sys.sleep(2^attempt)
            next
        }
        ##Deliberately does NOT echo the response body: a gateway that mirrors
        ##the request back would put restricted text on stderr, and a CI job
        ##captures stderr.
        stop("gateway error ", code, " (body withheld -- it can contain the prompt)")
    }
    stop("gateway still failing after ", RETRY_MAX, " attempts")
}

##------------------------------------------------------- text utilities -----

tokenize <- function(x) {
    if (is.na(x) || !nzchar(x)) return(character(0))
    x <- tolower(x)
    x <- gsub("[^a-z0-9 ]+", " ", x)
    t <- strsplit(trimws(x), "\\s+")[[1]]
    t[nzchar(t)]
}

ngrams <- function(tok, n) {
    if (length(tok) < n) return(character(0))
    vapply(seq_len(length(tok) - n + 1),
           function(i) paste(tok[i:(i + n - 1)], collapse = " "),
           character(1))
}

##TRUE if the description reuses any run of N_GRAM consecutive tokens from ANY
##restricted input. Returns the shared runs so --review can show a human exactly
##what tripped it rather than merely asserting that something did.
##
##The window shrinks for inputs shorter than N_GRAM tokens: a fixed 6 would make
##short excerpts unflaggable, and a model echoing one back wholesale would sail
##through. Short excerpts are the least sensitive case, but silently exempting
##them from the only check we have is not a defensible default.
overlap <- function(restricted, description) {
    dt <- tokenize(description)
    shared <- character(0); nmin <- NA_integer_
    for (src in restricted) {
        ts <- tokenize(src)
        n <- min(N_GRAM, length(ts))
        if (n < 2) next
        hit <- intersect(ngrams(ts, n), ngrams(dt, n))
        if (length(hit)) {
            shared <- c(shared, hit)
            nmin <- if (is.na(nmin)) n else min(nmin, n)
        }
    }
    list(flag = length(shared) > 0, shared = unique(shared),
         n = if (is.na(nmin)) N_GRAM else nmin)
}

##A reply is only a description if it describes something. The model answers a
##thin bundle by asking for more input ("I need to see the excerpt...", "Could
##you please share..."), and the earlier draft published those verbatim -- 2 of
##17 rows in the 2026-09-05 pilot. It also emits markdown headers, which are
##stripped rather than rejected.
CHATTER <- paste(
    "i need (to see|the actual)", "i don'?t see", "could you (please )?(share|provide)",
    "i'?d be happy to help", "please provide", "you'?ve provided",
    "^(sure|certainly|here'?s|okay)\\b", "as an ai", "i cannot",
    sep = "|")

clean_reply <- function(txt) {
    if (is.na(txt)) return(NA_character_)
    ##Strip leading markdown headers and bold-only preamble lines.
    txt <- gsub("(?m)^#+\\s.*$", "", txt, perl = TRUE)
    txt <- gsub("(?m)^\\*\\*[^*]+\\*\\*:?\\s*$", "", txt, perl = TRUE)
    trimws(gsub("\\s+", " ", txt))
}

is_chatter <- function(txt) {
    if (is.na(txt) || !nzchar(txt)) return(TRUE)
    grepl(CHATTER, tolower(txt), perl = TRUE)
}

##--------------------------------------------------------------- sources ----

blank <- function(x) {
    x <- trimws(as.character(x))
    ifelse(is.na(x) | x == "" | tolower(x) == "na", NA, x)
}
key <- function(x) tolower(trimws(as.character(x)))

##The tags sheet, read for Context Text (column 4) and the structured columns.
##This script is the one sanctioned consumer of column 4.
get_sheet <- function() {
    sh <- gsheet2tbl(SHEET_URL)
    if (ncol(sh) < N_COLS_MIN) {
        stop("Sheet layout changed (", ncol(sh), " cols) -- re-check COL_* ",
             "before proceeding.")
    }
    first <- trimws(as.character(sh[[1]][1]))
    if (!identical(tolower(first), INSTRUCTION_SENTINEL)) {
        stop("Refusing to drop row 1 -- it looks like real data, not the ",
             "instruction row.")
    }
    got <- tolower(trimws(names(sh)[COL_POS]))
    if (!identical(got, COL_NAMES)) {
        stop("Tags sheet columns have moved. Expected at positions ",
             paste(COL_POS, collapse = ","), ": ",
             paste(COL_NAMES, collapse = " | "), "\n  got: ",
             paste(got, collapse = " | "),
             "\nRefusing to run -- position 4 is the only thing keeping raw ",
             "excerpts out of the public CSVs.")
    }
    sh <- sh[-1, ]
    d <- data.frame(
        table          = key(sh[[COL_TABLE]]),
        construct_name = blank(sh[[COL_CONSTRUCT]]),
        context_text   = blank(sh[[COL_CONTEXT]]),
        sample         = blank(sh[[COL_SAMPLE]]),
        construct_type = blank(sh[[COL_CTYPE]]),
        tool           = blank(sh[[COL_TOOL]]),
        item_format    = blank(sh[[COL_FORMAT]]),
        language       = blank(sh[[COL_LANG]]),
        stringsAsFactors = FALSE)
    d <- d[!is.na(d$table), ]
    d[!duplicated(d$table), ]
}

read_csv_if <- function(f) {
    if (!file.exists(f)) return(NULL)
    read.csv(f, stringsAsFactors = FALSE, colClasses = "character")
}

##Rights gate. Fail-closed: a table matching a named exclusion or an instrument
##pattern contributes no item wording. Exact-table rows and pattern rows are
##both honoured; patterns catch instruments we have not enumerated yet.
load_exclusions <- function() {
    ex <- read_csv_if(EXCLUSIONS_FILE)
    if (is.null(ex)) {
        stop(EXCLUSIONS_FILE, " is missing. It is the rights gate on item ",
             "wording -- refusing to run without it.")
    }
    list(tables   = key(ex$table[nzchar(trimws(ex$table))]),
         patterns = trimws(ex$instrument_pattern[nzchar(trimws(ex$instrument_pattern))]))
}

item_barred <- function(tab, instrument, ex) {
    if (key(tab) %in% ex$tables) return(TRUE)
    if (!is.na(instrument) && length(ex$patterns)) {
        if (any(grepl(paste(ex$patterns, collapse = "|"), instrument,
                      ignore.case = TRUE))) return(TRUE)
    }
    FALSE
}

##Item wording, from the local cache 08_itemtext.R already writes. Never
##re-persisted by this script.
load_itemtext <- function(ex) {
    if (!file.exists(ITEMTEXT_RDATA)) return(list())
    e <- new.env(); load(ITEMTEXT_RDATA, envir = e)
    L <- e$L
    out <- list(); barred <- character(0)
    for (nm in names(L)) {
        df <- L[[nm]]
        instr <- if ("instrument" %in% names(df)) blank(df$instrument[1]) else NA
        if (item_barred(nm, instr, ex)) { barred <- c(barred, nm); next }
        txt <- blank(df$item_text)
        txt <- txt[!is.na(txt)]
        if (!length(txt)) next
        out[[key(nm)]] <- head(unique(txt), MAX_ITEMS_IN_BUNDLE)
    }
    attr(out, "barred") <- barred
    out
}

##OpenAlex abstracts. Free, no key. Fetched into memory and never written --
##an abstract is publisher text and inherits the same invariants as Context Text.
unpack_abstract <- function(ii) {
    if (is.null(ii) || !length(ii)) return(NA_character_)
    u <- suppressWarnings(unlist(ii))
    if (!length(u) || all(is.na(u))) return(NA_character_)
    n <- max(u, na.rm = TRUE)
    if (!is.finite(n)) return(NA_character_)
    w <- character(n + 1)
    for (k in names(ii)) for (p in ii[[k]]) w[p + 1] <- k
    paste(w, collapse = " ")
}

openalex_get <- function(u) {
    tryCatch({
        r <- GET(u, timeout(25))
        if (status_code(r) != 200) return(NULL)
        fromJSON(rawToChar(r$content), simplifyVector = FALSE)
    }, error = function(e) NULL)
}

##Title out of a reference string "Authors (Year). Title. Journal, ...".
title_of <- function(ref) {
    if (is.na(ref)) return(NA_character_)
    m <- sub("^.*?\\)\\.\\s*", "", ref)
    m <- sub("\\.\\s.*$", "", m)
    m <- gsub("[^A-Za-z0-9 ]", " ", m)
    m <- trimws(gsub("\\s+", " ", m))
    if (nchar(m) < 12) NA_character_ else m
}

fetch_abstract <- function(doi, reference) {
    if (OPT_NOFETCH) return(NA_character_)
    mail <- paste0("mailto=", OPENALEX_MAIL)
    if (!is.na(doi)) {
        j <- openalex_get(paste0(OPENALEX_BASE, "/works/doi:", doi, "?", mail))
        if (!is.null(j) && is.null(j$error)) {
            a <- unpack_abstract(j$abstract_inverted_index)
            if (!is.na(a)) return(a)
        }
    }
    ti <- title_of(reference)
    if (!is.na(ti)) {
        j <- openalex_get(paste0(OPENALEX_BASE, "/works?", mail,
                                 "&per_page=1&search=", URLencode(ti, reserved = TRUE)))
        if (!is.null(j) && length(j$results)) {
            return(unpack_abstract(j$results[[1]]$abstract_inverted_index))
        }
    }
    NA_character_
}

##----------------------------------------------------------------- units ----

##One row per live table, carrying every signal we hold for it, then grouped
##into units. A unit is a construct name where one exists, else a single table.
build_units <- function(sheet, ex) {
    meta <- read_csv_if("metadata.csv")
    if (is.null(meta)) stop("metadata.csv not found -- run stage 01 first.")
    tags <- read_csv_if("tags.csv")
    bib  <- read_csv_if("biblio.csv")
    itm  <- read_csv_if("itemtext_metadata.csv")

    d <- data.frame(table = key(meta$table), stringsAsFactors = FALSE)
    d <- d[!duplicated(d$table), , drop = FALSE]

    ##All joins lowercased: 308 metadata table names are not lowercase and drop
    ##silently from a case-sensitive join.
    pick <- function(df, col, from = "table") {
        if (is.null(df) || !(col %in% names(df))) return(rep(NA_character_, nrow(d)))
        blank(df[[col]][match(d$table, key(df[[from]]))])
    }
    d$construct_name <- pick(tags, "construct.name")
    d$construct_type <- pick(tags, "construct.type")
    d$sample         <- pick(tags, "sample")
    d$tool           <- pick(tags, "measurement.tool")
    d$item_format    <- pick(tags, "item.format")
    d$language       <- pick(tags, "primary.language.s.")
    d$age_range      <- pick(tags, "age.range")
    d$description    <- pick(bib, "Description")
    d$doi            <- pick(bib, "DOI__for_paper_")
    d$reference      <- pick(bib, "Reference_x")
    d$instrument     <- pick(itm, "instrument")

    ##Context Text comes from the sheet, which covers fewer tables than tags.csv.
    m <- match(d$table, sheet$table)
    d$context_text <- sheet$context_text[m]
    ##Sheet values win for the structured columns where the sheet has a row:
    ##a human tagger's judgement outranks the auto-tagger's.
    for (f in c("construct_name", "sample", "construct_type", "tool", "item_format")) {
        sv <- sheet[[f]][m]
        d[[f]] <- ifelse(!is.na(sv), sv, d[[f]])
    }

    ##Unit key: normalised construct name, else the table itself.
    cn <- tolower(gsub("[^a-z0-9 ]", "", tolower(blank(d$construct_name))))
    cn <- trimws(gsub("\\s+", " ", cn))
    d$unit_key  <- ifelse(is.na(cn) | cn == "", paste0("table:", d$table), paste0("construct:", cn))
    d$unit_kind <- ifelse(grepl("^construct:", d$unit_key), "construct", "table")
    d
}

##The bundle the model sees, plus the restricted strings the output is checked
##against. Restricted text goes into the prompt but never into the cache.
build_bundle <- function(rows, items) {
    f <- function(v) { v <- unique(v[!is.na(v)]); if (!length(v)) NA else paste(v, collapse = "; ") }
    parts <- character(0); used <- character(0); restricted <- character(0)

    add <- function(label, value, src, is_restricted = FALSE) {
        if (is.na(value) || !nzchar(value)) return(invisible())
        parts <<- c(parts, paste0(label, ": ", value))
        used <<- c(used, src)
        if (is_restricted) restricted <<- c(restricted, value)
    }

    add("Construct name", f(rows$construct_name), "construct_name")
    add("Dataset table name(s)", paste(head(rows$table, 5), collapse = ", "), "table_name")
    add("Instrument", f(rows$instrument), "instrument")
    add("Dataset description", f(rows$description), "dictionary_description")
    add("Construct type", f(rows$construct_type), "tags")
    add("Sample", f(rows$sample), "tags")
    add("Measurement tool", f(rows$tool), "tags")
    add("Item format", f(rows$item_format), "tags")
    add("Language", f(rows$language), "tags")
    add("Excerpt from the source paper", f(rows$context_text), "context_text", TRUE)

    it <- unlist(items[intersect(rows$table, names(items))], use.names = FALSE)
    if (length(it)) {
        it <- head(unique(it), MAX_ITEMS_IN_BUNDLE)
        add("Example items from the instrument", paste(it, collapse = " | "),
            "item_text", TRUE)
    }
    if (!is.na(rows$abstract[1])) {
        add("Abstract of the source paper", rows$abstract[1], "abstract", TRUE)
    }

    list(text = paste(parts, collapse = "\n"),
         used = paste(sort(unique(used)), collapse = "+"),
         restricted = restricted)
}

prompt_describe <- function(bundle) {
    paste0(
"You are describing what a psychometric or educational dataset measures, for a\n",
"research data repository. Below is everything known about one construct.\n\n",
"Write ONE description of 1-2 sentences saying what is measured, and where the\n",
"evidence supports it, who was measured and how. Requirements:\n",
"  - Write in your own words and your own sentence structure.\n",
"  - Do not copy any run of ", N_GRAM, "+ consecutive words from anything below.\n",
"  - Do not quote item wording. Describe what the items ask about instead.\n",
"  - State only what the evidence supports; do not speculate or embellish.\n",
"  - Do not evaluate the instrument's quality.\n",
"  - Output the description only. No preamble, no heading, no commentary.\n",
"  - If the evidence is too thin to say anything specific, write exactly:\n",
"    INSUFFICIENT\n\n",
"EVIDENCE\n--------\n", bundle$text)
}

##----------------------------------------------------------------- cache ----

CACHE_COLS <- c("row_hash", "unit_key", "unit_kind", "construct_description",
                "sources_used", "similarity_flag", "provenance", "reviewed")

read_cache <- function() {
    if (!file.exists(CACHE_FILE)) {
        e <- as.data.frame(matrix(character(0), ncol = length(CACHE_COLS),
                                  dimnames = list(NULL, CACHE_COLS)),
                           stringsAsFactors = FALSE)
        e$similarity_flag <- logical(0); e$reviewed <- logical(0)
        return(e)
    }
    ch <- read.csv(CACHE_FILE, stringsAsFactors = FALSE, colClasses = "character")
    missing <- setdiff(CACHE_COLS, names(ch))
    if (length(missing)) stop("cache is missing column(s): ", paste(missing, collapse = ", "))
    ch$similarity_flag <- toupper(ch$similarity_flag) %in% c("TRUE", "T")
    ch$reviewed        <- toupper(ch$reviewed) %in% c("TRUE", "T")
    ch
}

write_cache <- function(ch) {
    stray <- setdiff(names(ch), CACHE_COLS)
    if (length(stray) > 0) {
        stop("refusing to write cache with unexpected column(s): ",
             paste(stray, collapse = ", "),
             " -- the cache must never carry restricted text.")
    }
    write.csv(ch[, CACHE_COLS], CACHE_FILE, row.names = FALSE, na = "NA")
}

##---------------------------------------------------------------- review ----

review_flagged <- function(units, ch) {
    pending <- ch[ch$provenance == "pending review" & !ch$reviewed, ]
    if (nrow(pending) == 0) { cat("No units pending review.\n"); return(invisible()) }
    cat(nrow(pending), " unit(s) pending review. Threshold: any shared ",
        N_GRAM, "-gram with a restricted input.\n", sep = "")
    for (i in seq_len(nrow(pending))) {
        u <- pending$unit_key[i]
        rows <- units[units$unit_key == u, ]
        if (!nrow(rows)) next
        cat("\n", strrep("=", 78), "\n", u, "  [", pending$row_hash[i], "]\n", sep = "")
        cat("\n-- RESTRICTED INPUTS (live, not stored) --\n")
        if (!all(is.na(rows$context_text))) {
            cat("  Context Text: ", paste(unique(na.omit(rows$context_text)), collapse = " / "), "\n")
        }
        cat("\n-- DESCRIPTION --\n", pending$construct_description[i], "\n", sep = "")
        ##Recomputed live from the sheet rather than stored: the whole point is
        ##that the source text is not on disk. Item wording and abstracts are
        ##not replayed here, so a unit flagged on those shows an empty list --
        ##the sources line says which inputs were in play.
        ov <- overlap(na.omit(rows$context_text), pending$construct_description[i])
        if (length(ov$shared)) {
            cat("\n-- SHARED ", ov$n, "-GRAMS (vs Context Text) --\n", sep = "")
            for (g in ov$shared) cat("  * ", g, "\n", sep = "")
        } else {
            cat("\n-- SHARED N-GRAMS --\n  (not from Context Text; ",
                "flagged on item wording or abstract)\n", sep = "")
        }
        cat("\n-- SOURCES --\n  ", pending$sources_used[i], "\n", sep = "")
    }
    cat("\n", strrep("=", 78), "\nTo clear a unit: set reviewed = TRUE on its ",
        "row_hash in ", CACHE_FILE, "\nand re-run without --review.\n", sep = "")
}

##------------------------------------------------------------------ main ----

if (OPT_LIST) { list_models(); quit(save = "no") }

ex    <- load_exclusions()
items <- load_itemtext(ex)
barred <- attr(items, "barred")
cat("rights gate: ", length(ex$tables), " named exclusions, ",
    length(ex$patterns), " instrument patterns\n", sep = "")
if (length(barred)) {
    cat("  excluded from item-wording bundles: ", paste(barred, collapse = ", "), "\n", sep = "")
}
cat("item wording available for ", length(items), " table(s)\n", sep = "")

sheet <- get_sheet()
units <- build_units(sheet, ex)
units$abstract <- NA_character_
cache <- read_cache()
cat("tables: ", nrow(units), " | units: ", length(unique(units$unit_key)),
    " | cache: ", nrow(cache), "\n", sep = "")

if (OPT_REVIEW) { review_flagged(units, cache); quit(save = "no") }

##Which units to describe.
all_keys <- unique(units$unit_key)
todo_keys <- setdiff(all_keys, cache$unit_key)

if (OPT_SAMPLE) {
    ##A stratified 20, not the first 20: the corpus has very different evidence
    ##profiles and a sample that misses them teaches nothing.
    ntok <- function(x) ifelse(is.na(x), 0L, lengths(strsplit(trimws(x), "\\s+")))
    u1 <- units[!duplicated(units$unit_key), ]
    u1$ctok <- ntok(u1$context_text)
    strata <- list(
        rich_context   = u1$unit_key[u1$ctok >= 30],
        thin_context   = u1$unit_key[u1$ctok > 0 & u1$ctok < 10],
        desc_only      = u1$unit_key[u1$ctok == 0 & is.na(u1$construct_name) & !is.na(u1$description)],
        has_itemtext   = u1$unit_key[u1$table %in% names(items)],
        abstract_only  = u1$unit_key[u1$ctok == 0 & !is.na(u1$doi) & is.na(u1$instrument)],
        shared         = names(which(table(units$unit_key[units$unit_kind == "construct"]) > 5)))
    want <- c(rich_context = 4, thin_context = 4, desc_only = 4,
              has_itemtext = 3, abstract_only = 3, shared = 2)
    set.seed(1406)
    picked <- character(0)
    for (s in names(want)) {
        pool <- setdiff(unique(strata[[s]]), picked)
        if (!length(pool)) next
        picked <- c(picked, sample(pool, min(want[[s]], length(pool))))
    }
    todo_keys <- picked
    cat("--sample: ", length(todo_keys), " stratified units\n", sep = "")
} else if (!is.na(OPT_LIMIT)) {
    todo_keys <- head(todo_keys, OPT_LIMIT)
    cat("--limit=", OPT_LIMIT, ": ", length(todo_keys), " of ",
        length(all_keys), " units\n", sep = "")
}

cat(length(todo_keys), " unit(s) to describe\n", sep = "")

if (length(todo_keys) > 0 && !OPT_STUB && !OPT_STUBCOPY) invisible(gateway_key())

new <- list(); flushed <- 0
##Parallel to `new`, and only read by the --stub-copy verdict: a unit with no
##restricted input has nothing to leak, so it must NOT be counted as a miss.
had_restricted <- logical(0)
for (i in seq_along(todo_keys)) {
    u <- todo_keys[i]
    rows <- units[units$unit_key == u, ]

    ##Abstracts are fetched per unit, held in memory, and never written.
    if (!OPT_NOFETCH && is.na(rows$abstract[1])) {
        rows$abstract[1] <- fetch_abstract(rows$doi[1], rows$reference[1])
    }

    b <- build_bundle(rows, items)
    if (!nzchar(b$text)) {
        new[[length(new) + 1]] <- data.frame(
            row_hash = digest(u), unit_key = u, unit_kind = rows$unit_kind[1],
            construct_description = NA_character_, sources_used = "",
            similarity_flag = FALSE, provenance = "no evidence", reviewed = FALSE,
            stringsAsFactors = FALSE)
        cat("[", i, "/", length(todo_keys), "] ", u, "  no evidence\n", sep = "")
        had_restricted <- c(had_restricted, FALSE)
        next
    }

    txt <- if (OPT_STUBCOPY) {
        ##Adversarial: echo the restricted text back. This MUST trip the flag on
        ##every unit that has any restricted input.
        if (length(b$restricted)) paste(b$restricted, collapse = " ") else "Stub copy, no restricted input."
    } else if (OPT_STUB) {
        "A stub description produced without contacting any model."
    } else {
        describe_chat(prompt_describe(b))
    }

    txt <- clean_reply(txt)
    ov  <- overlap(b$restricted, txt)

    if (is.na(txt) || identical(txt, "INSUFFICIENT") || is_chatter(txt)) {
        prov <- "no description"; flag <- FALSE; txt <- NA_character_
    } else if (ov$flag) {
        prov <- "pending review"; flag <- TRUE
    } else {
        prov <- "described"; flag <- FALSE
    }

    new[[length(new) + 1]] <- data.frame(
        row_hash = digest(paste(u, b$text)), unit_key = u,
        unit_kind = rows$unit_kind[1], construct_description = txt,
        sources_used = b$used, similarity_flag = flag, provenance = prov,
        reviewed = FALSE, stringsAsFactors = FALSE)

    had_restricted <- c(had_restricted, length(b$restricted) > 0)

    cat("[", i, "/", length(todo_keys), "] ", substr(u, 1, 52), "  ", prov,
        if (flag) "  <-- FLAGGED" else "", "\n", sep = "")

    if (!OPT_STUBCOPY && length(new) - flushed >= CACHE_FLUSH_EVERY) {
        write_cache(rbind(cache, do.call(rbind, new)))
        flushed <- length(new)
    }
    if (!OPT_STUB && !OPT_STUBCOPY) Sys.sleep(1)
}

##--stub-copy writes nothing. Its descriptions are the restricted text itself,
##so persisting them would defeat the invariant the test exists to check. It
##reports a verdict and stops.
if (OPT_STUBCOPY) {
    res <- do.call(rbind, new)
    miss <- had_restricted & res$provenance != "pending review"
    cat("\n", strrep("=", 60), "\nADVERSARIAL TEST: ", sum(had_restricted),
        " of ", nrow(res), " unit(s) carried restricted input; ",
        sum(had_restricted) - sum(miss), " flagged.\n",
        nrow(res) - sum(had_restricted),
        " unit(s) had no restricted input and nothing to leak.\n", sep = "")
    if (any(miss)) {
        cat("FAIL -- restricted text was echoed back and NOT caught:\n")
        print(res$unit_key[miss])
        quit(save = "no", status = 1)
    }
    cat("PASS -- every unit carrying restricted input was caught.\n",
        "Nothing written to disk.\n", sep = "")
    quit(save = "no")
}

if (length(new)) cache <- rbind(cache, do.call(rbind, new))
write_cache(cache)

##--------------------------------------------------------------- outputs ----

out <- merge(units[, c("table", "unit_key", "construct_name")],
             cache[, c("unit_key", "construct_description", "sources_used", "provenance", "reviewed")],
             by = "unit_key", all.x = FALSE)

cleared <- out$provenance == "pending review" & out$reviewed
out$provenance[cleared] <- "described"
out$construct_description[out$provenance == "pending review"] <- NA

out <- out[order(out$table),
           c("table", "unit_key", "construct_name", "construct_description",
             "sources_used", "provenance")]
names(out)[names(out) == "unit_key"] <- "construct_key"
write.csv(out, OUTPUT_FILE, row.names = FALSE, na = "NA")
cat("\nwrote ", OUTPUT_FILE, ": ", nrow(out), " rows\n", sep = "")

##The two-column file is what gets circulated for feedback.
share <- out[!is.na(out$construct_description), c("table", "construct_description")]
names(share) <- c("table", "description")
write.csv(share, SHARE_FILE, row.names = FALSE)
cat("wrote ", SHARE_FILE, ": ", nrow(share), " rows\n", sep = "")

print(table(out$provenance))
np <- sum(out$provenance == "pending review")
if (np > 0) cat("\n", np, " row(s) pending review. Run: Rscript 03b_describe.R --review\n", sep = "")
