"use client";

import { useEffect } from "react";
import { useAuth } from "@/lib/auth";
import { dismissPushPrompt, pushSupported, subscribeToPush } from "@/lib/push";

export function PushNotificationRegistrar() {
  const { token } = useAuth();

  useEffect(() => {
    if (!token || !pushSupported()) return;
    if (Notification.permission === "granted") {
      subscribeToPush(token).catch(() => undefined);
      return;
    }
    if (Notification.permission === "default") {
      subscribeToPush(token)
        .then((ok) => {
          if (!ok) dismissPushPrompt();
        })
        .catch(() => dismissPushPrompt());
    }
  }, [token]);

  return null;
}
