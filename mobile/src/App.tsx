import { ActivityIndicator, View } from 'react-native';

import { AccompanimentControls } from '@/components/AccompanimentControls';
import { useAuthBootstrap } from '@/hooks/useAuthBootstrap';
import { AppNavigator } from '@/navigation/AppNavigator';
import { LoginScreen } from '@/screens/LoginScreen';
import { useAuthStore } from '@/store/authStore';

export default function App() {
  useAuthBootstrap();
  const { loading, session } = useAuthStore((s) => ({ loading: s.loading, session: s.session }));

  if (loading) {
    return (
      <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
        <ActivityIndicator />
      </View>
    );
  }

  if (!session) return <LoginScreen />;

  return (
    <View style={{ flex: 1 }}>
      <AppNavigator />
      <AccompanimentControls />
    </View>
  );
}
