import { api } from "./client";

export interface GroupCreatePayload {
  name: string;
  organizer_email: string;
  budget?: number;
  reveal_date?: string;
  allow_household?: boolean;
}

export interface GroupCreateResponse {
  group_id: string;
  join_url: string;
  join_pin: string;
  join_token: string;
}

export async function createGroup(payload: GroupCreatePayload) {
  const { data } = await api.post<GroupCreateResponse>("/groups", payload);
  return data;
}

export interface JoinGroupPayload {
  name: string;
  email: string;
  household?: string;
  interests?: string[];
  nogos?: string[];
  pin: string;
  token: string;
}

export async function joinGroup(groupId: string, payload: JoinGroupPayload) {
  await api.post(`/groups/${groupId}/join`, payload);
}

export async function issueToken(groupId: string) {
  const { data } = await api.post<{ access_token: string; token_type: string }>(
    `/groups/${groupId}/token`
  );
  return data;
}
