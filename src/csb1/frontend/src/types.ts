export type ConnectionState = {
  status: "disconnected" | "connecting" | "connected" | "error";
  port: string | null;
  error: string | null;
  changedAt: string;
};

export type RailroadState = {
  profile: string;
  connection: ConnectionState;
  trackPower: "on" | "off";
  emergencyStop: boolean;
  commandStation: { identity?: string } | null;
  locomotives: Record<string, LocomotiveState>;
};

export type LocomotiveState = {
  address: number;
  speed?: number;
  direction?: "forward" | "reverse";
  functions?: Record<string, boolean>;
};
