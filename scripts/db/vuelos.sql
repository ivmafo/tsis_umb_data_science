-- Table: public.fligths

-- DROP TABLE IF EXISTS public.fligths;

CREATE TABLE IF NOT EXISTS public.fligths
(
    id integer NOT NULL DEFAULT nextval('fligths_id_seq'::regclass),
    fecha timestamp without time zone,
    sid integer,
    ssr integer,
    callsign character varying(10) COLLATE pg_catalog."default",
    matricula character varying(10) COLLATE pg_catalog."default",
    tipo_aeronave character varying(10) COLLATE pg_catalog."default",
    empresa character varying(50) COLLATE pg_catalog."default",
    numero_vuelo integer,
    tipo_vuelo character varying(1) COLLATE pg_catalog."default",
    tiempo_inicial timestamp without time zone,
    origen character varying(10) COLLATE pg_catalog."default",
    fecha_salida date,
    hora_salida time without time zone,
    hora_pv time without time zone,
    destino character varying(10) COLLATE pg_catalog."default",
    fecha_llegada date,
    hora_llegada time without time zone,
    nivel integer,
    duracion integer,
    distancia integer,
    velocidad integer,
    eq_ssr character varying(10) COLLATE pg_catalog."default",
    nombre_origen character varying(100) COLLATE pg_catalog."default",
    nombre_destino character varying(100) COLLATE pg_catalog."default",
    fecha_registro timestamp without time zone,
    CONSTRAINT fligths_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.fligths
    OWNER to postgres;