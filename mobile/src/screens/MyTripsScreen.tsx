import { createMaterialTopTabNavigator } from '@react-navigation/material-top-tabs';
import { useEffect, useState } from 'react';
import { ScrollView, StyleSheet } from 'react-native';

import { TripCard } from '@/components/TripCard';
import { fetchMyTrips } from '@/services/mobilityService';

const Tab = createMaterialTopTabNavigator();

export function MyTripsScreen() {
  return (
    <Tab.Navigator>
      <Tab.Screen name="Activos" component={ActiveTripsTab} />
      <Tab.Screen name="Histórico" component={HistoryTripsTab} />
    </Tab.Navigator>
  );
}

function ActiveTripsTab() {
  const [trips, setTrips] = useState<any[]>([]);
  useEffect(() => {
    fetchMyTrips().then(setTrips).catch(() => setTrips([]));
  }, []);

  return (
    <ScrollView contentContainerStyle={styles.container}>
      {(trips.length ? trips : [{ id: 'active-demo', title: 'Viaje activo demo', subtitle: 'Participación sincronizada con backend', meta: 'Estado: En curso' }]).map((trip) => (
        <TripCard key={trip.id} title={trip.title} subtitle={trip.subtitle} meta={trip.meta} />
      ))}
    </ScrollView>
  );
}

function HistoryTripsTab() {
  return (
    <ScrollView contentContainerStyle={styles.container}>
      <TripCard title="Histórico demo" subtitle="Viajes finalizados" meta="Próximamente con endpoint de histórico" />
    </ScrollView>
  );
}

const styles = StyleSheet.create({ container: { padding: 16, gap: 12 } });
