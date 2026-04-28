import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import { useAuthStore } from '@/store/authStore';

export function HomeScreen() {
  const user = useAuthStore((s) => s.user);
  const displayName = user?.user_metadata?.full_name ?? user?.email ?? 'Comunidad FCFM';

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.welcome}>Bienvenido, {displayName}</Text>

      <View style={styles.quickRow}>
        <QuickAction title="Transporte Público" icon="🚇" />
        <QuickAction title="Vehículos" icon="🚗" />
        <QuickAction title="Rutas" icon="🧭" />
      </View>

      <View style={styles.feedCard}>
        <Text style={styles.feedTitle}>Actividad Reciente</Text>
        <Text style={styles.feedPlaceholder}>Próximamente: feed comunitario en tiempo real.</Text>
      </View>
    </ScrollView>
  );
}

function QuickAction({ title, icon }: { title: string; icon: string }) {
  return (
    <Pressable style={styles.quickAction}>
      <Text style={styles.quickIcon}>{icon}</Text>
      <Text style={styles.quickText}>{title}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  container: { padding: 20, gap: 20 },
  welcome: { fontSize: 24, fontWeight: '700' },
  quickRow: { flexDirection: 'row', gap: 10 },
  quickAction: {
    flex: 1,
    backgroundColor: '#e2e8f0',
    borderRadius: 14,
    padding: 14,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 100,
  },
  quickIcon: { fontSize: 24, marginBottom: 6 },
  quickText: { fontWeight: '600', textAlign: 'center' },
  feedCard: { backgroundColor: '#f8fafc', borderRadius: 14, padding: 16, borderWidth: 1, borderColor: '#e2e8f0' },
  feedTitle: { fontSize: 18, fontWeight: '700', marginBottom: 8 },
  feedPlaceholder: { color: '#64748b' },
});
