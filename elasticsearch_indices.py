# Jupyter notebook cell to list Elasticsearch indices with error handling
from elasticsearch import Elasticsearch

def list_elasticsearch_indices(url='http://localhost:9200'):
    """
    Connects to an Elasticsearch cluster and retrieves a list of index names.
    
    Args:
        url (str): Elasticsearch cluster URL. Defaults to 'http://localhost:9200'.
        
    Returns:
        list: List of index names, or None if connection fails.
    """
    try:
        # Create Elasticsearch client
        es = Elasticsearch([url])
        
        # Call cat indices API to get index names
        indices = es.cat.indices(format='json')
        
        # Extract index names
        index_names = [index['index'] for index in indices]
        
        return index_names
        
    except Exception as e:
        print(f"Error connecting to Elasticsearch at {url}: {e}")
        return None

# Execute the function to list indices
index_list = list_elasticsearch_indices()
if index_list is not None:
    print(index_list)