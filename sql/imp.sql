--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: member; Type: TABLE; Schema: public; Owner: imp; Tablespace: 
--

CREATE TABLE member (
    member_id integer NOT NULL,
    username text NOT NULL,
    password text NOT NULL
);


ALTER TABLE public.member OWNER TO imp;

--
-- Name: member_member_id_seq; Type: SEQUENCE; Schema: public; Owner: imp
--

CREATE SEQUENCE member_member_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.member_member_id_seq OWNER TO imp;

--
-- Name: member_member_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: imp
--

ALTER SEQUENCE member_member_id_seq OWNED BY member.member_id;


--
-- Name: metadata; Type: TABLE; Schema: public; Owner: imp; Tablespace: 
--

CREATE TABLE metadata (
    track_id integer NOT NULL,
    field text NOT NULL,
    "values" text[] NOT NULL
);


ALTER TABLE public.metadata OWNER TO imp;

--
-- Name: track; Type: TABLE; Schema: public; Owner: imp; Tablespace: 
--

CREATE TABLE track (
    track_id integer NOT NULL,
    member_id integer NOT NULL,
    original_format text NOT NULL,
    duration integer NOT NULL,
    fingerprint text NOT NULL
);


ALTER TABLE public.track OWNER TO imp;

--
-- Name: track_track_id_seq; Type: SEQUENCE; Schema: public; Owner: imp
--

CREATE SEQUENCE track_track_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.track_track_id_seq OWNER TO imp;

--
-- Name: track_track_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: imp
--

ALTER SEQUENCE track_track_id_seq OWNED BY track.track_id;


--
-- Name: member_id; Type: DEFAULT; Schema: public; Owner: imp
--

ALTER TABLE ONLY member ALTER COLUMN member_id SET DEFAULT nextval('member_member_id_seq'::regclass);


--
-- Name: track_id; Type: DEFAULT; Schema: public; Owner: imp
--

ALTER TABLE ONLY track ALTER COLUMN track_id SET DEFAULT nextval('track_track_id_seq'::regclass);


--
-- Data for Name: member; Type: TABLE DATA; Schema: public; Owner: imp
--

COPY member (member_id, username, password) FROM stdin;
\.


--
-- Name: member_member_id_seq; Type: SEQUENCE SET; Schema: public; Owner: imp
--

SELECT pg_catalog.setval('member_member_id_seq', 1, false);


--
-- Data for Name: metadata; Type: TABLE DATA; Schema: public; Owner: imp
--

COPY metadata (track_id, field, "values") FROM stdin;
\.


--
-- Data for Name: track; Type: TABLE DATA; Schema: public; Owner: imp
--

COPY track (track_id, member_id, original_format, duration, fingerprint) FROM stdin;
\.


--
-- Name: track_track_id_seq; Type: SEQUENCE SET; Schema: public; Owner: imp
--

SELECT pg_catalog.setval('track_track_id_seq', 1, false);


--
-- Name: member_pkey; Type: CONSTRAINT; Schema: public; Owner: imp; Tablespace: 
--

ALTER TABLE ONLY member
    ADD CONSTRAINT member_pkey PRIMARY KEY (member_id);


--
-- Name: metadata_pkey; Type: CONSTRAINT; Schema: public; Owner: imp; Tablespace: 
--

ALTER TABLE ONLY metadata
    ADD CONSTRAINT metadata_pkey PRIMARY KEY (track_id, field);


--
-- Name: track_pkey; Type: CONSTRAINT; Schema: public; Owner: imp; Tablespace: 
--

ALTER TABLE ONLY track
    ADD CONSTRAINT track_pkey PRIMARY KEY (track_id);


--
-- Name: metadata_track_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: imp
--

ALTER TABLE ONLY metadata
    ADD CONSTRAINT metadata_track_id_fkey FOREIGN KEY (track_id) REFERENCES track(track_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: track_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: imp
--

ALTER TABLE ONLY track
    ADD CONSTRAINT track_member_id_fkey FOREIGN KEY (member_id) REFERENCES member(member_id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

