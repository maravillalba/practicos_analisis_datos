-- TP N.º 3 - Base NO normalizada (tabla única) con los datos limpios del TP N.º 2
CREATE DATABASE IF NOT EXISTS club_deportivo_cerro_alto;
USE club_deportivo_cerro_alto;

DROP TABLE IF EXISTS socios;
CREATE TABLE socios (
    id INT,
    socio VARCHAR(100) NOT NULL,
    dni INT,
    alta DATE,
    actividad VARCHAR(50),
    cat VARCHAR(50),
    cuota DECIMAL(10, 2),
    estado VARCHAR(50),
    email VARCHAR(100),
    telefono VARCHAR(50),
    observaciones TEXT,
    antiguedad_meses DECIMAL(5, 1),
    condicion VARCHAR(20)   -- agregada: Vigente / Baja (TP N.º 2)
);

INSERT INTO socios (id, socio, dni, alta, actividad, cat, cuota, estado, email, telefono, observaciones, antiguedad_meses, condicion) VALUES
(101, 'Marcos Ibáñez', 34567890, '2024-03-15', 'Pádel', 'Activo', 18500.00, 'Pagado', 'marcos@mail.com', '3814123456', 'Socio al día', 31.00, 'Vigente'),
(102, 'Rocío Farías', 36789012, '2024-04-10', 'Pádel', 'Activo', 18500.00, 'Pendiente', 'Sin dato', '3814234567', 'Falta registrar mail', 30.00, 'Vigente'),
(103, 'Enzo Molina', 38901234, '2024-01-20', 'Natación', 'Activo', 18500.00, 'Pagado', 'enzo@mail.com', 'Sin dato', NULL, 33.00, 'Vigente'),
(104, 'Valentina Ruiz', 40123456, '2024-05-12', 'Fútbol 5', 'Activo', 18500.00, 'Pagado', 'vale@mail.com', '3814455667', 'Revisar signo', 29.00, 'Vigente'),
(105, 'Gonzalo Gómez', 35111222, '2023-11-05', 'Pádel', 'Cadete', NULL, 'Pagado', 'gonza@mail.com', '3814556677', 'Valor sospechoso cuota alto', 35.00, 'Vigente'),
(106, 'Lucía Peralta', 37222333, NULL, 'Fútbol 5', 'Activo', 18500.00, 'Pendiente', 'lucia@mail.com', '3814667788', 'Fecha inexistente 30 Feb', NULL, 'Vigente'),
(107, 'Agustín Silva', 39333444, '2024-06-01', 'Básquet', 'Vitalicio', 0.00, 'Exento', 'agustin@mail.com', '3814778899', 'Exento por estatuto', 28.00, 'Vigente'),
(108, 'Camila Torres', 41444555, '2024-02-14', 'Natación', 'Activo', 18500.00, 'Pagado', 'cami.torres@gmail.com', '3814889900', NULL, 32.00, 'Vigente'),
(109, 'Juan Pérez', 32555666, '2023-08-10', 'Pádel', 'Activo', 18500.00, 'Pagado', 'jperez@mail.com', '3814990011', NULL, 38.00, 'Vigente'),
(111, 'Mariana López', 33666777, '2022-05-18', 'Gimnasio', 'Sin dato', 18500.00, 'Vencido', 'marian@mail.com', 'Sin dato', 'Socio dado de baja en 2023 pero figura en cuotas', 53.00, 'Baja'),
(112, 'Carlos Rodríguez', 31777888, '2024-07-01', 'Fútbol 5', 'Activo', 18500.00, 'Pendiente', 'carlos.r@mail.com', '3815112233', NULL, 27.00, 'Vigente'),
(113, 'Sofía Martínez', 42888999, '2024-07-15', 'Pádel', 'Activo', 18500.00, 'Pagado', 'sofi@mail.com', '3815223344', NULL, 27.00, 'Vigente'),
(114, 'Mateo Romero', 43999000, '2024-08-01', 'Básquet', 'Cadete', 12000.00, 'Pagado', 'mateo@mail.com', '3815334455', NULL, 26.00, 'Vigente'),
(115, 'Elena Díaz', 30000111, '2024-08-05', 'Natación', 'Activo', 18500.00, 'Pendiente', 'elena@mail.com', 'Sin dato', NULL, 26.00, 'Vigente'),
(116, 'Nicolás Benítez', 38111222, '2024-03-22', 'Fútbol 5', 'Activo', 18500.00, 'Pagado', 'nico@mail.com', '3815556677', NULL, 31.00, 'Vigente'),
(117, 'Paula Morales', 39222333, '2024-04-18', 'Pádel', 'Activo', 18500.00, 'Pagado', 'paula@mail.com', '3815667788', NULL, 30.00, 'Vigente'),
(118, 'Lucas Ferreyra', 40333444, '2024-01-10', 'Tenis', 'Activo', 22000.00, 'Pagado', 'lucas@mail.com', '3815778899', NULL, 33.00, 'Vigente'),
(119, 'Florencia Castro', 41444555, '2026-09-30', 'Gimnasio', 'Activo', 18500.00, 'Pagado', 'flor@mail.com', '3815889900', 'Alta 30/09/2026 válida (observación original desactualizada)', 1.00, 'Vigente'),
(120, 'Gabriel Trevisan', 28555666, '2021-03-01', 'Pádel', 'Honorario', 0.00, 'Exento', 'g.trevisan@cerroalto.ar', '3815990011', 'Profesor/Referente', 67.00, 'Vigente');

-- Q1: ¿Cuántos socios vigentes tiene el club y en qué actividades se concentran?
SELECT actividad,
       COUNT(*) AS socios_vigentes
FROM socios
WHERE condicion = 'Vigente'
GROUP BY actividad
ORDER BY socios_vigentes DESC;

-- Q2a: ¿Qué parte de los socios vigentes tiene la cuota al día? (detalle por estado)
SELECT estado,
       COUNT(*) AS cantidad,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM socios WHERE condicion = 'Vigente'), 1) AS porcentaje,
       SUM(cuota) AS monto
FROM socios
WHERE condicion = 'Vigente'
GROUP BY estado
ORDER BY cantidad DESC;

-- Q2b: ¿Qué porcentaje de los socios que deben pagar está al día y cuánto dinero está pendiente?
SELECT COUNT(*) AS socios_que_pagan_cuota,
       SUM(CASE WHEN estado = 'Pagado' THEN 1 ELSE 0 END) AS al_dia,
       ROUND(SUM(CASE WHEN estado = 'Pagado' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS porcentaje_al_dia,
       SUM(CASE WHEN estado = 'Pendiente' THEN cuota ELSE 0 END) AS monto_pendiente
FROM socios
WHERE condicion = 'Vigente'
  AND estado <> 'Exento';

-- Q3: ¿En qué actividades se concentra la morosidad?
SELECT actividad,
       COUNT(*) AS socios_que_pagan,
       SUM(CASE WHEN estado = 'Pendiente' THEN 1 ELSE 0 END) AS pendientes,
       ROUND(SUM(CASE WHEN estado = 'Pendiente' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS porcentaje_pendiente,
       SUM(CASE WHEN estado = 'Pendiente' THEN cuota ELSE 0 END) AS monto_pendiente
FROM socios
WHERE condicion = 'Vigente'
  AND estado <> 'Exento'
GROUP BY actividad
ORDER BY porcentaje_pendiente DESC, pendientes DESC;

-- Q4: ¿Cuál es la cuota promedio por tipo de socio?
SELECT cat AS tipo_socio,
       COUNT(cuota) AS socios_con_cuota,
       ROUND(AVG(cuota), 2) AS cuota_promedio,
       MIN(cuota) AS cuota_minima,
       MAX(cuota) AS cuota_maxima
FROM socios
WHERE condicion = 'Vigente'
  AND cuota > 0          -- excluye exentos ($0) y la cuota a verificar (NULL)
GROUP BY cat
ORDER BY cuota_promedio DESC;

-- Q5: ¿Cómo evolucionaron las altas de socios por año? (versión MySQL;
-- en el informe se resolvió con Pandas: no muestra los años sin altas, como 2025)
SELECT YEAR(alta) AS anio, COUNT(*) AS altas
FROM socios
WHERE alta IS NOT NULL
GROUP BY YEAR(alta)
ORDER BY anio;
