local specification = {
    --
    -- metadata
    --
    name      = "sbl",
    version   = "1.00",
    comment   = "Society of Biblical Literature Handbook of Style, 2nd edition, specification",
    author    = "Joey McCollum",
    copyright = "ConTeXt development team",
    --
    -- derived (combinations of) fields (all share the same default set)
    --
    virtual = {
        "authoryear",
        "authoryears",
        "authornum",
        "num",
        "suffix",
    },
    --
    -- special datatypes
    --
    types = {
        --
        -- list of fields that are interpreted as names: "NAME [and NAME]" where
        -- NAME is one of the following:
        --
        -- First vons Last
        -- vons Last, First
        -- vons Last, Jrs, First
        -- Vons, Last, Jrs, First
        --
        author      = "author", -- interpreted as name(s)
        withauthor  = "author",
        editor      = "author",
        witheditor  = "author",
        translator  = "author",
        doi         = "url",        -- an external link
        url         = "url",
        page        = "pagenumber", -- number or range: f--t
        pages       = "pagenumber",
        volume      = "range",
        number      = "range",
        keywords    = "keyword",    -- comma|-|separated list
        year        = "number",
    },
    --
    -- categories with their specific fields
    --
    categories = {
        --
        -- categories are added below
        --
    },
}

local generic = {
    --
    -- A set returns the first field (in order of position below) that is found
    -- present in an entry. A set having the same name as a field conditionally
    -- allows the substitution of an alternate field.
    --
    -- note that anything can get assigned a doi or be available online. 
    series = { "shortseries", "series" }, -- prefer shorthand to long form
    journal = { "shortjournal", "journal" }, -- prefer shorthand to long form
    location = { "location", "address" }, -- interchangeable
    institution = { "institution", "school" }, -- interchangeable
    origpublisher = { "origpublisher", "origlocation", "origdate" }, -- the presence of any of these fields indicates that the entry is a reprint
    date = { "date", "year", "pubstate" }, -- prefer the more specific field, and prefer any date to publication state (e.g., "forthcoming")
    doi = { "doi", "url" },
}

-- Definition of recognized categories and the fields that they contain.
-- Required fields should be present; optional fields may also be rendered;
-- all other fields will be ignored.

-- Sets contain either/or in order of precedence.
--
-- For a category *not* defined here yet present in the dataset, *all* fields
-- are taken as optional. This allows for flexibility in the addition of new
-- categories.

local categories = specification.categories

-- an article from a journal

categories.article = {
    sets = {
        author = { "author", "organization"},
        journal = generic.journal,
        date = generic.date,
        doi = generic.doi,
    },
    required = {
        "author", -- a set
        "title",
        "journal", -- a set
    },
    optional = {
        "withauthor", "withauthortype", 
        "translator", "origlanguage",
        "date",
        "type", "file",
        "volume", "number", "pages",
        "doi", "note",
    },
}

-- an article from a magazine (treated the same in SBL; see §6.3.9)
categories.magazine = categories.article

-- an article in a newspaper (not covered by SBL)
categories.newspaper = categories.magazine

-- (from jabref) to be identified and setup ...

categories.periodical = {
    sets = {
        author = { "editor", "publisher", "organization", },
        series = generic.series,
        date = generic.date,
        doi = generic.doi,
    },
    required = {
        "title",
        "date", -- a set
    },
    optional = {
        "author",
        "witheditor", "witheditortype",
        "translator", "origlanguage",
        "series", "volume", "number",
        "month",
        "organization",
        "doi", "note",
        "file",
    },
}

-- (from jabref) to be identified and setup ...

categories.standard = {
    sets = {
        author = { "author", "institution", "organization" },
        date = generic.date,
        doi = generic.doi,
    },
    required = {
        "author",
        "title",
        "date", -- a set
        "doi", "note",
    },
    optional = {
        "withauthor", "withauthortype", 
        "translator",
    },
}

-- a book with an explicit publisher.

categories.book = {
    sets = {
        author = { "author", "editor" },
        series = generic.series,
        origpublisher = generic.origpublisher,
        location = generic.location,
        date = generic.date,
        doi = generic.doi,
    },
    required = { 
        "author", -- a set
        "title",
        "publisher",
    },
    optional = {
        "withauthor", "withauthortype",
        "editor",
        "witheditor", "witheditortype",
        "translator", "origlanguage",
        "volumes",
        "series", "seriesseries", "number",
        "origpublisher",
        "location",
        "date",
        "doi", "note",
        "abstract",
    },
}

categories.mvbook = categories.book

-- a part of a book, which may be a chapter (or section or whatever) and/or a range of pages.
-- note that biblatex-sbl uses @incollection to refer to this entry type, 
-- not to the the next entry type!

categories.inbook = {
    sets = {
        author  = { "author", "organization" },
        editor = { "editor", "bookeditor" }, -- interchangeable
        witheditor = { "witheditor", "withbookeditor" }, -- interchangeable
        witheditortype = { "witheditortype", "withbookeditortype" }, -- interchangeable
        series = generic.series,
        origpublisher = generic.origpublisher,
        location = generic.location,
        date = generic.date,
        doi = generic.doi,
    },
    required = {
        "author", -- author of the article (or book, if the author also wrote the book)
        "title", -- title of the article
        "booktitle", -- title of the book
        "publisher",
    },
    optional = {
        "withauthor", "withauthortype",
        "editor",
        "witheditor", "witheditortype",
        "translator", "origlanguage",
        "volume",
        "maintitle",
        "maineditor",
        "withmaineditor", "withmaineditortype",
        "series", "seriesseries", "number",
        "origpublisher",
        "location",
        "date",
        "pages",
        "doi", "note",
    },
}

-- a book that is itself part of a titled collection.
-- (like inbook, but the entry in question is one or more volumes of a multi-volume work )
-- note that biblatex-sbl uses @collection to refer to this entry type.

categories.incollection = {
    sets = {
        author = { "author", "editor" },
        title = { "title", "booktitle" },
        editor = { "editor", "bookeditor" }, -- interchangeable
        witheditor = { "witheditor", "withbookeditor" }, -- interchangeable
        witheditortype = { "witheditortype", "withbookeditortype" }, -- interchangeable
        series = generic.series,
        origpublisher = generic.origpublisher,
        location = generic.location,
        date = generic.date,
        doi = generic.doi,
    },
    required = {
        "author", -- a set
        "title", -- title of this book
        "maintitle", -- title of the collection
        "publisher",
    },
    optional = {
        "withauthor", "withauthortype", 
        "editor", 
        "witheditor", "witheditortype",
        "translator", "origlanguage",
        "volume",
        "maineditor",
        "withmaineditor", "withmaineditortype",
        "series", "seriesseries", "number",
        "location",
        "date",
        "origpublisher",
        "doi", "note",
    },
}

-- the proceedings of a conference.

categories.proceedings = {
    sets = {
        author = { "editor", "organization" }, -- no "author"!
        series = generic.series,
        origpublisher = generic.origpublisher,
        publisher = { "publisher", "organization" },
        location = generic.location,
        date = generic.date,
        doi = generic.doi,
    },
    required = {
        "author", -- referring to the set above
        "title",
        "publisher",
    },
    optional = {
        "witheditor", "witheditortype",
        "translator", "origlanguage",
        "series", "seriesseries", "number",
        "location",
        "date",
        "origpublisher",
        "doi", "note",
    },
}

-- an article in a conference proceedings.

categories.inproceedings = {
    sets     = categories.incollection.sets,
    required = categories.incollection.required,
    optional = {
        "withauthor", "withauthortype",
        "witheditor", "witheditortype",
        "translator", "origlanguage",
        "year", "date", "origdate",
        "edition", 
        "series", "seriesseries", "number",
        "location",
        "date",
        "origpublisher",
        "organization",
        "doi", "note",
    },
}

categories.conference = categories.inproceedings

-- a thesis (type can be specified as a field).

categories.thesis = {
    sets = {
        institution = generic.institution,
        location = generic.location,
        date = generic.date,
        doi = generic.doi,
    },
    required = {
        "author",
        "title",
        "institution", -- a set
        "date", -- a set
        "type", -- typically "Masters" or "PhD"
    },
    optional = {
        "withauthor", "withauthortype",
        "translator", "origlanguage",
        "location",
        "doi", "note",
    },
}

-- a Master's thesis.

categories.mastersthesis = {
    sets     = categories.thesis.sets,
    required = {
        "author",
        "title",
        "institution", -- a set
        "date", -- a set
    },
    optional = {
        "withauthor", "withauthortype",
        "translator", "origlanguage",
        "location",
        "doi", "note",
    },
}

-- a PhD. thesis.

categories.phdthesis = categories.mastersthesis

-- a document having an author and title, but not formally published.

categories.unpublished = {
    sets = {
        doi = generic.doi,
    },
    required = {
        "author",
        "title",
        "note",
    },
    optional = {
        "withauthor", "translator",
        "file",
        "year", "date",
        "doi",
    },
}

-- a document published online with no print counterpart (§6.4.13)
-- an online database (§6.4.14)
-- a website or blog (§6.4.15)

categories.online = {
    sets = {
        author = { "author", "organization", "editor", },
        location = generic.location,
        date = generic.date,
        doi = generic.doi
    },
    required = {
        "title",
    },
    optional = {
        "author", 
        "withauthor", "withauthortype",
        "translator", "origlanguage",
        "journaltitle",
        "date",
        "eprint", "eprintdate", "eprintclass", "eprinttype",
        "location",
        "howpublished",
        "doi", "note",
    },
}

-- electronic sources are not addressed by SBL, so their category will be treated as an alias of @online

categories.electronic = categories.online

-- use this type when nothing else fits.

categories.misc = {
    sets = {
        author = { "author", "organization", "editor" },
        location = generic.location,
        date = generic.date,
        doi  = generic.doi,
    },
    required = {
        -- nothing is really important here
    },
    optional = {
        "author", 
        "withauthor", "withauthortype",
        "title",
        "witheditor", "witheditortype",
        "translator", "origlanguage",
        "edition", 
        "volumes",
        "volume",
        "maintitle",
        "maineditor",
        "withmaineditor", "withmaineditortype",
        "series", "seriesseries", "number",
        "howpublished",
        "location",
        "publisher",
        "date",
        "doi", "note",
    },
}

-- other (whatever jabref does not know!)

categories.other = {
    sets = {
        location = generic.location,
        date = generic.date,
        doi  = generic.doi,
    },
    required = {
        "author",
        "title",
        "date"
    },
    optional = {
        "withauthor", "withauthortype",
        "witheditor", "witheditortype",
        "translator", "origlanguage",
        "edition", 
        "volumes",
        "volume",
        "maintitle",
        "maineditor",
        "withmaineditor", "withmaineditortype",
        "series", "seriesseries", "number",
        "howpublished",
        "location",
        "publisher",
        "doi", "note",
    },
}

-- if all else fails to match:

categories.literal = {
    sets = {
        author = { "key" },
        doi    = generic.doi,
    },
    required = {
        "author",
        "text"
    },
    optional = {
        "withauthor", "withauthortype",
        "witheditor", "witheditortype",
        "translator", "origlanguage",
        "edition", 
        "volumes",
        "volume",
        "maintitle",
        "maineditor",
        "withmaineditor", "withmaineditortype",
        "series", "seriesseries", "number",
        "howpublished",
        "location",
        "publisher",
        "date",
        "doi", "note",
    },
    virtual = false,
}

-- done

return specification
