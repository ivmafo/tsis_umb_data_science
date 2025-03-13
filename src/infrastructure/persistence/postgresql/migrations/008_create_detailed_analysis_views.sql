-- PREGUNTAR A NILSON SI LA CAPACIDAD SE DEBE SACAR POR HORA
-- Vista para análisis detallado de sectores // REVISAR SI SE HACER SOBRE FECHA INICIAL
-- View: public.sector_detailed_analysis

-- DROP VIEW public.sector_detailed_analysis;

CREATE OR REPLACE VIEW public.sector_detailed_analysis
 AS
 WITH flight_times AS (
         SELECT fligths.origen AS sector,
            date_trunc('hour'::text, fligths.fecha) AS hora,
            count(*) AS num_vuelos,
            avg(EXTRACT(epoch FROM fligths.fecha_llegada::timestamp without time zone + fligths.hora_llegada::interval - (fligths.fecha_salida::timestamp without time zone + fligths.hora_salida::interval))) AS tps,
            count(DISTINCT fligths.tipo_aeronave) AS tipos_aeronaves,
            count(DISTINCT fligths.empresa) AS aerolineas,
            count(DISTINCT fligths.tipo_vuelo) AS tipos_vuelo
           FROM fligths
          GROUP BY fligths.origen, (date_trunc('hour'::text, fligths.fecha))
        )
 SELECT ft.sector,
    ft.hora,
    ft.num_vuelos,
    ft.tps,
    ft.tipos_aeronaves,
    ft.aerolineas,
    ft.tipos_vuelo,
    cfg_msg.value::integer * cfg_com.value::integer * ft.num_vuelos AS tiempo_total_comunicaciones,
    cfg_coord.value::integer * ft.num_vuelos AS tiempo_total_coordinacion,
    cfg_tareas.value::integer AS tiempo_tareas_observables,
        CASE
            WHEN ft.tipos_aeronaves > 3 OR ft.tipos_vuelo > 2 THEN cfg_comp_alta.value::numeric
            WHEN ft.tipos_aeronaves = 1 AND ft.tipos_vuelo = 1 THEN cfg_comp_baja.value::numeric
            ELSE cfg_comp_base.value::numeric
        END AS factor_complejidad
   FROM flight_times ft
     JOIN config cfg_msg ON cfg_msg.key::text = 'tiempo_mensaje_promedio'::text
     JOIN config cfg_com ON cfg_com.key::text = 'comunicaciones_promedio_aeronave'::text
     JOIN config cfg_coord ON cfg_coord.key::text = 'tiempo_coordinacion_promedio'::text
     JOIN config cfg_tareas ON cfg_tareas.key::text = 'tiempo_tareas_observables'::text
     JOIN config cfg_comp_alta ON cfg_comp_alta.key::text = 'factor_complejidad_alta'::text
     JOIN config cfg_comp_base ON cfg_comp_base.key::text = 'factor_complejidad_base'::text
     JOIN config cfg_comp_baja ON cfg_comp_baja.key::text = 'factor_complejidad_baja'::text;

ALTER TABLE public.sector_detailed_analysis
    OWNER TO postgres;



/********************************************/
/********************************************/
/************* VISTA CORREGIDA *************/
/********************************************/
/********************************************/
CREATE OR REPLACE VIEW public.sector_detailed_analysis AS
WITH flight_times AS (
    SELECT 
        fligths.origen AS sector,
        date_trunc('hour', fligths.fecha) AS hora,
        count(*) AS num_vuelos,
        avg(EXTRACT(epoch FROM (CAST(fligths.fecha_llegada AS timestamp) + fligths.hora_llegada::interval - (CAST(fligths.fecha_salida AS timestamp) + fligths.hora_salida::interval)))) AS tps,
        count(DISTINCT fligths.tipo_aeronave) AS tipos_aeronaves,
        count(DISTINCT fligths.empresa) AS aerolineas,
        count(DISTINCT fligths.tipo_vuelo) AS tipos_vuelo
    FROM fligths
    GROUP BY fligths.origen, date_trunc('hour', fligths.fecha)
)
SELECT 
    ft.sector,
    ft.hora,
    ft.num_vuelos,
    ft.tps,
    ft.tipos_aeronaves,
    ft.aerolineas,
    ft.tipos_vuelo,
    cfg_msg.value::integer * cfg_com.value::integer * ft.num_vuelos AS tiempo_total_comunicaciones,
    cfg_coord.value::integer * ft.num_vuelos AS tiempo_total_coordinacion,
    cfg_tareas.value::integer AS tiempo_tareas_observables,
    CASE 
        WHEN ft.tipos_aeronaves > 3 OR ft.tipos_vuelo > 2 THEN cfg_comp_alta.value::numeric
        WHEN ft.tipos_aeronaves = 1 AND ft.tipos_vuelo = 1 THEN cfg_comp_baja.value::numeric
        ELSE cfg_comp_base.value::numeric
    END AS factor_complejidad
FROM flight_times ft
JOIN config cfg_msg ON cfg_msg.key = 'tiempo_mensaje_promedio'
JOIN config cfg_com ON cfg_com.key = 'comunicaciones_promedio_aeronave'
JOIN config cfg_coord ON cfg_coord.key = 'tiempo_coordinacion_promedio'
JOIN config cfg_tareas ON cfg_tareas.key = 'tiempo_tareas_observables'
JOIN config cfg_comp_alta ON cfg_comp_alta.key = 'factor_complejidad_alta'
JOIN config cfg_comp_base ON cfg_comp_base.key = 'factor_complejidad_base'
JOIN config cfg_comp_baja ON cfg_comp_baja.key = 'factor_complejidad_baja';


/***********************************************************************/
/********************* FUNCION DE CALCULO DE SECTOR ********************/

-- DROP FUNCTION IF EXISTS public.calculate_detailed_sector_capacity(character varying, timestamp without time zone);

CREATE OR REPLACE FUNCTION public.calculate_detailed_sector_capacity(
	p_sector character varying,
	p_hora timestamp without time zone)
    RETURNS TABLE(sector character varying, hora timestamp without time zone, tps numeric, tfc numeric, tm numeric, tc numeric, tt numeric, factor_complejidad numeric, scv numeric, capacidad_horaria integer, carga_trabajo_total numeric) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
BEGIN
    RETURN QUERY
    WITH sector_metrics AS (
        SELECT 
            sda.*,
            sda.tiempo_total_comunicaciones AS tm,
            sda.tiempo_total_coordinacion AS tc,
            sda.tiempo_tareas_observables AS tt,
            (sda.tiempo_total_comunicaciones + 
             sda.tiempo_total_coordinacion + 
             sda.tiempo_tareas_observables) AS tfc
        FROM sector_detailed_analysis sda
        WHERE sda.sector = p_sector
        AND sda.hora = p_hora
    )
    SELECT 
        sm.sector,
        sm.hora,
        ROUND(sm.tps::DECIMAL, 2),
        ROUND(sm.tfc::DECIMAL, 2),
        ROUND(sm.tm::DECIMAL, 2),
        ROUND(sm.tc::DECIMAL, 2),
        ROUND(sm.tt::DECIMAL, 2),
        sm.factor_complejidad,
        ROUND((sm.tfc * 1.3 / NULLIF(sm.tps, 0))::DECIMAL, 2) as scv,
        ROUND(((3600 / NULLIF(sm.tps, 0)) * (sm.tfc * 1.3 / NULLIF(sm.tps, 0)))::DECIMAL, 0)::INTEGER as capacidad_horaria,
        ROUND((sm.tfc * sm.factor_complejidad)::DECIMAL, 2) as carga_trabajo_total
    FROM sector_metrics sm;
END;
$BODY$;

ALTER FUNCTION public.calculate_detailed_sector_capacity(character varying, timestamp without time zone)
    OWNER TO postgres;


/***************************/
/***************************/
/*****  MODO DE USO  *******/
/***************************/
/***************************/

SELECT * FROM calculate_detailed_sector_capacity('SKBO', '2017-02-01 00:00:00'::TIMESTAMP);









-- View: public.sector_detailed_analysis

-- DROP VIEW public.sector_detailed_analysis;

CREATE OR REPLACE VIEW public.sector_detailed_analysis
 AS
 WITH flight_times AS (
         SELECT fligths.origen AS sector,
            date_trunc('hour'::text, fligths.tiempo_inicial) AS hora,
            count(*) AS num_vuelos,
            avg(EXTRACT(epoch FROM fligths.fecha_llegada::timestamp without time zone + fligths.hora_llegada::interval - (fligths.fecha_salida::timestamp without time zone + fligths.hora_salida::interval))) AS tps,
            count(DISTINCT fligths.tipo_aeronave) AS tipos_aeronaves,
            count(DISTINCT fligths.empresa) AS aerolineas,
            count(DISTINCT fligths.tipo_vuelo) AS tipos_vuelo
           FROM fligths
          GROUP BY fligths.origen, (date_trunc('hour'::text, fligths.tiempo_inicial))
        )
 SELECT ft.sector,
    ft.hora,
    ft.num_vuelos,
    ft.tps,
    ft.tipos_aeronaves,
    ft.aerolineas,
    ft.tipos_vuelo,
    cfg_msg.value::integer + cfg_com.value::integer AS tiempo_total_comunicaciones,
    cfg_coord.value::integer AS tiempo_total_coordinacion,
    cfg_tareas.value::integer AS tiempo_tareas_observables,
        CASE
            WHEN ft.tipos_aeronaves > 3 OR ft.tipos_vuelo > 2 THEN cfg_comp_alta.value::numeric
            WHEN ft.tipos_aeronaves = 1 AND ft.tipos_vuelo = 1 THEN cfg_comp_baja.value::numeric
            ELSE cfg_comp_base.value::numeric
        END AS factor_complejidad
   FROM flight_times ft
     JOIN config cfg_msg ON cfg_msg.key::text = 'tiempo_mensaje_promedio'::text
     JOIN config cfg_com ON cfg_com.key::text = 'comunicaciones_promedio_aeronave'::text
     JOIN config cfg_coord ON cfg_coord.key::text = 'tiempo_coordinacion_promedio'::text
     JOIN config cfg_tareas ON cfg_tareas.key::text = 'tiempo_tareas_observables'::text
     JOIN config cfg_comp_alta ON cfg_comp_alta.key::text = 'factor_complejidad_alta'::text
     JOIN config cfg_comp_base ON cfg_comp_base.key::text = 'factor_complejidad_base'::text
     JOIN config cfg_comp_baja ON cfg_comp_baja.key::text = 'factor_complejidad_baja'::text;

ALTER TABLE public.sector_detailed_analysis
    OWNER TO postgres;
