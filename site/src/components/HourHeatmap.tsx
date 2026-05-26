import React from "react";

export default function HourHeatmap({ grid }: { grid: number[][] }) {
  const max = Math.max(...grid.flat());
  const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  return (
    <div className="font-mono text-[10px]">
      <div className="grid grid-cols-[40px_repeat(24,1fr)] gap-[2px]">
        <div></div>
        {Array.from({ length: 24 }, (_, h) => (
          <div key={h} className="text-center opacity-50">{h}</div>
        ))}
        {grid.map((row, di) => (
          <React.Fragment key={di}>
            <div className="opacity-60">{days[di]}</div>
            {row.map((v, hi) => {
              const a = max ? v / max : 0;
              return <div key={hi} title={`${days[di]} ${hi}:00 — ${v} msgs`}
                style={{ background: `rgba(212,175,106,${a})`, height: 14 }} />;
            })}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}
