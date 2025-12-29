import os
from dotenv import load_dotenv
from pymongo import MongoClient

"""
Migration script: Copy data from labsDB.lectures to classroomsDB.classroom,
transforming 'lab' field to 'classroom'. Also copy users and settings.
Run once against your Atlas cluster (MONGO_URI in .env).
"""

def main():
    load_dotenv()
    mongo_uri = os.getenv('MONGO_URI')
    if not mongo_uri:
        raise RuntimeError('MONGO_URI missing in environment')
    client = MongoClient(mongo_uri)

    src_db = client['labsDB']
    dst_db = client['classroomsDB']

    src_lectures = src_db['lectures']
    dst_classroom = dst_db['classroom']

    # Copy lectures → classroom
    count = 0
    for doc in src_lectures.find({}):
        # Transform lab→classroom
        classroom_value = doc.get('classroom') or doc.get('lab')
        doc_copy = {k: v for k, v in doc.items() if k != '_id'}
        if classroom_value is not None:
            doc_copy['classroom'] = classroom_value
        # Remove legacy lab field
        doc_copy.pop('lab', None)
        dst_classroom.insert_one(doc_copy)
        count += 1
    print(f"Migrated {count} lecture documents to classroomsDB.classroom")

    # Copy users (upsert)
    src_users = src_db['users']
    dst_users = dst_db['users']
    for u in src_users.find({}):
        u_copy = {k: v for k, v in u.items() if k != '_id'}
        dst_users.update_one({'username': u_copy.get('username')}, {'$set': u_copy}, upsert=True)
    print("Users migrated/upserted")

    # Copy settings (upsert single doc)
    src_settings = src_db['settings']
    dst_settings = dst_db['settings']
    s = src_settings.find_one({'_id': 'global'})
    if s is None:
        s = {'_id': 'global', 'weekdays': 'sun-thu'}
    dst_settings.update_one({'_id': 'global'}, {'$set': {'weekdays': s.get('weekdays', 'sun-thu')}}, upsert=True)
    print("Settings migrated/upserted")

    print("Migration completed. Verify data, then optionally drop labsDB.")

if __name__ == '__main__':
    main()
