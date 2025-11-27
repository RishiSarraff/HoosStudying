export interface MySQLUser {
    user_id: number,
    firebase_uid: string,
    first_name: string,
    last_name: string,
    email: string,
    created_user: boolean
    needs_name: boolean
}

export interface UploadResponse{
    success: boolean;
    message: string;
    file_name: string;
    storage_path: string;
    download_url: string;
    chunk_count: number;
    embedding_count: number;
    vector_db_stored: boolean;
}

export interface UploadFormProps {
    user: MySQLUser;
}

export interface NameModalProps {
    onSubmit: (first_name: string, last_name: string) => void;
}

export interface UserUpdateNameRequest {
    first_name: string;
    last_name?: string;
}

