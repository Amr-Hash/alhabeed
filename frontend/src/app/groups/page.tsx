import { Suspense } from "react";
import GroupsContent from "./GroupsContent";

export default function GroupsPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <GroupsContent />
    </Suspense>
  );
}
