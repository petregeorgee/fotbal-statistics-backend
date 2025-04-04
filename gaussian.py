import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm

# Step 1: Create mock inputs for match half-time and full-time scores
np.random.seed(42)  # For reproducibility

# Generate random half-time scores (0-3 goals)
half_time_scores = np.random.randint(0, 4, size=100)

# Generate random full-time scores (0-6 goals)
full_time_scores = np.random.randint(0, 7, size=100)

# Combine into a DataFrame
mock_data = pd.DataFrame({
    'Half-Time Score': half_time_scores,
    'Full-Time Score': full_time_scores
})

# Step 2: Calculate Gaussian distribution parameters
half_time_mean = mock_data['Half-Time Score'].mean()
half_time_std = mock_data['Half-Time Score'].std()
full_time_mean = mock_data['Full-Time Score'].mean()
full_time_std = mock_data['Full-Time Score'].std()
print(half_time_mean)
print(half_time_std)

# Generate Gaussian distributions
x_half_time = np.linspace(0, 3, 100)
y_half_time = norm.pdf(x_half_time, loc=half_time_mean, scale=half_time_std)

x_full_time = np.linspace(0, 6, 100)
y_full_time = norm.pdf(x_full_time, loc=full_time_mean, scale=full_time_std)

# Step 3: Plot the Gaussian distributions
plt.figure(figsize=(12, 6))

# Half-Time Score Distribution
plt.subplot(1, 2, 1)
plt.plot(x_half_time, y_half_time, label=f"Mean: {half_time_mean:.2f}, Std Dev: {half_time_std:.2f}")
plt.title("Gaussian Distribution of Half-Time Scores")
plt.xlabel("Half-Time Score")
plt.ylabel("Probability Density")
plt.legend()

# Full-Time Score Distribution
plt.subplot(1, 2, 2)
plt.plot(x_full_time, y_full_time, label=f"Mean: {full_time_mean:.2f}, Std Dev: {full_time_std:.2f}")
plt.title("Gaussian Distribution of Full-Time Scores")
plt.xlabel("Full-Time Score")
plt.ylabel("Probability Density")
plt.legend()

plt.tight_layout()
plt.show()


def analyze_gaussian_distribution(half_time_scores, full_time_scores):
    half_time_array = np.array(half_time_scores)
    full_time_array = np.array(full_time_scores)

    half_time_mean = np.mean(half_time_array)
    half_time_std = np.std(half_time_array)

    full_time_mean = np.mean(full_time_array)
    full_time_std = np.std(full_time_array)

    x_half_time = np.linspace(min(half_time_array), max(half_time_array), 100)
    y_half_time = norm.pdf(x_half_time, loc=half_time_mean, scale=half_time_std)

    x_full_time = np.linspace(min(full_time_array), max(full_time_array), 100)
    y_full_time = norm.pdf(x_full_time, loc=full_time_mean, scale=full_time_std)

    plt.figure(figsize=(12, 6))

    # Half-Time Score Distribution
    plt.subplot(1, 2, 1)
    plt.plot(x_half_time, y_half_time, label=f"Mean: {half_time_mean:.2f}, Std Dev: {half_time_std:.2f}")
    plt.title("Gaussian Distribution of Half-Time Scores")
    plt.xlabel("Half-Time Score")
    plt.ylabel("Probability Density")
    plt.legend()

    # Full-Time Score Distribution
    plt.subplot(1, 2, 2)
    plt.plot(x_full_time, y_full_time, label=f"Mean: {full_time_mean:.2f}, Std Dev: {full_time_std:.2f}")
    plt.title("Gaussian Distribution of Full-Time Scores")
    plt.xlabel("Full-Time Score")
    plt.ylabel("Probability Density")
    plt.legend()

    plt.tight_layout()
    plt.show()

