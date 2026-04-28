import { View, Text, StyleSheet } from 'react-native';

import { AccompanimentControls } from '@/components/AccompanimentControls';
import { SosSliderButton } from '@/components/SosSliderButton';

export function AppHeader() {
  return (
    <View style={styles.container}>
      <Text style={styles.brand}>Conecta FCFM</Text>
      <View style={styles.actions}>
        <AccompanimentControls compact />
        <SosSliderButton />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    height: 64,
    paddingHorizontal: 12,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#0f172a',
  },
  brand: { color: '#fff', fontSize: 18, fontWeight: '700' },
  actions: { flexDirection: 'row', alignItems: 'center', gap: 8 },
});
