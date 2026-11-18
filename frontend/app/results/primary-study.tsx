// Recorded results from research/multiprotein_study_findings.md and its evaluation report.
const results = [
  { protein: 'IRED', higher: 0, tied: 9, lower: 1, measurements: 50 },
  { protein: 'Hydro P06241', higher: 0, tied: 7, lower: 3, measurements: 55 },
  { protein: 'Hydro P01053', higher: 0, tied: 10, lower: 0, measurements: 40 },
  { protein: 'Hydro P0A9X9', higher: 0, tied: 9, lower: 1, measurements: 45 },
];

export function PrimaryStudy() {
  return <div className="workflow-layout primary-study">
    <section className="results-section" aria-labelledby="primary-study-heading">
      <span className="section-index">PRIMARY STUDY</span>
      <h2 id="primary-study-heading">Neither repair policy improved the best score</h2>
      <p>The study ran nine methods on four protein groups, with ten matched starts per group. Each repair policy produced 35 ties and five lower scores across 40 starts compared with keeping the scoring rule fixed.</p>
      <div className="results-table-wrap" role="region" aria-labelledby="primary-study-table" tabIndex={0}>
        <table className="results-table">
          <caption id="primary-study-table">Best score at each policy’s stopping point. Both repair policies had the same counts.</caption>
          <thead><tr><th scope="col">Protein group</th><th scope="col">Higher</th><th scope="col">Tied</th><th scope="col">Lower</th><th scope="col">Median new measurements per repair policy</th></tr></thead>
          <tbody>{results.map(row => <tr key={row.protein}>
            <th scope="row">{row.protein}</th><td>{row.higher}</td><td>{row.tied}</td><td>{row.lower}</td><td>{row.measurements}</td>
          </tr>)}</tbody>
        </table>
      </div>
    </section>
    <aside className="method-note" aria-label="Interpreting the primary study">
      <h2>Repair often stopped earlier</h2>
      <p>The fixed scoring rule used all 100 new measurements in every run. Both repair policies often stopped after proposed changes failed the checks. The comparison reflects both the scoring rules and the number of measurements each policy used.</p>
    </aside>
  </div>;
}
