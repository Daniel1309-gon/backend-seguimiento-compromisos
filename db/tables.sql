-- Table: public.auditor

-- DROP TABLE IF EXISTS public.auditor;

CREATE TABLE IF NOT EXISTS public.auditor
(
    aud_user character varying(20) COLLATE pg_catalog."default" NOT NULL DEFAULT 'DAI'::character varying,
    aud_name character varying(40) COLLATE pg_catalog."default" NOT NULL,
    estado character varying(10) COLLATE pg_catalog."default" NOT NULL DEFAULT 'Activo'::character varying,
    CONSTRAINT usuario PRIMARY KEY (aud_user)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.auditor
    OWNER to postgres;

-- Trigger: t_audit_auditor

-- DROP TRIGGER IF EXISTS t_audit_auditor ON public.auditor;

CREATE OR REPLACE TRIGGER t_audit_auditor
    AFTER INSERT OR DELETE
    ON public.auditor
    FOR EACH ROW
    EXECUTE FUNCTION public.log_auditor();



-- Table: public.auditoria

-- DROP TABLE IF EXISTS public.auditoria;

CREATE TABLE IF NOT EXISTS public.auditoria
(
    id_aud integer NOT NULL DEFAULT nextval('auditoria_id_aud_seq'::regclass),
    user_aud character varying(20) COLLATE pg_catalog."default" NOT NULL,
    topic character varying(40) COLLATE pg_catalog."default" NOT NULL,
    area character varying(50) COLLATE pg_catalog."default" NOT NULL,
    date_onbase date NOT NULL DEFAULT ((now() AT TIME ZONE 'America/Bogota'::text))::date,
    radicate_onbase character varying(15) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT auditoria_pkey PRIMARY KEY (id_aud),
    CONSTRAINT "auditor_dueño" FOREIGN KEY (user_aud)
        REFERENCES public.auditor (aud_user) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.auditoria
    OWNER to postgres;

-- Trigger: t_audit_auditoria

-- DROP TRIGGER IF EXISTS t_audit_auditoria ON public.auditoria;

CREATE OR REPLACE TRIGGER t_audit_auditoria
    AFTER INSERT OR DELETE OR UPDATE 
    ON public.auditoria
    FOR EACH ROW
    EXECUTE FUNCTION public.log_auditoria();



-- Table: public.compromiso

-- DROP TABLE IF EXISTS public.compromiso;

CREATE TABLE IF NOT EXISTS public.compromiso
(
    id_com integer NOT NULL DEFAULT nextval('compromiso_id_com_seq'::regclass),
    op_id integer NOT NULL,
    action text COLLATE pg_catalog."default" NOT NULL,
    deadline date NOT NULL DEFAULT (((now() AT TIME ZONE 'America/Bogota'::text))::date + '2 mons'::interval),
    estado character varying(10) COLLATE pg_catalog."default" NOT NULL DEFAULT 'En proceso'::character varying,
    CONSTRAINT compromiso_pkey PRIMARY KEY (id_com),
    CONSTRAINT op_de_mejora FOREIGN KEY (op_id)
        REFERENCES public.op_mejora (id_op) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.compromiso
    OWNER to postgres;

-- Trigger: t_audit_compromiso

-- DROP TRIGGER IF EXISTS t_audit_compromiso ON public.compromiso;

CREATE OR REPLACE TRIGGER t_audit_compromiso
    AFTER INSERT OR DELETE OR UPDATE 
    ON public.compromiso
    FOR EACH ROW
    EXECUTE FUNCTION public.log_compromiso();



-- Table: public.op_mejora

-- DROP TABLE IF EXISTS public.op_mejora;

CREATE TABLE IF NOT EXISTS public.op_mejora
(
    id_op integer NOT NULL DEFAULT nextval('op_mejora_id_op_seq'::regclass),
    aud_id integer NOT NULL,
    description text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT op_mejora_pkey PRIMARY KEY (id_op),
    CONSTRAINT auditoria FOREIGN KEY (aud_id)
        REFERENCES public.auditoria (id_aud) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.op_mejora
    OWNER to postgres;

-- Trigger: t_audit_op_mejora

-- DROP TRIGGER IF EXISTS t_audit_op_mejora ON public.op_mejora;

CREATE OR REPLACE TRIGGER t_audit_op_mejora
    AFTER INSERT OR DELETE OR UPDATE 
    ON public.op_mejora
    FOR EACH ROW
    EXECUTE FUNCTION public.log_op_mejora();



-- Table: public.seguimiento

-- DROP TABLE IF EXISTS public.seguimiento;

CREATE TABLE IF NOT EXISTS public.seguimiento
(
    id_seg integer NOT NULL DEFAULT nextval('seguimiento_id_seg_seq'::regclass),
    com_id integer NOT NULL,
    created_by character varying(20) COLLATE pg_catalog."default" NOT NULL,
    observation text COLLATE pg_catalog."default" NOT NULL,
    created_at date NOT NULL DEFAULT (now() AT TIME ZONE 'America/Bogota'::text),
    CONSTRAINT seguimiento_pkey PRIMARY KEY (id_seg),
    CONSTRAINT seguimiento_com_id_fkey FOREIGN KEY (com_id)
        REFERENCES public.compromiso (id_com) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT seguimiento_created_by_fkey FOREIGN KEY (created_by)
        REFERENCES public.auditor (aud_user) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.seguimiento
    OWNER to postgres;
-- Index: ix_seguimiento_id_seg

-- DROP INDEX IF EXISTS public.ix_seguimiento_id_seg;

CREATE INDEX IF NOT EXISTS ix_seguimiento_id_seg
    ON public.seguimiento USING btree
    (id_seg ASC NULLS LAST)
    TABLESPACE pg_default;



-- Table: public.system_logs

-- DROP TABLE IF EXISTS public.system_logs;

CREATE TABLE IF NOT EXISTS public.system_logs
(
    id integer NOT NULL DEFAULT nextval('system_logs_id_seq'::regclass),
    table_name character varying(50) COLLATE pg_catalog."default",
    action character varying(10) COLLATE pg_catalog."default",
    record_id text COLLATE pg_catalog."default",
    old_data text COLLATE pg_catalog."default",
    new_data text COLLATE pg_catalog."default",
    changed_at timestamp without time zone DEFAULT (now() AT TIME ZONE 'America/Bogota'::text),
    app_user character varying(100) COLLATE pg_catalog."default",
    db_user character varying(50) COLLATE pg_catalog."default" DEFAULT CURRENT_USER,
    CONSTRAINT system_logs_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.system_logs
    OWNER to postgres;