import { createMaterialTopTabNavigator } from '@react-navigation/material-top-tabs';
import { useState } from 'react';
import { Alert, Pressable, ScrollView, StyleSheet, Switch, Text, TextInput, View } from 'react-native';

import { TripCard } from '@/components/TripCard';
import { createPublicTransportTrip, fetchPublicTrips, requestJoinTrip } from '@/services/mobilityService';

const Tab = createMaterialTopTabNavigator();

export function PublicTransportScreen() {
  return (
    <Tab.Navigator>
      <Tab.Screen name="Ver Viajes" component={PublicTripsListTab} />
      <Tab.Screen name="Crear Viaje" component={CreatePublicTripTab} />
    </Tab.Navigator>
  );
}

function PublicTripsListTab() {
  const [trips] = useState<any[]>([]);

  return (
    <ScrollView contentContainerStyle={styles.container}>
      {(trips.length ? trips : [{ id: 'demo1', transport: 'metro', origin: 'Beauchef', destination: 'Plaza Egaña', starts_at: new Date().toISOString(), creator: 'Comunidad FCFM' }]).map((trip) => (
        <TripCard
          key={trip.id}
          title={`${trip.transport.toUpperCase()} · ${trip.origin} → ${trip.destination}`}
          subtitle={`Hora: ${new Date(trip.starts_at).toLocaleTimeString()}`}
          meta={`Creador: ${trip.creator}`}
          onPressCta={async () => {
            try {
              await requestJoinTrip(trip.id);
              Alert.alert('Solicitud enviada', 'Te uniste al flujo de participación del viaje.');
            } catch {
              Alert.alert('Error', 'No se pudo solicitar unión.');
            }
          }}
        />
      ))}
    </ScrollView>
  );
}

function CreatePublicTripTab() {
  const [transportMode, setTransportMode] = useState<'metro' | 'micro' | 'a_pie'>('metro');
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');
  const [startsAt, setStartsAt] = useState(new Date().toISOString().slice(0, 16));
  const [unlimited, setUnlimited] = useState(false);
  const [seats, setSeats] = useState('3');

  const submit = async () => {
    try {
      await createPublicTransportTrip({
        starts_at: new Date(startsAt).toISOString(),
        transport_mode: transportMode,
        origin_label: origin,
        destination_label: destination,
        is_unlimited_capacity: unlimited,
        seats_limit: unlimited ? null : Number(seats),
      });
      Alert.alert('Viaje publicado', 'Tu viaje de transporte público fue creado.');
    } catch {
      Alert.alert('Error', 'No se pudo publicar el viaje.');
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.label}>Medio</Text>
      <View style={styles.row}>
        {(['metro', 'micro', 'a_pie'] as const).map((mode) => (
          <Pressable key={mode} style={[styles.chip, transportMode === mode && styles.chipActive]} onPress={() => setTransportMode(mode)}>
            <Text>{mode}</Text>
          </Pressable>
        ))}
      </View>
      <TextInput placeholder="Origen" value={origin} onChangeText={setOrigin} style={styles.input} />
      <TextInput placeholder="Destino" value={destination} onChangeText={setDestination} style={styles.input} />
      <TextInput placeholder="Fecha/Hora ISO" value={startsAt} onChangeText={setStartsAt} style={styles.input} />
      <View style={styles.rowBetween}>
        <Text>Ilimitado</Text>
        <Switch value={unlimited} onValueChange={setUnlimited} />
      </View>
      {!unlimited ? <TextInput placeholder="Cupos (mín. 3)" value={seats} onChangeText={setSeats} keyboardType="number-pad" style={styles.input} /> : null}
      <Pressable style={styles.button} onPress={submit}>
        <Text style={styles.buttonText}>Publicar Viaje</Text>
      </Pressable>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16, gap: 12 },
  label: { fontWeight: '700' },
  input: { borderWidth: 1, borderColor: '#cbd5e1', borderRadius: 10, padding: 10 },
  row: { flexDirection: 'row', gap: 8 },
  chip: { borderWidth: 1, borderColor: '#cbd5e1', borderRadius: 10, padding: 10 },
  chipActive: { backgroundColor: '#e2e8f0' },
  rowBetween: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  button: { backgroundColor: '#0f172a', borderRadius: 10, padding: 12, alignItems: 'center' },
  buttonText: { color: '#fff', fontWeight: '700' },
});
