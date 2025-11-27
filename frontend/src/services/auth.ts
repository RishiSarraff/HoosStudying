import { auth } from '../firebase'
import { onAuthStateChanged, signOut} from 'firebase/auth';
import type { User } from 'firebase/auth';
import type { MySQLUser } from "../types"
import axios from "axios";

export async function syncUserToDatabase(firebaseUser: User): Promise<MySQLUser>{
    const token = await firebaseUser.getIdToken();

    const response = await axios.post("http://localhost:8000/api/auth/verify",
        { token },
        {
            headers: {
                "Content-Type": "application/json",
            },
        }
    );

    return response.data;
}

export async function getCurrentUser(token: string): Promise<MySQLUser>{

    const response = await axios.post("http://localhost:8000/api/auth/me",
        { token },
        {
            headers: {
                "Content-Type": "application/json",
            },
        }
    );
    return response.data;
}

export function setupAuthListener(
    onUserSynced: (user: MySQLUser) => void,
    onUserSignedOut: () => void
): () => void {
    return onAuthStateChanged(auth, async (firebaseUser) => {
        if (firebaseUser) {
            try {
                const mysqlUser = await syncUserToDatabase(firebaseUser);

                const needsName = !mysqlUser.first_name; 
                mysqlUser.needs_name = needsName;       
                
                onUserSynced(mysqlUser);
                
                if (mysqlUser.created_user) {
                    console.log('New user created in MySQL:', mysqlUser);
                } else {
                    console.log('Existing user signed in:', mysqlUser);
                }
            } catch (error) {
                console.error('Error syncing user to MySQL:', error);
            }
        } else {
            onUserSignedOut();
        }
    });
}

export async function logout(): Promise<void> {
    try {
        await signOut(auth);
    } catch (error) {
        console.error('Error signing out:', error);
        throw error;
    }
}

export async function getCurrentToken(): Promise<string | null> {
    const user = auth.currentUser;
    if (!user) return null;
    return await user.getIdToken();
}