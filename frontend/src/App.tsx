import React, { useEffect, useState } from "react";
import { Typography, Box} from "@mui/material";
import AuthPage from "./components/AuthPage";
import UploadForm from "./components/UploadForm";
import { setupAuthListener, getCurrentToken } from "./services/auth";
import type { MySQLUser } from "./types"; 
import axios from "axios"
import NameModal from "./components/NameModal";

const App: React.FC = () => {
  const [user, setUser] = useState<MySQLUser | null>(null);
  const [needsName, setNeedsName] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = setupAuthListener(
      (mysqlUser) => {
        setUser(mysqlUser);
        if(mysqlUser.needs_name){
          setNeedsName(true)
        }
        setLoading(false);
      },
      () => {
        setUser(null);
        setLoading(false)
      }
    )

    return () => unsubscribe();
  }, []);

  if (loading) {
    return (
        <Box
        sx={{
            minHeight: "100vh",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
        }}
        >
        <Typography variant="h4">Loading...</Typography>
        </Box>
    );
  }

  if (!user) {
    return <AuthPage />;
  }

  return (
    <div>
      {needsName && (
        <NameModal
          onSubmit={async (first_name, last_name) => {
            const token = await getCurrentToken();

            await axios.post(
              "http://localhost:8000/api/auth/user/update-name",
              { first_name, last_name },
              { headers: { Authorization: `Bearer ${token}` } }
            );

            if (user) {
              setUser({ ...user, first_name, last_name, needs_name: false });
            }

            setNeedsName(false);
          }}
        />
      )}
      <div>
        <UploadForm user={user}/> 
      </div>
    </div>
  );
};

export default App;
