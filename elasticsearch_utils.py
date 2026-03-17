from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError, NotFoundError, TransportError

def fetch_index_timestamps(index_name: str, host: str = "http://localhost:9200") -> tuple:
    """
    Fetch the first and last @timestamp from an Elasticsearch index.
    
    Args:
        index_name (str): Name of the Elasticsearch index to query
        host (str): Elasticsearch cluster host URL (default: http://localhost:9200)
        
    Returns:
        tuple: (first_timestamp, last_timestamp) where each is a datetime object or None
        
    Raises:
        ConnectionError: If unable to connect to Elasticsearch
        TransportError: If query fails due to transport issues
        ValueError: If timestamp parsing fails
    """
    es = Elasticsearch([host])
    
    try:
        # Get first document (sorted ascending by @timestamp)
        first_query = {
            "size": 1,
            "sort": [{"@timestamp": {"order": "asc"}}],
            "_source": ["@timestamp"]
        }
        first_response = es.search(index=index_name, body=first_query)
        
        # Get last document (sorted descending by @timestamp)
        last_query = {
            "size": 1,
            "sort": [{"@timestamp": {"order": "desc"}}],
            "_source": ["@timestamp"]
        }
        last_response = es.search(index=index_name, body=last_query)
        
        # Extract timestamps
        first_timestamp = None
        last_timestamp = None
        
        if first_response['hits']['hits']:
            first_timestamp_str = first_response['hits']['hits'][0]['_source']['@timestamp']
            first_timestamp = datetime.fromisoformat(first_timestamp_str.replace('Z', '+00:00'))
            
        if last_response['hits']['hits']:
            last_timestamp_str = last_response['hits']['hits'][0]['_source']['@timestamp']
            last_timestamp = datetime.fromisoformat(last_timestamp_str.replace('Z', '+00:00'))
            
        return (first_timestamp, last_timestamp)
        
    except NotFoundError:
        # Index does not exist or is empty
        return (None, None)
    except Exception as e:
        # Re-raise connection or other errors with more context
        raise e