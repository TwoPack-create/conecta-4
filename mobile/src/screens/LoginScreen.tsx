import * as Linking from 'expo-linking';
import * as WebBrowser from 'expo-web-browser';
import { useMemo, useState } from 'react';
import { Alert, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';

import { isAllowedInstitutionalEmail, supabase } from '@/services/supabase';

WebBrowser.maybeCompleteAuthSession();

export function LoginScreen() {
  const [emailForValidation, setEmailForValidation] = useState('');
  const redirectTo = useMemo(() => Linking.createURL('/auth/callback'), []);

  const loginWithGoogle = async () => {
    if (emailForValidation && !isAllowedInstitutionalEmail(emailForValidation)) {
      Alert.alert('Acceso restringido', 'Solo se permiten correos institucionales válidos.');
      return;
    }

    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo, queryParams: { prompt: 'select_account' } },
    });

    if (error) {
      Alert.alert('Error de autenticación', error.message);
      return;
    }

    if (data?.url) {
      const result = await WebBrowser.openAuthSessionAsync(data.url, redirectTo);
      if (result.type !== 'success') {
        Alert.alert('Autenticación cancelada', 'No se pudo completar Google Login.');
      }
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Conecta FCFM</Text>
      <Text style={styles.subtitle}>Inicia con Google usando correo institucional</Text>

      <TextInput
        placeholder="correo@ing.uchile.cl"
        autoCapitalize="none"
        keyboardType="email-address"
        value={emailForValidation}
        onChangeText={setEmailForValidation}
        style={styles.input}
      />

      <Pressable style={styles.button} onPress={loginWithGoogle}>
        <Text style={styles.buttonText}>Continuar con Google</Text>
      </Pressable>

      <Text style={styles.note}>Dominios permitidos: @ug.uchile.cl, @ing.uchile.cl, @uchile.cl, @idiem.cl</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 24, gap: 12 },
  title: { fontSize: 30, fontWeight: '800' },
  subtitle: { fontSize: 14, color: '#475569' },
  input: { width: '100%', borderWidth: 1, borderColor: '#cbd5e1', borderRadius: 10, padding: 12 },
  button: { width: '100%', backgroundColor: '#0f172a', borderRadius: 10, padding: 14, alignItems: 'center' },
  buttonText: { color: '#fff', fontWeight: '700' },
  note: { marginTop: 8, fontSize: 12, color: '#64748b', textAlign: 'center' },
});
