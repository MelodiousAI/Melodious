export function ScoreArt() {
  return (
    <div className="relative h-[22rem] w-full">
      <div className="absolute left-0 top-4 w-[52%] rotate-[4deg] rounded-sm border border-stone-200/70 bg-[hsl(38,35%,95%)] p-4 shadow-[0_18px_45px_rgba(120,113,108,0.12)]">
        <svg viewBox="0 0 200 70" className="w-full opacity-55" xmlns="http://www.w3.org/2000/svg">
          {[15, 23, 31, 39, 47].map((y) => (
            <line key={y} x1="10" y1={y} x2="190" y2={y} stroke="currentColor" strokeWidth="0.5" />
          ))}
          <text x="16" y="42" fontSize="18" fill="currentColor">
            C
          </text>
          {[50, 75, 100, 130, 160].map((x, index) => (
            <ellipse
              key={x}
              cx={x}
              cy={31 + (index % 3) * 8 - 4}
              rx="4"
              ry="2.5"
              fill="currentColor"
              transform={`rotate(-8 ${x} ${31 + (index % 3) * 8 - 4})`}
            />
          ))}
        </svg>
      </div>

      <div className="absolute right-0 top-10 w-[84%] rounded-sm border border-stone-200/70 bg-[hsl(35,32%,97%)] p-6 shadow-[0_28px_70px_rgba(120,113,108,0.16)]">
        <svg viewBox="0 0 360 180" className="w-full text-stone-900/55" xmlns="http://www.w3.org/2000/svg">
          {[40, 48, 56, 64, 72].map((y) => (
            <line key={`top-${y}`} x1="20" y1={y} x2="340" y2={y} stroke="currentColor" strokeWidth="0.6" />
          ))}
          <text x="26" y="68" fontSize="24" fill="currentColor">
            C
          </text>
          {[80, 108, 136, 176, 204, 232, 260, 300].map((x, index) => {
            const y = [64, 56, 52, 60, 68, 56, 48, 60][index]
            return (
              <g key={`note-${x}`}>
                <ellipse cx={x} cy={y} rx="4.5" ry="3" fill="currentColor" transform={`rotate(-8 ${x} ${y})`} />
                <line x1={x + 4} y1={y} x2={x + 4} y2={y - 20} stroke="currentColor" strokeWidth="0.8" />
              </g>
            )
          })}
          {[110, 118, 126, 134, 142].map((y) => (
            <line key={`bottom-${y}`} x1="20" y1={y} x2="340" y2={y} stroke="currentColor" strokeWidth="0.6" />
          ))}
          <text x="26" y="136" fontSize="18" fill="currentColor">
            F
          </text>
          {[80, 136, 176, 232, 300].map((x, index) => {
            const y = [134, 126, 130, 122, 130][index]
            return (
              <g key={`bass-${x}`}>
                <ellipse cx={x} cy={y} rx="4.5" ry="3" fill="currentColor" transform={`rotate(-8 ${x} ${y})`} />
                <line x1={x + 4} y1={y} x2={x + 4} y2={y - 18} stroke="currentColor" strokeWidth="0.8" />
              </g>
            )
          })}
        </svg>
      </div>

      <div className="absolute right-[4%] top-[14%] h-20 w-20 rounded-full bg-amber-300/20 blur-2xl" />
    </div>
  )
}
