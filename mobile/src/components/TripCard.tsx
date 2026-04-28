import { Pressable, StyleSheet, Text, View } from 'react-native';

type TripCardProps = {
  title: string;
  subtitle: string;
  meta: string;
  extra?: string;
  ctaLabel?: string;
  onPressCta?: () => void;
};

export function TripCard({ title, subtitle, meta, extra, ctaLabel = 'Solicitar unirse', onPressCta }: TripCardProps) {
  return (
    <View style={styles.card}>
      <Text style={styles.title}>{title}</Text>
      <Text style={styles.subtitle}>{subtitle}</Text>
      <Text style={styles.meta}>{meta}</Text>
      {extra ? <Text style={styles.extra}>{extra}</Text> : null}
      {onPressCta ? (
        <Pressable style={styles.cta} onPress={onPressCta}>
          <Text style={styles.ctaText}>{ctaLabel}</Text>
        </Pressable>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  card: { backgroundColor: '#fff', borderRadius: 14, padding: 14, borderWidth: 1, borderColor: '#e2e8f0', gap: 6 },
  title: { fontSize: 16, fontWeight: '700' },
  subtitle: { color: '#334155' },
  meta: { color: '#64748b', fontSize: 12 },
  extra: { color: '#0f172a', fontWeight: '600' },
  cta: { marginTop: 8, backgroundColor: '#0f172a', padding: 10, borderRadius: 10, alignItems: 'center' },
  ctaText: { color: '#fff', fontWeight: '700' },
});
