import sys
import hashlib
import uuid

def generate_deterministic_uuid(fields):
    """
    Generates a deterministic UUID based on a list of string fields.
    Joins the fields with a delimiter and hashes them.
    """
    if not fields:
        raise ValueError("At least one field is required to generate a UUID.")
        
    # Join fields with a unique delimiter to prevent collision (e.g. "a"+"bc" vs "ab"+"c")
    combined = "||".join(str(f) for f in fields)
    
    # MD5 hash
    m = hashlib.md5()
    m.update(combined.encode('utf-8'))
    
    # Convert first 16 bytes of the hash into a UUID
    deterministic_uuid = uuid.UUID(bytes=m.digest())
    return str(deterministic_uuid)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_deterministic_id.py <field1> [field2] ...")
        sys.exit(1)
        
    print(generate_deterministic_uuid(sys.argv[1:]))
