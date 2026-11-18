type Tone = 'accent' | 'warn' | 'ink' | 'rest';
type Segment = { value: number; tone: Tone; label: string };
export type BarRow = { label: string; segments: Segment[] };

const LABEL_WIDTH = 168;
const BAR_WIDTH = 440;
const ROW_HEIGHT = 40;
const BAR_HEIGHT = 28;

export function BarRows({
  id,
  title,
  description,
  rows,
  legend,
}: {
  id: string;
  title: string;
  description: string;
  rows: BarRow[];
  legend: { tone: Tone; label: string }[];
}) {
  const width = LABEL_WIDTH + BAR_WIDTH + 8;
  const height = rows.length * ROW_HEIGHT;
  return (
    <figure className="bar-figure">
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-labelledby={`${id}-title ${id}-desc`}>
        <title id={`${id}-title`}>{title}</title>
        <desc id={`${id}-desc`}>{description}</desc>
        {rows.map((row, index) => {
          const total = row.segments.reduce((sum, segment) => sum + segment.value, 0);
          let x = LABEL_WIDTH;
          const y = index * ROW_HEIGHT + (ROW_HEIGHT - BAR_HEIGHT) / 2;
          return (
            <g key={row.label}>
              <text className="bar-row-label" x={0} y={y + BAR_HEIGHT / 2 + 5}>
                {row.label}
              </text>
              {row.segments.map((segment) => {
                if (segment.value === 0) return null;
                const segmentWidth = (segment.value / total) * BAR_WIDTH;
                const start = x;
                x += segmentWidth;
                return (
                  <g key={segment.label}>
                    <rect
                      className={`bar-${segment.tone}`}
                      x={start}
                      y={y}
                      width={segmentWidth}
                      height={BAR_HEIGHT}
                    />
                    <text
                      className={`bar-value bar-value-${segment.tone}`}
                      x={start + segmentWidth / 2}
                      y={y + BAR_HEIGHT / 2 + 5}
                      textAnchor="middle"
                    >
                      {segment.value}
                    </text>
                  </g>
                );
              })}
            </g>
          );
        })}
      </svg>
      <figcaption>
        <ul className="bar-legend">
          {legend.map((item) => (
            <li key={item.label}>
              <span className={`bar-swatch bar-${item.tone}`} aria-hidden="true" />
              {item.label}
            </li>
          ))}
        </ul>
      </figcaption>
    </figure>
  );
}
