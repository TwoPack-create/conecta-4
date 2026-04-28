import { createMaterialTopTabNavigator } from '@react-navigation/material-top-tabs';
import { useMemo, useState } from 'react';
import { Alert, ScrollView, StyleSheet, Text, TextInput, View, Pressable } from 'react-native';
import MapView, { Marker, Polyline } from 'react-native-maps';

import { TripCard } from '@/components/TripCard';
import { createVehicleTrip, requestJoinTrip } from '@/services/mobilityService';

const Tab = createMaterialTopTabNavigator();

export function VehicleScreen() {
  return (
    <Tab.Navigator>
      <Tab.Screen name="Ver Viajes" component={VehicleTripsListTab} />
      <Tab.Screen name="Publicar Viaje" component={CreateVehicleTripTab} />
    </Tab.Navigator>
  );
}

function VehicleTripsListTab() {
  const demo = [{ id: 'veh1', driver: 'María', rating: 4.8, seats_available: 2, cost_total: 3200, origin: 'Beauchef', destination: 'Providencia', starts_at: new Date().toISOString() }];
  return (
    <ScrollView contentContainerStyle={styles.container}>
      {demo.map((trip) => (
        <TripCard
          key={trip.id}
          title={`🚗 ${trip.origin} → ${trip.destination}`}
          subtitle={`Hora: ${new Date(trip.starts_at).toLocaleTimeString()} · Asientos: ${trip.seats_available}`}
          meta={`Conductor: ${trip.driver} · ⭐ ${trip.rating}`}
          extra={`Total pasajero: CLP ${trip.cost_total}`}
          onPressCta={async () => {
            try {
              await requestJoinTrip(trip.id);
              Alert.alert('Solicitud enviada', 'Se envió tu solicitud al conductor.');
            } catch {
              Alert.alert('Error', 'No se pudo solicitar viaje.');
            }
          }}
        />
      ))}
    </ScrollView>
  );
}

function CreateVehicleTripTab() {
  const [origin, setOrigin] = useState('Beauchef 850, Santiago');
  const [destination, setDestination] = useState('Providencia, Santiago');
  const [startsAt, setStartsAt] = useState(new Date().toISOString().slice(0, 16));
  const [seats, setSeats] = useState('3');
  const [distanceKm, setDistanceKm] = useState('8');

  const originCoord = { latitude: -33.457, longitude: -70.664 };
  const destinationCoord = { latitude: -33.426, longitude: -70.617 };

  const region = useMemo(
    () => ({
      latitude: (originCoord.latitude + destinationCoord.latitude) / 2,
      longitude: (originCoord.longitude + destinationCoord.longitude) / 2,
      latitudeDelta: 0.08,
      longitudeDelta: 0.08,
    }),
    []
  );

  const submit = async () => {
    try {
      await createVehicleTrip({
        starts_at: new Date(startsAt).toISOString(),
        origin_label: origin,
        destination_label: destination,
        seats_total: Number(seats),
        distance_km: Number(distanceKm),
      });
      Alert.alert('Viaje publicado', 'Tu viaje de vehículo fue creado con costeo automático.');
    } catch {
      Alert.alert('Error', 'No se pudo publicar el viaje.');
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <TextInput value={origin} onChangeText={setOrigin} placeholder="Origen" style={styles.input} />
      <TextInput value={destination} onChangeText={setDestination} placeholder="Destino" style={styles.input} />
      <TextInput value={startsAt} onChangeText={setStartsAt} placeholder="Fecha/Hora" style={styles.input} />
      <TextInput value={seats} onChangeText={setSeats} placeholder="Asientos" keyboardType="number-pad" style={styles.input} />
      <TextInput value={distanceKm} onChangeText={setDistanceKm} placeholder="Distancia km" keyboardType="numeric" style={styles.input} />

      <View style={styles.mapWrap}>
        <MapView style={styles.map} region={region}>
          <Marker coordinate={originCoord} title="Origen" />
          <Marker coordinate={destinationCoord} title="Destino" />
          <Polyline coordinates={[originCoord, destinationCoord]} strokeWidth={4} strokeColor="#2563eb" />
        </MapView>
      </View>

      <Pressable style={styles.button} onPress={submit}>
        <Text style={styles.buttonText}>Publicar Viaje</Text>
      </Pressable>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16, gap: 12 },
  input: { borderWidth: 1, borderColor: '#cbd5e1', borderRadius: 10, padding: 10 },
  mapWrap: { borderRadius: 12, overflow: 'hidden', borderWidth: 1, borderColor: '#cbd5e1' },
  map: { width: '100%', height: 250 },
  button: { backgroundColor: '#0f172a', borderRadius: 10, padding: 12, alignItems: 'center' },
  buttonText: { color: '#fff', fontWeight: '700' },
});
