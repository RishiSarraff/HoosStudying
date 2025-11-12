import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import localSession
from app.crudFunctions import userFunctions, messageFunctions, pipelineFunctions, conversationFunctions
import random

def get_db():
    db = localSession()
    return db

class TestMessageFunctionsComplete:
    def __init__(self):
        self.db = get_db()
        self.test_user_ids = []
        self.test_message_ids = []
        self.test_pipeline_ids = []
        self.test_conversation_ids = []
        self.test_general_conversation_ids = []
        ## We will keep the test_user_ids, message_ids, conversation in an array to clean them up after successes, fails and so on

    def run_all_tests(self):
        print("Run ALL Message Function Tests")

        try:
            print("Create Test Message")
            self.setup_test_messages()

            print("Test All Read Functions")
            self.test_get_all_messages_in_conversation()
            self.test_get_all_messages_from_user()
            self.test_get_all_pipeline_messages()
            self.test_get_message_by_id()
            self.test_get_recent_messages()
            self.test_get_last_message_in_conversation()

        except Exception as e:
            print(f"TEST FAILED: {e}")
            raise
        finally:
            self.cleanup()

    def setup_test_messages(self):
        ## in order to make a message, we need to make a conversation, which itself needs a user and a pipeline.
    
        test_data = [
            ("John", "Doe", f"john.doe{random.randint(1000,9999)}@test.com", "Pipeline Name 1", "Pipeline Description 1"),
            ("Jane", "Smith", f"jane.smith{random.randint(1000,9999)}@test.com", "Pipeline Name 2", "Pipeline Description 2"),
            ("Bob", "Johnson", f"bob.j{random.randint(1000,9999)}@test.com", "Pipeline Name 3", "Pipeline Description 3"),
            ("Alice", "Williams", f"alice.w{random.randint(1000,9999)}@test.com", "Pipeline Name 4", "Pipeline Description 4"),
            ("Charlie", "Brown", f"charlie.b{random.randint(1000,9999)}@test.com", "Pipeline Name 5", "Pipeline Description 5"),
        ]

        for first_name, last_name, email, pipeline_name, description in test_data:
            user = userFunctions.create_user(
                self.db, 
                first_name, 
                last_name, 
                email
            )

            user_id = user['user_id']

            self.test_user_ids.append(user_id)

            pipeline = pipelineFunctions.create_pipeline(
                self.db,
                user_id,
                pipeline_name,
                description
            )

            pipeline_id = pipeline['pipeline_id']

            self.test_pipeline_ids.append(pipeline_id)

            conversation = conversationFunctions.create_conversation(
                self.db, 
                user_id,
                pipeline_id
            )

            conversation_id = conversation['conversation_id']

            self.test_conversation_ids.append(conversation_id)

            general_conversation = conversationFunctions.create_general_conversation(
                self.db,
                user_id
            )
            general_conversation_id = general_conversation['conversation_id']

            self.test_conversation_ids.append(general_conversation_id)
            self.test_general_conversation_ids.append(general_conversation_id)

            print(f"Created the test user {user_id} with {conversation['user_id']} in pipeline {pipeline_id}")

            # after creating the test user we will create 3-4 messages for each conversation and insert those into our message ids list
            for i in range(5):
                user_message = messageFunctions.create_user_message(
                    self.db,
                    conversation_id,
                    f"This is user message #{i}"
                )
                self.test_message_ids.append(user_message['message_id'])

                bot_message = messageFunctions.create_bot_message(
                    self.db,
                    conversation_id,
                    f"This is bot message #{i}"
                )
                self.test_message_ids.append(bot_message['message_id'])

            # we created our messages here and insert them.

    def test_get_message_by_id(self):
        message_id = self.test_message_ids[0]

        message = messageFunctions.get_message_by_id(
            self.db,
            message_id
        )
        assert message is not None, f"Message from message id {message_id} could not be retrieved"
        assert message['message_id'] == message_id, "Message ID mismatch"

        assert 'conversation_id' in message, "Missing conversation_id"
        assert 'sender_type' in message, "Missing sender_type"
        assert 'message_text' in message, "Missing message_text"
        assert 'timestamp' in message, "Missing timestamp"

        assert message['sender_type'] in ['user', 'bot'], "Sender type of message is incorrect"
        assert len(message['message_text']) > 0, "Message text is empty"
        assert message['conversation_id'] in self.test_conversation_ids, \
            "Message belongs to invalid conversation"

        invalid_message = messageFunctions.get_message_by_id(
            self.db,
            99999
        )
        assert invalid_message is None, f"Invalid message was incorrectly returned back"
        print(f"Messages can be correctly retrieved using ID")

    def test_get_all_messages_from_user(self):
        user_id = self.test_user_ids[0]

        list_of_all_messages = messageFunctions.get_all_messages_from_user(
            self.db,
            user_id
        )
        assert list_of_all_messages is not None, "List of all messages by user could not be retrieved"
        assert isinstance(list_of_all_messages, list), "List of all messages is the wrong type"
        print(f"Retrieved all the messages from user {user_id}")

        user_conversations = conversationFunctions.get_conversations_by_user(self.db, user_id)
        user_conversation_ids = set(conv['conversation_id'] for conv in user_conversations)
        print(f"User has {len(user_conversation_ids)} conversations")

        sender_types = set()
        for each_message in list_of_all_messages:
            assert each_message['conversation_id'] in user_conversation_ids, \
            f"Message {each_message['message_id']} belongs to conversation not owned by user {user_id}"
        
            assert 'conversation_id' in each_message, "Missing conversation_id"
            assert 'sender_type' in each_message, "Missing sender_type"
            assert 'message_text' in each_message, "Missing message_text"
            assert 'timestamp' in each_message, "Missing timestamp"

            sender_types.add(each_message['sender_type'])

        assert 'user' in sender_types, "Should have messages from user"
        assert 'bot' in sender_types, "Should have messages from bot"
        print(f"Found messages from both user and bot (sender types: {sender_types})")

        invalid_user_id_list = messageFunctions.get_all_messages_from_user(
            self.db,
            99999
        )

        assert invalid_user_id_list == [], "Invalid user ID for messages gave wrong list"
        print(f"User {user_id} has all the right messages with the correct information.")

    def test_get_all_pipeline_messages(self):
        pipeline_id = self.test_pipeline_ids[0]

        list_of_all_messages = messageFunctions.get_all_pipeline_messages(
            self.db,
            pipeline_id
        )
        assert list_of_all_messages is not None, "List of all messages by pipeline could not be retrieved"
        assert isinstance(list_of_all_messages, list), "List of all messages is the wrong type"
        print(f"Retrieved all the messages from pipeline {pipeline_id}")

        pipeline_conversations = conversationFunctions.get_conversations_by_pipeline(self.db, pipeline_id)
        pipeline_conversation_ids = set(conv['conversation_id'] for conv in pipeline_conversations)
        print(f"Pipeline has {len(pipeline_conversations)} conversations")

        sender_types = set()
        for each_message in list_of_all_messages:
            assert each_message['conversation_id'] in pipeline_conversation_ids, \
            f"Message {each_message['message_id']} belongs to conversation not owned by pipeline {pipeline_id}"
        
            assert 'conversation_id' in each_message, "Missing conversation_id"
            assert 'sender_type' in each_message, "Missing sender_type"
            assert 'message_text' in each_message, "Missing message_text"
            assert 'timestamp' in each_message, "Missing timestamp"

            sender_types.add(each_message['sender_type'])

        assert 'user' in sender_types, "Should have messages from user"
        assert 'bot' in sender_types, "Should have messages from bot"
        print(f"Found messages from both user and bot (sender types: {sender_types})")

        invalid_pipeline_id_list = messageFunctions.get_all_messages_from_user(
            self.db,
            99999
        )

        assert invalid_pipeline_id_list == [], "Invalid pipeline ID for messages gave wrong list"
        print(f"Pipeline {pipeline_id} has all the right messages with the correct information.")

    def test_get_all_messages_in_conversation(self):
        conversation_id = self.test_conversation_ids[0]

        list_of_all_messages = messageFunctions.get_all_messages_in_conversation(
            self.db,
            conversation_id
        )
        assert list_of_all_messages is not None, "List of all messages by conversation could not be retrieved"
        assert isinstance(list_of_all_messages, list), "List of all messages is the wrong type"
        print(f"Retrieved all the messages from conversation {conversation_id}")

        sender_types = set()
        for each_message in list_of_all_messages:
            assert each_message['conversation_id'] == conversation_id, f"Message {each_message['user_id']} has the wrong conversation associated with it."

            assert 'conversation_id' in each_message, "Missing conversation_id"
            assert 'sender_type' in each_message, "Missing sender_type"
            assert 'message_text' in each_message, "Missing message_text"
            assert 'timestamp' in each_message, "Missing timestamp"

            sender_types.add(each_message['sender_type'])

        assert 'user' in sender_types, "Should have messages from user"
        assert 'bot' in sender_types, "Should have messages from bot"
        print(f"Found messages from both user and bot (sender types: {sender_types})")

        invalid_conversation_id_list = messageFunctions.get_all_messages_in_conversation(
            self.db,
            99999
        )

        assert invalid_conversation_id_list == [], "Invalid conversation ID for messages gave wrong list"
        print(f"Conversation {conversation_id} has all the right messages with the correct information.")

    def test_get_recent_messages(self):
        conversation_id = self.test_conversation_ids[0]
        
        recent_messages = messageFunctions.get_recent_messages(
            self.db,
            conversation_id,
            limit=5
        )
        
        assert recent_messages is not None, "Could not retrieve recent messages"
        assert isinstance(recent_messages, list), "Should return a list"
        print(f"Got back {len(recent_messages)} recent messages from conversation {conversation_id}")
        
        for message in recent_messages:
            assert message['conversation_id'] == conversation_id, \
                f"Message {message['message_id']} is in the wrong conversation"
        
        timestamps = [message['timestamp'] for message in recent_messages]
        assert timestamps == sorted(timestamps, reverse=True), \
            "Messages should in ascending order"
        print("Messages are correctly in the right ascending order")
        
        invalid_messages = messageFunctions.get_recent_messages(
            self.db,
            99999,
            limit=10
        )
        assert invalid_messages == [], "Should return empty for invalid conversation"
        print("Correctly handles invalid conversation ID")

    def test_get_last_message_in_conversation(self):
        conversation_id = self.test_conversation_ids[0]
        
        last_message = messageFunctions.get_last_message_in_conversation(
            self.db,
            conversation_id
        )
        
        assert last_message is not None, "Could not retrieve last message"
        assert last_message['conversation_id'] == conversation_id, \
            "Message is associated to wrong conversation"
        print(f"Retrieved last message (ID: {last_message['message_id']}) from conversation {conversation_id}")
        
        assert 'message_id' in last_message, "Missing message_id"
        assert 'sender_type' in last_message, "Missing sender_type"
        assert 'message_text' in last_message, "Missing message_text"
        assert 'timestamp' in last_message, "Missing timestamp"
        
        all_messages = messageFunctions.get_all_messages_in_conversation(
            self.db,
            conversation_id
        )
        
        if len(all_messages) > 0:
            latest = max(all_messages, key=lambda m: m['timestamp'])
            assert last_message['message_id'] == latest['message_id'], \
                "Retrieved message is not the most recent"
            print(f"Verified it's the most recent message: '{last_message['message_text'][:50]}...'")
        
        invalid_last = messageFunctions.get_last_message_in_conversation(
            self.db,
            99999
        )
        assert invalid_last is None, "Should return None for invalid conversation"
        print("Correctly handles invalid conversation ID")

    def cleanup(self):
        print("Cleaning up test data...")
        
        deleted_count = 0
        for user_id in self.test_user_ids:
            try:
                if userFunctions.delete_user_by_id(self.db, user_id):
                    deleted_count += 1
            except:
                pass
                
        print(f"Cleaned up {deleted_count}/{len(self.test_user_ids)} test messages")
        self.db.close()

        self.test_user_ids.clear()
        self.test_message_ids.clear()
        self.test_conversation_ids.clear()
        self.test_general_conversation_ids.clear()
        self.test_pipeline_ids.clear()

if __name__ == "__main__":
    tester = TestMessageFunctionsComplete()
    tester.run_all_tests()
