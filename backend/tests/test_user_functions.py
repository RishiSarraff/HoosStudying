import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import localSession
from app.crudFunctions import userFunctions
import random

def get_db():
    db = localSession()
    return db

class TestUserFunctionsComplete:
    def __init__(self):
        self.db = get_db()
        self.test_users = [] 
        ## We will keep the test_users in an array to clean them up after successes, fails and so on

    def run_all_tests(self):
        print("Run ALL User Function Tests")

        try:

            print("Create Test Users")
            self.setup_test_users()

            print("Test All Read Functions")
            self.test_get_user_by_id()
            self.test_get_all_users()
            self.test_get_user_by_email()
            self.test_get_user_by_name()
            self.test_get_user_count()

            print("Test All Update Functions")
            self.test_update_user()
        except Exception as e:
            print(f"TEST FAILED: {e}")
            raise
        finally:
            self.cleanup()

    def setup_test_users(self):
        test_data = [
            ("John", "Doe", f"john.doe{random.randint(1000,9999)}@test.com"),
            ("Jane", "Smith", f"jane.smith{random.randint(1000,9999)}@test.com"),
            ("Bob", "Johnson", f"bob.j{random.randint(1000,9999)}@test.com"),
            ("Alice", "Williams", f"alice.w{random.randint(1000,9999)}@test.com"),
            ("Charlie", "Brown", f"charlie.b{random.randint(1000,9999)}@test.com"),
        ]

        for first_name, last_name, email in test_data:
            user = userFunctions.create_user(self.db, first_name, last_name, email)
            self.test_users.append(user['user_id'])
            print(f"Created the test user with {user['user_id']}")

    def test_get_user_by_id(self):
        user_id = self.test_users[0]

        fetched_user = userFunctions.get_user_by_id(self.db, user_id)
        assert fetched_user is not None, "Failed to get User"
        assert fetched_user['first_name'] == "John", "User First Name Mismatch"
        assert fetched_user['last_name'] == "Doe", "User Last Name Mismatch"
        print(f"Retrieved user {fetched_user['first_name']} {fetched_user['last_name']}")

        invalid_user = userFunctions.get_user_by_id(self.db, 999999)
        assert invalid_user is None, "Should return None for invalid ID"
        print("Correctly returns None for invalid user Id")

    def test_get_all_users(self):
        all_users = userFunctions.get_all_users(self.db)
        assert all_users is not None, "Failed to fetch all users"
        assert len(all_users) >= len(self.test_users), f"Should have at least {len(self.test_users)} users"

        test_set_user_ids = set(self.test_users)
        fetched_set_of_users = set(user['user_id'] for user in all_users)

        assert test_set_user_ids.issubset(fetched_set_of_users), "Not all test users found in results"

        print(f"Successfully fetched {len(all_users)}")

    def test_get_user_by_email(self):
        user_id = self.test_users[1]

        user_by_id = userFunctions.get_user_by_id(self.db, user_id)
        user_email = user_by_id['email']

        fetched_user = userFunctions.get_user_by_email(self.db, user_email)
        assert fetched_user is not None, "Failed to get User by email"
        assert fetched_user['email'] == user_email, "Email Mismatch"
        assert fetched_user['first_name'] == user_by_id['first_name'], "User First Name Mismatch"
        print(f"Retrieved user with email: {user_email}")

        non_existent = userFunctions.get_user_by_email(self.db, "nonexistent@test.com")
        assert non_existent is None, "Should return None for non-existent email"
        print("Correctly returns None for invalid email")

    def test_get_user_by_name(self):        
        # Test with first name
        users_named_john = userFunctions.get_user_by_name(self.db, "John")
        assert len(users_named_john) >= 1, "Should find at least one John"
        assert any(user['first_name'] == "John" for user in users_named_john), "Should find John"
        print(f"{len(users_named_john)} users named 'John'")
        
        # Test with last name
        users_named_smith = userFunctions.get_user_by_name(self.db, "Smith")
        assert len(users_named_smith) >= 1, "Should find at least one Smith"
        assert any(user['last_name'] == "Smith" for user in users_named_smith), "Should find Smith"
        print(f"{len(users_named_smith)} users with 'Smith' in name")
        
        # Test with partial name
        users_with_j = userFunctions.get_user_by_name(self.db, "J")
        assert len(users_with_j) >= 2, "Should find multiple users with 'J' in name"
        print(f"{len(users_with_j)} users with 'J' in name")
        
        # Test with full name
        users_full_name = userFunctions.get_user_by_name(self.db, "Bob Johnson")
        assert len(users_full_name) >= 1, "Should find user by full name"
        print(f"{len(users_full_name)} users with full name match")

    def test_get_user_count(self):        
        initial_count = userFunctions.get_user_count(self.db)
        assert initial_count >= len(self.test_users), f"Should have at least {len(self.test_users)} users"
        print(f"Initial user count is {initial_count} users")
        
        new_user = userFunctions.create_user(
            self.db, 
            "Test", 
            "Counter", 
            f"counter{random.randint(1000,9999)}@test.com"
        )
        self.test_users.append(new_user['user_id'])

        new_count = userFunctions.get_user_count(self.db)
        assert new_count == initial_count + 1, "Count should increase by 1"
        print(f"Count correctly increased to {new_count}")

    def test_get_pipeline_count_by_user(self):        
        user_id = self.test_users[0]
        
        pipeline_count = userFunctions.get_pipeline_count_by_user(self.db, user_id)
        assert pipeline_count >= 1, "Should have at least 1 pipeline (general)"
        print(f"User has {pipeline_count} pipelines")
        
        if pipeline_count >= 1:
            print("Trigger successfully created general pipeline")

    def test_update_user(self):
        user_id = self.test_users[3]

        updated_user = userFunctions.update_user(
            self.db,
            user_id,
            first_name="Charlie"
        )

        assert updated_user['first_name'] == "Charlie", "First name not updated"
        assert updated_user['last_name'] == "Williams", "Last name should remain unchanged"
        print("Successfully updated user")

        # Update last name only
        updated = userFunctions.update_user(
            self.db,
            user_id,
            last_name="Wilson"
        )
        print(updated['first_name'])
        print(updated['last_name'])
        assert updated['first_name'] == "Charlie", "First name should remain as updated"
        assert updated['last_name'] == "Wilson", "Last name not updated"
        print("Successfully updated last name only")
        
        # Update email
        new_email = f"alicia.wilson{random.randint(1000,9999)}@test.com"
        updated = userFunctions.update_user(
            self.db,
            user_id,
            email=new_email
        )
        assert updated['email'] == new_email, "Email not updated"
        print("Successfully updated email")
        
        # Update all fields at once
        updated = userFunctions.update_user(
            self.db,
            user_id,
            first_name="Alice",
            last_name="Williams",
            email=f"alice.restored{random.randint(1000,9999)}@test.com"
        )
        assert updated['first_name'] == "Alice", "Failed to update all fields"
        print("Successfully updated all fields at once")


    def cleanup(self):
        print("Cleaning up test data...")
        
        deleted_count = 0
        for user_id in self.test_users:
            try:
                if userFunctions.delete_user_by_id(self.db, user_id):
                    deleted_count += 1
            except:
                pass
                
        print(f"Cleaned up {deleted_count}/{len(self.test_users)} test users")
        self.db.close()

if __name__ == "__main__":
    tester = TestUserFunctionsComplete()
    tester.run_all_tests()
