##Collections: labelled groupings of IRW tables (issue #1633).
##
##Reads a version-controlled registry (../collections/registry.csv), executes
##each row's rule against metadata.csv / tags.csv, unions in any hand-curated
##members, and writes two CSVs for upload to the irw_meta Redivis dataset:
##
##  collections.csv         one row per collection  (the registry, plus derived
##                          coverage / n_tables / basis)
##  collection_members.csv  one row per (table, collection) membership
##
##Adding a collection is a DATA change: one line in registry.csv, optionally one
##file in ../collections/curated/. No code change here, and none in the R or
##Python packages or the site. That is the whole point of the long format --
##do not "improve" this by adding per-collection branches.
##
##NO credentials and NO Redivis access: everything is read off disk. This is the
##only pipeline stage a reviewer can run end to end without a token.
##
##It also never opens the tags Google Sheet. The `cname:` rules read the already
##published tags.csv, whose "construct name" is column 3 of 03_tags.R's
##positional KEEP_COLS. Column 4 ("Context Text", verbatim paper excerpts) is
##structurally unreachable from here. Do not add a sheet read to this script.

suppressPackageStartupMessages(library(readr))

COLL_DIR   <- "../collections"
REGISTRY   <- file.path(COLL_DIR, "registry.csv")
CURATED    <- file.path(COLL_DIR, "curated")
OUT_COLL   <- "collections.csv"
OUT_MEM    <- "collection_members.csv"
OUT_REPORT <- "collections_report.txt"

##Rule prefixes that read metadata.csv, and so see every documented table.
##`cname:` reads tags.csv, which covers only part of the warehouse; `curated`
##is whatever a human put in the file. Coverage is DERIVED from this, never
##authored, so it cannot drift from the rule that produced the membership.
META_RULES <- c("var", "var_any", "var_prefix", "meta")

stop_if <- function(cond, ...) if (isTRUE(cond)) stop(..., call. = FALSE)

##---- inputs -------------------------------------------------------------

read_registry <- function() {
    stop_if(!file.exists(REGISTRY), "Missing ", REGISTRY)
    reg <- read.csv(REGISTRY, stringsAsFactors = FALSE, check.names = FALSE)
    need <- c("collection", "label", "kind", "definition", "rule", "maintainer", "added")
    missing <- setdiff(need, names(reg))
    stop_if(length(missing) > 0, "registry.csv is missing column(s): ",
            paste(missing, collapse = ", "))
    stop_if(anyDuplicated(reg$collection) > 0, "Duplicate collection slug(s): ",
            paste(unique(reg$collection[duplicated(reg$collection)]), collapse = ", "))
    bad <- reg$collection[!grepl("^[a-z][a-z0-9_]*$", reg$collection)]
    stop_if(length(bad) > 0, "Collection slugs must be lower-case snake_case: ",
            paste(bad, collapse = ", "))
    stop_if(!all(reg$kind %in% c("design", "instrument", "construct")),
            "Unknown kind(s): ",
            paste(unique(reg$kind[!reg$kind %in% c("design","instrument","construct")]),
                  collapse = ", "))
    reg
}

read_curated <- function(slug) {
    f <- file.path(CURATED, paste0(slug, ".csv"))
    if (!file.exists(f)) return(NULL)
    cur <- read.csv(f, stringsAsFactors = FALSE, check.names = FALSE)
    stop_if(!"table" %in% names(cur), f, ": needs a `table` column.")
    if (!"basis" %in% names(cur)) cur$basis <- "curated"
    cur$basis[is.na(cur$basis) | !nzchar(cur$basis)] <- "curated"
    ##`note` is for the human reviewer and is deliberately NOT published:
    ##review material stays on disk, only membership goes to Redivis.
    cur[, c("table", "basis"), drop = FALSE]
}

##---- rule evaluation ----------------------------------------------------
##Every evaluator returns table names as spelled in metadata.csv.

split_rule <- function(rule) {
    i <- regexpr(":", rule, fixed = TRUE)
    if (i < 0) return(list(type = rule, arg = ""))
    list(type = substr(rule, 1, i - 1), arg = substr(rule, i + 1, nchar(rule)))
}

eval_rule <- function(rule, meta, tags) {
    p <- split_rule(rule)
    vars <- strsplit(p$arg, "|", fixed = TRUE)[[1]]

    switch(p$type,
        ##presence of every named variable
        "var" = {
            want <- strsplit(p$arg, "+", fixed = TRUE)[[1]]
            meta$table[vapply(meta$var_list, function(v) all(want %in% v), logical(1))]
        },
        ##presence of any named variable
        "var_any" = meta$table[vapply(meta$var_list, function(v) any(vars %in% v), logical(1))],
        ##any variable starting with any named prefix
        "var_prefix" = meta$table[vapply(meta$var_list, function(v)
            any(vapply(vars, function(p_) any(startsWith(v, p_)), logical(1))), logical(1))],
        ##a logical column of metadata.csv, reused rather than recomputed so
        ##irw_filter(longitudinal=TRUE) and collection="longitudinal" agree
        "meta" = {
            stop_if(!p$arg %in% names(meta), "meta: rule names no such metadata column: ", p$arg)
            col <- meta[[p$arg]]
            meta$table[!is.na(col) & (col %in% c(TRUE, "TRUE", "True", "true"))]
        },
        ##regex over the tags sheet's free-text construct name
        "cname" = {
            hit <- grepl(p$arg, tags$construct_name, ignore.case = TRUE, perl = TRUE)
            tags$meta_table[hit & !is.na(tags$meta_table)]
        },
        "curated" = character(0),
        stop("Unknown rule type '", p$type, "' in rule '", rule,
             "'. Known: var, var_any, var_prefix, meta, cname, curated.", call. = FALSE)
    )
}

##---- main ---------------------------------------------------------------

main <- function() {
    stop_if(!file.exists("metadata.csv"), "metadata.csv not found -- run 01_metadata.R first (and run this from metadata/).")
    stop_if(!file.exists("tags.csv"), "tags.csv not found -- run 03_tags.R first.")

    meta <- read.csv("metadata.csv", stringsAsFactors = FALSE, check.names = FALSE)
    tags <- read.csv("tags.csv", stringsAsFactors = FALSE, check.names = FALSE)
    reg  <- read_registry()

    meta$var_list <- strsplit(tolower(meta$variables), "\\|\\s*")
    meta$var_list <- lapply(meta$var_list, trimws)

    ##THE case trap: metadata.csv preserves original table-name case (307 rows
    ##are not lower-case) while 03_tags.R lower-cases every tags row. Joining
    ##these case-sensitively silently loses those 307 tables and understates
    ##tag coverage as 53% instead of 62%. Always map through lower case.
    key <- setNames(meta$table, tolower(meta$table))
    names(tags)[names(tags) == "construct name"] <- "construct_name"
    stop_if(!"construct_name" %in% names(tags), "tags.csv has no `construct name` column.")
    tags$meta_table <- unname(key[tolower(tags$table)])

    dangling <- sum(is.na(tags$meta_table))
    n_tagged <- length(unique(stats::na.omit(tags$meta_table)))

    ##Warn (do not fail) when metadata.csv is missing configured warehouses --
    ##"metadata-complete" is complete over irw_metadata(), not over the live
    ##warehouse, and this is where that gap becomes visible.
    if (file.exists("redivis_config.R")) {
        cfg <- new.env(); sys.source("redivis_config.R", envir = cfg)
        if (!is.null(cfg$IRW_CORE_DATASETS)) {
            absent <- setdiff(cfg$IRW_CORE_DATASETS, unique(meta$dataset))
            if (length(absent) > 0)
                warning("metadata.csv has no rows for configured core dataset(s): ",
                        paste(absent, collapse = ", "),
                        ". 'metadata-complete' coverage excludes them.", call. = FALSE)
        }
    }

    members <- list(); report <- character()
    for (i in seq_len(nrow(reg))) {
        slug <- reg$collection[i]; rule <- reg$rule[i]
        derived <- unique(eval_rule(rule, meta, tags))
        cur <- read_curated(slug)

        rtype <- split_rule(rule)$type
        stop_if(rtype == "curated" && is.null(cur),
                slug, ": rule is `curated` but ", file.path(CURATED, paste0(slug, ".csv")),
                " does not exist. A curated collection with no member file would publish zero rows.")

        cur_tables <- character(0); cur_basis <- character(0)
        if (!is.null(cur)) {
            mapped <- unname(key[tolower(cur$table)])
            unknown <- cur$table[is.na(mapped)]
            stop_if(length(unknown) > 0, slug, ": curated file names table(s) absent from metadata.csv: ",
                    paste(unknown, collapse = ", "))
            keep <- !mapped %in% derived          # rule wins; do not double-count
            cur_tables <- mapped[keep]; cur_basis <- cur$basis[keep]
        }

        tbl <- c(derived, cur_tables)
        bas <- c(rep(paste0("rule:", rule), length(derived)), cur_basis)
        stop_if(length(tbl) == 0, slug, ": produced zero members. Refusing to publish an empty collection.")

        members[[slug]] <- data.frame(table = tbl, collection = slug, basis = bas,
                                      stringsAsFactors = FALSE)

        reg$coverage[i] <- if (rtype %in% META_RULES) "metadata-complete"
                           else if (rtype == "cname") "tagged-subset-only"
                           else "curated-only"
        reg$n_tables[i] <- length(tbl)
        reg$basis[i]    <- if (length(derived) && length(cur_tables)) "rule+curated"
                           else if (length(cur_tables)) "curated" else "rule"

        ##How many tags rows this rule matched but could not publish, because
        ##the table they name is not in metadata.csv. Reported, not hidden.
        if (rtype == "cname") {
            lost <- sum(grepl(split_rule(rule)$arg, tags$construct_name,
                              ignore.case = TRUE, perl = TRUE) & is.na(tags$meta_table))
            if (lost > 0)
                report <- c(report, sprintf("  %-24s %4d matching tags row(s) dropped: no such table in metadata.csv",
                                            slug, lost))
        }
    }

    mem <- do.call(rbind, members)
    mem <- mem[order(mem$collection, mem$table), ]        # deterministic: re-runs must diff empty
    rownames(mem) <- NULL

    ##(table, collection) is the identity of a membership row and must be unique.
    ##A curated file listing the same table twice is the way this happens. The
    ##differ keys on this pair, so a duplicate here would be silently dropped
    ##from every future diff rather than reported.
    dup <- duplicated(mem[, c("table", "collection")])
    stop_if(any(dup), "Duplicate (table, collection) row(s): ",
            paste(sprintf("%s/%s", mem$table[dup], mem$collection[dup]), collapse = ", "),
            ". Check the curated file for repeats.")

    ##Denominator belongs in the definition -- `coverage` alone is an opaque
    ##token, and "63 tables" means nothing without "of the 2,251 tagged".
    tagged_note <- sprintf(" (searched the %s tagged tables of %s; coverage incomplete)",
                           format(n_tagged, big.mark = ","), format(nrow(meta), big.mark = ","))
    reg$definition <- ifelse(reg$coverage == "tagged-subset-only",
                             paste0(reg$definition, tagged_note), reg$definition)

    reg <- reg[, c("collection", "label", "kind", "definition", "rule",
                   "coverage", "basis", "n_tables", "maintainer", "added")]

    readr::write_csv(reg, OUT_COLL)
    readr::write_csv(mem, OUT_MEM)

    per_table <- table(table(mem$table))
    lines <- c(
        sprintf("collections            : %d", nrow(reg)),
        sprintf("membership rows        : %d", nrow(mem)),
        sprintf("tables reached         : %d of %d", length(unique(mem$table)), nrow(meta)),
        sprintf("in >1 collection       : %d", sum(per_table[as.integer(names(per_table)) > 1])),
        sprintf("tags rows w/o a table  : %d", dangling),
        "", "by coverage:",
        paste0("  ", names(table(reg$coverage)), ": ", as.integer(table(reg$coverage))),
        "", "counts by collection:",
        sprintf("  %-24s %-20s %5d", reg$collection, reg$coverage, reg$n_tables)
    )
    if (length(report)) lines <- c(lines, "", "dropped (tags row names no table in metadata.csv):", report)
    writeLines(lines, OUT_REPORT)
    cat(paste(lines, collapse = "\n"), "\n")
    cat("\nwrote", OUT_COLL, "and", OUT_MEM, "and", OUT_REPORT, "\n")
}

main()
