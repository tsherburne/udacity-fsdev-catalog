--
-- PostgreSQL database setup
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;


SET search_path = public, pg_catalog;
SET default_tablespace = '';
SET default_with_oids = false;

--
-- Name: articles; Type: TABLE; Schema: public; Owner: vagrant; Tablespace: 
--
--
-- Name: articles; Type: TABLE; Schema: public; Owner: vagrant; Tablespace: 
--

CREATE TABLE articles (
    author integer NOT NULL,
    title text NOT NULL,
    slug text NOT NULL,
    lead text,
    body text,
    "time" timestamp with time zone DEFAULT now(),
    id integer NOT NULL
);


ALTER TABLE articles OWNER TO postgres;

--
-- Name: articles_id_seq; Type: SEQUENCE; Schema: public; Owner: vagrant
--

CREATE SEQUENCE authors_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE authors_id_seq OWNER TO postgres;
--
-- Name: authors_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vagrant
--

ALTER SEQUENCE authors_id_seq OWNED BY authors.id;
