export default function Loading() {
  return (
    <div className="content" role="status" aria-live="polite">
      <div className="skeleton" aria-hidden="true">
        <span />
        <span />
        <span />
      </div>
      <span className="sr-only">Loading</span>
    </div>
  );
}
