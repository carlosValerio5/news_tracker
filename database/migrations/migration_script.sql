--- Database: news_tracker

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


-- SEQUENCE: news_schema.adminconfig_id_seq

-- DROP SEQUENCE IF EXISTS news_schema.adminconfig_id_seq;

CREATE SEQUENCE IF NOT EXISTS news_schema.adminconfig_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;


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

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_last_updated
    ON news_schema.adminconfig USING btree
    (last_updated ASC NULLS LAST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default;

-- Index: uq_adminconfig_target_email

-- DROP INDEX IF EXISTS news_schema.uq_adminconfig_target_email;

CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS uq_adminconfig_target_email
    ON news_schema.adminconfig USING btree
    (target_email COLLATE pg_catalog."default" ASC NULLS LAST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default;

ALTER SEQUENCE news_schema.adminconfig_id_seq
    OWNED BY news_schema.adminconfig.id;

ALTER SEQUENCE news_schema.adminconfig_id_seq
    OWNER TO postgres;



-- SEQUENCE: news_schema.articlekeywords_id_seq

-- DROP SEQUENCE IF EXISTS news_schema.articlekeywords_id_seq;

CREATE SEQUENCE IF NOT EXISTS news_schema.articlekeywords_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;


-- Table: news_schema.articlekeywords

-- DROP TABLE IF EXISTS news_schema.articlekeywords;

CREATE TABLE IF NOT EXISTS news_schema.articlekeywords
(
    id integer NOT NULL DEFAULT nextval('news_schema.articlekeywords_id_seq'::regclass),
    keyword_1 text COLLATE pg_catalog."default" NOT NULL,
    keyword_2 text COLLATE pg_catalog."default",
    keyword_3 text COLLATE pg_catalog."default",
    extraction_confidence numeric(3,2),
    extracted_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    composed_query text COLLATE pg_catalog."default" GENERATED ALWAYS AS (((((lower(COALESCE(keyword_1, ''::text)) || '|'::text) || lower(COALESCE(keyword_2, ''::text))) || '|'::text) || lower(COALESCE(keyword_3, ''::text)))) STORED,
    CONSTRAINT articlekeywords_pkey PRIMARY KEY (id),
    CONSTRAINT keywords_not_empty CHECK (keyword_1 IS NOT NULL AND TRIM(BOTH FROM keyword_1) <> ''::text)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS news_schema.articlekeywords
    OWNER to postgres;
-- Index: idx_composed_query

-- DROP INDEX IF EXISTS news_schema.idx_composed_query;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_composed_query
    ON news_schema.articlekeywords USING btree
    (composed_query COLLATE pg_catalog."default" ASC NULLS LAST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default;
-- Index: idx_keyword_1

-- DROP INDEX IF EXISTS news_schema.idx_keyword_1;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_keyword_1
    ON news_schema.articlekeywords USING btree
    (keyword_1 COLLATE pg_catalog."default" ASC NULLS LAST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default;

-- DROP INDEX IF EXISTS news_schema.uq_composed_query;

CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS uq_composed_query
    ON news_schema.articlekeywords USING btree
    (composed_query COLLATE pg_catalog."default" ASC NULLS LAST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default;

ALTER SEQUENCE news_schema.articlekeywords_id_seq
    OWNED BY news_schema.articlekeywords.id;

ALTER SEQUENCE news_schema.articlekeywords_id_seq
    OWNER TO postgres;





-- SEQUENCE: news_schema.dailytrends_id_seq

-- DROP SEQUENCE IF EXISTS news_schema.dailytrends_id_seq;

CREATE SEQUENCE IF NOT EXISTS news_schema.dailytrends_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

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

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scraped_at
    ON news_schema.dailytrends USING btree
    (scraped_at ASC NULLS LAST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default;



ALTER SEQUENCE news_schema.dailytrends_id_seq
    OWNED BY news_schema.dailytrends.id;

ALTER SEQUENCE news_schema.dailytrends_id_seq
    OWNER TO postgres;



-- SEQUENCE: news_schema.news_id_seq

-- DROP SEQUENCE IF EXISTS news_schema.news_id_seq;

CREATE SEQUENCE IF NOT EXISTS news_schema.news_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

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
    keywords_id integer,
    CONSTRAINT news_pkey PRIMARY KEY (id),
    CONSTRAINT news_keywords_id_fkey FOREIGN KEY (keywords_id)
        REFERENCES news_schema.articlekeywords (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS news_schema.news
    OWNER to postgres;
-- Index: idx_news_section

-- DROP INDEX IF EXISTS news_schema.idx_news_section;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_news_section
    ON news_schema.news USING btree
    (news_section COLLATE pg_catalog."default" ASC NULLS LAST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default;
-- Index: idx_published_at

-- DROP INDEX IF EXISTS news_schema.idx_published_at;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_published_at
    ON news_schema.news USING btree
    (published_at ASC NULLS LAST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default;

-- DROP INDEX IF EXISTS news_schema.uq_news_url_headline;

CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS uq_news_url_headline
    ON news_schema.news USING btree
    (url COLLATE pg_catalog."default" ASC NULLS LAST, headline COLLATE pg_catalog."default" ASC NULLS LAST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default;

ALTER SEQUENCE news_schema.news_id_seq
    OWNED BY news_schema.news.id;

ALTER SEQUENCE news_schema.news_id_seq
    OWNER TO postgres;



-- SEQUENCE: news_schema.trendsresults_id_seq

-- DROP SEQUENCE IF EXISTS news_schema.trendsresults_id_seq;

CREATE SEQUENCE IF NOT EXISTS news_schema.trendsresults_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

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
    article_keywords_id integer NOT NULL,
    CONSTRAINT trendsresults_pkey PRIMARY KEY (id),
    CONSTRAINT trends_results_article_keywords_id_fkey FOREIGN KEY (article_keywords_id)
        REFERENCES news_schema.articlekeywords (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS news_schema.trendsresults
    OWNER to postgres;
-- Index: idx_has_data

-- DROP INDEX IF EXISTS news_schema.idx_has_data;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_has_data
    ON news_schema.trendsresults USING btree
    (has_data ASC NULLS LAST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default;
-- Index: idx_trends_results_article_keywords_id

-- DROP INDEX IF EXISTS news_schema.idx_trends_results_article_keywords_id;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_trends_results_article_keywords_id
    ON news_schema.trendsresults USING btree
    (article_keywords_id ASC NULLS LAST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default;



ALTER SEQUENCE news_schema.trendsresults_id_seq
    OWNED BY news_schema.trendsresults.id;

ALTER SEQUENCE news_schema.trendsresults_id_seq
    OWNER TO postgres;


-- View: news_schema.recent_activity

-- DROP VIEW news_schema.recent_activity;

CREATE OR REPLACE VIEW news_schema.recent_activity
 AS
 SELECT row_number() OVER (ORDER BY activity_type, occurred_at) AS id,
    activity_type,
    description,
    occurred_at,
    entity_id,
    entity_type
   FROM ( SELECT row_number() OVER (ORDER BY users.created_at DESC) AS row_number,
            'user-registered'::text AS activity_type,
            concat('User ', users.email, ' registered') AS description,
            users.created_at AS occurred_at,
            users.id AS entity_id,
            'users'::text AS entity_type
           FROM news_schema.users
        UNION ALL
         SELECT row_number() OVER (ORDER BY (count(*))) AS row_number,
            'article_published'::text AS activity_type,
            concat(count(*), ' articles were created.') AS description,
            CURRENT_DATE AS occurred_at,
            NULL::integer AS entity_id,
            'news'::text AS entity_type
           FROM news_schema.news
          WHERE news.created_at >= CURRENT_DATE
         HAVING count(*) > 0
        UNION ALL
         SELECT row_number() OVER (ORDER BY (count(*))) AS row_number,
            'keywords_extracted'::text AS activity_type,
            concat(count(*), ' sets of keywords were extracted') AS concat,
            CURRENT_DATE AS occurred_at,
            NULL::integer AS entity_id,
            'articlekeywords'::text AS entity_type
           FROM news_schema.articlekeywords
          WHERE articlekeywords.extracted_at >= CURRENT_DATE
         HAVING count(*) > 0) activities
  ORDER BY occurred_at DESC
 LIMIT 100;

ALTER TABLE news_schema.recent_activity
    OWNER TO postgres;

-- SEQUENCE: news_schema.users_id_seq

-- DROP SEQUENCE IF EXISTS news_schema.users_id_seq;

CREATE SEQUENCE IF NOT EXISTS news_schema.users_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

-- Table: news_schema.users

-- DROP TABLE IF EXISTS news_schema.users;

CREATE TABLE IF NOT EXISTS news_schema.users
(
    id integer NOT NULL DEFAULT nextval('news_schema.users_id_seq'::regclass),
    email text COLLATE pg_catalog."default" NOT NULL,
    name text COLLATE pg_catalog."default",
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    last_login timestamp without time zone,
    role character(1) COLLATE pg_catalog."default",
    google_id text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT users_pkey PRIMARY KEY (id),
    CONSTRAINT users_email_key UNIQUE (email)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS news_schema.users
    OWNER to postgres;

ALTER SEQUENCE news_schema.users_id_seq
    OWNED BY news_schema.users.id;

ALTER SEQUENCE news_schema.users_id_seq
    OWNER TO postgres;
-- Index: idx_users_email

-- DROP INDEX IF EXISTS news_schema.idx_users_email;

CREATE INDEX IF NOT EXISTS idx_users_email
    ON news_schema.users USING btree
    (email COLLATE pg_catalog."default" ASC NULLS LAST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default;
-- Index: uq_users_google_id

-- DROP INDEX IF EXISTS news_schema.uq_users_google_id;

CREATE UNIQUE INDEX IF NOT EXISTS uq_users_google_id
    ON news_schema.users USING btree
    (google_id COLLATE pg_catalog."default" ASC NULLS LAST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default;
