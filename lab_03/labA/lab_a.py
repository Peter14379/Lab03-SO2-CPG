import math
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# -----------------------------
# Lab A conditions
# -----------------------------
conditions = [
    ("A0", 1.1, 0.2),   # baseline
    ("A1", 1.1, 0.4),   # change phi only
    ("A2", 1.3, 0.2),   # change alpha only
]

# อย่างน้อย 3 initial conditions
initial_states = [
    (0.1, 0.0),
    (0.0, 0.1),
    (0.1, 0.1),
]

steps = 1000
warmup = 200

# ต้องรันไฟล์นี้จากโฟลเดอร์ lab_03
output_dir = Path("results/lab_a")
output_dir.mkdir(parents=True, exist_ok=True)


def find_peaks(values):
    """Return indices of simple local maxima."""
    peaks = []

    for i in range(1, len(values) - 1):
        if values[i] > values[i - 1] and values[i] >= values[i + 1]:
            peaks.append(i)

    return peaks


def mean_period(values):
    """Average period measured in time steps."""
    peaks = find_peaks(values)

    if len(peaks) < 2:
        return None

    periods = [
        peaks[i + 1] - peaks[i]
        for i in range(len(peaks) - 1)
    ]

    return sum(periods) / len(periods)


def phase_lag_steps(values1, values2):
    """Estimate phase lag from peaks of o1 and o2."""
    peaks1 = find_peaks(values1)
    peaks2 = find_peaks(values2)

    if not peaks1 or not peaks2:
        return None

    period = mean_period(values1)

    if period is None:
        return None

    lags = []

    for p1 in peaks1:
        nearest = min(peaks2, key=lambda p2: abs(p2 - p1))
        lag = nearest - p1

        # wrap lag to approximately +/- half period
        while lag > period / 2:
            lag -= period

        while lag < -period / 2:
            lag += period

        lags.append(lag)

    return sum(lags) / len(lags)


summary_rows = []


for condition, alpha, phi in conditions:

    # SO(2) weight matrix
    w11 = alpha * math.cos(phi)
    w12 = alpha * math.sin(phi)
    w21 = -alpha * math.sin(phi)
    w22 = alpha * math.cos(phi)

    for run, (a1, a2) in enumerate(initial_states, start=1):

        rows = []

        # t = 0 ... 1000
        for t in range(steps + 1):

            o1 = math.tanh(a1)
            o2 = math.tanh(a2)

            rows.append([
                t,
                condition,
                a1,
                a2,
                o1,
                o2,
                alpha,
                phi,
                w11,
                w12,
                w21,
                w22,
            ])

            if t < steps:

                # simultaneous update
                next_a1 = w11 * o1 + w12 * o2
                next_a2 = w21 * o1 + w22 * o2

                a1, a2 = next_a1, next_a2

        name = f"{condition}_IC{run}"

        # -----------------------------
        # Save raw CSV
        # -----------------------------
        csv_path = output_dir / f"{name}.csv"

        with open(csv_path, "w", newline="", encoding="utf-8-sig") as file:

            writer = csv.writer(file)

            writer.writerow([
                "t",
                "condition",
                "a1",
                "a2",
                "o1",
                "o2",
                "alpha",
                "phi",
                "w11",
                "w12",
                "w21",
                "w22",
            ])

            writer.writerows(rows)

        # -----------------------------
        # Analyze after transient
        # -----------------------------
        stable = rows[warmup:]

        times = [row[0] for row in stable]
        values1 = [row[4] for row in stable]
        values2 = [row[5] for row in stable]

        amp1 = (max(values1) - min(values1)) / 2
        amp2 = (max(values2) - min(values2)) / 2

        period1 = mean_period(values1)
        period2 = mean_period(values2)

        phase_lag = phase_lag_steps(values1, values2)

        summary_rows.append([
            condition,
            run,
            alpha,
            phi,
            initial_states[run - 1][0],
            initial_states[run - 1][1],
            amp1,
            amp2,
            period1,
            period2,
            phase_lag,
        ])

        # -----------------------------
        # Plot
        # -----------------------------
        fig, axes = plt.subplots(2, 1, figsize=(10, 7))

        # Time plot
        axes[0].plot(times, values1, label="o1")
        axes[0].plot(times, values2, label="o2")

        axes[0].set_xlabel("Time step")
        axes[0].set_ylabel("Output")
        axes[0].set_title(
            f"{name}: alpha={alpha}, phi={phi} rad"
        )

        axes[0].legend()
        axes[0].grid(True)

        # Phase plane
        axes[1].plot(values1, values2)

        axes[1].set_xlabel("o1")
        axes[1].set_ylabel("o2")
        axes[1].set_title("Phase plane")

        axes[1].set_aspect("equal", adjustable="box")
        axes[1].grid(True)

        fig.tight_layout()

        fig.savefig(
            output_dir / f"{name}.png",
            dpi=180
        )

        plt.close(fig)

        print(
            f"{name}: "
            f"amp o1={amp1:.4f}, "
            f"amp o2={amp2:.4f}, "
            f"period o1={period1:.2f} steps, "
            f"phase lag={phase_lag:.2f} steps"
        )


# -----------------------------
# Save summary table
# -----------------------------
with open(
    output_dir / "lab_a_summary.csv",
    "w",
    newline="",
    encoding="utf-8-sig",
) as file:

    writer = csv.writer(file)

    writer.writerow([
        "condition",
        "run",
        "alpha",
        "phi",
        "initial_a1",
        "initial_a2",
        "amplitude_o1",
        "amplitude_o2",
        "period_o1_steps",
        "period_o2_steps",
        "phase_lag_steps",
    ])

    writer.writerows(summary_rows)


print()
print("Finished!")
print(f"Results saved in: {output_dir.resolve()}")