"""
Database schema - to execute manually via a script
"""

CREATE_USER_TABLE = """
    CREATE TABLE `User` (
        user_id INT AUTO_INCREMENT,
        firebase_uid VARCHAR(128) UNIQUE NOT NULL,
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50) NOT NULL,
        email VARCHAR(100) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id),
        UNIQUE KEY unique_email (email)
    );
"""

CREATE_PIPELINE_TABLE = """
    CREATE TABLE `Pipeline` (
        pipeline_id INT AUTO_INCREMENT,
        user_id INT NOT NULL,
        pipeline_name VARCHAR(50) NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (pipeline_id),
        FOREIGN KEY (user_id) REFERENCES `User` (user_id)
            ON DELETE CASCADE
            ON UPDATE CASCADE
    );
"""

CREATE_DOCUMENT_TABLE = """
    CREATE TABLE `Document` (
        document_id INT AUTO_INCREMENT,
        user_id INT NOT NULL,
        file_name VARCHAR(50) NOT NULL,
        file_type VARCHAR(5) NOT NULL,
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (document_id),
        FOREIGN KEY (user_id) REFERENCES `User` (user_id)
          ON DELETE CASCADE
          ON UPDATE CASCADE   
    );
"""

CREATE_DOCUMENT_METADATA_TABLE = """
    CREATE TABLE `Document_Metadata` (
        metadata_id INT AUTO_INCREMENT,
        document_id INT NOT NULL UNIQUE,
        file_size INT,
        page_count INT,
        word_count INT,
        language VARCHAR(10),
        encoding VARCHAR(50),
        firebase_storage_path VARCHAR(500),
        firebase_download_url TEXT,
        checksum VARCHAR(255),
        mime_type VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (metadata_id),
        FOREIGN KEY (document_id) REFERENCES `Document` (document_id)
            ON DELETE CASCADE
            ON UPDATE CASCADE
    );
"""

CREATE_DOCUMENT_CHUNK_TABLE = """
    CREATE TABLE `Document_Chunk` (
        chunk_id INT AUTO_INCREMENT,
        document_id INT NOT NULL,
        chunk_text TEXT NOT NULL,
        chunk_index INT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (chunk_id),
        UNIQUE KEY unique_document_chunk (document_id, chunk_index),
        FOREIGN KEY (document_id) REFERENCES `Document` (document_id)
            ON DELETE CASCADE
            ON UPDATE CASCADE
    );
"""

CREATE_PIPELINE_DOCUMENTS_TABLE = """
    CREATE TABLE `Pipeline_Documents` (
        pipeline_id INT NOT NULL,
        document_id INT NOT NULL,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT TRUE,
        PRIMARY KEY (pipeline_id, document_id),
        FOREIGN KEY (pipeline_id) REFERENCES `Pipeline` (pipeline_id)
            ON DELETE CASCADE
            ON UPDATE CASCADE,
        FOREIGN KEY (document_id) REFERENCES `Document` (document_id)
            ON DELETE CASCADE
            ON UPDATE CASCADE
    );
"""

CREATE_CONVERSATION_TABLE = """
    CREATE TABLE `Conversation` (
        conversation_id INT AUTO_INCREMENT,
        user_id INT NOT NULL,
        pipeline_id INT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_message_at TIMESTAMP,
        PRIMARY KEY (conversation_id),
        FOREIGN KEY (user_id) REFERENCES `User` (user_id)
            ON DELETE CASCADE
            ON UPDATE CASCADE,
        FOREIGN KEY (pipeline_id) REFERENCES `Pipeline` (pipeline_id)
            ON DELETE SET NULL
            ON UPDATE CASCADE
    );
"""

CREATE_MESSAGE_TABLE = """
    CREATE TABLE `Message` (
        message_id INT AUTO_INCREMENT,
        conversation_id INT NOT NULL,
        sender_type ENUM('user', 'bot') NOT NULL,
        message_text TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (message_id),
        FOREIGN KEY (conversation_id) REFERENCES `Conversation` (conversation_id)
            ON DELETE CASCADE
            ON UPDATE CASCADE
    );
"""

CREATE_TAG_TABLE = """
    CREATE TABLE `Tag` (
        tag_id INT AUTO_INCREMENT, 
        user_id INT NULL, 
        name VARCHAR(50) NOT NULL, 
        color VARCHAR(50) NOT NULL, 
        tag_type ENUM('system', 'custom') DEFAULT 'custom', 
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
        PRIMARY KEY (tag_id), 
        FOREIGN KEY (user_id) REFERENCES User(user_id) 
            ON DELETE CASCADE,
        UNIQUE KEY unique_user_tag (user_id, name)
    );
"""

CREATE_PIPELINE_TAG_TABLE = """
    CREATE TABLE `Pipeline_Tag` (
        pipeline_id INT NOT NULL,
        tag_id INT NOT NULL,
        PRIMARY KEY (pipeline_id, tag_id),
        FOREIGN KEY (pipeline_id) REFERENCES `Pipeline` (pipeline_id)
            ON DELETE CASCADE
            ON UPDATE CASCADE,
        FOREIGN KEY (tag_id) REFERENCES `Tag` (tag_id)
            ON DELETE CASCADE
            ON UPDATE CASCADE
    );
"""

ALL_TABLES = [
    CREATE_USER_TABLE,
    CREATE_PIPELINE_TABLE,
    CREATE_DOCUMENT_TABLE,
    CREATE_DOCUMENT_METADATA_TABLE,
    CREATE_DOCUMENT_CHUNK_TABLE,
    CREATE_PIPELINE_DOCUMENTS_TABLE,
    CREATE_CONVERSATION_TABLE,
    CREATE_MESSAGE_TABLE,
    CREATE_TAG_TABLE,
    CREATE_PIPELINE_TAG_TABLE
]