import { apiClient } from '@/services/apiClient';

export async function createPublicTransportTrip(payload: {
  starts_at: string;
  transport_mode: 'metro' | 'micro' | 'a_pie';
  origin_label: string;
  destination_label: string;
  is_unlimited_capacity: boolean;
  seats_limit: number | null;
  line_or_route?: string;
  direction?: string;
}) {
  return apiClient.post('/api/v1/trips/public-transport', payload);
}

export async function createVehicleTrip(payload: {
  starts_at: string;
  origin_label: string;
  destination_label: string;
  distance_km: number;
  seats_total: number;
  acepta_encargos?: boolean;
}) {
  return apiClient.post('/api/v1/trips/vehicle', payload);
}

export async function requestJoinTrip(tripId: string) {
  return apiClient.post('/api/v1/participation/join', { trip_id: tripId });
}

// TODO: replace when backend listing endpoints are available.
export async function fetchPublicTrips() {
  return [] as any[];
}

export async function fetchVehicleTrips() {
  return [] as any[];
}

export async function fetchMyTrips() {
  return [] as any[];
}
