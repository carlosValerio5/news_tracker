export interface RegisterAdminResponse {
  detail: string;
}

export interface AdminConfigResponse {
  detail?: string;
  target_email?: string;
  summary_send_time?: string;
  last_updated?: string;
}

export interface AdminConfig {
  target_email: string;
  summary_send_time: string;
  last_updated: Date;
}
