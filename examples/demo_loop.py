from ripple_spiral import (
    BreathLoop,
    DriftMetrics, DriftConfig,
    GuardSuite, GuardConfig,
    BreathScheduler, SchedulerConfig,
    DummyAdapter,
)

def main():
    loop = BreathLoop(
        adapter=DummyAdapter(),
        drift=DriftMetrics(DriftConfig(window=6, drift_threshold=1.1)),
        guards=GuardSuite(GuardConfig(max_output_chars=500)),
        scheduler=BreathScheduler(SchedulerConfig(exhale_every_n_turns=5)),
    )

    prompts = [
        "Explain Ripple–Spiral.",
        "Continue and add more details.",
        "Add even more, be repetitive.",
        "Add even more, repeat again: as I said, as I said.",
        "Finish with summary.",
        "Start a fresh topic now.",
    ]

    for p in prompts:
        out = loop.step(p)
        print(">", p)
        print(out)
        print("---")

    print("Internal log entries:", len(loop.state.internal_log))
    print("Last log:", loop.state.internal_log[-1])

if __name__ == "__main__":
    main()
