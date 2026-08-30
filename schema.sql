--
-- PostgreSQL database dump
--

\restrict yVUxjDNTUtDbQzo6ZnOK62jV8tw8TvOeg9u5mzWteP6e1egRvmdzGhVLliXlaD8

-- Dumped from database version 16.15
-- Dumped by pg_dump version 16.15

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

--
-- Name: evidencetype; Type: TYPE; Schema: public; Owner: jobflow
--

CREATE TYPE public.evidencetype AS ENUM (
    'PROJECT',
    'EXPERIENCE'
);


ALTER TYPE public.evidencetype OWNER TO jobflow;

--
-- Name: profilestatus; Type: TYPE; Schema: public; Owner: jobflow
--

CREATE TYPE public.profilestatus AS ENUM (
    'DRAFT',
    'VERIFIED'
);


ALTER TYPE public.profilestatus OWNER TO jobflow;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: jobflow
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO jobflow;

--
-- Name: applications; Type: TABLE; Schema: public; Owner: jobflow
--

CREATE TABLE public.applications (
    id integer NOT NULL,
    user_id integer NOT NULL,
    job_id integer NOT NULL,
    status character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.applications OWNER TO jobflow;

--
-- Name: applications_id_seq; Type: SEQUENCE; Schema: public; Owner: jobflow
--

CREATE SEQUENCE public.applications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.applications_id_seq OWNER TO jobflow;

--
-- Name: applications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jobflow
--

ALTER SEQUENCE public.applications_id_seq OWNED BY public.applications.id;


--
-- Name: jobs; Type: TABLE; Schema: public; Owner: jobflow
--

CREATE TABLE public.jobs (
    id integer NOT NULL,
    external_job_id character varying,
    source character varying NOT NULL,
    source_url character varying NOT NULL,
    title character varying NOT NULL,
    company character varying NOT NULL,
    location character varying,
    description text,
    date_posted timestamp with time zone,
    employment_type character varying,
    salary_display character varying,
    workplace_type character varying,
    experience_level character varying,
    created_at timestamp with time zone DEFAULT now(),
    scraped_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.jobs OWNER TO jobflow;

--
-- Name: jobs_id_seq; Type: SEQUENCE; Schema: public; Owner: jobflow
--

CREATE SEQUENCE public.jobs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.jobs_id_seq OWNER TO jobflow;

--
-- Name: jobs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jobflow
--

ALTER SEQUENCE public.jobs_id_seq OWNED BY public.jobs.id;


--
-- Name: master_resumes; Type: TABLE; Schema: public; Owner: jobflow
--

CREATE TABLE public.master_resumes (
    id integer NOT NULL,
    user_id integer NOT NULL,
    content text NOT NULL,
    format character varying,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.master_resumes OWNER TO jobflow;

--
-- Name: master_resumes_id_seq; Type: SEQUENCE; Schema: public; Owner: jobflow
--

CREATE SEQUENCE public.master_resumes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.master_resumes_id_seq OWNER TO jobflow;

--
-- Name: master_resumes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jobflow
--

ALTER SEQUENCE public.master_resumes_id_seq OWNED BY public.master_resumes.id;


--
-- Name: profile_achievements; Type: TABLE; Schema: public; Owner: jobflow
--

CREATE TABLE public.profile_achievements (
    id integer NOT NULL,
    profile_id integer NOT NULL,
    title character varying NOT NULL,
    description text
);


ALTER TABLE public.profile_achievements OWNER TO jobflow;

--
-- Name: profile_achievements_id_seq; Type: SEQUENCE; Schema: public; Owner: jobflow
--

CREATE SEQUENCE public.profile_achievements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.profile_achievements_id_seq OWNER TO jobflow;

--
-- Name: profile_achievements_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jobflow
--

ALTER SEQUENCE public.profile_achievements_id_seq OWNED BY public.profile_achievements.id;


--
-- Name: profile_education; Type: TABLE; Schema: public; Owner: jobflow
--

CREATE TABLE public.profile_education (
    id integer NOT NULL,
    profile_id integer NOT NULL,
    institution character varying NOT NULL,
    degree character varying NOT NULL,
    date_str character varying
);


ALTER TABLE public.profile_education OWNER TO jobflow;

--
-- Name: profile_education_id_seq; Type: SEQUENCE; Schema: public; Owner: jobflow
--

CREATE SEQUENCE public.profile_education_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.profile_education_id_seq OWNER TO jobflow;

--
-- Name: profile_education_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jobflow
--

ALTER SEQUENCE public.profile_education_id_seq OWNED BY public.profile_education.id;


--
-- Name: profile_experience; Type: TABLE; Schema: public; Owner: jobflow
--

CREATE TABLE public.profile_experience (
    id integer NOT NULL,
    profile_id integer NOT NULL,
    company character varying NOT NULL,
    title character varying NOT NULL,
    description text,
    achievements text
);


ALTER TABLE public.profile_experience OWNER TO jobflow;

--
-- Name: profile_experience_id_seq; Type: SEQUENCE; Schema: public; Owner: jobflow
--

CREATE SEQUENCE public.profile_experience_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.profile_experience_id_seq OWNER TO jobflow;

--
-- Name: profile_experience_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jobflow
--

ALTER SEQUENCE public.profile_experience_id_seq OWNED BY public.profile_experience.id;


--
-- Name: profile_projects; Type: TABLE; Schema: public; Owner: jobflow
--

CREATE TABLE public.profile_projects (
    id integer NOT NULL,
    profile_id integer NOT NULL,
    name character varying NOT NULL,
    description text,
    role character varying,
    url character varying
);


ALTER TABLE public.profile_projects OWNER TO jobflow;

--
-- Name: profile_projects_id_seq; Type: SEQUENCE; Schema: public; Owner: jobflow
--

CREATE SEQUENCE public.profile_projects_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.profile_projects_id_seq OWNER TO jobflow;

--
-- Name: profile_projects_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jobflow
--

ALTER SEQUENCE public.profile_projects_id_seq OWNED BY public.profile_projects.id;


--
-- Name: profile_skills; Type: TABLE; Schema: public; Owner: jobflow
--

CREATE TABLE public.profile_skills (
    id integer NOT NULL,
    profile_id integer NOT NULL,
    name character varying NOT NULL,
    proficiency character varying
);


ALTER TABLE public.profile_skills OWNER TO jobflow;

--
-- Name: profile_skills_id_seq; Type: SEQUENCE; Schema: public; Owner: jobflow
--

CREATE SEQUENCE public.profile_skills_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.profile_skills_id_seq OWNER TO jobflow;

--
-- Name: profile_skills_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jobflow
--

ALTER SEQUENCE public.profile_skills_id_seq OWNED BY public.profile_skills.id;


--
-- Name: resume_versions; Type: TABLE; Schema: public; Owner: jobflow
--

CREATE TABLE public.resume_versions (
    id integer NOT NULL,
    application_id integer NOT NULL,
    master_resume_id integer,
    adjusted_content text NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.resume_versions OWNER TO jobflow;

--
-- Name: resume_versions_id_seq; Type: SEQUENCE; Schema: public; Owner: jobflow
--

CREATE SEQUENCE public.resume_versions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.resume_versions_id_seq OWNER TO jobflow;

--
-- Name: resume_versions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jobflow
--

ALTER SEQUENCE public.resume_versions_id_seq OWNED BY public.resume_versions.id;


--
-- Name: skill_evidence; Type: TABLE; Schema: public; Owner: jobflow
--

CREATE TABLE public.skill_evidence (
    id integer NOT NULL,
    skill_id integer,
    evidence_type public.evidencetype NOT NULL,
    evidence_id integer NOT NULL
);


ALTER TABLE public.skill_evidence OWNER TO jobflow;

--
-- Name: skill_evidence_id_seq; Type: SEQUENCE; Schema: public; Owner: jobflow
--

CREATE SEQUENCE public.skill_evidence_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.skill_evidence_id_seq OWNER TO jobflow;

--
-- Name: skill_evidence_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jobflow
--

ALTER SEQUENCE public.skill_evidence_id_seq OWNED BY public.skill_evidence.id;


--
-- Name: user_profiles; Type: TABLE; Schema: public; Owner: jobflow
--

CREATE TABLE public.user_profiles (
    id integer NOT NULL,
    user_id integer NOT NULL,
    status public.profilestatus NOT NULL,
    career_goals text,
    target_roles text,
    target_industries text,
    location_prefs text,
    personalization_prefs text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    name character varying,
    title character varying
);


ALTER TABLE public.user_profiles OWNER TO jobflow;

--
-- Name: user_profiles_id_seq; Type: SEQUENCE; Schema: public; Owner: jobflow
--

CREATE SEQUENCE public.user_profiles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_profiles_id_seq OWNER TO jobflow;

--
-- Name: user_profiles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jobflow
--

ALTER SEQUENCE public.user_profiles_id_seq OWNED BY public.user_profiles.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: jobflow
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.users OWNER TO jobflow;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: jobflow
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO jobflow;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jobflow
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: applications id; Type: DEFAULT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.applications ALTER COLUMN id SET DEFAULT nextval('public.applications_id_seq'::regclass);


--
-- Name: jobs id; Type: DEFAULT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.jobs ALTER COLUMN id SET DEFAULT nextval('public.jobs_id_seq'::regclass);


--
-- Name: master_resumes id; Type: DEFAULT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.master_resumes ALTER COLUMN id SET DEFAULT nextval('public.master_resumes_id_seq'::regclass);


--
-- Name: profile_achievements id; Type: DEFAULT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.profile_achievements ALTER COLUMN id SET DEFAULT nextval('public.profile_achievements_id_seq'::regclass);


--
-- Name: profile_education id; Type: DEFAULT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.profile_education ALTER COLUMN id SET DEFAULT nextval('public.profile_education_id_seq'::regclass);


--
-- Name: profile_experience id; Type: DEFAULT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.profile_experience ALTER COLUMN id SET DEFAULT nextval('public.profile_experience_id_seq'::regclass);


--
-- Name: profile_projects id; Type: DEFAULT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.profile_projects ALTER COLUMN id SET DEFAULT nextval('public.profile_projects_id_seq'::regclass);


--
-- Name: profile_skills id; Type: DEFAULT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.profile_skills ALTER COLUMN id SET DEFAULT nextval('public.profile_skills_id_seq'::regclass);


--
-- Name: resume_versions id; Type: DEFAULT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.resume_versions ALTER COLUMN id SET DEFAULT nextval('public.resume_versions_id_seq'::regclass);


--
-- Name: skill_evidence id; Type: DEFAULT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.skill_evidence ALTER COLUMN id SET DEFAULT nextval('public.skill_evidence_id_seq'::regclass);


--
-- Name: user_profiles id; Type: DEFAULT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.user_profiles ALTER COLUMN id SET DEFAULT nextval('public.user_profiles_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: applications applications_pkey; Type: CONSTRAINT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.applications
    ADD CONSTRAINT applications_pkey PRIMARY KEY (id);


--
-- Name: jobs jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_pkey PRIMARY KEY (id);


--
-- Name: jobs jobs_source_url_key; Type: CONSTRAINT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_source_url_key UNIQUE (source_url);


--
-- Name: master_resumes master_resumes_pkey; Type: CONSTRAINT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.master_resumes
    ADD CONSTRAINT master_resumes_pkey PRIMARY KEY (id);


--
-- Name: profile_achievements profile_achievements_pkey; Type: CONSTRAINT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.profile_achievements
    ADD CONSTRAINT profile_achievements_pkey PRIMARY KEY (id);


--
-- Name: profile_education profile_education_pkey; Type: CONSTRAINT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.profile_education
    ADD CONSTRAINT profile_education_pkey PRIMARY KEY (id);


--
-- Name: profile_experience profile_experience_pkey; Type: CONSTRAINT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.profile_experience
    ADD CONSTRAINT profile_experience_pkey PRIMARY KEY (id);


--
-- Name: profile_projects profile_projects_pkey; Type: CONSTRAINT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.profile_projects
    ADD CONSTRAINT profile_projects_pkey PRIMARY KEY (id);


--
-- Name: profile_skills profile_skills_pkey; Type: CONSTRAINT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.profile_skills
    ADD CONSTRAINT profile_skills_pkey PRIMARY KEY (id);


--
-- Name: resume_versions resume_versions_pkey; Type: CONSTRAINT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.resume_versions
    ADD CONSTRAINT resume_versions_pkey PRIMARY KEY (id);


--
-- Name: skill_evidence skill_evidence_pkey; Type: CONSTRAINT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.skill_evidence
    ADD CONSTRAINT skill_evidence_pkey PRIMARY KEY (id);


--
-- Name: user_profiles user_profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.user_profiles
    ADD CONSTRAINT user_profiles_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_applications_id; Type: INDEX; Schema: public; Owner: jobflow
--

CREATE INDEX ix_applications_id ON public.applications USING btree (id);


--
-- Name: ix_jobs_external_job_id; Type: INDEX; Schema: public; Owner: jobflow
--

CREATE INDEX ix_jobs_external_job_id ON public.jobs USING btree (external_job_id);


--
-- Name: ix_jobs_id; Type: INDEX; Schema: public; Owner: jobflow
--

CREATE INDEX ix_jobs_id ON public.jobs USING btree (id);


--
-- Name: ix_jobs_source; Type: INDEX; Schema: public; Owner: jobflow
--

CREATE INDEX ix_jobs_source ON public.jobs USING btree (source);


--
-- Name: ix_master_resumes_id; Type: INDEX; Schema: public; Owner: jobflow
--

CREATE INDEX ix_master_resumes_id ON public.master_resumes USING btree (id);


--
-- Name: ix_profile_achievements_id; Type: INDEX; Schema: public; Owner: jobflow
--

CREATE INDEX ix_profile_achievements_id ON public.profile_achievements USING btree (id);


--
-- Name: ix_profile_education_id; Type: INDEX; Schema: public; Owner: jobflow
--

CREATE INDEX ix_profile_education_id ON public.profile_education USING btree (id);


--
-- Name: ix_profile_experience_id; Type: INDEX; Schema: public; Owner: jobflow
--

CREATE INDEX ix_profile_experience_id ON public.profile_experience USING btree (id);


--
-- Name: ix_profile_projects_id; Type: INDEX; Schema: public; Owner: jobflow
--

CREATE INDEX ix_profile_projects_id ON public.profile_projects USING btree (id);


--
-- Name: ix_profile_skills_id; Type: INDEX; Schema: public; Owner: jobflow
--

CREATE INDEX ix_profile_skills_id ON public.profile_skills USING btree (id);


--
-- Name: ix_resume_versions_id; Type: INDEX; Schema: public; Owner: jobflow
--

CREATE INDEX ix_resume_versions_id ON public.resume_versions USING btree (id);


--
-- Name: ix_user_profiles_id; Type: INDEX; Schema: public; Owner: jobflow
--

CREATE INDEX ix_user_profiles_id ON public.user_profiles USING btree (id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: jobflow
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: jobflow
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: applications applications_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.applications
    ADD CONSTRAINT applications_job_id_fkey FOREIGN KEY (job_id) REFERENCES public.jobs(id) ON DELETE CASCADE;


--
-- Name: applications applications_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.applications
    ADD CONSTRAINT applications_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: master_resumes master_resumes_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.master_resumes
    ADD CONSTRAINT master_resumes_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: profile_achievements profile_achievements_profile_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.profile_achievements
    ADD CONSTRAINT profile_achievements_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES public.user_profiles(id) ON DELETE CASCADE;


--
-- Name: profile_education profile_education_profile_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.profile_education
    ADD CONSTRAINT profile_education_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES public.user_profiles(id) ON DELETE CASCADE;


--
-- Name: profile_experience profile_experience_profile_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.profile_experience
    ADD CONSTRAINT profile_experience_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES public.user_profiles(id) ON DELETE CASCADE;


--
-- Name: profile_projects profile_projects_profile_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.profile_projects
    ADD CONSTRAINT profile_projects_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES public.user_profiles(id) ON DELETE CASCADE;


--
-- Name: profile_skills profile_skills_profile_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.profile_skills
    ADD CONSTRAINT profile_skills_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES public.user_profiles(id) ON DELETE CASCADE;


--
-- Name: resume_versions resume_versions_application_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.resume_versions
    ADD CONSTRAINT resume_versions_application_id_fkey FOREIGN KEY (application_id) REFERENCES public.applications(id) ON DELETE CASCADE;


--
-- Name: resume_versions resume_versions_master_resume_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.resume_versions
    ADD CONSTRAINT resume_versions_master_resume_id_fkey FOREIGN KEY (master_resume_id) REFERENCES public.master_resumes(id) ON DELETE SET NULL;


--
-- Name: skill_evidence skill_evidence_skill_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.skill_evidence
    ADD CONSTRAINT skill_evidence_skill_id_fkey FOREIGN KEY (skill_id) REFERENCES public.profile_skills(id) ON DELETE CASCADE;


--
-- Name: user_profiles user_profiles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jobflow
--

ALTER TABLE ONLY public.user_profiles
    ADD CONSTRAINT user_profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict yVUxjDNTUtDbQzo6ZnOK62jV8tw8TvOeg9u5mzWteP6e1egRvmdzGhVLliXlaD8

