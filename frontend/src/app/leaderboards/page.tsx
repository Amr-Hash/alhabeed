import { Suspense } from "react";
import LeaderboardsContent from "./LeaderboardsContent";

export default function LeaderboardsPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <LeaderboardsContent />
    </Suspense>
  );
}
