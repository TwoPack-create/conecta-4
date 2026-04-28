import { NavigationContainer } from '@react-navigation/native';
import { createDrawerNavigator } from '@react-navigation/drawer';

import { AppHeader } from '@/components/AppHeader';
import { HomeScreen } from '@/screens/HomeScreen';
import { MyTripsScreen } from '@/screens/MyTripsScreen';
import { PlaceholderScreen } from '@/screens/PlaceholderScreen';
import { PublicTransportScreen } from '@/screens/PublicTransportScreen';
import { VehicleScreen } from '@/screens/VehicleScreen';

const Drawer = createDrawerNavigator();

export function AppNavigator() {
  return (
    <NavigationContainer>
      <Drawer.Navigator
        screenOptions={{
          header: () => <AppHeader />,
          drawerType: 'front',
        }}
      >
        <Drawer.Screen name="Inicio" component={HomeScreen} />
        <Drawer.Screen name="Transporte Público" component={PublicTransportScreen} />
        <Drawer.Screen name="Vehículo" component={VehicleScreen} />
        <Drawer.Screen name="Mis Viajes" component={MyTripsScreen} />
        <Drawer.Screen name="Rutas">{() => <PlaceholderScreen title="Rutas" />}</Drawer.Screen>
        <Drawer.Screen name="Perfil">{() => <PlaceholderScreen title="Perfil" />}</Drawer.Screen>
        <Drawer.Screen name="Configuración">{() => <PlaceholderScreen title="Configuración" />}</Drawer.Screen>
      </Drawer.Navigator>
    </NavigationContainer>
  );
}
