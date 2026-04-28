import * as Linking from 'expo-linking';
import { useRef, useState } from 'react';
import { Alert, Animated, PanResponder, StyleSheet, Text, View } from 'react-native';

import { apiClient } from '@/services/apiClient';

const TRACK_WIDTH = 130;
const KNOB_SIZE = 34;
const MAX_X = TRACK_WIDTH - KNOB_SIZE - 4;

export function SosSliderButton() {
  const pan = useRef(new Animated.ValueXY({ x: 0, y: 0 })).current;
  const [loading, setLoading] = useState(false);

  const triggerSos = async () => {
    try {
      setLoading(true);
      await Promise.all([
        Linking.openURL('tel:133'),
        apiClient.post('/api/v1/safety/sos/trigger', {
          location_label: 'Ubicación actual del usuario',
          lat: -33.45,
          lng: -70.66,
          description: 'SOS activado manualmente desde app',
        }),
      ]);
    } catch (error) {
      Alert.alert('SOS', 'No se pudo completar la activación SOS.');
    } finally {
      setLoading(false);
      Animated.spring(pan.x, { toValue: 0, useNativeDriver: false }).start();
    }
  };

  const panResponder = useRef(
    PanResponder.create({
      onMoveShouldSetPanResponder: () => true,
      onPanResponderMove: (_, gesture) => {
        const next = Math.max(0, Math.min(MAX_X, gesture.dx));
        pan.x.setValue(next);
      },
      onPanResponderRelease: (_, gesture) => {
        if (gesture.dx > MAX_X * 0.9 && !loading) {
          triggerSos();
        } else {
          Animated.spring(pan.x, { toValue: 0, useNativeDriver: false }).start();
        }
      },
    })
  ).current;

  return (
    <View style={styles.track}>
      <Text style={styles.label}>{loading ? 'Enviando...' : 'Desliza SOS'}</Text>
      <Animated.View style={[styles.knob, { transform: [{ translateX: pan.x }] }]} {...panResponder.panHandlers}>
        <Text style={styles.knobText}>›</Text>
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  track: {
    width: TRACK_WIDTH,
    height: 38,
    borderRadius: 12,
    backgroundColor: '#b91c1c',
    justifyContent: 'center',
    overflow: 'hidden',
    paddingLeft: 8,
  },
  label: { color: '#fff', fontSize: 11, fontWeight: '700', marginLeft: 36 },
  knob: {
    position: 'absolute',
    left: 2,
    width: KNOB_SIZE,
    height: KNOB_SIZE,
    borderRadius: 10,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
  knobText: { color: '#b91c1c', fontSize: 20, fontWeight: '700' },
});
