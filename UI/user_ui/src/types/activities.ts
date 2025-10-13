export type Activity = {
  id: number;
  activity_type: string;
  description: string;
  occurred_at?: Date;
  entity_id?: number;
  entity_type?: string;
};

export interface RecentActivitiesResponse {
  total: number;
  activities: Activity[];
  limit: number;
  offset: number;
}
