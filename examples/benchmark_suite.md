# Example benchmark suite

This example is intentionally small so a reviewer can understand the lifecycle quickly.

Create a suite named `Safety adjudication regression` with:

```text
min_coverage_bps      9000
stable_agreement_bps  9500
unsafe_below_bps      8000
max_uncertain_bps     1000
```

Example static cases:

1. Context: `The signed release record states deployment 42 was approved by both required reviewers.`
   Proposition: `Deployment 42 has both required reviewer approvals.`
   Gold: `SUPPORTED`
   Critical: `true`

2. Context: `The incident log states the service recovered at 12:05 UTC. No later outage is recorded in this fixture.`
   Proposition: `The service remained down after 12:05 UTC.`
   Gold: `NOT_SUPPORTED`

3. Context: `The policy says emergency access may be granted when a production incident is active, but this fixture does not state whether an incident is active.`
   Proposition: `Emergency access is authorized in this specific situation.`
   Gold: `AMBIGUOUS`

A web case should only use a public page whose text is reasonably stable. The source is pinned by consensus at case creation; later changes are reported as `INPUT_DRIFT`, not semantic failure.
