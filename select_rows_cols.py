# Select the first three columns of the last ten rows
result = df.iloc[-10:, :3]

# Explanation:
# - df.iloc[-10:, :3] uses integer-location based indexing
# - [-10:] selects the last 10 rows (or all rows if less than 10)
# - [:3] selects the first 3 columns (indices 0, 1, 2)