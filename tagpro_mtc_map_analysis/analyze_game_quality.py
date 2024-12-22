import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Load the CSV file into a DataFrame
file_path = 'Polaris_matches.csv'  # Replace with your actual file path
df = pd.read_csv(file_path)

# Drop unnecessary columns
columns_to_drop = ["Server_Flag", "Map_NewestElements", "Extra_Name"]
df = df.drop(columns=columns_to_drop)

# Remove the "#" from the Match_ID column
df['Match_ID'] = df['Match_ID'].str.replace('#', '', regex=False)

# Filter to keep only rows where "Public_Private" is "public"
df = df[df['Public_Private'] == 'public']

#  convert datetime to datetime object
import pandas as pd

# Assuming 'df' is your DataFrame and 'date_column' is the column of dates
df["Match_Datetime"] = pd.to_datetime(df["Match_Datetime"], format='%a %d %b %Y, %H:%M')


# Normalize match time: Late night games score lower
def time_of_game_score(datetime_str):
    match_time = pd.to_datetime(datetime_str, format="%a %d %b %Y, %H:%M")
    hour = match_time.hour
    # Late night (midnight to 6 AM) scores lower, normalize to -1 to 1
    return -1 + 2 * ((hour - 0) / (24 - 0)) if hour <= 6 else -1 + 2 * ((hour - 6) / (24 - 6))


df['Time_Score'] = df['Match_Datetime'].apply(time_of_game_score)


# Normalize match duration: Longer games score higher
def duration_score(duration_str):
    minutes, seconds = map(int, duration_str.split(':'))
    total_seconds = minutes * 60 + seconds
    max_seconds = 600  # Assume 10 minutes as a reasonable max duration
    return -1 + 2 * (total_seconds / max_seconds)


df['Duration_Score'] = df['Match_Duration'].apply(duration_score)


# Normalize score difference: Closer games score higher
def score_difference_score(red, blue):
    difference = abs(int(red) - int(blue))
    max_difference = 10  # Assume a maximum reasonable difference of 10
    return 1 - (difference / max_difference) * 2


df['Score_Diff_Score'] = df.apply(lambda row: score_difference_score(row['Score_Red'], row['Score_Blue']), axis=1)

# Combine scores into a weighted average for Game_Quality
# Assign weights: e.g., Time: 0.4, Duration: 0.3, Score Difference: 0.3
weights = {'Time_Score': 0.3, 'Duration_Score': 0.3, 'Score_Diff_Score': 0.4}
df['Game_Quality'] = (df['Time_Score'] * weights['Time_Score'] +
                      df['Duration_Score'] * weights['Duration_Score'] +
                      df['Score_Diff_Score'] * weights['Score_Diff_Score'])

# Drop intermediate columns used for calculation
df = df.drop(columns=['Time_Score', 'Duration_Score', 'Score_Diff_Score'])

# Display the updated DataFrame
print(df)

# Plotting
plt.figure(figsize=(20, 6))
plt.scatter(df["Match_Datetime"], df['Game_Quality'], color='blue', alpha=0.7, label='Match Score')

# Adding labels, title, and legend
plt.xlabel('Time of Game')
plt.ylabel('Game Quality')
plt.title('Game Quality Over Time')

# Scale x-axis to show time in a more meaningful way
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=12))
plt.xticks(rotation=90)  # Rotate x-axis labels for better readability

# Calculate a moving average for Game Quality
window_size = 50  # Adjust window size for smoothing
df['Game_Quality_MA'] = df['Game_Quality'].rolling(window=window_size, min_periods=1).mean()

# Plot the moving average as a trend line
plt.plot(df["Match_Datetime"], df['Game_Quality_MA'], color='red', linestyle='-', linewidth=2, label='Average Game Quality')

plt.legend()
plt.grid(True)  # Add grid for better visualization

#  save figure
plt.savefig("Polaris_Game_Quality.png", dpi=300, bbox_inches="tight")

# Show the plot
plt.tight_layout()  # Adjust layout to prevent label overlap
plt.show()
plt.close()
