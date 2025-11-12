import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import localSession
from app.crudFunctions import userFunctions, tagFunctions
import random

def get_db():
    db = localSession()
    return db

class TestTagFunctionsComplete:
    def __init__(self):
        self.db = get_db()
        self.test_user_ids = []
        self.test_tag_ids = []

    def run_all_tests(self):
        print("Run ALL Tag Function Tests")

        try:

            print("Create Test Tags")
            self.setup_test_tags()

            print("Test All Read Functions")
            self.test_get_tag_by_id()
            self.test_get_all_system_tags()
            self.test_get_custom_tags_by_user()
            self.test_get_all_tags_for_user()

            print("Test All Update Functions")
            self.test_update_tag()
        except Exception as e:
            print(f"TEST FAILED: {e}")
            raise
        finally:
            self.cleanup()

    def setup_test_tags(self):
        system_tags_data = [
            ("Important", "#FF0000"),
            ("Urgent", "#FFA500"),
            ("Archive", "#808080"),
        ]

        for tag_name, tag_color in system_tags_data:
            system_tag = tagFunctions.create_system_tag(
                self.db,
                name=tag_name,
                color=tag_color
            )
            system_tag_id = system_tag['tag_id']
            self.test_tag_ids.append(system_tag_id)
            
        custom_tags_data = [
            ("John", "Doe", f"john.doe{random.randint(1000,9999)}@test.com", "Tag Name #1", "#18b1c2"),
            ("Jane", "Smith", f"jane.smith{random.randint(1000,9999)}@test.com", "Tag Name #2", "#7531b9"),
            ("Bob", "Johnson", f"bob.j{random.randint(1000,9999)}@test.com", "Tag Name #3", "#2a9e2f"),
            ("Alice", "Williams", f"alice.w{random.randint(1000,9999)}@test.com", "Tag Name #4", "#0c0539"),
            ("Charlie", "Brown", f"charlie.b{random.randint(1000,9999)}@test.com", "Tag Name #5", "#2dbc7e"),
        ]
                
        for first_name, last_name, email, tag_name, tag_color in custom_tags_data:
            user = userFunctions.create_user(
                self.db,
                first_name, 
                last_name,
                email
            )
            user_id = user['user_id']
            self.test_user_ids.append(user_id)

            tag = tagFunctions.create_custom_tag(
                self.db,
                user_id=user_id,
                name=tag_name,
                color=tag_color
            )
            tag_id = tag['tag_id']
            self.test_tag_ids.append(tag_id)
            print(f"Created tag {tag_id} for user {user_id}")

    def test_get_tag_by_id(self):
        tag_id = self.test_tag_ids[0]

        tag = tagFunctions.get_tag_by_id(
            self.db,
            tag_id
        )

        assert tag is not None, "Tag could not be retrieved"
        assert tag['tag_id'] == tag_id, "Tag has the wrong Id"
        print(f"Retrieved the tag {tag_id}")

        assert 'user_id' in tag, "Missing user_id"
        assert 'name' in tag, "Missing name"
        assert 'color' in tag, "Missing color"
        assert 'tag_type' in tag, "Missing tag_type"
        print(f"Tag has all its attributes")

        invalid_tag = tagFunctions.get_tag_by_id(
            self.db,
            99999
        )
        assert invalid_tag is None, f"Invalid Tag {tag_id} was incorrectly found"
        print(f"Tag can be retrieved with its id")

    def test_get_all_system_tags(self):
        list_of_system_tags = tagFunctions.get_all_system_tags(
            self.db
        )
        assert list_of_system_tags is not None, "Could not retrieve list of system tags"
        assert isinstance(list_of_system_tags, list), "The type of list_of_system_tags wasn't a list"
        print("Retrieved all the system tags from table") 

        for each_system_tag in list_of_system_tags:
            assert each_system_tag['tag_type'] == 'system', f"Wrong tag type for tag {each_system_tag['tag_id']}"

            assert each_system_tag['user_id'] is None, f"System tag {each_system_tag['tag_id']} should have NULL user_id"
            
            assert 'tag_id' in each_system_tag, "Missing tag_id"
            assert 'name' in each_system_tag, "Missing name"
            assert 'color' in each_system_tag, "Missing color"
            assert 'tag_type' in each_system_tag, "Missing tag_type"
            assert len(each_system_tag['name']) > 0, "Tag name should not be empty"
            assert each_system_tag['color'].startswith('#'), "Color should start with #"
            
        print("All System Tags are correctly retrieved.")

    def test_get_custom_tags_by_user(self):
        user_id = self.test_user_ids[0]

        list_of_user_tags = tagFunctions.get_custom_tags_by_user(
            self.db,
            user_id
        )
        assert list_of_user_tags is not None, "Could not retrieve list of user tags"
        assert isinstance(list_of_user_tags, list), "The type of list_of_user_tags wasn't a list"
        print("Retrieved all the user tags from table") 

        for each_custom_tag in list_of_user_tags:
            assert each_custom_tag['user_id'] == user_id, f"User ID mismatch for tag {each_custom_tag['tag_id']}"
            assert each_custom_tag['tag_type'] == 'custom', f"Tag {each_custom_tag['tag_id']} is not a custom tag"

            assert 'tag_id' in each_custom_tag, "Missing tag_id"
            assert 'name' in each_custom_tag, "Missing name"
            assert 'color' in each_custom_tag, "Missing color"
            assert 'tag_type' in each_custom_tag, "Missing tag_type"

        print(f"All custom tags have the correct fields for user {user_id}")

        invalid_list_of_tags = tagFunctions.get_custom_tags_by_user(
            self.db,
            99999
        )
        assert invalid_list_of_tags == [] or invalid_list_of_tags is None, "List of User tags is not empty/invalid"
        print("Correctly handled invalid user Id case") 

    def test_get_all_tags_for_user(self):
        user_id = self.test_user_ids[0]

        list_of_user_tags = tagFunctions.get_all_tags_for_user(
            self.db,
            user_id
        )
        assert list_of_user_tags is not None, "Could not retrieve list of user tags"
        assert isinstance(list_of_user_tags, list), "The type of list_of_user_tags wasn't a list"
        print("Retrieved all the user tags from table") 

        for each_tag in list_of_user_tags:
            assert each_tag['tag_type'] in ['custom', 'system'], f"Tag {each_tag['tag_id']} is not a valid tag"

            assert 'user_id' in each_tag, "Missing user_id"
            assert 'name' in each_tag, "Missing name"
            assert 'color' in each_tag, "Missing color"
            assert 'tag_type' in each_tag, "Missing tag_type"

            if each_tag['tag_type'] == 'system':
                assert each_tag['user_id'] is None, \
                    f"System tag {each_tag['tag_id']} should have NULL user_id"
            else: 
                assert each_tag['user_id'] == user_id, \
                    f"Custom tag {each_tag['tag_id']} should belong to user {user_id}"
        print(f"All tags have the correct fields for user {user_id}")

        invalid_list_of_tags = tagFunctions.get_all_tags_for_user(
            self.db,
            99999
        )
        assert invalid_list_of_tags is not None, "List of User tags is not empty/invalid"
        assert all(tag['tag_type'] == 'system' for tag in invalid_list_of_tags), \
        "Should only return system tags for invalid user"
        print("Correctly handled invalid user Id case") 

    def test_update_tag(self):
        tag_id = self.test_tag_ids[5]

        updated_tag = tagFunctions.update_tag(
            self.db,
            tag_id,
            name="changed tag name"
        )
        
        assert updated_tag['name'] == "changed tag name", "Tag name not updated"
        assert updated_tag['color'] == "#2a9e2f", "Color should remain unchanged"
        assert updated_tag['tag_type'] == "custom", "Tag type should remain unchanged"
        print(f"Successfully updated tag {tag_id}'s name")

        updated_color = tagFunctions.update_tag(
            self.db,
            tag_id,
            color="#57eba3"
        )
        assert updated_color['name'] == "changed tag name", "Tag name should remain unchanged"
        assert updated_color['color'] == "#57eba3", "Color should be updated"
        assert updated_color['tag_type'] == "custom", "Tag type should remain unchanged"
        print(f"Successfully updated tag {tag_id}'s color")
        
        updated_everything = tagFunctions.update_tag(
            self.db,
            tag_id,
            name="changed again",
            color="#61c0e2",
        )
        assert updated_everything['name'] == "changed again", "Tag name should be updated"
        assert updated_everything['color'] == "#61c0e2", "Tag color should be updated"
        print("Successfully updated all fields at once")

        invalid = tagFunctions.update_tag(
            self.db, 
            99999, 
            name="Should Fail"
        )
        assert invalid is None, "Should return None for invalid tag ID"
        print("Correctly handles invalid tag ID")

    def cleanup(self):
        print("Cleaning up test data...")
        
        deleted_users = 0
        for user_id in self.test_user_ids:
            try:
                if userFunctions.delete_user_by_id(self.db, user_id):
                    deleted_users += 1
            except:
                pass
                
        print(f"Users deleted: {deleted_users}/{len(self.test_user_ids)}")

        self.test_user_ids.clear()
        self.test_tag_ids.clear()

        self.db.close()

if __name__ == "__main__":
    tester = TestTagFunctionsComplete()
    tester.run_all_tests()
