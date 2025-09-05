-- Database: news_tracker

-- DROP DATABASE IF EXISTS news_tracker;

CREATE DATABASE news_tracker
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    LOCALE_PROVIDER = 'libc'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;


-- SCHEMA: news_schema

-- DROP SCHEMA IF EXISTS news_schema ;

CREATE SCHEMA IF NOT EXISTS news_schema
    AUTHORIZATION postgres;



-- Table: news_schema.adminconfig

-- DROP TABLE IF EXISTS news_schema.adminconfig;

CREATE TABLE IF NOT EXISTS news_schema.adminconfig
(
    id integer NOT NULL DEFAULT nextval('news_schema.adminconfig_id_seq'::regclass),
    target_email text COLLATE pg_catalog."default" NOT NULL,
    summary_send_time time without time zone,
    last_updated timestamp without time zone,
    CONSTRAINT adminconfig_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS news_schema.adminconfig
    OWNER to postgres;
-- Index: idx_last_updated

-- DROP INDEX IF EXISTS news_schema.idx_last_updated;

CREATE INDEX IF NOT EXISTS idx_last_updated
    ON news_schema.adminconfig USING btree
    (last_updated ASC NULLS LAST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default;
-- Index: idx_target_email

-- DROP INDEX IF EXISTS news_schema.idx_target_email;

CREATE INDEX IF NOT EXISTS idx_target_email
    ON news_schema.adminconfig USING btree
    (target_email COLLATE pg_catalog."default" ASC NULLS LAST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default;

-- SEQUENCE: news_schema.adminconfig_id_seq

-- DROP SEQUENCE IF EXISTS news_schema.adminconfig_id_seq;

CREATE SEQUENCE IF NOT EXISTS news_schema.adminconfig_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

ALTER SEQUENCE news_schema.adminconfig_id_seq
    OWNED BY news_schema.adminconfig.id;

ALTER SEQUENCE news_schema.adminconfig_id_seq
    OWNER TO postgres;


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

-- SEQUENCE: news_schema.articlekeywords_id_seq

-- DROP SEQUENCE IF EXISTS news_schema.articlekeywords_id_seq;

CREATE SEQUENCE IF NOT EXISTS news_schema.articlekeywords_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

ALTER SEQUENCE news_schema.articlekeywords_id_seq
    OWNED BY news_schema.articlekeywords.id;

ALTER SEQUENCE news_schema.articlekeywords_id_seq
    OWNER TO postgres;


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
    increase_percentage integer NOT NULL,
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


-- SEQUENCE: news_schema.dailytrends_id_seq

-- DROP SEQUENCE IF EXISTS news_schema.dailytrends_id_seq;

CREATE SEQUENCE IF NOT EXISTS news_schema.dailytrends_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

ALTER SEQUENCE news_schema.dailytrends_id_seq
    OWNED BY news_schema.dailytrends.id;

ALTER SEQUENCE news_schema.dailytrends_id_seq
    OWNER TO postgres;


-- Table: news_schema.keywords

-- DROP TABLE IF EXISTS news_schema.keywords;

CREATE TABLE IF NOT EXISTS news_schema.keywords
(
    id integer NOT NULL DEFAULT nextval('news_schema.keywords_id_seq'::regclass),
    keyword text COLLATE pg_catalog."default" NOT NULL,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT keywords_pkey PRIMARY KEY (id),
    CONSTRAINT keywords_keyword_key UNIQUE (keyword)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS news_schema.keywords
    OWNER to postgres;
-- Index: idx_keywords_keyword

-- DROP INDEX IF EXISTS news_schema.idx_keywords_keyword;

CREATE INDEX IF NOT EXISTS idx_keywords_keyword
    ON news_schema.keywords USING btree
    (keyword COLLATE pg_catalog."default" ASC NULLS LAST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default;


-- SEQUENCE: news_schema.keywords_id_seq

-- DROP SEQUENCE IF EXISTS news_schema.keywords_id_seq;

CREATE SEQUENCE IF NOT EXISTS news_schema.keywords_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

ALTER SEQUENCE news_schema.keywords_id_seq
    OWNED BY news_schema.keywords.id;

ALTER SEQUENCE news_schema.keywords_id_seq
    OWNER TO postgres;



-- Table: news_schema.news

-- DROP TABLE IF EXISTS news_schema.news;

CREATE TABLE IF NOT EXISTS news_schema.news
(
    id integer NOT NULL DEFAULT nextval('news_schema.news_id_seq'::regclass),
    headline text COLLATE pg_catalog."default" NOT NULL,
    url text COLLATE pg_catalog."default" NOT NULL,
    news_section text COLLATE pg_catalog."default" NOT NULL,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    summary text COLLATE pg_catalog."default",
    published_at timestamp without time zone,
    CONSTRAINT news_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS news_schema.news
    OWNER to postgres;
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


-- SEQUENCE: news_schema.news_id_seq

-- DROP SEQUENCE IF EXISTS news_schema.news_id_seq;

CREATE SEQUENCE IF NOT EXISTS news_schema.news_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

ALTER SEQUENCE news_schema.news_id_seq
    OWNED BY news_schema.news.id;

ALTER SEQUENCE news_schema.news_id_seq
    OWNER TO postgres;


-- Table: news_schema.news_keywords

-- DROP TABLE IF EXISTS news_schema.news_keywords;

CREATE TABLE IF NOT EXISTS news_schema.news_keywords
(
    id integer NOT NULL DEFAULT nextval('news_schema.news_keywords_id_seq'::regclass),
    keyword_id integer,
    news_id integer,
    CONSTRAINT news_keywords_pkey PRIMARY KEY (id),
    CONSTRAINT news_keywords_keyword_id_news_id_key UNIQUE (keyword_id, news_id),
    CONSTRAINT news_keywords_keyword_id_fkey FOREIGN KEY (keyword_id)
        REFERENCES news_schema.keywords (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT news_keywords_news_id_fkey FOREIGN KEY (news_id)
        REFERENCES news_schema.news (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS news_schema.news_keywords
    OWNER to postgres;
-- Index: idx_news_keywords_keyword_news

-- DROP INDEX IF EXISTS news_schema.idx_news_keywords_keyword_news;

CREATE INDEX IF NOT EXISTS idx_news_keywords_keyword_news
    ON news_schema.news_keywords USING btree
    (keyword_id ASC NULLS LAST, news_id ASC NULLS LAST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default;

-- SEQUENCE: news_schema.news_keywords_id_seq

-- DROP SEQUENCE IF EXISTS news_schema.news_keywords_id_seq;

CREATE SEQUENCE IF NOT EXISTS news_schema.news_keywords_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

ALTER SEQUENCE news_schema.news_keywords_id_seq
    OWNED BY news_schema.news_keywords.id;

ALTER SEQUENCE news_schema.news_keywords_id_seq
    OWNER TO postgres;




-- Table: news_schema.trendsresults

-- DROP TABLE IF EXISTS news_schema.trendsresults;

CREATE TABLE IF NOT EXISTS news_schema.trendsresults
(
    id integer NOT NULL DEFAULT nextval('news_schema.trendsresults_id_seq'::regclass),
    has_data boolean NOT NULL,
    peak_interest integer,
    avg_interest numeric(5,2),
    current_interest integer NOT NULL,
    data_collected_at timestamp without time zone NOT NULL,
    data_period_start date,
    data_period_end date,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    geo text COLLATE pg_catalog."default" NOT NULL,
    keyword_id integer NOT NULL,
    CONSTRAINT trendsresults_pkey PRIMARY KEY (id),
    CONSTRAINT trendsresults_keyword_id_fkey FOREIGN KEY (keyword_id)
        REFERENCES news_schema.keywords (id) MATCH SIMPLE
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


-- SEQUENCE: news_schema.trendsresults_id_seq

-- DROP SEQUENCE IF EXISTS news_schema.trendsresults_id_seq;

CREATE SEQUENCE IF NOT EXISTS news_schema.trendsresults_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

ALTER SEQUENCE news_schema.trendsresults_id_seq
    OWNED BY news_schema.trendsresults.id;

ALTER SEQUENCE news_schema.trendsresults_id_seq
    OWNER TO postgres;