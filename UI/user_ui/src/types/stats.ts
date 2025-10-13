export type Stat = { value_daily: number | string; value_weekly?: number | string; diff?: number, label?: string };

export type Metrics = {
  activeUsers: Stat | null;
  newSignups: Stat | null;
  reportsGenerated: Stat | null;
};