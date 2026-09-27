import math
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ============================================================
# Lab B - Modulatory Input
# ============================================================

# Baseline parameters
alpha = 1.1
phi = 0.2

# Initial state
a1 = 0.1
a2 = 0.0

# ------------------------------------------------------------
# Modulatory input settings
# PowerPoint does not specify fixed values for M and I.
# These values are chosen for this experiment.
# ------------------------------------------------------------
M = 1.0
I_ON = 0.10

# Three segments:
# before input -> during input -> after input
SEGMENT_STEPS = 400
TOTAL_STEPS = SEGMENT_STEPS * 3

# Ignore transient after the beginning/switching of each segment
ANALYSIS_SKIP = 100


# ============================================================
# Baseline SO(2) weights
# ============================================================

Wd0 = alpha * math.cos(phi)
Wd1 = alpha * math.sin(phi)


# ============================================================
# Output directory
# ============================================================

LAB03_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = LAB03_DIR / "results" / "lab_b"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# Modulatory input I(t)
# ============================================================

def input_signal(t: int):
    """
    I(t):
    0 -> constant -> 0
    """

    if t < SEGMENT_STEPS:
        return 0.0, "before"

    elif t < 2 * SEGMENT_STEPS:
        return I_ON, "during"

    else:
        return 0.0, "after"


# ============================================================
# Analysis functions
# ============================================================

def find_peaks(values):
    """Find simple local maxima."""

    peaks = []

    for i in range(1, len(values) - 1):

        if values[i] > values[i - 1] and values[i] >= values[i + 1]:
            peaks.append(i)

    return peaks


def mean_period(values):
    """Calculate mean period in steps."""

    peaks = find_peaks(values)

    if len(peaks) < 2:
        return None

    periods = []

    for i in range(len(peaks) - 1):
        periods.append(peaks[i + 1] - peaks[i])

    return sum(periods) / len(periods)


def amplitude(values):
    """Amplitude = (max - min) / 2."""

    return (max(values) - min(values)) / 2


# ============================================================
# Run simulation
# ============================================================

rows = []

for t in range(TOTAL_STEPS + 1):

    I, segment = input_signal(t)

    # Modulated cross-connections
    W12m = Wd1 + M * I
    W21m = -(Wd1 + M * I)

    # Current outputs
    o1 = math.tanh(a1)
    o2 = math.tanh(a2)

    rows.append([
        t,
        segment,
        I,
        M,
        Wd0,
        Wd1,
        W12m,
        W21m,
        a1,
        a2,
        o1,
        o2,
        alpha,
        phi,
    ])

    # Simultaneous update
    if t < TOTAL_STEPS:

        next_a1 = Wd0 * o1 + W12m * o2
        next_a2 = W21m * o1 + Wd0 * o2

        a1 = next_a1
        a2 = next_a2


# ============================================================
# Save raw CSV
# ============================================================

raw_csv = OUTPUT_DIR / "lab_b.csv"

with open(raw_csv, "w", newline="", encoding="utf-8-sig") as file:

    writer = csv.writer(file)

    writer.writerow([
        "t",
        "segment",
        "I",
        "M",
        "Wd0",
        "Wd1",
        "W12m",
        "W21m",
        "a1",
        "a2",
        "o1",
        "o2",
        "alpha",
        "phi",
    ])

    writer.writerows(rows)


# ============================================================
# Analyze before / during / after
# ============================================================

segments = {
    "before": (
        ANALYSIS_SKIP,
        SEGMENT_STEPS
    ),

    "during": (
        SEGMENT_STEPS + ANALYSIS_SKIP,
        2 * SEGMENT_STEPS
    ),

    "after": (
        2 * SEGMENT_STEPS + ANALYSIS_SKIP,
        TOTAL_STEPS
    ),
}


summary_rows = []

for segment_name, (start, end) in segments.items():

    segment_rows = [
        row for row in rows
        if start <= row[0] < end
    ]

    o1_values = [row[10] for row in segment_rows]
    o2_values = [row[11] for row in segment_rows]

    amp_o1 = amplitude(o1_values)
    amp_o2 = amplitude(o2_values)

    period_o1 = mean_period(o1_values)
    period_o2 = mean_period(o2_values)

    I_value = segment_rows[0][2]
    W12_value = segment_rows[0][6]
    W21_value = segment_rows[0][7]

    summary_rows.append([
        segment_name,
        start,
        end,
        I_value,
        M,
        W12_value,
        W21_value,
        amp_o1,
        amp_o2,
        period_o1,
        period_o2,
    ])

    print(
        f"{segment_name}: "
        f"I={I_value:.3f}, "
        f"W12m={W12_value:.4f}, "
        f"W21m={W21_value:.4f}, "
        f"amp_o1={amp_o1:.4f}, "
        f"amp_o2={amp_o2:.4f}, "
        f"period_o1={period_o1:.2f} steps, "
        f"period_o2={period_o2:.2f} steps"
    )


# ============================================================
# Save summary CSV
# ============================================================

summary_csv = OUTPUT_DIR / "lab_b_summary.csv"

with open(summary_csv, "w", newline="", encoding="utf-8-sig") as file:

    writer = csv.writer(file)

    writer.writerow([
        "segment",
        "analysis_start",
        "analysis_end",
        "I",
        "M",
        "W12m",
        "W21m",
        "amplitude_o1",
        "amplitude_o2",
        "period_o1_steps",
        "period_o2_steps",
    ])

    writer.writerows(summary_rows)


# ============================================================
# Create plot
# ============================================================

times = [row[0] for row in rows]

I_values = [row[2] for row in rows]

W12_values = [row[6] for row in rows]
W21_values = [row[7] for row in rows]

o1_values = [row[10] for row in rows]
o2_values = [row[11] for row in rows]


fig, axes = plt.subplots(
    3,
    1,
    figsize=(12, 9),
    sharex=True
)


# ------------------------------------------------------------
# Plot 1: CPG outputs
# ------------------------------------------------------------

axes[0].plot(times, o1_values, label="o1")
axes[0].plot(times, o2_values, label="o2")

axes[0].set_ylabel("Output")
axes[0].set_title("Lab B - Modulatory Input")

axes[0].legend()
axes[0].grid(True)


# ------------------------------------------------------------
# Plot 2: Input I(t)
# ------------------------------------------------------------

axes[1].plot(times, I_values, label="I(t)")

axes[1].set_ylabel("Input I")

axes[1].legend()
axes[1].grid(True)


# ------------------------------------------------------------
# Plot 3: Modulated cross-connections
# ------------------------------------------------------------

axes[2].plot(times, W12_values, label="W12m")
axes[2].plot(times, W21_values, label="W21m")

axes[2].set_xlabel("Time step")
axes[2].set_ylabel("Weight")

axes[2].legend()
axes[2].grid(True)


# Mark input switching points
for ax in axes:

    ax.axvline(
        SEGMENT_STEPS,
        linestyle="--"
    )

    ax.axvline(
        2 * SEGMENT_STEPS,
        linestyle="--"
    )


fig.tight_layout()

plot_path = OUTPUT_DIR / "lab_b_plot.png"

fig.savefig(
    plot_path,
    dpi=180
)

plt.close(fig)


# ============================================================
# Final information
# ============================================================

print()
print("Lab B finished!")
print(f"alpha = {alpha}")
print(f"phi = {phi}")
print(f"M = {M}")
print(f"I during modulation = {I_ON}")

print()
print(f"Raw CSV     : {raw_csv}")
print(f"Summary CSV : {summary_csv}")
print(f"Plot        : {plot_path}")