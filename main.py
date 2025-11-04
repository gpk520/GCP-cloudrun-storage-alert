import functions_framework
from cloudevents.http import CloudEvent
from google.cloud import storage

# Initialize the Cloud Storage client outside the function for better performance
storage_client = storage.Client()

@functions_framework.cloud_event
def set_object_access_policy(cloud_event: CloudEvent) -> None:
    """
    Triggers on GCS object finalize event and sets object ACL based on bucket prefix.

    - Buckets starting with 'dev-' must be private.
    - Buckets starting with 'internal-' or 'non-iam' must be public (public-read).
    """
    
    # 1. Extract event data
    data = cloud_event.get_data()
    bucket_name = data.get('bucket')
    object_name = data.get('name')

    if not bucket_name or not object_name:
        print("Missing bucket name or object name in event data.")
        return

    print(f"Processing object: {object_name} in bucket: {bucket_name}")
    
    # 2. Determine required ACL based on bucket prefix
    if bucket_name.startswith('dev-'):
        # Private: Set predefined ACL to 'private' (or remove all public access)
        predefined_acl = 'private'
        print(f"Bucket {bucket_name} starts with 'dev-', setting ACL to **private**.")
    elif bucket_name.startswith('internal-') or bucket_name.startswith('non-iam'):
        # Public: Set predefined ACL to 'publicRead'
        predefined_acl = 'publicRead'
        print(f"Bucket {bucket_name} starts with 'internal-' or 'non-iam', setting ACL to **public-read**.")
    else:
        # Default policy for all other buckets (e.g., maintain default or set private)
        # Assuming private is the safest default if not explicitly defined
        predefined_acl = 'private'
        print(f"Bucket {bucket_name} has no matching prefix, setting ACL to **private**.")

    # 3. Apply the determined ACL to the object
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(object_name)

        # Update the object with the new predefined ACL
        # Note: If Uniform Bucket-Level Access is enabled on the bucket, 
        # object ACLs are disabled, and this call will fail.
        blob.acl.save(predefined_acl) 
        
        # Alternative: use blob.make_public() or blob.make_private() if only 
        # switching between allUsers:READER and private is needed.
        # if predefined_acl == 'publicRead':
        #    blob.make_public()
        # else:
        #    blob.make_private()

        print(f"Successfully set ACL on gs://{bucket_name}/{object_name} to {predefined_acl}.")

    except Exception as e:
        print(f"Error updating ACL for gs://{bucket_name}/{object_name}: {e}")
        # The service account running Cloud Run must have the 'storage.objectAdmin' role.


if __name__ == '__main__':
    # This block is for local testing (optional)
    print("Cloud Run service started.")
