# Conecta FCFM — Análisis inicial del PRD (Paso 0)

## Entendimiento del producto
- Red social hiperlocal y exclusiva para comunidad FCFM.
- Dos verticales de movilidad: Transporte Público (metro/micro/a pie) y Vehículos (carpooling con donación sugerida).
- Capa de seguridad activa: SOS, blips de riesgo, reportes comunitarios y modo Acompáñame con temporizador backend.
- Autenticación con Google vía Supabase restringida a dominios institucionales permitidos.

## Alcance del siguiente paso técnico
Antes de generar SQL final para Supabase, se validarán decisiones de modelado para:
- tablas núcleo de identidad y perfiles,
- viajes y participación,
- reportes/blips,
- acompañamiento/sesiones de seguridad,
- contactos de emergencia,
- mensajería y calificaciones,
- RLS por rol/propietario/participación.

## Preguntas de validación (bloqueantes para SQL definitivo)
1. ¿Los usuarios podrán pertenecer a múltiples dominios válidos (por ejemplo, mismo usuario con alias @ug y @ing) o se guardará solo el correo principal de Supabase Auth?
2. ¿Necesitamos multi-campus o solo FCFM Beauchef por ahora (para geocercas y validación de ubicaciones)?
3. Para viajes de transporte público: ¿el “creador” define cupos máximos o los grupos son ilimitados?
4. Para viajes en vehículo: ¿la donación sugerida se guarda como entero CLP y puede editarse tras publicar?
5. ¿El chat grupal será dentro de Supabase (tabla mensajes) o un servicio externo en una fase posterior?
6. ¿Blips de riesgo deben expirar automáticamente? Si sí, ¿tiempo por defecto (ej. 2h, 6h, 24h)?
7. En reportes de rutas: ¿la votación es una vez por usuario por reporte (up/down) con posibilidad de cambiar voto?
8. Modo Acompáñame: ¿se permite compartir ubicación continua durante el temporizador, o solo última ubicación al expirar?
9. Contactos de emergencia: ¿máximo 3 contactos estricto a nivel BD?
10. ¿Debemos soportar “grupos de emergencia” (colección de contactos) en MVP o solo contactos individuales?
11. ¿Quién puede ver datos bancarios del conductor: solo pasajeros que completaron el viaje o también participantes activos?
12. Calificaciones: ¿se califican personas (usuario→usuario) por viaje completado, anónimas para receptor, y una sola vez por par de usuarios por viaje?
13. ¿Necesitamos rol administrador/moderador en MVP para ocultar reportes/blips y gestionar abuso?
14. ¿Retención de datos de seguridad (SOS, acompañamiento, ubicaciones): cuánto tiempo conservar en BD?
15. ¿RLS de reportes/blips será lectura abierta para toda la comunidad autenticada y escritura solo autor autenticado?

