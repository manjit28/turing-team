import pandas as pd

def top20_by_population(df):
    """
    Returns the top 20 rows sorted by 'Population' column in descending order.
    
    Args:
        df (pd.DataFrame): Input DataFrame
        
    Returns:
        pd.DataFrame: Top 20 rows by population, or all rows if less than 20
    """
    return df.nlargest(20, 'Population')

# Demo with sample data
sample_data = {
    'City': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'],
    'Population': [8336817, 3979576, 2746388, 2320268, 1608139]
}

df = pd.DataFrame(sample_data)
result = top20_by_population(df)
print(result)