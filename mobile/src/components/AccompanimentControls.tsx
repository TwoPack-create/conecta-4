import { useEffect, useMemo, useState } from 'react';
import { Alert, Modal, Pressable, StyleSheet, Text, View } from 'react-native';

import { apiClient } from '@/services/apiClient';
import { useSafetyStore } from '@/store/safetyStore';

type Props = { compact?: boolean };

export function AccompanimentControls({ compact = false }: Props) {
  const [visible, setVisible] = useState(false);
  const [minutes, setMinutes] = useState(30);
  const session = useSafetyStore((s) => s.accompanimentSession);
  const setSession = useSafetyStore((s) => s.setAccompanimentSession);
  const setDrift = useSafetyStore((s) => s.setServerClientDriftMs);
  const driftMs = useSafetyStore((s) => s.serverClientDriftMs);

  const remainingSeconds = useCountdown(session?.expected_arrival_at ?? null, driftMs);

  const start = async () => {
    try {
      const response = await apiClient.post<{ id: string; status: string; expected_arrival_at: string; server_now?: string; created_at?: string }>('/api/v1/safety/accompaniment/start', {
        estimated_minutes: minutes,
      });
      setSession(response);
      setDrift(response.server_now ?? response.created_at ?? new Date().toISOString());
      setVisible(false);
    } catch {
      Alert.alert('Acompáñame', 'No se pudo iniciar la sesión.');
    }
  };

  const markSafe = async () => {
    if (!session) return;
    try {
      await apiClient.post(`/api/v1/safety/accompaniment/${session.id}/safe`);
      setSession(null);
    } catch {
      Alert.alert('Acompáñame', 'No se pudo confirmar llegada segura.');
    }
  };

  if (compact) {
    return (
      <>
        <Pressable style={[styles.shield, session && styles.shieldActive]} onPress={() => setVisible(true)}>
          <Text style={styles.shieldText}>🛡️</Text>
        </Pressable>
        <Modal transparent visible={visible} animationType="slide" onRequestClose={() => setVisible(false)}>
          <View style={styles.modalOverlay}>
            <View style={styles.modalContent}>
              <Text style={styles.modalTitle}>Modo Acompáñame</Text>
              <Text style={styles.modalSubtitle}>Tiempo estimado: {minutes} min</Text>
              <View style={styles.row}>
                {[15, 30, 45, 60].map((m) => (
                  <Pressable key={m} onPress={() => setMinutes(m)} style={[styles.chip, minutes === m && styles.chipActive]}>
                    <Text style={styles.chipText}>{m}</Text>
                  </Pressable>
                ))}
              </View>
              <Pressable style={styles.primary} onPress={start}>
                <Text style={styles.primaryText}>Activar Protección</Text>
              </Pressable>
            </View>
          </View>
        </Modal>
      </>
    );
  }

  if (!session) return null;
  const mm = Math.floor(remainingSeconds / 60);
  const ss = remainingSeconds % 60;
  return (
    <View style={styles.floatingBar}>
      <Text style={styles.floatingText}>Acompáñame activo · {`${mm}:${String(ss).padStart(2, '0')}`}</Text>
      <Pressable style={styles.safeButton} onPress={markSafe}>
        <Text style={styles.safeText}>Llegué a salvo</Text>
      </Pressable>
    </View>
  );
}

function useCountdown(expectedArrivalIso: string | null, driftMs: number): number {
  const target = useMemo(() => (expectedArrivalIso ? new Date(expectedArrivalIso).getTime() : null), [expectedArrivalIso]);
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    if (!target) return;
    const tick = () => setSeconds(Math.max(0, Math.floor((target - (Date.now() + driftMs)) / 1000)));
    tick();
    const timer = setInterval(tick, 1000);
    return () => clearInterval(timer);
  }, [target, driftMs]);

  return seconds;
}

const styles = StyleSheet.create({
  shield: { backgroundColor: '#1e293b', borderRadius: 8, paddingHorizontal: 12, paddingVertical: 8 },
  shieldActive: { backgroundColor: '#16a34a' },
  shieldText: { color: '#fff' },
  modalOverlay: { flex: 1, justifyContent: 'flex-end', backgroundColor: 'rgba(0,0,0,0.2)' },
  modalContent: { backgroundColor: '#fff', borderTopLeftRadius: 18, borderTopRightRadius: 18, padding: 20, gap: 12 },
  modalTitle: { fontSize: 20, fontWeight: '700' },
  modalSubtitle: { color: '#475569' },
  row: { flexDirection: 'row', gap: 8 },
  chip: { paddingHorizontal: 14, paddingVertical: 8, borderRadius: 10, borderWidth: 1, borderColor: '#cbd5e1' },
  chipActive: { backgroundColor: '#0f172a' },
  chipText: { color: '#111827' },
  primary: { backgroundColor: '#0f172a', borderRadius: 10, padding: 12, alignItems: 'center' },
  primaryText: { color: '#fff', fontWeight: '700' },
  floatingBar: {
    position: 'absolute',
    left: 12,
    right: 12,
    bottom: 14,
    backgroundColor: '#0f172a',
    borderRadius: 12,
    padding: 12,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  floatingText: { color: '#fff', fontWeight: '600' },
  safeButton: { backgroundColor: '#16a34a', borderRadius: 8, paddingHorizontal: 12, paddingVertical: 8 },
  safeText: { color: '#fff', fontWeight: '700' },
});
