"use client";

import { useEffect, useRef } from "react";
import { api, type NotificationListResponse } from "@/lib/api";

export const NOTIFICATION_POLL_INTERVAL_MS = 5 * 60 * 1000;

export function useNotificationPolling(
  token: string | null,
  onUpdate: (data: NotificationListResponse) => void,
  options?: { enabled?: boolean; limit?: number }
) {
  const onUpdateRef = useRef(onUpdate);
  onUpdateRef.current = onUpdate;
  const enabled = options?.enabled ?? true;
  const limit = options?.limit ?? 50;

  useEffect(() => {
    if (!token || !enabled) return;

    let cancelled = false;

    const poll = async () => {
      try {
        const data = await api.getNotifications(token, { limit });
        if (!cancelled) onUpdateRef.current(data);
      } catch {
        /* keep last known state */
      }
    };

    poll();
    const intervalId = window.setInterval(poll, NOTIFICATION_POLL_INTERVAL_MS);
    return () => {
      cancelled = true;
      window.clearInterval(intervalId);
    };
  }, [token, enabled, limit]);
}
