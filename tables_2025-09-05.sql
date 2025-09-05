--
-- PostgreSQL database dump
--

-- Dumped from database version 16.9 (Ubuntu 16.9-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.9 (Ubuntu 16.9-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: cardates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cardates (
    id integer NOT NULL,
    carid character varying(5),
    legid integer,
    remcap integer,
    accomtype character varying(1),
    CONSTRAINT remcap_nonnegative CHECK ((remcap >= 0))
);


ALTER TABLE public.cardates OWNER TO postgres;

--
-- Name: cardatesfancy; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cardatesfancy (
    carid character varying(5) NOT NULL,
    capacity integer,
    legid integer,
    id integer NOT NULL,
    accomtype character varying(1)
);


ALTER TABLE public.cardatesfancy OWNER TO postgres;

--
-- Name: cardates_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cardates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cardates_id_seq OWNER TO postgres;

--
-- Name: cardates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cardates_id_seq OWNED BY public.cardatesfancy.id;


--
-- Name: cardates_id_seq1; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cardates_id_seq1
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cardates_id_seq1 OWNER TO postgres;

--
-- Name: cardates_id_seq1; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cardates_id_seq1 OWNED BY public.cardates.id;


--
-- Name: legs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.legs (
    trainid character varying(3),
    dayoftrain integer,
    id integer NOT NULL,
    edgeid integer,
    date integer
);


ALTER TABLE public.legs OWNER TO postgres;

--
-- Name: cardatetrain; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.cardatetrain AS
 SELECT c.id,
    c.carid,
    c.remcap,
    c.legid,
    c.accomtype,
    l.trainid
   FROM (public.cardates c
     JOIN public.legs l ON ((c.legid = l.id)));


ALTER VIEW public.cardatetrain OWNER TO postgres;

--
-- Name: cardatetrainfancy; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.cardatetrainfancy AS
 SELECT c.id,
    c.carid,
    c.capacity,
    c.legid,
    c.accomtype,
    l.trainid
   FROM (public.cardatesfancy c
     JOIN public.legs l ON ((c.legid = l.id)));


ALTER VIEW public.cardatetrainfancy OWNER TO postgres;

--
-- Name: legreservations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.legreservations (
    id integer NOT NULL,
    reservationid integer,
    cardateid integer
);


ALTER TABLE public.legreservations OWNER TO postgres;

--
-- Name: reservations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reservations (
    id integer NOT NULL,
    car character varying(5),
    seats integer,
    startcity character varying(3),
    endcity character varying(3),
    date integer
);


ALTER TABLE public.reservations OWNER TO postgres;

--
-- Name: cardateusage; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.cardateusage AS
 SELECT l.cardateid,
    sum(r.seats) AS reservedseats
   FROM (public.legreservations l
     LEFT JOIN public.reservations r ON ((l.reservationid = r.id)))
  GROUP BY l.cardateid;


ALTER VIEW public.cardateusage OWNER TO postgres;

--
-- Name: citiesmain; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.citiesmain (
    index integer,
    mnemonic character varying(3) NOT NULL,
    commonname character varying(255)
);


ALTER TABLE public.citiesmain OWNER TO postgres;

--
-- Name: edges; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.edges (
    id integer NOT NULL,
    startcity character varying(3),
    endcity character varying(3)
);


ALTER TABLE public.edges OWNER TO postgres;

--
-- Name: edgeindex; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.edgeindex AS
 SELECT e.id AS edgeid,
    e.startcity,
    e.endcity,
    cs.index AS startindex,
    ce.index AS endindex
   FROM ((public.edges e
     JOIN public.citiesmain cs ON (((e.startcity)::text = (cs.mnemonic)::text)))
     JOIN public.citiesmain ce ON (((e.endcity)::text = (ce.mnemonic)::text)));


ALTER VIEW public.edgeindex OWNER TO postgres;

--
-- Name: edges_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.edges_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.edges_id_seq OWNER TO postgres;

--
-- Name: edges_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.edges_id_seq OWNED BY public.edges.id;


--
-- Name: legcars; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.legcars AS
 SELECT l.id AS legid,
    l.trainid,
    e.startcity,
    e.endcity,
    l.date,
    l.dayoftrain
   FROM (public.legs l
     LEFT JOIN public.edges e ON ((l.edgeid = e.id)));


ALTER VIEW public.legcars OWNER TO postgres;

--
-- Name: legedgeindex; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.legedgeindex AS
 SELECT l.trainid,
    l.dayoftrain,
    l.id AS legid,
    l.edgeid,
    l.date,
    e.startcity,
    e.endcity,
    e.startindex,
    e.endindex
   FROM (public.legs l
     JOIN ( SELECT e_1.id AS edgeid,
            e_1.startcity,
            e_1.endcity,
            cs.index AS startindex,
            ce.index AS endindex
           FROM ((public.edges e_1
             JOIN public.citiesmain cs ON (((e_1.startcity)::text = (cs.mnemonic)::text)))
             JOIN public.citiesmain ce ON (((e_1.endcity)::text = (ce.mnemonic)::text)))) e ON ((l.edgeid = e.edgeid)));


ALTER VIEW public.legedgeindex OWNER TO postgres;

--
-- Name: legreservations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.legreservations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.legreservations_id_seq OWNER TO postgres;

--
-- Name: legreservations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.legreservations_id_seq OWNED BY public.legreservations.id;


--
-- Name: legs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.legs ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.legs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: linktrains; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.linktrains (
    mainid character varying(3),
    secondid character varying(3),
    date integer
);


ALTER TABLE public.linktrains OWNER TO postgres;

--
-- Name: reservations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reservations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.reservations_id_seq OWNER TO postgres;

--
-- Name: reservations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reservations_id_seq OWNED BY public.reservations.id;


--
-- Name: trains; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.trains (
    id character varying(3) NOT NULL,
    name character varying(255),
    westbound boolean
);


ALTER TABLE public.trains OWNER TO postgres;

--
-- Name: cardates id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cardates ALTER COLUMN id SET DEFAULT nextval('public.cardates_id_seq1'::regclass);


--
-- Name: cardatesfancy id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cardatesfancy ALTER COLUMN id SET DEFAULT nextval('public.cardates_id_seq'::regclass);


--
-- Name: edges id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.edges ALTER COLUMN id SET DEFAULT nextval('public.edges_id_seq'::regclass);


--
-- Name: legreservations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.legreservations ALTER COLUMN id SET DEFAULT nextval('public.legreservations_id_seq'::regclass);


--
-- Name: reservations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservations ALTER COLUMN id SET DEFAULT nextval('public.reservations_id_seq'::regclass);


--
-- Name: cardatesfancy cardates_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cardatesfancy
    ADD CONSTRAINT cardates_pkey PRIMARY KEY (id);


--
-- Name: cardates cardates_pkey1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cardates
    ADD CONSTRAINT cardates_pkey1 PRIMARY KEY (id);


--
-- Name: citiesmain citiesmain_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.citiesmain
    ADD CONSTRAINT citiesmain_pkey PRIMARY KEY (mnemonic);


--
-- Name: edges edges_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.edges
    ADD CONSTRAINT edges_pkey PRIMARY KEY (id);


--
-- Name: legreservations legreservations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.legreservations
    ADD CONSTRAINT legreservations_pkey PRIMARY KEY (id);


--
-- Name: cardates nodupe_cardates; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cardates
    ADD CONSTRAINT nodupe_cardates UNIQUE (legid, carid);


--
-- Name: legs pk_id; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.legs
    ADD CONSTRAINT pk_id PRIMARY KEY (id);


--
-- Name: reservations reservations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservations
    ADD CONSTRAINT reservations_pkey PRIMARY KEY (id);


--
-- Name: trains trains_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trains
    ADD CONSTRAINT trains_pkey PRIMARY KEY (id);


--
-- Name: cardatesfancy cardates_legid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cardatesfancy
    ADD CONSTRAINT cardates_legid_fkey FOREIGN KEY (legid) REFERENCES public.legs(id);


--
-- Name: cardates cardates_legid_fkey1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cardates
    ADD CONSTRAINT cardates_legid_fkey1 FOREIGN KEY (legid) REFERENCES public.legs(id);


--
-- Name: edges edges_endcity_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.edges
    ADD CONSTRAINT edges_endcity_fkey FOREIGN KEY (endcity) REFERENCES public.citiesmain(mnemonic);


--
-- Name: edges edges_start_city_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.edges
    ADD CONSTRAINT edges_start_city_fkey FOREIGN KEY (startcity) REFERENCES public.citiesmain(mnemonic);


--
-- Name: legreservations legreservations_cardateid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.legreservations
    ADD CONSTRAINT legreservations_cardateid_fkey FOREIGN KEY (cardateid) REFERENCES public.cardatesfancy(id);


--
-- Name: legreservations legreservations_reservationid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.legreservations
    ADD CONSTRAINT legreservations_reservationid_fkey FOREIGN KEY (reservationid) REFERENCES public.reservations(id);


--
-- Name: legs legs_edgeid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.legs
    ADD CONSTRAINT legs_edgeid_fkey FOREIGN KEY (edgeid) REFERENCES public.edges(id);


--
-- Name: legs legs_trainid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.legs
    ADD CONSTRAINT legs_trainid_fkey FOREIGN KEY (trainid) REFERENCES public.trains(id);


--
-- Name: linktrains linktrains_mainid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.linktrains
    ADD CONSTRAINT linktrains_mainid_fkey FOREIGN KEY (mainid) REFERENCES public.trains(id);


--
-- Name: linktrains linktrains_secondid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.linktrains
    ADD CONSTRAINT linktrains_secondid_fkey FOREIGN KEY (secondid) REFERENCES public.trains(id);


--
-- Name: reservations reservations_endcity_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservations
    ADD CONSTRAINT reservations_endcity_fkey FOREIGN KEY (endcity) REFERENCES public.citiesmain(mnemonic);


--
-- Name: reservations reservations_startcity_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservations
    ADD CONSTRAINT reservations_startcity_fkey FOREIGN KEY (startcity) REFERENCES public.citiesmain(mnemonic);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT ALL ON SCHEMA public TO <YOURUSERHERE>;


--
-- Name: TABLE cardates; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.cardates TO <YOURUSERHERE>;


--
-- Name: TABLE cardatesfancy; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.cardatesfancy TO <YOURUSERHERE>;


--
-- Name: SEQUENCE cardates_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.cardates_id_seq TO <YOURUSERHERE>;


--
-- Name: SEQUENCE cardates_id_seq1; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.cardates_id_seq1 TO <YOURUSERHERE>;


--
-- Name: TABLE legs; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.legs TO <YOURUSERHERE>;


--
-- Name: TABLE cardatetrain; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.cardatetrain TO <YOURUSERHERE>;


--
-- Name: TABLE cardatetrainfancy; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.cardatetrainfancy TO <YOURUSERHERE>;


--
-- Name: TABLE legreservations; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.legreservations TO <YOURUSERHERE>;


--
-- Name: TABLE reservations; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.reservations TO <YOURUSERHERE>;


--
-- Name: TABLE cardateusage; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.cardateusage TO <YOURUSERHERE>;


--
-- Name: TABLE citiesmain; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.citiesmain TO <YOURUSERHERE>;


--
-- Name: TABLE edges; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.edges TO <YOURUSERHERE>;


--
-- Name: TABLE edgeindex; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.edgeindex TO <YOURUSERHERE>;


--
-- Name: SEQUENCE edges_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.edges_id_seq TO <YOURUSERHERE>;


--
-- Name: TABLE legcars; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.legcars TO <YOURUSERHERE>;


--
-- Name: TABLE legedgeindex; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.legedgeindex TO <YOURUSERHERE>;


--
-- Name: SEQUENCE legreservations_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.legreservations_id_seq TO <YOURUSERHERE>;


--
-- Name: SEQUENCE legs_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.legs_id_seq TO <YOURUSERHERE>;


--
-- Name: TABLE linktrains; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.linktrains TO <YOURUSERHERE>;


--
-- Name: SEQUENCE reservations_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.reservations_id_seq TO <YOURUSERHERE>;


--
-- Name: TABLE trains; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.trains TO <YOURUSERHERE>;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON TABLES TO <YOURUSERHERE>;


--
-- PostgreSQL database dump complete
--

