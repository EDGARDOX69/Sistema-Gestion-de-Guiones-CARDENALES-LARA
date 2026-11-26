CREATE TABLE `asignaciones_recursos` (
  `id` int(11) NOT NULL,
  `recurso_id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `fecha_asignacion` datetime DEFAULT current_timestamp(),
  `fecha_devolucion_esperada` date DEFAULT NULL,
  `fecha_devolucion_real` datetime DEFAULT NULL,
  `estado_asignacion_id` int(11) DEFAULT 1,
  `notas` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `contrato`
--

CREATE TABLE `contrato` (
  `id_contrato` int(11) NOT NULL,
  `id_patrocinador` int(11) NOT NULL,
  `fecha_inicio` date NOT NULL,
  `fecha_fin` date NOT NULL,
  `estado` varchar(100) NOT NULL,
  `estatus` varchar(100) NOT NULL,
  `tipo` varchar(50) NOT NULL,
  `monto_total` decimal(12,2) NOT NULL DEFAULT 0.00
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `contrato`
--

INSERT INTO `contrato` (`id_contrato`, `id_patrocinador`, `fecha_inicio`, `fecha_fin`, `estado`, `estatus`, `tipo`, `monto_total`) VALUES
(1, 1, '2026-04-01', '2026-10-31', '1', 'Vigente', '2', 85000.00),
(2, 2, '2026-05-01', '2026-09-30', '1', 'Vigente', '2', 62000.00),
(3, 3, '2026-06-01', '2026-08-31', '1', 'Vigente', '1', 25000.00),
(4, 4, '2026-04-15', '2026-07-15', '0', 'Vencido', '1', 30000.00),
(5, 5, '2026-03-01', '2026-12-31', '1', 'Vigente', '3', 120000.00),
(6, 6, '2026-06-01', '2026-09-30', '1', 'Vigente', '1', 18000.00),
(7, 7, '2026-07-01', '2026-09-30', '1', 'Vigente', '1', 15000.00),
(8, 8, '2026-04-01', '2026-11-30', '1', 'Vigente', '2', 45000.00),
(9, 9, '2026-05-15', '2026-08-15', '1', 'Vigente', '1', 22000.00);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `departamentos`
--

CREATE TABLE `departamentos` (
  `id` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `descripcion` varchar(200) DEFAULT NULL,
  `color` varchar(7) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `departamentos`
--

INSERT INTO `departamentos` (`id`, `nombre`, `descripcion`, `color`) VALUES
(1, 'Producción', 'Puesta en escena, guiones y transmisión', '#e74c3c'),
(2, 'Técnica', 'Soporte técnico, mantenimiento de equipos', '#3498db'),
(3, 'Comercial', 'Gestión de patrocinadores y contratos', '#2ecc71'),
(4, 'Administración', 'Gestión general del estadio', '#9b59b6'),
(5, 'Operaciones', 'Operaciones en vivo y palco', '#f39c12');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `elementos_guion`
--

CREATE TABLE `elementos_guion` (
  `id` int(11) NOT NULL,
  `guion_id` int(11) NOT NULL,
  `fecha_id` int(11) DEFAULT NULL,
  `tipo` varchar(20) NOT NULL,
  `hora` time DEFAULT NULL,
  `inning` int(11) DEFAULT NULL,
  `medio_inning` varchar(10) DEFAULT NULL,
  `contenido` text NOT NULL,
  `duracion_estimada` int(11) NOT NULL,
  `encargado` varchar(100) NOT NULL,
  `orden` int(11) DEFAULT NULL,
  `creado_en` datetime DEFAULT NULL,
  `estado` varchar(20) DEFAULT NULL,
  `inicio_curso` datetime DEFAULT NULL COMMENT 'Momento de entrada a en_curso'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `elementos_guion`
--

INSERT INTO `elementos_guion` (`id`, `guion_id`, `fecha_id`, `tipo`, `hora`, `inning`, `medio_inning`, `contenido`, `duracion_estimada`, `encargado`, `orden`, `creado_en`, `estado`, `inicio_curso`) VALUES
(1, 1, 1, 'pregame', '17:00:00', NULL, NULL, 'Apertura de puertas y bienvenida', 300, 'keiver', 1, '2026-07-08 09:05:00', 'pendiente', NULL),
(2, 1, 1, 'pregame', '17:30:00', NULL, NULL, 'Presentación de alineaciones por pantallas', 180, 'Genesis', 2, '2026-07-08 09:06:00', 'pendiente', NULL),
(3, 1, 1, 'pregame', '18:00:00', NULL, NULL, 'Ceremonia de lanzamiento inaugural', 240, 'keiver', 3, '2026-07-08 09:07:00', 'pendiente', NULL),
(4, 1, 1, 'pregame', '18:15:00', NULL, NULL, 'Himno Nacional - Orquesta del Estado', 180, 'Genesis', 4, '2026-07-08 09:08:00', 'pendiente', NULL),
(5, 1, 1, 'pregame', '18:20:00', NULL, NULL, 'Video bienvenida patrocinadores', 60, 'keiver', 5, '2026-07-08 09:09:00', 'pendiente', NULL),
(6, 1, 1, 'game', NULL, 1, 'baja', 'Publicidad Maltin Polar - Jumbotron', 30, 'keiver', 1, '2026-07-08 09:10:00', NULL, NULL),
(7, 1, 1, 'game', NULL, 1, 'alta', 'Publicidad Pepsi - Bafles del estadio', 30, 'Genesis', 2, '2026-07-08 09:11:00', NULL, NULL),
(8, 1, 1, 'game', NULL, 2, 'baja', 'Concurso Maltin Polar - Lanzamiento de pelota', 120, 'keiver', 3, '2026-07-08 09:12:00', NULL, NULL),
(9, 1, 1, 'game', NULL, 3, 'alta', 'Publicidad Banesco - Finanzas personales', 30, 'Genesis', 4, '2026-07-08 09:13:00', NULL, NULL),
(10, 1, 1, 'game', NULL, 4, 'baja', 'Reels Café Flor de Arauca', 25, 'keiver', 5, '2026-07-08 09:14:00', NULL, NULL),
(11, 1, 1, 'game', NULL, 5, 'alta', 'Publicidad Movilnet - Plan datos beisbol', 30, 'Genesis', 6, '2026-07-08 09:15:00', NULL, NULL),
(12, 1, 1, 'game', NULL, 6, 'baja', 'Ceremonia de premiación fan del juego', 180, 'keiver', 7, '2026-07-08 09:16:00', NULL, NULL),
(13, 1, 1, 'game', NULL, 7, 'alta', 'Publicidad Farmatodo - Salud y bienestar', 30, 'Genesis', 8, '2026-07-08 09:17:00', NULL, NULL),
(14, 1, 1, 'game', NULL, 8, 'baja', 'Reels Cerveza Regional', 25, 'keiver', 9, '2026-07-08 09:18:00', NULL, NULL),
(15, 1, 1, 'postgame', NULL, NULL, NULL, 'Entrega de premios a ganadores', 300, 'keiver', 1, '2026-07-08 09:19:00', NULL, NULL),
(16, 1, 1, 'postgame', NULL, NULL, NULL, 'Entrevistas post-juego y agradecimientos', 600, 'Genesis', 2, '2026-07-08 09:20:00', NULL, NULL),
(17, 2, 2, 'pregame', '17:00:00', NULL, NULL, 'Apertura de puertas', 300, 'keiver', 1, '2026-07-10 10:05:00', 'pendiente', NULL),
(18, 2, 2, 'pregame', '17:30:00', NULL, NULL, 'Presentación de alineaciones', 180, 'Genesis', 2, '2026-07-10 10:06:00', 'pendiente', NULL),
(19, 2, 2, 'pregame', '18:00:00', NULL, NULL, 'Ceremonia de lanzamiento inaugural', 240, 'keiver', 3, '2026-07-10 10:07:00', 'pendiente', NULL),
(20, 2, 2, 'pregame', '18:15:00', NULL, NULL, 'Himno Nacional', 180, 'Genesis', 4, '2026-07-10 10:08:00', 'pendiente', NULL),
(21, 2, 2, 'game', NULL, 1, 'baja', 'Publicidad Maltin Polar', 30, 'keiver', 1, '2026-07-10 10:10:00', NULL, NULL),
(22, 2, 2, 'game', NULL, 2, 'baja', 'Concurso Alimentos Mary - Sabor del juego', 120, 'keiver', 2, '2026-07-10 10:11:00', NULL, NULL),
(23, 2, 2, 'game', NULL, 3, 'alta', 'Publicidad Tubrica', 30, 'Genesis', 3, '2026-07-10 10:12:00', NULL, NULL),
(24, 2, 2, 'game', NULL, 5, 'baja', 'Reels Banesco', 25, 'keiver', 4, '2026-07-10 10:13:00', NULL, NULL),
(25, 2, 2, 'game', NULL, 7, 'alta', 'Publicidad Pepsi', 30, 'Genesis', 5, '2026-07-10 10:14:00', NULL, NULL),
(26, 3, 3, 'pregame', '18:00:00', NULL, NULL, 'Apertura de puertas y animación', 300, 'keiver', 1, '2026-07-10 11:05:00', 'pendiente', NULL),
(27, 3, 3, 'pregame', '18:30:00', NULL, NULL, 'Himno Nacional y presentación', 240, 'Genesis', 2, '2026-07-10 11:06:00', 'pendiente', NULL),
(28, 3, 3, 'game', NULL, 1, 'baja', 'Publicidad Movilnet', 30, 'keiver', 1, '2026-07-10 11:08:00', NULL, NULL),
(29, 3, 3, 'game', NULL, 3, 'baja', 'Concurso Café Flor de Arauca', 120, 'keiver', 2, '2026-07-10 11:09:00', NULL, NULL),
(30, 3, 3, 'game', NULL, 5, 'alta', 'Publicidad Farmatodo', 30, 'Genesis', 3, '2026-07-10 11:10:00', NULL, NULL),
(31, 3, 3, 'game', NULL, 7, 'baja', 'Reels Cerveza Regional', 25, 'keiver', 4, '2026-07-10 11:11:00', NULL, NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `estado_asignacion`
--

CREATE TABLE `estado_asignacion` (
  `id` int(11) NOT NULL,
  `nombre` varchar(30) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `estado_asignacion`
--

INSERT INTO `estado_asignacion` (`id`, `nombre`, `descripcion`) VALUES
(1, 'Pendiente', 'Asignación activa, pendiente de devolución'),
(2, 'Devuelto', 'Recurso devuelto exitosamente'),
(3, 'Vencido', 'Asignación vencida (no devuelto a tiempo)');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `estado_recurso`
--

CREATE TABLE `estado_recurso` (
  `id` int(11) NOT NULL,
  `nombre` varchar(30) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `estado_recurso`
--

INSERT INTO `estado_recurso` (`id`, `nombre`, `descripcion`) VALUES
(1, 'Disponible', 'Recurso disponible para uso o asignación'),
(2, 'Asignado', 'Recurso actualmente asignado a un usuario'),
(3, 'En Mantenimiento', 'Recurso en proceso de mantenimiento o reparación'),
(4, 'Dañado', 'Recurso reportado como dañado'),
(5, 'Baja', 'Recurso dado de baja del inventario');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `guiones`
--

CREATE TABLE `guiones` (
  `id` int(11) NOT NULL,
  `nombre` varchar(200) NOT NULL,
  `estado` varchar(20) DEFAULT NULL,
  `inicio_show` datetime DEFAULT NULL COMMENT 'Momento de Iniciar del show en vivo',
  `creado_en` datetime DEFAULT NULL,
  `modificado_en` datetime DEFAULT NULL,
  `tiempo_inning` int(11) DEFAULT NULL,
  `grupo_id` varchar(36) DEFAULT NULL,
  `status` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `guiones`
--

INSERT INTO `guiones` (`id`, `nombre`, `estado`, `inicio_show`, `creado_en`, `modificado_en`, `tiempo_inning`, `grupo_id`, `status`) VALUES
(1, 'Cardenales vs Leones - 2026-07-10', 'publicado', NULL, '2026-07-08 09:00:00', '2026-07-09 14:30:00', 120, NULL, 1),
(2, 'Cardenales vs Tiburones - 2026-07-12', 'borrador', NULL, '2026-07-10 10:00:00', '2026-07-10 10:00:00', 120, NULL, 1),
(3, 'Cardenales vs Navegantes - 2026-07-15', 'borrador', NULL, '2026-07-10 11:00:00', '2026-07-10 11:00:00', 120, NULL, 1),
(4, 'Cardenales vs Tigres - 2026-07-18', 'borrador', NULL, '2026-07-10 12:00:00', '2026-07-10 12:00:00', 120, NULL, 1),
(5, 'Cardenales vs Águilas - 2026-07-20', 'borrador', NULL, '2026-07-10 13:00:00', '2026-07-10 13:00:00', 120, NULL, 1),
(6, 'UI 81267f - 2026-11-25', 'borrador', NULL, '2026-11-25 09:55:15', '2026-11-25 09:55:16', 120, NULL, 0),
(7, 'UI 1b97b0 - 2026-11-25', 'borrador', NULL, '2026-11-25 09:55:21', '2026-11-25 09:55:22', 120, NULL, 0);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `guion_fechas`
--

CREATE TABLE `guion_fechas` (
  `id` int(11) NOT NULL,
  `guion_id` int(11) NOT NULL,
  `fecha` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `guion_fechas`
--

INSERT INTO `guion_fechas` (`id`, `guion_id`, `fecha`) VALUES
(1, 1, '2026-07-10'),
(2, 2, '2026-07-12'),
(3, 3, '2026-07-15'),
(4, 4, '2026-07-18'),
(5, 5, '2026-07-20'),
(6, 6, '2026-11-25'),
(7, 7, '2026-11-25');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `historial_chat`
--

CREATE TABLE `historial_chat` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `mensaje_usuario` text NOT NULL,
  `respuesta_ia` text NOT NULL,
  `contexto` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`contexto`)),
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `historial_mantenimiento`
--

CREATE TABLE `historial_mantenimiento` (
  `id` int(11) NOT NULL,
  `mantenimiento_id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `accion` varchar(50) NOT NULL,
  `descripcion` text NOT NULL,
  `creado_en` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `mantenimientos`
--

CREATE TABLE `mantenimientos` (
  `id` int(11) NOT NULL,
  `recurso_id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `estado` varchar(20) DEFAULT 'en_espera',
  `fecha_ingreso` date NOT NULL,
  `fecha_salida` date DEFAULT NULL,
  `diagnostico` text DEFAULT NULL,
  `observaciones` text DEFAULT NULL,
  `creado_en` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pagos`
--

CREATE TABLE `pagos` (
  `id_pago` int(11) NOT NULL,
  `id_contrato` int(11) NOT NULL,
  `monto` decimal(12,2) NOT NULL,
  `tipo_pago` varchar(20) NOT NULL,
  `referencia` varchar(100) DEFAULT NULL,
  `fecha_pago` date NOT NULL,
  `hora_pago` time NOT NULL,
  `registrado_por` int(11) DEFAULT NULL,
  `Descripcion` text DEFAULT NULL,
  `fecha_registro` datetime DEFAULT current_timestamp(),
  `estado` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `pagos`
--

INSERT INTO `pagos` (`id_pago`, `id_contrato`, `monto`, `tipo_pago`, `referencia`, `fecha_pago`, `hora_pago`, `registrado_por`, `Descripcion`, `fecha_registro`, `estado`) VALUES
(1, 1, 21250.00, 'Transferencia', 'TRF-2026-001', '2026-04-05', '10:00:00', 3, 'Pago inicial contrato Maltin Polar - 25%', '2026-04-05 10:05:00', 0),
(2, 1, 21250.00, 'Transferencia', 'TRF-2026-002', '2026-06-05', '10:00:00', 3, 'Segundo abono contrato Maltin Polar - 25%', '2026-06-05 10:05:00', 0),
(3, 2, 15500.00, 'Transferencia', 'TRF-2026-003', '2026-05-10', '11:00:00', 4, 'Pago inicial contrato Pepsi - 25%', '2026-05-10 11:05:00', 0),
(4, 5, 30000.00, 'Transferencia', 'TRF-2026-004', '2026-03-15', '09:30:00', 3, 'Pago inicial contrato Banesco - 25%', '2026-03-15 09:35:00', 0),
(5, 5, 30000.00, 'Transferencia', 'TRF-2026-005', '2026-06-15', '09:30:00', 3, 'Segundo abono contrato Banesco - 25%', '2026-06-15 09:35:00', 0),
(6, 8, 11250.00, 'Efectivo', 'EFE-2026-001', '2026-04-10', '14:00:00', 5, 'Pago inicial contrato Farmatodo - 25%', '2026-04-10 14:05:00', 0),
(7, 3, 6250.00, 'Efectivo', 'EFE-2026-002', '2026-06-10', '15:00:00', 5, 'Pago inicial contrato Café Flor - 50%', '2026-06-10 15:05:00', 0),
(8, 9, 5500.00, 'Transferencia', 'TRF-2026-006', '2026-05-20', '16:00:00', 6, 'Pago inicial contrato Cerveza Regional - 25%', '2026-05-20 16:05:00', 0);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `patrocinadores`
--

CREATE TABLE `patrocinadores` (
  `id_patrocinador` int(11) NOT NULL,
  `nombre_empresa` varchar(100) NOT NULL,
  `rif` varchar(20) NOT NULL,
  `tipo_contrato` int(11) NOT NULL,
  `nombre_contacto` text NOT NULL,
  `telefono` varchar(20) NOT NULL,
  `email` varchar(100) NOT NULL,
  `estado` int(11) NOT NULL,
  `encargado_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `patrocinadores`
--

INSERT INTO `patrocinadores` (`id_patrocinador`, `nombre_empresa`, `rif`, `tipo_contrato`, `nombre_contacto`, `telefono`, `email`, `estado`, `encargado_id`) VALUES
(1, 'Maltin Polar', 'J-00005820-9', 2, 'José Luis Rodríguez', '0212-4003000', 'jrodriguez@polar.com', 1, 3),
(2, 'Pepsi Venezuela', 'J-00028049-5', 2, 'María Fernanda López', '0212-5002000', 'mlopez@pepsi.com', 1, 4),
(3, 'Café Flor de Arauca', 'J-40206831-0', 1, 'Carlos Mendoza', '0251-2661100', 'cmendoza@cafeflor.com', 1, 5),
(4, 'Tubrica C.A', 'J-31028456-7', 1, 'Pedro Jiménez', '0241-8581000', 'p jimenez@tubrica.com', 1, 6),
(5, 'Banesco Banco Universal', 'J-00078321-3', 2, 'Ana Sofía Pérez', '0212-2064646', 'aperez@banesco.com', 1, 3),
(6, 'Movilnet C.A', 'J-30472189-0', 1, 'Roberto Díaz', '0212-3001000', 'rdiaz@movilnet.com', 1, 4),
(7, 'Alimentos Mary', 'J-29587314-6', 1, 'Luis Hernández', '0241-8782000', 'lhernandez@alimentosmary.com', 1, 5),
(8, 'Farmatodo C.A', 'J-00032815-8', 2, 'Gabriela Torres', '0212-7003000', 'gtorres@farmatodo.com', 1, 6),
(9, 'Cerveza Regional', 'J-40157623-8', 1, 'Manuel Castillo', '0261-7984000', 'mcastillo@regional.com', 1, 3);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `premios`
--

CREATE TABLE `premios` (
  `id` int(11) NOT NULL,
  `id_patrocinador` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `estado` varchar(20) DEFAULT 'pendiente',
  `fecha_creacion` date DEFAULT NULL,
  `fecha_entrega` datetime DEFAULT NULL,
  `entregado_por` int(11) DEFAULT NULL,
  `hora_creacion` time NOT NULL,
  `foto` varchar(200) DEFAULT 'default-premio.png',
  `cantidad` int(11) NOT NULL DEFAULT 1,
  `cantidad_entregada` int(11) NOT NULL DEFAULT 0,
  `estatus` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `premios`
--

INSERT INTO `premios` (`id`, `id_patrocinador`, `nombre`, `descripcion`, `estado`, `fecha_creacion`, `fecha_entrega`, `entregado_por`, `hora_creacion`, `foto`, `cantidad`, `cantidad_entregada`, `estatus`) VALUES
(1, 1, '6 Pack Maltin Polar', '
