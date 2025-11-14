import { TrendingUp } from "lucide-react";

const data = [
  { day: "Mon", calls: 45, height: "h-16" },
  { day: "Tue", calls: 78, height: "h-28" },
  { day: "Wed", calls: 62, height: "h-20" },
  { day: "Thu", calls: 95, height: "h-36" },
  { day: "Fri", calls: 58, height: "h-20" },
  { day: "Sat", calls: 42, height: "h-14" },
  { day: "Sun", calls: 38, height: "h-12" },
];

export const CallAnalytics = () => {
  return (
    <div className="glass-card rounded-2xl p-6 shine">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold">Call Analytics</h3>
        <div className="flex items-center gap-2 text-sm text-success">
          <TrendingUp className="w-4 h-4" />
          <span>+12.5%</span>
        </div>
      </div>

      <div className="flex items-end justify-between gap-4 h-48">
        {data.map((item, index) => (
          <div key={item.day} className="flex-1 flex flex-col items-center gap-2">
            <div className="w-full flex-1 flex items-end">
              <div
                className={cn(
                  "w-full rounded-t-lg bg-gradient-to-t from-primary to-accent transition-all hover:opacity-80",
                  item.height
                )}
                style={{
                  animation: `fade-in 0.5s ease-out ${index * 0.1}s both`,
                }}
              />
            </div>
            <span className="text-xs text-muted-foreground">{item.day}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

const cn = (...classes: string[]) => classes.filter(Boolean).join(" ");
