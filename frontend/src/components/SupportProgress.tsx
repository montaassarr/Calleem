export const SupportProgress = () => {
  return (
    <div className="glass-card rounded-2xl p-6 shine">
      <h3 className="text-lg font-semibold mb-6">Support Metrics</h3>

      <div className="relative w-48 h-48 mx-auto mb-6">
        <svg className="w-full h-full -rotate-90">
          <circle
            cx="96"
            cy="96"
            r="88"
            fill="none"
            stroke="currentColor"
            strokeWidth="12"
            className="text-muted"
          />
          <circle
            cx="96"
            cy="96"
            r="88"
            fill="none"
            stroke="url(#gradient)"
            strokeWidth="12"
            strokeLinecap="round"
            strokeDasharray={2 * Math.PI * 88}
            strokeDashoffset={2 * Math.PI * 88 * (1 - 0.87)}
            className="transition-all duration-1000"
          />
          <defs>
            <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="hsl(142 76% 36%)" />
              <stop offset="100%" stopColor="hsl(158 64% 52%)" />
            </linearGradient>
          </defs>
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-4xl font-bold">87%</span>
          <span className="text-sm text-muted-foreground">Resolution Rate</span>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 mb-1">
            <div className="w-3 h-3 rounded-full bg-gradient-to-r from-success to-success/80" />
            <span className="text-xs font-medium">Resolved</span>
          </div>
          <p className="text-sm text-muted-foreground">284</p>
        </div>
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 mb-1">
            <div className="w-3 h-3 rounded-full bg-gradient-to-r from-warning to-warning/80" />
            <span className="text-xs font-medium">Pending</span>
          </div>
          <p className="text-sm text-muted-foreground">42</p>
        </div>
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 mb-1">
            <div className="w-3 h-3 rounded-full bg-gradient-to-r from-muted to-muted/80" />
            <span className="text-xs font-medium">Idle</span>
          </div>
          <p className="text-sm text-muted-foreground">8</p>
        </div>
      </div>
    </div>
  );
};
