-- SCHEMA: news_schema

-- DROP SCHEMA IF EXISTS news_schema ;

CREATE SCHEMA IF NOT EXISTS news_schema
    AUTHORIZATION postgres;




-- Table: news_schema.news

-- DROP TABLE IF EXISTS news_schema.news;

CREATE TABLE IF NOT EXISTS news_schema.news
(
    id integer NOT NULL DEFAULT nextval('news_schema.news_id_seq'::regclass),
    keywords_id integer,
    headline text COLLATE pg_catalog."default" NOT NULL,
    url text COLLATE pg_catalog."default" NOT NULL,
    news_section text COLLATE pg_catalog."default" NOT NULL,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    summary text COLLATE pg_catalog."default",
    published_at timestamp without time zone,
    CONSTRAINT news_pkey PRIMARY KEY (id),
    CONSTRAINT news_keywords_id_fkey FOREIGN KEY (keywords_id)
        REFERENCES news_schema.articlekeywords (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS news_schema.news
    OWNER to postgres;
-- Index: idx_keywords_id

-- DROP INDEX IF EXISTS news_schema.idx_keywords_id;

CREATE INDEX IF NOT EXISTS idx_keywords_id
    ON news_schema.news USING btree
    (keywords_id ASC NULLS LAST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default;
-- Index: idx_news_section

-- DROP INDEX IF EXISTS news_schema.idx_news_section;

CREATE INDEX IF NOT EXISTS idx_news_section
    ON news_schema.news USING btree
    (news_section COLLATE pg_catalog."default" ASC NULLS LAST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default;
-- Index: idx_published_at

-- DROP INDEX IF EXISTS news_schema.idx_published_at;

CREATE INDEX IF NOT EXISTS idx_published_at
    ON news_schema.news USING btree
    (published_at ASC NULLS LAST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default;




-- Table: news_schema.articlekeywords

-- DROP TABLE IF EXISTS news_schema.articlekeywords;

CREATE TABLE IF NOT EXISTS news_schema.articlekeywords
(
    id integer NOT NULL DEFAULT nextval('news_schema.articlekeywords_id_seq'::regclass),
    keyword_1 text COLLATE pg_catalog."default" NOT NULL,
    keyword_2 text COLLATE pg_catalog."default",
    keyword_3 text COLLATE pg_catalog."default",
    composed_query text COLLATE pg_catalog."default" NOT NULL,
    extraction_confidence numeric(3,2),
    extracted_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT articlekeywords_pkey PRIMARY KEY (id),
    CONSTRAINT keywords_not_empty CHECK (keyword_1 IS NOT NULL AND TRIM(BOTH FROM keyword_1) <> ''::text)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS news_schema.articlekeywords
    OWNER to postgres;
-- Index: idx_composed_query

-- DROP INDEX IF EXISTS news_schema.idx_composed_query;

CREATE INDEX IF NOT EXISTS idx_composed_query
    ON news_schema.articlekeywords USING btree
    (composed_query COLLATE pg_catalog."default" ASC NULLS LAST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default;
-- Index: idx_keyword_1

-- DROP INDEX IF EXISTS news_schema.idx_keyword_1;

CREATE INDEX IF NOT EXISTS idx_keyword_1
    ON news_schema.articlekeywords USING btree
    (keyword_1 COLLATE pg_catalog."default" ASC NULLS LAST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default;



-- Table: news_schema.dailytrends

-- DROP TABLE IF EXISTS news_schema.dailytrends;

CREATE TABLE IF NOT EXISTS news_schema.dailytrends
(
    id integer NOT NULL DEFAULT nextval('news_schema.dailytrends_id_seq'::regclass),
    title text COLLATE pg_catalog."default" NOT NULL,
    ranking integer,
    geo text COLLATE pg_catalog."default" NOT NULL,
    start_timestamp timestamp without time zone NOT NULL,
    search_volume integer NOT NULL,
    increase_porcentage integer NOT NULL,
    category text COLLATE pg_catalog."default",
    scraped_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT dailytrends_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS news_schema.dailytrends
    OWNER to postgres;
-- Index: idx_scraped_at

-- DROP INDEX IF EXISTS news_schema.idx_scraped_at;

CREATE INDEX IF NOT EXISTS idx_scraped_at
    ON news_schema.dailytrends USING btree
    (scraped_at ASC NULLS LAST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default;



-- Table: news_schema.news

-- DROP TABLE IF EXISTS news_schema.news;

CREATE TABLE IF NOT EXISTS news_schema.news
(
    id integer NOT NULL DEFAULT nextval('news_schema.news_id_seq'::regclass),
    keywords_id integer,
    headline text COLLATE pg_catalog."default" NOT NULL,
    url text COLLATE pg_catalog."default" NOT NULL,
    news_section text COLLATE pg_catalog."default" NOT NULL,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    summary text COLLATE pg_catalog."default",
    published_at timestamp without time zone,
    CONSTRAINT news_pkey PRIMARY KEY (id),
    CONSTRAINT news_keywords_id_fkey FOREIGN KEY (keywords_id)
        REFERENCES news_schema.articlekeywords (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS news_schema.news
    OWNER to postgres;
-- Index: idx_keywords_id

-- DROP INDEX IF EXISTS news_schema.idx_keywords_id;

CREATE INDEX IF NOT EXISTS idx_keywords_id
    ON news_schema.news USING btree
    (keywords_id ASC NULLS LAST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default;
-- Index: idx_news_section

-- DROP INDEX IF EXISTS news_schema.idx_news_section;

CREATE INDEX IF NOT EXISTS idx_news_section
    ON news_schema.news USING btree
    (news_section COLLATE pg_catalog."default" ASC NULLS LAST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default;
-- Index: idx_published_at

-- DROP INDEX IF EXISTS news_schema.idx_published_at;

CREATE INDEX IF NOT EXISTS idx_published_at
    ON news_schema.news USING btree
    (published_at ASC NULLS LAST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default;





-- Table: news_schema.trendsresults

-- DROP TABLE IF EXISTS news_schema.trendsresults;

CREATE TABLE IF NOT EXISTS news_schema.trendsresults
(
    id integer NOT NULL DEFAULT nextval('news_schema.trendsresults_id_seq'::regclass),
    article_keywords_id integer NOT NULL,
    has_data boolean NOT NULL,
    peak_interest integer,
    avg_interest numeric(5,2),
    current_interest integer NOT NULL,
    data_collected_at timestamp without time zone NOT NULL,
    data_period_start date,
    data_period_end date,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    geo text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT trendsresults_pkey PRIMARY KEY (id),
    CONSTRAINT trendsresults_article_keywords_id_key UNIQUE (article_keywords_id),
    CONSTRAINT trendsresults_article_keywords_id_fkey FOREIGN KEY (article_keywords_id)
        REFERENCES news_schema.articlekeywords (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS news_schema.trendsresults
    OWNER to postgres;
-- Index: idx_has_data

-- DROP INDEX IF EXISTS news_schema.idx_has_data;

CREATE INDEX IF NOT EXISTS idx_has_data
    ON news_schema.trendsresults USING btree
    (has_data ASC NULLS LAST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default;