import { OctagonAlert, RefreshCw } from "lucide-react";

import { Button } from "@/components/ui/button";

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-xl border border-line bg-ink-900 px-6 py-16 text-center">
      <OctagonAlert className="h-6 w-6 text-crit" />
      <div>
        <p className="text-sm font-medium text-zinc-200">Could not reach the monitoring API</p>
        <p className="mt-1 max-w-md text-xs text-muted">{message}</p>
      </div>
      {onRetry && (
        <Button variant="outline" onClick={onRetry}>
          <RefreshCw className="h-3.5 w-3.5" /> Retry
        </Button>
      )}
    </div>
  );
}
