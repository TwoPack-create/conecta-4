# Conecta FCFM Mobile (Expo)

## Scaffold rápido

```bash
npx create-expo-app@latest conecta-fcfm-mobile --template blank-typescript
cd conecta-fcfm-mobile
npx expo install react-native-screens react-native-safe-area-context react-native-gesture-handler react-native-reanimated expo-auth-session expo-web-browser expo-linking expo-secure-store react-native-maps
npm install @react-navigation/native @react-navigation/drawer @react-navigation/native-stack @supabase/supabase-js zustand
```

## Estructura sugerida

```text
src/
  components/
  hooks/
  navigation/
  screens/
  services/
  store/
  theme/
  utils/
```

## Variables requeridas

Configurar en `.env`:

- `EXPO_PUBLIC_SUPABASE_URL`
- `EXPO_PUBLIC_SUPABASE_ANON_KEY`
- `EXPO_PUBLIC_API_BASE_URL`

## Flujo actual

- Login con Google usando Supabase OAuth.
- Pre-validación local de dominios institucionales permitidos.
- Estado global de sesión/JWT en Zustand.
- Cliente API centralizado que inyecta `Authorization: Bearer <jwt>` automáticamente.
- Header global con:
  - botón SOS deslizable (llama al `133` y dispara `POST /api/v1/safety/sos/trigger`),
  - escudo interactivo para iniciar Modo Acompáñame.
- Barra flotante global de Acompáñame con contador local y acción `Llegué a salvo`.
- Pantalla Inicio con bienvenida, accesos rápidos y placeholder de actividad reciente.
- Chat WebSocket backend disponible en: `ws(s)://<api>/api/v1/chat/ws/trips/{trip_id}?token=<jwt>`.

- TopTabs de movilidad para Transporte Público, Vehículo y Mis Viajes.
- Sincronización híbrida del contador Acompáñame con drift cliente-servidor en Zustand.
